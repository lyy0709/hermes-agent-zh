---
sidebar_position: 8
title: "MCP 配置参考"
description: "Hermes Agent MCP 配置键、过滤语义和实用工具策略的参考文档"
---

# MCP 配置参考

本页是主要 MCP 文档的简明参考伴侣。

有关概念性指导，请参阅：
- [MCP（模型上下文协议）](/docs/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/docs/guides/use-mcp-with-hermes)

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

    enabled: true
    timeout: 120
    connect_timeout: 60
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
| `enabled` | 布尔值 | 两者 | 为 false 时完全跳过该服务器 |
| `timeout` | 数字 | 两者 | 工具调用超时时间 |
| `connect_timeout` | 数字 | 两者 | 初始连接超时时间 |
| `tools` | 映射 | 两者 | 过滤和实用工具策略 |
| `auth` | 字符串 | HTTP | 身份验证方法。设置为 `oauth` 以启用带 PKCE 的 OAuth 2.1 |
| `sampling` | 映射 | 两者 | 服务器发起的 LLM 请求策略（参见 MCP 指南） |

## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 服务器原生 MCP 工具的白名单 |
| `exclude` | 字符串或列表 | 服务器原生 MCP 工具的黑名单 |
| `resources` | 类布尔值 | 启用/禁用 `list_resources` + `read_resource` |
| `prompts` | 类布尔值 | 启用/禁用 `list_prompts` + `get_prompt` |

## 过滤语义

### `include`

如果设置了 `include`，则只注册那些服务器原生的 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

如果设置了 `exclude` 且未设置 `include`，则注册除指定名称外的所有服务器原生 MCP 工具。

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

Hermes 可能会为每个 MCP 服务器注册以下实用工具包装器：

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

### 基于能力的注册

即使 `resources: true` 或 `prompts: true`，Hermes 也只在 MCP 会话实际暴露相应能力时才会注册那些实用工具。

因此以下情况是正常的：
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
- 配置保留以便后续重用

## 空结果行为

如果过滤移除了所有服务器原生工具，并且没有注册任何实用工具，Hermes 不会为该服务器创建空的 MCP 运行时工具集。

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

服务器名称和工具名称中的连字符 (`-`) 和点号 (`.`) 在注册前会被替换为下划线。这确保了工具名称是 LLM 函数调用 API 的有效标识符。

例如，一个名为 `my-api` 的服务器暴露一个名为 `list-items.v2` 的工具，会变为：

```text
mcp_my_api_list_items_v2
```

在编写 `include` / `exclude` 过滤器时请记住这一点——使用**原始的** MCP 工具名称（带连字符/点号），而不是清理后的版本。

## OAuth 2.1 身份验证

对于需要 OAuth 的 HTTP 服务器，在服务器条目上设置 `auth: oauth`：

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

行为：
- Hermes 使用 MCP SDK 的 OAuth 2.1 PKCE 流程（元数据发现、动态客户端注册、令牌交换和刷新）
- 首次连接时，会打开一个浏览器窗口进行授权
- 令牌持久化到 `~/.hermes/mcp-tokens/<server>.json` 并在会话间重用
- 令牌刷新是自动的；仅当刷新失败时才需要重新授权
- 仅适用于 HTTP/StreamableHTTP 传输（基于 `url` 的服务器）