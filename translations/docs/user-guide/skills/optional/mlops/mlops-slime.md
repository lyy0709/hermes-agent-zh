---
title: "Slime Rl Training — 提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导"
sidebar_label: "Slime Rl Training"
description: "提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Slime Rl Training

提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 强化学习后训练的指导。适用于训练 GLM 模型、实现自定义数据生成工作流，或需要紧密的 Megatron-LM 集成以进行 RL 扩展的场景。

## 技能元数据

| | |
|---|---|
| 来源 | Optional — 使用 `hermes skills install official/mlops/slime` 安装 |
| 路径 | `optional-skills/mlops/slime` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `sglang-router>=0.2.3`, `ray`, `torch>=2.0.0`, `transformers>=4.40.0` |
| 标签 | `Reinforcement Learning`, `Megatron-LM`, `SGLang`, `GRPO`, `Post-Training`, `GLM` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# slime：用于 RL 扩展的 LLM 后训练框架

slime 是清华大学 THUDM 团队推出的 LLM 后训练框架，为 GLM-4.5、GLM-4.6 和 GLM-4.7 提供支持。它连接 Megatron-LM 进行训练，并使用 SGLang 进行高吞吐量的轨迹生成。

## 何时使用 slime

**在以下情况选择 slime：**
- 需要原生 Megatron-LM 训练与 SGLang 推理
- 需要具有灵活数据缓冲区的自定义数据生成工作流
- 训练 GLM、Qwen3、DeepSeek V3 或 Llama 3 模型
- 需要研究级框架并具备生产支持（Z.ai）

**在以下情况考虑替代方案：**
- 需要企业级稳定性功能 → 使用 **miles**
- 希望灵活切换后端 → 使用 **verl**
- 需要 PyTorch 原生抽象 → 使用 **torchforge**

## 主要特性

- **训练**：支持完全并行（TP、PP、DP、SP）的 Megatron-LM
- **轨迹生成**：基于 SGLang 的高吞吐量生成，带路由器
- **数据缓冲区**：灵活的提示词管理和样本存储
- **模型**：GLM-4.x、Qwen3、DeepSeek V3/R1、Llama 3

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    数据缓冲区                           │
│ - 提示词初始化和管理                                   │
│ - 自定义数据生成和过滤                                 │
│ - 轨迹样本存储                                         │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
┌─────────────▼───────────┐ ┌─────────────▼───────────────┐
│ 训练 (Megatron-LM)      │ │ 轨迹生成 (SGLang + 路由器)  │
│ - Actor 模型训练        │ │ - 响应生成                  │
│ - Critic（可选）        │ │ - 奖励/验证器输出           │
│ - 权重同步到轨迹生成    │ │ - 多轮对话支持              │
└─────────────────────────┘ └─────────────────────────────┘
```

## 安装

```bash
# 推荐：Docker
docker pull slimerl/slime:latest
docker run --rm --gpus all --ipc=host --shm-size=16g \
  -it slimerl/slime:latest /bin/bash

# 在容器内
cd /root/slime && pip install -e . --no-deps
```

### 从源码安装

```bash
git clone https://github.com/THUDM/slime.git
cd slime
pip install -r requirements.txt
pip install -e .
```

## 快速开始：GRPO 训练

```bash
# 源模型配置
source scripts/models/qwen3-4B.sh

# 启动训练
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 4 \
    --rollout-num-gpus 4 \
    --advantage-estimator grpo \
    --use-kl-loss --kl-loss-coef 0.001 \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --prompt-data /path/to/data.jsonl \
    ${MODEL_ARGS[@]} ${CKPT_ARGS[@]}
