---
sidebar_position: 5
title: "内置技能目录"
description: "Hermes Agent 附带的内置技能目录"
---

# 内置技能目录

Hermes 附带一个大型内置技能库，安装时会复制到 `~/.hermes/skills/` 目录。本页面记录了位于仓库 `skills/` 目录下的内置技能。

## apple

Apple/macOS 特定技能 — iMessage、提醒事项、备忘录、查找以及 macOS 自动化。这些技能仅在 macOS 系统上加载。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `apple-notes` | 在 macOS 上通过 memo CLI 管理 Apple 备忘录（创建、查看、搜索、编辑）。 | `apple/apple-notes` |
| `apple-reminders` | 通过 remindctl CLI 管理 Apple 提醒事项（列出、添加、完成、删除）。 | `apple/apple-reminders` |
| `findmy` | 在 macOS 上使用 AppleScript 和屏幕截图，通过 FindMy.app 追踪 Apple 设备和 AirTag。 | `apple/findmy` |
| `imessage` | 在 macOS 上通过 imsg CLI 发送和接收 iMessage/SMS。 | `apple/imessage` |

## autonomous-ai-agents

用于生成和编排自主 AI 编程 Agent 及多 Agent 工作流的技能 — 运行独立的 Agent 进程、委派任务以及协调并行工作流。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `claude-code` | 将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）。用于构建功能、重构、PR 审查和迭代式编码。需要安装 claude CLI。 | `autonomous-ai-agents/claude-code` |
| `codex` | 将编码任务委派给 OpenAI Codex CLI Agent。用于构建功能、重构、PR 审查和批量问题修复。需要安装 codex CLI 和一个 git 仓库。 | `autonomous-ai-agents/codex` |
| `hermes-agent-spawning` | 将额外的 Hermes Agent 实例作为自主子进程生成，用于独立的长期运行任务。支持非交互式单次运行模式（-q）和用于多轮协作的交互式 PTY 模式。与 delegate_task 不同 — 这会运行一个完全独立的 hermes 进程。 | `autonomous-ai-agents/hermes-agent` |
| `opencode` | 将编码任务委派给 OpenCode CLI Agent，用于功能实现、重构、PR 审查和长期运行的自主会话。需要安装并认证 opencode CLI。 | `autonomous-ai-agents/opencode` |

## data-science

用于数据科学工作流的技能 — 交互式探索、Jupyter 笔记本、数据分析和可视化。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `jupyter-live-kernel` | 通过 hamelnb 使用实时 Jupyter 内核进行有状态的、迭代式的 Python 执行。当任务涉及探索、迭代或检查中间结果时加载此技能。 | `data-science/jupyter-live-kernel` |

## creative

创意内容生成 — ASCII 艺术、手绘风格图表和视觉设计工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `ascii-art` | 使用 pyfiglet（571 种字体）、cowsay、boxes、toilet、image-to-ascii、远程 API（asciified, ascii.co.uk）和 LLM 后备方案生成 ASCII 艺术。无需 API 密钥。 | `creative/ascii-art` |
| `ascii-video` | "ASCII 艺术视频的生产流水线 — 支持任何格式。将视频/音频/图像/生成式输入转换为彩色 ASCII 字符视频输出（MP4、GIF、图像序列）。涵盖：视频到 ASCII 转换、音频响应式音乐可视化、生成式 ASCII 艺术动画、混合… | `creative/ascii-video` |
| `excalidraw` | 使用 Excalidraw JSON 格式创建手绘风格图表。生成 .excalidraw 文件，用于架构图、流程图、序列图、概念图等。文件可在 excalidraw.com 打开或上传以获取可分享链接。 | `creative/excalidraw` |
| `p5js` | 使用 p5.js 进行交互式和生成式视觉艺术的生产流水线。创建草图，通过无头浏览器将其渲染为图像/视频，并提供实时预览。支持画布动画、数据可视化和创意编码实验。 | `creative/p5js` |

