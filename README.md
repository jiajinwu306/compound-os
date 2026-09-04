# COMPOUND.OS · 个人长期复利工作台

> 一个**从零构建的 Windows 桌面应用**——用「复利」视角可视化每天的能力、健康与关系。

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4)](#)
[![Stack](https://img.shields.io/badge/stack-native%20Python%20%2B%20HTML%20%2B%20PyWebView-0f6e56)](#)
[![Size](https://img.shields.io/badge/release-14MB-999)](#)
[![License](https://img.shields.io/badge/license-MIT-333)](#)

<!-- GIF 占位：录屏完成后用 docs/demo.gif 替换
![demo](docs/demo.gif)
-->

**[⬇️ 下载桌面版](../../releases)** · **[🎬 30 秒录屏](#录屏演示)** · **[📖 项目文档](#项目结构)** · **[English](#english)**

---

## 一句话定位

COMPOUND.OS 是一个 **Windows 原生桌面应用**，帮你用「复利」的视角看自己——长期积累的能力、健康与关系，每天记录、每天可视化、每周复盘。零依赖、零注册表、解压即用。

## 桌面端定位（先看这里）

这是一台**真桌面应用**，不是网页套壳：

| 能力 | 实现 |
|---|---|
| 独立窗口 | PyWebView 加载本地渲染层，无浏览器依赖 |
| 本地数据目录 | `%LOCALAPPDATA%\CompoundOS\workspace.json` |
| 系统级定时任务 | Windows 任务计划程序 · 每天 10:00 自动抓取资讯 |
| 桌面通知 | PowerShell + WinForms NotifyIcon · 原生 Toast |
| 原子化数据写入 | 临时文件 + `os.replace`，意外断电不损坏 |
| 打包体积 | 14 MB（含 Python 运行时 + WebView2 桥） |
| 安装方式 | 解压即用 · 零注册表写入 · 卸载即删除 |

> ⚠️ **macOS / Linux 用户**：可点 [在线 Preview](https://jiajinwu306.github.io/compound-os/) 看落地页和录屏，但桌面版仅 Windows。

## 五大模块

| 模块 | 作用 | 数据形态 |
|---|---|---|
| **AI 能力雷达** | 每日抓取 10 条 AI 官方资讯 | 4 个 RSS 源 · 12 字段标准化 · 可选 DeepSeek 翻译 |
| **增长曲线** | 30 天滚动画布，每天打一个点 | 时间序列 · 48h 自动归零 · 周期重启 |
| **今日作战** | 当日待办勾选，跨日自动顺延 | 任务列表 · 逾期高亮 |
| **身体账户** | 一周健康事件可视化人体水位 | 周事件流 · 人体轮廓 + 水位动画 |
| **爱意仪式** | 累计 20 次触发金色玫瑰动画 | 事件流 · 6 阶段仪式 · 记忆卡片 |

## 录屏演示

<!-- 录屏完成后打开下方注释
![30 秒演示](docs/demo.gif)
-->

> 30 秒录屏脚本见 [`docs/recording-script.md`](docs/recording-script.md)，照着录即可。

## 技术选型（Why no framework）

本项目**故意不**使用 React / Vue / Dify / LangChain——这是有意识的技术主张，不是因为不会用：

| 选择 | 理由 |
|---|---|
| **单文件 HTML（110 KB）** | 零依赖、离线可用、可邮件分发、可直接打印查看 |
| **原生 JS / CSS / SVG** | 所有图标、图表、人体水位都内联 SVG，零外部资源 |
| **PyWebView 套壳** | 复用同一份渲染层，避免维护两套 UI |
| **Python + requests** | RSS 抓取足够简单，5 个源够用，不引入额外框架 |
| **Windows 任务计划程序** | 系统原生调度，不引入 Airflow / Celery 这类重组件 |
| **`os.replace` 原子写** | 不引第三方 DB，保证意外断电数据不损坏 |
| **localStorage 兜底** | 桌面版 API 失败时自动回退，单一数据层 |

> 「**为问题选工具，而不是为工具找问题**」——一个 110 KB 的单文件能解决的桌面端需求，不值得引入 200 MB+ 的运行时。

## 本地运行

```bash
# 网页版（任任何 HTTP 服务器）
python -m http.server 8000
# 浏览器打开 http://localhost:8000

# 桌面版（需要 Python 3.10+ 与 WebView2 Runtime）
pip install pywebview pyinstaller requests
python desktop/main.py

# 构建桌面版（输出 dist/COMPOUND.OS.zip）
python desktop/build.py
```

> Windows 10/11 默认自带 WebView2 Runtime，无需额外安装。

## 项目结构

```
COMPOUND.OS/
├── index.html              # 渲染层（网页版 + 桌面版共用，单文件）
├── desktop/
│   ├── main.py             # PyWebView 入口
│   ├── api.py              # JS ↔ Python 桥接 API
│   ├── build.py            # PyInstaller 打包脚本
│   ├── run_dev.py          # 开发模式启动
│   ├── renderer/           # 桌面版渲染层副本
│   │   ├── index.html
│   │   └── news.json
│   └── assets/             # 图标资源（金色玫瑰）
│       ├── rose.ico
│       └── rose.png
├── fetch_news.py           # RSS 抓取 + 打分 + 配额
├── notify.ps1              # PowerShell 桌面通知
├── run_daily.bat           # 每日任务入口
├── setup_scheduler.bat     # 一键安装定时任务（管理员）
├── remove_scheduler.bat    # 移除定时任务
├── news.json               # 当前资讯缓存（运行时生成）
├── INSTALL.md              # 桌面版安装说明
├── README_DESKTOP.md       # 桌面版使用文档
├── NEWS_PIPELINE.md        # 资讯管线设计文档
├── ACCEPTANCE_REPORT.md    # 发布前验收报告
├── LICENSE
└── .gitignore
```

## 数据安全

| 存储位置 | 用途 | 保护 |
|---|---|---|
| `%LOCALAPPDATA%\CompoundOS\workspace.json` | 主状态（任务、增长、爱意） | 原子替换 · 导出/导入 JSON |
| `%LOCALAPPDATA%\CompoundOS\news.json` | 资讯缓存 | 原子替换 |
| `%LOCALAPPDATA%\CompoundOS\app.log` | 启动日志 | 滚动写入 |

- 无任何服务器，所有数据在用户本地
- 桌面版关闭时强制 flush，写入失败立即报错，不静默吞错
- 支持「导出 JSON」/「导入恢复」，跨设备迁移无障碍

## 适用场景

- **个人复盘**：每天 3 分钟记录，每周一次回顾
- **AI 资讯追踪**：每天 10 条官方源更新，无需打开网页
- **长期习惯可视化**：让「复利」从口号变成你看得见的曲线
- **个人作品站 demo**：完整桌面应用案例（含打包 + 自动任务 + 系统通知）

## English

COMPOUND.OS is a **Windows desktop application** built from scratch to visualize daily compounding — your abilities, health, and relationships.

**Stack:** native Python + single-file HTML (110 KB) + PyWebView + Windows Task Scheduler + PowerShell.

**Key features:**

- 5 modules: AI radar / growth curve / today tasks / body account / love ritual
- Local-first: data lives in `%LOCALAPPDATA%\CompoundOS`
- Auto-fetch: daily 10:00 RSS job via Windows Task Scheduler
- Atomic write: temp file + `os.replace`, survives power loss
- 14 MB release: zero registry write, unzip-and-run

**Why no framework?** "Choose tools for the problem, not problems for the tools." A 110 KB single file solves this desktop need without dragging in a 200 MB+ runtime.

See [`docs/architecture.md`](docs/architecture.md) for design notes (TODO).

## License

MIT