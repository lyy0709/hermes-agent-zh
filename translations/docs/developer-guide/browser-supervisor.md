---
sidebar_position: 18
title: "浏览器 CDP 监管器"
description: "Hermes 如何通过持久的 CDP 连接检测和响应原生 JS 对话框，并与跨域 iframe 交互。"
---

# 浏览器 CDP 监管器

CDP 监管器弥补了 Hermes 浏览器工具中长期存在的两个空白：

1.  **原生 JS 对话框** (`alert`/`confirm`/`prompt`/`beforeunload`) 会阻塞页面的 JS 线程。在没有监管的情况下，Agent 无法知道对话框已打开——后续的工具调用会挂起或抛出难以理解的错误。
2.  **跨域 iframe (OOPIF)** 对于顶层的 `Runtime.evaluate` 是不可见的。Agent 可以在 DOM 快照中看到 iframe 节点，但如果没有附加到子目标的 CDP 会话，则无法在其中点击、输入或执行 eval。

监管器通过为每个浏览器任务持有一个到后端 CDP 端点的持久 WebSocket 连接来解决这两个问题，将待处理的对话框和框架结构暴露到 `browser_snapshot` 中，并公开一个 `browser_dialog` 工具用于显式响应。

## 后端支持

| 后端 | 对话框检测 | 对话框响应 | 框架树 | 通过 `browser_cdp(frame_id=...)` 进行 OOPIF `Runtime.evaluate` |
|---|---|---|---|---|
| 本地 Chrome (`--remote-debugging-port`) / `/browser connect` | ✓ | ✓ 完整工作流 | ✓ | ✓ |
| Browserbase | ✓ (通过桥接) | ✓ 完整工作流 (通过桥接) | ✓ | ✓ |
| Camofox | ✗ 无 CDP (仅 REST) | ✗ | 通过 DOM 快照部分支持 | ✗ |

**Browserbase 特性。** Browserbase 的 CDP 代理内部使用 Playwright，并在约 10 毫秒内自动关闭原生对话框，因此 `Page.handleJavaScriptDialog` 无法跟上。监管器通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个桥接脚本，该脚本用同步 XHR 请求到一个特殊主机 (`hermes-dialog-bridge.invalid`) 来覆盖 `window.alert`/`confirm`/`prompt`。`Fetch.enable` 会在这些 XHR 请求触及网络之前拦截它们——对话框变成了监管器捕获的 `Fetch.requestPaused` 事件，而 `respond_to_dialog` 通过 `Fetch.fulfillRequest` 完成，并附带一个注入脚本解码的 JSON 主体。

从页面的角度来看，`prompt()` 仍然返回 Agent 提供的字符串。从 Agent 的角度来看，无论哪种方式，都是相同的 `browser_dialog(action=...)` API。

Camofox 不受支持——没有 CDP 接口，仅支持 REST。

## 架构

### CDPSupervisor

每个 Hermes `task_id` 在后台守护线程中运行一个 `asyncio.Task`。持有一个到后端 CDP 端点的持久 WebSocket 连接。维护：

-   **对话框队列** — `List[PendingDialog]`，包含 `{id, type, message, default_prompt, session_id, opened_at}`
-   **框架树** — `Dict[frame_id, FrameInfo]`，包含父子关系、URL、来源、是否为跨域子会话
-   **会话映射** — `Dict[session_id, SessionInfo]`，以便交互工具可以将 OOPIF 操作路由到正确的附加会话
-   **最近的控制台错误** — 最近 50 个错误的环形缓冲区，用于诊断

附加时订阅：

-   `Page.enable` — `javascriptDialogOpening`, `frameAttached`, `frameNavigated`, `frameDetached`
-   `Runtime.enable` — `executionContextCreated`, `consoleAPICalled`, `exceptionThrown`
-   `Target.setAutoAttach {autoAttach: true, flatten: true}` — 暴露子 OOPIF 目标；监管器在每个目标上启用 `Page`+`Runtime`

通过快照锁进行线程安全的状态访问；工具处理程序（同步）读取冻结的快照而无需等待。

### 生命周期

-   **启动：** `SupervisorRegistry.get_or_start(task_id, cdp_url)` — 由 `browser_navigate`、Browserbase 会话创建、`/browser connect` 调用。幂等。
-   **停止：** 会话拆卸或 `/browser disconnect`。取消 asyncio 任务，关闭 WebSocket，丢弃状态。
-   **重新绑定：** 如果 CDP URL 发生变化（用户重新连接到新的 Chrome），旧的监管器会停止，并启动一个新的——状态永远不会在不同端点之间复用。

### 对话框策略

可通过 `config.yaml` 中的 `browser.dialog_policy` 配置：

-   **`must_respond`** (默认) — 捕获，在 `browser_snapshot` 中暴露，等待显式的 `browser_dialog(action=...)` 调用。在 300 秒安全超时后若仍无响应，则自动关闭并记录日志。防止有问题的 Agent 永远阻塞。
-   `auto_dismiss` — 记录并立即关闭；Agent 事后通过 `browser_snapshot` 内的 `browser_state` 看到它。
-   `auto_accept` — 记录并接受（对于 `beforeunload` 很有用，当工作流希望干净地导航离开时）。

策略是按任务设置的；没有按对话框的覆盖。

## Agent 接口

### `browser_dialog` 工具

