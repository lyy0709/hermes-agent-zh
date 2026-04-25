---
title: "优化注意力 Flash"
sidebar_label: "优化注意力 Flash"
description: "使用 Flash Attention 优化 Transformer 注意力，实现 2-4 倍加速和 10-20 倍内存减少"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 优化注意力 Flash

使用 Flash Attention 优化 Transformer 注意力，实现 2-4 倍加速和 10-20 倍内存减少。在训练/运行长序列（>512 Token）的 Transformer、遇到注意力 GPU 内存问题或需要更快推理时使用。支持 PyTorch 原生 SDPA、flash-attn 库、H100 FP8 和滑动窗口注意力。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/flash-attention` 安装 |
| 路径 | `optional-skills/mlops/flash-attention` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `flash-attn`, `torch`, `transformers` |
| 标签 | `Optimization`, `Flash Attention`, `Attention Optimization`, `Memory Efficiency`, `Speed Optimization`, `Long Context`, `PyTorch`, `SDPA`, `H100`, `FP8`, `Transformers` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Flash Attention - 快速内存高效注意力

## 快速开始

Flash Attention 通过 IO 感知的分块和重计算，为 Transformer 注意力提供 2-4 倍加速和 10-20 倍内存减少。

**PyTorch 原生（最简单，PyTorch 2.2+）**:
```python
import torch
import torch.nn.functional as F

q = torch.randn(2, 8, 512, 64, device='cuda', dtype=torch.float16)  # [batch, heads, seq, dim]
k = torch.randn(2, 8, 512, 64, device='cuda', dtype=torch.float16)
v = torch.randn(2, 8, 512, 64, device='cuda', dtype=torch.float16)

# 如果可用，自动使用 Flash Attention
out = F.scaled_dot_product_attention(q, k, v)
```

**flash-attn 库（更多功能）**:
```bash
pip install flash-attn --no-build-isolation
```

```python
from flash_attn import flash_attn_func

# q, k, v: [batch, seqlen, nheads, headdim]
out = flash_attn_func(q, k, v, dropout_p=0.0, causal=True)
```

## 常见工作流

### 工作流 1：在现有 PyTorch 模型中启用

复制此清单：

```
Flash Attention 集成：
- [ ] 步骤 1：检查 PyTorch 版本（≥2.2）
- [ ] 步骤 2：启用 Flash Attention 后端
- [ ] 步骤 3：通过性能分析验证加速
- [ ] 步骤 4：测试准确性与基线匹配
```

**步骤 1：检查 PyTorch 版本**

```bash
python -c "import torch; print(torch.__version__)"
# 应 ≥2.2.0
```

如果 &lt;2.2，升级：
```bash
pip install --upgrade torch
```

**步骤 2：启用 Flash Attention 后端**

替换标准注意力：
```python
# 之前（标准注意力）
attn_weights = torch.softmax(q @ k.transpose(-2, -1) / math.sqrt(d_k), dim=-1)
out = attn_weights @ v

# 之后（Flash Attention）
import torch.nn.functional as F
out = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
```

强制使用 Flash Attention 后端：
```python
with torch.backends.cuda.sdp_kernel(
    enable_flash=True,
    enable_math=False,
    enable_mem_efficient=False
):
    out = F.scaled_dot_product_attention(q, k, v)
```

**步骤 3：通过性能分析验证加速**

```python
import torch.utils.benchmark as benchmark

def test_attention(use_flash):
    q, k, v = [torch.randn(2, 8, 2048, 64, device='cuda', dtype=torch.float16) for _ in range(3)]

    if use_flash:
        with torch.backends.cuda.sdp_kernel(enable_flash=True):
            return F.scaled_dot_product_attention(q, k, v)
    else:
        attn = (q @ k.transpose(-2, -1) / 8.0).softmax(dim=-1)
        return attn @ v

# 基准测试
t_flash = benchmark.Timer(stmt='test_attention(True)', globals=globals())
t_standard = benchmark.Timer(stmt='test_attention(False)', globals=globals())

