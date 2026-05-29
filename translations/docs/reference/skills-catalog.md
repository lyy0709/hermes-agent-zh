---
sidebar_position: 5
title: "内置技能目录"
description: "Hermes Agent 附带的内置技能目录"
---

# 内置技能目录

Hermes 附带一个大型内置技能库，安装时会复制到 `~/.hermes/skills/` 目录。下面的每个技能都链接到一个专用页面，其中包含其完整定义、设置和使用方法。

Hermes 还会在 `hermes update` 时同步内置技能，但同步清单会尊重本地删除和用户编辑。如果此处列出的某个技能在你的配置文件 `~/.hermes/skills/` 目录树中缺失，它仍然随 Hermes 一起提供；你可以使用 `hermes skills reset <name> --restore` 命令恢复它。

如果一个技能在此列表中缺失但存在于代码仓库中，目录可以通过运行 `website/scripts/generate-skill-docs.py` 重新生成。

## apple

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`apple-notes`](/docs/user-guide/skills/bundled/apple/apple-apple-notes) | 通过 memo CLI 管理 Apple 笔记：创建、搜索、编辑。 | `apple/apple-notes` |
| [`apple-reminders`](/docs/user-guide/skills/bundled/apple/apple-apple-reminders) | 通过 remindctl 管理 Apple 提醒事项：添加、列出、完成。 | `apple/apple-reminders` |
| [`findmy`](/docs/user-guide/skills/bundled/apple/apple-findmy) | 在 macOS 上通过 FindMy.app 追踪 Apple 设备/AirTag。 | `apple/findmy` |
| [`imessage`](/docs/user-guide/skills/bundled/apple/apple-imessage) | 在 macOS 上通过 imsg CLI 发送和接收 iMessage/短信。 | `apple/imessage` |
| [`macos-computer-use`](/docs/user-guide/skills/bundled/apple/apple-macos-computer-use) | 在后台驱动 macOS 桌面——截图、鼠标、键盘、滚动、拖拽——而不会窃取用户的鼠标光标、键盘焦点或 Space。适用于任何支持工具使用的模型。当 `computer_use` 工具被...时加载此技能。 | `apple/macos-computer-use` |

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | 将编码任务委派给 Claude Code CLI（功能、PR）。 | `autonomous-ai-agents/claude-code` |
| [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | 将编码任务委派给 OpenAI Codex CLI（功能、PR）。 | `autonomous-ai-agents/codex` |
| [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | 配置、扩展 Hermes Agent 或为其做贡献。 | `autonomous-ai-agents/hermes-agent` |
| [`kanban-codex-lane`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-kanban-codex-lane) | 当 Hermes Kanban 工作器希望将 Codex CLI 作为独立的实现通道运行，同时 Hermes 保持对任务生命周期、协调、测试和交接的所有权时使用。 | `autonomous-ai-agents/kanban-codex-lane` |
| [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | 将编码任务委派给 OpenCode CLI（功能、PR 审查）。 | `autonomous-ai-agents/opencode` |

## creative

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) | 深色主题的 SVG 架构/云/基础设施图，输出为 HTML。 | `creative/architecture-diagram` |
| [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art) | ASCII 艺术：pyfiglet、cowsay、boxes、image-to-ascii。 | `creative/ascii-art` |
| [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video) | ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF。 | `creative/ascii-video` |
| [`baoyu-article-illustrator`](/docs/user-guide/skills/bundled/creative/creative-baoyu-article-illustrator) | 文章插图：类型 × 风格 × 调色板一致性。 | `creative/baoyu-article-illustrator` |
| [`baoyu-comic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-comic) | 知识漫画：教育、传记、教程。 | `creative/baoyu-comic` |
| [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic) | 信息图：21 种布局 x 21 种风格。 | `creative/baoyu-infographic` |
| [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design) | 设计一次性 HTML 制品（落地页、演示文稿、原型）。 | `creative/claude-design` |
| [`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui) | 使用 ComfyUI 生成图像、视频和音频——安装、启动、管理节点/模型、运行带参数注入的工作流。使用官方的 comfy-cli 进行生命周期管理，并使用直接的 REST/WebSocket API 进行执行。 | `creative/comfyui` |
| [`ideation`](/docs/user-guide/skills/bundled/creative/creative-creative-ideation) | 通过创意约束生成项目想法。 | `creative/creative-ideation` |
| [`design-md`](/docs/user-guide/skills/bundled/creative/creative-design-md) | 编写/验证/导出 Google 的 DESIGN.md Token 规范文件。 | `creative/design-md` |
| [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) | 手绘风格的 Excalidraw JSON 图表（架构、流程图、序列图）。 | `creative/excalidraw` |
| [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer) | 人性化文本：去除 AI 痕迹，添加真实声音。 | `creative/humanizer` |
| [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video) | Manim CE 动画：3Blue1Brown 风格的数学/算法视频。 | `creative/manim-video` |
| [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js) | p5.js 草图：生成艺术、着色器、交互式、3D。 | `creative/p5js` |
| [`pixel-art`](/docs/user-guide/skills/bundled/creative/creative-pixel-art) | 像素艺术，附带时代调色板（NES、Game Boy、PICO-8）。 | `creative/pixel-art` |
| [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs) | 54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现。 | `creative/popular-web-designs` |
| [`pretext`](/docs/user-guide/skills/bundled/creative/creative-pretext) | 在使用 @chenglou/pretext 构建创意浏览器演示时使用——无 DOM 的文本布局，用于 ASCII 艺术、围绕障碍物的排版流、文本作为几何的游戏、动态排版以及文本驱动的生成艺术。生成单文件 HT... | `creative/pretext` |
| [`sketch`](/docs/user-guide/skills/bundled/creative/creative-sketch) | 一次性 HTML 线框图：2-3 个设计变体用于比较。 | `creative/sketch` |
| [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | 歌曲创作技巧和 Suno AI 音乐提示词。 | `creative/songwriting-and-ai-music` |
| [`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp) | 通过 twozero MCP 控制正在运行的 TouchDesigner 实例——创建操作器、设置参数、连接线路、执行 Python、构建实时视觉效果。包含 36 个原生工具。 | `creative/touchdesigner-mcp` |
## 数据科学

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`jupyter-live-kernel`](/docs/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) | 通过实时 Jupyter 内核进行迭代式 Python 编程 (hamelnb)。 | `data-science/jupyter-live-kernel` |

## 运维

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`kanban-orchestrator`](/docs/user-guide/skills/bundled/devops/devops-kanban-orchestrator) | 用于通过看板管理工作流的编排器配置的分解剧本和防诱惑规则。"不要自己动手"规则和基本生命周期会自动注入到每个看板工作者的系统提示词中；此技能... | `devops/kanban-orchestrator` |
| [`kanban-worker`](/docs/user-guide/skills/bundled/devops/devops-kanban-worker) | Hermes 看板工作者的陷阱、示例和边界情况。生命周期本身会作为 KANBAN_GUIDANCE 自动注入到每个工作者的系统提示词中（来自 agent/prompt_builder.py）；当您需要更深入的细节时，可以加载此技能... | `devops/kanban-worker` |
| [`webhook-subscriptions`](/docs/user-guide/skills/bundled/devops/devops-webhook-subscriptions) | Webhook 订阅：事件驱动的 Agent 运行。 | `devops/webhook-subscriptions` |

## 内部测试

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`dogfood`](/docs/user-guide/skills/bundled/dogfood/dogfood-dogfood) | Web 应用的探索性质量保证：发现错误、证据、报告。 | `dogfood` |

## 电子邮件

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) | Himalaya CLI：在终端中处理 IMAP/SMTP 电子邮件。 | `email/himalaya` |

## 游戏

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`minecraft-modpack-server`](/docs/user-guide/skills/bundled/gaming/gaming-minecraft-modpack-server) | 托管模组 Minecraft 服务器 (CurseForge, Modrinth)。 | `gaming/minecraft-modpack-server` |
| [`pokemon-player`](/docs/user-guide/skills/bundled/gaming/gaming-pokemon-player) | 通过无头模拟器 + RAM 读取来玩宝可梦游戏。 | `gaming/pokemon-player` |

## GitHub

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`codebase-inspection`](/docs/user-guide/skills/bundled/github/github-codebase-inspection) | 使用 pygount 检查代码库：代码行数、语言、比例。 | `github/codebase-inspection` |
| [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth) | GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录。 | `github/github-auth` |
| [`github-code-review`](/docs/user-guide/skills/bundled/github/github-github-code-review) | 审查 PR：通过 gh 或 REST API 查看差异、添加行内评论。 | `github/github-code-review` |
| [`github-issues`](/docs/user-guide/skills/bundled/github/github-github-issues) | 通过 gh 或 REST API 创建、分类、标记、分配 GitHub issues。 | `github/github-issues` |
| [`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow) | GitHub PR 生命周期：分支、提交、打开、CI、合并。 | `github/github-pr-workflow` |
| [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) | 克隆/创建/复刻仓库；管理远程仓库、发布。 | `github/github-repo-management` |

## MCP

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp) | MCP 客户端：连接服务器、注册工具 (stdio/HTTP)。 | `mcp/native-mcp` |

## 媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search) | 通过 curl + jq 从 Tenor 搜索/下载 GIF。 | `media/gif-search` |
| [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula) | HeartMuLa：根据歌词 + 标签生成类似 Suno 的歌曲。 | `media/heartmula` |
| [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee) | 通过 CLI 生成音频频谱图/特征 (mel, chroma, MFCC)。 | `media/songsee` |
| [`spotify`](/docs/user-guide/skills/bundled/media/media-spotify) | Spotify：播放、搜索、队列、管理播放列表和设备。 | `media/spotify` |
| [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content) | 将 YouTube 字幕转换为摘要、主题帖、博客。 | `media/youtube-content` |

## MLOps

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`audiocraft-audio-generation`](/docs/user-guide/skills/bundled/mlops/mlops-models-audiocraft) | AudioCraft：MusicGen 文本到音乐，AudioGen 文本到声音。 | `mlops/models/audiocraft` |
| [`dspy`](/docs/user-guide/skills/bundled/mlops/mlops-research-dspy) | DSPy：声明式 LM 程序，自动优化提示词，RAG。 | `mlops/research/dspy` |
| [`huggingface-hub`](/docs/user-guide/skills/bundled/mlops/mlops-huggingface-hub) | HuggingFace hf CLI：搜索/下载/上传模型、数据集。 | `mlops/huggingface-hub` |
| [`llama-cpp`](/docs/user-guide/skills/bundled/mlops/mlops-inference-llama-cpp) | llama.cpp 本地 GGUF 推理 + HF Hub 模型发现。 | `mlops/inference/llama-cpp` |
| [`evaluating-llms-harness`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-lm-evaluation-harness) | lm-eval-harness：对 LLM 进行基准测试 (MMLU, GSM8K 等)。 | `mlops/evaluation/lm-evaluation-harness` |
| [`obliteratus`](/docs/user-guide/skills/bundled/mlops/mlops-inference-obliteratus) | OBLITERATUS：消除 LLM 拒绝响应 (均值差异法)。 | `mlops/inference/obliteratus` |
| [`segment-anything-model`](/docs/user-guide/skills/bundled/mlops/mlops-models-segment-anything) | SAM：通过点、框、掩码进行零样本图像分割。 | `mlops/models/segment-anything` |
| [`serving-llms-vllm`](/docs/user-guide/skills/bundled/mlops/mlops-inference-vllm) | vLLM：高吞吐量 LLM 服务，OpenAI API，量化。 | `mlops/inference/vllm` |
| [`weights-and-biases`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-weights-and-biases) | W&B：记录 ML 实验、超参数搜索、模型注册表、仪表板。 | `mlops/evaluation/weights-and-biases` |
## 笔记记录

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) | 在 Obsidian 知识库中读取、搜索、创建和编辑笔记。 | `note-taking/obsidian` |

