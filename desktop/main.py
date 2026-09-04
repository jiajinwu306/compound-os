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

    api = Api()

    # PyWebView 默认会注入 window.pywebview，JS 通过 window.pywebview.api 调用 Python
    window = webview.create_window(
        title=APP_TITLE,
        url=renderer_html,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
        text_select=True,
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("[start] calling webview.start()\n")
    webview.start(debug=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("[exit] webview.start() returned\n")


if __name__ == "__main__":
    main()
