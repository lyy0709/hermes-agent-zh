---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具的权威参考，按工具集分组"
---

# 内置工具参考

本文档记录了 Hermes 工具注册表中的全部 55 个内置工具，按工具集分组。可用性因平台、凭证和启用的工具集而异。

**快速统计：** 12 个浏览器工具，4 个文件工具，10 个 RL 工具，4 个 Home Assistant 工具，2 个终端工具，2 个网页工具，5 个飞书工具，以及分布在其他工具集中的 15 个独立工具。

:::tip MCP 工具
除了内置工具，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具会带有服务器名前缀（例如，`github` MCP 服务器的 `github_create_issue`）。配置方法请参阅 [MCP 集成](/docs/user-guide/features/mcp)。
:::

## `browser` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `browser_back` | 在浏览器历史记录中导航回上一页。需要先调用 `browser_navigate`。 | — |
| `browser_cdp` | 发送原始 Chrome DevTools 协议 (CDP) 命令。用于处理 `browser_navigate`、`browser_click`、`browser_console` 等未涵盖的浏览器操作的逃生舱。仅在会话开始时可通过 CDP 端点访问时可用 —— 通过 `/browser connect` 或 `browser.cdp_url` 配置。参见 https://chromedevtools.github.io/devtools-protocol/ | — |
| `browser_dialog` | 响应原生 JavaScript 对话框（alert / confirm / prompt / beforeunload）。先调用 `browser_snapshot` —— 待处理的对话框会出现在其 `pending_dialogs` 字段中。然后调用 `browser_dialog(action='accept'|'dismiss')`。可用性与 `browser_cdp` 相同（Browserbase 或 `/browser connect`）。 | — |
| `browser_click` | 点击快照中由其引用 ID 标识的元素（例如，'@e5'）。引用 ID 在快照输出的方括号中显示。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_console` | 从当前页面获取浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息和未捕获的 JS 异常。使用此工具检测静默的 JavaScript 错误、失败的 API 调用和应用程序警告。需要… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表及其 URL 和 alt 文本。用于查找要用视觉工具分析的图片。需要先调用 `browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航到 URL。初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，优先使用 `web_search` 或 `web_extract`（更快、更便宜）。当您需要…时使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。用于提交表单（Enter）、导航（Tab）或键盘快捷键。需要先调用 `browser_navigate`。 | — |
| `browser_scroll` | 按方向滚动页面。使用此工具显示当前视口下方或上方的更多内容。需要先调用 `browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍树的基于文本的快照。返回带有引用 ID（如 @e1, @e2）的交互式元素，供 `browser_click` 和 `browser_type` 使用。full=false（默认）：包含交互式元素的紧凑视图。full=true：包含…的完整视图。 | — |
| `browser_type` | 将文本输入到由其引用 ID 标识的输入字段中。先清除字段，然后输入新文本。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_vision` | 截取当前页面的屏幕截图并用视觉 AI 进行分析。当您需要视觉理解页面内容时使用此工具 —— 对于验证码、视觉验证挑战、复杂布局或当文本快照…时特别有用。 | — |

## `clarify` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `clarify` | 当您在继续之前需要澄清、反馈或决策时，向用户提问。支持两种模式：1. **多项选择** —— 提供最多 4 个选项。用户选择一个或通过第 5 个“其他”选项输入自己的答案。2.… | — |

## `code_execution` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `execute_code` | 运行一个可以编程式调用 Hermes 工具的 Python 脚本。当您需要 3 个以上的工具调用并在它们之间有处理逻辑时，需要在工具输出进入您的上下文之前过滤/减少大型工具输出时，需要条件分支（…）时使用此工具。 | — |

## `cronjob` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `cronjob` | 统一的定时任务管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持带有一个或多个附加技能的技能支持任务，更新时 `skills=[]` 会清除附加的技能。Cron 运行发生在没有当前聊天上下文的新会话中。 | — |

## `delegation` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `delegate_task` | 生成一个或多个子 Agent 在隔离的上下文中处理任务。每个子 Agent 都有自己的对话、终端会话和工具集。只返回最终摘要 —— 中间工具结果永远不会进入您的上下文窗口。两种… | — |