## devops

DevOps 和基础设施自动化技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `webhook-subscriptions` | 为事件驱动的 Agent 激活创建和管理 Webhook 订阅。外部服务（GitHub、Stripe、CI/CD、IoT）POST 事件以触发 Agent 运行。需要启用 webhook 平台。 | `devops/webhook-subscriptions` |

## dogfood

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `dogfood` | 对 Web 应用程序进行系统性的探索性 QA 测试 — 发现错误、捕获证据并生成结构化报告。 | `dogfood/dogfood` |
| `hermes-agent-setup` | 帮助用户配置 Hermes Agent — CLI 使用、设置向导、模型/提供商选择、工具、技能、语音/STT/TTS、消息网关和故障排除。 | `dogfood/hermes-agent-setup` |

## email

用于从终端发送、接收、搜索和管理电子邮件的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `himalaya` | 通过 IMAP/SMTP 管理电子邮件的 CLI。使用 himalaya 从终端列出、读取、撰写、回复、转发、搜索和组织电子邮件。支持多账户和使用 MML（MIME 元语言）撰写消息。 | `email/himalaya` |

## gaming

用于设置、配置和管理游戏服务器、模组包以及游戏相关基础设施的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `minecraft-modpack-server` | 从 CurseForge/Modrinth 服务器包 zip 文件设置一个模组化 Minecraft 服务器。涵盖 NeoForge/Forge 安装、Java 版本、JVM 调优、防火墙、局域网配置、备份和启动脚本。 | `gaming/minecraft-modpack-server` |
| `pokemon-player` | 通过无头模拟自主玩宝可梦游戏。启动游戏服务器，从 RAM 读取结构化游戏状态，做出战略决策，并发送按钮输入 — 全部在终端中完成。 | `gaming/pokemon-player` |

## github

使用 gh CLI 和 git 通过终端管理仓库、拉取请求、代码审查、问题和 CI/CD 流水线的 GitHub 工作流技能。
| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `codebase-inspection` | 使用 pygount 检查和分析代码库，进行代码行数统计、语言分类以及代码与注释比例分析。当被要求检查代码行数、仓库大小、语言构成或代码库统计信息时使用。 | `github/codebase-inspection` |
| `github-auth` | 使用 git（通用可用）或 gh CLI 为 Agent 设置 GitHub 身份验证。涵盖 HTTPS 令牌、SSH 密钥、凭证助手和 gh auth —— 包含一个检测流程以自动选择正确的方法。 | `github/github-auth` |
| `github-code-review` | 通过分析 git diff 来审查代码变更，在 PR 上留下行内评论，并进行彻底的推送前审查。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 调用 GitHub REST API。 | `github/github-code-review` |
| `github-issues` | 创建、管理、分类和关闭 GitHub issue。搜索现有 issue、添加标签、分配人员并链接到 PR。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 调用 GitHub REST API。 | `github/github-issues` |
| `github-pr-workflow` | 完整的拉取请求生命周期 —— 创建分支、提交更改、打开 PR、监控 CI 状态、自动修复失败并合并。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 调用 GitHub REST API。 | `github/github-pr-workflow` |
| `github-repo-management` | 克隆、创建、分叉、配置和管理 GitHub 仓库。管理远程仓库、密钥、发布和工作流。可与 gh CLI 配合使用，或回退到使用 git + 通过 curl 调用 GitHub REST API。 | `github/github-repo-management` |

## inference-sh

通过 inference.sh 云平台执行 AI 应用的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `inference-sh-cli` | 通过 inference.sh CLI (infsh) 运行 150 多个 AI 应用 —— 图像生成、视频创作、LLM、搜索、3D、社交自动化。 | `inference-sh/cli` |

## leisure

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `find-nearby` | 使用 OpenStreetMap 查找附近地点（餐厅、咖啡馆、酒吧、药店等）。可使用坐标、地址、城市、邮政编码或 Telegram 位置标记。无需 API 密钥。 | `leisure/find-nearby` |

