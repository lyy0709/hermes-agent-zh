---
title: "Hermes Agent — 配置、扩展或为 Hermes Agent 做贡献"
sidebar_label: "Hermes Agent"
description: "配置、扩展或为 Hermes Agent 做贡献"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hermes Agent

配置、扩展或为 Hermes Agent 做贡献。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/hermes-agent` |
| 版本 | `2.1.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `hermes`, `setup`, `configuration`, `multi-agent`, `spawning`, `cli`, `gateway`, `development` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Hermes Agent

Hermes Agent 是 Nous Research 开发的一个开源 AI Agent 框架，可在你的终端、消息平台和 IDE 中运行。它属于与 Claude Code (Anthropic)、Codex (OpenAI) 和 OpenClaw 相同的类别——这些是使用工具调用来与你的系统交互的自主编码和任务执行 Agent。Hermes 可与任何 LLM 提供商（OpenRouter、Anthropic、OpenAI、DeepSeek、本地模型等 15 家以上）配合使用，并运行在 Linux、macOS 和 WSL 上。

Hermes 的不同之处：

- **通过技能自我改进** — Hermes 通过将可重用过程保存为技能来从经验中学习。当它解决复杂问题、发现工作流或被纠正时，可以将该知识持久化为技能文档，加载到未来的会话中。技能会随时间积累，使 Agent 更擅长处理你的特定任务和环境。
- **跨会话的持久记忆** — 记住你是谁、你的偏好、环境细节和学到的经验教训。可插拔的记忆后端（内置、Honcho、Mem0 等）让你可以选择记忆的工作方式。
- **多平台消息网关** — 同一个 Agent 可在 Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Email 等 10 多个平台上运行，并拥有完整的工具访问权限，而不仅仅是聊天。
- **提供商无关** — 在工作流中随时切换模型和提供商，无需更改其他任何内容。凭证池会自动在多个 API 密钥之间轮换。
- **配置文件** — 运行多个独立的 Hermes 实例，拥有隔离的配置、会话、技能和记忆。
- **可扩展** — 插件、MCP 服务器、自定义工具、Webhook 触发器、定时任务调度以及完整的 Python 生态系统。

人们使用 Hermes 进行软件开发、研究、系统管理、数据分析、内容创作、家庭自动化，以及任何其他受益于具有持久上下文和完整系统访问权限的 AI Agent 的任务。

**此技能帮助你有效地使用 Hermes Agent** — 设置它、配置功能、生成额外的 Agent 实例、排查问题、找到正确的命令和设置，以及在需要扩展或为其做贡献时理解系统的工作原理。

**文档：** https://hermes-agent.nousresearch.com/docs/

## 快速开始

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 交互式聊天（默认）
hermes

# 单次查询
hermes chat -q "What is the capital of France?"

# 设置向导
hermes setup

# 更改模型/提供商
hermes model

# 检查健康状况
hermes doctor
```

---

## CLI 参考

### 全局标志

```
hermes [flags] [command]

  --version, -V             显示版本
  --resume, -r SESSION      通过 ID 或标题恢复会话
  --continue, -c [NAME]     按名称恢复，或恢复最近的会话
  --worktree, -w            隔离的 git 工作树模式（并行 Agent）
  --skills, -s SKILL        预加载技能（逗号分隔或重复）
  --profile, -p NAME        使用命名的配置文件
  --yolo                    跳过危险命令确认
  --pass-session-id         在系统提示词中包含会话 ID
```

无子命令时默认为 `chat`。

### 聊天

```
hermes chat [flags]
  -q, --query TEXT          单次查询，非交互式
  -m, --model MODEL         模型（例如 anthropic/claude-sonnet-4）
  -t, --toolsets LIST       逗号分隔的工具集列表
  --provider PROVIDER       强制指定提供商（openrouter, anthropic, nous 等）
  -v, --verbose             详细输出
  -Q, --quiet               抑制横幅、旋转器、工具预览
  --checkpoints             启用文件系统检查点（/rollback）
  --source TAG              会话来源标签（默认：cli）
```

### 配置

```
hermes setup [section]      交互式向导（model|terminal|gateway|tools|agent）
hermes model                交互式模型/提供商选择器
hermes config               查看当前配置
hermes config edit          在 $EDITOR 中打开 config.yaml
hermes config set KEY VAL   设置配置值
hermes config path          打印 config.yaml 路径
hermes config env-path      打印 .env 路径
hermes config check         检查缺失/过时的配置
hermes config migrate       使用新选项更新配置
hermes login [--provider P] OAuth 登录（nous, openai-codex）
hermes logout               清除存储的认证信息
hermes doctor [--fix]       检查依赖项和配置
hermes status [--all]       显示组件状态
```

### 工具与技能

```
hermes tools                交互式工具启用/禁用（curses UI）
hermes tools list           显示所有工具及其状态
hermes tools enable NAME    启用一个工具集
hermes tools disable NAME   禁用一个工具集