## `feishu_doc` 工具集

作用域限定于飞书文档评论智能回复处理器 (`gateway/platforms/feishu_comment.py`)。不在 `hermes-cli` 或常规的飞书聊天适配器上公开。

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `feishu_doc_read` | 给定其 `file_type` 和 `token`，读取飞书/Lark 文档（Docx、Doc 或 Sheet）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive` 工具集

作用域限定于飞书文档评论处理器。驱动对网盘文件的评论读写操作。

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `feishu_drive_add_comment` | 在飞书/Lark 文档或文件上添加顶级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 列出飞书/Lark 文件上的整个文档评论，按最新优先排序。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论线程（整个文档或局部选择）上的回复。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论线程上发布回复，可选的 `@` 提及。 | 飞书应用凭证 |
## `file` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `patch` | 在文件中进行针对性的查找和替换编辑。在终端中请使用此工具代替 sed/awk。使用模糊匹配（9 种策略），因此微小的空格/缩进差异不会导致失败。返回统一的差异（unified diff）。编辑后自动运行语法检查… | — |
| `read_file` | 读取文本文件，附带行号和分页。在终端中请使用此工具代替 cat/head/tail。输出格式：'LINE_NUM\|CONTENT'。如果未找到文件，会建议相似的文件名。对于大文件，请使用 offset 和 limit 参数。注意：无法读取图像… | — |
| `search_files` | 搜索文件内容或按名称查找文件。在终端中请使用此工具代替 grep/rg/find/ls。基于 Ripgrep，比 shell 等效命令更快。内容搜索（target='content'）：在文件内进行正则表达式搜索。输出模式：完整匹配（包含行… | — |
| `write_file` | 将内容写入文件，完全替换现有内容。在终端中请使用此工具代替 echo/cat heredoc。自动创建父目录。会覆盖整个文件——如需进行针对性编辑，请使用 'patch'。 | — |

## `homeassistant` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `ha_call_service` | 调用 Home Assistant 服务以控制设备。使用 ha_list_services 来发现每个域（domain）可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可按域（light、switch、climate、sensor、binary_sensor、cover、fan 等）或区域名称（living room、kitchen、bedroom 等）进行筛选。 | — |
| `ha_list_services` | 列出可用的 Home Assistant 服务（操作）以控制设备。显示每种设备类型可以执行哪些操作以及它们接受哪些参数。使用此工具来发现如何控制通过 ha_list_entities 找到的设备。 | — |

:::note
**Honcho 工具** (`honcho_profile`, `honcho_search`, `honcho_context`, `honcho_reasoning`, `honcho_conclude`) 不再是内置工具。它们可通过 Honcho 记忆提供商插件在 `plugins/memory/honcho/` 处获得。有关安装和使用，请参阅[记忆提供商](../user-guide/features/memory-providers.md)。
:::

## `image_gen` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `image_generate` | 使用 FAL.ai 根据文本提示词生成高质量图像。底层模型由用户配置（默认：FLUX 2 Klein 9B，生成时间小于 1 秒），Agent 无法选择。返回单个图像 URL。使用…显示它 | FAL_KEY |

## `memory` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `memory` | 将重要信息保存到持久化记忆中，这些记忆在会话之间持续存在。你的记忆会在会话开始时出现在你的系统提示词中——这是你在对话之间记住用户和环境信息的方式。何时保存… | — |

## `messaging` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用目标。重要提示：当用户要求发送到特定频道或人员（不仅仅是平台名称）时，请先调用 send_message(action='list') 以查看可用目标… | — |

## `moa` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `mixture_of_agents` | 通过多个前沿 LLM 协作路由一个难题。进行 5 次 API 调用（4 个参考模型 + 1 个聚合器），并投入最大推理努力——请谨慎用于真正困难的问题。最适合：复杂数学、高级算法… | OPENROUTER_API_KEY |

## `rl` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `rl_check_status` | 获取训练运行的状态和指标。速率限制：对同一运行，两次检查之间强制间隔至少 30 分钟。返回 WandB 指标：step、state、reward_mean、loss、percent_correct。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_edit_config` | 更新配置字段。请先使用 rl_get_current_config() 查看所选环境的所有可用字段。每个环境都有不同的可配置选项。基础设施设置（tokenizer、URLs、lora_rank、learning_ra… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_current_config` | 获取当前环境配置。仅返回可修改的字段：group_size、max_token_length、total_steps、steps_per_eval、use_wandb、wandb_name、max_num_workers。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_results` | 获取已完成训练运行的最终结果和指标。返回最终指标和训练权重的路径。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_environments` | 列出所有可用的 RL 环境。返回环境名称、路径和描述。提示：使用文件工具读取 file_path 以了解每个环境的工作原理（验证器、数据加载、奖励）。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_runs` | 列出所有训练运行（活跃和已完成）及其状态。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_select_environment` | 选择用于训练的 RL 环境。加载环境的默认配置。选择后，使用 rl_get_current_config() 查看设置，并使用 rl_edit_config() 修改它们。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_start_training` | 使用当前环境和配置启动新的 RL 训练运行。大多数训练参数（lora_rank、learning_rate 等）是固定的。在启动前使用 rl_edit_config() 设置 group_size、batch_size、wandb_project。警告：训练… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_stop_training` | 停止正在运行的训练任务。如果指标看起来不佳、训练停滞或你想尝试不同的设置时使用。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_test_inference` | 针对任何环境的快速推理测试。使用 OpenRouter 运行几步推理 + 评分。默认：3 步 x 16 次完成 = 每个模型 48 次 rollout，测试 3 个模型 = 总共 144 次。测试环境加载、提示词构建、推理… | TINKER_API_KEY, WANDB_API_KEY |
## `session_search` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `session_search` | 搜索你过去对话的长期记忆。这是你的回忆功能——每个过去的会话都是可搜索的，此工具会总结发生了什么。在以下情况时主动使用此工具：- 用户说“我们之前做过这个”、“记得当时”、“上次…” | — |

