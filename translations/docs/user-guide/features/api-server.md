---
sidebar_position: 14
title: "API 服务器"
description: "将 hermes-agent 作为 OpenAI 兼容的 API 暴露，供任何前端使用"
---

# API 服务器

API 服务器将 hermes-agent 暴露为一个 OpenAI 兼容的 HTTP 端点。任何支持 OpenAI 格式的前端 —— Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及数百个其他前端 —— 都可以连接到 hermes-agent 并将其用作后端。

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

**内联图像输入：** 用户消息可以将 `content` 作为 `text` 和 `image_url` 部分的数组发送。支持远程 `http(s)` URL 和 `data:image/...` URL：

```json
{
  "model": "hermes-agent",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.png", "detail": "high"}}
      ]
    }
  ]
}
```

上传的文件（`file` / `input_file` / `file_id`）和非图像的 `data:` URL 将返回 `400 unsupported_content_type`。

**流式传输** (`"stream": true`)：返回服务器发送事件（SSE），包含逐 Token 的响应块。对于 **Chat Completions**，流使用标准的 `chat.completion.chunk` 事件以及 Hermes 自定义的 `hermes.tool.progress` 事件，用于工具启动的用户体验。对于 **Responses**，流使用 OpenAI Responses 事件类型，例如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。

**流中的工具进度：**
- **Chat Completions**：Hermes 发出 `event: hermes.tool.progress` 事件，用于工具启动的可见性，而不会污染持久化的助手文本。
- **Responses**：Hermes 在 SSE 流期间发出符合规范原生的 `function_call` 和 `function_call_output` 输出项，因此客户端可以实时渲染结构化的工具 UI。

### POST /v1/responses

OpenAI Responses API 格式。支持通过 `previous_response_id` 实现服务器端会话状态 —— 服务器存储完整的对话历史记录（包括工具调用和结果），因此多轮上下文得以保留，无需客户端管理。

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

**内联图像输入：** `input[].content` 可以包含 `input_text` 和 `input_image` 部分。支持远程 URL 和 `data:image/...` URL：

```json
{
  "model": "hermes-agent",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "Describe this screenshot."},
        {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0K..."}
      ]
    }
  ]
}
```

上传的文件（`input_file` / `file_id`）和非图像的 `data:` URL 将返回 `400 unsupported_content_type`。

#### 使用 previous_response_id 进行多轮对话

链接响应以在多个回合中保持完整上下文（包括工具调用）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务器从存储的响应链重建完整的对话 —— 所有之前的工具调用和结果都被保留。链式请求也共享同一个会话，因此多轮对话在仪表板和会话历史记录中显示为单个条目。

#### 命名对话

使用 `conversation` 参数代替跟踪响应 ID：

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务器会自动链接到该对话中的最新响应。类似于消息网关会话的 `/title` 命令。
### GET /v1/responses/\{id\}

根据 ID 检索先前存储的响应。

### DELETE /v1/responses/\{id\}

删除一个已存储的响应。

### GET /v1/models

将 Agent 列为可用模型。对外公布的模型名称默认为[配置文件](/docs/user-guide/profiles)的名称（对于默认配置文件则为 `hermes-agent`）。大多数前端进行模型发现时都需要此端点。

### GET /v1/capabilities

返回 API 服务器稳定接口的机器可读描述，供外部 UI、编排器和插件桥接器使用。

```json
{
  "object": "hermes.api_server.capabilities",
  "platform": "hermes-agent",
  "model": "hermes-agent",
  "auth": {"type": "bearer", "required": true},
  "features": {
    "chat_completions": true,
    "responses_api": true,
    "run_submission": true,
    "run_status": true,
    "run_events_sse": true,
    "run_stop": true
  }
}
```

在集成仪表板、浏览器 UI 或控制平面时使用此端点，以便它们能够发现正在运行的 Hermes 版本是否支持运行、流式传输、取消和会话连续性，而无需依赖私有的 Python 内部实现。

### GET /health

健康检查。返回 `{"status": "ok"}`。也可通过 **GET /v1/health** 访问，以兼容期望 `/v1/` 前缀的 OpenAI 客户端。

### GET /health/detailed

扩展健康检查，同时报告活跃会话、运行中的 Agent 和资源使用情况。对监控/可观测性工具很有用。

## 运行 API（支持流式传输的替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses`，服务器还暴露了一个**运行** API，用于长会话场景，客户端可以订阅进度事件，而无需自行管理流式传输。

### POST /v1/runs

创建一个新的 Agent 运行。返回一个 `run_id`，可用于订阅进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