hermes skills list          列出已安装的技能
hermes skills search QUERY  在技能中心搜索
hermes skills install ID    安装一个技能（ID 可以是中心标识符或直接的 https://…/SKILL.md URL；当 frontmatter 中没有名称时，传递 --name 来覆盖）
hermes skills inspect ID    预览而不安装
hermes skills config        按平台启用/禁用技能
hermes skills check         检查更新
hermes skills update        更新过时的技能
hermes skills uninstall N   移除一个中心技能
hermes skills publish PATH  发布到注册表
hermes skills browse        浏览所有可用技能
hermes skills tap add REPO  添加一个 GitHub 仓库作为技能源
```
### MCP 服务器

```
hermes mcp serve            以 MCP 服务器模式运行 Hermes
hermes mcp add NAME         添加一个 MCP 服务器（使用 --url 或 --command）
hermes mcp remove NAME      移除一个 MCP 服务器
hermes mcp list             列出已配置的服务器
hermes mcp test NAME        测试连接
hermes mcp configure NAME   切换工具选择
```

### 消息网关（消息平台）

```
hermes gateway run          在前台启动消息网关
hermes gateway install      安装为后台服务
hermes gateway start/stop   控制服务
hermes gateway restart      重启服务
hermes gateway status       检查状态
hermes gateway setup        配置平台
```

支持平台：Telegram、Discord、Slack、WhatsApp、Signal、Email、SMS、Matrix、Mattermost、Home Assistant、钉钉、飞书、企业微信、BlueBubbles（iMessage）、微信、API 服务器、Webhooks。Open WebUI 通过 API 服务器适配器连接。

平台文档：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### 会话

```
hermes sessions list        列出最近的会话
hermes sessions browse      交互式选择器
hermes sessions export OUT  导出为 JSONL
hermes sessions rename ID T 重命名会话
hermes sessions delete ID   删除会话
hermes sessions prune       清理旧会话（--older-than N 天）
hermes sessions stats       会话存储统计信息
```

### 定时任务

```
hermes cron list            列出任务（--all 包含已禁用的）
hermes cron create SCHED    创建：'30m'、'every 2h'、'0 9 * * *'
hermes cron edit ID         编辑计划、提示词、交付方式
hermes cron pause/resume ID 控制任务状态
hermes cron run ID          在下一个周期触发
hermes cron remove ID       删除任务
hermes cron status          调度器状态
```

### Webhooks

```
hermes webhook subscribe N  在 /webhooks/<name> 创建路由
hermes webhook list         列出订阅
hermes webhook remove NAME  移除订阅
hermes webhook test NAME    发送测试 POST 请求
```

### 配置文件

```
hermes profile list         列出所有配置文件
hermes profile create NAME  创建（--clone、--clone-all、--clone-from）
hermes profile use NAME     设置粘性默认值
hermes profile delete NAME  删除配置文件
hermes profile show NAME    显示详细信息
hermes profile alias NAME   管理包装脚本
hermes profile rename A B   重命名配置文件
hermes profile export NAME  导出为 tar.gz
hermes profile import FILE  从存档导入
```

### 凭证池

```
hermes auth add             交互式凭证向导
hermes auth list [PROVIDER] 列出池化凭证
hermes auth remove P INDEX  按提供商 + 索引移除
hermes auth reset PROVIDER  清除耗尽状态
```

### 其他

```
hermes insights [--days N]  使用情况分析
hermes update               更新到最新版本
hermes pairing list/approve/revoke  私信授权管理
hermes plugins list/install/remove  插件管理
hermes honcho setup/status  Honcho 记忆集成（需要 honcho 插件）
hermes memory setup/status/off  记忆提供商配置
hermes completion bash|zsh  Shell 自动补全
hermes acp                  ACP 服务器（IDE 集成）
hermes claw migrate         从 OpenClaw 迁移
hermes uninstall            卸载 Hermes
```

---

## 斜杠命令（会话内）

在交互式聊天会话中输入这些命令。新命令会经常添加；如果下面的内容看起来过时了，请在会话内运行 `/help` 获取权威列表，或查看[实时斜杠命令参考](https://hermes-agent.nousresearch.com/docs/reference/slash-commands)。权威注册表是 `hermes_cli/commands.py` — 所有消费者（自动补全、Telegram 菜单、Slack 映射、`/help`）都从中派生。

### 会话控制
```
/new (/reset)        新会话
/clear               清屏 + 新会话（CLI）
/retry               重新发送最后一条消息
/undo                移除最后一次交互
/title [name]        为会话命名
/compress            手动压缩上下文
/stop                终止后台进程
/rollback [N]        恢复文件系统检查点
/snapshot [sub]      创建或恢复 Hermes 配置/状态的状态快照（CLI）
/background <prompt> 在后台运行提示词
/queue <prompt>      排队等待下一轮
/steer <prompt>      在下一次工具调用后注入一条消息而不中断
/agents (/tasks)     显示活跃的 Agent 和正在运行的任务
/resume [name]       恢复一个已命名的会话
/goal [text|sub]     设定一个 Hermes 在多个回合中持续努力直到达成的长期目标
                     （子命令：status、pause、resume、clear）
/redraw              强制完全重绘 UI（CLI）
```

### 配置
```
/config              显示配置（CLI）
/model [name]        显示或更改模型
/personality [name]  设置人格
/reasoning [level]   设置推理级别（none|minimal|low|medium|high|xhigh|show|hide）
/verbose             循环切换：off → new → all → verbose
/voice [on|off|tts]  语音模式
/yolo                切换绕过批准
/busy [sub]          控制 Hermes 工作时 Enter 键的功能（CLI）
                     （子命令：queue、steer、interrupt、status）