```

---

## 工作流 1：标准 GRPO 训练

使用此工作流训练具有组相对优势的推理模型。

### 先决条件清单
- [ ] Docker 环境或已安装 Megatron-LM + SGLang
- [ ] 模型检查点（HuggingFace 或 Megatron 格式）
- [ ] JSONL 格式的训练数据

### 步骤 1：准备数据

```python
# data.jsonl 格式
{"prompt": "What is 2 + 2?", "label": "4"}
{"prompt": "Solve: 3x = 12", "label": "x = 4"}
```

或使用聊天格式：
```python
{
    "prompt": [
        {"role": "system", "content": "You are a math tutor."},
        {"role": "user", "content": "What is 15 + 27?"}
    ],
    "label": "42"
}
```

### 步骤 2：配置模型

选择一个预配置的模型脚本：

```bash
# 列出可用模型
ls scripts/models/
# glm4-9B.sh, qwen3-4B.sh, qwen3-30B-A3B.sh, deepseek-v3.sh, llama3-8B.sh, ...

# 源化你的模型
source scripts/models/qwen3-4B.sh
```

### 步骤 3：启动训练

```bash
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --advantage-estimator grpo \
    --use-kl-loss \
    --kl-loss-coef 0.001 \
    --prompt-data /path/to/train.jsonl \
    --input-key prompt \
    --label-key label \
    --apply-chat-template \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --save-interval 100 \
    --eval-interval 50 \
    ${MODEL_ARGS[@]}
```

### 步骤 4：监控训练
- [ ] 检查 TensorBoard：`tensorboard --logdir outputs/`
- [ ] 验证奖励曲线是否上升
- [ ] 监控各节点的 GPU 利用率

---

## 工作流 2：异步训练

使用异步模式，通过重叠轨迹生成和训练来提高吞吐量。

### 何时使用异步
- 模型较大且生成时间较长
- 同步模式下 GPU 空闲时间高
- 有足够的内存用于缓冲

### 启动异步训练

```bash
python train_async.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --advantage-estimator grpo \
    --async-buffer-size 4 \
    --prompt-data /path/to/train.jsonl \
    ${MODEL_ARGS[@]}
```

### 异步特定参数

```bash
--async-buffer-size 4        # 要缓冲的轨迹数量
--update-weights-interval 2  # 每 N 个轨迹同步一次权重
```

---

## 工作流 3：多轮代理式训练

使用此工作流训练具有工具使用或多步推理能力的 Agent。

### 先决条件
- [ ] 用于多轮逻辑的自定义生成函数
- [ ] 工具/环境接口

### 步骤 1：定义自定义生成函数

```python
# custom_generate.py
async def custom_generate(args, samples, evaluation=False):
    """具有工具调用的多轮生成。"""
    for sample in samples:
        conversation = sample.prompt

        for turn in range(args.max_turns):
            # 生成响应
            response = await generate_single(conversation)

            # 检查工具调用
            tool_call = extract_tool_call(response)
            if tool_call:
                tool_result = execute_tool(tool_call)
                conversation.append({"role": "assistant", "content": response})
                conversation.append({"role": "tool", "content": tool_result})
            else:
                break

        sample.response = response
        sample.reward = compute_reward(sample)

    return samples
```

### 步骤 2：使用自定义函数启动

```bash
python train.py \
    --custom-generate-function-path custom_generate.py \
    --max-turns 5 \
    --prompt-data /path/to/agent_data.jsonl \
    ${MODEL_ARGS[@]}
```

完整的多轮搜索示例请参见 `examples/search-r1/`。

---

## 配置参考

### 三种参数类别

slime 使用三种类型的参数：

**1. Megatron 参数**（直接传递）：
```bash
--tensor-model-parallel-size 2
--pipeline-model-parallel-size 1
--num-layers 32
--hidden-size 4096
```

**2. SGLang 参数**（以 `--sglang-` 为前缀）：
```bash
--sglang-mem-fraction-static 0.8
--sglang-context-length 8192
--sglang-log-level INFO
```

**3. slime 参数**：
```bash
# 资源分配
--actor-num-nodes 1
--actor-num-gpus-per-node 8
--rollout-num-gpus 8
--colocate  # 在训练/推理之间共享 GPU

# 数据
--prompt-data /path/to/data.jsonl
--input-key prompt
--label-key label

