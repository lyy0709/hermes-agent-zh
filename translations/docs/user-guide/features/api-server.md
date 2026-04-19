---
sidebar_position: 14
title: "API 服务器"
description: "将 hermes-agent 作为 OpenAI 兼容的 API 暴露给任何前端使用"
---

# API 服务器

API 服务器将 hermes-agent 暴露为一个 OpenAI 兼容的 HTTP 端点。任何支持 OpenAI 格式的前端 —— Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及数百个其他应用 —— 都可以连接到 hermes-agent 并将其用作后端。

你的 Agent 会使用其完整的工具集（终端、文件操作、网络搜索、记忆、技能）处理请求并返回最终响应。在流式传输时，工具进度指示器会内联显示，以便前端可以展示 Agent 正在执行的操作。

## 快速开始

### 1. 启用 API 服务器

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅在浏览器必须直接调用 Hermes 时设置
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动消息网关

```bash
hermes gateway
```

你将看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端

将任何 OpenAI 兼容的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端 —— 请参阅 [Open WebUI 集成指南](/docs/user-guide/messaging/open-webui) 获取分步说明。

## 端点

### POST /v1/chat/completions

标准的 OpenAI Chat Completions 格式。无状态 —— 完整的对话通过 `messages` 数组包含在每个请求中。

**请求：**
```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "You are a Python expert."},
    {"role": "user", "content": "Write a fibonacci function"}
  ],
  "stream": false
}
```

