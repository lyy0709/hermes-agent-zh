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
| **blackbox** | 将编码任务委派给 Blackbox AI CLI Agent。这是一个多模型 Agent，内置评判器，可通过多个 LLM 运行任务并选取最佳结果。 |
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
| **meme-generation** | 通过选择模板并使用 Pillow 叠加文本来生成真实的梗图。生成实际的 `.png` 梗图文件。 |

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
| **neuroskill-bci** | 用于神经科学研究工作流的脑机接口 (BCI) 集成。 |

## MCP

| 技能 | 描述 |
|-------|-------------|
| **fastmcp** | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。涵盖将 API 或数据库包装为 MCP 工具、暴露资源或提示词以及部署。 |

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
| **faiss** | Facebook 的高效相似性搜索和密集向量聚类库。支持数十亿向量、GPU 加速和各种索引类型（Flat, IVF, HNSW）。 |
| **flash-attention** | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。支持 PyTorch SDPA、flash-attn 库、H100 FP8 和滑动窗口。 |
| **hermes-atropos-environments** | 为 Atropos 训练构建、测试和调试 Hermes Agent RL 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、Agent 循环集成和评估。 |
| **huggingface-tokenizers** | 用于研究和生产的基于 Rust 的快速分词器。在 20 秒内完成 1GB 文本的分词。支持 BPE、WordPiece 和 Unigram 算法。 |
| **instructor** | 使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，并流式传输部分结果。 |
| **lambda-labs** | 用于 ML 训练和推理的预留和按需 GPU 云实例。提供 SSH 访问、持久文件系统和多节点集群。 |
| **llava** | 大型语言和视觉助手 — 视觉指令微调和基于图像的对话，结合了 CLIP 视觉和 LLaMA 语言模型。 |
| **nemo-curator** | 用于 LLM 训练的 GPU 加速数据整理。模糊去重（快 16 倍）、质量过滤（30 多种启发式方法）、语义去重、PII 脱敏。通过 RAPIDS 扩展。 |
| **pinecone** | 用于生产 AI 的托管向量数据库。自动扩展、混合搜索（稠密 + 稀疏）、元数据过滤和低延迟（p95 低于 100ms）。 |
| **pytorch-lightning** | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调函数和最少的样板代码。 |
| **qdrant** | 高性能向量相似性搜索引擎。由 Rust 驱动，具有快速最近邻搜索、带过滤的混合搜索和可扩展的向量存储。 |
| **saelens** | 使用 SAELens 训练和分析稀疏自编码器 (SAE)，将神经网络激活分解为可解释的特征。 |
| **simpo** | 简单偏好优化 — 无需参考模型的 DPO 替代方案，性能更优（在 AlpacaEval 2.0 上提升 +6.4 分）。无需参考模型。 |
| **slime** | 使用 Megatron+SGLang 框架通过 RL 进行 LLM 后训练。自定义数据生成工作流以及与 Megatron-LM 的紧密集成，以实现 RL 扩展。 |
| **tensorrt-llm** | 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量。在 A100/H100 上比 PyTorch 快 10-100 倍，支持量化（FP8/INT4）和动态批处理。 |
| **torchtitan** | 使用 4D 并行（FSDP2, TP, PP, CP）的 PyTorch 原生分布式 LLM 预训练。从 8 个 GPU 扩展到 512+ 个 GPU，支持 Float8 和 torch.compile。 |

## 生产力

| 技能 | 描述 |
|-------|-------------|
| **canvas** | Canvas LMS 集成 — 使用 API Token 认证获取已注册课程和作业。 |
| **memento-flashcards** | 用于学习和知识保留的间隔重复闪卡系统。 |
| **siyuan** | SiYuan 笔记 API，用于在自托管知识库中搜索、阅读、创建和管理块和文档。 |
| **telephony** | 为 Hermes 提供电话功能 — 配置 Twilio 号码、发送/接收短信/彩信、拨打电话，并通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。 |

## 研究

| 技能 | 描述 |
|-------|-------------|
| **bioinformatics** | 通往来自 bioSkills 和 ClawBio 的 400 多个生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学和结构生物学。 |
| **domain-intel** | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录和批量多域名分析。无需 API 密钥。 |
| **duckduckgo-search** | 通过 DuckDuckGo 进行免费网络搜索 — 文本、新闻、图片、视频。无需 API 密钥。 |
| **gitnexus-explorer** | 使用 GitNexus 为代码库建立索引，并通过 Web UI 和 Cloudflare 隧道提供交互式知识图谱。 |
| **parallel-cli** | Parallel CLI 的供应商技能 — Agent 原生网络搜索、提取、深度研究、丰富和监控。 |
| **qmd** | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 — 一个结合了 BM25、向量搜索和 LLM 重排的混合检索引擎。 |
| **scrapling** | 使用 Scrapling 进行网络爬取 — HTTP 获取、隐身浏览器自动化、Cloudflare 绕过以及通过 CLI 和 Python 进行蜘蛛爬取。 |

## 安全

| 技能 | 描述 |
|-------|-------------|
| **1password** | 设置和使用 1Password CLI (op)。安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥。 |
| **oss-forensics** | 开源软件取证 — 分析软件包、依赖项和供应链风险。 |
| **sherlock** | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 |

---

## 贡献可选技能

要向仓库添加新的可选技能：

1.  在 `optional-skills/<category>/<skill-name>/` 下创建目录
2.  添加一个包含标准 frontmatter（名称、描述、版本、作者）的 `SKILL.md` 文件
3.  在 `references/`、`templates/` 或 `scripts/` 子目录中包含任何支持文件
4.  提交拉取请求 — 技能在合并后将出现在此目录中