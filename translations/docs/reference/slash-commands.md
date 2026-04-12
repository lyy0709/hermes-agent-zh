---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息平台斜杠命令的完整参考"
---

# 斜杠命令参考

Hermes 有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，并从注册表提供自动补全
- **消息平台斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单根据注册表生成

已安装的技能也会作为动态斜杠命令暴露在这两个界面上。这包括捆绑的技能，如 `/plan`，它会打开计划模式并将 markdown 计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 可打开自动补全菜单。内置命令不区分大小写。

### 会话

| 命令 | 描述 |
|---------|-------------|
| `/new` (别名: `/reset`) | 开始一个新会话（新的会话 ID + 历史记录） |
| `/clear` | 清屏并开始一个新会话 |
| `/history` | 显示对话历史记录 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一条用户/助手消息交换 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress` | 手动压缩对话上下文（刷新记忆 + 总结） |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>` (别名: `/q`) | 为下一轮排队一个提示词（不中断当前 Agent 响应）。**注意：** `/q` 同时被 `/queue` 和 `/quit` 占用；最后注册的命令生效，因此实践中 `/q` 解析为 `/quit`。请明确使用 `/queue`。 |
| `/resume [name]` | 恢复一个先前命名的会话 |
| `/statusbar` (别名: `/sb`) | 切换上下文/模型状态栏的开关 |
| `/background <prompt>` (别名: `/bg`) | 在单独的后台会话中运行一个提示词。Agent 独立处理你的提示词 — 你的当前会话可以自由处理其他工作。任务完成后，结果会以面板形式显示。参见 [CLI 后台会话](/docs/user-guide/cli#background-sessions)。 |
| `/btw <question>` | 使用会话上下文提出临时性的附带问题（不使用工具，不持久化）。适用于在不影响对话历史的情况下快速澄清问题。 |
| `/plan [request]` | 加载捆绑的 `plan` 技能来编写 markdown 计划，而不是执行工作。计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。 |
| `/branch [name]` (别名: `/fork`) | 分支当前会话（探索不同的路径） |

### 配置

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名的自定义提供商）、`/model custom`（从端点自动检测） |
| `/provider` | 显示可用的提供商和当前提供商 |
| `/personality` | 设置预定义的人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 仅新 → 全部 → 详细。可以通过配置[为消息平台启用](#notes)。 |
| `/reasoning` | 管理推理力度和显示（用法：/reasoning [级别\|显示\|隐藏]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的确认提示。 |

### 工具与技能

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从 Agent 的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 断开连接。`status` 显示当前连接状态。如果未检测到调试器，则自动启动 Chrome。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/reload-mcp` (别名: `/reload_mcp`) | 从 config.yaml 重新加载 MCP 服务器 |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 Token 使用量、成本细分和会话时长 |
| `/insights` | 显示使用情况洞察和分析（最近 30 天） |
| `/platforms` (别名: `/gateway`) | 显示消息网关/消息平台状态 |
| `/paste` | 检查剪贴板中是否有图像并附加它 |
| `/profile` | 显示活动配置文件名称和主目录 |

### 退出

| 命令 | 描述 |
|---------|-------------|
| `/quit` | 退出 CLI（也可用：`/exit`）。请参阅上面 `/queue` 下关于 `/q` 的说明。 |

### 动态 CLI 斜杠命令

| 命令 | 描述 |
|---------|-------------|
| `/<skill-name>` | 将任何已安装的技能加载为按需命令。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方的可选技能目录中搜索、浏览、检查、安装、审核、发布和配置技能。 |

### 快捷命令

用户定义的快捷命令将一个短别名映射到一个较长的提示词。在 `~/.hermes/config.yaml` 中配置它们：

```yaml
quick_commands:
  review: "Review my latest git diff and suggest improvements"
  deploy: "Run the deployment script at scripts/deploy.sh and verify the output"
  morning: "Check my calendar, unread emails, and summarize today's priorities"
```

然后在 CLI 中输入 `/review`、`/deploy` 或 `/morning`。快捷命令在分发时解析，不会显示在内置的自动补全/帮助表中。

### 别名解析

命令支持前缀匹配：输入 `/h` 解析为 `/help`，`/mod` 解析为 `/model`。当前缀存在歧义（匹配多个命令）时，注册表顺序中的第一个匹配项胜出。完整的命令名称和已注册的别名始终优先于前缀匹配。

## 消息平台斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中支持以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始一个新对话。 |
| `/reset` | 重置对话历史记录。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名的自定义提供商（`/model custom:local:qwen`）和自动检测（`/model custom`）。 |
| `/provider` | 显示提供商可用性和认证状态。 |
| `/personality [name]` | 为会话设置人格叠加层。 |
| `/retry` | 重试最后一条消息。 |
| `/undo` | 移除最后一条消息交换。 |
| `/sethome` (别名: `/set-home`) | 将当前聊天标记为平台的主频道，用于接收交付。 |
| `/compress` | 手动压缩对话上下文。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复一个先前命名的会话。 |
| `/usage` | 显示 Token 使用量、估计的成本细分（输入/输出）、上下文窗口状态和会话时长。 |
| `/insights [days]` | 显示使用情况分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理力度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在单独的后台会话中运行一个提示词。任务完成后，结果会发送回同一个聊天。参见 [消息平台后台会话](/docs/user-guide/messaging/#background-sessions)。 |
| `/plan [request]` | 加载捆绑的 `plan` 技能来编写 markdown 计划，而不是执行工作。计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。 |
| `/reload-mcp` (别名: `/reload_mcp`) | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的确认提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行一个待处理的危险命令。`session` 仅为此会话批准；`always` 添加到永久允许列表。 |
| `/deny` | 拒绝一个待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/help` | 显示消息平台帮助。 |
| `/<skill-name>` | 按名称调用任何已安装的技能。 |

## 注意事项

- `/skin`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/statusbar` 和 `/plugins` 是 **仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置。
- `/status`、`/sethome`、`/update`、`/approve`、`/deny` 和 `/commands` 是 **仅限消息平台** 的命令。
- `/background`、`/voice`、`/reload-mcp`、`/rollback` 和 `/yolo` 在 **CLI 和消息网关** 中都有效。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。