/indicator [style]   选择 TUI 忙碌指示器样式（CLI）
                     （样式：kaomoji、emoji、unicode、ascii）
/footer [on|off]     切换在最终回复中显示网关运行时元数据页脚
/skin [name]         更改主题（CLI）
/statusbar           切换状态栏（CLI）
```

### 工具与技能
```
/tools               管理工具（CLI）
/toolsets            列出工具集（CLI）
/skills              搜索/安装技能（CLI）
/skill <name>        将技能加载到会话中
/reload-skills       重新扫描 ~/.hermes/skills/ 以查找新增/移除的技能
/reload              将 .env 变量重新加载到正在运行的会话中（CLI）
/reload-mcp          重新加载 MCP 服务器
/cron                管理定时任务（CLI）
/curator [sub]       后台技能维护（status、run、pin、archive、…）
/kanban [sub]        多配置文件协作看板（tasks、links、comments）
/plugins             列出插件（CLI）
```
### 消息网关
```
/approve             批准待处理的命令（消息网关）
/deny                拒绝待处理的命令（消息网关）
/restart             重启消息网关（消息网关）
/sethome             将当前聊天设置为首页频道（消息网关）
/update              将 Hermes 更新至最新版本（消息网关）
/topic [sub]         启用或检查 Telegram 私信主题会话（消息网关）
/platforms (/gateway) 显示平台连接状态（消息网关）
```

### 实用工具
```
/branch (/fork)      分支当前会话
/fast                切换优先级/快速处理模式
/browser             打开 CDP 浏览器连接
/history             显示对话历史记录（CLI）
/save                将对话保存到文件（CLI）
/copy [N]            将最后一条助手回复复制到剪贴板（CLI）
/paste               附加剪贴板中的图片（CLI）
/image               附加本地图片文件（CLI）
```

### 信息
```
/help                显示命令
/commands [page]     浏览所有命令（消息网关）
/usage               Token 使用量
/insights [days]     使用情况分析
/gquota              显示 Google Gemini Code Assist 配额使用情况（CLI）
/status              会话信息（消息网关）
/profile             活动配置文件信息
/debug               上传调试报告（系统信息 + 日志）并获取可分享链接
```

### 退出
```
/quit (/exit, /q)    退出 CLI
```

---

## 关键路径与配置

```
~/.hermes/config.yaml       主配置文件
~/.hermes/.env              API 密钥和密钥
$HERMES_HOME/skills/        已安装的技能
~/.hermes/sessions/         会话记录
~/.hermes/logs/             消息网关和错误日志
~/.hermes/auth.json         OAuth Token 和凭证池
~/.hermes/hermes-agent/     源代码（如果是通过 git 安装）
```

配置文件使用 `~/.hermes/profiles/<name>/` 目录，布局相同。

### 配置部分

使用 `hermes config edit` 或 `hermes config set section.key value` 进行编辑。

| 部分 | 关键选项 |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

完整配置参考：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### 提供商

支持 20+ 提供商。通过 `hermes model` 或 `hermes setup` 设置。

| 提供商 | 认证方式 | 密钥环境变量 |
|----------|------|-------------|
| OpenRouter | API 密钥 | `OPENROUTER_API_KEY` |
| Anthropic | API 密钥 | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API 密钥 | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` |
| DeepSeek | API 密钥 | `DEEPSEEK_API_KEY` |
| xAI / Grok | API 密钥 | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API 密钥 | `GLM_API_KEY` |
| MiniMax | API 密钥 | `MINIMAX_API_KEY` |
| MiniMax CN | API 密钥 | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API 密钥 | `KIMI_API_KEY` |
| Alibaba / DashScope | API 密钥 | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API 密钥 | `XIAOMI_API_KEY` |
| Kilo Code | API 密钥 | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API 密钥 | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API 密钥 | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API 密钥 | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| 自定义端点 | 配置 | `model.base_url` + `model.api_key` 在 config.yaml 中 |
| GitHub Copilot ACP | 外部 | `COPILOT_CLI_PATH` 或 Copilot CLI |

完整提供商文档：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 工具集

通过 `hermes tools`（交互式）或 `hermes tools enable/disable NAME` 启用/禁用。

| 工具集 | 提供的功能 |
|---------|-----------------|
| `web` | 网络搜索和内容提取 |
| `search` | 仅网络搜索（`web` 的子集） |
| `browser` | 浏览器自动化（Browserbase、Camofox 或本地 Chromium） |
| `terminal` | Shell 命令和进程管理 |
| `file` | 文件读/写/搜索/补丁 |
| `code_execution` | 沙盒化 Python 执行 |
| `vision` | 图像分析 |
| `image_gen` | AI 图像生成 |
| `video` | 视频分析和生成 |
| `tts` | 文本转语音 |
| `skills` | 技能浏览和管理 |
| `memory` | 跨会话持久化记忆 |
| `session_search` | 搜索过去的对话 |
| `delegation` | 子 Agent 任务委派 |
| `cronjob` | 定时任务管理 |
| `clarify` | 向用户询问澄清性问题 |
| `messaging` | 跨平台消息发送 |
| `todo` | 会话内任务规划和跟踪 |
| `kanban` | 多 Agent 工作队列工具（仅限工作节点） |
| `debugging` | 额外的内省/调试工具（默认关闭） |
| `safe` | 用于锁定会话的最小化、低风险工具集 |
| `spotify` | Spotify 播放和播放列表控制 |
| `homeassistant` | 智能家居控制（默认关闭） |
| `discord` | Discord 集成工具 |
| `discord_admin` | Discord 管理/审核工具 |
| `feishu_doc` | 飞书（Lark）文档工具 |
| `feishu_drive` | 飞书（Lark）云盘工具 |
| `yuanbao` | 元宝集成工具 |
| `rl` | 强化学习工具（默认关闭） |
| `moa` | 混合 Agent（默认关闭） |