## `skills` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——针对重复任务类型的可复用方法。新技能保存到 `~/.hermes/skills/`；现有技能可以在其所在位置修改。操作：create（完整的 SKILL.m… | — |
| `skill_view` | 技能允许加载特定任务和工作流的信息，以及脚本和模板。加载一个技能的全部内容或访问其链接的文件（参考资料、模板、脚本）。首次调用返回 SKILL.md 内容加上… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 `skill_view(name)` 加载完整内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `process` | 管理使用 `terminal(background=true)` 启动的后台进程。操作：'list'（显示所有）、'poll'（检查状态 + 新输出）、'log'（带分页的完整输出）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发… | — |
| `terminal` | 在 Linux 执行环境中执行 shell 命令。文件系统在调用之间保持持久化。对于长时间运行的服务器，设置 `background=true`。设置 `notify_on_complete=true`（与 `background=true` 一起）可以在进程完成时自动收到通知——无需轮询。不要使用 cat/head/tail——使用 `read_file`。不要使用 grep/rg/find——使用 `search_files`。 | — |

## `todo` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。用于包含 3 个以上步骤的复杂任务或当用户提供多个任务时。不带参数调用以读取当前列表。写入：- 提供 'todos' 数组来创建/更新项目 - merge=… | — |

## `vision` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `vision_analyze` | 使用 AI 视觉分析图像。提供全面的描述并回答关于图像内容的特定问题。 | — |

## `web` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `web_search` | 在网络上搜索任何主题的信息。返回最多 5 个相关结果，包含标题、URL 和描述。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 提取内容。以 Markdown 格式返回页面内容。也适用于 PDF URL——直接传递 PDF 链接，它会转换为 Markdown 文本。少于 5000 字符的页面返回完整 Markdown；更大的页面由 LLM 进行总结。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |

## `tts` 工具集

| 工具 | 描述 | 需要执行环境 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 MEDIA: 路径，平台会将其作为语音消息传递。在 Telegram 上，它会作为语音气泡播放；在 Discord/WhatsApp 上，则作为音频附件。在 CLI 模式下，保存到 `~/voice-memos/`。语音和提供商… | — |