```
browser_dialog(action, prompt_text=None, dialog_id=None)
```

-   `action="accept"` / `"dismiss"` → 响应指定的或唯一的待处理对话框（必需）
-   `prompt_text=...` → 提供给 `prompt()` 对话框的文本
-   `dialog_id=...` → 当多个对话框排队时用于消除歧义（罕见情况）

该工具仅用于响应。Agent 在调用前从 `browser_snapshot` 输出中读取待处理的对话框。

### `browser_snapshot` 扩展

当附加了监管器时，在现有的快照输出中添加三个可选字段：

```json
{
  "pending_dialogs": [
    {"id": "d-1", "type": "alert", "message": "Hello", "opened_at": 1650000000.0}
  ],
  "recent_dialogs": [
    {"id": "d-1", "type": "alert", "message": "...", "opened_at": 1650000000.0,
     "closed_at": 1650000000.1, "closed_by": "remote"}
  ],
  "frame_tree": {
    "top": {"frame_id": "FRAME_A", "url": "https://example.com/", "origin": "https://example.com"},
    "children": [
      {"frame_id": "FRAME_B", "url": "about:srcdoc", "is_oopif": false},
      {"frame_id": "FRAME_C", "url": "https://ads.example.net/", "is_oopif": true, "session_id": "SID_C"}
    ],
    "truncated": false
  }
}
```

-   **`pending_dialogs`** — 当前阻塞页面 JS 线程的对话框。Agent 必须调用 `browser_dialog(action=...)` 来响应。在 Browserbase 上为空，因为其 CDP 代理会在约 10 毫秒内自动关闭对话框。
-   **`recent_dialogs`** — 最多 20 个最近关闭的对话框的环形缓冲区，带有 `closed_by` 标签：`"agent"`（我们响应了）、`"auto_policy"`（本地 auto_dismiss/auto_accept）、`"watchdog"`（达到 must_respond 超时）或 `"remote"`（浏览器/后端为我们关闭了它，例如 Browserbase）。这就是 Browserbase 上的 Agent 仍然可以了解发生了什么的方式。
-   **`frame_tree`** — 框架结构，包括跨域 (OOPIF) 子框架。限制为 30 个条目 + OOPIF 深度 2，以限制广告密集型页面上的快照大小。当达到限制时，会暴露 `truncated: true`；需要完整树的 Agent 可以使用 `browser_cdp` 配合 `Page.getFrameTree`。

所有这些都没有新的工具模式接口——Agent 读取它已经请求的快照。

### 可用性门控

这两个接口都受 `_browser_cdp_check` 门控（监管器只能在 CDP 端点可达时运行）。在 Camofox / 无后端会话上，对话框工具被隐藏，快照省略新字段——不会增加模式膨胀。

## 跨域 iframe 交互

`browser_cdp(frame_id=...)` 通过监管器已连接的 WebSocket，使用 OOPIF 的子 `sessionId` 来路由 CDP 调用（特别是 `Runtime.evaluate`）。Agent 从 `browser_snapshot.frame_tree.children[]` 中挑选出 `is_oopif=true` 的 frame_ids，并将它们传递给 `browser_cdp`。对于同源 iframe（没有专用的 CDP 会话），Agent 使用来自顶层 `Runtime.evaluate` 的 `contentWindow`/`contentDocument` 代替——当 `frame_id` 属于非 OOPIF 时，监管器会抛出一个指向该备用方法的错误。

在 Browserbase 上，这是 iframe 交互唯一可靠的路径——无状态的 CDP 连接（每次 `browser_cdp` 调用时打开）会遇到签名 URL 过期，而监管器的长连接保持有效的会话。

## 文件布局

-   `tools/browser_supervisor.py` — `CDPSupervisor`, `SupervisorRegistry`, `PendingDialog`, `FrameInfo`
-   `tools/browser_dialog_tool.py` — `browser_dialog` 工具处理程序
-   `tools/browser_tool.py` — `browser_navigate` 启动钩子, `browser_snapshot` 合并, `/browser connect` 重新附加, `_cleanup_browser_session` 拆卸
-   `toolsets.py` — 在 `browser`, `hermes-acp`, `hermes-api-server` 和核心工具集中注册 `browser_dialog`（受 CDP 可达性门控）
-   `hermes_cli/config.py` — `browser.dialog_policy` 和 `browser.dialog_timeout_s` 默认值

## 非目标

-   检测/交互 Camofox（上游空白；单独跟踪）
-   将对话框/框架事件实时流式传输给用户（需要消息网关钩子）
-   跨会话持久化对话框历史记录（仅内存）
-   每个 iframe 的对话框策略（Agent 可以通过 `dialog_id` 表达这一点）
-   替换 `browser_cdp` — 它仍然是处理长尾需求（cookies、视口、网络节流）的逃生通道

## 测试

单元测试 (`tests/tools/test_browser_supervisor.py`) 使用一个 asyncio 模拟 CDP 服务器，该服务器使用足够的协议来执行所有状态转换：附加、启用、导航、对话框触发、对话框关闭、框架附加/分离、子目标附加、会话拆卸。真实后端 E2E（Browserbase + 本地 Chromium 系列浏览器）是手动的——通过 `/browser connect` 连接到活动的 Chromium 系列浏览器，并运行上述描述的对话框/框架测试用例。