完整枚举位于 `toolsets.py` 中的 `TOOLSETS` 字典；`_HERMES_CORE_TOOLS` 是大多数平台继承的默认捆绑包。

工具更改在 `/reset`（新会话）后生效。它们不会在对话中途应用，以保留提示词缓存。
---

## 安全与隐私开关

常见的“为什么 Hermes 对我的输出/工具调用/命令执行了 X 操作？”开关及其对应的精确修改命令。大多数开关需要重启会话（在聊天中使用 `/reset`，或启动新的 `hermes` 进程），因为它们只在启动时读取一次。

### 工具输出中的密钥脱敏

密钥脱敏**默认关闭**——工具输出（终端 stdout、`read_file`、网页内容、子 Agent 摘要等）会原样传递。如果用户希望 Hermes 在字符串进入对话上下文和日志之前，自动屏蔽那些看起来像 API 密钥、Token 和密钥的字符串：

```bash
hermes config set security.redact_secrets true       # 全局启用
```

**需要重启。** `security.redact_secrets` 在导入时被快照——在会话中途切换（例如，通过工具调用中的 `export HERMES_REDACT_SECRETS=true`）**不会**对正在运行的进程生效。请告知用户在终端中运行 `hermes config set security.redact_secrets true`，然后启动一个新会话。这是有意为之——防止 LLM 在任务中途自行切换开关。

要再次禁用：
```bash
hermes config set security.redact_secrets false
```

### 消息网关消息中的 PII 脱敏

与密钥脱敏分开。启用后，消息网关会在用户 ID 和电话号码到达模型之前，对用户 ID 进行哈希处理并移除电话号码：

```bash
hermes config set privacy.redact_pii true    # 启用
hermes config set privacy.redact_pii false   # 禁用（默认）
```

### 命令执行确认提示

默认情况下（`approvals.mode: manual`），Hermes 在运行被标记为破坏性的 shell 命令（`rm -rf`、`git reset --hard` 等）之前会提示用户。模式如下：

- `manual` — 总是提示（默认）
- `smart` — 使用辅助 LLM 自动批准低风险命令，对高风险命令进行提示
- `off` — 跳过所有确认提示（等同于 `--yolo`）

```bash
hermes config set approvals.mode smart       # 推荐的折中方案
hermes config set approvals.mode off         # 绕过所有确认（不推荐）
```

在不更改配置的情况下，按次调用绕过：
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

注意：YOLO / `approvals.mode: off` **不会**关闭密钥脱敏。它们是独立的。

### Shell 钩子允许列表

某些 shell 钩子集成在触发前需要显式允许。通过 `~/.hermes/shell-hooks-allowlist.json` 管理——首次有钩子想要运行时，会进行交互式提示。

### 禁用网页/浏览器/图像生成工具

要完全阻止模型访问网络或媒体工具，请打开 `hermes tools` 并按平台切换开关。在下一次会话（`/reset`）时生效。请参阅上文的“工具与技能”部分。

---

## 语音与转录

### STT（语音转文本）

来自消息平台的语音消息会自动转录。

提供商优先级（自动检测）：
1. **本地 faster-whisper** — 免费，无需 API 密钥：`pip install faster-whisper`
2. **Groq Whisper** — 免费额度：设置 `GROQ_API_KEY`
3. **OpenAI Whisper** — 付费：设置 `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — 设置 `MISTRAL_API_KEY`

配置：
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS（文本转语音）

| 提供商 | 环境变量 | 免费？ |
|----------|---------|-------|
| Edge TTS | 无 | 是（默认） |
| ElevenLabs | `ELEVENLABS_API_KEY` | 免费额度 |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | 付费 |
| MiniMax | `MINIMAX_API_KEY` | 付费 |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | 付费 |
| NeuTTS (本地) | 无（`pip install neutts[all]` + `espeak-ng`） | 免费 |

语音命令：`/voice on`（语音到语音）、`/voice tts`（始终语音）、`/voice off`。

---

## 启动额外的 Hermes 实例

将额外的 Hermes 进程作为完全独立的子进程运行——拥有独立的会话、工具和执行环境。

### 何时使用此功能 vs delegate_task

| | `delegate_task` | 启动 `hermes` 进程 |
|-|-----------------|--------------------------|
| 隔离性 | 独立对话，共享进程 | 完全独立的进程 |
| 持续时间 | 分钟级（受父循环限制） | 小时/天级 |
| 工具访问 | 父进程工具的子集 | 完整的工具访问权限 |
| 交互性 | 否 | 是（PTY 模式） |
| 用例 | 快速并行子任务 | 长期自主任务 |

### 一次性模式

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# 长时间任务后台运行：
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### 交互式 PTY 模式（通过 tmux）

Hermes 使用 prompt_toolkit，这需要一个真实的终端。使用 tmux 进行交互式启动：

```
# 启动
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# 等待启动，然后发送消息
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# 读取输出
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# 发送后续消息
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# 退出
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### 多 Agent 协调

