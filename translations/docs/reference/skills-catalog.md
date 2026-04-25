---
sidebar_position: 5
title: "内置技能目录"
description: "Hermes Agent 附带的内置技能目录"
---

# 内置技能目录

Hermes 附带一个大型内置技能库，安装时会复制到 `~/.hermes/skills/` 目录下。下面的每个技能都链接到一个专用页面，其中包含其完整定义、设置和使用方法。

如果某个技能在此列表中缺失但存在于代码仓库中，可以通过 `website/scripts/generate-skill-docs.py` 重新生成目录。

## apple

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`apple-notes`](/docs/user-guide/skills/bundled/apple/apple-apple-notes) | 通过 macOS 上的 memo CLI 管理 Apple Notes（创建、查看、搜索、编辑）。 | `apple/apple-notes` |
| [`apple-reminders`](/docs/user-guide/skills/bundled/apple/apple-apple-reminders) | 通过 remindctl CLI 管理 Apple Reminders（列出、添加、完成、删除）。 | `apple/apple-reminders` |
| [`findmy`](/docs/user-guide/skills/bundled/apple/apple-findmy) | 通过 macOS 上的 FindMy.app，使用 AppleScript 和屏幕截图来追踪 Apple 设备和 AirTag。 | `apple/findmy` |
| [`imessage`](/docs/user-guide/skills/bundled/apple/apple-imessage) | 通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS。 | `apple/imessage` |

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | 将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）。用于构建功能、重构、PR 审查和迭代式编码。需要安装 claude CLI。 | `autonomous-ai-agents/claude-code` |
| [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | 将编码任务委派给 OpenAI Codex CLI Agent。用于构建功能、重构、PR 审查和批量问题修复。需要安装 codex CLI 和一个 git 仓库。 | `autonomous-ai-agents/codex` |
| [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | 使用和扩展 Hermes Agent 的完整指南——CLI 用法、设置、配置、生成额外 Agent、消息网关平台、技能、语音、工具、配置文件以及简洁的贡献者参考。在帮助用户时加载此技能... | `autonomous-ai-agents/hermes-agent` |
| [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | 将编码任务委派给 OpenCode CLI Agent，用于功能实现、重构、PR 审查和长时间运行的自主会话。需要安装并认证 opencode CLI。 | `autonomous-ai-agents/opencode` |

## creative

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) | 生成软件系统和云基础设施的暗色主题 SVG 图表，作为带有内联 SVG 图形的独立 HTML 文件。语义化组件颜色（青色=前端，翠绿色=后端，紫色=数据库，琥珀色=云/AWS，玫瑰色=安全，... | `creative/architecture-diagram` |
| [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art) | 使用 pyfiglet（571 种字体）、cowsay、boxes、toilet、image-to-ascii、远程 API（asciified，ascii.co.uk）和 LLM 后备方案生成 ASCII 艺术。无需 API 密钥。 | `creative/ascii-art` |
| [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video) | ASCII 艺术视频的生产流水线——支持任何格式。将视频/音频/图像/生成式输入转换为彩色 ASCII 字符视频输出（MP4，GIF，图像序列）。涵盖：视频到 ASCII 转换、音频响应式音乐可视化器、... | `creative/ascii-video` |
| [`baoyu-comic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-comic) | 支持多种艺术风格和基调的知识漫画创作者。创建具有详细面板布局和序列图像生成的原创教育漫画。当用户要求创建“知识漫画”、“教育漫画”、“传记漫画”、“教程漫画”时使用... | `creative/baoyu-comic` |
| [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic) | 生成具有 21 种布局类型和 21 种视觉风格的专业信息图。分析内容，推荐布局×风格组合，并生成可供发布的信息图。当用户要求创建“信息图”、“视觉摘要”时使用... | `creative/baoyu-infographic` |
| [`ideation`](/docs/user-guide/skills/bundled/creative/creative-creative-ideation) | 通过创意约束生成项目创意。当用户说“我想构建一些东西”、“给我一个项目创意”、“我很无聊”、“我应该做什么”、“启发我”，或任何“我有工具但没有方向”的变体时使用。适用于... | `creative/creative-ideation` |
| [`design-md`](/docs/user-guide/skills/bundled/creative/creative-design-md) | 编写、验证、差异比较和导出 DESIGN.md 文件——Google 的开源格式规范，为编码 Agent 提供对设计系统的持久化、结构化理解（Token + 原理在一个文件中）。在构建设计系统时使用... | `creative/design-md` |
| [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) | 使用 Excalidraw JSON 格式创建手绘风格图表。为架构图、流程图、序列图、概念图等生成 .excalidraw 文件。文件可以在 excalidraw.com 打开或上传以获得可共享的链接... | `creative/excalidraw` |
| [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video) | 使用 Manim 社区版制作数学和技术动画的生产流水线。创建 3Blue1Brown 风格的讲解视频、算法可视化、方程推导、架构图和数据故事。当用户... | `creative/manim-video` |
| [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js) | 使用 p5.js 制作交互式和生成式视觉艺术的生产流水线。创建基于浏览器的草图、生成式艺术、数据可视化、交互式体验、3D 场景、音频响应式视觉效果和动态图形——导出为... | `creative/p5js` |
| [`pixel-art`](/docs/user-guide/skills/bundled/creative/creative-pixel-art) | 将图像转换为具有硬件精确调色板（NES，Game Boy，PICO-8，C64 等）的复古像素艺术，并将其动画化为短视频。预设涵盖街机、SNES 和 10 多种符合时代的外观。使用 `clarify` 让用户选择一种风格... | `creative/pixel-art` |
| [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs) | 从真实网站提取的 54 个生产级设计系统。加载模板以生成与 Stripe，Linear，Vercel，Notion，Airbnb 等网站视觉识别相匹配的 HTML/CSS。每个模板都包含颜色、排版... | `creative/popular-web-designs` |
| [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | 歌曲创作技巧、AI 音乐生成提示（Suno 重点）、模仿/改编技术、语音技巧和经验教训。这些是工具和想法，不是规则。当艺术需要时，可以打破其中任何一条。 | `creative/songwriting-and-ai-music` |
## 数据科学

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`jupyter-live-kernel`](/docs/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) | 通过 hamelnb 使用实时的 Jupyter 内核进行有状态的、迭代式的 Python 执行。当任务涉及探索、迭代或检查中间结果时加载此技能——例如数据科学、机器学习实验、API 探索或构建... | `data-science/jupyter-live-kernel` |

## 运维

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`webhook-subscriptions`](/docs/user-guide/skills/bundled/devops/devops-webhook-subscriptions) | 为事件驱动的 Agent 激活或直接推送通知（零 LLM 成本）创建和管理 Webhook 订阅。当用户希望外部服务触发 Agent 运行或将通知推送到聊天时使用。 | `devops/webhook-subscriptions` |

## 内部测试

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`dogfood`](/docs/user-guide/skills/bundled/dogfood/dogfood-dogfood) | 对 Web 应用程序进行系统性的探索性 QA 测试——发现错误、捕获证据并生成结构化报告 | `dogfood` |

## 电子邮件

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) | 通过 IMAP/SMTP 管理电子邮件的 CLI。使用 himalaya 在终端中列出、读取、撰写、回复、转发、搜索和组织电子邮件。支持多个账户和使用 MML（MIME 元语言）撰写消息。 | `email/himalaya` |

## 游戏

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`minecraft-modpack-server`](/docs/user-guide/skills/bundled/gaming/gaming-minecraft-modpack-server) | 从 CurseForge/Modrinth 服务器包 zip 文件设置一个模组化的 Minecraft 服务器。涵盖 NeoForge/Forge 安装、Java 版本、JVM 调优、防火墙、局域网配置、备份和启动脚本。 | `gaming/minecraft-modpack-server` |
| [`pokemon-player`](/docs/user-guide/skills/bundled/gaming/gaming-pokemon-player) | 通过无头模拟自主玩宝可梦游戏。启动游戏服务器，从 RAM 读取结构化游戏状态，做出战略决策，并发送按钮输入——全部在终端中完成。 | `gaming/pokemon-player` |

## GitHub

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`codebase-inspection`](/docs/user-guide/skills/bundled/github/github-codebase-inspection) | 使用 pygount 检查和分析代码库，进行代码行数统计、语言细分以及代码与注释比例分析。当被要求检查代码行数、仓库大小、语言构成或代码库统计数据时使用。 | `github/codebase-inspection` |
| [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth) | 使用 git（普遍可用）或 gh CLI 为 Agent 设置 GitHub 身份验证。涵盖 HTTPS Token、SSH 密钥、凭据助手和 gh auth——并带有自动选择正确方法的检测流程。 | `github/github-auth` |
| [`github-code-review`](/docs/user-guide/skills/bundled/github/github-github-code-review) | 通过分析 git 差异、在 PR 上留下内联评论以及执行彻底的推送前审查来审查代码变更。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 的 GitHub REST API。 | `github/github-code-review` |
| [`github-issues`](/docs/user-guide/skills/bundled/github/github-github-issues) | 创建、管理、分类和关闭 GitHub issue。搜索现有 issue、添加标签、分配人员并链接到 PR。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 的 GitHub REST API。 | `github/github-issues` |
| [`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow) | 完整的拉取请求生命周期——创建分支、提交更改、打开 PR、监控 CI 状态、自动修复失败并合并。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 的 GitHub REST API。 | `github/github-pr-workflow` |
| [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) | 克隆、创建、分叉、配置和管理 GitHub 仓库。管理远程仓库、密钥、发布和工作流。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 的 GitHub REST API。 | `github/github-repo-management` |

## MCP

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp) | 内置的 MCP（模型上下文协议）客户端，可连接到外部 MCP 服务器，发现其工具，并将它们注册为原生的 Hermes Agent 工具。支持 stdio 和 HTTP 传输，具有自动重连、安全过滤... | `mcp/native-mcp` |

## 媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search) | 使用 curl 从 Tenor 搜索和下载 GIF。除了 curl 和 jq 外没有其他依赖。适用于查找反应 GIF、创建视觉内容以及在聊天中发送 GIF。 | `media/gif-search` |
| [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula) | 设置并运行 HeartMuLa，这是一个开源的音乐生成模型系列（类似 Suno）。根据歌词 + 标签生成完整的歌曲，支持多语言。 | `media/heartmula` |
| [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee) | 通过 CLI 从音频文件生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）。适用于音频分析、音乐制作调试和视觉文档记录。 | `media/songsee` |
| [`spotify`](/docs/user-guide/skills/bundled/media/media-spotify) | 控制 Spotify——播放音乐、搜索目录、管理播放列表和音乐库、检查设备和播放状态。当用户要求播放/暂停/排队音乐、搜索曲目/专辑/艺术家、管理播放列表或检查正在播放的内容时加载... | `media/spotify` |
| [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content) | 获取 YouTube 视频字幕并将其转换为结构化内容（章节、摘要、帖子、博客文章）。当用户分享 YouTube URL 或视频链接、要求总结视频、请求字幕或希望提取... | `media/youtube-content` |
## mlops

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`audiocraft-audio-generation`](/docs/user-guide/skills/bundled/mlops/mlops-models-audiocraft) | 用于音频生成的 PyTorch 库，包括文本到音乐（MusicGen）和文本到声音（AudioGen）。当你需要根据文本描述生成音乐、创建音效或执行旋律条件音乐生成时使用。 | `mlops/models/audiocraft` |
| [`axolotl`](/docs/user-guide/skills/bundled/mlops/mlops-training-axolotl) | 使用 Axolotl 微调 LLM 的专家指导 - YAML 配置、100+ 模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持 | `mlops/training/axolotl` |
| [`dspy`](/docs/user-guide/skills/bundled/mlops/mlops-research-dspy) | 使用声明式编程构建复杂的 AI 系统，自动优化提示词，使用 DSPy（斯坦福 NLP 的系统化 LM 编程框架）创建模块化 RAG 系统和 Agent | `mlops/research/dspy` |
| [`huggingface-hub`](/docs/user-guide/skills/bundled/mlops/mlops-huggingface-hub) | Hugging Face Hub CLI (hf) — 搜索、下载和上传模型与数据集，管理仓库，使用 SQL 查询数据集，部署推理端点，管理 Spaces 和存储桶。 | `mlops/huggingface-hub` |
| [`llama-cpp`](/docs/user-guide/skills/bundled/mlops/mlops-inference-llama-cpp) | llama.cpp 本地 GGUF 推理 + HF Hub 模型发现。 | `mlops/inference/llama-cpp` |
| [`evaluating-llms-harness`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-lm-evaluation-harness) | 在 60+ 个学术基准（MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）上评估 LLM。用于基准测试模型质量、比较模型、报告学术结果或跟踪训练进度。行业标准，被 El... 使用 | `mlops/evaluation/lm-evaluation-harness` |
| [`obliteratus`](/docs/user-guide/skills/bundled/mlops/mlops-inference-obliteratus) | 使用 OBLITERATUS 移除开源权重 LLM 的拒绝行为 — 利用机制可解释性技术（均值差分、SVD、白化 SVD、LEACE、SAE 分解等）在保留推理能力的同时剔除护栏。提供 9 种 CLI 方法，... | `mlops/inference/obliteratus` |
| [`outlines`](/docs/user-guide/skills/bundled/mlops/mlops-inference-outlines) | 在生成过程中保证有效的 JSON/XML/代码结构，使用 Pydantic 模型实现类型安全的输出，支持本地模型（Transformers、vLLM），并使用 Outlines（dottxt.ai 的结构化生成库）最大化推理速度 | `mlops/inference/outlines` |
| [`segment-anything-model`](/docs/user-guide/skills/bundled/mlops/mlops-models-segment-anything) | 用于图像分割的基础模型，具有零样本迁移能力。当你需要使用点、框或掩码作为提示来分割图像中的任何对象，或自动生成图像中所有对象的掩码时使用。 | `mlops/models/segment-anything` |
| [`fine-tuning-with-trl`](/docs/user-guide/skills/bundled/mlops/mlops-training-trl-fine-tuning) | 使用 TRL 通过强化学习微调 LLM - 用于指令微调的 SFT，用于偏好对齐的 DPO，用于奖励优化的 PPO/GRPO，以及奖励模型训练。当需要 RLHF、使模型与偏好对齐或从...训练时使用 | `mlops/training/trl-fine-tuning` |
| [`unsloth`](/docs/user-guide/skills/bundled/mlops/mlops-training-unsloth) | 使用 Unsloth 进行快速微调的专家指导 - 训练速度提升 2-5 倍，内存占用减少 50-80%，LoRA/QLoRA 优化 | `mlops/training/unsloth` |
| [`serving-llms-vllm`](/docs/user-guide/skills/bundled/mlops/mlops-inference-vllm) | 使用 vLLM 的分页注意力机制和连续批处理技术以高吞吐量服务 LLM。用于部署生产级 LLM API、优化推理延迟/吞吐量，或在 GPU 内存有限的情况下服务模型。支持 OpenAI 兼容的... | `mlops/inference/vllm` |
| [`weights-and-biases`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-weights-and-biases) | 使用自动日志记录跟踪 ML 实验，实时可视化训练过程，通过扫描优化超参数，并使用 W&B（协作式 MLOps 平台）管理模型注册表 | `mlops/evaluation/weights-and-biases` |

