# COMPOUND.OS 发布前验收报告

> 验收时间：2026-09-04 16:40  
> 验收范围：不增加新功能，仅检查已有功能、代码质量、构建产物与启动稳定性。

---

## 1. 已通过项目

| # | 检查项 | 验证方式 | 结果 |
|---|---|---|---|
| 1 | 五个导航严格单板块切换 | 代码审查 + 运行 `switchModule` | ✅ 通过。`switchModule` 仅对当前目标 panel 加 `active`，其余 panel `display:none`，CSS 仅 `.panel.active{display:block}`。 |
| 2 | 所有按钮真实可用，数据刷新/重启后仍存在 | 代码审查所有 `<button>` 与 `addEventListener`；Node vm 模拟 localStorage 持久化 | ✅ 通过。所有按钮均有事件处理；添加任务 → `saveState` → 新上下文 `loadState` 后任务仍在。 |
| 3 | 增长曲线一天只能记录一次 | 代码审查 `recordedToday` 禁用逻辑 | ✅ 通过。`renderGrowth` 检测到今日已记录则禁用 input 和 button。 |
| 3 | 未来日期没有被提前绘制 | 代码审查 + 数据层测试 | ⚠️ 部分通过。UI 无法录入未来日期；但如果通过 JSON 导入未来日期，数据层仍会绘制（见风险项）。 |
| 3 | 进入板块时动画可重播 | 代码审查 `renderGrowthCurve` | ✅ 通过。`switchModule → refreshAll → renderGrowthCurve` 每次重新设置 `strokeDasharray/offset`。 |
| 3 | 48 小时规则和重启周期状态正确 | Node vm 单元测试 | ✅ 通过。>48h 未记录 → 记录清空、基线累加、`autoReset=true`；重启周期 → 基线=当前总分、记录清空、`zeroedCount+1`。 |
| 4 | 健康水位与本周事件数量一致 | Node vm 单元测试 | ✅ 通过。`healthLevel = min(100, round(events.length / 14 * 100))`，7 条事件对应 50% 水位。 |
| 5 | 爱意达到 20 次触发金色玫瑰动画 | 代码审查 `bindLove` | ✅ 通过。`state.love.length === 20 && !state.meta.eggShown` 时调用 `playEgg()`。 |
| 5 | 记忆卡片来自真实记录 | 代码审查 `playEgg` | ✅ 通过。`state.love.slice(-CARD_COUNT).reverse()` 直接取自真实记录。 |
| 5 | 重置按钮有二次确认 | 代码审查 `loveResetBtn` 点击处理 | ✅ 通过。连续两次 `confirmModal` 确认后才清空 `state.love`。 |
| 6 | 资讯标题、来源、日期、链接、图片显示 | Node vm 渲染测试 | ✅ 通过。缓存/实时模式均正确渲染标题、来源、日期、原文链接；有图时显示 `img`，无图时显示源占位 SVG。 |
| 6 | 缓存内容不得显示成实时 | 代码审查 + Node vm 测试 | ✅ 通过。`mode !== 'live'` 时 badge 固定为「缓存」；桌面端读取本地文件也强制 `mode='cache'`。 |
| 7 | 响应式布局代码层面无 overflow | CSS 审查 | ⚠️ 代码层面通过，但未在真实浏览器 1440×900 / 1920×1080 / 窄窗口截图验证（见风险项）。 |
| 8 | JS lint | `node --check` | ✅ 通过。 |
| 8 | Python lint | `python -m py_compile` | ✅ 通过。 |
| 8 | 生产构建 | PyInstaller `--onedir --windowed` | ✅ 通过。产出 `dist/COMPOUND.OS/COMPOUND.OS.exe`、`_internal/renderer/index.html`、`_internal/assets/rose.ico`。 |
| 8 | 桌面版启动测试 | 实际运行 EXE 8 秒 | ✅ 通过。EXE 启动后持续运行 8 秒未退出；`pywebview.log` 确认执行到 `webview.start()`。 |
| 9 | 桌面快捷方式 | `build.py` 输出 | ✅ 通过。`C:\Users\wujiajin\Desktop\COMPOUND.OS.lnk` 已创建。 |