```
# Agent A: 后端
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: 前端
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# 检查进度，在它们之间传递上下文
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```
### 会话恢复

```
# 恢复最近的会话
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# 恢复特定会话
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### 提示

- **快速子任务优先使用 `delegate_task`** — 比生成完整进程开销更小
- **编辑代码时生成 Agent 使用 `-w`（工作树模式）** — 防止 git 冲突
- **为一次性模式设置超时** — 复杂任务可能需要 5-10 分钟
- **使用 `hermes chat -q` 实现即发即弃** — 无需 PTY
- **交互式会话使用 tmux** — 原始 PTY 模式与 prompt_toolkit 存在 `\r` 与 `\n` 问题
- **定时任务**使用 `cronjob` 工具而非生成进程 — 处理交付和重试

---

## 持久化与后台系统

四个系统在主对话循环旁运行。此处为快速参考；完整的开发者说明位于 `AGENTS.md`，面向用户的文档位于 `website/docs/user-guide/features/`。

### 委派 (`delegate_task`)

同步子 Agent 生成 — 父 Agent 等待子 Agent 的摘要后再继续其自身循环。隔离的上下文 + 终端会话。

- **单个：** `delegate_task(goal, context, toolsets)`。
- **批量：** `delegate_task(tasks=[{goal, ...}, ...])` 并行运行子任务，上限由 `delegation.max_concurrent_children` 控制（默认 3）。
- **角色：** `leaf`（默认；不能重新委派）与 `orchestrator`（可以生成自己的工作进程，受 `delegation.max_spawn_depth` 限制）。
- **非持久化。** 如果父进程被中断，子进程将被取消。对于必须持续到本轮之后的工作，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

配置：`config.yaml` 中的 `delegation.*`。

### Cron（定时任务）

持久化调度器 — `cron/jobs.py` + `cron/scheduler.py`。通过 `cronjob` 工具、`hermes cron` CLI（`list`、`add`、`edit`、`pause`、`resume`、`run`、`remove`）或 `/cron` 斜杠命令驱动。

- **调度：** 时长（`"30m"`、`"2h"`）、"every" 短语（`"every monday 9am"`）、5 字段 cron（`"0 9 * * *"`）或 ISO 时间戳。
- **每任务配置：** `skills`、`model`/`provider` 覆盖、`script`（运行前数据收集；`no_agent=True` 使脚本成为整个任务）、`context_from`（将任务 A 的输出链接到任务 B）、`workdir`（在特定目录中运行并加载其 `AGENTS.md` / `CLAUDE.md`）、多平台交付。
- **不变性：** 每次运行有 3 分钟硬中断限制、`.tick.lock` 文件防止跨进程重复执行、cron 会话默认传递 `skip_memory=True`，并且 cron 交付使用页眉/页脚包装，而不是镜像到目标消息网关会话中（保持角色交替完整）。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### 策展器（技能生命周期）

对 Agent 创建技能的背景维护。跟踪使用情况，标记闲置技能为陈旧，归档陈旧技能，保留运行前的 tar.gz 备份以防丢失。

- **CLI：** `hermes curator <verb>` — `status`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`prune`、`backup`、`rollback`。
- **斜杠命令：** `/curator <subcommand>` 镜像 CLI。
- **范围：** 仅处理来源为 `created_by: "agent"` 的技能。捆绑 + 中心安装的技能不受影响。**永不删除** — 最大破坏性操作是归档。已固定的技能免于所有自动转换和所有 LLM 审查流程。
- **遥测：** 位于 `~/.hermes/skills/.usage.json` 的辅助文件记录每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state`、`pinned`。

配置：`curator.*`（`enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*`）。
用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### 看板（多 Agent 工作队列）

用于多配置文件 / 多工作进程协作的持久化 SQLite 看板。用户通过 `hermes kanban <verb>` 驱动；由调度器生成的工作进程会看到一个受 `HERMES_KANBAN_TASK` 限制的聚焦 `kanban_*` 工具集，而编排器配置文件可以选择加入更广泛的 `kanban` 工具集。除非配置，否则普通会话仍然具有零 `kanban_*` 模式占用。

- **CLI 动词（常用）：** `init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`。不常用：`watch`、`stats`、`runs`、`log`、`dispatch`、`daemon`、`gc`。
- **工作进程/编排器工具集：** `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`；在调度器生成的任务之外明确启用 `kanban` 工具集的配置文件还会获得用于看板路由的 `kanban_list` 和 `kanban_unblock`。
- **调度器** 默认在消息网关内运行（`kanban.dispatch_in_gateway: true`）— 回收陈旧的认领，提升就绪任务，原子化认领，生成分配到的配置文件。在配置的 `kanban.failure_limit` 次连续非成功尝试（默认：2）后自动阻塞任务。
- **隔离：** 看板是硬边界（工作进程在环境中固定 `HERMES_KANBAN_BOARD`）；租户是看板内的软命名空间，用于工作空间路径 + 记忆键隔离。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

## Windows 特定注意事项