## mcp

用于处理 MCP（模型上下文协议）服务器、工具和集成的技能。包括内置的原生 MCP 客户端（在 config.yaml 中配置服务器以自动发现工具）以及用于临时服务器交互的 mcporter CLI 桥接器。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `mcporter` | 使用 mcporter CLI 直接列出、配置、授权和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。 | `mcp/mcporter` |
| `native-mcp` | 内置的 MCP（模型上下文协议）客户端，可连接到外部 MCP 服务器，发现其工具，并将其注册为 Hermes Agent 的原生工具。支持 stdio 和 HTTP 传输，具有自动重连、安全过滤和零配置工具注入功能。 | `mcp/native-mcp` |

## media

用于处理媒体内容的技能 —— YouTube 字幕、GIF 搜索、音乐生成和音频可视化。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `gif-search` | 使用 curl 从 Tenor 搜索和下载 GIF。除了 curl 和 jq 外没有其他依赖。适用于查找反应 GIF、创建视觉内容以及在聊天中发送 GIF。 | `media/gif-search` |
| `heartmula` | 设置并运行 HeartMuLa，这是一个开源音乐生成模型系列（类似 Suno）。根据歌词 + 标签生成完整歌曲，支持多语言。 | `media/heartmula` |
| `songsee` | 通过 CLI 从音频文件生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）。适用于音频分析、音乐制作调试和视觉文档记录。 | `media/songsee` |
| `youtube-content` | 获取 YouTube 视频字幕并将其转换为结构化内容（章节、摘要、线程、博客文章）。 | `media/youtube-content` |

## mlops

通用 ML 运维工具 —— 模型中心管理、数据集操作和工作流编排。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `huggingface-hub` | Hugging Face Hub CLI (hf) —— 搜索、下载和上传模型与数据集，管理仓库，部署推理端点。 | `mlops/huggingface-hub` |

## mlops/cloud

用于 ML 工作负载的 GPU 云提供商和无服务器计算平台。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `lambda-labs-gpu-cloud` | 用于 ML 训练和推理的预留和按需 GPU 云实例。当您需要具有简单 SSH 访问、持久文件系统或用于大规模训练的高性能多节点集群的专用 GPU 实例时使用。 | `mlops/cloud/lambda-labs` |
| `modal-serverless-gpu` | 用于运行 ML 工作负载的无服务器 GPU 云平台。当您需要按需 GPU 访问而无需基础设施管理、将 ML 模型部署为 API 或运行具有自动扩展的批处理作业时使用。 | `mlops/cloud/modal` |

## mlops/evaluation

模型评估基准、实验跟踪、数据整理、分词器和可解释性工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `evaluating-llms-harness` | 在 60 多个学术基准（MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）上评估 LLM。当对模型质量进行基准测试、比较模型、报告学术结果或跟踪训练进度时使用。EleutherAI、HuggingFace 和主要实验室使用的行业标准。Sup… | `mlops/evaluation/lm-evaluation-harness` |
| `huggingface-tokenizers` | 为研究和生产优化的快速分词器。基于 Rust 的实现可在 <20 秒内对 1GB 文本进行分词。支持 BPE、WordPiece 和 Unigram 算法。训练自定义词汇表、跟踪对齐、处理填充/截断。与 transformers 无缝集成。使用… | `mlops/evaluation/huggingface-tokenizers` |
| `nemo-curator` | 用于 LLM 训练的 GPU 加速数据整理。支持文本/图像/视频/音频。功能包括模糊去重（快 16 倍）、质量过滤（30 多个启发式规则）、语义去重、PII 编辑、NSFW 检测。使用 RAPIDS 跨 GPU 扩展。用于准备高质量 t… | `mlops/evaluation/nemo-curator` |
| `sparse-autoencoder-training` | 提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征。当发现可解释特征、分析叠加或研究语言模型中的单义表示时使用… | `mlops/evaluation/saelens` |
| `weights-and-biases` | 使用自动日志记录跟踪 ML 实验，实时可视化训练过程，通过扫描优化超参数，并使用 W&B（协作式 MLOps 平台）管理模型注册表 | `mlops/evaluation/weights-and-biases` |
## mlops/inference

