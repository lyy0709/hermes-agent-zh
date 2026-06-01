---
sidebar_position: 12
sidebar_label: "内置插件"
title: "内置插件"
description: "Hermes Agent 随附的插件，通过生命周期钩子自动运行——磁盘清理等"
---

# 内置插件

Hermes 随仓库捆绑提供了一小部分插件。它们位于 `<repo>/plugins/<name>/` 目录下，并与 `~/.hermes/plugins/` 中的用户安装插件一同自动加载。它们使用与第三方插件相同的插件接口——钩子、工具、斜杠命令——只是在仓库内维护。

关于通用插件系统，请参阅[插件](/user-guide/features/plugins)页面；要编写自己的插件，请参阅[构建 Hermes 插件](/guides/build-a-hermes-plugin)。

## 发现机制如何工作

`PluginManager` 按顺序扫描四个来源：

1.  **捆绑插件** — `<repo>/plugins/<name>/`（本文档所述内容）
2.  **用户插件** — `~/.hermes/plugins/<name>/`
3.  **项目插件** — `./.hermes/plugins/<name>/`（需要设置 `HERMES_ENABLE_PROJECT_PLUGINS=1`）
4.  **Pip 入口点** — `hermes_agent.plugins`

发生名称冲突时，后扫描的来源会覆盖先前的——名为 `disk-cleanup` 的用户插件将替换捆绑的插件。

`plugins/memory/` 和 `plugins/context_engine/` 被特意排除在捆绑插件扫描之外。这些目录使用它们自己的发现路径，因为记忆提供商和上下文引擎是通过 `hermes memory setup` / 配置中的 `context.engine` 配置的单选提供商。

## 捆绑插件需手动启用

捆绑插件在默认情况下是禁用的。发现机制能找到它们（它们会出现在 `hermes plugins list` 和交互式 `hermes plugins` UI 中），但在你显式启用之前，它们都不会加载：

```bash
hermes plugins enable disk-cleanup
```

或者通过 `~/.hermes/config.yaml`：

```yaml
plugins:
  enabled:
    - disk-cleanup
```

这与用户安装插件使用的机制相同。捆绑插件永远不会自动启用——无论是全新安装，还是现有用户升级到更新的 Hermes。你总是需要显式选择启用。

要再次关闭捆绑插件：

```bash
hermes plugins disable disk-cleanup
# 或者：从 config.yaml 的 plugins.enabled 中移除它
```

## 当前随附的插件

仓库在 `plugins/` 目录下捆绑了这些插件。所有插件都需要手动启用——通过 `hermes plugins enable <name>` 启用。

