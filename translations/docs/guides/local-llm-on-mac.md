---
sidebar_position: 2
title: "在 Mac 上运行本地 LLM"
description: "在 macOS 上使用 llama.cpp 或 MLX 设置兼容 OpenAI 的本地 LLM 服务器，包括模型选择、内存优化以及在 Apple Silicon 上的真实基准测试"
---

# 在 Mac 上运行本地 LLM

本指南将引导您在 macOS 上运行一个兼容 OpenAI API 的本地 LLM 服务器。您将获得完全的隐私性、零 API 成本，以及在 Apple Silicon 上令人惊喜的良好性能。

我们涵盖两种后端：

| 后端 | 安装 | 最擅长 | 格式 |
|---------|---------|---------|--------|
| **llama.cpp** | `brew install llama.cpp` | 最快的首个 Token 生成时间，量化 KV 缓存以降低内存占用 | GGUF |
| **omlx** | [omlx.ai](https://omlx.ai) | 最快的 Token 生成速度，原生 Metal 优化 | MLX (safetensors) |

两者都暴露一个兼容 OpenAI 的 `/v1/chat/completions` 端点。Hermes 可与任一后端配合使用——只需将其指向 `http://localhost:8080` 或 `http://localhost:8000`。

:::info 仅限 Apple Silicon
本指南针对配备 Apple Silicon（M1 及更高版本）的 Mac。Intel Mac 可以使用 llama.cpp，但没有 GPU 加速——性能会显著降低。
:::

---

## 选择模型

对于入门，我们推荐 **Qwen3.5-9B**——这是一个强大的推理模型，经过量化后可以舒适地运行在 8GB+ 的统一内存中。

| 变体 | 磁盘大小 | 所需内存（128K 上下文） | 后端 |
|---------|-------------|---------------------------|---------|
| Qwen3.5-9B-Q4_K_M (GGUF) | 5.3 GB | 约 10 GB（使用量化 KV 缓存） | llama.cpp |
| Qwen3.5-9B-mlx-lm-mxfp4 (MLX) | 约 5 GB | 约 12 GB | omlx |

**内存经验法则：** 模型大小 + KV 缓存。一个 9B Q4 模型约 5 GB。在 128K 上下文下，使用 Q4 量化的 KV 缓存会增加约 4-5 GB。使用默认（f16）KV 缓存，则会膨胀到约 16 GB。llama.cpp 中的量化 KV 缓存标志是内存受限系统的关键技巧。

对于更大的模型（27B, 35B），您需要 32 GB+ 的统一内存。9B 模型是 8-16 GB 机器的理想选择。

---

## 选项 A：llama.cpp

llama.cpp 是最便携的本地 LLM 运行时。在 macOS 上，它默认使用 Metal 进行 GPU 加速。

### 安装

```bash
brew install llama.cpp
```

这将为您全局安装 `llama-server` 命令。

### 下载模型

您需要一个 GGUF 格式的模型。最简单的来源是通过 `huggingface-cli` 从 Hugging Face 下载：

```bash
brew install huggingface-cli
```

然后下载：

```bash
huggingface-cli download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf --local-dir ~/models
```

:::tip 受限制的模型
Hugging Face 上的某些模型需要身份验证。如果遇到 401 或 404 错误，请先运行 `huggingface-cli login`。
:::

### 启动服务器

```bash
llama-server -m ~/models/Qwen3.5-9B-Q4_K_M.gguf \
  -ngl 99 \
  -c 131072 \
  -np 1 \
  -fa on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --host 0.0.0.0
```

以下是每个标志的作用：

| 标志 | 用途 |
|------|---------|
| `-ngl 99` | 将所有层卸载到 GPU（Metal）。使用一个高数值以确保没有内容留在 CPU 上。 |
| `-c 131072` | 上下文窗口大小（128K Token）。如果内存不足，请减小此值。 |
| `-np 1` | 并行槽位数。对于单用户使用保持为 1——更多槽位会分割您的内存预算。 |
| `-fa on` | Flash attention。减少内存使用并加速长上下文推理。 |
| `--cache-type-k q4_0` | 将 Key 缓存量化为 4 位。**这是节省内存的关键。** |
| `--cache-type-v q4_0` | 将 Value 缓存量化为 4 位。与上述结合，这使 KV 缓存内存比 f16 减少约 75%。 |
| `--host 0.0.0.0` | 监听所有接口。如果不需要网络访问，请使用 `127.0.0.1`。 |

当您看到以下信息时，服务器就绪：

```
main: server is listening on http://0.0.0.0:8080
srv  update_slots: all slots are idle
```

### 受限系统的内存优化

`--cache-type-k q4_0 --cache-type-v q4_0` 标志对于内存有限的系统是最重要的优化。以下是 128K 上下文下的影响：

| KV 缓存类型 | KV 缓存内存（128K 上下文，9B 模型） |
|---------------|--------------------------------------|
| f16 (默认) | 约 16 GB |
| q8_0 | 约 8 GB |
| **q4_0** | **约 4 GB** |

在 8 GB 的 Mac 上，使用 `q4_0` KV 缓存并将上下文减少到 `-c 32768`（32K）。在 16 GB 上，您可以舒适地使用 128K 上下文。在 32 GB+ 上，您可以运行更大的模型或多个并行槽位。

如果仍然内存不足，首先减小上下文大小（`-c`），然后尝试更小的量化（用 Q3_K_M 代替 Q4_K_M）。

### 测试

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 获取模型名称

如果忘记了模型名称，可以查询模型端点：

```bash
curl -s http://localhost:8080/v1/models | jq '.data[].id'
```

---

## 选项 B：通过 omlx 使用 MLX

[omlx](https://omlx.ai) 是一个 macOS 原生应用，用于管理和提供 MLX 模型。MLX 是 Apple 自己的机器学习框架，专门针对 Apple Silicon 的统一内存架构进行了优化。

### 安装

从 [omlx.ai](https://omlx.ai) 下载并安装。它提供了一个用于模型管理的 GUI 和一个内置服务器。

### 下载模型

使用 omlx 应用浏览和下载模型。搜索 `Qwen3.5-9B-mlx-lm-mxfp4` 并下载。模型存储在本地（通常在 `~/.omlx/models/` 目录下）。

### 启动服务器

omlx 默认在 `http://127.0.0.1:8000` 上提供模型服务。从应用 UI 启动服务，或者使用 CLI（如果可用）。

### 测试

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-mlx-lm-mxfp4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 列出可用模型

omlx 可以同时提供多个模型：

```bash
curl -s http://127.0.0.1:8000/v1/models | jq '.data[].id'
```

---

## 基准测试：llama.cpp vs MLX

两种后端在同一台机器（Apple M5 Max，128 GB 统一内存）上测试，运行相同的模型（Qwen3.5-9B），量化级别相当（GGUF 为 Q4_K_M，MLX 为 mxfp4）。五个不同的提示，每个运行三次，后端顺序测试以避免资源争用。

### 结果

| 指标 | llama.cpp (Q4_K_M) | MLX (mxfp4) | 胜出者 |
|--------|-------------------|-------------|--------|
| **TTFT (平均)** | **67 毫秒** | 289 毫秒 | llama.cpp (快 4.3 倍) |
| **TTFT (p50)** | **66 毫秒** | 286 毫秒 | llama.cpp (快 4.3 倍) |
| **生成速度 (平均)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **生成速度 (p50)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **总时间 (512 Token)** | 7.3秒 | **5.5秒** | MLX (快 25%) |

### 这意味着什么

- **llama.cpp** 在提示处理方面表现出色——其 flash attention + 量化 KV 缓存流水线使您在大约 66 毫秒内获得第一个 Token。如果您正在构建感知响应性很重要的交互式应用程序（聊天机器人、自动补全），这是一个有意义的优势。

- **MLX** 一旦开始生成，Token 生成速度约快 37%。对于批量工作负载、长文本生成或任何总完成时间比初始延迟更重要的任务，MLX 完成得更快。

- 两种后端都**极其一致**——不同运行之间的差异可以忽略不计。您可以依赖这些数字。

### 您应该选择哪一个？

| 用例 | 推荐 |
|----------|---------------|
| 交互式聊天、低延迟工具 | llama.cpp |
| 长文本生成、批量处理 | MLX (omlx) |
| 内存受限（8-16 GB） | llama.cpp（量化 KV 缓存无与伦比） |
| 同时提供多个模型 | omlx（内置多模型支持） |
| 最大兼容性（也适用于 Linux） | llama.cpp |

---

## 连接到 Hermes

一旦您的本地服务器运行起来：

```bash
hermes model
```

选择 **自定义端点** 并按照提示操作。它会要求输入基础 URL 和模型名称——使用您上面设置的任一后端的值。

---

## 超时设置

Hermes 会自动检测本地端点（localhost，局域网 IP）并放宽其流式传输超时设置。对于大多数设置，无需配置。

如果仍然遇到超时错误（例如，在慢速硬件上处理非常大的上下文），您可以覆盖流式读取超时：

```bash
# 在您的 .env 文件中——从默认的 120 秒提高到 30 分钟
HERMES_STREAM_READ_TIMEOUT=1800
```

| 超时 | 默认值 | 本地自动调整 | 环境变量覆盖 |
|---------|---------|----------------------|------------------|
| 流读取（套接字级别） | 120秒 | 提高到 1800秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180秒 | 完全禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API 调用（非流式） | 1800秒 | 无需更改 | `HERMES_API_TIMEOUT` |

流读取超时是最可能引起问题的——它是接收下一个数据块的套接字级截止时间。在处理大型上下文的前缀填充期间，本地模型可能在处理提示时几分钟内不产生任何输出。自动检测会透明地处理这种情况。