Hermes 原生运行于 Windows（PowerShell、cmd、Windows Terminal、git-bash mintty、VS Code 集成终端）。大部分功能正常工作，但 Win32 和 POSIX 之间存在一些差异曾给我们带来困扰 — 当你遇到新的差异时，请在此记录，以便下一个人（或下一个会话）不必从头重新发现它们。

### 输入 / 键绑定

**Alt+Enter 不会插入换行符。** Windows Terminal 在终端层拦截 Alt+Enter 以切换全屏 — 该按键永远不会到达 prompt_toolkit。请改用 **Ctrl+Enter**。Windows Terminal 将 Ctrl+Enter 作为 LF（`c-j`）传递，与普通 Enter（`c-m` / CR）不同，并且 CLI 仅在 `win32` 上将 `c-j` 绑定到换行符插入（参见 `_bind_prompt_submit_keys` + `cli.py` 中仅限 Windows 的 `c-j` 绑定）。副作用：原始的 Ctrl+J 按键在 Windows 上也会插入换行符 — 这是不可避免的，因为 Windows Terminal 在 Win32 控制台 API 层将 Ctrl+Enter 和 Ctrl+J 折叠为相同的键码。在 Windows 上，Ctrl+J 没有冲突的绑定，所以这是一个无害的副作用。
mintty / git-bash 的行为相同（Alt+Enter 全屏），除非你在选项 → 键中禁用 Alt+Fn 快捷键。更简单的方法是直接使用 Ctrl+Enter。

**诊断键位绑定。** 运行 `python scripts/keystroke_diagnostic.py`（仓库根目录）以准确查看 prompt_toolkit 在当前终端中如何识别每个击键。可以解答诸如“Shift+Enter 是否作为独立按键传入？”（几乎从不——大多数终端将其折叠为普通 Enter）或“我的终端为 Ctrl+Enter 发送什么字节序列？”等问题。这就是确定 Ctrl+Enter = c-j 这一事实的方法。

### 配置 / 文件

**首次运行时出现 HTTP 400 "No models provided"。** `config.yaml` 保存时带有 UTF-8 BOM（Windows 应用程序写入时常见）。重新保存为不带 BOM 的 UTF-8 格式。`hermes config edit` 会写入不带 BOM 的文件；在记事本中进行手动编辑通常是罪魁祸首。

### `execute_code` / 沙盒

沙盒子进程出现 **WinError 10106**（“无法加载或初始化请求的服务提供程序”）——它无法创建 `AF_INET` 套接字，因此环回 TCP RPC 回退在 `connect()` 之前就失败了。根本原因通常**不是**损坏的 Winsock LSP；而是 Hermes 自身的环境清理器从子进程环境中删除了 `SYSTEMROOT` / `WINDIR` / `COMSPEC`。Python 的 `socket` 模块需要 `SYSTEMROOT` 来定位 `mswsock.dll`。已通过 `tools/code_execution_tool.py` 中的 `_WINDOWS_ESSENTIAL_ENV_VARS` 允许列表修复。如果仍然遇到此问题，请在 `execute_code` 块内回显 `os.environ` 以确认 `SYSTEMROOT` 已设置。完整的诊断方法见 `references/execute-code-sandbox-env-windows.md`。

### 测试 / 贡献

**`scripts/run_tests.sh` 在 Windows 上无法直接运行**——它查找的是 POSIX 虚拟环境布局（`.venv/bin/activate`）。安装在 `venv/Scripts/` 的 Hermes 虚拟环境中也没有 pip 或 pytest（为减小安装体积已剥离）。解决方法：将 `pytest + pytest-xdist + pyyaml` 安装到系统 Python 3.11 的用户站点，然后设置 `PYTHONPATH` 直接调用 pytest：

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

使用 `-n 0`，而不是 `-n 4`——`pyproject.toml` 的默认 `addopts` 已经包含了 `-n`，并且包装器的 CI 对等保证在非 POSIX 系统上不适用。

**仅限 POSIX 的测试需要跳过保护。** 代码库中已有的常见标记：
- 符号链接——在 Windows 上需要提升权限
- `0o600` 文件模式——NTFS 默认不强制执行 POSIX 模式位
- `signal.SIGALRM`——仅限 Unix（参见 `tests/conftest.py::_enforce_test_timeout`）
- Winsock / Windows 特定的回归问题——`@pytest.mark.skipif(sys.platform != "win32", ...)`

使用现有的跳过模式风格（`sys.platform == "win32"` 或 `sys.platform.startswith("win")`）以保持与测试套件其余部分的一致性。

### 路径 / 文件系统

**行尾。** Git 可能会警告 `LF 将在 Git 下次接触时被替换为 CRLF`。这只是表面问题——仓库的 `.gitattributes` 会进行规范化。不要让编辑器自动将已提交的 POSIX 换行文件转换为 CRLF。

**正斜杠几乎在所有地方都有效。** `C:/Users/...` 被所有 Hermes 工具和大多数 Windows API 接受。在代码和日志中优先使用正斜杠——避免在 bash 中转义反斜杠。

---

## 故障排除

### 语音功能不工作
1. 检查 config.yaml 中的 `stt.enabled: true`
2. 验证提供商：`pip install faster-whisper` 或设置 API 密钥
3. 在消息网关中：`/restart`。在 CLI 中：退出并重新启动。

### 工具不可用
1. `hermes tools` —— 检查工具集是否已为你的平台启用
2. 某些工具需要环境变量（检查 `.env`）
3. 启用工具后执行 `/reset`