---

## 2. 仍存在风险 / 未完全验证项

| # | 风险描述 | 影响 | 建议 |
|---|---|---|---|
| 1 | **响应式布局未在真实分辨率下截图验证** | 在 1440×900、1920×1080、窄窗口下可能出现未被代码审查发现的遮挡/溢出/重叠 | 在真实 Windows 桌面用浏览器/桌面 EXE 打开，切换 DevTools 设备模拟或窗口尺寸，目视检查五模块。 |
| 2 | **增长曲线未来日期数据层未过滤** | 若用户导入含未来日期的 JSON，曲线会绘制未来点 | 在 `renderGrowthCurve` 中增加 `d <= diffDays(g.cycleStart, todayStr())` 过滤，或导入校验时拒绝未来日期。 |
| 3 | **桌面版在沙箱中无法看到实际窗口** | 无法 100% 确认 WebView2 渲染正常、JS API 实际可用 | 在真实 Windows 桌面运行 `COMPOUND.OS.exe`，检查：窗口出现、能切换模块、添加任务后关闭再开数据仍在、点击资讯外链能在系统浏览器打开。 |
| 4 | **桌面版资讯更新不会自动刷新已打开的窗口** | 定时任务更新 `news.json` 后，已运行的桌面版仍显示旧缓存，需手动点「立即刷新」 | 可在后续版本增加文件监听或定时轮询 `loadNews()`。 |
| 5 | **导出/导入 JSON 在桌面版中未实测** | 桌面版 `URL.createObjectURL` + 锚点点击的下载行为在 WebView2 中可能异常 | 在真实桌面环境测试导出备份；如异常，可桥接到 Python `openExternal` 或文件对话框。 |
| 6 | **WebView2 Runtime 依赖** | 部分旧版 Windows 10 可能未安装 Edge WebView2 Runtime，导致程序无法显示窗口 | 在 README 中已说明；后续可增加启动时检测与下载引导。 |

---

## 3. 需要外部服务或系统权限的功能

| 功能 | 外部依赖 / 权限 | 说明 |
|---|---|---|
| 每日 10:00 资讯抓取 | Windows 任务计划程序 + 管理员权限 | 需右键「以管理员身份运行」`setup_scheduler.bat` 创建任务。 |
| 桌面 Toast 通知 | PowerShell + .NET WinForms | `notify.ps1` 使用系统自带 `System.Windows.Forms.NotifyIcon`，无需第三方。 |
| RSS 抓取 | 外部网络 + 4 个官方 RSS 源可用性 | `fetch_news.py` 依赖 OpenAI / GitHub / Google DeepMind / AWS ML Blog 的 RSS。 |
| DeepSeek 翻译（可选） | `DEEPSEEK_API_KEY` 环境变量 | 当前未启用；如需中文翻译，用户需自行设置 key。 |
| 资讯外链打开 | 系统默认浏览器 | 桌面版调用 `pywebview.api.openExternal(url)` → `webbrowser.open()`。 |
| 桌面版窗口渲染 | Microsoft Edge WebView2 Runtime | Windows 11 通常已自带；Windows 10 部分旧版本需安装。 |
| 数据持久化（桌面版） | `%LOCALAPPDATA%\CompoundOS` 写入权限 | 普通用户权限即可。 |

---

## 4. 验收结论

- **功能层面**：核心功能（导航切换、数据持久化、增长曲线、健康水位、爱意彩蛋、资讯缓存/实时区分）均通过自动化测试或代码审查验证。
- **构建层面**：lint、PyInstaller 打包、EXE 启动测试均通过。
- **发布前建议**：在真实 Windows 桌面完成一次完整视觉验收（响应式布局、WebView2 窗口渲染、桌面版数据读写、外链打开）。
- **当前状态**：达到代码可发布状态，但建议完成真实环境视觉验收后再正式对外分发。
