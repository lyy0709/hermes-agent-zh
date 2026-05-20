---
sidebar_position: 11
title: "ACP 编辑器集成"
description: "在 ACP 兼容的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes Agent"
---

# ACP 编辑器集成

Hermes Agent 可以作为 ACP 服务器运行，让 ACP 兼容的编辑器通过 stdio 与 Hermes 通信并渲染：

- 聊天消息
- 工具活动
- 文件差异
- 终端命令
- 批准提示
- 流式思考/响应块

当你希望 Hermes 表现得像一个编辑器原生的编码 Agent，而不是一个独立的 CLI 或消息机器人时，ACP 是一个很好的选择。

## Hermes 在 ACP 模式下暴露的内容

Hermes 运行时会使用一个为编辑器工作流精心设计的 `hermes-acp` 工具集。它包括：

- 文件工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端工具：`terminal`、`process`
- 网页/浏览器工具
- 记忆、待办事项、会话搜索
- 技能
- `execute_code` 和 `delegate_task`
- 视觉功能

它特意排除了不适合典型编辑器用户体验的内容，例如消息传递和定时任务管理。

## 安装

正常安装 Hermes，然后添加 ACP 额外依赖：

```bash
pip install -e '.[acp]'
```

这将安装 `agent-client-protocol` 依赖并启用：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

对于 Zed 注册表安装，Zed 通过官方的 ACP 注册表条目启动 Hermes。该条目使用 `uvx` 分发版运行：