## 生产力

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`airtable`](/docs/user-guide/skills/bundled/productivity/productivity-airtable) | 通过 curl 使用 Airtable REST API。记录的增删改查、筛选、更新插入。 | `productivity/airtable` |
| [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) | 通过 gws CLI 或 Python 使用 Gmail、日历、云端硬盘、文档、表格。 | `productivity/google-workspace` |
| [`linear`](/docs/user-guide/skills/bundled/productivity/productivity-linear) | Linear：通过 GraphQL + curl 管理问题、项目、团队。 | `productivity/linear` |
| [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps) | 通过 OpenStreetMap/OSRM 进行地理编码、查询兴趣点、路线、时区。 | `productivity/maps` |
| [`nano-pdf`](/docs/user-guide/skills/bundled/productivity/productivity-nano-pdf) | 通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写错误/标题。 | `productivity/nano-pdf` |
| [`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) | Notion API + ntn CLI：页面、数据库、Markdown、Workers。 | `productivity/notion` |
| [`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) | 从 PDF/扫描件中提取文本（使用 pymupdf、marker-pdf）。 | `productivity/ocr-and-documents` |
| [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) | 创建、读取、编辑 .pptx 演示文稿、幻灯片、备注、模板。 | `productivity/powerpoint` |
| [`teams-meeting-pipeline`](/docs/user-guide/skills/bundled/productivity/productivity-teams-meeting-pipeline) | 通过 Hermes CLI 操作 Teams 会议摘要流水线 —— 总结会议、检查流水线状态、重放作业、管理 Microsoft Graph 订阅。 | `productivity/teams-meeting-pipeline` |

