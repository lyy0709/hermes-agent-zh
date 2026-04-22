---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面——命令、快捷键、人格设定等"
---

# CLI 界面

Hermes Agent 的 CLI 是一个完整的终端用户界面（TUI）——而非网页 UI。它具备多行编辑、斜杠命令自动补全、对话历史记录、中断与重定向以及流式工具输出等功能。专为终端重度用户打造。

:::tip
Hermes 还附带了一个现代化的 TUI，支持模态叠加、鼠标选择和非阻塞输入。使用 `hermes --tui` 启动——请参阅 [TUI](tui.md) 指南。
:::

## 运行 CLI

```bash
# 启动交互式会话（默认）
hermes

# 单次查询模式（非交互式）
hermes chat -q "Hello"

# 使用特定模型
hermes chat --model "anthropic/claude-sonnet-4"

# 使用特定提供商
hermes chat --provider nous        # 使用 Nous Portal
hermes chat --provider openrouter  # 强制使用 OpenRouter

# 使用特定工具集
hermes chat --toolsets "web,terminal,skills"

# 启动时预加载一个或多个技能
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "open a draft PR"

# 恢复之前的会话
hermes --continue             # 恢复最近的 CLI 会话 (-c)
hermes --resume <session_id>  # 按 ID 恢复特定会话 (-r)

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 git worktree（用于并行运行多个 Agent）
hermes -w                         # worktree 中的交互模式
hermes -w -q "Fix issue #123"     # worktree 中的单次查询
```

## 界面布局

<img className="docs-terminal-figure" src="/img/docs/cli-layout.svg" alt="Hermes CLI 布局的样式化预览，展示了横幅、对话区域和固定的输入提示符。" />
<p className="docs-figure-caption">Hermes CLI 横幅、对话流和固定输入提示符，渲染为稳定的文档图形而非脆弱的文本艺术。</p>

欢迎横幅一目了然地显示您的模型、终端后端、工作目录、可用工具和已安装的技能。

### 状态栏

一个持久的状态栏位于输入区域上方，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（如果超过 26 个字符则截断） |
| Token 计数 | 已使用的上下文 Token / 最大上下文窗口 |
| 上下文条 | 带有颜色编码阈值的视觉填充指示器 |
| 成本 | 预估的会话成本（对于未知/零成本模型显示为 `n/a`） |
| 持续时间 | 已用会话时间 |

状态栏会根据终端宽度自适应——在 ≥ 76 列时显示完整布局，在 52–75 列时显示紧凑布局，在低于 52 列时显示最小布局（仅模型和持续时间）。

**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|-------|-----------|---------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 即将填满 |
| 橙色 | 80–95% | 接近限制 |
| 红色 | ≥ 95% | 即将溢出——考虑使用 `/compress` |

使用 `/usage` 获取详细分类，包括每类成本（输入与输出 Token）。

### 会话恢复显示