print(f"Flash: {t_flash.timeit(100).mean:.3f}s")
print(f"Standard: {t_standard.timeit(100).mean:.3f}s")
```

预期：对于 >512 Token 的序列，有 2-4 倍加速。

**步骤 4：测试准确性与基线匹配**

```python
# 比较输出
q, k, v = [torch.randn(1, 8, 512, 64, device='cuda', dtype=torch.float16) for _ in range(3)]

# Flash Attention
out_flash = F.scaled_dot_product_attention(q, k, v)

# 标准注意力
attn_weights = torch.softmax(q @ k.transpose(-2, -1) / 8.0, dim=-1)
out_standard = attn_weights @ v

# 检查差异
diff = (out_flash - out_standard).abs().max()
print(f"最大差异: {diff:.6f}")
# 对于 float16，应 <1e-3
```

### 工作流 2：使用 flash-attn 库获取高级功能

用于多查询注意力、滑动窗口或 H100 FP8。

复制此清单：

```
flash-attn 库设置：
- [ ] 步骤 1：安装 flash-attn 库
- [ ] 步骤 2：修改注意力代码
- [ ] 步骤 3：启用高级功能
- [ ] 步骤 4：基准测试性能
```

**步骤 1：安装 flash-attn 库**

```bash
# NVIDIA GPU (CUDA 12.0+)
pip install flash-attn --no-build-isolation

# 验证安装
python -c "from flash_attn import flash_attn_func; print('Success')"
```

**步骤 2：修改注意力代码**

```python
from flash_attn import flash_attn_func

# 输入: [batch_size, seq_len, num_heads, head_dim]
# 如果需要，从 [batch, heads, seq, dim] 转置
q = q.transpose(1, 2)  # [batch, seq, heads, dim]
k = k.transpose(1, 2)
v = v.transpose(1, 2)

out = flash_attn_func(
    q, k, v,
    dropout_p=0.1,
    causal=True,  # 用于自回归模型
    window_size=(-1, -1),  # 无滑动窗口
    softmax_scale=None  # 自动缩放
)

out = out.transpose(1, 2)  # 转回 [batch, heads, seq, dim]
```

**步骤 3：启用高级功能**

多查询注意力（跨头共享 K/V）：
```python
from flash_attn import flash_attn_func

# q: [batch, seq, num_q_heads, dim]
# k, v: [batch, seq, num_kv_heads, dim]  # 更少的 KV 头
out = flash_attn_func(q, k, v)  # 自动处理 MQA
```

滑动窗口注意力（局部注意力）：
```python
# 仅关注前后 256 个 Token 的窗口
out = flash_attn_func(
    q, k, v,
    window_size=(256, 256),  # (左, 右) 窗口
    causal=True
)
```

**步骤 4：基准测试性能**

```python
import torch
from flash_attn import flash_attn_func
import time

q, k, v = [torch.randn(4, 4096, 32, 64, device='cuda', dtype=torch.float16) for _ in range(3)]

# 预热
for _ in range(10):
    _ = flash_attn_func(q, k, v)

# 基准测试
torch.cuda.synchronize()
start = time.time()
for _ in range(100):
    out = flash_attn_func(q, k, v)
    torch.cuda.synchronize()
end = time.time()

print(f"每次迭代时间: {(end-start)/100*1000:.2f}ms")
print(f"已分配内存: {torch.cuda.max_memory_allocated()/1e9:.2f}GB")
```

### 工作流 3：H100 FP8 优化 (FlashAttention-3)

用于在 H100 GPU 上获得最大性能。

```
FP8 设置：
- [ ] 步骤 1：验证 H100 GPU 可用
- [ ] 步骤 2：安装支持 FP8 的 flash-attn
- [ ] 步骤 3：将输入转换为 FP8
- [ ] 步骤 4：使用 FP8 注意力运行
```

**步骤 1：验证 H100 GPU**

```bash
nvidia-smi --query-gpu=name --format=csv
# 应显示 "H100" 或 "H800"
```

**步骤 2：安装支持 FP8 的 flash-attn**

```bash
pip install flash-attn --no-build-isolation
# H100 包含 FP8 支持
```

**步骤 3：将输入转换为 FP8**

```python
import torch

q = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)
k = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)
v = torch.randn(2, 4096, 32, 64, device='cuda', dtype=torch.float16)

# 转换为 float8_e4m3 (FP8)
q_fp8 = q.to(torch.float8_e4m3fn)
k_fp8 = k.to(torch.float8_e4m3fn)
v_fp8 = v.to(torch.float8_e4m3fn)
```

**步骤 4：使用 FP8 注意力运行**

```python
from flash_attn import flash_attn_func

# FlashAttention-3 在 H100 上自动使用 FP8 内核
out = flash_attn_func(q_fp8, k_fp8, v_fp8)
# 结果：约 1.2 PFLOPS，比 FP16 快 1.5-2 倍
```

## 何时使用与替代方案

**在以下情况使用 Flash Attention：**
- 训练序列 >512 Token 的 Transformer
- 使用长上下文（>2K Token）进行推理
- GPU 内存受限（标准注意力导致 OOM）
- 需要 2-4 倍加速且无精度损失
- 使用 PyTorch 2.2+ 或可以安装 flash-attn

**改用替代方案：**
- **标准注意力**：序列 &lt;256 Token（开销不值得）
- **xFormers**：需要更多注意力变体（不仅仅是速度）
- **内存高效注意力**：CPU 推理（Flash Attention 需要 GPU）

## 常见问题

**问题：ImportError: cannot import flash_attn**

使用 no-build-isolation 标志安装：
```bash
pip install flash-attn --no-build-isolation
```

或先安装 CUDA 工具包：
```bash
conda install cuda -c nvidia
pip install flash-attn --no-build-isolation
```

**问题：比预期慢（无加速）**

Flash Attention 的收益随序列长度增加：
- &lt;512 Token：最小加速（10-20%）
- 512-2K Token：2-3 倍加速
- >2K Token：3-4 倍加速

检查序列长度是否足够。

**问题：RuntimeError: CUDA error**

验证 GPU 支持 Flash Attention：
```python
import torch
print(torch.cuda.get_device_capability())
# 对于 Turing+，应 ≥(7, 5)
```

Flash Attention 要求：
- Ampere (A100, A10): ✅ 完全支持
- Turing (T4): ✅ 支持
- Volta (V100): ❌ 不支持

**问题：精度下降**

检查 dtype 是否为 float16 或 bfloat16（非 float32）：
```python
q = q.to(torch.float16)  # 或 torch.bfloat16
```

Flash Attention 使用 float16/bfloat16 以获得速度。不支持 Float32。

## 高级主题

**与 HuggingFace Transformers 集成**：有关在 BERT、GPT、Llama 模型中启用 Flash Attention，请参阅 [references/transformers-integration.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/flash-attention/references/transformers-integration.md)。

**性能基准测试**：有关跨 GPU 和序列长度的详细速度和内存比较，请参阅 [references/benchmarks.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/flash-attention/references/benchmarks.md)。

**算法细节**：有关分块策略、重计算和 IO 复杂度分析，请参阅 [references/algorithm.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/flash-attention/references/algorithm.md)。

**高级功能**：有关旋转嵌入、ALiBi、分页 KV 缓存和自定义注意力掩码，请参阅 [references/advanced-features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/flash-attention/references/advanced-features.md)。

## 硬件要求

- **GPU**：NVIDIA Ampere+ (A100, A10, A30) 或 AMD MI200+
- **VRAM**：与标准注意力相同（Flash Attention 不增加内存）
- **CUDA**：12.0+（最低 11.8）
- **PyTorch**：2.2+ 用于原生支持

**不支持**：V100 (Volta)、CPU 推理

## 资源

- 论文："FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" (NeurIPS 2022)
- 论文："FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning" (ICLR 2024)
- 博客：https://tridao.me/blog/2024/flash3/
- GitHub：https://github.com/Dao-AILab/flash-attention
- PyTorch 文档：https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html