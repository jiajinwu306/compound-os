# -*- coding: utf-8 -*-
"""
COMPOUND.OS · 开发模式快速启动

不打包，直接运行 desktop/main.py，加载项目根目录的 index.html。
便于调试 JS ↔ Python 桥接。

用法：
    python desktop/run_dev.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