## note-taking

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) | 在 Obsidian 知识库中读取、搜索和创建笔记。 | `note-taking/obsidian` |

## productivity

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) | 为 Hermes 提供 Gmail、Calendar、Drive、Contacts、Sheets 和 Docs 集成。使用 Hermes 管理的 OAuth2 设置，优先使用 Google Workspace CLI (`gws`) 以获得更广泛的 API 覆盖，并回退到 Python 客户端库... | `productivity/google-workspace` |
| [`linear`](/docs/user-guide/skills/bundled/productivity/productivity-linear) | 通过 GraphQL API 管理 Linear 问题、项目和团队。创建、更新、搜索和组织问题。使用 API 密钥认证（无需 OAuth）。所有操作均通过 curl 执行 — 无依赖项。 | `productivity/linear` |
| [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps) | 位置智能 — 地理编码地点、反向地理编码坐标、查找附近地点（46 个 POI 类别）、驾驶/步行/骑行距离 + 时间、逐向导航、时区查询、命名地点的边界框 + 面积，以及 P... | `productivity/maps` |
| [`nano-pdf`](/docs/user-guide/skills/bundled/productivity/productivity-nano-pdf) | 使用 nano-pdf CLI 通过自然语言指令编辑 PDF。修改文本、修正拼写错误、更新标题，并在无需手动编辑的情况下对特定页面进行内容更改。 | `productivity/nano-pdf` |
| [`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) | 用于通过 curl 创建和管理页面、数据库和块的 Notion API。直接从终端搜索、创建、更新和查询 Notion 工作区。 | `productivity/notion` |
| [`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) | 从 PDF 和扫描文档中提取文本。对远程 URL 使用 web_extract，对本地基于文本的 PDF 使用 pymupdf，对 OCR/扫描文档使用 marker-pdf。对于 DOCX 使用 python-docx，对于 PPTX 请参阅 powerpoint 技能。 | `productivity/ocr-and-documents` |
| [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) | 任何涉及 .pptx 文件的方式（作为输入、输出或两者）时，都可以使用此技能。这包括：创建幻灯片、演示文稿或推介材料；读取、解析或从任何 .pptx 文件中提取文本（即使提取的... | `productivity/powerpoint` |
## 红队测试

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`godmode`](/docs/user-guide/skills/bundled/red-teaming/red-teaming-godmode) | 使用 G0DM0D3 技术越狱 API 服务的 LLM —— Parseltongue 输入混淆（33 种技术）、GODMODE CLASSIC 系统提示词模板、ULTRAPLINIAN 多模型竞速、编码升级，以及 Hermes 原生的预填充/系统提示词 i... | `red-teaming/godmode` |

