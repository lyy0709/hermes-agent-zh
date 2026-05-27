---
sidebar_position: 4
title: "MCP (模型上下文协议)"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器 —— 并精确控制 Hermes 加载哪些 MCP 工具"
---

# MCP (模型上下文协议)

MCP 允许 Hermes Agent 连接到外部工具服务器，使 Agent 能够使用 Hermes 本身之外的各类工具 —— GitHub、数据库、文件系统、浏览器栈、内部 API 等等。

如果你曾希望 Hermes 使用某个已存在于其他地方的工具，MCP 通常是实现这一目标最简洁的方式。

## MCP 为你带来的能力

- 无需先编写原生 Hermes 工具，即可访问外部工具生态系统
- 在同一配置中支持本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，为 MCP 资源和提示词提供实用包装器
- 按服务器进行过滤，以便只暴露你真正希望 Hermes 看到的 MCP 工具

## 快速开始

1. 安装 MCP 支持（如果使用了标准安装脚本，则已包含）：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

2. 在 `~/.hermes/config.yaml` 中添加一个 MCP 服务器：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3. 启动 Hermes：

```bash
hermes chat
```

4. 要求 Hermes 使用基于 MCP 的能力。

例如：

```text
列出 /home/user/projects 中的文件并总结仓库结构。
```

Hermes 将发现 MCP 服务器的工具，并像使用其他任何工具一样使用它们。

## 目录：一键安装 Nous 审核通过的 MCP

Hermes 附带一个精选的 MCP 服务器目录，这些服务器已经过 Nous 员工的审核和合并。它们默认是禁用的 —— 只安装你真正需要的。

```bash
hermes mcp                # 交互式选择器（默认）
hermes mcp catalog        # 纯文本列表，可编写脚本
hermes mcp install n8n    # 按名称安装目录条目
```

选择器会显示每个条目的当前状态：

```
n8n          可用              从 Hermes 管理和检查 n8n 工作流
linear       已启用            Linear 问题/项目管理（远程 OAuth）
github       已安装（禁用）    GitHub 仓库 + PR 工具
```

在行上按 `Enter` 键进行安装（并完成任何必需的凭据配置）、启用、禁用或卸载。目录条目存储在 hermes-agent 仓库的 `optional-mcps/` 目录下 —— 该目录中的存在即表示 Nous 的批准。没有社区提交层级；条目通过合并 PR 来添加。

目录条目可能需要：

- **API 密钥** —— Hermes 在安装时提示，并将值写入 `~/.hermes/.env`。非机密值（如基础 URL）写入同一文件。
- **OAuth**（远程 MCP）—— 在配置中写为 `auth: oauth`；MCP 客户端在首次连接时打开浏览器。
- **OAuth**（第三方提供商，如 Google/GitHub）—— 如果你尚未认证，Hermes 会指引你使用 `hermes auth <provider>`。

### 安装时的工具选择

配置凭据后，Hermes 会探测 MCP 服务器以列出其暴露的所有工具，并呈现一个复选框列表：

```
为 'linear' 选择工具（空格切换，回车确认）
  [x] find_issues       查找匹配查询的问题
  [x] get_issue         获取单个问题
  [x] create_issue      创建新问题
  [ ] delete_workspace  删除 Linear 工作区
  ...
```

预选中的行来自：

1. **你之前的选择**（如果你之前安装过此条目 —— 重新安装会保留你之前的设置，清单的默认值不会覆盖它）
2. **清单的 `tools.default_enabled`**（如果条目声明了此字段 —— 某些目录条目会预先修剪有变更性或很少使用的工具）
3. **所有工具**（如果以上两者均不适用）

按 ENTER 提交复选框列表。只有选中的工具会出现在 `mcp_servers.<name>.tools.include` 中。如果你选择了所有工具，则不会写入过滤器（配置结构最简洁，行为相同）。

**如果探测失败**（服务器无法访问、OAuth 尚未完成、后端服务未运行），安装仍会成功：直接应用清单的 `tools.default_enabled`（如果已声明），或者不写入过滤器（如果未声明）。一旦服务器可访问，重新运行 `hermes mcp configure <name>` 以进行细化配置。

### 信任模型

安装目录条目会运行清单指定的所有内容 —— `git clone`、条目的 `bootstrap` 命令（`pip install`、`npm install` 等），以及最终 MCP 服务器自身的代码。清单需要通过 PR 审核才能进入 hermes-agent 仓库，因此 Nous 在每个条目发布前都已审核过 —— **但你仍然应该在安装前阅读清单**，特别是 `source:` 字段的仓库、`install.bootstrap:` 命令以及任何 `transport.command:` 调用。

清单位于 GitHub 上的 [`optional-mcps/<name>/manifest.yaml`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps)。选择器在安装时也会打印清单的 `source:` URL，以便你快速验证上游仓库。