当恢复之前的会话时（`hermes -c` 或 `hermes --resume <id>`），一个“先前对话”面板会出现在横幅和输入提示符之间，显示对话历史的紧凑摘要。详情和配置请参阅 [会话 - 恢复时的对话摘要](sessions.md#conversation-recap-on-resume)。

## 快捷键

| 按键 | 操作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Alt+Enter` 或 `Ctrl+J` | 新行（多行输入） |
| `Alt+V` | 当终端支持时，从剪贴板粘贴图像 |
| `Ctrl+V` | 粘贴文本并视情况附加剪贴板图像 |
| `Ctrl+B` | 当语音模式启用时，开始/停止语音录制（`voice.record_key`，默认：`ctrl+b`） |
| `Ctrl+C` | 中断 Agent（在 2 秒内双击以强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 将 Hermes 挂起到后台（仅限 Unix）。在 shell 中运行 `fg` 以恢复。 |
| `Tab` | 接受自动建议（幽灵文本）或自动补全斜杠命令 |

## 斜杠命令

输入 `/` 以查看自动补全下拉菜单。Hermes 支持大量 CLI 斜杠命令、动态技能命令和用户定义的快捷命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助 |
| `/model` | 显示或更改当前模型 |
| `/tools` | 列出当前可用工具 |
| `/skills browse` | 浏览技能中心和官方可选技能 |
| `/background <prompt>` | 在单独的背景会话中运行提示词 |
| `/skin` | 显示或切换活动的 CLI 皮肤 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 录制） |
| `/voice tts` | 切换 Hermes 回复的语音播放 |
| `/reasoning high` | 增加推理力度 |
| `/title My Session` | 为当前会话命名 |

完整的 CLI 和消息内置命令列表，请参阅 [斜杠命令参考](../reference/slash-commands.md)。

关于设置、提供商、静音调优以及消息平台/Discord 语音使用，请参阅 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写——`/HELP` 与 `/help` 效果相同。已安装的技能也会自动成为斜杠命令。
:::

## 快捷命令

您可以定义自定义命令，这些命令会立即运行 shell 命令而无需调用 LLM。这些命令在 CLI 和消息平台（Telegram、Discord 等）中均可使用。

```yaml
# ~/.hermes/config.yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```

然后在任何聊天中输入 `/status` 或 `/gpu`。更多示例请参阅 [配置指南](/docs/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果您已经知道本次会话要激活哪些技能，可以在启动时传入：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```
Hermes 会在首次交互前将每个已命名的技能加载到会话提示词中。该标志在交互模式和单次查询模式下均有效。

## 技能斜杠命令

`~/.hermes/skills/` 目录下安装的每个技能都会自动注册为斜杠命令。技能名称即成为命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅输入技能名称会加载它，并让 Agent 询问你的需求：
/excalidraw
```

## 人格

设置预定义的人格以改变 Agent 的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置人格包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher`、`hype`。

你也可以在 `~/.hermes/config.yaml` 中定义自定义人格：

```yaml
personalities:
  helpful: "You are a helpful, friendly AI assistant."
  kawaii: "You are a kawaii assistant! Use cute expressions..."
  pirate: "Arrr! Ye be talkin' to Captain Hermes..."
  # 添加你自己的！
```

## 多行输入

有两种方式输入多行消息：

1. **`Alt+Enter` 或 `Ctrl+J`** — 插入新行
2. **反斜杠续行** — 在行尾使用 `\` 以继续：

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info
支持粘贴多行文本 — 使用 `Alt+Enter` 或 `Ctrl+J` 插入换行，或直接粘贴内容。
:::

## 中断 Agent

你可以在任何时候中断 Agent：

- 当 Agent 工作时**输入新消息并按 Enter** — 它会中断并处理你的新指令
- **`Ctrl+C`** — 中断当前操作（在 2 秒内按两次以强制退出）
- 正在进行的终端命令会立即被终止（SIGTERM，1 秒后发送 SIGKILL）
- 中断期间输入的多个消息会被合并为一个提示词

### 忙碌输入模式

`display.busy_input_mode` 配置键控制当你在 Agent 工作时按下 Enter 时发生的情况：

| 模式 | 行为 |
|------|----------|
| `"interrupt"` (默认) | 你的消息会中断当前操作并立即被处理 |
| `"queue"` | 你的消息会被静默排队，并在 Agent 完成后作为下一轮交互发送 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "queue"   # 或 "interrupt" (默认)
```

队列模式在你想要准备后续消息而不想意外取消正在进行的工作时很有用。未知值会回退到 `"interrupt"`。

### 挂起到后台

在 Unix 系统上，按 **`Ctrl+Z`** 将 Hermes 挂起到后台 — 就像任何终端进程一样。Shell 会打印确认信息：

```
Hermes Agent has been suspended. Run `fg` to bring Hermes Agent back.
```

在你的 shell 中输入 `fg` 以恢复会话，回到你离开时的状态。Windows 不支持此功能。

## 工具进度显示

CLI 会在 Agent 工作时显示动画反馈：

**思考动画**（在 API 调用期间）：
```
  ◜ (｡•́︿•̀｡) pondering... (1.2s)
  ◠ (⊙_⊙) contemplating... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ got it! (3.1s)
```

**工具执行反馈：**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 循环切换显示模式：`off → new → all → verbose`。此命令也可以为消息平台启用 — 参见[配置](/docs/user-guide/configuration#display-settings)。

### 工具预览长度

`display.tool_preview_length` 配置键控制在工具调用预览行（例如文件路径、终端命令）中显示的最大字符数。默认值为 `0`，表示无限制 — 显示完整路径和命令。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # 将工具预览截断为 80 个字符 (0 = 无限制)
```

这在窄终端上或当工具参数包含非常长的文件路径时很有用。

## 会话管理

### 恢复会话

当你退出 CLI 会话时，会打印一个恢复命令：

```
Resume this session with:
  hermes --resume 20260225_143052_a1b2c3

Session:        20260225_143052_a1b2c3
Duration:       12m 34s
Messages:       28 (5 user, 18 tool calls)
```

恢复选项：

```bash
hermes --continue                          # 恢复最近的 CLI 会话
hermes -c                                  # 简写形式
hermes -c "my project"                     # 恢复一个命名会话（谱系中最新的）
hermes --resume 20260225_143052_a1b2c3     # 按 ID 恢复特定会话
hermes --resume "refactoring auth"         # 按标题恢复
hermes -r 20260225_143052_a1b2c3           # 简写形式
```

恢复会从 SQLite 中还原完整的对话历史。Agent 会看到所有先前的消息、工具调用和响应 — 就像你从未离开过一样。

在聊天中使用 `/title My Session Name` 来命名当前会话，或从命令行使用 `hermes sessions rename <id> <title>`。使用 `hermes sessions list` 浏览过去的会话。

### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库 `~/.hermes/state.db` 中。该数据库保存：

- 会话元数据（ID、标题、时间戳、Token 计数器）
- 消息历史
- 跨压缩/恢复会话的谱系
- 由 `session_search` 使用的全文搜索索引

一些消息适配器也会在数据库旁边保留每个平台的转录文件，但 CLI 本身是从 SQLite 会话存储中恢复的。

### 上下文压缩

长对话在接近上下文限制时会自动进行总结：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在达到上下文限制的 50% 时压缩

# 在 auxiliary 下配置总结模型：
auxiliary:
  compression:
    model: "google/gemini-3-flash-preview"  # 用于总结的模型
```

当压缩触发时，中间的交互轮次会被总结，而前 3 轮和后 4 轮交互总是会被保留。
## 后台会话

在单独的后台会话中运行提示词，同时继续使用 CLI 进行其他工作：

```
/background Analyze the logs in /var/log and summarize any errors from today
```

Hermes 会立即确认任务并返回提示词：

```
🔄 Background task #1 started: "Analyze the logs in /var/log and summarize..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示词都会在守护线程中生成一个**完全独立的 Agent 会话**：

- **隔离的对话** — 后台 Agent 不知道你当前会话的历史记录。它只接收你提供的提示词。
- **相同的配置** — 后台 Agent 继承你当前会话的模型、提供商、工具集、推理设置和备用模型。
- **非阻塞** — 你的前台会话保持完全交互性。你可以聊天、运行命令，甚至启动更多后台任务。
- **多任务** — 你可以同时运行多个后台任务。每个任务都会获得一个编号 ID。

### 结果

当后台任务完成时，结果会以面板形式显示在你的终端中：

```
╭─ ⚕ Hermes (background #1) ──────────────────────────────────╮
│ Found 3 errors in syslog from today:                         │
│ 1. OOM killer invoked at 03:22 — killed process nginx        │
│ 2. Disk I/O error on /dev/sda1 at 07:15                      │
│ 3. Failed SSH login attempts from 192.168.1.50 at 14:30      │
╰──────────────────────────────────────────────────────────────╯
```

如果任务失败，你将看到错误通知。如果你的配置中启用了 `display.bell_on_complete`，任务完成时终端会响铃。

### 使用场景

- **长时间运行的研究** — 在你编写代码时，执行 "/background research the latest developments in quantum error correction"
- **文件处理** — 在你继续对话时，执行 "/background analyze all Python files in this repo and list any security issues"
- **并行调查** — 启动多个后台任务，同时探索不同的角度

:::info
后台会话不会出现在你的主对话历史记录中。它们是独立的会话，拥有自己的任务 ID（例如 `bg_143022_a1b2c3`）。
:::

## 静默模式

默认情况下，CLI 在静默模式下运行，该模式：
- 抑制来自工具的详细日志记录
- 启用可爱风格的动画反馈
- 保持输出简洁且用户友好

如需调试输出：
```bash
hermes chat --verbose
```