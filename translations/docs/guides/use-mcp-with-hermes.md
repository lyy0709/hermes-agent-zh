---
sidebar_position: 6
title: "在 Hermes 中使用 MCP"
description: "连接 MCP 服务器到 Hermes Agent 的实用指南，包括过滤其工具以及在真实工作流中安全使用它们"
---

# 在 Hermes 中使用 MCP

本指南展示了如何在日常工作中实际使用 MCP 与 Hermes Agent。

如果说功能页面解释了 MCP 是什么，那么本指南则是关于如何快速、安全地从中获取价值。

## 何时应该使用 MCP？

在以下情况下使用 MCP：
- 某个工具已经以 MCP 形式存在，而你不想构建原生的 Hermes 工具
- 你希望 Hermes 通过一个干净的 RPC 层来操作本地或远程系统
- 你需要对每个服务器的暴露进行细粒度控制
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

最后一点很重要。良好的 MCP 使用方式不仅仅是“连接一切”，而是“连接正确的东西，并暴露最小的有用接口”。

## 步骤 1：安装 MCP 支持

如果你使用标准安装脚本安装了 Hermes，MCP 支持已经包含在内（安装程序会运行 `uv pip install -e ".[all]"`）。

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
告诉我现在有哪些基于 MCP 的工具可用。
```

## 步骤 4：立即开始过滤

如果服务器暴露了大量工具，不要等到以后才处理。

### 示例：仅白名单你想要的工具

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

## WSL2：将 WSL 中的 Hermes 桥接到 Windows Chrome

这是以下情况下的实用设置：

- Hermes 在 WSL2 内部运行
- 你想要控制的浏览器是你 Windows 上正常登录的 Chrome
- 从 WSL 使用 `/browser connect` 很麻烦或不可靠

在此设置中，Hermes **不**直接连接到 Chrome。而是：

- Hermes 在 WSL 中运行
- Hermes 启动一个本地 stdio MCP 服务器
- 该 MCP 服务器通过 Windows 互操作（`cmd.exe` 或 `powershell.exe`）启动
- MCP 服务器附加到你实时的 Windows Chrome 会话

心智模型：

```text
Hermes (WSL) -> MCP stdio 桥接 -> Windows Chrome
```

### 为什么这种模式有用

- 你可以保留真实的 Windows 浏览器配置文件、Cookie 和登录状态
- Hermes 保持在其受支持的 Unix 环境（WSL2）中
- 浏览器控制作为 MCP 工具暴露，而不是依赖 Hermes 核心的浏览器传输

### 推荐的服务器

使用 `chrome-devtools-mcp`。

如果你的 Windows Chrome 已经通过 `chrome://inspect/#remote-debugging` 启用了实时远程调试，可以从 WSL 这样添加它：

```bash
hermes mcp add chrome-devtools-win --command cmd.exe --args /c "npx -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics"
```

保存服务器后：

```bash
hermes mcp test chrome-devtools-win
```

然后启动一个新的 Hermes 会话或运行：

```text
/reload-mcp
```

### 典型提示词

加载后，Hermes 可以直接使用带 MCP 前缀的浏览器工具。例如：

```text
调用 MCP 工具 mcp_chrome_devtools_win_list_pages，列出当前浏览器标签页。
```

### 当 `/browser connect` 是错误工具时

如果 Hermes 在 WSL 中运行，而 Chrome 在 Windows 上运行，即使 Chrome 已打开且可调试，`/browser connect` 也可能会失败。

常见原因：

- WSL 无法访问 Chrome 向 Windows 工具暴露的同一主机本地端点
- 较新的 Chrome 实时调试流程与经典的 `ws://localhost:9222` 不同
- 从 Windows 端的辅助工具（如 `chrome-devtools-mcp`）更容易附加到浏览器

在这些情况下，对于相同环境的设置使用 `/browser connect`，对于 WSL 到 Windows 的浏览器桥接使用 MCP。

### 已知陷阱

- 当通过 MCP 使用 Windows stdio 可执行文件时，从 Windows 挂载的路径（如 `/mnt/c/Users/<你>` 或 `/mnt/c/workspace/...`）启动 Hermes。
- 如果你从 `/root` 或 `/home/...` 启动 Hermes，Windows 可能会在 MCP 服务器启动前发出 `UNC` 当前目录警告。
- 如果 `chrome-devtools-mcp --autoConnect` 在枚举页面时超时，请减少 Chrome 中的后台/冻结标签页并重试。

