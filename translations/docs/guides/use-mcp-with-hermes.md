---
sidebar_position: 6
title: "在 Hermes 中使用 MCP"
description: "一份实用指南，介绍如何将 MCP 服务器连接到 Hermes Agent，过滤其工具，并在实际工作流中安全地使用它们"
---

# 在 Hermes 中使用 MCP

本指南展示了如何在日常工作中实际使用 MCP 与 Hermes Agent。

如果说功能页面解释了 MCP 是什么，那么本指南则是关于如何快速、安全地从中获取价值。

## 何时应该使用 MCP？

在以下情况下使用 MCP：
- 某个工具已经以 MCP 形式存在，而你不想构建原生的 Hermes 工具
- 你希望 Hermes 通过一个干净的 RPC 层操作本地或远程系统
- 你需要对每个服务器的暴露进行细粒度的控制
- 你希望将 Hermes 连接到内部 API、数据库或公司系统，而无需修改 Hermes 核心

在以下情况下不要使用 MCP：
- 内置的 Hermes 工具已经很好地解决了问题
- 服务器暴露了大量危险的工具接口，而你还没有准备好过滤它们
- 你只需要一个非常狭窄的集成，而原生工具会更简单、更安全

## 心智模型

将 MCP 视为一个适配层：

- Hermes 仍然是 Agent
- MCP 服务器提供工具
- Hermes 在启动或重新加载时发现这些工具
- 模型可以像使用普通工具一样使用它们
- 你可以控制每个服务器的可见范围

最后一点很重要。良好的 MCP 使用不仅仅是“连接一切”，而是“连接正确的东西，暴露最小的有用接口”。

## 步骤 1：安装 MCP 支持

如果你使用标准安装脚本安装了 Hermes，则 MCP 支持已包含在内（安装程序会运行 `uv pip install -e ".[all]"`）。

如果你安装时没有包含额外功能，需要单独添加 MCP：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

对于基于 npm 的服务器，请确保 Node.js 和 `npx` 可用。

对于许多 Python MCP 服务器，`uvx` 是一个很好的默认选择。

## 步骤 2：首先添加一个服务器

从一个单一、安全的服务器开始。

示例：仅对一个项目目录进行文件系统访问。

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

然后启动 Hermes：

```bash
hermes chat
```

现在提出一个具体的问题：

```text
检查这个项目并总结仓库的布局。
```

## 步骤 3：验证 MCP 已加载

你可以通过几种方式验证 MCP：

- 配置后，Hermes 的横幅/状态应显示 MCP 集成
- 询问 Hermes 它有哪些可用工具
- 配置更改后使用 `/reload-mcp`
- 如果服务器连接失败，请检查日志

一个实用的测试提示词：

```text
告诉我目前有哪些基于 MCP 的工具可用。
```

## 步骤 4：立即开始过滤

如果服务器暴露了大量工具，不要等到以后。

### 示例：仅允许你想要的工具（白名单）

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

对于敏感系统，这通常是最好的默认设置。

### 示例：阻止危险操作（黑名单）

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 示例：也禁用实用程序包装器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

## 过滤实际上影响什么？

在 Hermes 中，MCP 暴露的功能分为两类：

1. 服务器原生的 MCP 工具
- 使用以下方式过滤：
  - `tools.include`
  - `tools.exclude`

2. Hermes 添加的实用程序包装器
- 使用以下方式过滤：
  - `tools.resources`
  - `tools.prompts`

### 你可能会看到的实用程序包装器

资源：
- `list_resources`
- `read_resource`

提示词：
- `list_prompts`
- `get_prompt`

这些包装器仅在以下情况下出现：
- 你的配置允许它们，并且
- MCP 服务器会话实际支持这些功能

因此，如果服务器没有资源/提示词，Hermes 不会假装它有。

## 常见模式

### 模式 1：本地项目助手

当你希望 Hermes 在一个有界的工作空间上进行推理时，使用 MCP 进行仓库本地的文件系统或 git 服务器访问。

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

好的提示词：

```text
审查项目结构，找出配置所在的位置。
```

