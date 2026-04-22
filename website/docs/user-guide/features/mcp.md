---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器，并精确控制 Hermes 加载哪些 MCP 工具"
---

# MCP (Model Context Protocol)

MCP 允许 Hermes Agent 连接到外部工具服务器，使 Agent 能够使用 Hermes 自身之外的各类工具——例如 GitHub、数据库、文件系统、浏览器栈、内部 API 等等。

如果你曾希望 Hermes 使用一个已存在于别处的工具，MCP 通常是实现这一目标最简洁的方式。

## MCP 带来的能力

- 无需先编写原生 Hermes 工具，即可访问外部工具生态系统
- 可在同一配置中同时使用本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，为 MCP 资源和提示词提供实用程序包装器
- 支持按服务器进行过滤，以便仅暴露你真正希望 Hermes 看到的 MCP 工具

## 快速开始

1.  安装 MCP 支持（如果使用了标准安装脚本，则已包含）：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

2.  在 `~/.hermes/config.yaml` 中添加一个 MCP 服务器：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3.  启动 Hermes：

```bash
hermes chat
```

4.  要求 Hermes 使用基于 MCP 的能力。

例如：

```text
列出 /home/user/projects 中的文件并总结仓库结构。
```

Hermes 将发现 MCP 服务器的工具，并像使用其他任何工具一样使用它们。

## 两种 MCP 服务器

### Stdio 服务器

Stdio 服务器作为本地子进程运行，并通过 stdin/stdout 进行通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况下使用 stdio 服务器：
- 服务器安装在本地
- 你需要低延迟访问本地资源
- 你正在参考展示 `command`、`args` 和 `env` 的 MCP 服务器文档

### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

在以下情况下使用 HTTP 服务器：
- MCP 服务器托管在其他地方
- 你的组织暴露了内部 MCP 端点
- 你不希望 Hermes 为该集成启动本地子进程

## 基础配置参考

Hermes 从 `~/.hermes/config.yaml` 中的 `mcp_servers` 下读取 MCP 配置。

### 通用键

| 键 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | Stdio MCP 服务器的可执行文件 |
| `args` | 列表 | Stdio 服务器的参数 |
| `env` | 映射 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 端点 |
| `headers` | 映射 | 远程服务器的 HTTP 请求头 |
| `timeout` | 数字 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 初始连接超时时间 |
| `enabled` | 布尔值 | 如果为 `false`，Hermes 将完全跳过该服务器 |
| `tools` | 映射 | 按服务器进行的工具过滤和实用程序策略 |

### 最小化 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 最小化 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## Hermes 如何注册 MCP 工具

Hermes 为 MCP 工具添加前缀，以避免与内置名称冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

在实践中，你通常不需要手动调用带前缀的名称——Hermes 会看到该工具并在正常推理过程中选择它。

## MCP 实用工具

当服务器支持时，Hermes 还会围绕 MCP 资源和提示词注册实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具按服务器注册，遵循相同的前缀模式，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要说明

这些实用工具现在具备能力感知：
- 仅当 MCP 会话实际支持资源操作时，Hermes 才会注册资源实用工具
- 仅当 MCP 会话实际支持提示词操作时，Hermes 才会注册提示词实用工具

因此，一个暴露了可调用工具但没有资源/提示词的服务器将不会获得这些额外的包装器。

## 按服务器过滤

你可以控制每个 MCP 服务器向 Hermes 提供哪些工具，从而实现对工具命名空间的精细管理。

### 完全禁用服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果 `enabled: false`，Hermes 将完全跳过该服务器，甚至不会尝试连接。

### 白名单服务器工具

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues]
```

只有这些 MCP 服务器工具会被注册。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

除了被排除的工具外，所有服务器工具都会被注册。

### 优先级规则

如果两者同时存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 优先。

### 也过滤实用工具

你也可以单独禁用 Hermes 添加的实用程序包装器：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 会禁用 `list_resources` 和 `read_resource`
- `tools.prompts: false` 会禁用 `list_prompts` 和 `get_prompt`

### 完整示例
```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues, search_code]
      prompts: false

  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer]
      resources: false

  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