## 红队测试

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`godmode`](/docs/user-guide/skills/bundled/red-teaming/red-teaming-godmode) | 越狱 LLM：Parseltongue、GODMODE、ULTRAPLINIAN。 | `red-teaming/godmode` |

## 研究

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) | 通过关键词、作者、类别或 ID 搜索 arXiv 论文。 | `research/arxiv` |
| [`blogwatcher`](/docs/user-guide/skills/bundled/research/research-blogwatcher) | 通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源。 | `research/blogwatcher` |
| [`llm-wiki`](/docs/user-guide/skills/bundled/research/research-llm-wiki) | Karpathy 的 LLM Wiki：构建/查询相互链接的 Markdown 知识库。 | `research/llm-wiki` |
| [`polymarket`](/docs/user-guide/skills/bundled/research/research-polymarket) | 查询 Polymarket：市场、价格、订单簿、历史记录。 | `research/polymarket` |
| [`research-paper-writing`](/docs/user-guide/skills/bundled/research/research-research-paper-writing) | 为 NeurIPS/ICML/ICLR 撰写机器学习论文：从设计到提交。 | `research/research-paper-writing` |

## 智能家居

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`openhue`](/docs/user-guide/skills/bundled/smart-home/smart-home-openhue) | 通过 OpenHue CLI 控制 Philips Hue 灯、场景、房间。 | `smart-home/openhue` |