### 清单版本兼容性

清单会固定一个 `manifest_version`。目录是向前兼容的：如果 PR 添加了一个条目，其 `manifest_version` 比你已安装的 Hermes 所理解的版本更新，选择器会为该条目显示警告（`⚠ '<name>' 需要更新的 Hermes`），而不是默默地隐藏它。当你看到此警告时，请运行 `hermes update` 来安装最新的 Hermes。

### 运行时的 `${ENV_VAR}` 替换

在条目的 `transport.command`、`transport.args`、`transport.url` 和 `headers` 内部，`${VAR}` 占位符会在服务器连接时从环境变量（包括 `~/.hermes/.env` 中的所有内容）中解析。这在目录条目需要引用用户在其他地方配置的值时非常有用 —— 例如 `${HOME}/foo` 或 `${MY_PROVIDER_TOKEN}`。

请注意，这与目录清单中的 `${INSTALL_DIR}` 不同，后者在安装时被替换为目录克隆条目仓库的路径。

### 后续更新工具选择
```bash
hermes mcp configure linear
```

重新打开相同的清单，并预选中您当前的选项。当您想要启用更多工具，或当服务器添加了您想要选择加入的新工具时使用此命令。

### 更新目录清单

MCP 永远不会自动更新。如果清单版本在 Hermes 更新后发生更改，请重新运行 `hermes mcp install <name>` 以刷新。

要将 MCP 添加到目录，请向 [`optional-mcps/`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps) 提交 PR。

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
- 您希望对本地资源进行低延迟访问
- 您正在遵循显示 `command`、`args` 和 `env` 的 MCP 服务器文档

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
- 您的组织暴露了内部 MCP 端点
- 您不希望 Hermes 为该集成生成本地子进程

### OAuth 认证的 HTTP 服务器

大多数托管的 MCP 服务器（Linear、Sentry、Atlassian、Asana、Figma、Stripe 等）需要 OAuth 2.1 而不是静态的承载令牌。设置 `auth: oauth`，Hermes 将通过 MCP Python SDK 处理发现、动态客户端注册、PKCE、令牌交换、刷新和升级认证。

```yaml
mcp_servers:
  linear:
    url: "https://mcp.linear.app/mcp"
    auth: oauth
```

首次连接时，Hermes 会打印一个授权 URL，在可能的情况下打开您的浏览器，并在本地环回端口上等待 OAuth 回调。令牌以 0o600 权限缓存在 `~/.hermes/mcp-tokens/<server>.json` 中；后续运行会静默地重用它们，直到刷新失败。

**远程/无头主机。** 当 Hermes 在与您的浏览器不同的机器上运行时，环回回调无法到达您的笔记本电脑。有两种方法可以完成流程：

- **粘贴返回（无需设置）：** 在交互式终端上，Hermes 会在授权 URL 旁边打印“或者在此处粘贴重定向 URL…”。在浏览器中打开 URL，批准，复制浏览器最终显示的完整 URL（重定向将显示连接错误——这是预期的），将其粘贴到提示符处。仅包含 `?code=…&state=…` 的查询字符串也有效。
- **SSH 端口转发：** 在单独的终端中运行 `ssh -N -L <port>:127.0.0.1:<port> user@host`，然后让重定向正常进行。