模型服务、量化（GGUF/GPTQ）、结构化输出、推理优化和模型手术工具，用于部署和运行 LLM。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `gguf-quantization` | GGUF 格式和 llama.cpp 量化，用于高效的 CPU/GPU 推理。在消费级硬件、Apple Silicon 上部署模型，或需要灵活的 2-8 位量化且无需 GPU 时使用。 | `mlops/inference/gguf` |
| `guidance` | 使用正则表达式和语法控制 LLM 输出，保证有效的 JSON/XML/代码生成，强制执行结构化格式，并使用 Guidance（微软研究院的约束生成框架）构建多步骤工作流。 | `mlops/inference/guidance` |
| `instructor` | 使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，以类型安全的方式解析复杂的 JSON，并使用 Instructor（经过实战检验的结构化输出库）流式传输部分结果。 | `mlops/inference/instructor` |
| `llama-cpp` | 在 CPU、Apple Silicon 和消费级 GPU（无需 NVIDIA 硬件）上运行 LLM 推理。用于边缘部署、M1/M2/M3 Mac、AMD/Intel GPU 或 CUDA 不可用时。支持 GGUF 量化（1.5-8 位），可减少内存占用，在 CPU 上相比 PyTorch 提速 4-10 倍。 | `mlops/inference/llama-cpp` |
| `obliteratus` | 使用 OBLITERATUS（机制可解释性技术，包括 diff-in-means、SVD、白化 SVD、LEACE、SAE 分解等）移除开源权重 LLM 的拒绝行为，在保留推理能力的同时剔除护栏。包含 9 个 CLI 方法、28 个分析模块、116 个模型预设… | `mlops/inference/obliteratus` |
| `outlines` | 在生成过程中保证有效的 JSON/XML/代码结构，使用 Pydantic 模型实现类型安全的输出，支持本地模型（Transformers、vLLM），并使用 Outlines（dottxt.ai 的结构化生成库）最大化推理速度。 | `mlops/inference/outlines` |
| `serving-llms-vllm` | 使用 vLLM 的 PagedAttention 和连续批处理提供高吞吐量的 LLM 服务。用于部署生产级 LLM API、优化推理延迟/吞吐量，或在 GPU 内存有限的情况下服务模型。支持 OpenAI 兼容的端点、量化（GPTQ/AWQ/FP8），以及… | `mlops/inference/vllm` |
| `tensorrt-llm` | 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。用于在 NVIDIA GPU（A100/H100）上进行生产部署，需要比 PyTorch 快 10-100 倍的推理速度，或需要服务量化模型（FP8/INT4）、支持动态批处理和多重… | `mlops/inference/tensorrt-llm` |

## mlops/models

