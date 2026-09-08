# -*- coding: utf-8 -*-
r"""
COMPOUND.OS · Windows 桌面入口

使用 PyWebView 加载本地 renderer/index.html，不启动外部浏览器。
数据持久化交给 desktop/api.py，保存到 %LOCALAPPDATA%\CompoundOS。

运行方式：
    python desktop/main.py

PyInstaller 打包后：
    dist/COMPOUND.OS/COMPOUND.OS.exe
"""

import os
import pathlib
import sys
import webview

from api import Api


APP_TITLE = "COMPOUND.OS"


def resource_path(relative_path: str):
    """兼容开发模式与 PyInstaller 单目录模式。"""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def main():
    # 启动日志：帮助在无显示环境排查问题
    log_path = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "CompoundOS", "pywebview.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[start] pid={os.getpid()} renderer_exists={os.path.exists(resource_path(os.path.join('renderer', 'index.html')))}\n")

    renderer_html = resource_path(os.path.join("renderer", "index.html"))
    # 兼容开发时直接运行 desktop/main.py 的情况：回退到项目根目录的 index.html
    if not os.path.exists(renderer_html):
        root_html = resource_path(os.path.join("..", "index.html"))
        if os.path.exists(root_html):
            renderer_html = root_html

    if not os.path.exists(renderer_html):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[error] renderer not found: {renderer_html}\n")
        print(f"[错误] 找不到渲染页面: {renderer_html}", file=sys.stderr)
        sys.exit(1)

    # ⚠️ 不要给 file:// URL 追加 "?desktop=1" 之类的 query string。
    # 实测（2026-09-07）：EdgeChromium/WebView2 会把 "?" 编码成 "%3F" 并当作文件名的一部分，
    # 导致页面加载失败（location.href 变成 chrome-error://chromewebdata/），整个界面白屏。
    # fragment("#") 方案同样不稳定（evaluate_js 返回 None）。
    # 因此桌面端判定统一交给前端的 window.pywebview 检测——该方式已实测可靠。
    try:
        page_url = pathlib.Path(renderer_html).resolve().as_uri()
    except Exception:
        page_url = renderer_html

    api = Api()

    # PyWebView 默认会注入 window.pywebview，JS 通过 window.pywebview.api 调用 Python
    window = webview.create_window(
        title=APP_TITLE,
        url=page_url,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
        text_select=True,
    )

    # ⚠️ 关闭时落盘交给前端 beforeunload（index.html 已监听并调用 flushState）。
    # 曾在此用 window.events.closing += on_closing 同步调 window.evaluate_js()，
    # 实测（2026-09-08）会导致点关闭按钮时窗口卡死「未响应」：
    # evaluate_js 是同步调用，等待 JS 返回结果，但窗口已进入关闭流程、JS 执行
    # 环境被冻结，结果永远回不来 → Python 主线程阻塞 → 程序无法关闭。
    # 因此不再在 Python 侧触发 JS，仅保留前端的 beforeunload 落盘逻辑。

    # ⚠️ 关键修复（数据丢失 bug）
    # PyWebView 的 private_mode 默认为 True（隐私模式），该模式下 WebView 的
    # localStorage 不落盘，关闭窗口即被清空 —— 这是「重开就重置」的直接原因之一。
    # 这里显式关闭隐私模式，并把缓存目录固定到 %LOCALAPPDATA%\CompoundOS\WebViewCache，
    # 保证 localStorage 兜底通道同样可持久化。
    storage_path = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "CompoundOS", "WebViewCache",
    )
    os.makedirs(storage_path, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("[start] calling webview.start()\n")
    try:
        webview.start(debug=False, private_mode=False, storage_path=storage_path)
    except TypeError:
        # 部分 pywebview 版本不支持 storage_path 参数，降级为仅关闭隐私模式
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[warn] storage_path unsupported, fallback\n")
        webview.start(debug=False, private_mode=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("[exit] webview.start() returned\n")


if __name__ == "__main__":
    main()
