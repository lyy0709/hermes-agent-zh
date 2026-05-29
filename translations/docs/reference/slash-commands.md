---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息平台斜杠命令的完整参考"
---

# 斜杠命令参考

Hermes 有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，注册表提供自动补全
- **消息平台斜杠命令** — 由 `gateway/run.py` 分发，注册表生成帮助文本和平台菜单

已安装的技能也会作为动态斜杠命令在这两个界面上暴露。这包括捆绑的技能，如 `/plan`，它会打开计划模式并将 Markdown 计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 下。

## 权限和管理员/用户划分

每个支持按用户允许列表的消息平台（Telegram、Discord、Slack、Matrix、Mattermost、Signal……）也支持两级斜杠命令划分：**管理员**获得每个已注册的命令，**普通用户**只获得你在 `user_allowed_commands` 中列出的命令名称（加上始终允许的基础命令 `/help` 和 `/whoami`）。在 `~/.hermes/gateway-config.yaml` 中相应平台的 `extra:` 块内配置 `allow_admin_from` 和 `user_allowed_commands`（以及按群组对应的 `group_allow_admin_from` / `group_user_allowed_commands`）。

请参阅各平台文档中的示例 — 结构在所有平台中都是相同的：

- [Telegram](../user-guide/messaging/telegram.md#slash-command-access-control)
- [Discord](../user-guide/messaging/discord.md)
- [Slack](../user-guide/messaging/slack.md)
- [Matrix](../user-guide/messaging/matrix.md)
- [Mattermost](../user-guide/messaging/mattermost.md)
- [Signal](../user-guide/messaging/signal.md)

如果某个作用域的 `allow_admin_from` 未设置，则该作用域将保持无限制的向后兼容模式 — 每个允许的用户都可以运行每个命令。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 以打开自动补全菜单。内置命令不区分大小写。

### 会话

| 命令 | 描述 |
|---------|-------------|
| `/new [name]` (别名: `/reset`) | 开始一个新会话（新的会话 ID + 历史记录）。可选的 `[name]` 设置初始会话标题 — 例如，`/new my-experiment` 打开一个已标题为 `my-experiment` 的新会话，以便稍后使用 `/resume` 或 `/sessions` 轻松找到。附加 `now`、`--yes` 或 `-y` 以跳过确认模态框 — 例如，`/reset now`、`/new --yes my-experiment`。 |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史记录 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一个用户/助手交换 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [focus topic]` | 手动压缩对话上下文（刷新记忆 + 摘要）。可选的重点主题可缩小摘要保留的范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [number]） |
| `/snapshot [create\|restore <id>\|prune]` (别名: `/snap`) | 创建或恢复 Hermes 配置/状态的状态快照。`create [label]` 保存快照，`restore <id>` 恢复到该快照，`prune [N]` 删除旧快照，或无参数列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>` (别名: `/q`) | 为下一轮排队一个提示词（不中断当前 Agent 响应）。 |
| `/steer <prompt>` | 注入一个在运行中的备注，该备注**在下一次工具调用之后**到达 Agent — 不中断，不创建新的用户轮次。文本在当前工具完成后附加到最后一个工具结果的内容中，为 Agent 提供新的上下文，而不会破坏当前的工具调用循环。使用此命令在任务中途调整方向（例如，当 Agent 正在运行测试时，“专注于认证模块”）。 |
| `/goal <text>` | 设置一个 Hermes 跨轮次持续努力实现的长期目标 — 我们对 Ralph 循环的实现。每轮之后，一个辅助判断模型决定目标是否完成；如果没有，Hermes 自动继续。预算默认为 20 轮（`goals.max_turns`）；任何真实的用户消息都会抢占继续循环，并且状态在 `/resume` 后保留。完整指南请参阅[持久目标](/user-guide/features/goals)。 |
| `/subgoal <text>` | 在活动目标循环中途追加一个用户提供的标准。继续提示词将逐字呈现所有子目标给 Agent，并且判断模型在做出 DONE/CONTINUE 裁决时会考虑它们 — 因此，只有在原始目标**和**每个子目标都满足时，目标才会被标记为完成。子命令：`/subgoal`（列表）、`/subgoal remove <N>`、`/subgoal clear`。需要有一个活动的 `/goal`。 |
| `/resume [name]` | 恢复一个先前命名的会话 |
| `/sessions` (TUI 别名: `/switch`) | 经典 CLI：在交互式选择器中浏览和恢复之前的会话。TUI：为当前打开的 TUI 会话打开实时会话切换器。在 TUI 中使用 `/sessions new` 立即启动另一个实时会话。 |
| `/redraw` | 强制完全重绘 UI（在 tmux 调整大小、鼠标选择伪影等之后恢复终端漂移） |
| `/status` | 显示会话信息 — 模型、提供商、配置文件、会话 ID、工作目录、标题、创建/更新时间戳、Token 总数、Agent 运行状态 — 后跟一个本地**会话摘要**块（最近的用户/助手轮次计数、工具结果计数、使用最多的工具、最近处理的几个文件、最新的用户提示词和最新的助手回复）。摘要是根据内存中的对话本地计算的；无需 LLM 调用，不影响提示词缓存。 |
| `/agents` (别名: `/tasks`) | 显示当前会话中活动的 Agent 和正在运行的任务。 |
| `/background <prompt>` (别名: `/bg`, `/btw`) | 在单独的背景会话中运行一个提示词。Agent 独立处理你的提示词 — 你的当前会话保持空闲以进行其他工作。任务完成后，结果会显示为一个面板。请参阅[CLI 背景会话](/user-guide/cli#background-sessions)。 |
| `/branch [name]` (别名: `/fork`) | 分支当前会话（探索不同的路径） |
| `/handoff <platform>` | **仅限 CLI。** 将当前会话移交给一个消息平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix）。消息网关会立即接收它，在支持线程的平台上创建一个新线程（Telegram 主题、Discord 文本频道线程、Slack 消息锚定线程），将目的地重新绑定到你的 CLI session_id 以便完整回放具有角色意识的转录，并伪造一个合成的用户轮次，以便 Agent 确认它正在新位置工作。成功后，你的 CLI 会干净地退出，并给出 `/resume` 提示；随时可以使用 `/resume <title>` 在本地恢复。在轮次中途拒绝。要求消息网关正在运行，并且为目标平台配置了主频道（从目标聊天中使用 `/sethome`）。请参阅[跨平台移交](/user-guide/sessions#cross-platform-handoff)。 |
### 配置

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [模型名称]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名的自定义提供商）、`/model custom`（从端点自动检测）以及用户定义的别名（`/model fav`、`/model grok` — 参见[自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商，请退出会话并从终端运行 `hermes model`。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)（适用于 OpenAI/Codex 模型）。`auto`（默认）使用 Hermes 的标准聊天补全；`codex_app_server` 将回合交给 `codex app-server` 子进程，用于原生 shell、apply_patch、ChatGPT 订阅认证和迁移的 Codex 插件。在下一次会话生效。 |
| `/personality` | 设置预定义的人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新任务 → 全部 → 详细。可以通过配置[为消息传递启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`、`fast`、`status`。 |
| `/reasoning` | 管理推理力度和显示（用法：/reasoning [级别\|show\|hide]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/statusbar` (别名：`/sb`) | 切换上下文/模型状态栏的开关 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的确认提示。 |
| `/footer [on\|off\|status]` | 切换最终回复上的消息网关运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅限 CLI：控制 Hermes 工作时按 Enter 键的行为 — 将新消息加入队列、在回合中途引导或立即中断。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅限 CLI：选择 TUI 忙碌指示器样式。 |

### 工具与技能

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [名称...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从 Agent 的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chromium 系列 CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome、Brave、Chromium 或 Edge 实例（默认：`http://127.0.0.1:9222`）。`disconnect` 断开连接。`status` 显示当前连接。如果未检测到调试器，会自动启动一个受支持的 Chromium 系列浏览器。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能 |
| `/bundles` | 列出已配置的技能包 — `/<名称>` 斜杠别名，可一次性预加载多个技能。在 `~/.hermes/config.yaml` 的 `bundles:` 下配置。参见[技能包](/user-guide/features/skills#skill-bundles)。 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/curator` | 后台技能维护 — `status`、`run`、`pin`、`archive`。参见[策展器](/user-guide/features/curator)。 |
| `/kanban <action>` | 无需离开聊天即可驱动多配置文件、多项目协作看板。完整的 `hermes kanban` 功能可用：`/kanban list`、`/kanban show t_abc`、`/kanban create "title" --assignee X`、`/kanban comment t_abc "text"`、`/kanban unblock t_abc`、`/kanban dispatch` 等。包含多看板支持：`/kanban boards list`、`/kanban boards create <slug>`、`/kanban boards switch <slug>`、`/kanban --board <slug> <action>`。参见[看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp` (别名：`/reload_mcp`) | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload-skills` (别名：`/reload_skills`) | 重新扫描 `~/.hermes/skills/` 以查找新安装或移除的技能 |
| `/reload` | 将 `.env` 变量重新加载到正在运行的会话中（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 Token 使用情况、成本明细、会话时长，以及 — 当活跃提供商提供时 — 一个**账户限制**部分，其中包含从提供商 API 实时拉取的剩余配额/积分/计划使用情况。 |
| `/insights` | 显示使用洞察和分析（最近 30 天） |
| `/platforms` (别名：`/gateway`) | 显示消息网关/消息传递平台状态（仅限 CLI 的摘要视图）。 |
| `/platform <list\|pause\|resume> [名称]` | 操作正在运行的消息网关平台。`/platform list` 列出每个适配器及其状态（运行中、因断路器暂停、手动暂停）；`/platform pause <名称>` 停止向该适配器分派新消息而不卸载它；`/platform resume <名称>` 重新启用它。当适配器的断路器因重复的可重试故障（网络/速率限制/5xx）而跳闸时，消息网关也会自动暂停该适配器 — 一旦上游恢复健康，使用 `/platform resume <名称>` 清除断路器。在消息网关可达的任何地方都可用（CLI 会话、Telegram、Discord 等）。 |
| `/paste` | 附加剪贴板图像 |
| `/copy [数字]` | 将最后一条助手响应复制到剪贴板（或使用数字指定倒数第 N 条）。仅限 CLI。 |
| `/image <路径>` | 为你的下一个提示词附加本地图像文件。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。在消息传递中也可用。 |
| `/profile` | 显示活跃配置文件名称和主目录 |
| `/gquota` | 显示 Google Gemini Code Assist 配额使用情况并带有进度条（仅在 `google-gemini-cli` 提供商活跃时可用）。 |
### 退出

| 命令 | 说明 |
|---------|-------------|
| `/quit` | 退出 CLI（同义词：`/exit`）。关于 `/q` 的说明请参见上文 `/queue` 部分。传递 `--delete`（或 `-d`）参数——例如 `/exit --delete`——可以在退出前同时永久删除当前会话的 SQLite 历史记录和磁盘上的对话记录。适用于对隐私敏感或一次性任务。 |

### 动态 CLI 斜杠命令

| 命令 | 说明 |
|---------|-------------|
| `/<技能名称>` | 将任何已安装的技能加载为按需命令。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方的可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

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

然后在 CLI 或消息平台上输入 `/status`、`/deploy` 或 `/inbox`。快捷命令在调度时解析，可能不会出现在每个内置的自动补全/帮助表中。

纯字符串的提示词快捷方式不支持作为快捷命令。请将较长的可重用提示词放在技能中，或使用 `type: alias` 指向现有的斜杠命令。

### 自定义模型别名

为您经常使用的模型定义自己的简称，然后在 CLI 或任何消息平台中使用 `/model <别名>` 来调用它们。别名在两者中的工作方式相同，适用于仅会话（默认）和 `--global` 开关。

支持两种配置格式：

**完整格式** — 固定一个确切的模型、提供商，以及可选的 base URL。将此内容放入 `~/.hermes/config.yaml`：

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  ollama-qwen:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

**简短格式** — 在一个字符串中使用 `provider/model`。无需编辑 YAML，直接从 shell 设置：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

然后在聊天中使用：

```
/model fav            # 仅限当前会话
/model grok --global  # 同时将当前模型的更改持久化到 config.yaml
```

用户定义的别名优先于内置的简称，因此将别名命名为 `sonnet`、`kimi`、`opus` 等会覆盖内置名称。别名不区分大小写。

### 别名解析

命令支持前缀匹配：输入 `/h` 会解析为 `/help`，输入 `/mod` 会解析为 `/model`。当前缀存在歧义（匹配多个命令）时，注册表顺序中的第一个匹配项胜出。完整的命令名称和已注册的别名始终优先于前缀匹配。

## 消息斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant 和 Teams 聊天中支持以下内置命令：

| 命令 | 说明 |
|---------|-------------|
| `/start` | 平台协议命令。许多聊天平台（Telegram、Discord 等）在用户首次打开机器人对话时会自动发送 `/start`。Hermes 会静默确认此 ping——不回复 Agent，不消耗会话回合——因此首次接触握手不会浪费回合。您也可以显式发送它以确认网关可达。 |
| `/new` | 开始新的对话。 |
| `/reset` | 重置对话历史记录。 |
| `/status` | 显示会话信息，后跟一个本地的**会话摘要**块（最近的回合数、使用最多的工具、触及的文件、最新的提示词 + 回复）。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名的自定义提供商（`/model custom:local:qwen`）、自动检测（`/model custom`）和用户定义的别名（`/model fav`、`/model grok`——参见[自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新的提供商或设置 API 密钥，请在终端（聊天会话之外）使用 `hermes model`。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)。持久化到 config.yaml 中的 `model.openai_runtime` 并驱逐缓存的 Agent，以便下一条消息获取新的运行时。在下一次会话生效。 |
| `/personality [name]` | 为会话设置人格覆盖层。 |
| `/fast [normal\|fast\|status]` | 切换快速模式——OpenAI 优先处理 / Anthropic 快速模式。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 移除最后一次交互。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为平台上的交付主频道。 |
| `/compress [focus topic]` | 手动压缩对话上下文。可选的重点主题可以缩小摘要保留的范围。 |
| `/topic [off\|help\|session-id]` | **仅限 Telegram 私信。** 管理用户管理的多会话主题模式。`/topic` 启用它或显示状态；`/topic off` 禁用它并清除绑定；`/topic help` 显示用法；在主题内使用 `/topic <session-id>` 恢复之前的会话。参见[多会话私信模式](/user-guide/messaging/telegram#multi-session-dm-mode-topic)。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示 Token 使用情况、估计的成本明细（输入/输出）、上下文窗口状态、会话持续时间，以及——当活跃提供商提供时——一个**账户限制**部分，其中包含从提供商 API 实时拉取的剩余配额/额度。 |
| `/insights [days]` | 显示使用情况分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理力度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在单独的后台会话中运行提示词。任务完成后，结果将发送回同一个聊天。参见[消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/queue <prompt>`（别名：`/q`） | 将提示词排队等待下一个回合，而不中断当前回合。 |
| `/steer <prompt>` | 在下一次工具调用后注入一条消息而不中断——模型会在下一次迭代中拾取它，而不是作为一个新回合。 |
| `/goal <text>` | 设置一个 Hermes 在多个回合中持续努力实现的目标——我们对 Ralph 循环的实现。一个评判模型会在每个回合后检查；如果未完成，Hermes 会自动继续，直到完成、您暂停/清除它，或达到回合预算（默认 20）。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。在 Agent 运行期间可以安全地运行 status/pause/clear；设置新目标需要先执行 `/stop`。参见[持久目标](/user-guide/features/goals)。 |
| `/footer [on\|off\|status]` | 切换最终回复上的运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/curator [status\|run\|pin\|archive]` | 后台技能维护控制。 |
| `/kanban <action>` | 从聊天中驱动多配置文件、多项目的协作看板——参数界面与 CLI 完全相同。绕过运行中 Agent 的防护，因此 `/kanban unblock t_abc`、`/kanban comment t_abc "…"`、`/kanban list --mine`、`/kanban boards switch <slug>` 等可以在回合中途工作。`/kanban create …` 会自动将发起聊天的频道订阅到新任务的终端事件。参见[看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的批准提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行一个待定的危险命令。`session` 仅批准当前会话；`always` 添加到永久允许列表。 |
| `/deny` | 拒绝一个待定的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在排空活跃运行后优雅地重启网关。当网关重新上线时，它会向请求者的聊天/线程发送确认信息。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享的链接。 |
| `/help` | 显示消息帮助。 |
| `/<技能名称>` | 按名称调用任何已安装的技能。 |
## 说明

- `/skin`、`/snapshot`、`/gquota`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy`、`/handoff` 和 `/quit` 是**仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny`、`/topic` 和 `/commands` 是**仅限消息平台**的命令。
- `/status`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/reload-skills`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator`、`/kanban`、`/sessions` 和 `/yolo` 在 **CLI 和消息网关** 中均可使用。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
- 在 TUI 中，`/sessions` 显示当前 TUI 进程中的活动会话。对于已保存或已关闭的对话记录，请使用 `/resume [name]` 或 `hermes --tui --resume <id-or-title>`。

## 破坏性命令的确认提示

CLI 在执行会丢弃未保存会话状态的斜杠命令之前会进行提示。当前的破坏性命令集如下：

| 命令 | 破坏内容 |
|---------|------------------|
| `/clear` | 清屏并开始一个新会话 —— 当前会话 ID 和内存中的历史记录将丢失。 |
| `/new` / `/reset` | 开始一个新会话（新的会话 ID + 空历史记录）。 |
| `/undo` | 从历史记录中移除最后一条用户/助手交互。 |
| `/exit --delete` / `/quit --delete` | 退出**并**永久删除当前会话的 SQLite 历史记录和磁盘上的对话记录。 |

对于这些命令，CLI 会打开一个三选一的模态框：**批准一次**（本次执行）、**始终批准**（执行并持久化设置 `approvals.destructive_slash_confirm: false`，以便未来的破坏性命令无需提示即可运行）或**取消**。

**内联跳过：** 附加 `now`、`--yes` 或 `-y` 可以绕过模态框以执行单次调用 —— 例如 `/reset now`、`/new --yes my-session`、`/clear -y`、`/undo -y`。这在模态框在您的终端上无法正确渲染时（参见 [issue #30768](https://github.com/NousResearch/hermes-agent/issues/30768) 了解原生 Windows PowerShell 的情况）或在针对 CLI 编写脚本时很有用。

在 `~/.hermes/config.yaml` 中设置 `approvals.destructive_slash_confirm: false` 可以全局禁用提示；将其设置回 `true` 可以重新启用。相关背景请参阅 [安全 — 破坏性斜杠命令确认](../user-guide/security.md#dangerous-command-approval)。