特定模型架构和工具——计算机视觉（CLIP、SAM、Stable Diffusion）、语音（Whisper）、音频生成（AudioCraft）和多模态模型（LLaVA）。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `audiocraft-audio-generation` | 用于音频生成的 PyTorch 库，包括文本到音乐（MusicGen）和文本到声音（AudioGen）。当需要根据文本描述生成音乐、创建音效或进行旋律条件音乐生成时使用。 | `mlops/models/audiocraft` |
| `clip` | OpenAI 的连接视觉和语言的模型。支持零样本图像分类、图文匹配和跨模态检索。在 4 亿个图文对上训练。用于图像搜索、内容审核或无需微调的视觉语言任务。最适合通用… | `mlops/models/clip` |
| `llava` | 大型语言和视觉助手。支持视觉指令微调和基于图像的对话。结合了 CLIP 视觉编码器和 Vicuna/LLaMA 语言模型。支持多轮图像聊天、视觉问答和指令跟随。用于视觉语言聊天… | `mlops/models/llava` |
| `segment-anything-model` | 用于图像分割的基础模型，支持零样本迁移。当需要使用点、框或掩码作为提示分割图像中的任何对象，或自动生成图像中所有对象掩码时使用。 | `mlops/models/segment-anything` |
| `stable-diffusion-image-generation` | 通过 HuggingFace Diffusers 使用 Stable Diffusion 模型进行最先进的文本到图像生成。用于根据文本提示生成图像、执行图像到图像转换、修复或构建自定义扩散流水线时使用。 | `mlops/models/stable-diffusion` |
| `whisper` | OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译成英语和语言识别。六种模型尺寸，从 tiny（3900 万参数）到 large（15.5 亿参数）。用于语音转文本、播客转录或多语言音频处理… | `mlops/models/whisper` |

## mlops/research

用于通过声明式编程构建和优化 AI 系统的 ML 研究框架。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `dspy` | 使用声明式编程构建复杂的 AI 系统，自动优化提示词，使用 DSPy（斯坦福 NLP 的系统化 LM 编程框架）创建模块化的 RAG 系统和 Agent。 | `mlops/research/dspy` |

## mlops/training

用于训练 LLM 和其他模型的微调、RLHF/DPO/GRPO 训练、分布式训练框架和优化工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `axolotl` | 使用 Axolotl 微调 LLM 的专家指导——YAML 配置、100+ 模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持。 | `mlops/training/axolotl` |
| `distributed-llm-pretraining-torchtitan` | 使用 torchtitan 提供 PyTorch 原生的分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）。当使用 8 到 512+ 个 GPU 大规模预训练 Llama 3.1、DeepSeek V3 或自定义模型，并需要 Float8、torch.compile 和分布式检查点时使用。 | `mlops/training/torchtitan` |
| `fine-tuning-with-trl` | 使用 TRL 通过强化学习微调 LLM——用于指令微调的 SFT、用于偏好对齐的 DPO、用于奖励优化的 PPO/GRPO，以及奖励模型训练。当需要 RLHF、使模型与偏好对齐或从人类反馈中训练时使用。与 HuggingFace Tr… | `mlops/training/trl-fine-tuning` |
| `grpo-rl-training` | 使用 TRL 进行 GRPO/RL 微调以实现推理和特定任务模型训练的专家指导。 | `mlops/training/grpo-rl-training` |
| `hermes-atropos-environments` | 为 Atropos 训练构建、测试和调试 Hermes Agent RL 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、Agent 循环集成、使用工具进行评估、wandb 日志记录以及三种 CLI 模式（serve/process/evaluate）。当创建、审查或修复… | `mlops/training/hermes-atropos-environments` |
| `huggingface-accelerate` | 最简单的分布式训练 API。只需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。DeepSpeed/FSDP/Megatron/DDP 的统一 API。自动设备放置、混合精度（FP16/BF16/FP8）。交互式配置，单一启动命令。HuggingFace 生态系统标准。 | `mlops/training/accelerate` |
| `optimizing-attention-flash` | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。当使用长序列（>512 Token）训练/运行 Transformer、遇到注意力机制的 GPU 内存问题或需要更快推理时使用。支持 PyTorch 原生 SDPA，… | `mlops/training/flash-attention` |
| `peft-fine-tuning` | 使用 LoRA、QLoRA 和 25+ 种方法对 LLM 进行参数高效微调。当 GPU 内存有限时微调大型模型（7B-70B）、需要训练 <1% 的参数且精度损失最小，或用于多适配器服务时使用。HuggingFace 的官方库，… | `mlops/training/peft` |
| `pytorch-fsdp` | 使用 PyTorch FSDP 进行完全分片数据并行训练的专家指导——参数分片、混合精度、CPU 卸载、FSDP2。 | `mlops/training/pytorch-fsdp` |
| `pytorch-lightning` | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统和最少的样板代码。使用相同代码可从笔记本电脑扩展到超级计算机。当需要内置最佳实践的简洁训练循环时使用。 | `mlops/training/pytorch-lightning` |
| `simpo-training` | 用于 LLM 对齐的简单偏好优化。DPO 的无参考替代方案，性能更优（在 AlpacaEval 2.0 上提升 +6.4 分）。无需参考模型，比 DPO/PPO 更高效。当需要比 DPO/PPO 更简单、更快速的偏好对齐训练时使用。 | `mlops/training/simpo` |
| `slime-rl-training` | 使用 slime（一个 Megatron+SGLang 框架）为 LLM 后训练提供 RL 指导。当训练 GLM 模型、实现自定义数据生成工作流，或需要紧密的 Megatron-LM 集成以进行 RL 扩展时使用。 | `mlops/training/slime` |
| `unsloth` | 使用 Unsloth 进行快速微调的专家指导——训练速度提升 2-5 倍，内存减少 50-80%，LoRA/QLoRA 优化。 | `mlops/training/unsloth` |
## mlops/vector-databases

