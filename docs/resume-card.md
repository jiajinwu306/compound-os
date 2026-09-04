# 简历 + 作品站卡片 · COMPOUND.OS

> 三段可复制粘贴的文案，分别给：简历 / 个人作品站 / 面试官追问。

---

## 一、简历一句话（项目条目）

### 中文版（推荐）

```
COMPOUND.OS · 个人长期复利工作台 · 独立开发
• 原生技术栈从零构建 Windows 桌面应用：单文件 HTML 前端 + PyWebView 客户端
  + Python 资讯管线，实现本地数据原子持久化、每日定时抓取与系统级通知。
• 5 个核心模块（AI 雷达 / 增长曲线 / 今日作战 / 身体账户 / 爱意仪式），
  零外部依赖，14 MB 解压即用。
• 在线展示：jiajinwu306.github.io/compound-os · 源码：github.com/jiajinwu306/compound-os
```

### 英文版

```
COMPOUND.OS — Personal Long-term Compounding Workbench · Independent Project
• Built a native Windows desktop application from scratch: single-file HTML
  renderer + PyWebView shell + Python RSS pipeline, with atomic local persistence,
  daily scheduled fetch, and system-level notifications.
• 5 core modules (AI Radar / Growth Curve / Today Tasks / Body Account /
  Love Ritual), zero external dependencies, 14 MB unzip-and-run.
• Live preview: jiajinwu306.github.io/compound-os
  Source: github.com/jiajinwu306/compound-os
```

### 一行极简版（用于简历技能区 / Twitter bio）

```
COMPOUND.OS · A native Windows desktop app visualizing daily compounding · 14 MB · 0 framework
```

---

## 二、个人作品站卡片（HTML 片段）

> 适配你已有的作品站。深色卡片版直接复制，浅色卡片版替换背景色即可。

### 深色卡片版（推荐用于技术向作品站）

```html
<a href="https://jiajinwu306.github.io/compound-os/" class="card project-card-dark">
  <div class="card-tag">2026 · Side Project</div>
  <h3 class="card-title">COMPOUND.OS</h3>
  <p class="card-sub">个人长期复利工作台 · Native Windows desktop app</p>
  <div class="card-bullets">
    <span>📦 14 MB</span>
    <span>🪟 Windows desktop</span>
    <span>📡 Daily auto-fetch</span>
    <span>🎯 5 modules</span>
  </div>
  <p class="card-desc">
    从零构建的 Windows 桌面应用——单文件 HTML 前端 + PyWebView 客户端 + Python 资讯管线。
    零外部依赖，本地数据原子持久化，系统级每日定时抓取。
  </p>
  <div class="card-stack">
    <code>Python</code><code>PyWebView</code><code>HTML/CSS/JS</code>
    <code>RSS</code><code>PyInstaller</code>
  </div>
  <div class="card-actions">
    <span class="card-link">Live preview →</span>
    <span class="card-link">Source →</span>
  </div>
</a>
```

### 卡片截图建议

- **第一张**：刚才展示页 hero 区的窗口 mockup（你已经有了 SVG 版本，可以截 docs/index.html 的 hero）
- **第二张**：增长曲线 + 身体账户双模块截图（录屏后取帧）
- **第三张**：爱意仪式金色玫瑰特写（动画触发瞬间）

---

## 三、面试官可能追问 + 简短答案

> 准备这 5 个问题的回答，能省掉 80% 的临场压力。

### Q1：「为什么不用 React / Vue？」

**回答模板**：

> 「这个项目的核心约束是 **零依赖 + 离线可用 + 单文件可分发**。110 KB 的单文件装下了 5 个模块的交互、动画和数据层——如果用 React，构建产物至少 500 KB，还得引构建工具链；最关键的是，我想证明**前端框架不是项目成功的必要条件**，懂工具但不滥用工具是产品工程师的判断力。
>
> 当然，**如果是多人协作的 SaaS，我会毫不犹豫用 React**——框架解决的是工程化，不是这个单文件场景的问题。」

### Q2：「为什么用 PyWebView 而不是 Electron？」

**回答模板**：

> 「Electron 打包最小 80 MB，因为它要内嵌 Chromium；PyWebView 直接复用系统的 **WebView2**（Windows 10/11 自带），所以最后成品只有 14 MB。
>
> 另一个考量是 **Python 生态对接**：本项目有 Python 抓取管线、有 PowerShell 通知、有 Windows 任务计划程序——所有这些都用 Python 调用最自然，PyWebView 让我在主程序里直接调用这些能力。」

### Q3：「数据怎么保证不丢？」

**回答模板**：

> 「两层保护。第一层：**localStorage 兜底**，网页版纯前端，关浏览器也不丢。第二层：**临时文件 + os.replace 原子写**，桌面版写 JSON 时先写 `.tmp` 文件，flush 后再 `os.replace` 替换主文件——意外断电时主文件要么是旧版本要么是新版本，不会损坏。
>
> 我还做了 `pywebview.log` 启动日志，写失败立即报错，不静默吞错。」

### Q4：「每日 10 条 AI 资讯是怎么保证质量的？」

**回答模板**：

> 「三层过滤。**第一层是源**：只接 4 个官方 RSS（OpenAI News、GitHub Changelog、Google DeepMind、AWS ML Blog），不用聚合源。**第二层是打分**：关键词正负表（'release' / 'launch' / 'announce' 加分，'funding' / 'hiring' / 'opinion' 减分）；时间越新分越高；每源最多 4 条配额避免单一源霸榜。最后按分数取前 10。
>
> 这套策略在 `NEWS_PIPELINE.md` 里有完整文档。」

### Q5：「这个项目最大的 trade-off 是什么？」

**回答模板**：

> 「**单文件 HTML 不能模块化导入**。当我后期要拆出 settings 模块和 dialog 组件时，发现文件已经 110 KB / 2200 行了——重构成本大于收益。
>
> 所以下一个项目（PayDance 工资看板）我会**用 Vite + 原生 JS 模块化**，把样式和逻辑拆分。这次的经验告诉我：单文件适合 demo 和作品集，工程化项目还是模块化更好。
>
> 这也是这个 README 里专门写『Why no framework』的原因——**技术选型要看场景，不能一概而论**。」

---

## 四、GitHub 仓库描述（Settings → About）

```
A native Windows desktop app visualizing daily compounding — built with Python + PyWebView + single-file HTML.
```

### Topics（标签，建议选 6 个）

```
python · pywebview · desktop-app · windows · rss · single-file-html
```

### Website

```
https://jiajinwu306.github.io/compound-os/
```

---

## 五、提交时简历项目区排列建议

| 顺序 | 项目 | 说明 |
|---|---|---|
| 1 | COMPOUND.OS | **首选位置**——这是真桌面应用 + 5 个完整模块 |
| 2 | 飞书会议待办跟进 Agent | 第二——也是 AI 产品方向，体现 LLM 编排能力 |
| 3 | PayDance 工资看板（筹备中）| 第三——视觉稿阶段，但说明在持续积累 |

> 三个项目都围绕 **AI 产品 / 个人提效** 主线，HR 一眼能看出方向。