有关完整步骤，包括无 DCR 服务器（例如 Slack）、预注册的 `client_id`/`client_secret`、范围自定义以及通过 `hermes mcp login <server>` 重新认证，请参阅 [通过 SSH / 远程主机的 OAuth](../../guides/oauth-over-ssh.md#mcp-servers)。

**陷阱——配置自动重新加载竞争。** 当您从正在运行的 Hermes 会话内部编辑 `~/.hermes/config.yaml` 时，CLI 会自动重新加载 MCP 连接，超时时间为 30 秒。这对于交互式 OAuth 流程来说不够。添加条目后，从新终端运行 `hermes mcp login <server>` —— 它会等待完整的 5 分钟让您完成认证。

## 基本配置参考

Hermes 从 `~/.hermes/config.yaml` 中的 `mcp_servers` 下读取 MCP 配置。

### 通用键

| 键 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行文件 |
| `args` | 列表 | stdio 服务器的参数 |
| `env` | 映射 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 端点 |
| `headers` | 映射 | 远程服务器的 HTTP 头 |
| `timeout` | 数字 | 工具调用超时 |
| `connect_timeout` | 数字 | 初始连接超时 |
| `enabled` | 布尔值 | 如果为 `false`，Hermes 完全跳过该服务器 |
| `supports_parallel_tool_calls` | 布尔值 | 如果为 `true`，来自此服务器的工具可以并发运行 |
| `tools` | 映射 | 每服务器的工具过滤和实用程序策略 |

### 最小 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 最小 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## 内置预设

对于知名的 MCP 服务器，`hermes mcp add` 接受一个 `--preset` 标志，该标志会填充传输详细信息，这样您就不必查找命令和参数。预设仅提供默认值——您在同一命令行上传递的任何其他内容（环境变量、头信息、过滤）仍然优先。

| 预设 | 它连接的内容 |
|---|---|
| `codex` | Codex CLI 的 MCP 服务器（通过 stdio 的 `codex mcp-server`）。要求 PATH 上有 `codex` CLI。 |

```bash
# 一行命令将 Codex CLI 添加为 MCP 服务器
hermes mcp add codex --preset codex
```

这将写入等效于：

```yaml
mcp_servers:
  codex:
    command: "codex"
    args: ["mcp-server"]
```

您可以选择任何本地名称（`hermes mcp add my-codex --preset codex` 也可以）；预设仅提供 `command`/`args` 的默认值。

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

实际上，您通常不需要手动调用带前缀的名称——Hermes 会看到该工具并在正常推理过程中选择它。

## MCP 实用工具

当支持时，Hermes 还会围绕 MCP 资源和提示词注册实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具按服务器注册，遵循相同的前缀模式，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`
### 重要说明

这些实用工具现在具备能力感知功能：
- 仅当 MCP 会话实际支持资源操作时，Hermes 才会注册资源实用工具
- 仅当 MCP 会话实际支持提示词操作时，Hermes 才会注册提示词实用工具

因此，一个仅暴露可调用工具但不提供资源/提示词操作的服务器将不会获得这些额外的包装器。

## 按服务器过滤

你可以控制每个 MCP 服务器向 Hermes 贡献哪些工具，从而实现对工具命名空间的精细管理。

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

仅注册这些 MCP 服务器工具。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

注册除排除项之外的所有服务器工具。

### 优先级规则

如果两者同时存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 优先。

### 也过滤实用工具

你也可以单独禁用 Hermes 添加的实用包装器：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 禁用 `list_resources` 和 `read_resource`
- `tools.prompts: false` 禁用 `list_prompts` 和 `get_prompt`

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

如果你的配置过滤掉了所有可调用工具，并且禁用或省略了所有支持的实用工具，Hermes 将不会为该服务器创建空的运行时 MCP 工具集。

这可以保持工具列表的整洁。

## 运行时行为

### 发现时间

Hermes 在启动时发现 MCP 服务器，并将其工具注册到常规工具注册表中。

### 动态工具发现

当 MCP 服务器在运行时其可用工具发生变化时，可以通过发送 `notifications/tools/list_changed` 通知来告知 Hermes。当 Hermes 收到此通知时，它会自动重新获取服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp`。

这对于能力动态变化的 MCP 服务器非常有用（例如，当加载新数据库模式时添加工具，或当服务离线时移除工具的服务器）。

刷新操作受锁保护，因此来自同一服务器的快速连续通知不会导致重叠刷新。提示词和资源变更通知（`prompts/list_changed`、`resources/list_changed`）会被接收，但尚未采取行动。

### 重新加载

如果你更改了 MCP 配置，请使用：

```text
/reload-mcp
```

这将从配置重新加载 MCP 服务器并刷新可用工具列表。对于服务器自身推送的运行时工具变更，请参阅上面的[动态工具发现](#dynamic-tool-discovery)。

### 工具集

每个配置的 MCP 服务器在贡献至少一个已注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集级别更容易理解 MCP 服务器。

## 安全模型

### Stdio 环境过滤

对于 stdio 服务器，Hermes 不会盲目传递你的完整 shell 环境。

只有明确配置的 `env` 加上一个安全基线才会被传递。这减少了意外泄露密钥的风险。

### 配置级暴露控制

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
显示标记为 bug 的未解决问题，然后为不稳定的 MCP 重连行为起草一个新问题。
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
- 你的过滤配置排除了这些工具
- 该服务器上不存在实用功能
- 服务器被 `enabled: false` 禁用

如果你是有意过滤，这是预期行为。
### 为什么资源或提示词工具没有出现？

因为 Hermes 现在只会在以下两个条件同时满足时才注册这些包装器：
1. 你的配置允许它们
2. 服务器会话实际支持该功能

这是有意为之，以确保工具列表的真实性。

## 并行工具调用

默认情况下，MCP 工具是顺序运行的——一次一个。如果你的 MCP 服务器暴露的工具可以安全地并发运行（例如只读查询、独立的 API 调用），你可以选择启用并行执行：

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

当 `supports_parallel_tool_calls` 为 `true` 时，Hermes 可能会在单个工具调用批次中同时执行来自该服务器的多个工具，就像它对内置的只读工具（web_search、read_file 等）所做的那样。

:::caution
仅对工具可以安全同时运行的 MCP 服务器启用并行调用。如果工具读取和写入共享状态、文件、数据库或外部资源，请在启用此设置前审查读/写竞争条件。
:::

## MCP 采样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这允许 MCP 服务器请求 Hermes 代表其生成文本——对于需要 LLM 能力但没有自己模型访问权限的服务器非常有用。

采样功能**默认启用**于所有 MCP 服务器（当 MCP SDK 支持时）。可以在每个服务器的 `sampling` 键下进行配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # 启用采样（默认：true）
      model: "openai/gpt-4o"  # 覆盖采样请求的模型（可选）
      max_tokens_cap: 4096     # 每个采样响应的最大 Token 数（默认：4096）
      timeout: 30              # 每个请求的超时时间（秒）（默认：30）
      max_rpm: 10              # 速率限制：每分钟最大请求数（默认：10）
      max_tool_rounds: 5       # 采样循环中的最大工具使用轮数（默认：5）
      allowed_models: []       # 服务器可以请求的模型名称白名单（空 = 任何）
      log_level: "info"        # 审计日志级别：debug、info 或 warning（默认：info）
```

采样处理器包含滑动窗口速率限制器、每个请求的超时设置以及工具循环深度限制，以防止失控使用。指标（请求计数、错误、使用的 Token）按服务器实例进行跟踪。

要禁用特定服务器的采样：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## 将 Hermes 作为 MCP 服务器运行

除了连接**到** MCP 服务器，Hermes 也可以**作为**一个 MCP 服务器。这让其他支持 MCP 的 Agent（Claude Code、Cursor、Codex 或任何 MCP 客户端）能够使用 Hermes 的消息传递能力——列出会话、读取消息历史记录，并通过所有已连接的平台发送消息。

### 何时使用此功能

- 你希望 Claude Code、Cursor 或其他编码 Agent 通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 你希望有一个单一的 MCP 服务器，能同时桥接到 Hermes 所有已连接的消息平台
- 你已经有一个正在运行的、连接了平台的 Hermes 消息网关

### 快速开始

```bash
hermes mcp serve
```

这将启动一个 stdio MCP 服务器。MCP 客户端（而不是你）管理进程的生命周期。

### MCP 客户端配置

将 Hermes 添加到你的 MCP 客户端配置中。例如，在 Claude Code 的 `~/.claude/claude_desktop_config.json` 中：

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

或者，如果你在特定位置安装了 Hermes：

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

MCP 服务器暴露了 10 个工具，匹配 OpenClaw 的频道桥接接口，外加一个 Hermes 特有的频道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息会话。可按平台筛选或按名称搜索。 |
| `conversation_get` | 通过会话键获取一个会话的详细信息。 |
| `messages_read` | 读取会话的近期消息历史记录。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图像、媒体）。 |
| `events_poll` | 轮询自某个游标位置以来的新会话事件。 |
| `events_wait` | 长轮询/阻塞直到下一个事件到达（近实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上可用的消息目标。 |
| `permissions_list_open` | 列出在此桥接会话期间观察到的待处理审批请求。 |
| `permissions_respond` | 允许或拒绝一个待处理的审批请求。 |

### 事件系统

MCP 服务器包含一个实时事件桥接器，它会轮询 Hermes 的会话数据库以获取新消息。这使 MCP 客户端能够近实时地感知传入的会话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（阻塞直到超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`

事件队列存储在内存中，并在桥接器连接时启动。较早的消息可以通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # 正常模式
hermes mcp serve --verbose    # 在 stderr 上启用调试日志
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）读取会话数据。一个后台线程轮询数据库以获取新消息，并维护一个内存中的事件队列。对于发送消息，它使用与 Hermes Agent 本身相同的 `send_message` 基础设施。

**读取操作**（列出会话、读取历史记录、轮询事件）**不需要**消息网关正在运行。**发送操作**则需要消息网关正在运行，因为平台适配器需要活跃的连接。
### 当前限制

- 内嵌的 `hermes mcp serve` 目前仅暴露一个**仅限 stdio** 的 MCP 服务器。如果你需要一个 HTTP MCP 服务器，请运行一个单独的适配器——或者，更常见的是，使用 Hermes 的 MCP **客户端**端，它已经同时支持 stdio 和 HTTP（在 `mcp_servers.yaml` / `config.yaml` 中使用 `url` + `headers`；参见上文的 [HTTP 服务器](#http-servers)）。
- 通过基于 mtime 优化的数据库轮询进行约 200 毫秒间隔的事件轮询（当文件未更改时跳过工作）
- 尚无 `claude/channel` 推送通知协议
- 仅限文本发送（无法通过 `messages_send` 发送媒体/附件）

## 相关文档

- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [斜杠命令](/reference/slash-commands)
- [常见问题](/reference/faq)