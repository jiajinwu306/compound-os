# v1.0.0 资产更新说明（数据丢失 bug 修复）

> 用途：替换 GitHub Release v1.0.0 里的 `COMPOUND.OS.zip`，并在原描述**顶部**追加下面这段「更新说明」。

---

## 一、追加到 Release 描述顶部的文案（复制这段）

```markdown
---

### 🔧 2026-09-07 更新：修复「数据重启后全部丢失」的严重 bug

本次更新替换了 `COMPOUND.OS.zip`，**如果你下载过 9/4 的旧版本，请重新下载**。

**问题**：关闭窗口再打开，今日待办 / 重要的人等所有记录全部重置。

**根因**（两处叠加）：

1. 前端用 `const IS_PYWEBVIEW = !!window.pywebview` 判定桌面端，但 `window.pywebview`
   是宿主在页面**加载完成后异步注入**的，这行代码却在脚本同步执行时就求值 → 恒为 `false`。
   桌面端因此全程误走 localStorage 分支，Python 文件存储通道从未被调用。
2. `webview.start()` 未关闭 `private_mode`（PyWebView 默认为 True），
   隐私模式下 WebView 的 localStorage 不落盘，关窗即清空。

**修复**：

- 前端改为运行时轮询检测宿主就绪（`waitForPyWebView`），`saveState` 双写保险
  （Python 文件 + localStorage 兜底），新增关窗前强制落盘 `flushState`
- 后端显式 `private_mode=False`，缓存目录固定到 `%LOCALAPPDATA%\CompoundOS\WebViewCache`，
  并绑定关窗事件触发落盘
- 数据实际落盘位置：`%LOCALAPPDATA%\CompoundOS\workspace.json`

**已验证**：写入 → 关闭 → 重开，数据完整保留（含中文）。
```

---

## 二、操作步骤（网页端，约 2 分钟）

1. 打开 → **https://github.com/jiajinwu306/compound-os/releases/tag/v1.0.0**
2. 右上角点 **Edit release**（铅笔图标）
3. **替换资产**：
   - 在 Assets 区找到 `COMPOUND.OS.zip`（旧的 9/4 版）
   - 点它右侧的 **🗑 删除**
   - 点 "Attach binaries by dropping them here or **selecting them**"
   - 选择文件：
     ```
     E:\workbuddy\2026-09-04-11-23-02\COMPOUND.OS\dist\COMPOUND.OS.zip
     ```
     （14.0 MB / 193 个文件）
4. **追加描述**：把上面第一段的 Markdown 粘贴到描述框**最顶部**
5. 拉到页面底部点绿色的 **Update release**

---

## 三、验证

更新后浏览器会跳回 release 页面，确认：

- [ ] Assets 区显示 `COMPOUND.OS.zip · 14 MB`
- [ ] 描述顶部出现「🔧 2026-09-07 更新」
- [ ] 标签仍是 `v1.0.0`，且标记 `Latest`
- [ ] 下载链接可访问：
      `https://github.com/jiajinwu306/compound-os/releases/latest/download/COMPOUND.OS.zip`