```text
检查本地 git 状态，总结最近的变化。
```

### 模式 2：GitHub 问题分类助手

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false
```

好的提示词：

```text
列出关于 MCP 的未解决问题，按主题对它们进行分组，并为最常见的错误起草一个高质量的问题。
```

```text
在仓库中搜索 _discover_and_register_server 的使用，并解释 MCP 工具是如何注册的。
```

### 模式 3：内部 API 助手

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      include: [list_customers, get_customer, list_invoices]
      resources: false
      prompts: false
```

好的提示词：

```text
查找客户 ACME Corp 并总结最近的发票活动。
```

在这种情况下，严格的白名单远比排除列表要好。

### 模式 4：文档 / 知识服务器

一些 MCP 服务器暴露的提示词或资源更像是共享的知识资产，而不是直接的操作。

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

好的提示词：

```text
列出文档服务器中可用的 MCP 资源，然后阅读入门指南并总结它。
```

```text
列出文档服务器暴露的提示词，并告诉我哪些有助于事件响应。
```

## 教程：带过滤的端到端设置

这是一个实用的步骤。

### 阶段 1：添加 GitHub MCP 并设置严格的白名单

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
      prompts: false
      resources: false
```

启动 Hermes 并询问：

```text
在代码库中搜索对 MCP 的引用，并总结主要的集成点。
```

### 阶段 2：仅在需要时扩展

如果你以后也需要更新问题：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

然后重新加载：

```text
/reload-mcp
```

### 阶段 3：添加第二个服务器，采用不同的策略

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
```

现在 Hermes 可以结合它们：

```text
检查本地项目文件，然后在 GitHub 上创建一个问题，总结你发现的错误。
```

这就是 MCP 变得强大的地方：无需更改 Hermes 核心即可实现多系统工作流。

## 安全使用建议

### 对于危险系统，优先使用白名单

对于任何涉及财务、面向客户或具有破坏性的系统：
- 使用 `tools.include`
- 从尽可能小的集合开始

### 禁用未使用的实用程序

如果你不希望模型浏览服务器提供的资源/提示词，请关闭它们：

```yaml
tools:
  resources: false
  prompts: false
```

### 保持服务器范围狭窄

示例：
- 文件系统服务器仅根植于一个项目目录，而不是整个主目录
- git 服务器指向一个仓库
- 内部 API 服务器默认暴露以读取为主的工具

### 配置更改后重新加载

```text
/reload-mcp
```

在更改以下内容后执行此操作：
- include/exclude 列表
- 启用标志
- resources/prompts 开关
- 认证头信息 / 环境变量

## 按症状排查

### "服务器已连接，但我期望的工具缺失"

可能的原因：
- 被 `tools.include` 过滤掉了
- 被 `tools.exclude` 排除了
- 实用程序包装器通过 `resources: false` 或 `prompts: false` 被禁用
- 服务器实际上不支持资源/提示词

### "服务器已配置，但没有任何内容加载"

检查：
- 配置中没有遗留 `enabled: false`
- 命令/运行时存在（`npx`、`uvx` 等）
- HTTP 端点可达
- 认证环境变量或头信息正确

### "为什么我看到的工具比 MCP 服务器宣传的少？"

因为 Hermes 现在尊重你的每个服务器策略和基于功能的注册。这是预期的，通常也是可取的。

### "如何在不删除配置的情况下移除 MCP 服务器？"

使用：

```yaml
enabled: false
```

这样可以保留配置，但阻止连接和注册。

## 推荐的首次 MCP 设置

适合大多数用户的第一个服务器：
- 文件系统
- git
- GitHub
- fetch / 文档 MCP 服务器
- 一个狭窄的内部 API

不适合作为第一个服务器的：
- 具有大量破坏性操作且没有过滤的大型业务系统
- 任何你不够了解、无法进行约束的东西

## 相关文档

- [MCP (Model Context Protocol)](/docs/user-guide/features/mcp)
- [FAQ](/docs/reference/faq)
- [Slash Commands](/docs/reference/slash-commands)