# 训练循环
--num-rollout 3000
--rollout-batch-size 32
--n-samples-per-prompt 8
--global-batch-size 256

# 算法
--advantage-estimator grpo  # 或：gspo, ppo, reinforce_plus_plus
--use-kl-loss
--kl-loss-coef 0.001
```

### 关键约束

```
rollout_batch_size × n_samples_per_prompt = global_batch_size × num_steps_per_rollout
```

示例：32 × 8 = 256 × 1

---

## 数据缓冲区系统

slime 的数据缓冲区支持灵活的数据管理：

### 基本数据源

```python
class RolloutDataSource:
    def get_samples(self, num_samples):
        """从数据集中获取提示词。"""
        return self.dataset.sample(num_samples)

    def add_samples(self, samples):
        """生成后调用（默认无操作）。"""
        pass
```

### 缓冲数据源（离策略）

```python
class RolloutDataSourceWithBuffer(RolloutDataSource):
    def __init__(self):
        self.buffer = []

    def add_samples(self, samples):
        """存储生成的样本以供重用。"""
        self.buffer.extend(samples)

    def buffer_filter(self, args, buffer, num_samples):
        """自定义选择逻辑（优先级、分层等）。"""
        return select_best(buffer, num_samples)
```

---

## 常见问题与解决方案

### 问题：SGLang 引擎崩溃

**症状**：推理引擎在训练中途死亡

**解决方案**：
```bash
# 启用容错
--use-fault-tolerance

# 增加内存分配
--sglang-mem-fraction-static 0.85

# 减小批次大小
--rollout-batch-size 16
```

### 问题：权重同步超时

**症状**：轨迹生成后训练挂起

**解决方案**：
```bash
# 增加同步间隔
--update-weights-interval 5

# 使用共置模式（无网络传输）
--colocate
```

### 问题：训练期间 OOM

**症状**：反向传播期间 CUDA OOM

**解决方案**：
```bash
# 启用梯度检查点
--recompute-activations

# 减小微批次大小
--micro-batch-size 1

# 启用序列并行
--sequence-parallel
```

### 问题：数据加载缓慢

**症状**：数据获取期间 GPU 空闲

**解决方案**：
```bash
# 增加数据工作进程数
--num-data-workers 4

# 使用流式数据集
--streaming-data
```

---

## 支持的模型

| 模型系列 | 配置 |
|--------------|----------------|
| GLM | GLM-4.5, GLM-4.6, GLM-4.7, GLM-Z1-9B |
| Qwen | Qwen3 (4B, 8B, 30B-A3B), Qwen3-MoE, Qwen2.5 |
| DeepSeek | V3, V3.1, R1 |
| Llama | Llama 3 (8B, 70B) |
| 其他 | Kimi K2, Moonlight-16B |

每个模型在 `scripts/models/` 中都有预配置的脚本。

---

## 高级主题

### 共置模式

在训练和推理之间共享 GPU 以减少内存：

```bash
python train.py \
    --colocate \
    --actor-num-gpus-per-node 8 \
    --sglang-mem-fraction-static 0.4 \
    ${MODEL_ARGS[@]}
```

### 自定义奖励模型

```python
# custom_rm.py
class CustomRewardModel:
    def __init__(self, model_path):
        self.model = load_model(model_path)

    def compute_reward(self, prompts, responses):
        inputs = self.tokenize(prompts, responses)
        scores = self.model(inputs)
        return scores.tolist()
```

```bash
--custom-rm-path custom_rm.py
```

### 评估多任务

```bash
--eval-prompt-data aime /path/to/aime.jsonl \
--eval-prompt-data gsm8k /path/to/gsm8k.jsonl \
--n-samples-per-eval-prompt 16
```

---

## 资源

- **文档**：https://thudm.github.io/slime/
- **GitHub**：https://github.com/THUDM/slime
- **博客**：https://lmsys.org/blog/2025-07-09-slime/
- **示例**：参见 `examples/` 目录，包含 14 多个工作示例