---
title: "Serving Llms Vllm — 使用 vLLM 的 PagedAttention 和连续批处理实现高吞吐量 LLM 服务"
sidebar_label: "Serving Llms Vllm"
description: "使用 vLLM 的 PagedAttention 和连续批处理实现高吞吐量 LLM 服务"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Serving Llms Vllm

使用 vLLM 的 PagedAttention 和连续批处理实现高吞吐量 LLM 服务。适用于部署生产级 LLM API、优化推理延迟/吞吐量，或在 GPU 内存有限的情况下服务模型。支持 OpenAI 兼容的端点、量化（GPTQ/AWQ/FP8）和张量并行。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/vllm` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `vllm`, `torch`, `transformers` |
| 标签 | `vLLM`, `推理服务`, `PagedAttention`, `连续批处理`, `高吞吐量`, `生产环境`, `OpenAI API`, `量化`, `张量并行` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# vLLM - 高性能 LLM 服务

## 快速开始

vLLM 通过 PagedAttention（基于块的 KV 缓存）和连续批处理（混合预填充/解码请求）实现了比标准 transformers 高 24 倍的吞吐量。

**安装**：
```bash
pip install vllm
```

**基础离线推理**：
```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, max_tokens=256)

outputs = llm.generate(["Explain quantum computing"], sampling)
print(outputs[0].outputs[0].text)
```

**OpenAI 兼容服务器**：
```bash
vllm serve meta-llama/Llama-3-8B-Instruct

# 使用 OpenAI SDK 查询
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
"
```

## 常见工作流

### 工作流 1：生产 API 部署

复制此清单并跟踪进度：

```
部署进度：
- [ ] 步骤 1：配置服务器设置
- [ ] 步骤 2：使用有限流量测试
- [ ] 步骤 3：启用监控
- [ ] 步骤 4：部署到生产环境
- [ ] 步骤 5：验证性能指标
```

**步骤 1：配置服务器设置**

根据模型大小选择配置：

```bash
# 适用于单 GPU 上的 7B-13B 模型
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000

# 适用于使用张量并行的 30B-70B 模型
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000

# 适用于带缓存和指标的生产环境
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```

**步骤 2：使用有限流量测试**

在生产前运行负载测试：

```bash
# 安装负载测试工具
pip install locust

# 创建包含示例请求的 test_load.py
# 运行：locust -f test_load.py --host http://localhost:8000
```

验证 TTFT（首 Token 时间）< 500ms 且吞吐量 > 100 请求/秒。

**步骤 3：启用监控**

vLLM 在端口 9090 上暴露 Prometheus 指标：

```bash
curl http://localhost:9090/metrics | grep vllm
```

需要监控的关键指标：
- `vllm:time_to_first_token_seconds` - 延迟
- `vllm:num_requests_running` - 活动请求数
- `vllm:gpu_cache_usage_perc` - KV 缓存利用率

**步骤 4：部署到生产环境**

使用 Docker 实现一致的部署：

```bash
# 在 Docker 中运行 vLLM
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching
```

**步骤 5：验证性能指标**

检查部署是否达到目标：
- TTFT < 500ms（对于短提示词）
- 吞吐量 > 目标请求/秒
- GPU 利用率 > 80%
- 日志中无 OOM 错误

### 工作流 2：离线批量推理

用于处理大型数据集而无需服务器开销。

复制此清单：

```
批量处理：
- [ ] 步骤 1：准备输入数据
- [ ] 步骤 2：配置 LLM 引擎
- [ ] 步骤 3：运行批量推理
- [ ] 步骤 4：处理结果
```

**步骤 1：准备输入数据**

```python
# 从文件加载提示词
prompts = []
with open("prompts.txt") as f:
    prompts = [line.strip() for line in f]

print(f"Loaded {len(prompts)} prompts")
```

**步骤 2：配置 LLM 引擎**

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    tensor_parallel_size=2,  # 使用 2 个 GPU
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

sampling = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
    stop=["</s>", "\n\n"]
)
```

**步骤 3：运行批量推理**

vLLM 自动对请求进行批处理以提高效率：

```python
# 在一次调用中处理所有提示词
outputs = llm.generate(prompts, sampling)

# vLLM 内部处理批处理
# 无需手动分块提示词
```

**步骤 4：处理结果**

