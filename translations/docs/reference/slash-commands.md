---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息斜杠命令的完整参考"
---

# 斜杠命令参考

Hermes 有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，并从注册表提供自动补全
- **消息斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单根据注册表生成

已安装的技能也会作为动态斜杠命令在这两个界面上公开。这包括捆绑的技能，如 `/plan`，它会打开计划模式并将 Markdown 计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 下。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 以打开自动补全菜单。内置命令不区分大小写。

### 会话

| 命令 | 描述 |
|---------|-------------|
| `/new` (别名: `/reset`) | 开始一个新会话（新的会话 ID + 历史记录） |
| `/clear` | 清屏并开始一个新会话 |
| `/history` | 显示对话历史记录 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一组用户/助手交换 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [focus topic]` | 手动压缩对话上下文（刷新记忆 + 摘要）。可选的焦点主题可以缩小摘要保留的范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/snapshot [create\|restore <id>\|prune]` (别名: `/snap`) | 创建或恢复 Hermes 配置/状态的状态快照。`create [标签]` 保存快照，`restore <id>` 恢复到该快照，`prune [N]` 删除旧快照，或无参数列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>` (别名: `/q`) | 为下一轮排队一个提示词（不会中断当前 Agent 的响应）。 |
| `/steer <prompt>` | 注入一个在运行中的备注，该备注**在下一次工具调用之后**到达 Agent — 不中断，不创建新的用户轮次。文本在当前工具完成后附加到最后一个工具结果的内容中，为 Agent 提供新的上下文，而不会破坏当前的工具调用循环。使用此命令在任务中途调整方向（例如，当 Agent 正在运行测试时，“专注于认证模块”）。 |
| `/resume [name]` | 恢复一个先前命名的会话 |
| `/redraw` | 强制完全重绘 UI（在 tmux 调整大小、鼠标选择伪影等之后恢复终端漂移） |
| `/status` | 显示会话信息 |
| `/agents` (别名: `/tasks`) | 显示当前会话中活跃的 Agent 和正在运行的任务。 |
| `/background <prompt>` (别名: `/bg`, `/btw`) | 在单独的后台会话中运行一个提示词。Agent 独立处理你的提示词 — 你的当前会话保持空闲以进行其他工作。任务完成后，结果会以面板形式出现。参见 [CLI 后台会话](/docs/user-guide/cli#background-sessions)。 |
| `/branch [name]` (别名: `/fork`) | 分支当前会话（探索不同的路径） |

### 配置

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`，`/model provider:model`（切换提供商），`/model custom:model`（自定义端点），`/model custom:name:model`（命名的自定义提供商），`/model custom`（从端点自动检测）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新的提供商，请退出会话并从终端运行 `hermes model`。 |
| `/personality` | 设置预定义的人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新工具 → 所有工具 → 详细。可以通过配置[为消息启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`，`fast`，`status`。 |
| `/reasoning` | 管理推理力度和显示（用法：/reasoning [级别\|show\|hide]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/statusbar` (别名: `/sb`) | 切换上下文/模型状态栏的开关 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的确认提示。 |
| `/footer [on\|off\|status]` | 切换最终回复上的消息网关运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅限 CLI：控制当 Hermes 正在工作时按 Enter 键的作用 — 将新消息排队、在轮次中途引导或立即中断。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅限 CLI：选择 TUI 忙碌指示器样式。 |

### 工具与技能

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从 Agent 的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 分离。`status` 显示当前连接。如果未检测到调试器，则自动启动 Chrome。 |
| `/skills` | 从在线注册表中搜索、安装、检查或管理技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/curator` | 后台技能维护 — `status`，`run`，`pin`，`archive`。参见 [Curator](/docs/user-guide/features/curator)。 |
| `/reload-mcp` (别名: `/reload_mcp`) | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload` | 将 `.env` 变量重新加载到正在运行的会话中（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |
### 信息

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 Token 使用量、成本明细、会话时长，以及 — 当活跃提供商支持时 — 一个 **账户限制** 部分，其中包含从提供商 API 实时拉取的剩余配额/积分/套餐使用情况。 |
| `/insights` | 显示使用情况洞察和分析（最近 30 天） |
| `/platforms` (别名: `/gateway`) | 显示消息网关/消息平台状态 |
| `/paste` | 附加剪贴板中的图像 |
| `/copy [数字]` | 将最后一条助手回复复制到剪贴板（或使用数字指定倒数第 N 条）。仅限 CLI。 |
| `/image <路径>` | 为你的下一个提示词附加本地图像文件。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。在消息传递中也可用。 |
| `/profile` | 显示活跃配置文件名和主目录 |
| `/gquota` | 显示 Google Gemini Code Assist 配额使用情况（带进度条）（仅在 `google-gemini-cli` 提供商活跃时可用）。 |

### 退出

| 命令 | 描述 |
|---------|-------------|
| `/quit` | 退出 CLI（也可用：`/exit`）。 |

### 动态 CLI 斜杠命令

| 命令 | 描述 |
|---------|-------------|
| `/<技能名称>` | 将任何已安装的技能加载为按需命令。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方的可选技能目录中搜索、浏览、检查、安装、审核、发布和配置技能。 |

### 快捷命令

用户定义的快捷命令将一个简短的斜杠命令映射到 shell 命令或另一个斜杠命令。在 `~/.hermes/config.yaml` 中配置它们：

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  deploy:
    type: exec
    command: scripts/deploy.sh
  inbox:
    type: alias
    target: /gmail unread
```

然后在 CLI 或消息平台中输入 `/status`、`/deploy` 或 `/inbox`。快捷命令在调度时解析，可能不会出现在每个内置的自动补全/帮助表中。

纯字符串的提示词快捷方式不支持作为快捷命令。将较长的可重用提示词放在技能中，或使用 `type: alias` 指向现有的斜杠命令。

### 别名解析

命令支持前缀匹配：输入 `/h` 会解析为 `/help`，输入 `/mod` 会解析为 `/model`。当前缀存在歧义（匹配多个命令）时，按注册表顺序的第一个匹配项胜出。完整的命令名称和已注册的别名始终优先于前缀匹配。

## 消息传递斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中支持以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始新的对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的 Agent。 |
| `/model [提供商:模型]` | 显示或更改模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名的自定义提供商（`/model custom:local:qwen`）和自动检测（`/model custom`）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商或设置 API 密钥，请从你的终端（在聊天会话之外）使用 `hermes model`。 |
| `/personality [名称]` | 为会话设置灵魂（人格）覆盖层。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先处理 / Anthropic 快速模式。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 移除最后一次交互。 |
| `/sethome` (别名: `/set-home`) | 将当前聊天标记为平台的主频道，用于交付。 |
| `/compress [聚焦主题]` | 手动压缩对话上下文。可选的聚焦主题可缩小摘要保留的范围。 |
| `/title [名称]` | 设置或显示会话标题。 |
| `/resume [名称]` | 恢复之前命名的会话。 |
| `/usage` | 显示 Token 使用量、预估成本明细（输入/输出）、上下文窗口状态、会话时长，以及 — 当活跃提供商支持时 — 一个 **账户限制** 部分，其中包含从提供商 API 实时拉取的剩余配额/积分。 |
| `/insights [天数]` | 显示使用情况分析。 |
| `/reasoning [级别\|show\|hide]` | 更改推理强度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [数字]` | 列出或恢复文件系统检查点。 |
| `/background <提示词>` | 在单独的后台会话中运行提示词。任务完成后，结果将传回同一聊天。参见[消息传递后台会话](/docs/user-guide/messaging/#background-sessions)。 |
| `/queue <提示词>` (别名: `/q`) | 为下一轮排队一个提示词，不中断当前轮次。 |
| `/steer <提示词>` | 在下一次工具调用后注入一条消息而不中断 — 模型会在下一次迭代时拾取它，而不是作为新的一轮。 |
| `/footer [on\|off\|status]` | 切换最终回复上的运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/curator [status\|run\|pin\|archive]` | 后台技能维护控制。 |
| `/reload-mcp` (别名: `/reload_mcp`) | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的批准提示。 |
| `/commands [页码]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行一个待定的危险命令。`session` 仅为此会话批准；`always` 添加到永久允许列表。 |
| `/deny` | 拒绝一个待定的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在排空活跃运行后优雅地重启消息网关。当消息网关重新上线时，它会向请求者的聊天/线程发送确认信息。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。 |
| `/help` | 显示消息传递帮助。 |
| `/<技能名称>` | 按名称调用任何已安装的技能。 |
## 注意事项

- `/skin`、`/snapshot`、`/gquota`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy` 和 `/quit` 是**仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny` 和 `/commands` 是**仅限消息平台**的命令。
- `/status`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator` 和 `/yolo` 在 **CLI 和消息网关**中均可使用。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。