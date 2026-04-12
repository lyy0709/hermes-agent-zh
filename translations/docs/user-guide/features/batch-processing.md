---
sidebar_position: 12
title: "批量处理"
description: "大规模生成 Agent 轨迹——并行处理、检查点和工具集分布"
---

# 批量处理

批量处理功能允许你并行运行 Hermes Agent 处理数百或数千个提示词，生成结构化的轨迹数据。这主要用于**训练数据生成**——生成包含工具使用统计信息的 ShareGPT 格式轨迹，可用于微调或评估。

## 概述

批量运行器 (`batch_runner.py`) 处理一个包含提示词的 JSONL 数据集，通过一个具有工具访问权限的完整 Agent 会话运行每个提示词。每个提示词都在其独立的执行环境中运行。输出是结构化的轨迹数据，包含完整的对话历史、工具调用统计信息和推理覆盖率指标。

## 快速开始

```bash
# 基本批量运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=4

# 恢复中断的运行
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --resume

# 列出可用的工具集分布
python batch_runner.py --list_distributions
```

## 数据集格式

输入数据集是一个 JSONL 文件（每行一个 JSON 对象）。每个条目必须包含一个 `prompt` 字段：

```jsonl
{"prompt": "编写一个查找最长回文子串的 Python 函数"}
{"prompt": "使用 Flask 创建一个用于用户身份验证的 REST API 端点"}
{"prompt": "调试此错误：TypeError: cannot unpack non-iterable NoneType object"}
```

条目可选地可以包含：
- `image` 或 `docker_image`：用于此提示词沙盒的容器镜像（适用于 Docker、Modal 和 Singularity 后端）
- `cwd`：任务终端会话的工作目录覆盖

## 配置选项

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--dataset_file` | (必需) | JSONL 数据集路径 |
| `--batch_size` | (必需) | 每批处理的提示词数量 |
| `--run_name` | (必需) | 本次运行的名称（用于输出目录和检查点） |
| `--distribution` | `"default"` | 从中采样的工具集分布 |
| `--model` | `claude-sonnet-4.6` | 使用的模型 |
| `--base_url` | `https://openrouter.ai/api/v1` | API 基础 URL |
| `--api_key` | (环境变量) | 模型的 API 密钥 |
| `--max_turns` | `10` | 每个提示词的最大工具调用迭代次数 |
| `--num_workers` | `4` | 并行工作进程数 |
| `--resume` | `false` | 从检查点恢复 |
| `--verbose` | `false` | 启用详细日志记录 |
| `--max_samples` | 全部 | 仅处理数据集中的前 N 个样本 |
| `--max_tokens` | 模型默认值 | 每个模型响应的最大 Token 数 |

### 提供商路由 (OpenRouter)

| 参数 | 描述 |
|-----------|-------------|
| `--providers_allowed` | 允许的提供商，逗号分隔（例如 `"anthropic,openai"`） |
| `--providers_ignored` | 忽略的提供商，逗号分隔（例如 `"together,deepinfra"`） |
| `--providers_order` | 首选的提供商顺序，逗号分隔 |
| `--provider_sort` | 按 `"price"`、`"throughput"` 或 `"latency"` 排序 |

### 推理控制

| 参数 | 描述 |
|-----------|-------------|
| `--reasoning_effort` | 努力级别：`none`、`minimal`、`low`、`medium`、`high`、`xhigh` |
| `--reasoning_disabled` | 完全禁用推理/思考 Token |

### 高级选项

| 参数 | 描述 |
|-----------|-------------|
| `--ephemeral_system_prompt` | 执行期间使用但**不**保存到轨迹的系统提示词 |
| `--log_prefix_chars` | 日志预览中显示的字符数（默认：100） |
| `--prefill_messages_file` | 包含用于少样本提示的预填充消息的 JSON 文件路径 |

## 工具集分布

每个提示词都会从一个**分布**中随机采样一组工具集。这确保了训练数据涵盖不同的工具组合。使用 `--list_distributions` 查看所有可用的分布。

在当前实现中，分布为**每个独立的工具集**分配一个概率。采样器独立地翻转每个工具集，然后保证至少有一个工具集被启用。这与手动编写的预构建组合表不同。

## 输出格式