用于 RAG、语义搜索和 AI 应用后端的向量相似性搜索和嵌入数据库。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `chroma` | 用于 AI 应用的开源嵌入数据库。存储嵌入和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。可从笔记本扩展到生产集群。用于语义搜索、RAG 应用或文档检索。最佳… | `mlops/vector-databases/chroma` |
| `faiss` | Facebook 的库，用于高效相似性搜索和密集向量聚类。支持数十亿向量、GPU 加速和各种索引类型（Flat、IVF、HNSW）。用于快速 k-NN 搜索、大规模向量检索，或当你需要纯相似性搜索而无需… | `mlops/vector-databases/faiss` |
| `pinecone` | 用于生产 AI 应用的托管向量数据库。完全托管、自动扩展，具有混合搜索（稠密 + 稀疏）、元数据过滤和命名空间。低延迟（&lt;100ms p95）。用于生产 RAG、推荐系统或大规模语义搜索。最适合服务器… | `mlops/vector-databases/pinecone` |
| `qdrant-vector-search` | 用于 RAG 和语义搜索的高性能向量相似性搜索引擎。当构建需要快速最近邻搜索、带过滤的混合搜索或具有 Rust 驱动性能的可扩展向量存储的生产 RAG 系统时使用。 | `mlops/vector-databases/qdrant` |

## note-taking

笔记技能，用于保存信息、协助研究，以及在多会话规划和信息共享中进行协作。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `obsidian` | 在 Obsidian 知识库中读取、搜索和创建笔记。 | `note-taking/obsidian` |

## productivity

用于文档创建、演示文稿、电子表格和其他生产力工作流的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `google-workspace` | 通过 Python 集成 Gmail、Calendar、Drive、Contacts、Sheets 和 Docs。使用 OAuth2 并自动刷新 Token。无需外部二进制文件——完全在 Hermes venv 中使用 Google 的 Python 客户端库运行。 | `productivity/google-workspace` |
| `linear` | 通过 GraphQL API 管理 Linear 问题、项目和团队。创建、更新、搜索和组织问题。 | `productivity/linear` |
| `nano-pdf` | 使用 nano-pdf CLI 通过自然语言指令编辑 PDF。修改文本、修复拼写错误、更新标题，并对特定页面进行内容更改，无需手动编辑。 | `productivity/nano-pdf` |
| `notion` | 用于通过 curl 创建和管理页面、数据库和块的 Notion API。直接从终端搜索、创建、更新和查询 Notion 工作区。 | `productivity/notion` |
| `ocr-and-documents` | 从 PDF 和扫描文档中提取文本。对远程 URL 使用 web_extract，对本地基于文本的 PDF 使用 pymupdf，对 OCR/扫描文档使用 marker-pdf。对于 DOCX 使用 python-docx，对于 PPTX 请参阅 powerpoint 技能。 | `productivity/ocr-and-documents` |
| `powerpoint` | "在任何涉及 .pptx 文件的情况下使用此技能——无论是作为输入、输出还是两者。这包括：创建幻灯片、演示文稿或宣传稿；从任何 .pptx 文件中读取、解析或提取文本（即使提取的内容将用于其他地方，例如在… | `productivity/powerpoint` |

