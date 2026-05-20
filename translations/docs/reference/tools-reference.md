---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具的权威参考，按工具集分组"
---

# 内置工具参考

本文档记录了 Hermes 的内置工具，按工具集分组。可用性因平台、凭证和启用的工具集而异。

**快速统计（当前注册表）：** 约 70 个工具 — 10 个浏览器工具（核心）+ 2 个 CDP 门控浏览器工具，4 个文件工具，10 个 RL 工具，4 个 Home Assistant 工具，2 个终端工具，2 个网页工具，5 个飞书工具，7 个 Spotify 工具（由捆绑的 `spotify` 插件注册），5 个元宝工具，7 个看板工具（在看板调度器生成 Agent 时注册），2 个 Discord 工具，以及一些独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`video_generate`、`vision_analyze`、`video_analyze`、`mixture_of_agents`、`send_message`、`todo`、`computer_use`、`process`）。

:::tip MCP 工具
除了内置工具，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具带有前缀 `mcp_<server>_`（例如，`github` MCP 服务器的 `mcp_github_create_issue`）。配置请参见 [MCP 集成](/docs/user-guide/features/mcp)。
:::

## `browser` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `browser_back` | 在浏览器历史记录中导航回上一页。需要先调用 `browser_navigate`。 | — |
| `browser_click` | 点击快照中由其引用 ID 标识的元素（例如，'@e5'）。引用 ID 在快照输出的方括号中显示。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_console` | 从当前页面获取浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息和未捕获的 JS 异常。使用此工具检测静默的 JavaScript 错误、失败的 API 调用和应用程序警告。需要... | — |
| `browser_get_images` | 获取当前页面上所有图片的列表及其 URL 和 alt 文本。用于查找要用视觉工具分析的图片。需要先调用 `browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航到 URL。初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，建议使用 `web_search` 或 `web_extract`（更快、更便宜）。当您需要...时使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。用于提交表单（Enter）、导航（Tab）或键盘快捷键。需要先调用 `browser_navigate`。 | — |
| `browser_scroll` | 沿某个方向滚动页面。使用此工具显示当前视口下方或上方的更多内容。需要先调用 `browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍树的基于文本的快照。返回带有引用 ID（如 @e1, @e2）的交互式元素，供 `browser_click` 和 `browser_type` 使用。full=false（默认）：包含交互式元素的紧凑视图。full=true：完整... | — |
| `browser_type` | 将文本输入到由其引用 ID 标识的输入字段中。先清除字段，然后输入新文本。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_vision` | 截取当前页面的屏幕截图并用视觉 AI 进行分析。当您需要从视觉上理解页面内容时使用此工具 — 对于验证码、视觉验证挑战、复杂布局或当文本快照...时特别有用。 | — |

## `browser` 工具集（CDP 门控工具）

这两个工具属于 `browser` 工具集，但仅在会话开始时可通过 Chrome DevTools Protocol 端点访问时注册 — 通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 会话或 Camofox。

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `browser_cdp` | 发送原始 Chrome DevTools Protocol 命令。用于处理高级 `browser_*` 工具未涵盖的浏览器操作的逃生舱口。参见 https://chromedevtools.github.io/devtools-protocol/ | CDP 端点 |
| `browser_dialog` | 响应原生 JavaScript 对话框（alert / confirm / prompt / beforeunload）。先调用 `browser_snapshot` — 待处理的对话框会出现在其 `pending_dialogs` 字段中。然后调用 `browser_dialog(action='accept'\|'dismiss')`。 | CDP 端点 |

## `clarify` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `clarify` | 当您在继续之前需要澄清、反馈或决策时，向用户提问。支持两种模式：1. **多项选择** — 提供最多 4 个选项。用户选择一个或通过第 5 个“其他”选项输入自己的答案。2.… | — |

## `code_execution` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `execute_code` | 运行一个可以编程方式调用 Hermes 工具的 Python 脚本。当您需要 3 个以上的工具调用并在它们之间有处理逻辑时，需要在工具输出进入您的上下文之前过滤/减少大型工具输出时，需要条件分支（…）时使用此工具。 | — |

## `cronjob` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `cronjob` | 统一的定时任务管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持带有一个或多个附加技能的技能支持的任务，更新时 `skills=[]` 会清除附加的技能。Cron 运行发生在没有当前聊天上下文的新会话中。 | — |

