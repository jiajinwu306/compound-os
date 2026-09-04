# 30 秒录屏脚本 · COMPOUND.OS

> 目标：让面试官 **30 秒内** 看完「这是一个真桌面应用 · 它能跑 · 它有完整功能」。

---

## 一、录屏前准备

### 软件
- **录屏**：Windows 自带 `Win + G`（Xbox Game Bar），或免费开源 [OBS Studio](https://obsproject.com/)（更可控）
- **转 GIF**：免费 [ScreenToGif](https://www.screetimg.com/)（Windows 专属，可裁剪 + 加字幕）
- **鼠标聚光**：ScreenToGif 编辑器自带 spotlight 效果

### 设置
- 分辨率：1920×1080 或 1440×900
- 窗口大小：把窗口拉成 1280×800 左右，居中放置
- 录屏前清空任务栏通知（避免录到无关通知）

### 环境
- 打开 `COMPOUND.OS.exe` 等到主界面完全加载
- 默认数据（5 个模块有示例数据）即可，不用先录「空状态 → 录数据」（面试官不在乎）

---

## 二、30 秒镜头脚本

| 时间 | 镜头 | 动作 | 字幕/特效 |
|---|---|---|---|
| 0-3s | 全屏窗口 | 双击桌面图标，弹出窗口，等加载 | 字幕：`Native Windows app · 14MB` |
| 3-5s | 窗口全景 | 鼠标从左到右缓慢扫过五个导航 | 字幕：`5 modules · 1 single file` |
| 5-9s | AI 能力雷达 | 点击"AI 雷达"，停留 2 秒，点击第一条外链（在浏览器打开瞬间） | 字幕：`Daily AI news · 4 RSS · auto fetch` |
| 9-13s | 增长曲线 | 点击"增长曲线"，停留 2 秒，鼠标移到曲线最高点 | 字幕：`30-day canvas · one record per day` |
| 13-16s | 今日作战 | 点击"今日作战"，勾选一项任务，停留 | 字幕：`Today's tasks · cross-day auto-roll` |
| 16-20s | 身体账户 | 点击"身体账户"，停留，看水位 | 字幕：`Body account · weekly water level` |
| 20-25s | 爱意仪式 | 点击"爱意仪式"，如果不满 20 次就手动加几次（点"+记一次"按钮）直到 20，触发玫瑰 | 字幕：`20 records → golden rose ritual` |
| 25-28s | 玫瑰动画 | 等金色玫瑰动画完成（6 阶段，约 8-12 秒）—— 录屏脚本里可以截取关键阶段 | 字幕：`6-stage memory ritual` |
| 28-30s | 收尾 | 鼠标移到"立即刷新"按钮，点击一次看到 toast 提示 | 字幕：`Built natively · 0 framework` |

> ⚠️ **20 次触发爱意仪式**是核心爆点。如果第一次跑没满 20 次，在 `setup` 数据里加几条假记录（每条 1 秒加 1 个），或者临时改代码上限阈值到 5 用于录屏，录完改回 20。
>
> **更稳的做法**：录屏脚本里写好辅助函数（不在本仓库内、临时文件），录完删除。

---

## 三、剪辑要点（ScreenToGif 操作）

1. **裁剪**：去掉窗口外黑边，比例 16:9
3. **裁掉开头和结尾**：双击图标 + 退出动画都裁掉，只留窗口内的 30 秒
4. **字幕**：ScreenToGif「标题」面板，添加 5 条上面表格里的字幕
5. **鼠标聚光**：在"点击导航"、"勾选任务"、"触发玫瑰"三处加 spotlight
6. **导出**：保存为 `docs/demo.gif`，压缩到 < 8MB（GitHub README 友好）

---

## 四、上传到 README

录完后：

```bash
# 把 demo.gif 放到 docs/
cp demo.gif docs/demo.gif
```

然后编辑 `README.md`，把以下两处注释打开：

```markdown
<!-- 把注释符号删掉 -->
![demo](docs/demo.gif)
```

```markdown
<!-- 把注释符号删掉 -->
![30 秒演示](docs/demo.gif)
```

---

## 五、备选：上传完整视频到 B 站 / YouTube

如果想多一个"完整版 90 秒"录屏：

1. B 站：上传视频 → 标题「COMPOUND.OS · 个人长期复利工作台 30 秒演示」→ 标签「AI 产品 / 个人项目 / Windows 桌面应用」
2. YouTube：同样上传，标题英文 `COMPOUND.OS Demo · A native Windows desktop app built from scratch`
3. 把视频链接挂到 README 的「录屏演示」段落下面：

```markdown
## 录屏演示

![30 秒演示](docs/demo.gif)

📺 完整 90 秒版本：[B 站](https://www.bilibili.com/video/xxx) | [YouTube](https://youtu.be/xxx)
```

---

## 六、时间预估

| 步骤 | 时间 |
|---|---|
| 录屏 + 反复 | 30 分钟 |
| ScreenToGif 剪辑 + 字幕 | 20 分钟 |
| 上传到 README | 5 分钟 |
| **合计** | **~1 小时** |

> 经验：第一次录屏会反复 3-5 次，不要追求一镜到底，关键是 30 秒内「让人看懂产品是什么」。