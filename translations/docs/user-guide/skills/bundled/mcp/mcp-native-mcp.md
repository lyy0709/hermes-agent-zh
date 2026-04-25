---
title: "原生 MCP"
sidebar_label: "原生 MCP"
description: "内置的 MCP（模型上下文协议）客户端，可连接外部 MCP 服务器，发现其工具，并将其注册为 Hermes Agent 的原生工具"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 原生 MCP

内置的 MCP（模型上下文协议）客户端，可连接外部 MCP 服务器，发现其工具，并将其注册为 Hermes Agent 的原生工具。支持 stdio 和 HTTP 传输，具备自动重连、安全过滤和零配置工具注入功能。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mcp/native-mcp` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `MCP`, `Tools`, `Integrations` |
| 相关技能 | [`mcporter`](/docs/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 原生 MCP 客户端

Hermes Agent 内置了一个 MCP 客户端，它在启动时连接 MCP 服务器，发现其工具，并使这些工具可作为一等工具供 Agent 直接调用。无需桥接 CLI —— MCP 服务器的工具将与 `terminal`、`read_file` 等内置工具一同出现。

## 使用时机

在以下情况下使用此技能：
- 连接 MCP 服务器并从 Hermes Agent 内部使用其工具
- 通过 MCP 添加外部能力（文件系统访问、GitHub、数据库、API）
- 运行基于本地 stdio 的 MCP 服务器（npx、uvx 或任何命令）
- 连接到远程 HTTP/StreamableHTTP MCP 服务器
- 让 MCP 工具在每个会话中自动被发现并可用

对于临时、一次性的 MCP 工具调用（无需配置任何内容），请改用 `mcporter` 技能。

## 先决条件

- **mcp Python 包** —— 可选依赖项；使用 `pip install mcp` 安装。如果未安装，MCP 支持将静默禁用。
- **Node.js** —— 基于 `npx` 的 MCP 服务器（大多数社区服务器）所需
- **uv** —— 基于 `uvx` 的 MCP 服务器（基于 Python 的服务器）所需

安装 MCP SDK：

```bash
pip install mcp
# 或者，如果使用 uv：
uv pip install mcp
```

## 快速开始

将 MCP 服务器添加到 `~/.hermes/config.yaml` 中的 `mcp_servers` 键下：

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

重启 Hermes Agent。启动时它将：
1. 连接到服务器
2. 发现可用工具
3. 使用前缀 `mcp_time_*` 注册它们
4. 将它们注入到所有平台工具集中

然后你就可以自然地使用这些工具 —— 只需让 Agent 获取当前时间。

## 配置参考

`mcp_servers` 下的每个条目都是一个服务器名称到其配置的映射。有两种传输类型：**stdio**（基于命令）和 **HTTP**（基于 URL）。

### Stdio 传输（command + args）

```yaml
mcp_servers:
  server_name:
    command: "npx"             # （必需）要运行的可执行文件
    args: ["-y", "pkg-name"]   # （可选）命令参数，默认：[]
    env:                       # （可选）子进程的环境变量
      SOME_API_KEY: "value"
    timeout: 120               # （可选）每次工具调用的超时时间（秒），默认：120
    connect_timeout: 60        # （可选）初始连接超时时间（秒），默认：60
```

### HTTP 传输（url）

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # （必需）服务器 URL
    headers:                                     # （可选）HTTP 头
      Authorization: "Bearer sk-..."
    timeout: 180               # （可选）每次工具调用的超时时间（秒），默认：120
    connect_timeout: 60        # （可选）初始连接超时时间（秒），默认：60
```

### 所有配置选项

| 选项            | 类型   | 默认值 | 描述                                       |
|-------------------|--------|---------|---------------------------------------------------|
| `command`         | 字符串 | --      | 要运行的可执行文件（stdio 传输，必需）     |
| `args`            | 列表   | `[]`    | 传递给命令的参数                   |
| `env`             | 字典   | `{}`    | 子进程的额外环境变量    |
| `url`             | 字符串 | --      | 服务器 URL（HTTP 传输，必需）             |
| `headers`         | 字典   | `{}`    | 每个请求发送的 HTTP 头              |
| `timeout`         | 整数    | `120`   | 每次工具调用的超时时间（秒）                  |
| `connect_timeout` | 整数    | `60`    | 初始连接和发现的超时时间      |

注意：服务器配置必须包含 `command`（stdio）或 `url`（HTTP）之一，不能同时包含两者。

## 工作原理

### 启动发现

当 Hermes Agent 启动时，`discover_mcp_tools()` 在工具初始化期间被调用：

1. 从 `~/.hermes/config.yaml` 读取 `mcp_servers`
2. 对于每个服务器，在专用的后台事件循环中生成一个连接
3. 初始化 MCP 会话并调用 `list_tools()` 来发现可用工具
4. 在 Hermes 工具注册表中注册每个工具

### 工具命名约定

MCP 工具使用以下命名模式注册：

```
mcp_{server_name}_{tool_name}
```

名称中的连字符和点会被替换为下划线，以兼容 LLM API。

示例：
- 服务器 `filesystem`，工具 `read_file` → `mcp_filesystem_read_file`
- 服务器 `github`，工具 `list-issues` → `mcp_github_list_issues`
- 服务器 `my-api`，工具 `fetch.data` → `mcp_my_api_fetch_data`

### 自动注入

发现后，MCP 工具会自动注入到所有 `hermes-*` 平台工具集（CLI、Discord、Telegram 等）中。这意味着 MCP 工具在每个会话中都可用，无需任何额外配置。

### 连接生命周期