## `delegation` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `delegate_task` | 生成一个或多个子 Agent 在隔离的上下文中处理任务。每个子 Agent 都有自己的对话、终端会话和工具集。仅返回最终摘要 — 中间工具结果永远不会进入您的上下文窗口。两种… | — |
## `feishu_doc` 工具集

限定于飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）。不在 `hermes-cli` 或常规飞书聊天适配器中公开。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `feishu_doc_read` | 给定文件类型和 Token，读取飞书/Lark 文档（Docx、Doc 或 Sheet）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive` 工具集

限定于飞书文档评论处理器。驱动对云盘文件的评论读写操作。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `feishu_drive_add_comment` | 在飞书/Lark 文档或文件上添加顶级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 列出飞书/Lark 文件上的全文档评论，按最新优先排序。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论线程（全文档或局部选择）的回复。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论线程上发布回复，可选择 `@` 提及。 | 飞书应用凭证 |

## `file` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `patch` | 在文件中进行针对性的查找和替换编辑。在终端中使用此工具代替 sed/awk。使用模糊匹配（9 种策略），因此微小的空白/缩进差异不会导致失败。返回统一差异。编辑后自动运行语法检查… | — |
| `read_file` | 读取带有行号和分页的文本文件。在终端中使用此工具代替 cat/head/tail。输出格式：'LINE_NUM\|CONTENT'。如果未找到文件，会建议相似的文件名。对于大文件，使用 offset 和 limit 参数。注意：无法读取图像… | — |
| `search_files` | 搜索文件内容或按名称查找文件。在终端中使用此工具代替 grep/rg/find/ls。基于 Ripgrep，比 shell 等效命令更快。内容搜索（target='content'）：在文件内进行正则表达式搜索。输出模式：完整匹配（带行… | — |
| `write_file` | 将内容写入文件，完全替换现有内容。在终端中使用此工具代替 echo/cat heredoc。自动创建父目录。会覆盖整个文件——进行针对性编辑时请使用 'patch'。 | — |

## `homeassistant` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `ha_call_service` | 调用 Home Assistant 服务来控制设备。使用 ha_list_services 来发现每个域可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可选择按域（light、switch、climate、sensor、binary_sensor、cover、fan 等）或区域名称（living room、kitchen、bedroom 等）过滤。 | — |
| `ha_list_services` | 列出可用的 Home Assistant 服务（操作）以控制设备。显示可以在每种设备类型上执行的操作以及它们接受的参数。使用此工具来发现如何控制通过 ha_list_entities 找到的设备。 | — |

## `computer_use` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `computer_use` | 通过 cua-driver 进行后台 macOS 桌面控制——截图（SOM / vision / AX）、点击/拖拽/滚动/输入/按键/等待、list_apps、focus_app。不会窃取用户的鼠标光标或键盘焦点。适用于任何支持工具使用的模型。仅限 macOS。 | `cua-driver` 在 `$PATH` 中（通过 `hermes tools` 安装）。 |

:::note
**Honcho 工具**（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_reasoning`、`honcho_conclude`）不再是内置工具。它们可通过 Honcho 记忆提供商插件在 `plugins/memory/honcho/` 获取。有关安装和使用，请参阅[记忆提供商](../user-guide/features/memory-providers.md)。
:::

## `image_gen` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `image_generate` | 使用 FAL.ai 从文本提示词生成高质量图像。底层模型由用户配置（默认：FLUX 2 Klein 9B，生成时间小于 1 秒），Agent 无法选择。返回单个图像 URL。使用…显示它。 | FAL_KEY |

## `kanban` 工具集