**响应：**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "Here's a fibonacci function..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250}
}
```

**流式传输** (`"stream": true`)：返回服务器发送事件（SSE），包含逐 Token 的响应块。对于 **Chat Completions**，流使用标准的 `chat.completion.chunk` 事件以及 Hermes 自定义的 `hermes.tool.progress` 事件用于工具启动的用户体验。对于 **Responses**，流使用 OpenAI Responses 事件类型，例如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。

**流中的工具进度**：
- **Chat Completions**：Hermes 发出 `event: hermes.tool.progress` 事件，用于工具启动的可见性，而不会污染持久化的助手文本。
- **Responses**：Hermes 在 SSE 流期间发出符合规范的 `function_call` 和 `function_call_output` 输出项，因此客户端可以实时渲染结构化的工具 UI。

### POST /v1/responses

OpenAI Responses API 格式。通过 `previous_response_id` 支持服务器端会话状态 —— 服务器存储完整的对话历史记录（包括工具调用和结果），因此多轮上下文得以保留，无需客户端管理。

**请求：**
```json
{
  "model": "hermes-agent",
  "input": "What files are in my project?",
  "instructions": "You are a helpful coding assistant.",
  "store": true
}
```

**响应：**
```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "hermes-agent",
  "output": [
    {"type": "function_call", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1"},
    {"type": "function_call_output", "call_id": "call_1", "output": "README.md src/ tests/"},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Your project has..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

#### 使用 previous_response_id 进行多轮对话

链接响应以在多个轮次中保持完整上下文（包括工具调用）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务器从存储的响应链中重建完整的对话 —— 所有之前的工具调用和结果都被保留。链式请求也共享同一个会话，因此多轮对话在仪表板和会话历史中显示为单个条目。

#### 命名对话

使用 `conversation` 参数代替跟踪响应 ID：

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务器会自动链接到该对话中的最新响应。类似于网关会话的 `/title` 命令。

### GET /v1/responses/\{id\}

按 ID 检索先前存储的响应。

### DELETE /v1/responses/\{id\}

删除存储的响应。

### GET /v1/models

将 Agent 列为可用模型。广告的模型名称默认为 [配置文件](/docs/user-guide/profiles) 名称（或默认配置文件的 `hermes-agent`）。大多数前端需要此端点进行模型发现。

### GET /health

健康检查。返回 `{"status": "ok"}`。也可在 **GET /v1/health** 访问，适用于期望 `/v1/` 前缀的 OpenAI 兼容客户端。

### GET /health/detailed

扩展的健康检查，同时报告活动会话、运行中的 Agent 和资源使用情况。适用于监控/可观测性工具。

## Runs API（流式友好的替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses`，服务器还暴露了一个 **runs** API，用于长格式会话，客户端希望订阅进度事件而不是自己管理流式传输。

### POST /v1/runs

创建一个新的 Agent 运行。返回一个 `run_id`，可用于订阅进度事件。
### GET /v1/runs/\{run_id\}/events

服务器发送事件流，用于传输运行的工具调用进度、Token 增量以及生命周期事件。专为希望在不丢失状态的情况下连接/断开连接的仪表板和富客户端设计。

## 作业 API（后台定时任务）

服务器暴露了一个轻量级的作业 CRUD 接口，用于从远程客户端管理定时/后台 Agent 运行。所有端点都受相同的 Bearer 认证保护。

### GET /api/jobs

列出所有定时作业。

### POST /api/jobs

创建一个新的定时作业。请求体接受与 `hermes cron` 相同的格式——提示词、计划、技能、提供商覆盖、交付目标。

### GET /api/jobs/\{job_id\}

获取单个作业的定义和上次运行状态。

### PATCH /api/jobs/\{job_id\}

更新现有作业的字段（提示词、计划等）。支持部分更新，字段将被合并。

### DELETE /api/jobs/\{job_id\}

删除作业。同时会取消任何正在进行的运行。

### POST /api/jobs/\{job_id\}/pause

暂停作业而不删除它。下次计划运行的时间戳将被挂起，直到恢复。

### POST /api/jobs/\{job_id\}/resume

恢复先前暂停的作业。

### POST /api/jobs/\{job_id\}/run

立即触发作业运行，不受计划限制。

## 系统提示词处理

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent 会**将其叠加在**其核心系统提示词之上。你的 Agent 将保留其所有工具、记忆和技能——前端的系统提示词会添加额外的指令。

这意味着你可以为每个前端定制行为，而不会丢失能力：
- Open WebUI 系统提示词："你是一个 Python 专家。始终包含类型提示。"
- Agent 仍然拥有终端、文件工具、网络搜索、记忆等能力。

## 认证

通过 `Authorization` 请求头进行 Bearer Token 认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果你需要浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

:::warning 安全
API 服务器授予对 hermes-agent 工具集的完全访问权限，**包括终端命令**。当绑定到非环回地址（如 `0.0.0.0`）时，**必须**设置 `API_SERVER_KEY`。同时，保持 `API_SERVER_CORS_ORIGINS` 范围狭窄以控制浏览器访问。

默认绑定地址（`127.0.0.1`）仅用于本地使用。默认情况下禁用浏览器访问；仅对明确受信任的来源启用。
:::

## 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅限 localhost） |
| `API_SERVER_KEY` | _(无)_ | Bearer Token 用于认证 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许的浏览器来源 |
| `API_SERVER_MODEL_NAME` | _(配置文件名称)_ | `/v1/models` 上的模型名称。默认为配置文件名称，对于默认配置文件则为 `hermes-agent`。 |

### config.yaml

```yaml
# 暂不支持 — 请使用环境变量。
# config.yaml 支持将在未来版本中提供。
```

## 安全头

所有响应都包含安全头：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止 Referrer 泄漏

## CORS

API 服务器默认**不**启用浏览器 CORS。

对于直接浏览器访问，请设置明确的允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 时：
- **预检响应** 包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应** 包含 CORS 头，以便浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求头——客户端可以发送它以实现去重（响应按密钥缓存 5 分钟）

大多数已记录的前端（如 Open WebUI）采用服务器到服务器连接，完全不需要 CORS。

## 兼容的前端

任何支持 OpenAI API 格式的前端都可以使用。已测试/记录的集成：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/docs/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义提供商端点 |
| LibreChat | 34k | 在 librechat.yaml 中设置自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI 提供商 |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API 主机设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |

## 使用配置文件的多用户设置

要为多个用户提供他们自己独立的 Hermes 实例（独立的配置、记忆、技能），请使用[配置文件](/docs/user-guide/profiles)：

```bash
# 为每个用户创建一个配置文件
hermes profile create alice
hermes profile create bob

# 在每个配置文件的不同端口上配置 API 服务器
hermes -p alice config set API_SERVER_ENABLED true
hermes -p alice config set API_SERVER_PORT 8643
hermes -p alice config set API_SERVER_KEY alice-secret

hermes -p bob config set API_SERVER_ENABLED true
hermes -p bob config set API_SERVER_PORT 8644
hermes -p bob config set API_SERVER_KEY bob-secret

# 启动每个配置文件的消息网关
hermes -p alice gateway &
hermes -p bob gateway &
```

每个配置文件的 API 服务器会自动将配置文件名称作为模型 ID 进行通告：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，将每个添加为单独的连接。模型下拉菜单将显示 `alice` 和 `bob` 作为不同的模型，每个都由一个完全隔离的 Hermes 实例支持。详情请参阅 [Open WebUI 指南](/docs/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 限制

- **响应存储** — 存储的响应（用于 `previous_response_id`）保存在 SQLite 中，并在消息网关重启后保留。最多存储 100 个响应（LRU 淘汰）。
- **不支持文件上传** — 目前尚不支持通过 API 上传文件进行视觉/文档分析。
- **模型字段是装饰性的** — 请求中的 `model` 字段会被接受，但实际使用的 LLM 模型是在服务器端的 config.yaml 中配置的。
## 代理模式

该 API 服务器也作为**消息网关代理模式**的后端。当另一个 Hermes 消息网关实例配置了指向此 API 服务器的 `GATEWAY_PROXY_URL` 时，它会将所有消息转发到这里，而不是运行自己的 Agent。这使得拆分部署成为可能——例如，一个处理 Matrix E2EE 的 Docker 容器将消息中继到宿主机端的 Agent。

完整的设置指南请参阅 [Matrix 代理模式](/docs/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)。