### 模型/提供商问题
1. `hermes doctor` —— 检查配置和依赖项
2. `hermes login` —— 重新验证 OAuth 提供商
3. 检查 `.env` 中是否有正确的 API 密钥
4. **Copilot 403**：`gh auth login` 的 Token 对 Copilot API **无效**。你必须通过 `hermes model` → GitHub Copilot 使用 Copilot 特定的 OAuth 设备代码流程。

### 更改未生效
- **工具/技能：** `/reset` 会启动一个新的会话，并更新工具集
- **配置更改：** 在消息网关中：`/restart`。在 CLI 中：退出并重新启动。
- **代码更改：** 重启 CLI 或消息网关进程

### 技能未显示
1. `hermes skills list` —— 验证是否已安装
2. `hermes skills config` —— 检查平台启用状态
3. 显式加载：`/skill name` 或 `hermes -s name`

### 消息网关问题
首先检查日志：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见的消息网关问题：
- **SSH 注销时消息网关终止：** 启用 linger：`sudo loginctl enable-linger $USER`
- **WSL2 关闭时消息网关终止：** WSL2 需要在 `/etc/wsl.conf` 中设置 `systemd=true` 才能使 systemd 服务正常工作。如果没有设置，消息网关会回退到 `nohup`（会话关闭时终止）。
- **消息网关崩溃循环：** 重置失败状态：`systemctl --user reset-failed hermes-gateway`

### 平台特定问题
- **Discord 机器人静默：** 必须在 Bot → Privileged Gateway Intents 中启用 **Message Content Intent**。
- **Slack 机器人仅在私信中工作：** 必须订阅 `message.channels` 事件。没有它，机器人会忽略公共频道。
- **Windows 特定问题**（`Alt+Enter` 换行、WinError 10106、UTF-8 BOM 配置、测试套件、行尾）：请参阅上面的 **Windows 特定注意事项** 部分。

### 辅助模型不工作
如果 `auxiliary` 任务（视觉、压缩）静默失败，`auto` 提供商无法找到后端。要么设置 `OPENROUTER_API_KEY` 或 `GOOGLE_API_KEY`，要么显式配置每个辅助任务的提供商：
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## 查找位置

