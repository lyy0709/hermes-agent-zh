---
title: 图像生成
description: 通过 FAL.ai 生成图像 —— 支持 11 种模型，包括 FLUX 2、GPT Image (1.5 & 2)、Nano Banana Pro、Ideogram、Recraft V4 Pro、Krea 2 等，可通过 `hermes tools` 选择。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成

Hermes Agent 通过 FAL.ai 从文本提示词生成图像。开箱即用支持 11 种模型，每种模型在速度、质量和成本之间有不同的权衡。可通过 `hermes tools` 配置活动模型，并持久化保存在 `config.yaml` 中。

## 支持的模型

| 模型 | 速度 | 优势 | 价格 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `<1s` | 快速，清晰的文本 | $0.006/MP |
| `fal-ai/flux-2-pro` | ~6s | 工作室级照片写实 | $0.03/MP |
| `fal-ai/z-image/turbo` | ~2s | 中英双语，6B 参数 | $0.005/MP |
| `fal-ai/nano-banana-pro` | ~8s | Gemini 3 Pro，推理深度，文本渲染 | $0.15/张 (1K) |
| `fal-ai/gpt-image-1.5` | ~15s | 提示词遵循度 | $0.034/张 |
| `fal-ai/gpt-image-2` | ~20s | SOTA 文本渲染 + CJK，世界感知的照片写实 | $0.04–0.06/张 |
| `fal-ai/ideogram/v3` | ~5s | 最佳字体排版 | $0.03–0.09/张 |
| `fal-ai/recraft/v4/pro/text-to-image` | ~8s | 设计，品牌系统，生产就绪 | $0.25/张 |
| `fal-ai/qwen-image` | ~12s | 基于 LLM，复杂文本 | $0.02/MP |
| `fal-ai/krea/v2/medium/text-to-image` | ~15-25s | 插画，动漫，绘画，富有表现力/艺术风格 | $0.030–0.035/张 |
| `fal-ai/krea/v2/large/text-to-image` | ~25-60s | 照片写实，原始质感外观（运动模糊，颗粒，胶片） | $0.060–0.065/张 |