## 研究

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) | 使用 arXiv 的免费 REST API 搜索和检索学术论文。无需 API 密钥。可通过关键词、作者、类别或 ID 进行搜索。可与 web_extract 或 ocr-and-documents 技能结合以阅读完整的论文内容。 | `research/arxiv` |
| [`blogwatcher`](/docs/user-guide/skills/bundled/research/research-blogwatcher) | 使用 blogwatcher-cli 工具监控博客和 RSS/Atom 源以获取更新。添加博客、扫描新文章、跟踪阅读状态并按类别筛选。 | `research/blogwatcher` |
| [`llm-wiki`](/docs/user-guide/skills/bundled/research/research-llm-wiki) | Karpathy 的 LLM Wiki —— 构建和维护一个持久化、相互链接的 Markdown 知识库。摄取来源、查询编译后的知识并进行一致性检查。 | `research/llm-wiki` |
| [`polymarket`](/docs/user-guide/skills/bundled/research/research-polymarket) | 查询 Polymarket 预测市场数据 —— 搜索市场、获取价格、订单簿和价格历史。通过公共 REST API 只读访问，无需 API 密钥。 | `research/polymarket` |
| [`research-paper-writing`](/docs/user-guide/skills/bundled/research/research-research-paper-writing) | 用于撰写 ML/AI 研究论文的端到端流水线 —— 从实验设计到分析、起草、修订和提交。涵盖 NeurIPS、ICML、ICLR、ACL、AAAI、COLM。集成了自动化实验监控、统计分析... | `research/research-paper-writing` |

