---
title: "分布式 LLM 预训练 Torchtitan"
sidebar_label: "分布式 LLM 预训练 Torchtitan"
description: "使用 torchtitan 提供 PyTorch 原生的分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 分布式 LLM 预训练 Torchtitan

使用 torchtitan 提供 PyTorch 原生的分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）。适用于在 8 到 512+ 个 GPU 上大规模预训练 Llama 3.1、DeepSeek V3 或自定义模型，支持 Float8、torch.compile 和分布式检查点。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/torchtitan` 安装 |
| 路径 | `optional-skills/mlops/torchtitan` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `torch>=2.6.0`, `torchtitan>=0.2.0`, `torchao>=0.5.0` |
| 标签 | `模型架构`, `分布式训练`, `TorchTitan`, `FSDP2`, `张量并行`, `流水线并行`, `上下文并行`, `Float8`, `Llama`, `预训练` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# TorchTitan - PyTorch 原生分布式 LLM 预训练

## 快速开始

TorchTitan 是 PyTorch 官方的大规模 LLM 预训练平台，支持可组合的 4D 并行（FSDP2、TP、PP、CP），在 H100 GPU 上相比基线实现 65%+ 的加速。

**安装**：
```bash
# 从 PyPI 安装（稳定版）
pip install torchtitan

# 从源码安装（最新功能，需要 PyTorch nightly）
git clone https://github.com/pytorch/torchtitan
cd torchtitan
pip install -r requirements.txt
```

**下载分词器**：
```bash
# 从 https://huggingface.co/settings/tokens 获取 HF Token
python scripts/download_hf_assets.py --repo_id meta-llama/Llama-3.1-8B --assets tokenizer --hf_token=...
```

**在 8 个 GPU 上开始训练**：
```bash
CONFIG_FILE="./torchtitan/models/llama3/train_configs/llama3_8b.toml" ./run_train.sh
```

## 常见工作流

### 工作流 1：在单节点上预训练 Llama 3.1 8B

复制此清单：

```
单节点预训练：
- [ ] 步骤 1：下载分词器
- [ ] 步骤 2：配置训练
- [ ] 步骤 3：启动训练
- [ ] 步骤 4：监控和检查点
```

**步骤 1：下载分词器**

```bash
python scripts/download_hf_assets.py \
  --repo_id meta-llama/Llama-3.1-8B \
  --assets tokenizer \
  --hf_token=YOUR_HF_TOKEN
```

**步骤 2：配置训练**

编辑或创建 TOML 配置文件：

```toml
# llama3_8b_custom.toml
[job]
dump_folder = "./outputs"
description = "Llama 3.1 8B training"

[model]
name = "llama3"
flavor = "8B"
hf_assets_path = "./assets/hf/Llama-3.1-8B"

[optimizer]
name = "AdamW"
lr = 3e-4

[lr_scheduler]
warmup_steps = 200

[training]
local_batch_size = 2
seq_len = 8192
max_norm = 1.0
steps = 1000
dataset = "c4"

[parallelism]
data_parallel_shard_degree = -1  # 使用所有 GPU 进行 FSDP

[activation_checkpoint]
mode = "selective"
selective_ac_option = "op"

[checkpoint]
enable = true
folder = "checkpoint"
interval = 500
```

**步骤 3：启动训练**

```bash
# 单节点 8 个 GPU
CONFIG_FILE="./llama3_8b_custom.toml" ./run_train.sh

# 或显式使用 torchrun
torchrun --nproc_per_node=8 \
  -m torchtitan.train \
  --job.config_file ./llama3_8b_custom.toml
```

**步骤 4：监控和检查点**

TensorBoard 日志保存到 `./outputs/tb/`：
```bash
tensorboard --logdir ./outputs/tb
```

### 工作流 2：使用 SLURM 进行多节点训练

```
多节点训练：
- [ ] 步骤 1：为扩展配置并行策略
- [ ] 步骤 2：设置 SLURM 脚本
- [ ] 步骤 3：提交作业
- [ ] 步骤 4：从检查点恢复
```

**步骤 1：为扩展配置并行策略**

对于 256 个 GPU（32 个节点）上的 70B 模型：
```toml
[parallelism]
data_parallel_shard_degree = 32  # 跨 32 个 rank 的 FSDP
tensor_parallel_degree = 8        # 节点内的 TP
pipeline_parallel_degree = 1      # 70B 模型不使用 PP
context_parallel_degree = 1       # 对于长序列可增加
```

**步骤 2：设置 SLURM 脚本**

```bash
#!/bin/bash
#SBATCH --job-name=llama70b
#SBATCH --nodes=32
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-node=8

srun torchrun \
  --nnodes=32 \
  --nproc_per_node=8 \
  --rdzv_backend=c10d \
  --rdzv_endpoint=$MASTER_ADDR:$MASTER_PORT \
  -m torchtitan.train \
  --job.config_file ./llama3_70b.toml
```

**步骤 3：提交作业**

```bash
sbatch multinode_trainer.slurm
```

**步骤 4：从检查点恢复**

如果配置的文件夹中存在检查点，训练会自动恢复。

### 工作流 3：为 H100 启用 Float8 训练

Float8 在 H100 GPU 上可提供 30-50% 的加速。

```
Float8 训练：
- [ ] 步骤 1：安装 torchao
- [ ] 步骤 2：配置 Float8
- [ ] 步骤 3：使用编译启动
```

**步骤 1：安装 torchao**

```bash
USE_CPP=0 pip install git+https://github.com/pytorch/ao.git
```

**步骤 2：配置 Float8**

添加到你的 TOML 配置中：
```toml
[model]
converters = ["quantize.linear.float8"]