价格为撰写本文时 FAL 的定价；请查看 [fal.ai](https://fal.ai/) 获取当前价格。

## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，您可以通过 **[Tool Gateway](tool-gateway.md)** 使用图像生成功能，而无需 FAL API 密钥。您的模型选择在两个路径中都会持久化。新安装可以通过运行 `hermes setup --portal` 登录并一次性开启所有网关工具；现有安装可以通过 `hermes tools` 选择 **Nous Subscription** 作为图像生成后端。

如果托管网关针对特定模型返回 `HTTP 4xx`，则表示该模型尚未在门户端代理 —— Agent 会告知您，并提供补救步骤（设置 `FAL_KEY` 以直接访问，或选择其他模型）。
:::

### 获取 FAL API 密钥

1. 在 [fal.ai](https://fal.ai/) 注册
2. 从您的仪表板生成 API 密钥

### 配置并选择模型

运行工具命令：

```bash
hermes tools
```

导航到 **🎨 Image Generation**，选择您的后端（Nous Subscription 或 FAL.ai），然后选择器会显示所有支持的模型，以列对齐的表格呈现 —— 使用方向键导航，按 Enter 键选择：

```
  Model                          Speed    Strengths                    Price
  fal-ai/flux-2/klein/9b         <1s      Fast, crisp text             $0.006/MP   ← currently in use
  fal-ai/flux-2-pro              ~6s      Studio photorealism          $0.03/MP
  fal-ai/z-image/turbo           ~2s      Bilingual EN/CN, 6B          $0.005/MP
  ...
```

您的选择将保存到 `config.yaml`：

```yaml
image_gen:
  model: fal-ai/flux-2/klein/9b
  use_gateway: false            # 如果使用 Nous Subscription 则为 true
```

### GPT-Image 质量

`fal-ai/gpt-image-1.5` 和 `fal-ai/gpt-image-2` 的请求质量固定为 `medium`（约 $0.034–$0.06/张，1024×1024）。我们不向用户暴露 `low` / `high` 等级选项，以便 Nous Portal 的计费对所有用户保持可预测性 —— 不同等级之间的成本差异为 3–22 倍。如果您想要更便宜的选项，请选择 Klein 9B 或 Z-Image Turbo；如果您想要更高质量，请使用 Nano Banana Pro 或 Recraft V4 Pro。

## 使用

面向 Agent 的模式有意保持最小化 —— 模型会使用您配置的任何设置：

```
生成一幅宁静的山景，带有樱花
```

```
创建一个方形肖像，描绘一只睿智的老猫头鹰 —— 使用字体排版模型
```

```
为我制作一个未来主义的城市景观，横向构图
```

## 宽高比

从 Agent 的角度来看，每个模型都接受相同的三种宽高比。在内部，每个模型的原生尺寸规格会自动填充：

| Agent 输入 | image_size (flux/z-image/qwen/recraft/ideogram) | aspect_ratio (nano-banana-pro) | image_size (gpt-image-1.5) | image_size (gpt-image-2) |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3` (1024×768) |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd` (1024×1024) |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3` (768×1024) |

GPT Image 2 映射到 4:3 预设，而不是 16:9，因为其最小像素数为 655,360 —— `landscape_16_9` 预设（1024×576 = 589,824）会被拒绝。

此转换发生在 `_build_fal_payload()` 中 —— Agent 代码永远不需要了解每个模型的模式差异。

## 自动放大

通过 FAL 的 **Clarity Upscaler** 进行放大是按模型门控的：

| 模型 | 放大？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 向后兼容（曾是选择器之前的默认设置） |
| 所有其他模型 | ✗ | 快速模型会失去其亚秒级的价值主张；高分辨率模型不需要它 |

当放大运行时，使用以下设置：

| 设置 | 值 |
|---|---|
| 放大倍数 | 2× |
| 创造力 | 0.35 |
| 相似度 | 0.6 |
| 引导尺度 | 4 |
| 推理步数 | 18 |

如果放大失败（网络问题，速率限制），则会自动返回原始图像。

## 内部工作原理

1.  **模型解析** — `_resolve_fal_model()` 从 `config.yaml` 读取 `image_gen.model`，回退到 `FAL_IMAGE_MODEL` 环境变量，然后回退到 `fal-ai/flux-2/klein/9b`。
2.  **负载构建** — `_build_fal_payload()` 将您的 `aspect_ratio` 转换为模型的原生格式（预设枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用任何调用方覆盖，然后过滤到模型的 `supports` 白名单，以便永远不会发送不支持的键。
3.  **提交** — `_submit_fal_request()` 通过直接的 FAL 凭据或托管的 Nous 网关路由。
4.  **放大** — 仅当模型的元数据具有 `upscale: True` 时才运行。
5.  **交付** — 最终图像 URL 返回给 Agent，Agent 发出一个 `MEDIA:<url>` 标签，平台适配器会将其转换为原生媒体。

## 调试

启用调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会输出到 `./logs/image_tools_debug_<session_id>.json`，包含每次调用的详细信息（模型、参数、时间、错误）。

## 平台交付

| 平台 | 交付方式 |
|---|---|
| **CLI** | 图像 URL 以 Markdown `![](url)` 格式打印 —— 点击打开 |
| **Telegram** | 照片消息，提示词作为标题 |
| **Discord** | 嵌入在消息中 |
| **Slack** | URL 由 Slack 展开 |
| **WhatsApp** | 媒体消息 |
| **其他** | 纯文本中的 URL |

## 限制

*   **需要 FAL 凭据**（直接的 `FAL_KEY` 或 Nous Subscription）
*   **仅限文本到图像** —— 此工具不支持修复、图像到图像或编辑
*   **临时 URL** —— FAL 返回的托管 URL 在数小时/数天后过期；如有需要请本地保存
*   **每个模型的约束** —— 某些模型不支持 `seed`、`num_inference_steps` 等。`supports` 过滤器会静默丢弃不支持的参数；这是预期行为