## 智能家居

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`openhue`](/docs/user-guide/skills/bundled/smart-home/smart-home-openhue) | 通过 OpenHue CLI 控制 Philips Hue 灯、房间和场景。开关灯、调整亮度、颜色、色温以及激活场景。 | `smart-home/openhue` |

## 社交媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) | 通过 xurl（官方 X API CLI）与 X/Twitter 交互。用于发帖、回复、引用、搜索、时间线、提及、点赞、转发、书签、关注、私信、媒体上传和原始 v2 端点访问。 | `social-media/xurl` |

## 软件开发

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) | Hermes 的计划模式 —— 检查上下文，将 Markdown 计划写入活动工作区的 `.hermes/plans/` 目录，但不执行工作。 | `software-development/plan` |
| [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | 预提交验证流水线 —— 静态安全扫描、基于基线的质量门控、独立评审员子代理和自动修复循环。在代码更改后、提交、推送或打开 PR 之前使用。 | `software-development/requesting-code-review` |
| [`subagent-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) | 在执行具有独立任务的实施计划时使用。为每个任务分派新的 delegate_task，并进行两阶段评审（规范符合性评审，然后是代码质量评审）。 | `software-development/subagent-driven-development` |
| [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 在遇到任何错误、测试失败或意外行为时使用。4 阶段根本原因调查 —— 在未首先理解问题之前不进行修复。 | `software-development/systematic-debugging` |
| [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) | 在实现任何功能或错误修复时，在编写实现代码之前使用。通过测试优先的方法强制执行 RED-GREEN-REFACTOR 循环。 | `software-development/test-driven-development` |
| [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans) | 当您拥有多步骤任务的规范或需求时使用。创建包含易于处理的任务、确切文件路径和完整代码示例的全面实施计划。 | `software-development/writing-plans` |