### 示例：黑名单危险操作

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
1. 服务器原生 MCP 工具
- 通过以下配置过滤：
  - `tools.include`
  - `tools.exclude`

2. Hermes 添加的实用工具包装器
- 通过以下配置过滤：
  - `tools.resources`
  - `tools.prompts`

### 您可能看到的实用工具包装器

资源：
- `list_resources`
- `read_resource`

提示词：
- `list_prompts`
- `get_prompt`

这些包装器仅在以下情况下出现：
- 您的配置允许它们，并且
- MCP 服务器会话实际支持这些功能

因此，如果服务器没有资源/提示词，Hermes 不会假装它有。

## 常见模式

### 模式 1：本地项目助手

当您希望 Hermes 在一个有界的工作空间上进行推理时，使用 MCP 连接仓库本地的文件系统或 git 服务器。

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
审查项目结构并找出配置所在的位置。
```

```text
检查本地 git 状态并总结最近的变化。
```

### 模式 2：GitHub 分类助手

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
列出关于 MCP 的未解决问题，按主题聚类，并为最常见的错误草拟一个高质量的问题。
```

```text
在仓库中搜索 _discover_and_register_server 的使用情况，并解释 MCP 工具是如何注册的。
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

## 教程：带过滤功能的端到端设置

这是一个实用的步骤。

### 阶段 1：使用严格的白名单添加 GitHub MCP

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

如果您稍后也需要更新问题：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

然后重新加载：

```text
/reload-mcp
```

### 阶段 3：添加具有不同策略的第二个服务器

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

现在 Hermes 可以组合使用它们：

```text
检查本地项目文件，然后在 GitHub 上创建一个问题来总结您发现的错误。
```

这就是 MCP 的强大之处：无需更改 Hermes 核心即可实现多系统工作流。

## 安全使用建议

### 对于危险系统，优先使用允许列表

对于任何涉及财务、面向客户或具有破坏性的系统：
- 使用 `tools.include`
- 从尽可能小的集合开始

### 禁用未使用的实用工具

如果您不希望模型浏览服务器提供的资源/提示词，请将其关闭：

```yaml
tools:
  resources: false
  prompts: false
```

### 保持服务器范围狭窄

示例：
- 文件系统服务器根目录指向一个项目目录，而不是整个主目录
- git 服务器指向一个仓库
- 默认情况下暴露以读取为主工具的的内部 API 服务器

### 配置更改后重新加载

```text
/reload-mcp
```

在更改以下内容后执行此操作：
- include/exclude 列表
- 启用标志
- 资源/提示词开关
- 认证头信息 / 环境变量

## 按症状排查

### "服务器已连接，但我期望的工具缺失"

可能的原因：
- 被 `tools.include` 过滤
- 被 `tools.exclude` 排除
- 通过 `resources: false` 或 `prompts: false` 禁用了实用工具包装器
- 服务器实际上不支持资源/提示词

### "服务器已配置，但没有任何内容加载"

检查：
- 配置中没有遗留 `enabled: false`
- 命令/运行时存在（`npx`、`uvx` 等）
- HTTP 端点可访问
- 认证环境变量或头信息正确

### "为什么我看到的工具比 MCP 服务器宣传的少？"

因为 Hermes 现在尊重您的每服务器策略和基于功能的注册。这是预期的，通常也是可取的。

### "如何在不删除配置的情况下移除 MCP 服务器？"

使用：

```yaml
enabled: false
```

这将保留配置，但阻止连接和注册。

## 推荐的首次 MCP 设置

适合大多数用户的优秀初始服务器：
- 文件系统
- git
- GitHub
- fetch / 文档 MCP 服务器
- 一个范围狭窄的内部 API

不适合的初始服务器：
- 具有大量破坏性操作且没有过滤功能的大型业务系统
- 任何您不够了解而无法约束的系统

## 相关文档
- [MCP（模型上下文协议）](/docs/user-guide/features/mcp)
- [常见问题解答](/docs/reference/faq)
- [斜杠命令](/docs/reference/slash-commands)