| 插件 | 类型 | 用途 |
|---|---|---|
| `disk-cleanup` | 钩子 + 斜杠命令 | 自动跟踪临时文件并在会话结束时清理它们 |
| `security-guidance` | 钩子 | 在 `write_file`/`patch` 操作时模式匹配危险代码并附加安全警告（或阻止）——包含 25 条规则（基于 Anthropic 的 `claude-plugins-official` 模式的 Apache-2.0 分支） |
| `observability/langfuse` | 钩子 | 将轮次 / LLM 调用 / 工具追踪到 [Langfuse](https://langfuse.com) |
| `spotify` | 后端（7 个工具） | 原生 Spotify 播放、队列、搜索、播放列表、专辑、资料库 |
| `google_meet` | 独立插件 | 加入 Meet 通话、实时字幕转录、可选实时双向音频 |
| `image_gen/openai` | 图像后端 | OpenAI `gpt-image-2` 图像生成后端（FAL 的替代方案） |
| `image_gen/openai-codex` | 图像后端 | 通过 Codex OAuth 进行 OpenAI 图像生成 |
| `image_gen/xai` | 图像后端 | xAI `grok-2-image` 后端 |
| `hermes-achievements` | 仪表板标签页 | 根据你的真实 Hermes 会话历史生成的 Steam 风格可收集徽章 |
| `kanban/dashboard` | 仪表板标签页 | 用于多 Agent 调度器的看板 UI——任务、评论、扇出、看板切换。请参阅[看板多 Agent](./kanban.md)。 |

记忆提供商 (`plugins/memory/*`) 和上下文引擎 (`plugins/context_engine/*`) 在[记忆提供商](./memory-providers.md)中单独列出——它们分别通过 `hermes memory` 和 `hermes plugins` 管理。以下是两个基于长期运行钩子的插件的完整详细信息。

### disk-cleanup

自动跟踪并删除会话期间创建的临时文件——测试脚本、临时输出、定时任务日志、过时的 Chrome 配置文件——无需 Agent 记住调用工具。

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 在 `HERMES_HOME` 或 `/tmp/hermes-*` 内创建匹配 `test_*`、`tmp_*` 或 `*.test.*` 的文件时，将其静默跟踪为 `test` / `temp` / `cron-output`。 |
| `on_session_end` | 如果在轮次期间自动跟踪了任何测试文件，则运行安全的 `quick` 清理并记录一行摘要。否则保持静默。 |

**删除规则：**

| 类别 | 阈值 | 确认 |
|---|---|---|
| `test` | 每次会话结束时 | 从不 |
| `temp` | 自跟踪起 >7 天 | 从不 |
| `cron-output` | 自跟踪起 >14 天 | 从不 |
| HERMES_HOME 下的空目录 | 总是 | 从不 |
| `research` | >30 天，超过最新的 10 个 | 总是（仅 deep 模式） |
| `chrome-profile` | 自跟踪起 >14 天 | 总是（仅 deep 模式） |
| 文件 >500 MB | 从不自动 | 总是（仅 deep 模式） |

**斜杠命令** — `/disk-cleanup` 在 CLI 和消息网关会话中均可用：

```
/disk-cleanup status                     # 分类统计 + 前 10 个最大文件
/disk-cleanup dry-run                    # 预览而不删除
/disk-cleanup quick                      # 立即运行安全清理
/disk-cleanup deep                       # quick + 列出需要确认的项目
/disk-cleanup track <路径> <类别>        # 手动跟踪
/disk-cleanup forget <路径>              # 停止跟踪（不删除）
```

**状态** — 所有内容都位于 `$HERMES_HOME/disk-cleanup/`：

| 文件 | 内容 |
|---|---|
| `tracked.json` | 跟踪的路径，包含类别、大小和时间戳 |
| `tracked.json.bak` | 上述文件的原子写入备份 |
| `cleanup.log` | 每次跟踪 / 跳过 / 拒绝 / 删除的仅追加审计日志 |

**安全性** — 清理操作仅触及 `HERMES_HOME` 或 `/tmp/hermes-*` 下的路径。Windows 挂载点 (`/mnt/c/...`) 会被拒绝。众所周知的高级状态目录（`logs/`、`memories/`、`sessions/`、`cron/`、`cache/`、`skills/`、`plugins/`、`disk-cleanup/` 自身）即使为空也永远不会被移除——全新安装不会在第一次会话结束时被清空。
**启用：** `hermes plugins enable disk-cleanup`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable disk-cleanup`。

### security-guidance

对文件写入进行快速模式匹配的安全警告。当 Agent 的 `write_file` / `patch` / `skill_manage` 调用包含的内容匹配已知的危险代码模式时——`pickle.load`、未使用 `SafeLoader` 的 `yaml.load`、`eval(`、`os.system`、`subprocess(..., shell=True)`、JS `child_process.exec`、React `dangerouslySetInnerHTML`、原始的 `.innerHTML =` / `.outerHTML =` / `document.write`、Node `crypto.createCipher`、AES ECB 模式、禁用的 TLS 验证、易受 XXE 攻击的 `xml.etree` / `minidom` 解析器、没有 SRI 的 `<script src="//..." >`、没有 `weights_only=True` 的 `torch.load`、GitHub Actions `${{ github.event.* }}` 注入——该插件会在工具结果后附加一个 `⚠️ 安全指导` 区块。

文件仍会被写入。模型会在下一轮的工具消息中读取警告，并可以修复代码或说明在此上下文中该结构为何是安全的。模式匹配存在一定的误报率，因此默认行为是警告（而非阻止）。

**覆盖范围：** 总共 25 条规则，涵盖不安全的反序列化、命令注入、XSS 接收器、加密陷阱、XXE、供应链（SRI）和 CI/CD 工作流注入。模式数据是 [Anthropic 的 `claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks) 的逐字 Apache-2.0 分支——有关归属信息，请参阅插件的 `LICENSE` 和 `NOTICE` 文件。

**模式：**

| 环境变量 | 效果 |
|---|---|
| （未设置） | **警告模式**（默认）——文件被写入，警告附加到结果 |
| `SECURITY_GUIDANCE_BLOCK=1` | **阻止模式**——写入被拒绝，警告作为阻止原因返回 |
| `SECURITY_GUIDANCE_DISABLE=1` | 紧急停止开关——插件加载但不执行任何操作 |

**启用：** `hermes plugins enable security-guidance`（或在 `hermes plugins` 中勾选复选框）。

**再次禁用：** `hermes plugins disable security-guidance`。

**它目前不做什么：** 上游的 Anthropic 插件还有另外两层——对每个涉及文件的 Agent 轮次进行 LLM 差异审查，以及一个在提交时进行的、跨文件追踪数据流的代理式审查。这两者都尚未移植。Agent 已经可以通过 `delegate_task` 按需运行这些审查。

### observability/langfuse

将 Hermes 轮次、LLM 调用和工具调用追踪到 [Langfuse](https://langfuse.com)——一个开源的 LLM 可观测性平台。每个轮次一个跨度，每次 API 调用一个生成，每个工具调用一个工具观察。使用总量、按类型的 Token 计数和成本估算来自 Hermes 规范的 `agent.usage_pricing` 数字，因此 Langfuse 仪表板看到的细分（输入 / 输出 / `cache_read_input_tokens` / `cache_creation_input_tokens` / `reasoning_tokens`）与 `hermes logs` 中显示的相同。

该插件采用故障开放策略：未安装 SDK、没有凭据或发生瞬时的 Langfuse 错误——所有这些在钩子中都会变成静默的无操作。Agent 循环永远不会受到影响。

**设置（交互式——推荐）：**

```bash
hermes tools          # → Langfuse Observability → Cloud or Self-Hosted
```

向导会收集你的密钥，`pip install` 安装 `langfuse` SDK，并为你将 `observability/langfuse` 添加到 `plugins.enabled`。重启 Hermes，下一个轮次就会发送追踪。

**设置（手动）：**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

然后将凭据放入 `~/.hermes/.env`：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # 或你的自托管 URL
```

**工作原理：**

| 钩子 | 行为 |
|---|---|
| `pre_api_request` / `pre_llm_call` | 打开（或重用）一个每轮次的根跨度 "Hermes turn"。为此 API 调用启动一个 `generation` 子观察，并将序列化的最近消息作为输入。 |
| `post_api_request` / `post_llm_call` | 关闭生成，附加 `usage_details`、`cost_details`、`finish_reason`、助手输出 + 工具调用。如果没有工具调用且内容非空，则关闭轮次。 |
| `pre_tool_call` | 使用清理过的 `args` 启动一个 `tool` 子观察。 |
| `post_tool_call` | 使用清理过的 `result` 关闭工具观察。`read_file` 的有效载荷会被总结（头部 + 尾部 + 省略的行数），以便巨大的文件读取保持在 `HERMES_LANGFUSE_MAX_CHARS` 限制内。 |

会话分组通过 `langfuse.propagate_attributes` 使用 Hermes 会话 ID（或子 Agent 的任务 ID）作为键，因此单个 `hermes chat` 会话中的所有内容都位于一个 Langfuse 会话下。

**验证：**

```bash
hermes plugins list                 # observability/langfuse 应显示 "enabled"
hermes chat -q "hello"              # 在 Langfuse UI 中检查 "Hermes turn" 追踪
```

**可选调优**（在 `.env` 中）：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | 追踪上的环境标签（`production`、`staging`、…） |
| `HERMES_LANGFUSE_RELEASE` | — | 发布/版本标签 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | 传递给 SDK 的采样率（0.0–1.0） |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | 消息内容 / 工具参数 / 工具结果的每字段截断长度 |
| `HERMES_LANGFUSE_DEBUG` | `false` | 详细的插件日志记录到 `agent.log` |

Hermes 前缀和标准 SDK 环境变量（`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY`、`LANGFUSE_BASE_URL`）都被接受——当两者都设置时，Hermes 前缀的变量优先。

**性能：** Langfuse 客户端在第一次钩子调用后被缓存。如果凭据或 SDK 缺失，该决定也会被缓存——后续的钩子会快速返回，而无需重新检查环境变量或重新加载配置。

**禁用：** `hermes plugins disable observability/langfuse`。插件模块仍会被发现，但在你重新启用之前，不会运行任何模块代码。

### google_meet

让 Agent 能够**加入、转录并参与 Google Meet 通话**——在会议中做笔记，会后总结讨论内容，跟进具体要点，并且（可选地）通过 TTS 将回复语音播报到通话中。
**新增功能：**

- 一个无头虚拟参与者，通过浏览器自动化加入 Meet URL
- 通过配置的 STT 提供商对会议音频进行实时转录
- Agent 调用 `meet_summarize` / `meet_speak` / `meet_followup` 工具集来对其听到的内容采取行动
- 会后产物（转录稿、带发言者归属的笔记、行动项）保存在 `~/.hermes/cache/google_meet/<meeting_id>/` 下

**设置：**

```bash
hermes plugins enable google_meet
# 首次使用时，会提示你通过插件的 OAuth 流程登录 ——
# 需要一个具有 Meet 访问权限的 Google 账户。如果会议强制执行“仅受邀参与者可以加入”，
# 则可能需要主持人批准。
```

在聊天中使用：

> "加入 meet.google.com/abc-defg-hij 并做笔记。通话结束后，给我发送一份包含行动项的摘要。"

Agent 会启动会议加入，在通话进行过程中将转录流式传输回其上下文，并在会议结束时（或当你告诉它停止时）生成一份结构化摘要。

**使用场景：** 定期的站会，你希望有一个机器人来为异步参与者转录和总结；需要结构化笔记的取证式访谈；任何原本需要使用 Fireflies / Otter / Grain 的场景。当你不想让 AI 监听时 —— 不要启用它。

**禁用：** `hermes plugins disable google_meet`。任何缓存的转录稿和录音将保留在 `~/.hermes/cache/google_meet/` 中，直到你手动删除。

### hermes-achievements

在仪表板中添加一个 **Steam 风格的成就标签页** —— 根据你真实的 Hermes 会话历史生成的 60 多个可收集、分级的徽章。工具链成就、调试模式、氛围编码连胜、技能/记忆使用情况、模型/提供商多样性、生活习性（周末和夜间会话）。最初由 [@PCinkusz](https://github.com/PCinkusz) 作为外部插件开发；现已纳入主仓库，以便与 Hermes 功能变更保持同步。

**工作原理：**

- 在仪表板后端扫描你整个 `~/.hermes/state.db` 会话历史
- 每个会话的统计数据通过 `(started_at, last_active)` 指纹进行缓存，因此只有新的或更改过的会话会在后续扫描中重新分析
- 首次扫描在后台线程中运行 —— 仪表板永远不会因此阻塞等待，即使数据库中有数千个会话
- 解锁状态持久化到 `$HERMES_HOME/plugins/hermes-achievements/state.json`

**等级进阶：** 铜 → 银 → 金 → 钻石 → 奥林匹亚。每张卡片都包含一个“统计内容”部分，列出正在追踪的确切指标。

**成就状态：**

| 状态 | 含义 |
|---|---|
| 已解锁 | 至少达到一个等级 |
| 已发现 | 已知成就，进度可见，但尚未获得 |
| 秘密 | 隐藏状态，直到 Hermes 在你的历史记录中检测到第一个相关信号 |

**API** —— 路由挂载在 `/api/plugins/hermes-achievements/` 下：

| 端点 | 用途 |
|---|---|
| `GET /achievements` | 包含每个徽章解锁状态的完整目录（首次冷扫描运行时返回一个待处理的占位符） |
| `GET /scan-status` | 后台扫描器的状态：`idle` / `running` / `failed`，上次运行时长，运行次数 |
| `GET /recent-unlocks` | 最近解锁的二十个徽章，最新的在前 |
| `GET /sessions/{id}/badges` | 主要在特定会话中获得的徽章 |
| `POST /rescan` | 手动同步重新扫描（阻塞；当用户点击重新扫描按钮时使用） |
| `POST /reset-state` | 清除解锁历史和缓存快照 |

**状态文件** —— 位于 `$HERMES_HOME/plugins/hermes-achievements/` 下：

| 文件 | 内容 |
|---|---|
| `state.json` | 解锁历史：你获得了哪些徽章以及何时获得。在 Hermes 更新中保持稳定。 |
| `scan_snapshot.json` | 上次完成的扫描负载（仪表板加载时立即提供） |
| `scan_checkpoint.json` | 按指纹索引的每个会话统计缓存（使热重新扫描快速） |

**性能说明：**

- 对约 8,000 个会话进行冷扫描需要几分钟。它在首次仪表板请求时在后台线程中运行；UI 会看到一个待处理的占位符并轮询 `/scan-status`。
- **冷扫描期间的增量结果** —— 扫描器每处理约 250 个会话发布一次部分快照，因此每次仪表板刷新都会随着扫描的进行显示更多已解锁的徽章。无需长时间盯着零进度。
- 热重新扫描会重用每个会话的统计数据，只要其 `started_at` + `last_active` 指纹与检查点匹配 —— 即使在大历史记录上也能在几秒钟内完成。
- 内存中快照的 TTL 为 120 秒；过时的请求会立即提供旧快照并触发后台刷新。你绝不会仅仅因为 TTL 过期而等待加载动画。

**启用：** 无需启用 —— `hermes-achievements` 是一个仅限仪表板的插件（无生命周期钩子，无模型可见工具）。它在首次启动时自动注册为 `hermes dashboard` 中的一个标签页。`plugins.enabled` 配置仅控制生命周期/工具插件；仪表板插件纯粹通过其 `dashboard/manifest.json` 被发现。

**选择退出：** 删除或重命名 `plugins/hermes-achievements/dashboard/manifest.json`，或者在 `~/.hermes/plugins/hermes-achievements/` 中使用一个不包含仪表板的同名用户插件来覆盖它。插件在 `$HERMES_HOME/plugins/hermes-achievements/` 下的状态文件会保留 —— 重新安装会保留你的解锁历史。

## 添加捆绑插件

捆绑插件的编写方式与任何其他 Hermes 插件完全相同 —— 参见 [构建 Hermes 插件](/guides/build-a-hermes-plugin)。唯一的区别是：

- 目录位于 `<repo>/plugins/<name>/` 而不是 `~/.hermes/plugins/<name>/`
- 在 `hermes plugins list` 中，清单来源报告为 `bundled`
- 同名的用户插件会覆盖捆绑版本

一个插件适合捆绑的条件是：

- 没有可选依赖项（或者它们已经是 `pip install .[all]` 依赖项）
- 其行为对大多数用户有益，并且是选择退出而非选择加入
- 其逻辑与生命周期钩子绑定，否则 Agent 必须记住调用这些钩子
- 它补充了核心功能，而没有扩展模型可见的工具表面
反例——应保持为用户可安装的插件，而非捆绑打包：需要 API 密钥的第三方集成、小众工作流、依赖树庞大的组件、任何会显著改变 Agent 默认行为的内容。