## 如果所有内容都被过滤掉会怎样？

如果你的配置过滤掉了所有可调用工具，并且禁用或省略了所有支持的实用程序，Hermes 将不会为该服务器创建一个空的运行时 MCP 工具集。

这可以保持工具列表的整洁。

## 运行时行为

### 发现时机

Hermes 在启动时发现 MCP 服务器，并将其工具注册到常规的工具注册表中。

### 动态工具发现

MCP 服务器可以在运行时其可用工具发生变化时，通过发送 `notifications/tools/list_changed` 通知来告知 Hermes。当 Hermes 收到此通知时，它会自动重新获取服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp`。

这对于能力动态变化的 MCP 服务器非常有用（例如，加载新数据库模式时添加工具的服务器，或服务下线时移除工具的服务器）。

刷新操作受锁保护，因此来自同一服务器的快速连续通知不会导致重叠的刷新。提示词和资源变更通知（`prompts/list_changed`、`resources/list_changed`）会被接收，但尚未采取行动。

### 重新加载

如果你更改了 MCP 配置，请使用：

```text
/reload-mcp
```

这将从配置重新加载 MCP 服务器并刷新可用工具列表。对于服务器自身推送的运行时工具变更，请参阅上面的[动态工具发现](#动态工具发现)。

### 工具集

每个配置的 MCP 服务器在贡献至少一个已注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集层面更容易理解 MCP 服务器。

## 安全模型

### Stdio 环境变量过滤

对于 stdio 服务器，Hermes 不会盲目传递你的完整 shell 环境。

只有明确配置的 `env` 加上一个安全基线会被传递。这减少了意外泄露密钥的风险。

### 配置级别的暴露控制

新的过滤支持也是一种安全控制：
- 禁用你不希望模型看到的危险工具
- 对于敏感服务器，仅暴露最小化的白名单
- 当你不想暴露该功能面时，禁用资源/提示词包装器

## 使用示例

### 具有最小化问题管理功能的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue]
      prompts: false
      resources: false
```

使用方式：

```text
显示标记为 bug 的未解决问题，然后为不稳定的 MCP 重连行为草拟一个新问题。
```

### 移除了危险操作的 Stripe 服务器

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

使用方式：

```text
查找最近 10 笔失败的付款并总结常见的失败原因。
```

### 用于单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

使用方式：

```text
检查项目根目录并解释目录结构。
```

## 故障排除

### MCP 服务器无法连接

检查：

```bash
# 验证 MCP 依赖是否已安装（标准安装已包含）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

然后验证你的配置并重启 Hermes。

### 工具未出现

可能的原因：
- 服务器连接失败
- 发现失败
- 你的过滤器配置排除了这些工具
- 该服务器上不存在该实用程序功能
- 服务器被 `enabled: false` 禁用

如果你是有意过滤，这是预期行为。

### 为什么资源或提示词实用程序没有出现？

因为 Hermes 现在只在以下两个条件都满足时才注册这些包装器：
1. 你的配置允许它们
2. 服务器会话实际支持该功能

这是有意为之，以保持工具列表的真实性。

## MCP 采样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这允许 MCP 服务器请求 Hermes 代表其生成文本——对于需要 LLM 能力但没有自己模型访问权限的服务器非常有用。

采样功能默认对所有 MCP 服务器**启用**（当 MCP SDK 支持时）。可以在每个服务器的 `sampling` 键下进行配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # 启用采样（默认：true）
      model: "openai/gpt-4o"  # 覆盖采样请求的模型（可选）
      max_tokens_cap: 4096     # 每次采样响应的最大 Token 数（默认：4096）
      timeout: 30              # 每次请求的超时时间（秒）（默认：30）
      max_rpm: 10              # 速率限制：每分钟最大请求数（默认：10）
      max_tool_rounds: 5       # 采样循环中最大工具使用轮数（默认：5）
      allowed_models: []       # 服务器可以请求的模型名称白名单（空 = 任何）
      log_level: "info"        # 审计日志级别：debug、info 或 warning（默认：info）
```

