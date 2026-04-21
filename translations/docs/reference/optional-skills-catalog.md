---
sidebar_position: 9
title: "可选技能目录"
description: "hermes-agent 附带的官方可选技能 — 通过 hermes skills install official/<category>/<skill> 安装"
---

# 可选技能目录

官方可选技能随 hermes-agent 仓库一同发布，位于 `optional-skills/` 目录下，但**默认不激活**。需要显式安装它们：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

安装后，该技能会出现在 Agent 的技能列表中，并在检测到相关任务时自动加载。

卸载方法：

```bash
hermes skills uninstall <skill-name>
```

---

## 自主 AI Agent

| 技能 | 描述 |
|-------|-------------|
| **blackbox** | 将编码任务委派给 Blackbox AI CLI agent。这是一个多模型 Agent，内置评判器，可通过多个 LLM 运行任务并选取最佳结果。 |
| **honcho** | 在 Hermes 中配置和使用 Honcho 记忆 — 跨会话用户建模、多配置文件对等隔离、观察配置和辩证推理。 |

## 区块链

| 技能 | 描述 |
|-------|-------------|
| **base** | 查询 Base（以太坊 L2）区块链数据，附带美元计价 — 钱包余额、Token 信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络统计。无需 API 密钥。 |
| **solana** | 查询 Solana 区块链数据，附带美元计价 — 钱包余额、Token 投资组合、交易详情、NFT、巨鲸检测和实时网络统计。无需 API 密钥。 |

## 通信

| 技能 | 描述 |
|-------|-------------|
| **one-three-one-rule** | 用于提案和决策的结构化沟通框架。 |

## 创意

| 技能 | 描述 |
|-------|-------------|
| **blender-mcp** | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。 |
| **concept-diagrams** | 生成扁平、极简、支持明暗模式的 SVG 图表，作为独立的 HTML 文件，使用统一的教育视觉语言（9 种语义色阶，自动深色模式）。最适合物理设置、化学机制、数学曲线、物理对象（飞机、涡轮机、智能手机）、平面图、横截面、生命周期/流程叙述以及中心辐射型系统图。附带 15 个示例图表。 |
| **meme-generation** | 通过选择模板并使用 Pillow 叠加文本来生成真实的 meme 图片。生成实际的 `.png` meme 文件。 |
| **touchdesigner-mcp** | 通过 twozero MCP 插件控制正在运行的 TouchDesigner 实例 — 创建操作器、设置参数、连接线路、执行 Python、构建实时音频反应式视觉效果和 GLSL 网络。包含 36 个原生工具。 |

## DevOps

| 技能 | 描述 |
|-------|-------------|
| **cli** | 通过 inference.sh CLI (infsh) 运行 150 多个 AI 应用 — 图像生成、视频创作、LLM、搜索、3D 和社交自动化。 |
| **docker-management** | 管理 Docker 容器、镜像、卷、网络和 Compose 堆栈 — 生命周期操作、调试、清理和 Dockerfile 优化。 |

## 电子邮件

| 技能 | 描述 |
|-------|-------------|
| **agentmail** | 通过 AgentMail 为 Agent 提供其专属的电子邮件收件箱。使用 Agent 拥有的电子邮件地址自主发送、接收和管理电子邮件。 |

## 健康

| 技能 | 描述 |
|-------|-------------|
| **fitness-nutrition** | 健身房锻炼计划制定和营养追踪器。通过 wger 按肌肉、设备或类别搜索 690 多种练习。通过 USDA FoodData Central 查找 380,000 多种食物的宏量营养素和卡路里。计算 BMI、TDEE、单次最大重复次数、宏量营养素分配和体脂率 — 纯 Python，无需 pip 安装。 |
| **neuroskill-bci** | 用于神经科学研究工作流的脑机接口集成。 |

## MCP

| 技能 | 描述 |
|-------|-------------|
| **fastmcp** | 在 Python 中使用 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。涵盖将 API 或数据库包装为 MCP 工具、暴露资源或提示词以及部署。 |
| **mcporter** | `mcporter` CLI — 直接从终端列出、配置、验证和调用 MCP 服务器/工具（HTTP 或 stdio）。适用于临时 MCP 交互；对于常驻工具发现，请改用内置的 `native-mcp` 客户端。 |

## 迁移

| 技能 | 描述 |
|-------|-------------|
| **openclaw-migration** | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。导入记忆、SOUL.md、命令白名单、用户技能和选定的工作区资产。 |

## MLOps

最大的可选类别 — 涵盖从数据整理到生产推理的完整 ML 流水线。