| 查找内容... | 位置 |
|----------------|----------|
| 配置选项 | `hermes config edit` 或 [配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| 可用工具 | `hermes tools list` 或 [工具参考](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| 斜杠命令 | 会话中的 `/help` 或 [斜杠命令参考](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| 技能目录 | `hermes skills browse` 或 [技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| 提供商设置 | `hermes model` 或 [提供商指南](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| 平台设置 | `hermes gateway setup` 或 [消息传递文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP 服务器 | `hermes mcp list` 或 [MCP 指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| 配置文件 | `hermes profile list` 或 [配置文件文档](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| 定时任务 | `hermes cron list` 或 [定时任务文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| 记忆 | `hermes memory status` 或 [记忆文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| 环境变量 | `hermes config env-path` 或 [环境变量参考](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI 命令 | `hermes --help` 或 [CLI 参考](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| 消息网关日志 | `~/.hermes/logs/gateway.log` |
| 会话文件 | `~/.hermes/sessions/` 或 `hermes sessions browse` |
| 源代码 | `~/.hermes/hermes-agent/` |
---

## 贡献者快速参考

面向临时贡献者和 PR 作者。完整开发者文档：https://hermes-agent.nousresearch.com/docs/developer-guide/

### 项目结构

<!-- ascii-guard-ignore -->
```
hermes-agent/
├── run_agent.py          # AIAgent — 核心对话循环
├── model_tools.py        # 工具发现与分发
├── toolsets.py           # 工具集定义
├── cli.py                # 交互式 CLI (HermesCLI)
├── hermes_state.py       # SQLite 会话存储
├── agent/                # 提示词构建器、上下文压缩、记忆、模型路由、凭证池、技能分发
├── hermes_cli/           # CLI 子命令、配置、设置、命令
│   ├── commands.py       # 斜杠命令注册表 (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, 环境变量定义
│   └── main.py           # CLI 入口点和 argparse
├── tools/                # 每个工具一个文件
│   └── registry.py       # 中央工具注册表
├── gateway/              # 消息网关
│   └── platforms/        # 平台适配器 (telegram, discord 等)
├── cron/                 # 任务调度器
├── tests/                # ~3000 个 pytest 测试
└── website/              # Docusaurus 文档站点
```
<!-- ascii-guard-ignore-end -->

配置：`~/.hermes/config.yaml` (设置)，`~/.hermes/.env` (API 密钥)。

### 添加工具 (3 个文件)

**1. 创建 `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 添加到 `toolsets.py`** → `_HERMES_CORE_TOOLS` 列表。

自动发现：任何包含顶级 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入 —— 无需手动维护列表。

所有处理程序必须返回 JSON 字符串。使用 `get_hermes_home()` 处理路径，切勿硬编码 `~/.hermes`。

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 中添加 `CommandDef`
2. 在 `cli.py` 的 `process_command()` 中添加处理程序
3. (可选) 在 `gateway/run.py` 中添加网关处理程序

所有消费者（帮助文本、自动补全、Telegram 菜单、Slack 映射）都会自动从中央注册表派生。

### Agent 循环 (高层概述)

```
run_conversation():
  1. 构建系统提示词
  2. 当迭代次数 < 最大值 时循环：
     a. 调用 LLM (OpenAI 格式的消息 + 工具模式)
     b. 如果 tool_calls → 通过 handle_function_call() 分发每个调用 → 追加结果 → 继续
     c. 如果是文本响应 → 返回
  3. 接近 Token 限制时自动触发上下文压缩
```

### 测试

```bash
python -m pytest tests/ -o 'addopts=' -q   # 完整测试套件
python -m pytest tests/tools/ -q            # 特定区域
```

- 测试会自动将 `HERMES_HOME` 重定向到临时目录 —— 绝不接触真实的 `~/.hermes/`
- 推送任何更改前运行完整测试套件
- 使用 `-o 'addopts='` 来清除任何内置的 pytest 标志

**Windows 贡献者：** `scripts/run_tests.sh` 目前查找的是 POSIX 虚拟环境 (`.venv/bin/activate` / `venv/bin/activate`)，在 Windows 上（其布局是 `venv/Scripts/activate` + `python.exe`）会报错。安装在 `venv/Scripts/` 的 Hermes 虚拟环境也没有 `pip` 或 `pytest` —— 为了最终用户安装包大小，它被精简了。解决方法：将 pytest + pytest-xdist + pyyaml 安装到系统 Python 3.11 的用户站点 (`/c/Program Files/Python311/python -m pip install --user pytest pytest-xdist pyyaml`)，然后直接运行测试：

```bash
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/tools/test_foo.py -v --tb=short -n 0
```

使用 `-n 0` (而不是 `-n 4`)，因为 `pyproject.toml` 的默认 `addopts` 已经包含了 `-n`，并且包装器的 CI 一致性方案不适用于非 POSIX 环境。

**跨平台测试防护：** 使用仅限 POSIX 的系统调用的测试需要一个跳过标记。代码库中已有的常见标记：
- 创建符号链接 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")` (参见 `tests/cron/test_cron_script.py`)
- POSIX 文件模式 (0o600 等) → `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")` (参见 `tests/hermes_cli/test_auth_toctou_file_modes.py`)
- `signal.SIGALRM` → 仅限 Unix (参见 `tests/conftest.py::_enforce_test_timeout`)
- 实时 Winsock / Windows 特定回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

**仅对 `sys.platform` 进行 Monkeypatch 是不够的**，当被测试的代码也调用 `platform.system()` / `platform.release()` / `platform.mac_ver()` 时。这些函数会独立地重新读取真实的操作系统，因此，在 Windows 运行器上设置 `sys.platform = "linux"` 的测试，仍然会看到 `platform.system() == "Windows"` 并进入 Windows 分支。需要同时修补这三者：

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

参见 `tests/agent/test_prompt_builder.py::TestEnvironmentHints` 中的工作示例。

### 扩展系统提示词中的执行环境信息块

关于主机操作系统、用户主目录、当前工作目录、终端后端以及 shell（Windows 上是 bash 与 PowerShell）的事实性指导信息，由 `agent/prompt_builder.py::build_environment_hints()` 生成。这也是 WSL 提示和每个后端探测逻辑所在的位置。约定如下：

- **本地终端后端** → 发出主机信息（操作系统、`$HOME`、当前工作目录）+ Windows 特定说明（主机名 ≠ 用户名，`terminal` 使用 bash 而非 PowerShell）。
- **远程终端后端** (`_REMOTE_TERMINAL_BACKENDS` 中的任何内容：`docker, singularity, modal, daytona, ssh, vercel_sandbox, managed_modal`) → **完全抑制**主机信息，仅描述后端。通过 `tools.environments.get_environment(...).execute(...)` 在后端内部运行实时的 `uname`/`whoami`/`pwd` 探测，每个进程缓存在 `_BACKEND_PROBE_CACHE` 中，如果探测超时则使用静态回退。
- **提示词编写的关键事实：** 当 `TERMINAL_ENV != "local"` 时，*每个*文件工具 (`read_file`, `write_file`, `patch`, `search_files`) 都在后端容器内运行，而不是在主机上。在这种情况下，系统提示词绝不能描述主机 —— Agent 无法触及它。
完整的设计说明、确切的输出字符串和测试注意事项：
`references/prompt-builder-environment-hints.md`。

**重构安全模式（POSIX 等效性防护）：** 当你将内联逻辑提取到添加了 Windows/平台特定行为的辅助函数中时，请在测试文件中保留一个 `_legacy_<name>` 的预言函数，它是旧代码的逐字副本，然后对其进行参数化差异比较。示例：`tests/tools/test_code_execution_windows_env.py::TestPosixEquivalence`。这锁定了 POSIX 行为逐位相同的约束，并使任何未来的偏差通过清晰的差异对比而明显失败。

### 提交规范

```
type: 简洁的主题行

可选的正文。
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

### 关键规则

- **绝不破坏提示词缓存** — 不要在会话中途更改上下文、工具或系统提示词
- **消息角色交替** — 绝不连续出现两条助手消息或两条用户消息
- 所有路径都使用 `hermes_constants` 中的 `get_hermes_home()`（配置文件安全）
- 配置值放在 `config.yaml` 中，密钥放在 `.env` 中
- 新工具需要一个 `check_fn`，以便仅在满足要求时出现