## 社交媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) | 通过 xurl CLI 使用 X/Twitter：发帖、搜索、私信、媒体、v2 API。 | `social-media/xurl` |

## 软件开发

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`debugging-hermes-tui-commands`](/docs/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) | 调试 Hermes TUI 斜杠命令：Python、消息网关、Ink UI。 | `software-development/debugging-hermes-tui-commands` |
| [`hermes-agent-skill-authoring`](/docs/user-guide/skills/bundled/software-development/software-development-hermes-agent-skill-authoring) | 在仓库内编写 SKILL.md：frontmatter、验证器、结构。 | `software-development/hermes-agent-skill-authoring` |
| [`hermes-s6-container-supervision`](/docs/user-guide/skills/bundled/software-development/software-development-hermes-s6-container-supervision) | 修改、调试或扩展 Hermes Agent Docker 镜像内的 s6-overlay 监管树 —— 添加新服务、调试配置文件网关、理解架构 B 主程序模式。 | `software-development/hermes-s6-container-supervision` |
| [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger) | 通过 --inspect + Chrome DevTools Protocol CLI 调试 Node.js。 | `software-development/node-inspect-debugger` |
| [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) | 计划模式：将 Markdown 计划写入 .hermes/plans/，不执行。 | `software-development/plan` |
| [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy) | 调试 Python：pdb REPL + debugpy 远程调试（DAP）。 | `software-development/python-debugpy` |
| [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | 提交前代码审查：安全扫描、质量门禁、自动修复。 | `software-development/requesting-code-review` |
| [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike) | 在构建前进行一次性实验以验证想法。 | `software-development/spike` |
| [`subagent-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) | 通过 delegate_task 子 Agent 执行计划（两阶段审查）。 | `software-development/subagent-driven-development` |
| [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 四阶段根本原因调试：在修复前理解错误。 | `software-development/systematic-debugging` |
| [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) | TDD：强制执行 RED-GREEN-REFACTOR 循环，先写测试后写代码。 | `software-development/test-driven-development` |
| [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans) | 编写实施计划：分解为小任务、路径、代码。 | `software-development/writing-plans` |
## yuanbao

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`yuanbao`](/docs/user-guide/skills/bundled/yuanbao/yuanbao-yuanbao) | Yuanbao（元宝）群组：@提及用户，查询信息/成员。 | `yuanbao` |