采样处理器包含滑动窗口速率限制器、每次请求超时和工具循环深度限制，以防止使用失控。指标（请求计数、错误、使用的 Token 数）按服务器实例进行跟踪。

要为特定服务器禁用采样：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```
## 将 Hermes 作为 MCP 服务器运行

除了可以连接**到** MCP 服务器，Hermes 也可以**作为**一个 MCP 服务器。这使得其他支持 MCP 的 Agent（Claude Code、Cursor、Codex 或任何 MCP 客户端）能够使用 Hermes 的消息传递能力——列出会话、读取消息历史记录，并通过您所有已连接的平台发送消息。

### 使用场景

- 您希望 Claude Code、Cursor 或其他编程 Agent 通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 您需要一个单一的 MCP 服务器，一次性桥接到 Hermes 所有已连接的消息平台
- 您已经有一个正在运行的、连接了平台的 Hermes 消息网关

### 快速开始

```bash
hermes mcp serve
```

这将启动一个 stdio MCP 服务器。MCP 客户端（而不是您）管理进程的生命周期。

### MCP 客户端配置

将 Hermes 添加到您的 MCP 客户端配置中。例如，在 Claude Code 的 `~/.claude/claude_desktop_config.json` 中：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

或者，如果您将 Hermes 安装在了特定位置：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "/home/user/.hermes/hermes-agent/venv/bin/hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 可用工具

MCP 服务器公开了 10 个工具，与 OpenClaw 的频道桥接功能相匹配，外加一个 Hermes 特有的频道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息会话。可按平台筛选或按名称搜索。 |
| `conversation_get` | 通过会话密钥获取一个会话的详细信息。 |
| `messages_read` | 读取一个会话的近期消息历史记录。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图像、媒体）。 |
| `events_poll` | 轮询自某个游标位置以来的新会话事件。 |
| `events_wait` | 长轮询/阻塞直到下一个事件到达（近实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`， `discord:#general`）。 |
| `channels_list` | 列出所有平台上可用的消息发送目标。 |
| `permissions_list_open` | 列出在此桥接会话期间观察到的待处理审批请求。 |
| `permissions_respond` | 批准或拒绝一个待处理的审批请求。 |

### 事件系统

MCP 服务器包含一个实时事件桥接器，它会轮询 Hermes 的会话数据库以获取新消息。这使 MCP 客户端能够近乎实时地感知到传入的会话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（阻塞直到超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`， `approval_requested`， `approval_resolved`

事件队列存储在内存中，并在桥接器连接时启动。较早的消息可以通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # 正常模式
hermes mcp serve --verbose    # 在 stderr 上启用调试日志
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）读取会话数据。一个后台线程轮询数据库以获取新消息，并维护一个内存中的事件队列。对于发送消息，它使用与 Hermes Agent 本身相同的 `send_message` 基础设施。

对于读取操作（列出会话、读取历史记录、轮询事件），消息网关**不需要**运行。对于发送操作，消息网关**需要**运行，因为平台适配器需要活跃的连接。

### 当前限制

- 仅支持 Stdio 传输（尚不支持 HTTP MCP 传输）
- 通过基于 mtime 优化的数据库轮询实现约 200 毫秒间隔的事件轮询（当文件未更改时跳过工作）
- 尚不支持 `claude/channel` 推送通知协议
- 仅支持纯文本发送（尚不支持通过 `messages_send` 发送媒体/附件）

## 相关文档

- [与 Hermes 一起使用 MCP](/docs/guides/use-mcp-with-hermes)
- [CLI 命令](/docs/reference/cli-commands)
- [斜杠命令](/docs/reference/slash-commands)
- [常见问题](/docs/reference/faq)