```python
# 提取生成的文本
results = []
for output in outputs:
    prompt = output.prompt
    generated = output.outputs[0].text
    results.append({
        "prompt": prompt,
        "generated": generated,
        "tokens": len(output.outputs[0].token_ids)
    })

# 保存到文件
import json
with open("results.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"Processed {len(results)} prompts")
```

### 工作流 3：量化模型服务

在有限的 GPU 内存中容纳大型模型。

```
量化设置：
- [ ] 步骤 1：选择量化方法
- [ ] 步骤 2：查找或创建量化模型
- [ ] 步骤 3：使用量化标志启动
- [ ] 步骤 4：验证准确性
```

**步骤 1：选择量化方法**

- **AWQ**：最适合 70B 模型，精度损失最小
- **GPTQ**：广泛的模型支持，良好的压缩率
- **FP8**：在 H100 GPU 上最快

**步骤 2：查找或创建量化模型**

使用 HuggingFace 上的预量化模型：

```bash
# 搜索 AWQ 模型
# 示例：TheBloke/Llama-2-70B-AWQ
```

**步骤 3：使用量化标志启动**

```bash
# 使用预量化模型
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95

# 结果：70B 模型占用约 40GB VRAM
```

**步骤 4：验证准确性**

测试输出是否符合预期质量：

```python
# 比较量化与非量化模型的响应
# 验证特定任务的性能未发生变化
```

## 使用时机与替代方案对比

**在以下情况下使用 vLLM：**
- 部署生产级 LLM API（100+ 请求/秒）
- 服务 OpenAI 兼容的端点
- GPU 内存有限但需要大型模型
- 多用户应用程序（聊天机器人、助手）
- 需要低延迟和高吞吐量

**在以下情况下使用替代方案：**
- **llama.cpp**：CPU/边缘推理，单用户
- **HuggingFace transformers**：研究、原型设计、一次性生成
- **TensorRT-LLM**：仅限 NVIDIA，需要绝对最高性能
- **Text-Generation-Inference**：已在 HuggingFace 生态系统中

## 常见问题

**问题：模型加载期间内存不足**

减少内存使用：
```bash
vllm serve MODEL \
  --gpu-memory-utilization 0.7 \
  --max-model-len 4096
```

或使用量化：
```bash
vllm serve MODEL --quantization awq
```

**问题：首 Token 慢（TTFT > 1 秒）**

为重复提示词启用前缀缓存：
```bash
vllm serve MODEL --enable-prefix-caching
```

对于长提示词，启用分块预填充：
```bash
vllm serve MODEL --enable-chunked-prefill
```

**问题：模型未找到错误**

对于自定义模型，使用 `--trust-remote-code`：
```bash
vllm serve MODEL --trust-remote-code
```

**问题：吞吐量低（<50 请求/秒）**

增加并发序列数：
```bash
vllm serve MODEL --max-num-seqs 512
```

使用 `nvidia-smi` 检查 GPU 利用率 - 应 >80%。

**问题：推理速度慢于预期**

验证张量并行使用的是 2 的幂次方个 GPU：
```bash
vllm serve MODEL --tensor-parallel-size 4  # 而不是 3
```

启用推测解码以加速生成：
```bash
vllm serve MODEL --speculative-model DRAFT_MODEL
```

## 高级主题

**服务器部署模式**：有关 Docker、Kubernetes 和负载均衡配置，请参阅 [references/server-deployment.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/server-deployment.md)。

**性能优化**：有关 PagedAttention 调优、连续批处理细节和基准测试结果，请参阅 [references/optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/optimization.md)。

**量化指南**：有关 AWQ/GPTQ/FP8 设置、模型准备和准确性比较，请参阅 [references/quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/quantization.md)。

**故障排除**：有关详细的错误消息、调试步骤和性能诊断，请参阅 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/troubleshooting.md)。

## 硬件要求

- **小型模型（7B-13B）**：1x A10（24GB）或 A100（40GB）
- **中型模型（30B-40B）**：2x A100（40GB）配合张量并行
- **大型模型（70B+）**：4x A100（40GB）或 2x A100（80GB），使用 AWQ/GPTQ

支持的平台：NVIDIA（主要）、AMD ROCm、Intel GPU、TPU

## 资源

- 官方文档：https://docs.vllm.ai
- GitHub：https://github.com/vllm-project/vllm
- 论文："Efficient Memory Management for Large Language Model Serving with PagedAttention" (SOSP 2023)
- 社区：https://discuss.vllm.ai