所有输出都保存到 `data/<run_name>/`：

```text
data/my_run/
├── trajectories.jsonl    # 合并的最终输出（所有批次合并）
├── batch_0.jsonl         # 单个批次结果
├── batch_1.jsonl
├── ...
├── checkpoint.json       # 恢复检查点
└── statistics.json       # 聚合工具使用统计
```

### 轨迹格式

`trajectories.jsonl` 中的每一行都是一个 JSON 对象：

```json
{
  "prompt_index": 42,
  "conversations": [
    {"from": "human", "value": "编写一个函数..."},
    {"from": "gpt", "value": "我来创建那个函数...",
     "tool_calls": [...]},
    {"from": "tool", "value": "..."},
    {"from": "gpt", "value": "这是完成的函数..."}
  ],
  "metadata": {
    "batch_num": 2,
    "timestamp": "2026-01-15T10:30:00",
    "model": "anthropic/claude-sonnet-4.6"
  },
  "completed": true,
  "partial": false,
  "api_calls": 3,
  "toolsets_used": ["terminal", "file"],
  "tool_stats": {
    "terminal": {"count": 2, "success": 2, "failure": 0},
    "read_file": {"count": 1, "success": 1, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0
  }
}
```

`conversations` 字段使用类似 ShareGPT 的格式，包含 `from` 和 `value` 字段。工具统计信息被归一化，包含所有可能的工具并带有零默认值，确保条目之间模式一致，以便与 HuggingFace 数据集兼容。

## 检查点

批量运行器具有强大的检查点功能，用于容错：

- **检查点文件：** 每批完成后保存，跟踪哪些提示词索引已完成
- **基于内容的恢复：** 在 `--resume` 时，运行器扫描现有的批次文件，并通过实际文本内容（不仅仅是索引）匹配已完成的提示词，即使数据集顺序发生变化也能恢复
- **失败的提示词：** 只有成功完成的提示词才被标记为完成——失败的提示词将在恢复时重试
- **批次合并：** 完成后，所有批次文件（包括之前运行的）将合并到单个 `trajectories.jsonl` 中

### 恢复工作原理

1. 扫描所有 `batch_*.jsonl` 文件以查找已完成的提示词（通过内容匹配）
2. 过滤数据集以排除已完成的提示词
3. 对剩余的提示词重新分批
4. 仅处理剩余的提示词
5. 将所有批次文件（旧的和新的）合并到最终输出中

## 质量过滤

批量运行器应用自动质量过滤：

- **无推理过滤器：** 丢弃零个助手轮次包含推理（没有 `<REASONING_SCRATCHPAD>` 或原生思考 Token）的样本
- **损坏条目过滤器：** 在最终合并期间过滤掉包含幻觉工具名称（不在有效工具列表中）的条目
- **推理统计：** 跟踪整个运行中带有/不带有推理的轮次百分比

## 统计信息

完成后，运行器会打印全面的统计信息：

- **工具使用：** 每个工具的调用次数、成功/失败率
- **推理覆盖率：** 包含推理的助手轮次百分比
- **丢弃的样本：** 因缺乏推理而被过滤的样本数量
- **持续时间：** 总处理时间

统计信息也会保存到 `statistics.json` 中，以便进行程序化分析。

## 使用场景

### 训练数据生成

生成多样化的工具使用轨迹用于微调：

```bash
python batch_runner.py \
    --dataset_file=data/coding_prompts.jsonl \
    --batch_size=20 \
    --run_name=coding_v1 \
    --model=anthropic/claude-sonnet-4.6 \
    --num_workers=8 \
    --distribution=default \
    --max_turns=15
```

### 模型评估

评估模型在标准化提示词上使用工具的能力：

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### 每个提示词的容器镜像

对于需要特定环境的基准测试，每个提示词可以指定自己的容器镜像：

```jsonl
{"prompt": "安装 numpy 并计算 3x3 矩阵的特征值", "image": "python:3.11-slim"}
{"prompt": "编译此 Rust 程序并运行它", "image": "rust:1.75"}
{"prompt": "设置一个 Node.js Express 服务器", "image": "node:20-alpine", "cwd": "/app"}
```

批量运行器在运行每个提示词之前会验证 Docker 镜像是否可访问。