当 Agent 由看板调度器生成（设置了 `HERMES_KANBAN_TASK` 环境变量）或在明确启用了 `kanban` 工具集的配置文件中运行时注册。任务作用域的工作器使用生命周期工具来处理其分配的任务；编排器配置文件额外获得看板路由工具，如 `kanban_list` 和 `kanban_unblock`。完整工作流请参阅[看板多 Agent](/docs/user-guide/features/kanban)。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `kanban_show` | 显示分配给此工作器的活动看板任务（标题、描述、评论、依赖项）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_list` | 列出看板任务（带过滤器）。仅限编排器；对调度器生成的任务工作器隐藏。 | 启用了 `kanban` 工具集的配置文件 |
| `kanban_complete` | 使用结构化的交接负载（结果、工件、后续任务）将当前任务标记为完成。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_block` | 因向用户提问而阻塞当前任务——调度器暂停，呈现问题，并在人工回复后恢复。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_heartbeat` | 在长时间运行的操作期间发送进度心跳，以便调度器知道工作器仍然存活。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_comment` | 在不改变任务状态的情况下向任务线程添加评论——用于呈现中间发现。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_create` | 从当前任务扇出子任务。由编排器和生成后续任务的工作器使用。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_link` | 用父 → 子依赖边链接任务。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_unblock` | 将阻塞的任务返回到 `ready` 状态。仅限编排器；对调度器生成的任务工作器隐藏。 | 启用了 `kanban` 工具集的配置文件 |
## `memory` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `memory` | 将重要信息保存到持久化记忆中，这些信息在会话之间持续存在。你的记忆会在会话开始时出现在系统提示词中——这是你在不同对话之间记住用户和环境信息的方式。何时保存… | — |

## `messaging` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用目标。重要提示：当用户要求发送到特定频道或人员（不仅仅是平台名称）时，请先调用 `send_message(action='list')` 以查看可用目标… | — |

## `moa` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `mixture_of_agents` | 通过多个前沿 LLM 协作路由解决难题。进行 5 次 API 调用（4 个参考模型 + 1 个聚合器），并投入最大推理努力——请谨慎用于真正困难的问题。最适合：复杂数学、高级算法… | OPENROUTER_API_KEY |

## `session_search` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `session_search` | 搜索存储在本地会话数据库中的过往会话，或在单个会话内滚动浏览。基于 FTS5 的检索；返回数据库中的实际消息（无需 LLM 调用）。三种模式：发现（传递 `query`）、滚动（传递 `session_id` + `around_message_id`）、浏览（无参数）。 | — |

## `skills` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——针对重复任务类型的可重用方法。新技能保存到 `~/.hermes/skills/`；现有技能可以在其所在位置修改。操作：创建（完整的 SKILL.m…） | — |
| `skill_view` | 技能允许加载特定任务和工作流的信息，以及脚本和模板。加载技能的全部内容或访问其链接的文件（参考资料、模板、脚本）。首次调用返回 SKILL.md 内容加上… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 `skill_view(name)` 加载完整内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `process` | 管理通过 `terminal(background=true)` 启动的后台进程。操作：'list'（显示所有）、'poll'（检查状态 + 新输出）、'log'（带分页的完整输出）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发送…） | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在调用之间保持持久化。对于长时间运行的服务器，设置 `background=true`。设置 `notify_on_complete=true`（与 `background=true` 一起）可以在进程完成时自动收到通知——无需轮询。不要使用 cat/head/tail——使用 `read_file`。不要使用 grep/rg/find——使用 `search_files`。 | — |

## `todo` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。适用于包含 3 个以上步骤的复杂任务或用户提供多个任务时。不带参数调用以读取当前列表。写入：- 提供 'todos' 数组以创建/更新项目 - merge=… | — |

## `vision` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `vision_analyze` | 使用 AI 视觉分析图像。对于支持视觉的主模型，将原始图像像素作为多模态工具结果返回，以便模型在其下一轮中本地查看。对于纯文本主模型，回退到辅助视觉模型，该模型描述图像并将描述作为文本返回。两种情况下工具签名相同。 | — |

## `video` 工具集

可选工具集（未加载到默认的 `hermes-cli` 集合中）。通过 `--toolsets video` 添加或在 `toolsets:` 配置中包含 `video`。

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `video_analyze` | 分析来自 URL 或文件路径的视频内容——字幕、场景分解、关键时间戳和视觉描述。 | — |

## `video_gen` 工具集

可选工具集（未加载到默认的 `hermes-cli` 集合中）。通过 `--toolsets video_gen` 添加或在 `hermes tools` → 视频生成中启用，该向导还会引导你选择后端。

后端以插件形式提供，位于 `plugins/video_gen/<name>/` 下：

- **xAI Grok-Imagine** — 文生视频和图生视频（SuperGrok OAuth 或 `XAI_API_KEY`）。
- **FAL.ai** — Veo 3.1, Pixverse v6, Kling O3（需要 `FAL_KEY`）。

单一的 `video_generate` 工具涵盖两种模式——传递 `image_url` 来为静态图像制作动画，省略它则仅从文本生成。活动后端会自动路由到正确的端点。该工具的描述在会话开始时重建，以反映活动后端的实际能力（模式、宽高比、分辨率、时长范围、最大参考图像数、音频支持）。有关后端开发，请参阅[视频生成提供商插件](/docs/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `video_generate` | 使用用户配置的视频生成后端，从文本提示词（文生视频）生成视频或为静态图像制作动画（图生视频）。传递 `image_url` 来为该图像制作动画；省略它则仅从文本生成。后端会自动路由到正确的端点。在 `video` 字段中返回 HTTP URL 或绝对文件路径。 | 活动的 `video_gen` 插件 + 其凭据（例如 `XAI_API_KEY`, `FAL_KEY`） |

## `web` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `web_search` | 在网络上搜索信息。默认返回最多 5 个结果，包含标题、URL 和描述。接受可选的 `limit` 参数（1-100，默认 5）。查询会传递到配置的后端，因此当后端支持时，诸如 `site:domain`、`filetype:pdf`、`intitle:word`、`-term` 和 `"exact phrase"` 等运算符可能有效。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 提取内容。以 Markdown 格式返回页面内容。也适用于 PDF URL——直接传递 PDF 链接，它会转换为 Markdown 文本。小于 5000 字符的页面返回完整 Markdown；更大的页面由 LLM 进行摘要。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
## `x_search` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `x_search` | 使用 xAI 内置的 `x_search` 响应工具搜索 X（Twitter）帖子、个人资料和主题。用于查找 X 上当前的讨论、反应或主张，而非一般网页。默认关闭——需通过 `hermes tools` → 🐦 X (Twitter) 搜索选择启用。仅在配置了 xAI 凭据时注册模式（由 check_fn 控制）。 | XAI_API_KEY **或** xAI Grok OAuth（SuperGrok 订阅）登录 |

## `tts` 工具集

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 MEDIA: 路径，平台会将其作为语音消息传递。在 Telegram 上以语音气泡播放，在 Discord/WhatsApp 上作为音频附件。在 CLI 模式下，保存到 ~/voice-memos/。语音和提供商… | — |

## `discord` 工具集

在 `hermes-discord` 平台工具集上注册（仅限消息网关）。使用与消息适配器相同的机器人令牌。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `discord` | 读取并参与 Discord 服务器。操作包括 `search_members`、`fetch_messages`、`send_message`、`react`、`fetch_channel`、`list_channels` 等。 | `DISCORD_BOT_TOKEN` |

## `discord_admin` 工具集

在 `hermes-discord` 平台工具集上注册。管理操作要求机器人拥有相应的 Discord 权限。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：列出公会/频道/角色，创建/编辑/删除频道，管理角色授予、超时、踢出和封禁。 | `DISCORD_BOT_TOKEN` + 机器人权限 |

## `spotify` 工具集

由捆绑的 `spotify` 插件注册。需要 OAuth 令牌——运行一次 `hermes spotify setup` 进行授权。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `spotify_playback` | 控制 Spotify 播放，检查活动播放状态，或获取最近播放的曲目。 | Spotify OAuth |
| `spotify_devices` | 列出 Spotify Connect 设备或将播放转移到其他设备。 | Spotify OAuth |
| `spotify_queue` | 检查用户的 Spotify 队列或向其中添加项目。 | Spotify OAuth |
| `spotify_search` | 在 Spotify 目录中搜索曲目、专辑、艺术家、播放列表、节目或剧集。 | Spotify OAuth |
| `spotify_playlists` | 列出、检查、创建、更新和修改 Spotify 播放列表。 | Spotify OAuth |
| `spotify_albums` | 获取 Spotify 专辑元数据或专辑曲目。 | Spotify OAuth |
| `spotify_library` | 列出、保存或移除用户保存的 Spotify 曲目或专辑。 | Spotify OAuth |

## `hermes-yuanbao` 工具集

仅在 `hermes-yuanbao` 平台工具集上注册。Yuanbao 是腾讯的聊天应用；这些工具驱动其私信/群组/表情 API。

| 工具 | 描述 | 所需执行环境 |
|------|-------------|----------------------|
| `yb_query_group_info` | 查询群组（应用中称为“派/Pai”）的基本信息：名称、所有者、成员数量。 | Yuanbao 凭据 |
| `yb_query_group_members` | 查询群组成员（用于 `@` 提及、按名称查找用户、列出机器人）。 | Yuanbao 凭据 |
| `yb_send_dm` | 向群组中的用户发送私信/直接消息，可选择附带媒体文件。 | Yuanbao 凭据 |
| `yb_search_sticker` | 通过关键字搜索内置的 Yuanbao 表情（TIM 表情）目录。 | Yuanbao 凭据 |
| `yb_send_sticker` | 向当前的 Yuanbao 聊天发送内置表情。 | Yuanbao 凭据 |