运行接受一个简单的 `input` 字符串以及可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id`。当提供 `session_id` 时，Hermes 会在运行状态中显示它，以便外部 UI 可以将运行与其自己的会话 ID 关联起来。

### GET /v1/runs/\{run_id\}

轮询当前的运行状态。这对于需要状态但不想保持 SSE 连接打开的仪表板，或者在导航后重新连接的 UI 很有用。

```json
{
  "object": "hermes.run",
  "run_id": "run_abc123",
  "status": "completed",
  "session_id": "space-session",
  "model": "hermes-agent",
  "output": "Done.",
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

在终端状态（`completed`、`failed` 或 `cancelled`）之后，状态会短暂保留，以便轮询和 UI 协调。

### GET /v1/runs/\{run_id\}/events

服务器发送事件流，包含运行的工具调用进度、Token 增量以及生命周期事件。专为希望在不丢失状态的情况下连接/断开的仪表板和富客户端设计。

### POST /v1/runs/\{run_id\}/stop

中断正在运行的 Agent 轮次。该端点会立即返回 `{"status": "stopping"}`，同时 Hermes 会要求活跃的 Agent 在下一个安全的中断点停止。

## 任务 API（后台调度工作）

服务器暴露了一个轻量级的任务 CRUD 接口，用于从远程客户端管理调度/后台 Agent 运行。所有端点都受相同的 Bearer 认证保护。

### GET /api/jobs

列出所有已调度的任务。

### POST /api/jobs

创建一个新的调度任务。请求体接受与 `hermes cron` 相同的格式 —— 提示词、调度计划、技能、提供商覆盖、交付目标。

### GET /api/jobs/\{job_id\}

获取单个任务的定义和上次运行状态。

### PATCH /api/jobs/\{job_id\}

更新现有任务的字段（提示词、调度计划等）。支持部分更新合并。

### DELETE /api/jobs/\{job_id\}

删除一个任务。同时会取消任何正在进行的运行。

### POST /api/jobs/\{job_id\}/pause

暂停一个任务而不删除它。下次计划运行的时间戳将被挂起，直到恢复。

### POST /api/jobs/\{job_id\}/resume

恢复先前暂停的任务。

### POST /api/jobs/\{job_id\}/run

立即触发任务运行，不受调度计划限制。

## 系统提示词处理

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent 会**将其叠加在**其核心系统提示词之上。你的 Agent 将保留其所有工具、记忆和技能 —— 前端的系统提示词会添加额外的指令。

这意味着你可以针对每个前端定制行为，而不会丢失功能：
- Open WebUI 系统提示词："你是一个 Python 专家。始终包含类型提示。"
- Agent 仍然拥有终端、文件工具、网络搜索、记忆等功能。

## 认证

通过 `Authorization` 请求头进行 Bearer Token 认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果你需要浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许来源列表。

:::warning 安全
API 服务器授予对 hermes-agent 工具集的完全访问权限，**包括终端命令**。当绑定到非环回地址（如 `0.0.0.0`）时，**必须**设置 `API_SERVER_KEY`。同时，保持 `API_SERVER_CORS_ORIGINS` 范围狭窄以控制浏览器访问。

默认的绑定地址（`127.0.0.1`）仅用于本地使用。默认情况下禁用浏览器访问；仅对明确信任的来源启用。
:::

## 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅限 localhost） |
| `API_SERVER_KEY` | _(无)_ | Bearer Token 用于认证 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许浏览器来源 |
| `API_SERVER_MODEL_NAME` | _(配置文件名称)_ | `/v1/models` 上的模型名称。默认为配置文件名称，对于默认配置文件则为 `hermes-agent`。 |

### config.yaml

```yaml
# 暂不支持 —— 请使用环境变量。
# 对 config.yaml 的支持将在未来版本中提供。
```
## 安全头部

所有响应都包含安全头部：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止来源信息泄漏

## CORS

API 服务器默认**不**启用浏览器 CORS。

如需直接通过浏览器访问，请设置明确的允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 后：
- **预检响应**包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应**包含 CORS 头部，以便浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求头部 — 客户端可以发送它以实现去重（响应会按键缓存 5 分钟）

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

## 使用配置文件的多人设置

要为多个用户提供各自隔离的 Hermes 实例（独立的配置、记忆、技能），请使用[配置文件](/docs/user-guide/profiles)：

```bash
# 为每个用户创建配置文件
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

在 Open WebUI 中，将每个添加为单独的连接。模型下拉菜单会显示 `alice` 和 `bob` 作为不同的模型，每个都由一个完全隔离的 Hermes 实例支持。详情请参阅 [Open WebUI 指南](/docs/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 限制

- **响应存储** — 存储的响应（用于 `previous_response_id`）保存在 SQLite 中，并在消息网关重启后保留。最多存储 100 个响应（LRU 淘汰）。
- **不支持文件上传** — 在 `/v1/chat/completions` 和 `/v1/responses` 上都支持内联图像，但不支持通过 API 上传文件（`file`、`input_file`、`file_id`）和非图像文档输入。
- **模型字段是装饰性的** — 请求中的 `model` 字段会被接受，但实际使用的 LLM 模型是在服务器端的 config.yaml 中配置的。

## 代理模式

API 服务器也用作**消息网关代理模式**的后端。当另一个 Hermes 消息网关实例配置了 `GATEWAY_PROXY_URL` 指向此 API 服务器时，它会将所有消息转发到这里，而不是运行自己的 Agent。这支持拆分部署 — 例如，一个处理 Matrix E2EE 的 Docker 容器将消息中继到主机端的 Agent。

完整设置指南请参阅 [Matrix 代理模式](/docs/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)。