[quantize.linear.float8]
enable_fsdp_float8_all_gather = true
precompute_float8_dynamic_scale_for_fsdp = true
filter_fqns = ["output"]  # 排除输出层

[compile]
enable = true
components = ["model", "loss"]
```

**步骤 3：使用编译启动**

```bash
CONFIG_FILE="./llama3_8b.toml" ./run_train.sh \
  --model.converters="quantize.linear.float8" \
  --quantize.linear.float8.enable_fsdp_float8_all_gather \
  --compile.enable
```

### 工作流 4：针对 405B 模型的 4D 并行

```
4D 并行（FSDP + TP + PP + CP）：
- [ ] 步骤 1：创建种子检查点
- [ ] 步骤 2：配置 4D 并行
- [ ] 步骤 3：在 512 个 GPU 上启动
```

**步骤 1：创建种子检查点**

跨 PP 阶段进行一致初始化所需：
```bash
NGPU=1 CONFIG_FILE=./llama3_405b.toml ./run_train.sh \
  --checkpoint.enable \
  --checkpoint.create_seed_checkpoint \
  --parallelism.data_parallel_shard_degree 1 \
  --parallelism.tensor_parallel_degree 1 \
  --parallelism.pipeline_parallel_degree 1
```

**步骤 2：配置 4D 并行**

```toml
[parallelism]
data_parallel_shard_degree = 8   # FSDP
tensor_parallel_degree = 8       # 节点内的 TP
pipeline_parallel_degree = 8     # 跨节点的 PP
context_parallel_degree = 1      # 用于长序列的 CP

[training]
local_batch_size = 32
seq_len = 8192
```

**步骤 3：在 512 个 GPU 上启动**

```bash
# 64 个节点 x 8 个 GPU = 512 个 GPU
srun torchrun --nnodes=64 --nproc_per_node=8 \
  -m torchtitan.train \
  --job.config_file ./llama3_405b.toml
```

## 何时使用 vs 替代方案

**在以下情况使用 TorchTitan：**
- 从头开始预训练 LLM（8B 到 405B+）
- 需要无需第三方依赖的 PyTorch 原生解决方案
- 需要可组合的 4D 并行（FSDP2、TP、PP、CP）
- 在支持 Float8 的 H100 上进行训练
- 希望获得与 torchtune/HuggingFace 可互操作的检查点

**在以下情况使用替代方案：**
- **Megatron-LM**：针对纯 NVIDIA 部署追求极致性能
- **DeepSpeed**：更广泛的 ZeRO 优化生态系统，支持推理
- **Axolotl/TRL**：用于微调而非预训练
- **LitGPT**：用于教育目的、小规模训练

## 常见问题

**问题：大模型内存不足**

启用激活检查点并减小批次大小：
```toml
[activation_checkpoint]
mode = "full"  # 替代 "selective"

[training]
local_batch_size = 1
```

或使用梯度累积：
```toml
[training]
local_batch_size = 1
global_batch_size = 32  # 累积梯度
```

**问题：TP 导致异步集合通信内存过高**

设置环境变量：
```bash
export TORCH_NCCL_AVOID_RECORD_STREAMS=1
```

**问题：Float8 训练没有更快**

Float8 仅对大型 GEMM 有益。过滤小层：
```toml
[quantize.linear.float8]
filter_fqns = ["attention.wk", "attention.wv", "output", "auto_filter_small_kn"]
```

**问题：并行策略更改后检查点加载失败**

使用 DCP 的重分片能力：
```bash
# 将分片检查点转换为单个文件
python -m torch.distributed.checkpoint.format_utils \
  dcp_to_torch checkpoint/step-1000 checkpoint.pt
```

**问题：流水线并行初始化**

首先创建种子检查点（参见工作流 4，步骤 1）。

## 支持的模型

| 模型 | 尺寸 | 状态 |
|-------|-------|--------|
| Llama 3.1 | 8B, 70B, 405B | 生产就绪 |
| Llama 4 | 多种 | 实验性 |
| DeepSeek V3 | 16B, 236B, 671B (MoE) | 实验性 |
| GPT-OSS | 20B, 120B (MoE) | 实验性 |
| Qwen 3 | 多种 | 实验性 |
| Flux | 扩散模型 | 实验性 |

## 性能基准（H100）

| 模型 | GPU 数量 | 并行策略 | TPS/GPU | 技术 |
|-------|------|-------------|---------|------------|
| Llama 8B | 8 | FSDP | 5,762 | 基线 |
| Llama 8B | 8 | FSDP+compile+FP8 | 8,532 | +48% |
| Llama 70B | 256 | FSDP+TP+AsyncTP | 876 | 2D 并行 |
| Llama 405B | 512 | FSDP+TP+PP | 128 | 3D 并行 |

## 高级主题

**FSDP2 配置**：参见 [references/fsdp.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/torchtitan/references/fsdp.md) 了解详细的 FSDP2 与 FSDP1 对比以及 ZeRO 等效配置。

**Float8 训练**：参见 [references/float8.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/torchtitan/references/float8.md) 了解张量级与行级缩放方案。

**检查点**：参见 [references/checkpoint.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/torchtitan/references/checkpoint.md) 了解 HuggingFace 转换和异步检查点。

**添加自定义模型**：参见 [references/custom-models.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/torchtitan/references/custom-models.md) 了解 TrainSpec 协议。

## 资源

- GitHub：https://github.com/pytorch/torchtitan
- 论文：https://arxiv.org/abs/2410.06511
- ICLR 2025：https://iclr.cc/virtual/2025/poster/29620
- PyTorch 论坛：https://discuss.pytorch.org/c/distributed/torchtitan/44