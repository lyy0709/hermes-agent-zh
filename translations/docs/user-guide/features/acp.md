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
- 审批提示
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

它有意排除了不适合典型编辑器用户体验的功能，例如消息传递和定时任务管理。

## 安装

正常安装 Hermes，然后添加 ACP 额外依赖：

```bash
pip install -e '.[acp]'
```

这将安装 `agent-client-protocol` 依赖并启用：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

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

## 编辑器设置

### VS Code

安装 [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) 扩展。

连接步骤：

1.  从活动栏打开 ACP Client 面板。
2.  从内置 Agent 列表中选择 **Hermes Agent**。
3.  连接并开始聊天。

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

示例设置片段：

```json
{
  "agent_servers": {
    "hermes-agent": {
      "type": "custom",
      "command": "hermes",
      "args": ["acp"],
    },
  },
}
```

### JetBrains

使用兼容 ACP 的插件，并将其指向：

```text
/path/to/hermes-agent/acp_registry
```

## 注册表清单

ACP 注册表清单位于：

```text
acp_registry/agent.json
```

它声明了一个基于命令的 Agent，其启动命令为：

```text
hermes acp
```

## 配置和凭据

ACP 模式使用与 CLI 相同的 Hermes 配置：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供商解析使用 Hermes 正常的运行时解析器，因此 ACP 会继承当前配置的提供商和凭据。

## 会话行为

ACP 会话由 ACP 适配器的内存会话管理器在服务器运行时进行跟踪。

每个会话存储：

- 会话 ID
- 工作目录
- 选定的模型
- 当前对话历史
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 正常的持久化/日志路径，但 ACP 的 `list/load/resume/fork` 操作仅限于当前运行的 ACP 服务器进程。

## 工作目录行为

ACP 会话将编辑器的当前工作目录绑定到 Hermes 任务 ID，因此文件和终端工具会相对于编辑器工作区运行，而不是服务器进程的当前工作目录。

## 审批

危险的终端命令可以作为审批提示路由回编辑器。ACP 的审批选项比 CLI 流程更简单：

- 允许一次
- 始终允许
- 拒绝

在超时或出错时，审批桥接器会拒绝请求。

## 故障排除

### 编辑器中未显示 ACP Agent

检查：

- 编辑器是否指向正确的 `acp_registry/` 路径
- Hermes 是否已安装并在你的 PATH 中
- 是否安装了 ACP 额外依赖 (`pip install -e '.[acp]'`)

### ACP 启动但立即报错

尝试以下检查：

```bash
hermes doctor
hermes status
hermes acp
```

### 缺少凭据

ACP 模式没有自己的登录流程。它使用 Hermes 现有的提供商设置。通过以下方式配置凭据：

```bash
hermes model
```

或通过编辑 `~/.hermes/.env`。

## 另请参阅

- [ACP 内部机制](../../developer-guide/acp-internals.md)
- [提供商运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)