## research

用于学术研究、论文发现、文献综述、领域侦察、市场数据、内容监控和科学知识检索的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `arxiv` | 使用其免费的 REST API 从 arXiv 搜索和检索学术论文。无需 API 密钥。按关键词、作者、类别或 ID 搜索。与 web_extract 或 ocr-and-documents 技能结合以阅读完整论文内容。 | `research/arxiv` |
| `blogwatcher` | 使用 blogwatcher CLI 监控博客和 RSS/Atom 源以获取更新。添加博客、扫描新文章并跟踪已读内容。 | `research/blogwatcher` |
| `llm-wiki` | Karpathy 的 LLM Wiki——构建和维护一个持久的、相互链接的 Markdown 知识库。摄取来源、查询编译后的知识并进行一致性检查。与 RAG 不同，该 wiki 一次性编译知识并保持其最新状态。可作为 Obsidian 知识库使用。可通过 `skills.config.wiki.path` 配置。 | `research/llm-wiki` |
| `domain-intel` | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查和批量多域名分析。无需 API 密钥。 | `research/domain-intel` |
| `duckduckgo-search` | 通过 DuckDuckGo 进行免费网络搜索——文本、新闻、图片、视频。无需 API 密钥。如果已安装，优先使用 `ddgs` CLI；仅在验证当前运行时环境中 `ddgs` 可用后，才使用 Python DDGS 库。 | `research/duckduckgo-search` |
| `ml-paper-writing` | 为 NeurIPS、ICML、ICLR、ACL、AAAI、COLM 撰写可发表的 ML/AI 论文。在从研究仓库起草论文、构建论点、验证引用或准备最终提交版本时使用。包括 LaTeX 模板、审稿人指南和引用验证… | `research/ml-paper-writing` |
| `polymarket` | 查询 Polymarket 预测市场数据——搜索市场、获取价格、订单簿和价格历史。通过公共 REST API 只读访问，无需 API 密钥。 | `research/polymarket` |

## red-teaming

用于 LLM 红队测试、越狱和安全过滤器绕过研究的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `godmode` | 使用 G0DM0D3 技术越狱 API 服务的 LLM——Parseltongue 输入混淆（33 种技术）、GODMODE CLASSIC 系统提示词模板、ULTRAPLINIAN 多模型竞赛、编码升级以及 Hermes 原生预填充/系统提示词集成。适用于任何可通过 API 访问的模型，包括闭源模型。 | `red-teaming/godmode` |

## smart-home
# 智能家居