- 每个服务器作为一个长期运行的 asyncio Task 在后台守护线程中运行
- 连接在 Agent 进程的整个生命周期内持续存在
- 如果连接断开，将触发带指数退避的自动重连（最多重试 5 次，最大退避 60 秒）
- 在 Agent 关闭时，所有连接都会被优雅地关闭
### 幂等性

`discover_mcp_tools()` 是幂等的 —— 多次调用它只会连接到尚未连接的服务器。失败的服务器会在后续调用中重试。

## 传输类型

### Stdio 传输

最常见的传输方式。Hermes 将 MCP 服务器作为子进程启动，并通过 stdin/stdout 进行通信。

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

子进程继承一个**经过过滤的**环境（见下文安全部分）以及你在 `env` 中指定的任何变量。

### HTTP / StreamableHTTP 传输

用于远程或共享的 MCP 服务器。要求 `mcp` 包包含 HTTP 客户端支持 (`mcp.client.streamable_http`)。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

如果你安装的 `mcp` 版本中没有 HTTP 支持，该服务器将因 ImportError 而失败，其他服务器将继续正常运行。

## 安全

### 环境变量过滤

对于 stdio 服务器，Hermes **不会**将你的完整 shell 环境传递给 MCP 子进程。只继承安全的基础变量：

- `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`
- 任何 `XDG_*` 变量

所有其他环境变量（API 密钥、Token、密钥）都会被排除，除非你通过 `env` 配置键显式添加它们。这可以防止凭据意外泄露给不受信任的 MCP 服务器。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # 只有这个 Token 会传递给子进程
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### 错误消息中的凭据脱敏

如果 MCP 工具调用失败，错误消息中任何类似凭据的模式在展示给 LLM 之前会自动进行脱敏处理。这包括：

- GitHub PATs (`ghp_...`)
- OpenAI 风格的密钥 (`sk-...`)
- Bearer Token
- 通用的 `token=`, `key=`, `API_KEY=`, `password=`, `secret=` 模式

## 故障排除

### "MCP SDK not available -- skipping MCP tool discovery"

未安装 `mcp` Python 包。请安装：

```bash
pip install mcp
```

### "No MCP servers configured"

`~/.hermes/config.yaml` 中没有 `mcp_servers` 键，或者该键为空。请至少添加一个服务器。

### "Failed to connect to MCP server 'X'"

常见原因：
- **命令未找到**：`command` 二进制文件不在 PATH 中。确保安装了 `npx`、`uvx` 或相关命令。
- **包未找到**：对于 npx 服务器，npm 包可能不存在，或者可能需要在 args 中添加 `-y` 来自动安装。
- **超时**：服务器启动时间过长。请增加 `connect_timeout`。
- **端口冲突**：对于 HTTP 服务器，URL 可能无法访问。

### "MCP server 'X' requires HTTP transport but mcp.client.streamable_http is not available"

你的 `mcp` 包版本不包含 HTTP 客户端支持。请升级：

```bash
pip install --upgrade mcp
```

### 工具未出现

- 检查服务器是否列在 `mcp_servers` 下（而不是 `mcp` 或 `servers`）
- 确保 YAML 缩进正确
- 查看 Hermes Agent 启动日志中的连接消息
- 工具名称以 `mcp_{server}_{tool}` 为前缀 —— 查找该模式

### 连接持续断开

客户端会以指数退避（1秒、2秒、4秒、8秒、16秒，上限为60秒）重试最多5次。如果服务器根本上无法访问，则在5次尝试后放弃。请检查服务器进程和网络连接。

## 示例

### 时间服务器 (uvx)

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

注册类似 `mcp_time_get_current_time` 的工具。

### 文件系统服务器 (npx)

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

注册类似 `mcp_filesystem_read_file`、`mcp_filesystem_write_file`、`mcp_filesystem_list_directory` 的工具。

### 带身份验证的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

注册类似 `mcp_github_list_issues`、`mcp_github_create_pull_request` 等工具。

### 远程 HTTP 服务器

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

### 多个服务器

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
    timeout: 300
```

所有服务器的所有工具都会同时注册并可用。每个服务器的工具都以其名称作为前缀，以避免冲突。

## 采样（服务器发起的 LLM 请求）

Hermes 支持 MCP 的 `sampling/createMessage` 功能 —— MCP 服务器可以在工具执行期间通过 Agent 请求 LLM 补全。这支持了 Agent 在环的工作流（数据分析、内容生成、决策制定）。

采样**默认启用**。可按服务器配置：

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # 默认值: true
      model: "gemini-3-flash" # 模型覆盖（可选）
      max_tokens_cap: 4096    # 每次请求的最大 Token 数
      timeout: 30             # LLM 调用超时（秒）
      max_rpm: 10             # 每分钟最大请求数
      allowed_models: []      # 模型白名单（空 = 全部）
      max_tool_rounds: 5      # 工具循环限制（0 = 禁用）
      log_level: "info"       # 审计详细程度
```
服务器也可以在采样请求中包含 `tools`，用于多轮工具增强的工作流。`max_tool_rounds` 配置可以防止无限的工具循环。每个服务器的审计指标（请求数、错误数、Token 数、工具使用次数）通过 `get_mcp_status()` 进行跟踪。

对于不受信任的服务器，可以通过 `sampling: { enabled: false }` 禁用采样。

## 注意事项

- 从 Agent 的角度看，MCP 工具是同步调用的，但实际上是在专用的后台事件循环中异步运行的
- 工具结果以 JSON 格式返回，格式为 `{"result": "..."}` 或 `{"error": "..."}`
- 原生 MCP 客户端独立于 `mcporter` —— 你可以同时使用两者
- 服务器连接是持久化的，并在同一 Agent 进程内的所有会话中共享
- 添加或移除服务器需要重启 Agent（目前不支持热重载）