```bash
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

在使用注册表安装路径之前，请确保 `uv` 在 `PATH` 中可用。

## 启动 ACP 服务器

以下任一命令都可以在 ACP 模式下启动 Hermes：

```bash
hermes acp
```

```bash
hermes-acp
```

```bash
python -m acp_adapter
```

Hermes 将日志输出到 stderr，因此 stdout 保留给 ACP JSON-RPC 通信使用。

对于非交互式检查：

```bash
hermes acp --version
hermes acp --check
```

### 浏览器工具（可选）

浏览器工具（`browser_navigate`、`browser_click` 等）依赖于 `agent-browser` npm 包和 Chromium，它们不是 Python wheel 的一部分。使用以下命令安装它们：

```bash
hermes acp --setup-browser           # 交互式（在约 400 MB 下载前提示）
hermes acp --setup-browser --yes     # 非交互式接受下载
```

这是一个独立的命令。Zed 注册表的终端认证流程（`hermes acp --setup`）在模型选择后也会将浏览器引导程序作为后续问题提供，因此大多数用户永远不需要直接运行 `--setup-browser`。

它的作用：

- 如果缺失，将 Node.js 22 LTS 安装到 `~/.hermes/node/`
- 将 `npm install -g agent-browser @askjo/camofox-browser` 安装到该前缀（无需 sudo — `npm` 的 `--prefix` 指向用户可写的 Hermes 管理的 Node）
- 安装 Playwright Chromium，或者在检测到系统 Chrome/Chromium 可用时使用它

引导程序是幂等的 — 重新运行它很快，并且会跳过已经完成的工作。

## 编辑器设置

### VS Code

安装 [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) 扩展。

连接步骤：

1. 从活动栏打开 ACP Client 面板。
2. 从内置 Agent 列表中选择 **Hermes Agent**。
3. 连接并开始聊天。

如果你想手动定义 Hermes，可以通过 VS Code 设置中的 `acp.agents` 添加：

```json
{
  "acp.agents": {
    "Hermes Agent": {
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

### Zed

Zed v0.221.x 及更高版本通过官方的 ACP 注册表安装外部 Agent。

1. 打开 Agent 面板。
2. 点击 **Add Agent**，或运行 `zed: acp registry` 命令。
3. 搜索 **Hermes Agent**。
4. 安装它并启动一个新的 Hermes 外部 Agent 线程。

前提条件：

- 首先使用 `hermes model` 配置 Hermes 提供商凭据，或在 `~/.hermes/.env` / `~/.hermes/config.yaml` 中设置。
- 安装 `uv`，以便注册表启动器可以运行 `uvx --from 'hermes-agent[acp]==<version>' hermes-acp`。

在注册表条目可用之前进行本地开发时，请在 Zed 设置中使用自定义 Agent 服务器：

```json
{
  "agent_servers": {
    "hermes-agent": {
      "type": "custom",
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

### JetBrains

使用 ACP 兼容的插件，并将其指向：

```text
/path/to/hermes-agent/acp_registry
```

## 注册表清单

Hermes 官方 ACP 注册表元数据的源副本位于：

```text
acp_registry/agent.json
acp_registry/icon.svg
```

上游注册表 PR 将这些文件复制到 `agentclientprotocol/registry` 中的顶级 `hermes-agent/` 目录。

注册表条目使用 `uvx` 分发版，直接指向 `hermes-agent` PyPI 发布：

```text
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

注册表 CI 会验证固定的版本是否存在于 PyPI 上，因此清单的 `version` 和 uvx `package` 固定必须始终与 `pyproject.toml` 匹配。`scripts/release.py` 会自动保持它们同步。

## 配置和凭据

ACP 模式使用与 CLI 相同的 Hermes 配置：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供商解析使用 Hermes 正常的运行时解析器，因此 ACP 继承当前配置的提供商和凭据。Hermes 还为首次运行的注册表客户端提供终端认证方法（`--setup`）；这会打开 Hermes 的交互式模型/提供商设置。

## 会话行为

ACP 会话由 ACP 适配器的内存会话管理器在服务器运行时跟踪。

每个会话存储：

- 会话 ID
- 工作目录
- 选定的模型
- 当前对话历史
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 正常的持久化/日志路径，但 ACP 的 `list/load/resume/fork` 范围限定在当前运行的 ACP 服务器进程内。

## 工作目录行为

ACP 会话将编辑器的 cwd 绑定到 Hermes 任务 ID，因此文件和终端工具相对于编辑器工作空间运行，而不是服务器进程的 cwd。

## 批准

危险的终端命令可以路由回编辑器作为批准提示。ACP 批准选项比 CLI 流程更简单：

- 允许一次
- 始终允许
- 拒绝

超时或出错时，批准桥接器会拒绝请求。

### 会话范围的编辑自动批准

ACP 在*允许一次*和*始终允许*之间暴露了第三个层级：**允许在此会话中**。从编辑器的权限提示中选择此选项，仅将批准记录在当前 ACP 会话中 — 该会话中后续所有匹配的命令都会无提示通过，但新的 ACP 会话（或重启编辑器）会重置状态，并在第一次时重新提示。

| 选项 | 编辑器标签 | 范围 | 跨重启持久化 |
|---|---|---|---|
| `allow_once` | 允许一次 | 这一次工具调用 | 否 |
| `allow_session` | 允许在此会话中 | 此 ACP 会话中所有匹配的调用 | 否 — 会话结束时清除 |
| `allow_always` | 始终允许 | 所有未来会话 | 是（写入 Hermes 永久允许列表） |
| `deny` | 拒绝 | 这一次工具调用 | 否 |

`allow_session` 是编辑器工作流的正确默认设置，在该工作流中，你信任一个 Agent 执行任务期间，但不想授予长期有效的允许列表条目。安全权衡很简单：范围越广，编辑器中断你的次数就越少，而行为不当的 Agent（或提示注入）在你注意到之前可能造成的损害就越大。对于不熟悉的命令，从 `allow_once` 开始；在多次看到 Agent 正确运行相同模式后，提升到 `allow_session`；将 `allow_always` 保留给你永远信任的真正幂等命令（例如 `git status`）。

ACP 桥接器将这些选项映射到 Hermes 内部的批准语义 — `allow_always` 写入永久允许列表条目，方式与 CLI 相同，而 `allow_session` 仅影响当前 ACP 会话的进程内批准缓存。

## 故障排除

### 编辑器中未出现 ACP Agent

检查：

- 在 Zed 中，使用 `zed: acp registry` 打开 ACP 注册表并搜索 **Hermes Agent**。
- 对于手动/本地开发，验证自定义的 `agent_servers` 命令指向 `hermes acp`。
- Hermes 已安装并在你的 PATH 中。
- ACP 额外依赖已安装（`pip install -e '.[acp]'`）。
- 如果从官方的 Zed 注册表条目启动，请安装 `uv`。

### ACP 启动但立即出错

尝试以下检查：

```bash
hermes acp --version
hermes acp --check
hermes doctor
hermes status
```

### 缺少凭据

ACP 模式使用 Hermes 现有的提供商设置。使用以下命令配置凭据：

```bash
hermes model
```

或通过编辑 `~/.hermes/.env`。注册表客户端也可以触发 Hermes 的终端认证流程，该流程运行相同的交互式提供商/模型设置。

### Zed 注册表启动器找不到 uv

从官方 uv 安装文档安装 `uv`，然后从 Zed 重试 Hermes Agent 线程。

## 另请参阅

- [ACP 内部原理](../../developer-guide/acp-internals.md)
- [提供商运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)