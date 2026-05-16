---
sidebar_position: 8
title: "编程式集成"
description: "三种用于从外部程序驱动 hermes-agent 的协议：ACP、TUI 消息网关 JSON-RPC 和 OpenAI 兼容的 HTTP API"
---

# 编程式集成

Hermes 提供了三种协议，用于从外部程序（如 IDE 插件、自定义 UI、CI 流水线、嵌入式子 Agent）驱动 Agent。请根据您的传输方式和消费者选择适合的协议。

| 协议 | 传输方式 | 最适合 | 定义文件 |
|----------|-----------|----------|------------|
| **ACP** | 基于 stdio 的 JSON-RPC | 已支持 [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) 的 IDE 客户端（VS Code、Zed、JetBrains） | `acp_adapter/` |
| **TUI 消息网关** | 基于 stdio（或 WebSocket）的 JSON-RPC | 希望对会话、斜杠命令、审批和流式事件进行细粒度控制的自定义宿主程序 | `tui_gateway/server.py` |
| **API 服务器** | HTTP + 服务器发送事件 | 兼容 OpenAI 的前端（Open WebUI、LobeChat、LibreChat…）以及语言无关的 Web 客户端 | `gateway/platforms/api_server.py` |

这三种协议都驱动同一个 `AIAgent` 核心。它们仅在传输格式和暴露的功能集上有所不同。

---

## ACP (Agent Client Protocol)

`hermes acp` 启动一个基于 stdio 的 JSON-RPC 服务器，使用 ACP 协议。VS Code（Zed Industries 的 ACP 扩展）、Zed 以及任何安装了 ACP 插件的 JetBrains IDE 在生产环境中都使用此协议。

暴露的能力包括：会话创建、提示词提交、流式 Agent 消息块、工具调用事件、权限请求、会话分叉、取消和身份验证。工具输出会被渲染成 IDE 能理解的 ACP `Diff`/`ToolCall` 内容块。

完整的生命周期、事件桥接和审批流程：[ACP 内部机制](./acp-internals)。

```bash
hermes acp                  # 在 stdio 上提供 ACP 服务
hermes acp --bootstrap      # 为支持 ACP 的 IDE 打印安装代码片段
```

---

## TUI 消息网关 JSON-RPC

`tui_gateway/server.py` 是 Ink TUI (`hermes --tui`) 和嵌入式仪表板 PTY 桥接器所使用的协议。任何外部宿主程序都可以通过 stdio（或通过 `tui_gateway/ws.py` 使用 WebSocket）使用相同的协议。

### 方法目录（部分）

```
prompt.submit           prompt.background       session.steer
session.create          session.list            session.interrupt
session.history         session.compress        session.branch
session.title           session.usage           session.status
clarify.respond         sudo.respond            secret.respond
approval.respond        config.set / config.get commands.catalog
command.resolve         command.dispatch        cli.exec
reload.mcp              reload.env              process.stop
delegation.status       subagent.interrupt      spawn_tree.save / list / load
terminal.resize         clipboard.paste         image.attach
```

### 流式返回的事件

`message.delta`, `message.complete`, `tool.start`, `tool.progress`, `tool.complete`, `approval.request`, `clarify.request`, `sudo.request`, `secret.request`, `gateway.ready`，以及会话生命周期和错误事件。

### Pi 风格 RPC 映射

Pi-mono RPC 规范（[issue #360](https://github.com/NousResearch/hermes-agent/issues/360)）中的每个命令在 TUI 消息网关中都有对应的等效命令：

| Pi 命令 | Hermes 等效命令 |
|------------|-------------------|
| `prompt` | `prompt.submit`（或 ACP `session/prompt`） |
| `steer` | `session.steer` |
| `follow_up` | `prompt.submit`（在当前轮次后排队） |
| `abort` | `session.interrupt` |
| `set_model` | 为 `/model <provider:model>` 执行 `command.dispatch`（会话中，持久化） |
| `compact` | `session.compress` |
| `get_state` | `session.status` |
| `get_messages` | `session.history` |
| `switch_session` | `session.resume` |
| `fork` | `session.branch` |
| `ui_request` / `ui_response` | `clarify.respond` / `sudo.respond` / `secret.respond` / `approval.respond` |

---

## OpenAI 兼容的 API 服务器

`gateway/platforms/api_server.py` 通过 HTTP 暴露 hermes 的功能，供任何已支持 OpenAI 格式的客户端使用。当您想要一个 Web 前端、一个由 curl 驱动的 CI 运行器或一个非 Python 消费者时，这非常有用。

端点：

```
POST /v1/chat/completions        OpenAI Chat Completions（通过 SSE 流式传输）
POST /v1/responses               OpenAI Responses API（有状态）
POST /v1/runs                    启动一个运行，返回 run_id (202)
GET  /v1/runs/{id}               运行状态
GET  /v1/runs/{id}/events        生命周期事件的 SSE 流
POST /v1/runs/{id}/approval      处理待定的审批
POST /v1/runs/{id}/stop          中断运行
GET  /v1/capabilities            机器可读的功能标志
GET  /v1/models                  列出 hermes-agent
GET  /health, /health/detailed
```

设置、请求头（`X-Hermes-Session-Id`、`X-Hermes-Session-Key`）和前端连接：[API 服务器](../user-guide/features/api-server)。

---

## 我应该使用哪一个？

- **您正在编写 IDE 插件，并且该 IDE 已支持 ACP** → ACP。IDE 端无需进行任何协议工作。
- **您正在编写自定义桌面/Web/TUI 宿主程序，并希望拥有 Hermes 的每一项功能**（斜杠命令、审批、澄清、多 Agent、会话分支）→ TUI 消息网关 JSON-RPC。
- **您希望使用任何兼容 OpenAI 的前端、一个语言无关的 HTTP 客户端，或由 curl 驱动的自动化** → API 服务器。
- **您希望在进程内嵌入 Python 代码，而不使用子进程** → 直接导入 `run_agent.AIAgent`。请参阅 [Agent 循环](./agent-loop)。

---

## 模型热切换

会话中的模型切换在所有界面上都有效——其底层实现是 `/model` 斜杠命令。

- **CLI / TUI:** `/model claude-sonnet-4` 或 `/model openrouter:anthropic/claude-sonnet-4.6`
- **TUI 消息网关 RPC:** 使用 `{"command": "/model claude-sonnet-4"}` 执行 `command.dispatch`
- **ACP:** IDE 将斜杠命令作为提示词发送；Agent 会调度它
- **API 服务器:** 在请求体中包含 `model` 字段或设置 `X-Hermes-Model`

内置了提供商感知的解析（相同的模型名称会根据您当前使用的提供商选择正确的格式）。请参阅 `hermes_cli/model_switch.py`。

---

## 关于 `--mode rpc` 的说明

Hermes 没有 `--mode rpc` 标志。上述三种协议已经涵盖了所有用例——ACP 用于 IDE 协议客户端，TUI 消息网关用于 stdio JSON-RPC 宿主程序，API 服务器用于 HTTP。如果您发现确实存在这三种协议都无法满足的空白，请提交一个 issue，并说明您正在构建的具体消费者。