控制智能家居设备的技能——灯光、开关、传感器和家庭自动化系统。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openhue` | 通过 OpenHue CLI 控制飞利浦 Hue 灯光、房间和场景。开关灯、调整亮度、颜色、色温以及激活场景。 | `smart-home/openhue` |

## 社交媒体

与社交平台交互的技能——发布、阅读、监控和账户操作。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `xitter` | 使用官方 X API 凭证，通过 x-cli 终端客户端与 X/Twitter 交互。 | `social-media/xitter` |

## 软件开发

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `code-review` | 以安全和质量为重点进行彻底代码审查的指南 | `software-development/code-review` |
| `plan` | Hermes 的计划模式——检查上下文，将 Markdown 计划写入活动工作区/后端工作目录的 `.hermes/plans/` 中，但不执行工作。 | `software-development/plan` |
| `requesting-code-review` | 在完成任务、实现主要功能或合并前使用。通过系统化的审查流程验证工作是否符合要求。 | `software-development/requesting-code-review` |
| `subagent-driven-development` | 在执行具有独立任务的实施计划时使用。为每个任务分派新的 delegate_task，并进行两阶段审查（规范符合性，然后是代码质量）。 | `software-development/subagent-driven-development` |
| `systematic-debugging` | 在遇到任何错误、测试失败或意外行为时使用。4 阶段根本原因调查——在理解问题之前不进行修复。 | `software-development/systematic-debugging` |
| `test-driven-development` | 在实现任何功能或错误修复时，在编写实现代码之前使用。通过测试优先的方法强制执行 RED-GREEN-REFACTOR 循环。 | `software-development/test-driven-development` |
| `writing-plans` | 当您有多步骤任务的规范或需求时使用。创建包含小任务、确切文件路径和完整代码示例的全面实施计划。 | `software-development/writing-plans` |

---

# 可选技能

可选技能随仓库提供，位于 `optional-skills/` 下，但**默认不激活**。它们涵盖较重或小众的用例。使用以下命令安装：

```bash
hermes skills install official/<category>/<skill>
```

## 自主 AI Agent

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blackbox` | 将编码任务委派给 Blackbox AI CLI Agent。这是一个具有内置评判器的多模型 Agent，通过多个 LLM 运行任务并选择最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 | `autonomous-ai-agents/blackbox` |

## 区块链

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `base` | 使用美元定价查询 Base（以太坊 L2）区块链数据——钱包余额、Token 信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络统计。使用 Base RPC + CoinGecko。无需 API 密钥。 | `blockchain/base` |
| `solana` | 使用美元定价查询 Solana 区块链数据——钱包余额、带价值的 Token 投资组合、交易详情、NFT、巨鲸检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 | `blockchain/solana` |

## 创意

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blender-mcp` | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。 | `creative/blender-mcp` |
| `meme-generation` | 通过选择模板并使用 Pillow 叠加文本来生成真实的 meme 图像。生成实际的 .png meme 文件。 | `creative/meme-generation` |

## 运维

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `docker-management` | 管理 Docker 容器、镜像、卷、网络和 Compose 堆栈——生命周期操作、调试、清理和 Dockerfile 优化。 | `devops/docker-management` |

## 电子邮件

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `agentmail` | 通过 AgentMail 为 Agent 提供其专用的电子邮件收件箱。使用 Agent 拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 | `email/agentmail` |

## 健康

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `neuroskill-bci` | 连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40 多个衍生的 EXG 分数）纳入响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）和 NeuroSkill 桌面应用程序。 | `health/neuroskill-bci` |

## MCP

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `fastmcp` | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。在创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、暴露资源或提示词，或准备 FastMCP 服务器进行 HTTP 部署时使用。 | `mcp/fastmcp` |

## 迁移

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openclaw-migration` | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent 中。从 ~/.openclaw 导入与 Hermes 兼容的记忆、SOUL.md、命令允许列表、用户技能和选定的工作区资产，然后报告无法迁移的内容及原因。 | `migration/openclaw-migration` |

## 生产力

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `telephony` | 为 Hermes 提供电话功能——配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，直接拨打电话，以及通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。 | `productivity/telephony` |

## 研究

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `bioinformatics` | 通往来自 bioSkills 和 ClawBio 的 400 多个生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等。 | `research/bioinformatics` |
| `qmd` | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录——这是一个结合了 BM25、向量搜索和 LLM 重排的混合检索引擎。支持 CLI 和 MCP 集成。 | `research/qmd` |
## 安全

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `1password` | 设置和使用 1Password CLI (op)。用于安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥。 | `security/1password` |
| `oss-forensics` | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖已删除提交恢复、强制推送检测、IOC 提取、多源证据收集和结构化取证报告。 | `security/oss-forensics` |
| `sherlock` | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 | `security/sherlock` |