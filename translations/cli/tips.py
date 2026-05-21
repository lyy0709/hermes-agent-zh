"""CLI 会话开始时显示的随机提示，帮助用户发现功能。"""

import random


# ---------------------------------------------------------------------------
# 提示语料库 — 涵盖斜杠命令、CLI 标志、配置、按键绑定、工具、消息网关、技能、配置文件和工作流技巧的单行提示。
# ---------------------------------------------------------------------------

TIPS = [
    # --- 斜杠命令 ---
    "/background <prompt>（别名 /bg 或 /btw）在单独的会话中运行任务，而你当前的会话保持空闲。",
    "/branch 分叉当前会话，以便你可以在不丢失进度的情况下探索不同的方向。",
    "/compress 在对话上下文变得过长时手动压缩。",
    "/rollback 列出文件系统检查点 — 将 Agent 修改的文件恢复到任何先前状态。",
    "/rollback diff 2 预览自检查点 2 以来的更改，而不恢复任何内容。",
    "/rollback 2 src/file.py 从特定检查点恢复单个文件。",
    "/title \"我的项目\" 为你的会话命名 — 稍后使用 /resume 或 hermes -c 恢复。",
    "/resume 从先前命名的会话中上次中断的地方继续。",
    "/queue <prompt> 为下一轮排队一条消息，而不中断当前轮次。",
    "/undo 从对话中移除最后一条用户/助手交换。",
    "/retry 重新发送你的最后一条消息 — 当 Agent 的响应不太正确时很有用。",
    "/verbose 循环切换工具进度显示：关闭 → 新工具 → 全部 → 详细。",
    "/reasoning high 增加模型的思考深度。/reasoning show 显示推理过程。",
    "/fast 切换优先级处理以获得更快的 API 响应（取决于提供商）。",
    "/yolo 跳过会话剩余时间内所有危险命令的批准提示。",
    "/model 允许你在会话中途切换模型 — 试试 /model sonnet 或 /model gpt-5。",
    "/model --global 永久更改你的默认模型。",
    "/personality pirate 设置一个有趣的个性 — 14 个内置选项，从 kawaii 到 shakespeare。",
    "/skin 更改 CLI 主题 — 试试 ares、mono、slate、poseidon 或 charizard。",
    "/statusbar 切换一个持久的状态栏，显示模型、Token、上下文填充百分比、成本和持续时间。",
    "/tools disable browser 临时移除当前会话的浏览器工具。",
    "/browser connect 通过 CDP 将浏览器工具附加到你正在运行的 Chromium 系列浏览器。",
    "/plugins 列出已安装的插件及其状态。",
    "/cron 管理定时任务 — 设置重复提示并交付到任何平台。",
    "/reload-mcp 热重载 MCP 服务器配置，无需重启。",
    "/usage 显示 Token 使用情况、成本细分和会话持续时间。",
    "/insights 显示过去 30 天的使用分析。",
    "/paste 检查你的剪贴板中是否有图像，并将其附加到你的下一条消息。",
    "/profile 显示哪个配置文件处于活动状态及其主目录。",
    "/config 一目了然地显示你当前的配置。",
    "/stop 终止由 Agent 生成的所有正在运行的后台进程。",

    # --- @ 上下文引用 ---
    "@file:path/to/file.py 将文件内容直接注入到你的消息中。",
    "@file:main.py:10-50 仅注入文件的第 10-50 行。",
    "@folder:src/ 注入目录树列表。",
    "@diff 将你未暂存的 git 更改注入到消息中。",
    "@staged 将你已暂存的 git 更改（git diff --staged）注入到消息中。",
    "@git:5 注入最后 5 次提交的完整补丁。",
    "@url:https://example.com 获取并注入网页内容。",
    "输入 @ 触发文件系统路径补全 — 交互式导航到任何文件。",
    "组合多个引用：\"Review @file:main.py and @file:test.py for consistency.\"",

    # --- 按键绑定 ---
    "Alt+Enter 插入换行符以进行多行输入。（Windows Terminal 会拦截 Alt+Enter — 请改用 Ctrl+Enter。）",
    "Ctrl+C 中断 Agent。在 2 秒内按两次以强制退出。",
    "Ctrl+Z 将 Hermes 挂起到后台 — 在 shell 中运行 fg 以恢复。",
    "Tab 接受自动建议的幽灵文本或自动补全斜杠命令。",
    "在 Agent 工作时输入新消息以中断并重定向它。",
    "Alt+V 从剪贴板粘贴图像到对话中。",
    "粘贴 5 行以上文本会自动保存到文件并插入紧凑的引用。",

    # --- CLI 标志 ---
    "hermes -c 恢复你最近的 CLI 会话。hermes -c \"项目名称\" 按标题恢复。",
    "hermes -w 创建一个隔离的 git 工作树 — 非常适合并行 Agent 工作流。",
    "hermes -w -q \"修复问题 #42\" 结合工作树隔离与一次性查询。",
    "hermes chat -t web,terminal 仅为特定工具集启用会话。",
    "hermes chat -s github-pr-workflow 在启动时预加载一个技能。",
    "hermes chat -q \"查询\" 运行单个非交互式查询并退出。",
    "hermes chat --max-turns 200 覆盖每轮默认的 90 次迭代限制。",
    "hermes chat --checkpoints 在每次破坏性文件更改之前启用文件系统快照。",
    "hermes --yolo 绕过整个会话中所有危险命令的批准提示。",
    "hermes chat --source telegram 标记会话以便在 hermes sessions list 中过滤。",
    "hermes -p work chat 在特定配置文件下运行，而不更改你的默认配置。",

    # --- CLI 子命令 ---
    "hermes doctor --fix 诊断并自动修复配置和依赖问题。",
    "hermes dump 输出紧凑的设置摘要 — 非常适合错误报告。",
    "hermes config set KEY VALUE 自动将密钥路由到 .env，其他所有内容路由到 config.yaml。",
    "hermes config edit 在你的默认编辑器中打开 config.yaml。",
    "hermes config check 扫描缺失或过时的配置选项。",
    "hermes sessions browse 打开一个带搜索功能的交互式会话选择器。",
    "hermes sessions stats 按平台和数据库大小显示会话计数。",
    "hermes sessions prune --older-than 30 清理旧会话。",
    "hermes skills search react --source skills-sh 搜索 skills.sh 公共目录。",
    "hermes skills check 扫描已安装的中心技能以获取上游更新。",
    "hermes skills tap add myorg/skills-repo 添加自定义 GitHub 技能源。",
    "hermes skills snapshot export setup.json 导出你的技能配置以进行备份或共享。",
    "hermes mcp add github --command npx 从命令行添加 MCP 服务器。",
    "hermes mcp serve 将 Hermes 本身作为 MCP 服务器运行，供其他 Agent 使用。",
    "hermes auth add 允许你添加多个 API 密钥以进行凭据池轮换。",
    "hermes completion bash >> ~/.bashrc 为所有命令和配置文件启用 Tab 补全。",
    "hermes logs -f 实时跟踪 agent.log。--level WARNING --since 1h 过滤输出。",
    "hermes backup 创建整个 Hermes 主目录的 zip 备份。",
    "hermes profile create coder 创建一个隔离的配置文件，该配置文件将成为其自己的命令。",
    "hermes profile create work --clone 将你当前的配置和密钥复制到新配置文件。",
    "hermes update 自动将新的捆绑技能同步到所有配置文件。",
    "hermes gateway install 将 Hermes 设置为系统服务（systemd/launchd）。",
    "hermes memory setup 允许你配置外部记忆提供商（Honcho、Mem0 等）。",
    "hermes webhook subscribe 创建具有 HMAC 验证的事件驱动 Webhook 路由。",
    "节省资金：hermes tools 禁用未使用的工具，hermes skills config 精简技能。",
    "/reasoning low 或 /reasoning minimal 将思考深度降低到默认值（中等）以下 — 更快、更便宜的响应。",
    "hermes models 将视觉、压缩和辅助任务路由到更便宜的模型 — 在不降低主聊天模型的情况下，将后台 Token 成本降低 85% 以上。",

    # --- 配置 ---
    "在 config.yaml 中设置 display.bell_on_complete: true，以便在长任务完成时听到铃声。",
    "设置 display.streaming: true 以实时查看模型生成时出现的 Token。",
    "设置 display.show_reasoning: true 以观察模型的链式推理过程。",
    "设置 display.compact: true 以减少输出中的空白，使信息更密集。",
    "设置 display.busy_input_mode: queue 将消息排队而不是中断 Agent，或设置为 steer 以通过 /steer 在运行中注入它们。",
    "设置 display.resume_display: minimal 以在恢复会话时跳过完整的对话回顾。",
    "设置 compression.threshold: 0.50 以控制自动压缩何时触发（默认：上下文的 50%）。",
    "设置 agent.max_turns: 200 以允许 Agent 每轮执行更多工具调用步骤。",
    "设置 file_read_max_chars: 200000 以增加每次 read_file 调用的最大内容量。",
    "设置 approvals.mode: smart 以让 LLM 自动批准安全命令并自动拒绝危险命令。",
    "在 config.yaml 中设置 fallback_model 以自动故障转移到备用提供商。",
    "设置 privacy.redact_pii: true 以在发送给 LLM 之前哈希用户 ID 和电话号码。",
    "设置 browser.record_sessions: true 以自动将浏览器会话录制为 WebM 视频。",
    "在 config.yaml 中设置 worktree: true 以始终创建 git 工作树（与 hermes -w 相同）。",
    "设置 security.website_blocklist.enabled: true 以阻止 Web 工具访问特定域名。",
    "设置 cron.wrap_response: false 以交付原始 Agent 输出，不带 cron 页眉/页脚。",
    "HERMES_TIMEZONE 使用任何 IANA 时区字符串覆盖服务器时区。",
    "环境变量替换在 config.yaml 中有效：使用 ${VAR_NAME} 语法。",
    "config.yaml 中的快速命令可立即运行 shell 命令，无需使用任何 Token。",
    "自定义个性可以在 config.yaml 中的 agent.personalities 下定义。",
    "provider_routing 控制 OpenRouter 提供商的排序、白名单和黑名单。",

    # --- 工具与能力 ---
    "execute_code 运行调用 Hermes 工具的 Python 脚本 — 结果保留在上下文之外。",
    "delegate_task 默认生成最多 3 个并发子 Agent（delegation.max_concurrent_children），具有隔离上下文以进行并行工作。",
    "web_extract 适用于 PDF URL — 传递任何 PDF 链接，它会转换为 markdown。",
    "search_files 基于 ripgrep，比 grep 更快 — 用它代替终端 grep。",
    "patch 使用 9 种模糊匹配策略，因此微小的空白差异不会破坏编辑。",
    "patch 支持 V4A 格式，用于在单个调用中进行批量多文件编辑。",
    "read_file 在找不到文件时建议类似的文件名。",
    "read_file 自动去重 — 重新读取未更改的文件会返回轻量级存根。",
    "browser_vision 截取屏幕截图并用 AI 进行分析 — 适用于验证码和视觉内容。",
    "browser_console 可以在页面上下文中评估 JavaScript 表达式。",
    "image_generate 使用 FLUX 2 Pro 和自动 2 倍放大创建图像。",
    "text_to_speech 将文本转换为音频 — 在 Telegram 上以语音气泡形式播放。",
    "send_message 可以从会话内到达任何已连接的消息传递平台。",
    "todo 工具帮助 Agent 在会话期间跟踪复杂的多步骤任务。",
    "session_search 对所有过去的对话执行全文搜索。",
    "Agent 自动将偏好、更正和环境事实保存到记忆中。",
    "mixture_of_agents 将难题通过 4 个前沿 LLM 协作路由。",
    "终端命令支持后台模式，并带有 notify_on_complete 以处理长时间运行的任务。",
    "终端后台进程支持 watch_patterns 以提醒特定的输出行。",
    "终端工具支持 6 个后端：本地、Docker、SSH、Modal、Daytona 和 Singularity。",

    # --- 配置文件 ---
    "每个配置文件都有自己的配置、API 密钥、记忆、会话、技能和定时任务。",
    "配置文件名称成为 shell 命令 — 'hermes profile create coder' 创建 'coder' 命令。",
    "hermes profile export coder -o backup.tar.gz 创建可移植的配置文件存档。",
    "如果两个配置文件意外共享一个机器人令牌，第二个消息网关会被阻止并显示清晰的错误信息。",

    # --- 会话 ---
    "会话在第一次交换后自动生成描述性标题 — 无需手动命名。",
    "会话标题支持谱系：\"我的项目\" → \"我的项目 #2\" → \"我的项目 #3\"。",
    "退出时，Hermes 会打印一个恢复命令，包含会话 ID 和统计信息。",
    "hermes sessions export backup.jsonl 导出所有会话以进行备份或分析。",
    "hermes -r SESSION_ID 通过其 ID 恢复任何特定的过去会话。",

    # --- 记忆 ---
    "记忆是冻结的快照 — 更改仅在下次会话开始时出现在系统提示词中。",
    "记忆条目会自动扫描提示词注入和泄露模式。",
    "Agent 有两个记忆存储：个人笔记（约 2200 字符）和用户档案（约 1375 字符）。",
    "你给 Agent 的更正（\"不，这样做\"）通常会自动保存到记忆中。",

    # --- 技能 ---
    "超过 80 个捆绑技能，涵盖 github、创意、mlops、生产力、研究等。",
    "每个已安装的技能都会自动成为斜杠命令 — 输入 / 查看所有命令。",
    "hermes skills install official/security/1password 从仓库安装可选技能。",
    "技能可以限制在特定的操作系统平台 — 有些仅在 macOS 或 Linux 上加载。",
    "config.yaml 中的 skills.external_dirs 允许你从自定义目录加载技能。",
    "Agent 可以使用 skill_manage 创建自己的技能作为程序性记忆。",
    "plan 技能将 markdown 计划保存在活动工作区的 .hermes/plans/ 下。",

    # --- 定时任务与调度 ---
    "定时任务可以附加技能：hermes cron add --skill blogwatcher \"检查新帖子\"。",
    "定时任务交付目标包括 telegram、discord、slack、电子邮件、短信和 12 个以上平台。",
    "如果定时任务响应以 [SILENT] 开头，则抑制交付 — 适用于仅监控的任务。",
    "定时任务支持相对延迟（30m）、间隔（每 2h）、cron 表达式和 ISO 时间戳。",
    "定时任务在全新的 Agent 会话中运行 — 提示词必须是自包含的。",

    # --- 语音 ---
    "如果安装了 faster-whisper（免费本地语音转文本），语音模式无需 API 密钥即可工作。",
    "五个 TTS 提供商可用：Edge TTS（免费）、ElevenLabs、OpenAI、NeuTTS（免费本地）、MiniMax。",
    "/voice on 在 CLI 中启用语音模式。Ctrl+B 切换按下说话录音。",
    "流式 TTS 在生成句子时播放 — 你无需等待完整响应。",
    "Telegram、Discord、WhatsApp 和 Slack 上的语音消息会自动转录。",

    # --- 消息网关与消息传递 ---
    "Hermes 在 21 个消息传递平台上运行：Telegram、Discord、Slack、WhatsApp、Signal、Matrix、IRC、Microsoft Teams、电子邮件等。",
    "hermes gateway install 将其设置为系统服务，在启动时启动。",
    "DingTalk 使用流模式 — 无需 Webhook 或公共 URL。",
    "BlueBubbles 通过本地 macOS 服务器将 iMessage 引入 Hermes。",
    "Webhook 路由支持 HMAC 验证、速率限制和事件过滤。",
    "API 服务器暴露一个与 Open WebUI 和 LibreChat 兼容的 OpenAI 兼容端点。",
    "Discord 语音频道模式：机器人加入 VC，转录语音，并回话。",
    "group_sessions_per_user: true 在群聊中为每个人提供自己的会话。",
    "/sethome 将聊天标记为定时任务交付的主频道。",
    "消息网关支持基于不活动的超时 — 活动的 Agent 可以无限期运行。",

    # --- 安全 ---
    "危险命令批准有 4 个层级：一次、会话、始终（永久允许列表）、拒绝。",
    "智能批准模式使用 LLM 自动批准安全命令并标记危险命令。",
    "SSRF 保护阻止私有网络、环回、链路本地和云元数据地址。",
    "Tirith 预执行扫描检测同形 URL 欺骗和管道到解释器模式。",
    "MCP 子进程接收过滤后的环境 — 只有安全的系统变量通过。",
    "上下文文件（.hermes.md、AGENTS.md）在加载前会进行安全扫描以检测提示词注入。",
    "config.yaml 中的 command_allowlist 永久批准特定的 shell 命令模式。",

    # --- 上下文与压缩 ---
    "当上下文达到阈值时自动压缩 — 记忆被刷新，历史被总结。",
    "状态栏随着上下文填充而变为黄色、橙色，然后红色。",
    "~/.hermes/SOUL.md 下的 SOUL.md 是 Agent 的主要身份 — 自定义它以塑造行为。",
    "Hermes 从 .hermes.md、AGENTS.md、CLAUDE.md 或 .cursorrules（第一个匹配项）加载项目上下文。",
    "子目录 AGENTS.md 文件在 Agent 导航到文件夹时逐步被发现。",
    "上下文文件限制为 20,000 个字符，并进行智能头/尾截断。",

    # --- 浏览器 ---
    "五个浏览器提供商：本地 Chromium、Browserbase、Browser Use、Camofox 和 Firecrawl。",
    "Camofox 是一个反检测浏览器 — 具有 C++ 指纹欺骗功能的 Firefox 分支。",
    "browser_navigate 自动返回页面快照 — 之后无需调用 browser_snapshot。",
    "browser_vision 与 annotate=true 在交互式元素上叠加编号标签。",

    # --- MCP ---
    "MCP 服务器在 config.yaml 中配置 — 支持 stdio 和 HTTP 传输。",
    "每服务器工具过滤：tools.include 白名单和 tools.exclude 黑名单特定工具。",
    "MCP 服务器在运行时自动生成工具集 — hermes tools 可以按平台切换它们。",
    "MCP OAuth 支持：auth: oauth 启用基于浏览器的 PKCE 授权。",

    # --- 检查点与回滚 ---
    "当没有文件被修改时，检查点零开销 — 默认启用。",
    "自动保存预回滚快照，以便你可以撤销撤销操作。",
    "/rollback 还会撤销对话轮次，因此 Agent 不会记住已回滚的更改。",
    "检查点使用 ~/.hermes/checkpoints/ 中的影子仓库 — 你项目的 .git 永远不会被触及。",

    # --- 批量与数据 ---
    "batch_runner.py 并行处理数百个提示词以生成训练数据。",
    "hermes chat -Q 为程序化使用启用安静模式 — 抑制横幅和旋转器。",
    "轨迹保存（--save-trajectories）捕获完整的工具使用痕迹以进行模型训练。",

    # --- 插件 ---
    "三种插件类型：通用（工具/钩子）、记忆提供商和上下文引擎。",
    "hermes plugins install owner/repo 直接从 GitHub 安装插件。",
    "8 个外部记忆提供商可用：Honcho、OpenViking、Mem0、Hindsight 等。",
    "插件钩子包括 pre/post_tool_call、pre/post_llm_call 和用于输出规范化的 transform_terminal_output。",

    # --- 杂项 ---
    "提示词缓存（Anthropic）通过重用缓存的系统提示词前缀来降低成本。",
    "Agent 在后台线程中自动生成会话标题 — 零延迟影响。",
    "智能模型路由可以将简单查询自动路由到更便宜的模型。",
    "斜杠命令支持前缀匹配：/h 解析为 /help，/mod 解析为 /model。",
    "将文件路径拖入终端会自动附加图像或作为上下文发送。",
    "仓库根目录中的 .worktreeinclude 列出要复制到工作树中的 gitignored 文件。",
    "hermes acp 将 Hermes 作为 ACP 服务器运行，用于 VS Code、Zed 和 JetBrains 集成。",
    "自定义提供商：在 config.yaml 的 custom_providers 下保存命名的端点。",
    "HERMES_EPHEMERAL_SYSTEM_PROMPT 注入一个永远不会持久化到历史记录的系统提示词。",
    "credential_pool_strategies 支持 fill_first、round_robin、least_used 和 random rotation。",
    "hermes login 支持基于 OAuth 的 Nous 和 OpenAI Codex 提供商身份验证。",
    "API 服务器支持 Chat Completions 和 Responses API，并具有服务器端状态。",
    "config.yaml 中的 tool_preview_length: 0 在旋转器的活动源中显示完整的文件路径。",
    "hermes status --deep 在所有组件上运行更深入的诊断检查。",

    # --- 隐藏的宝石与高级用户技巧 ---
    "定时任务可以附加 Python 脚本（--script），其标准输出作为上下文注入到提示词中。",
    "定时任务脚本位于 ~/.hermes/scripts/ 中，并在 Agent 之前运行 — 非常适合数据收集流水线。",
    "config.yaml 中的 prefill_messages_file 将少量示例注入到每个 API 调用中，永远不会保存到历史记录。",
    "SOUL.md 完全替换 Agent 的默认身份 — 重写它以让 Hermes 成为你自己的。",
    "SOUL.md 在首次运行时自动植入默认个性。编辑 ~/.hermes/SOUL.md 以自定义。",
    "/compress <焦点主题> 将 60-70% 的摘要预算分配给你的主题，并积极修剪其余部分。",
    "在第二次及以后的压缩中，压缩器会更新先前的摘要，而不是从头开始。",
    "在消息网关会话重置之前，Hermes 会自动在后台将重要事实刷新到记忆中。",
    "config.yaml 中的 network.force_ipv4: true 修复在具有损坏 IPv6 的服务器上的挂起 — 猴子补丁 socket。",
    "终端工具注释常见的退出代码：grep 返回 1 = '未找到匹配项（不是错误）'。",
    "失败的前台终端命令会自动重试最多 3 次，并采用指数退避（2s、4s、8s）。",
    "裸 sudo 命令会自动重写以从 .env 管道 SUDO_PASSWORD — 无需交互式提示。",
    "execute_code 具有内置助手：json_parse() 用于容错解析、shell_quote() 和带退避的 retry()。",
    "execute_code 的 7 个沙盒工具（web_search、terminal、read/write/search/patch）使用 RPC — 永远不会进入上下文。",
    "读取同一文件区域 3 次以上会触发警告。4 次以上，会被硬阻止以防止循环。",
    "write_file 和 patch 检测文件自上次读取以来是否被外部修改，并警告过时。",
    "V4A 补丁格式支持添加文件、删除文件和移动文件指令 — 不仅仅是更新。",
    "MCP 服务器可以通过采样请求 LLM 补全 — Agent 成为服务器的工具。",
    "MCP 服务器发送 notifications/tools/list_changed 以触发自动工具重新注册，无需重启。",
    "delegate_task 与 acp_command: 'claude' 从任何平台生成 Claude Code 作为子 Agent。",
    "委派有一个心跳线程 — 子活动传播到父级，防止消息网关超时。",
    "当提供商返回 HTTP 402（需要付款）时，辅助客户端会自动故障转移到下一个。",
    "agent.tool_use_enforcement 引导描述动作而不是调用工具的模型 — 对 GPT/Codex 自动。",
    "agent.restart_drain_timeout（默认 60 秒）让正在运行的 Agent 在消息网关重启生效前完成。",
    "agent.api_max_retries（默认 3 次）控制 Agent 在暴露错误之前重试失败 API 调用的次数 — 降低它以快速故障转移。",
    "消息网关按会话缓存 AIAgent 实例 — 销毁此缓存会破坏 Anthropic 提示词缓存。",
    "任何网站都可以通过 /.well-known/skills/index.json 暴露技能 — 技能中心会自动发现它们。",
    "~/.hermes/skills/.hub/audit.log 下的技能审计日志跟踪每次安装和移除操作。",
    "过时的 git 工作树会自动清理：启动时清理 24-72 小时旧且没有未推送提交的工作树。",
    "每个配置文件在 HERMES_HOME/home/ 下都有自己的子进程 HOME — 隔离的 git、ssh、npm、gh 配置。",
    "HERMES_HOME_MODE 环境变量（八进制，例如 0701）为 Web 服务器遍历设置自定义目录权限。",
    "容器模式：将 .container-mode 放在 HERMES_HOME 中，主机 CLI 会自动执行到容器中。",
    "Ctrl+C 有 5 个优先级层级：取消录音 → 取消提示词 → 取消选择器 → 中断 Agent → 退出。",
    "Agent 运行期间的每次中断都会记录到 ~/.hermes/interrupt_debug.log 并带有时间戳。",
    "BROWSER_CDP_URL 将浏览器工具连接到任何正在运行的 Chromium 系列浏览器 — 接受 WebSocket、HTTP 或 host:port。",
    "BROWSERBASE_ADVANCED_STEALTH=true 启用具有自定义 Chromium 的高级反检测（Scale 计划）。",
    "CLI 在终端宽度小于 80 列时自动切换到紧凑模式。",
    "快速命令支持两种类型：exec（直接运行 shell 命令）和 alias（重定向到另一个命令）。",
    "每任务委派模型：config 中的 delegation.model 和 delegation.provider 将子 Agent 路由到更便宜的模型。",
    "delegation.reasoning_effort 独立控制子 Agent 的思考深度。",
    "config.yaml 中的 display.platforms 允许每个平台的显示覆盖：{telegram: {tool_progress: all}}。",
    "config 中的 human_delay.mode 模拟人类打字速度 — 可配置的 min_ms/max_ms 范围。",
    "配置版本迁移在加载时自动运行 — 新的配置键出现而无需手动干预。",
    "GPT 和 Codex 模型获得特殊的系统提示词指导，用于工具纪律和强制工具使用。",
    "Gemini 模型获得针对绝对路径、并行工具调用和非交互式命令的定制指令。",
    "config.yaml 中的 context.engine 可以设置为插件名称，用于替代的上下文管理策略。",
    "超过 8000 个 Token 的浏览器页面在返回给 Agent 之前由辅助 LLM 自动总结。",
    "压缩器进行廉价的预传递：超过 200 个字符的工具输出在 LLM 运行之前被替换为占位符。",
    "当压缩失败时，进一步尝试会暂停 10 分钟，以避免 API 冲击。",
    "长危险命令（>70 字符）在批准提示中获得一个 'view' 选项，以便首先查看完整文本。",
    "音频电平可视化在语音录音期间根据麦克风 RMS 电平显示 ▁▂▃▄▅▆▇ 条。",
    "配置文件名称不能与现有的 PATH 二进制文件冲突 — 'hermes profile create ls' 将被拒绝。",
    "hermes profile create backup --clone-all 复制所有内容（配置、密钥、SOUL.md、记忆、技能、会话）。",
    "语音录音键可通过 config.yaml 中的 voice.record_key 配置 — 不仅仅是 Ctrl+B。",
    ".cursorrules 和 .cursor/rules/*.mdc 文件被自动检测并作为项目上下文加载。",
    "上下文文件支持 10 种以上的提示词注入模式 — 不可见 Unicode、'忽略指令'、泄露尝试。",
    "GPT-5 和 Codex 在消息格式中使用 'developer' 角色而不是 'system'。",
    "每任务辅助覆盖：config.yaml 中的 auxiliary.vision.provider、auxiliary.compression.model 等。",
    "辅助客户端将 'main' 视为提供商别名 — 解析为你实际的主要提供商 + 模型。",
    "hermes claw migrate --dry-run 预览 OpenClaw 迁移而不写入任何内容。",
    "带有引号或转义空格的文件路径会自动处理 — 无需手动清理。",
    "斜杠命令永远不会触发大粘贴折叠 — 带有大参数的 /command 正常工作。",
    "在中断模式下，在 Agent 执行期间输入的斜杠命令绕过中断逻辑并立即运行。",
    "HERMES_DEV=1 绕过容器模式检测以进行本地开发。",
    "每个 MCP 服务器都有自己的工具集（mcp-servername），可以通过 hermes tools 独立切换。",
    "config 中的 MCP ${ENV_VAR} 占位符在服务器生成时解析 — 包括来自 ~/.hermes/.env 的变量。",
    "来自受信任仓库（NousResearch）的技能获得 'trusted' 安全级别；社区技能获得额外扫描。",
    "~/.hermes/skills/.hub/quarantine/ 下的技能隔离区保存待安全审查的技能。",

    # --- 高级斜杠命令 ---
    '/steer <prompt> 在下一次工具调用后注入一个注释 — 在任务中途微调方向而不中断。',
    '/goal <text> 设置一个持续的 Ralph 循环目标 — Hermes 在一轮又一轮后自动继续，直到判断器说完成。',
    '/snapshot create [label] 保存 Hermes 配置的完整状态快照；/snapshot restore <id> 稍后恢复。',
    '/copy [N] 将最后的助手响应复制到你的剪贴板，或者使用数字复制倒数第 N 个。',
    '/redraw 强制完全重新绘制 UI，修复 tmux 调整大小或鼠标选择伪影后的终端漂移。',
    '/agents（别名 /tasks）显示当前会话中活动的 Agent 和正在运行的后台任务。',
    '/footer 切换最终回复上的消息网关页脚，显示模型、工具计数和轮次计时。',
    '/busy queue|steer|interrupt 控制在 Hermes 工作时按 Enter 键的作用。',
    '/topic 在 Telegram 私信中启用用户管理的多会话主题模式 — /topic <id> 内联恢复过去的会话。',
    '/approve session|always 使用你选择的信任范围运行待处理的危险命令；/deny 拒绝它。',
    '/restart 在排空活动运行后优雅地重启消息网关，然后在恢复时通知请求者。',
    '/kanban boards switch <slug> 从聊天内部切换活动的多项目看板。',
    '/reload 将 ~/.hermes/.env 重新加载到正在运行的会话中 — 获取新的 API 密钥而无需重启。',

    # --- 定时任务（无 Agent 和脚本） ---
    'cronjob 与 no_agent=True 按计划运行脚本并直接发送其标准输出 — 零 Token，零 LLM。',
    '空的定时任务脚本标准输出意味着静默滴答 — 不交付任何内容，非常适合阈值看门狗。',
    "HERMES_CRON_MAX_PARALLEL（默认 4）限制每次滴答运行多少个定时任务，以免突发流量使你的密钥饱和。",

    # --- 消息网关钩子 ---
    '消息网关钩子位于 ~/.hermes/hooks/<name>/ 下，包含 HOOK.yaml + handler.py — 处理程序必须命名为 `handle`。',
    '钩子事件包括 gateway:startup、session:start、agent:step 和 command:* 通配符订阅。',
    '放置一个 ~/.hermes/BOOT.md 清单，gateway:startup 钩子每次启动时将其作为一次性 Agent 运行。',

    # --- 策展器 ---
    'hermes curator run --dry-run 预览策展器将归档或合并的内容，而不进行任何更改。',
    "hermes curator pin <skill> 硬隔离一个技能，防止自动归档和 Agent 的 skill_manage 工具。",
    'hermes curator rollback 从运行前快照恢复技能 — 备份位于 skills/.curator_backups/ 下。',

    # --- 凭据池与路由 ---
    'hermes auth reset <provider> 清除凭据池上的所有冷却和耗尽标志。',
    'credential_pool_strategies.<provider>: round_robin 均匀轮换密钥，而不是默认的 fill_first。',
    'use_gateway: true 每工具将 Web、图像、tts 或浏览器路由通过你的 Nous 订阅 — 无需额外密钥。',
    'provider_routing.data_collection: deny 在 OpenRouter 上排除存储数据的提供商。',
    'provider_routing.require_parameters: true 仅路由到支持你请求中每个参数的提供商。',

    # --- TUI 与仪表板 ---
    'HERMES_TUI_RESUME=1 在启动时自动重新附加到最近的 TUI 会话 — SSH 断开后很方便。',
    "HERMES_TUI_THEME=light|dark|<hex> 在未设置 COLORFGBG 的终端上强制 TUI 主题。",
    'TUI 中的 Ctrl+G 或 Ctrl+X Ctrl+E 在 $EDITOR 中打开输入缓冲区以进行长多行提示词。',
    'TUI 内联渲染 LaTeX — $E=mc^2$ 变成 Unicode 数学而不是原始 TeX。',
    'hermes dashboard 在 127.0.0.1:9119 启动本地 Web UI — 零数据离开本地主机。',
    'hermes dashboard --tui 通过 xterm.js 和 WebSocket PTY 将完整的 Hermes TUI 嵌入到你的浏览器中。',
    '在 ~/.hermes/dashboard-themes/ 中放置一个包含两种调色板颜色的 YAML 以重新设计整个仪表板的外观。',
    '仪表板插件是即插即用的：manifest.json + JS 包在 ~/.hermes/dashboard-plugins/ 中 — 无需 npm 构建。',
    '仪表板主题中的 layoutVariant: cockpit 添加一个 260px 的左侧轨道，插件可以通过侧边栏槽填充。',

    # --- 环境变量与配置门控 ---
    "display.tool_progress_command: true 在消息传递平台上暴露 /verbose；默认情况下它仅限 CLI。",
    'HERMES_BACKGROUND_NOTIFICATIONS=result 仅在后台任务完成时通知（相对于 all/error/off）。',
    'HERMES_WRITE_SAFE_ROOT 将 write_file 和 patch 限制在目录前缀内；外部写入需要批准。',
    'HERMES_IGNORE_RULES 跳过 AGENTS.md、SOUL.md、.cursorrules、记忆和预加载技能的自动注入。',
    'HERMES_ACCEPT_HOOKS 自动批准 config.yaml 中声明的未见过的 shell 钩子，而无需 TTY 提示。',
    'auxiliary.goal_judge.model 将 /goal 判断器路由到廉价快速模型，以保持循环成本接近零。',
    '检查点跳过包含超过 50,000 个文件的目录，以避免在大型单体仓库上进行缓慢的 git 操作。',

    # --- TTS ---
    'tts.provider: piper 在 CPU 上运行 44 种语言的本地 TTS — 语音自动下载到 ~/.hermes/cache/piper-voices/。',
    'tts.providers.<name>.type: command 使用 {input_path} 和 {output_path} 占位符连接任何 CLI TTS 引擎。',

    # --- API 服务器与代理 ---
    'API_SERVER_ENABLED=true 与消息网关一起运行一个 OpenAI 兼容端点，用于 Open WebUI 和 LibreChat。',
    'GATEWAY_PROXY_URL 运行拆分设置：平台 I/O 本地，Agent 工作委派给远程 API 服务器。',

    # --- 平台特定 ---
    'MATRIX_DEVICE_ID 固定一个稳定的设备 ID 用于 E2EE — 没有它，密钥每次启动都会轮换，历史解密会中断。',
    'TELEGRAM_WEBHOOK_SECRET 在设置 TELEGRAM_WEBHOOK_URL 时是必需的 — 使用 openssl rand -hex 32 生成。',

    # --- 批量 ---
    "batch_runner.py --resume content-matches 通过文本匹配已完成的提示词，因此数据集重新排序不会重新运行已完成的工作。",

    # --- 较少人知的斜杠命令 ---
    '/new 在原地启动一个新会话（别名 /reset）— 新的会话 ID，干净的历史记录，CLI 保持打开。',
    '/clear 清除终端屏幕并启动一个新会话 — 一个用于视觉重置的快捷方式。',
    '/history 内联打印当前对话而不离开 CLI — 适用于快速重读。',
    '/save 将会话写入磁盘而不结束会话。',
    '/status 一目了然地显示会话信息：ID、标题、模型、Token 使用情况和经过时间。',
    '/image <path> 附加本地图像文件到你的下一个提示词，无需粘贴或拖放。',
    '/platforms 直接从聊天内部显示消息网关和消息传递平台连接状态。',
    '/commands 分页显示完整的斜杠命令 + 已安装技能列表 — 在没有 Tab 补全的平台上很有用。',
    '/toolsets 列出每个可用的工具集，以便你知道 -t/--toolsets 接受什么。',
    '/gquota 显示 Google Gemini Code Assist 配额使用情况，并在该提供商处于活动状态时显示进度条。',
    '/voice tts 切换仅 TTS 模式 — Agent 回复大声播放，但你仍然输入提示词。',
    '/reload-skills 重新扫描 ~/.hermes/skills/，以便即插即用的技能出现而无需重启会话。',
    '/indicator kaomoji|emoji|unicode|ascii 选择在 Agent 运行期间显示的 TUI 忙碌指示器样式。',
    '/debug 上传支持包（系统信息 + 日志）并返回可共享链接 — 在聊天中也有效。',

    # --- CLI 子命令与标志 ---
    'hermes -z "<prompt>" 是最纯粹的一次性：标准输出上的最终答案，没有其他内容 — 非常适合在脚本中管道传输。',
    'hermes chat --pass-session-id 将会话 ID 注入系统提示词，以便 Agent 可以自我引用它。',
    'hermes chat --image path/to/pic.png 将本地图像附加到单个 -q 查询，无需单独的上传步骤。',
    'hermes chat --ignore-user-config 跳过 ~/.hermes/config.yaml — 可重现的错误报告和 CI 运行。',
    "hermes chat --source tool 标记程序化聊天，以便它们不会使 hermes sessions list 混乱。",
    'hermes dump --show-keys 包括经过编辑的 API 密钥指纹，以进行更深层次的支持调试。',
    'hermes sessions rename <ID> "新标题" 重命名任何过去的会话；hermes sessions delete <ID> 删除一个。',
    'hermes import 恢复由 sessions export 或 profile export 生成的会话导出或配置文件存档。',
    'hermes fallback 交互式管理 fallback_model 链 — 无需手动编辑 config.yaml。',
    'hermes pairing 轮换私信配对令牌 — 轮换后的第一个消息者获得对机器人的访问权限。',
    'hermes setup 在一个交互式流程中引导首次用户完成提供商、密钥和平台连接。',
    'hermes status --deep 在每个组件上运行完整的健康扫描；普通的 hermes status 是快速视图。',

    # --- Agent 行为环境变量 ---
    'HERMES_AGENT_TIMEOUT=0 为正在运行的 Agent 禁用消息网关不活动终止 — 用于长时间研究运行。',
    'HERMES_ENABLE_PROJECT_PLUGINS=1 从 ./.hermes/plugins/ 自动加载仓库本地插件 — 设计上受信任门控。',
    "HERMES_DISABLE_FILE_STATE_GUARD=1 关闭 patch 和 write_file 上的 '自你读取后文件已更改' 防护。",
    'HERMES_ALLOW_PRIVATE_URLS=true 允许 Web 工具访问 localhost 和私有网络 — 在消息网关模式下默认关闭。',
    'HERMES_OPTIONAL_SKILLS=name1,name2 在每个配置文件的首次运行时自动安装额外的可选目录技能。',
    'HERMES_BUNDLED_SKILLS 指向自定义的捆绑技能树 — 由 Homebrew 和 Nix 打包使用。',
    'HERMES_DUMP_REQUEST_STDOUT=1 将每个 API 请求负载转储到标准输出而不是日志文件。',
    'HERMES_OAUTH_TRACE=1 记录经过编辑的 OAuth 令牌交换和刷新尝试以调试提供商身份验证。',
    'HERMES_STREAM_RETRIES（默认 3 次）控制中间流重连尝试以应对瞬态网络错误。',

    # --- 消息网关行为环境变量 ---
    'HERMES_GATEWAY_BUSY_ACK_ENABLED=false 当用户向繁忙的 Agent 发送消息时，静默 ⚡/⏳/⏩ 确认消息。',
    'HERMES_AGENT_NOTIFY_INTERVAL（默认 180 秒）设置消息网关在长轮次中通知进度的频率。',
    'HERMES_RESTART_DRAIN_TIMEOUT（默认 900 秒）限制 /restart 在强制之前等待正在运行的任务的时间。',
    'HERMES_CHECKPOINT_TIMEOUT（默认 30 秒）限制文件系统检查点创建 — 在大型单体仓库上提高它。',

    # --- 辅助任务与图像生成 ---
    'config.yaml 中的 image_gen.model 选择 FAL 模型：flux-2/klein、gpt-image-2、nano-banana-pro 等。',
    'image_gen.provider 通过插件（OpenAI Images、Codex、FAL）路由图像生成，而不是默认。',
    'AUXILIARY_VISION_BASE_URL + AUXILIARY_VISION_API_KEY 将视觉分析指向任何 OpenAI 兼容端点。',

    # --- 安全 ---
    'security.tirith_fail_open: false 使 Hermes 在 tirith 扫描器本身出错时阻止命令。',
    'TIRITH_FAIL_OPEN 环境变量覆盖 tirith_fail_open 配置 — 无需编辑 config.yaml 的快速切换。',

    # --- 会话与源标签 ---
    '--source tool 聊天默认从 hermes sessions list 中排除 — 显式设置 --source 以查看它们。',
    '会话 ID 带有时间戳前缀（20250305_091523_abcd），以便在 ls 和 jq 中自然排序。',

    # --- 杂项 ---
    'API_SERVER_MODEL_NAME 自定义 /v1/models 上的模型名称 — 对于多配置文件 Open WebUI 设置至关重要。',
    '仪表板插件从 /dashboard-plugins/<name>/ 提供 — 将文件放入 ~/.hermes/dashboard-plugins/。',
]
def get_random_tip(exclude_recent: int = 0) -> str:
    """Return a random tip string.

    Args:
        exclude_recent: not used currently; reserved for future
            deduplication across sessions.
    """
    return random.choice(TIPS)