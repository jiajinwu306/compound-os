# -*- coding: utf-8 -*-
r"""
COMPOUND.OS · PyWebView JS ↔ Python 桥接 API

暴露给前端的能力：
- loadState / saveState：读写 %LOCALAPPDATA%\CompoundOS\workspace.json
- loadNews / saveNewsCache：读写 %LOCALAPPDATA%\CompoundOS\news.json
- openExternal：调用系统默认浏览器打开外链

所有写操作使用「临时文件 + os.replace」实现原子替换，意外退出时
不会损坏主数据文件。
"""

import json
import os
import shutil
import tempfile
import webbrowser
from pathlib import Path


APP_NAME = "CompoundOS"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME
STATE_FILE = DATA_DIR / "workspace.json"
NEWS_FILE = DATA_DIR / "news.json"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(path: Path, text: str):
    """原子写入 JSON：先写到临时文件，再 replace，失败不损坏原文件。"""
    _ensure_data_dir()
    path = Path(path)
    # 用同级目录创建临时文件，保证 replace 原子且跨分区安全
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def _fallback_news_path():
    """获取打包时内嵌的默认 news.json 路径。
    修复（2026-09-08）：PyInstaller --onedir 下 build.py 用
    `--add-data=RENDERER_DIR;renderer` 把整目录塞到 renderer/ 子目录，
    news.json 实际位于 <MEIPASS>/renderer/news.json，不是 <MEIPASS>/news.json。
    这里按 frozen / dev 两种模式分别返回正确路径。"""
    if getattr(sys, "frozen", False):
        # PyInstaller --onedir 模式：<exe_dir>/_internal/renderer/news.json
        return Path(sys._MEIPASS) / "renderer" / "news.json"
    # 开发模式：项目根/news.json
    return Path(__file__).resolve().parent.parent / "news.json"


class Api:
    """PyWebView JS API：方法名可直接在 JS 中通过 window.pywebview.api.xxx() 调用。"""

    def loadState(self):
        _ensure_data_dir()
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return ""
        return ""

    def saveState(self, json_str: str):
        try:
            # 先校验 JSON 格式，避免写入损坏数据
            json.loads(json_str)
        except Exception as e:
            raise ValueError(f"状态 JSON 格式异常: {e}")
        _atomic_write_json(STATE_FILE, json_str)
        return True

    def loadNews(self):
        _ensure_data_dir()
        # 候选顺序（2026-09-09 调整）：
        # 1) 用户数据目录缓存（桌面端「立即刷新」后落盘的位置）
        # 2) 项目根 news.json（开发者手动跑 fetch_news.py 后那份最新数据；
        #    让点「立即刷新」能立刻读到，不必等重新打开或拷贝到缓存）
        # 3) 打包内嵌默认数据（<MEIPASS>/renderer/news.json）
        project_news = None
        if not getattr(sys, "frozen", False):
            project_news = Path(__file__).resolve().parent.parent / "news.json"
        for candidate in (NEWS_FILE, project_news, _fallback_news_path()):
            if candidate is None:
                continue
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    continue
        return ""

    def saveNewsCache(self, json_str: str):
        try:
            json.loads(json_str)
        except Exception as e:
            raise ValueError(f"资讯 JSON 格式异常: {e}")
        _atomic_write_json(NEWS_FILE, json_str)
        return True

    def openExternal(self, url: str):
        """用系统默认浏览器打开外部链接。"""
        if not url:
            return False
        # 基础安全校验：只允许 http / https
        lowered = url.lower()
        if not (lowered.startswith("http://") or lowered.startswith("https://")):
            return False
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    def log(self, message: str):
        """前端调试日志：写入 %LOCALAPPDATA%\\CompoundOS\\app.log。"""
        _ensure_data_dir()
        log_path = DATA_DIR / "app.log"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                from datetime import datetime
                f.write(f"{datetime.now().isoformat()} {message}\n")
        except Exception:
            pass
        return True


import sys  # noqa: E402
