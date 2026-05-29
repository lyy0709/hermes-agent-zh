---
sidebar_position: 8
title: "MCP 配置参考"
description: "Hermes Agent MCP 配置键、过滤语义和实用工具策略参考"
---

# MCP 配置参考

本页是主要 MCP 文档的简明参考伴侣。

概念性指南请参阅：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)

## 根配置结构

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio 服务器
    args: []
    env: {}

    # 或者
    url: "..."          # HTTP 服务器
    headers: {}

    # 可选的 HTTP/SSE TLS 设置：
    ssl_verify: true                # 布尔值或 CA 捆绑包路径（PEM）
    client_cert: "/path/to/cert.pem"  # mTLS 客户端证书（见下文）
    # client_key: "/path/to/key.pem"  # 可选，当密钥位于单独的文件中时

    enabled: true
    timeout: 120
    connect_timeout: 60
    supports_parallel_tool_calls: false
    tools:
      include: []
      exclude: []
      resources: true
      prompts: true
```

## 服务器键

| 键 | 类型 | 适用对象 | 含义 |
|---|---|---|---|
| `command` | 字符串 | stdio | 要启动的可执行文件 |
| `args` | 列表 | stdio | 子进程的参数 |
| `env` | 映射 | stdio | 传递给子进程的环境变量 |
| `url` | 字符串 | HTTP | 远程 MCP 端点 |
| `headers` | 映射 | HTTP | 远程服务器请求的头部 |
| `ssl_verify` | 布尔值或字符串 | HTTP | TLS 验证。`true`（默认）使用系统 CA，`false` 禁用验证（不安全），或指向自定义 CA 捆绑包（PEM）的字符串路径 |
| `client_cert` | 字符串或列表 | HTTP | mTLS 客户端证书。字符串 = 包含证书 + 密钥的 PEM 文件路径。列表 `[cert, key]` = 单独的文件。列表 `[cert, key, password]` = 加密的密钥 |
| `client_key` | 字符串 | HTTP | 客户端私钥路径，当 `client_cert` 是字符串且密钥位于单独的文件中时 |
| `enabled` | 布尔值 | 两者 | 为 false 时完全跳过该服务器 |
| `timeout` | 数字 | 两者 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 两者 | 初始连接超时时间 |
| `supports_parallel_tool_calls` | 布尔值 | 两者 | 允许此服务器的工具并发运行 |
| `tools` | 映射 | 两者 | 过滤和实用工具策略 |
| `auth` | 字符串 | HTTP | 认证方法。设置为 `oauth` 以启用带 PKCE 的 OAuth 2.1 |
| `sampling` | 映射 | 两者 | 服务器发起的 LLM 请求策略（见 MCP 指南） |

## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 白名单服务器原生 MCP 工具 |
| `exclude` | 字符串或列表 | 黑名单服务器原生 MCP 工具 |
| `resources` | 布尔类 | 启用/禁用 `list_resources` + `read_resource` |
| `prompts` | 布尔类 | 启用/禁用 `list_prompts` + `get_prompt` |

## 过滤语义

### `include`

如果设置了 `include`，则只注册那些服务器原生的 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

如果设置了 `exclude` 且未设置 `include`，则注册除这些名称外的所有服务器原生 MCP 工具。

```yaml
tools:
  exclude: [delete_customer]
```

### 优先级

如果两者都设置，`include` 优先。

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

结果：
- `create_issue` 仍然被允许
- `delete_issue` 被忽略，因为 `include` 优先

## 实用工具策略

Hermes 可能会为每个 MCP 服务器注册这些实用包装器：

资源：
- `list_resources`
- `read_resource`

提示词：
- `list_prompts`
- `get_prompt`

### 禁用资源

```yaml
tools:
  resources: false
```

### 禁用提示词

```yaml
tools:
  prompts: false
```

### 能力感知注册

即使 `resources: true` 或 `prompts: true`，Hermes 也只在 MCP 会话实际暴露相应能力时才注册那些实用工具。

所以这是正常的：
- 你启用了提示词
- 但没有出现提示词实用工具
- 因为服务器不支持提示词

## `enabled: false`

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

行为：
- 不尝试连接
- 不进行发现
- 不注册工具
- 配置保留以备后续重用

## 空结果行为

如果过滤移除了所有服务器原生工具且没有注册实用工具，Hermes 不会为该服务器创建空的 MCP 运行时工具集。

## 配置示例

### 安全的 GitHub 白名单

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      resources: false
      prompts: false
```

### Stripe 黑名单

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 仅资源的文档服务器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

### TLS 客户端证书（mTLS）

对于需要客户端证书的 HTTP/SSE 服务器，设置 `client_cert`（以及可选的 `client_key`）：

```yaml
mcp_servers:
  # 证书和密钥组合在单个 PEM 文件中
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/secrets/mcp-client.pem"

  # 单独的证书和密钥文件
  partner_api:
    url: "https://mcp.partner.example.com/mcp"
    client_cert: "~/secrets/client.crt"
    client_key: "~/secrets/client.key"

  # 带密码的加密密钥（3元素列表形式）
  bank_api:
    url: "https://mcp.bank.example.com/mcp"
    client_cert: ["~/secrets/client.crt", "~/secrets/client.key", "my-passphrase"]

  # 自定义 CA 捆绑包（私有 CA / 自签名服务器）
  lab_api:
    url: "https://mcp.lab.local/mcp"
    ssl_verify: "~/secrets/lab-ca.pem"
    client_cert: "~/secrets/lab-client.pem"
```

注意：
- 路径支持 `~` 扩展。缺少文件会在连接时快速失败，并显示服务器范围的错误消息。
- `ssl_verify: false` 完全禁用服务器证书验证。不要在真实服务中使用此选项。
- 适用于 Streamable HTTP 和 SSE 传输。

## 重新加载配置

更改 MCP 配置后，使用以下命令重新加载服务器：

```text
/reload-mcp
```

## 工具命名

服务器原生的 MCP 工具变为：

```text
mcp_<server>_<tool>
```

示例：
- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

实用工具遵循相同的前缀模式：
- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`

### 名称清理

服务器名称和工具名称中的连字符（`-`）和点（`.`）在注册前会被替换为下划线。这确保了工具名称是 LLM 函数调用 API 的有效标识符。

例如，一个名为 `my-api` 的服务器暴露一个名为 `list-items.v2` 的工具，会变为：

```text
mcp_my_api_list_items_v2
```

在编写 `include` / `exclude` 过滤器时请记住这一点——使用**原始**的 MCP 工具名称（带连字符/点），而不是清理后的版本。

## OAuth 2.1 认证

对于需要 OAuth 的 HTTP 服务器，在服务器条目上设置 `auth: oauth`：

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

行为：
- Hermes 使用 MCP SDK 的 OAuth 2.1 PKCE 流程（元数据发现、动态客户端注册、令牌交换和刷新）
- 首次连接时，会打开浏览器窗口进行授权
- 令牌持久化到 `~/.hermes/mcp-tokens/<server>.json` 并在会话间重用
- 令牌刷新是自动的；仅当刷新失败时才需要重新授权
- 仅适用于 HTTP/StreamableHTTP 传输（基于 `url` 的服务器）