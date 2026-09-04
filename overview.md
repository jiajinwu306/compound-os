# COMPOUND.OS v5 Windows 桌面版交付说明

## 本次完成内容

按用户「按 A 方案做桌面化，需要桌面快捷方式」的指示，保留现有单文件 HTML 网页源码，使用 PyWebView 套壳为 Windows 便携软件：

1. **新增桌面端代码（`desktop/`）**
   - `main.py`：PyWebView 窗口入口，加载 `renderer/index.html`，不启动外部浏览器。
   - `api.py`：JS ↔ Python 桥接 API，暴露 `loadState` / `saveState` / `loadNews` / `saveNewsCache` / `openExternal` / `log`。
   - `build.py`：一键构建脚本，生成图标、打包 PyInstaller、验证资源、创建桌面快捷方式、压缩 ZIP。
   - `run_dev.py`：开发模式快速启动。

2. **改造 `index.html` 支持 PyWebView 桥接**
   - 检测 `window.pywebview` 存在时，状态读写走 Python API，否则回退 `localStorage`。
   - 资讯刷新从 `fetch('./news.json')` 改为调用 `pywebview.api.loadNews()`。
   - 外部新闻链接调用 `pywebview.api.openExternal()` 由系统浏览器打开。
   - 保留纯浏览器运行能力，网页版与桌面版共用同一份源码。

3. **数据持久化到 `%LOCALAPPDATA%\CompoundOS`**
   - `workspace.json`：主状态（待办、增长、健康、爱意、UI 等）。
   - `news.json`：资讯缓存（可写入，优先于打包默认数据）。
   - 所有写操作使用「临时文件 + `os.replace`」原子替换，防止意外关闭损坏数据。

4. **资源打包**
   - PyInstaller `--onedir --windowed` 打包。
   - 包含 `renderer/index.html`、`renderer/news.json`、`assets/rose.ico`、`assets/rose.png`。
   - 生成金色玫瑰图标作为程序图标。

5. **桌面快捷方式**
   - 构建完成后自动在 Windows 桌面创建 `COMPOUND.OS.lnk`。
   - 快捷方式指向 `dist/COMPOUND.OS/COMPOUND.OS.exe`，使用玫瑰图标。

6. **交付物**
   - `dist/COMPOUND.OS/`：完整程序目录。
   - `dist/COMPOUND.OS.zip`：完整压缩包。
   - `README_DESKTOP.md`：中文使用说明（数据位置、迁移方法、常见问题）。

## 验证结果

- `index.html` 内联 JS 语法检查通过（Node `--check`）。
- `desktop/*.py` Python 语法检查通过。
- `api.py` 单测通过：`saveState` / `loadState` / `loadNews` / `openExternal` 均正常。
- PyInstaller 打包成功，关键资源存在：
  - `dist/COMPOUND.OS/COMPOUND.OS.exe`
  - `_internal/renderer/index.html`
  - `_internal/renderer/news.json`
  - `_internal/assets/rose.ico`
- EXE 启动后持续运行超过 12 秒未立即退出。
- 桌面快捷方式已生成：`C:\Users\wujiajin\Desktop\COMPOUND.OS.lnk`
- ZIP 压缩包已生成：`E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS\dist\COMPOUND.OS.zip`

## 环境限制说明

- 当前构建环境为无显示界面的沙箱，无法实际看到 WebView2 渲染窗口，因此无法通过截图验证 UI 是否正常显示。
- 在真实 Windows 桌面环境中，双击 `COMPOUND.OS.exe` 应能正常打开窗口并显示网页界面。
- 如遇到启动无窗口，请检查系统是否已安装 Microsoft Edge WebView2 Runtime（Windows 11 通常已自带）。

## 文件清单

```
E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS\
├── index.html                     # 网页版源码（已兼容 PyWebView）
├── news.json                      # 默认 AI 资讯缓存
├── fetch_news.py                  # RSS 抓取脚本
├── setup_scheduler.bat            # 创建每日 10:00 自动任务
├── remove_scheduler.bat           # 移除自动任务
├── run_daily.bat                  # 每日任务入口
├── notify.ps1                     # Windows Toast 通知
├── INSTALL.md                     # 英文安装说明（任务计划程序）
├── NEWS_PIPELINE.md               # 资讯管线说明
├── README_DESKTOP.md              # 中文桌面版使用说明
├── overview.md                    # 本文件
└── desktop/
    ├── main.py                    # PyWebView 入口
    ├── api.py                     # JS ↔ Python API
    ├── build.py                   # 一键构建脚本
    ├── run_dev.py                 # 开发模式启动
    ├── assets/
    │   ├── rose.ico               # 程序图标
    │   └── rose.png               # 图标 PNG
    └── renderer/
        ├── index.html             # 打包用页面
        └── news.json              # 打包用默认资讯
└── dist/
    ├── COMPOUND.OS/               # 完整程序目录
    │   ├── COMPOUND.OS.exe
    │   └── _internal/
    └── COMPOUND.OS.zip            # 便携压缩包
```

## 使用方式

### 直接使用桌面版

1. 解压 `dist/COMPOUND.OS.zip` 到任意目录。
2. 双击 `COMPOUND.OS.exe`。
3. 数据自动保存在 `%LOCALAPPDATA%\CompoundOS`。

### 重新构建

```powershell
cd "E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS"
C:\Users\wujiajin\.workbuddy\binaries\python\envs\compound_os_build\Scripts\python.exe desktop/build.py
```

## 已知限制

- 桌面版与网页版数据不自动互通，需手动导出/导入 JSON 备份。
- 首次运行需要系统已安装 WebView2 Runtime。
- 资讯每日 10:00 自动推送仍由 `setup_scheduler.bat` 控制，与桌面版独立运行。

## 后续可选迭代

- 增加桌面版启动时自动检查/提示安装 WebView2 Runtime。
- 桌面版与网页版通过云端或局域网实现数据同步。
- 增加托盘图标、最小化到托盘、开机自启。
- 资讯更新后主动刷新桌面版界面（目前需手动点「立即刷新」）。