| 技能 | 描述 |
|-------|-------------|
| **accelerate** | 最简单的分布式训练 API。只需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。为 DeepSpeed/FSDP/Megatron/DDP 提供统一 API。 |
| **chroma** | 开源嵌入数据库。存储嵌入和元数据，执行向量和全文搜索。为 RAG 和语义搜索提供简单的 4 函数 API。 |
| **clip** | OpenAI 连接图像和文本的视觉语言模型。零样本图像分类、图文匹配和跨模态检索。在 4 亿个图文对上训练。用于图像搜索、内容审核或无需微调的视觉语言任务。 |
| **faiss** | Facebook 用于高效相似性搜索和密集向量聚类的库。支持数十亿向量、GPU 加速和各种索引类型（Flat、IVF、HNSW）。 |
| **flash-attention** | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。支持 PyTorch SDPA、flash-attn 库、H100 FP8 和滑动窗口。 |
| **guidance** | 使用正则表达式和语法控制 LLM 输出，保证有效的 JSON/XML/代码生成，强制执行结构化格式，并使用 Guidance（微软研究的约束生成框架）构建多步骤工作流。 |
| **hermes-atropos-environments** | 为 Atropos 训练构建、测试和调试 Hermes Agent RL 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、Agent 循环集成和评估。 |
| **huggingface-tokenizers** | 用于研究和生产的基于 Rust 的快速分词器。在 20 秒内完成 1GB 文本分词。支持 BPE、WordPiece 和 Unigram 算法。 |
| **instructor** | 使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，并流式传输部分结果。 |
| **lambda-labs** | 用于 ML 训练和推理的预留和按需 GPU 云实例。提供 SSH 访问、持久文件系统和多节点集群。 |
| **llava** | 大型语言和视觉助手 — 结合 CLIP 视觉和 LLaMA 语言模型的视觉指令微调和基于图像的对话。 |
| **modal** | 用于运行 ML 工作负载的无服务器 GPU 云平台。无需基础设施管理即可按需访问 GPU，将 ML 模型部署为 API，或运行具有自动扩展功能的批处理作业。 |
| **nemo-curator** | 用于 LLM 训练的 GPU 加速数据整理。模糊去重（快 16 倍）、质量过滤（30 多种启发式方法）、语义去重、PII 编辑。通过 RAPIDS 扩展。 |
| **peft-fine-tuning** | 使用 LoRA、QLoRA 和 25 多种方法对 LLM 进行参数高效微调。在有限的 GPU 内存上，以最小的精度损失训练 `<1%` 的参数，适用于 7B–70B 模型。HuggingFace 官方 PEFT 库。 |
| **pinecone** | 用于生产 AI 的托管向量数据库。自动扩展、混合搜索（稠密 + 稀疏）、元数据过滤和低延迟（p95 低于 100 毫秒）。 |
| **pytorch-fsdp** | 使用 PyTorch FSDP 进行全分片数据并行训练的专家指南 — 参数分片、混合精度、CPU 卸载、FSDP2。 |
| **pytorch-lightning** | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调函数和最少的样板代码。 |
| **qdrant** | 高性能向量相似性搜索引擎。基于 Rust，具有快速最近邻搜索、带过滤的混合搜索和可扩展的向量存储。 |
| **saelens** | 使用 SAELens 训练和分析稀疏自编码器，将神经网络激活分解为可解释的特征。 |
| **simpo** | 简单偏好优化 — 无需参考模型的 DPO 替代方案，性能更优（在 AlpacaEval 2.0 上 +6.4 分）。无需参考模型。 |
| **slime** | 使用 Megatron+SGLang 框架通过 RL 进行 LLM 后训练。自定义数据生成工作流和紧密的 Megatron-LM 集成，用于 RL 扩展。 |
| **stable-diffusion-image-generation** | 通过 HuggingFace Diffusers 使用 Stable Diffusion 进行最先进的文生图。文生图、图生图、修复和自定义扩散流水线。 |
| **tensorrt-llm** | 使用 NVIDIA TensorRT 优化 LLM 推理以实现最大吞吐量。在 A100/H100 上，通过量化（FP8/INT4）和动态批处理，比 PyTorch 快 10-100 倍。 |
| **torchtitan** | 使用 4D 并行（FSDP2、TP、PP、CP）进行 PyTorch 原生分布式 LLM 预训练。从 8 个 GPU 扩展到 512+ 个 GPU，支持 Float8 和 torch.compile。 |
| **whisper** | OpenAI 的通用语音识别。支持 99 种语言，提供转录、翻译成英语和语言识别功能。六种模型大小，从 tiny（3900 万参数）到 large（15.5 亿参数）。最适合稳健的多语言 ASR。 |
## 生产力

| 技能 | 描述 |
|-------|-------------|
| **canvas** | Canvas LMS 集成 — 使用 API Token 认证获取已注册课程和作业。 |
| **memento-flashcards** | 用于学习和知识保留的间隔重复闪卡系统。 |
| **siyuan** | SiYuan 笔记 API，用于在自托管知识库中搜索、阅读、创建和管理块与文档。 |
| **telephony** | 赋予 Hermes 电话能力 — 配置 Twilio 号码、发送/接收短信/彩信、拨打电话，并通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。 |

## 研究

| 技能 | 描述 |
|-------|-------------|
| **bioinformatics** | 通往来自 bioSkills 和 ClawBio 的 400 多种生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学和结构生物学。 |
| **domain-intel** | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录和批量多域名分析。无需 API 密钥。 |
| **duckduckgo-search** | 通过 DuckDuckGo 进行免费网络搜索 — 文本、新闻、图片、视频。无需 API 密钥。 |
| **gitnexus-explorer** | 使用 GitNexus 索引代码库，并通过 Web UI 和 Cloudflare 隧道提供交互式知识图谱。 |
| **parallel-cli** | Parallel CLI 的供应商技能 — 面向 Agent 的原生网络搜索、提取、深度研究、信息丰富和监控。 |
| **qmd** | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 — 一个结合了 BM25、向量搜索和 LLM 重排的混合检索引擎。 |
| **scrapling** | 使用 Scrapling 进行网页抓取 — HTTP 获取、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 进行蜘蛛爬取。 |

## 安全

| 技能 | 描述 |
|-------|-------------|
| **1password** | 设置和使用 1Password CLI (op)。安装 CLI、启用桌面应用集成、登录，并为命令读取/注入密钥。 |
| **oss-forensics** | 开源软件取证 — 分析软件包、依赖项和供应链风险。 |
| **sherlock** | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 |

---

## 贡献可选技能

要向仓库添加新的可选技能：

1.  在 `optional-skills/<category>/<skill-name>/` 下创建一个目录
2.  添加一个包含标准 frontmatter（名称、描述、版本、作者）的 `SKILL.md` 文件
3.  在 `references/`、`templates/` 或 `scripts/` 子目录中包含任何支持文件
4.  提交一个拉取请求 — 技能在合并后将出现在此目录中