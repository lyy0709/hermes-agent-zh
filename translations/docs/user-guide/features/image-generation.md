---
title: 图像生成
description: 使用 FLUX 2 Pro 模型生成高质量图像，并通过 FAL.ai 自动进行超分辨率放大。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成

Hermes Agent 可以使用 FAL.ai 的 **FLUX 2 Pro** 模型从文本提示词生成图像，并通过 **Clarity Upscaler** 自动进行 2 倍超分辨率放大以提升画质。

## 设置

### 获取 FAL API 密钥

1. 在 [fal.ai](https://fal.ai/) 注册
2. 从您的控制面板生成 API 密钥

### 配置密钥

```bash
# 添加到 ~/.hermes/.env
FAL_KEY=your-fal-api-key-here
```

### 安装客户端库

```bash
pip install fal-client
```

:::info
当设置了 `FAL_KEY` 时，图像生成工具会自动可用。无需额外的工具集配置。
:::

## 工作原理

当您要求 Hermes 生成图像时：

1.  **生成** — 您的提示词被发送到 FLUX 2 Pro 模型 (`fal-ai/flux-2-pro`)
2.  **超分辨率放大** — 生成的图像自动使用 Clarity Upscaler (`fal-ai/clarity-upscaler`) 进行 2 倍放大
3.  **交付** — 返回放大后的图像 URL

如果超分辨率放大因任何原因失败，则会返回原始图像作为后备方案。

## 使用方法

只需要求 Hermes 创建图像：

```
生成一幅宁静的山景，带有樱花
```

```
创建一幅栖息在古老树枝上的智慧老猫头鹰的肖像
```

```
为我制作一幅带有飞行汽车和霓虹灯的未来主义城市景观
```

## 参数

`image_generate_tool` 接受以下参数：

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `prompt` | *(必需)* | — | 所需图像的文本描述 |
| `aspect_ratio` | `"landscape"` | `landscape`, `square`, `portrait` | 图像宽高比 |
| `num_inference_steps` | `50` | 1–100 | 去噪步数（越多=质量越高，越慢） |
| `guidance_scale` | `4.5` | 0.1–20.0 | 遵循提示词的紧密程度 |
| `num_images` | `1` | 1–4 | 要生成的图像数量 |
| `output_format` | `"png"` | `png`, `jpeg` | 图像文件格式 |
| `seed` | *(随机)* | 任意整数 | 用于可重现结果的随机种子 |

## 宽高比

该工具使用简化的宽高比名称，这些名称映射到 FLUX 2 Pro 的图像尺寸：

| 宽高比 | 映射到 | 最适合 |
|-------------|---------|----------|
| `landscape` | `landscape_16_9` | 壁纸、横幅、场景 |
| `square` | `square_hd` | 个人资料图片、社交媒体帖子 |
| `portrait` | `portrait_16_9` | 角色艺术、手机壁纸 |

:::tip
您也可以直接使用原始的 FLUX 2 Pro 尺寸预设：`square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`。也支持最大 2048x2048 的自定义尺寸。
:::

## 自动超分辨率放大

每张生成的图像都会使用 FAL.ai 的 Clarity Upscaler 自动进行 2 倍放大，设置如下：

| 设置项 | 值 |
|---------|-------|
| 放大倍数 | 2x |
| 创造力 | 0.35 |
| 相似度 | 0.6 |
| 引导尺度 | 4 |
| 推理步数 | 18 |
| 正向提示词 | `"masterpiece, best quality, highres"` + 您的原始提示词 |
| 负向提示词 | `"(worst quality, low quality, normal quality:2)"` |

超分辨率放大器在保留原始构图的同时增强细节和分辨率。如果超分辨率放大器失败（网络问题、速率限制），则会自动返回原始分辨率的图像。

## 示例提示词

以下是一些可以尝试的有效提示词：

```
一位粉色波波头、浓重眼线的女性的街头抓拍照
```

```
具有玻璃幕墙的现代建筑，日落光线
```

```
带有鲜艳色彩和几何图案的抽象艺术
```

```
栖息在古老树枝上的智慧老猫头鹰的肖像
```

```
带有飞行汽车和霓虹灯的未来主义城市景观
```

## 调试

启用图像生成的调试日志记录：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志保存到 `./logs/image_tools_debug_<session_id>.json`，包含每个生成请求、参数、时间以及任何错误的详细信息。

## 安全设置

图像生成工具默认在禁用安全检查的情况下运行 (`safety_tolerance: 5`，最宽松的设置)。这是在代码级别配置的，用户无法调整。

## 平台交付

生成的图像根据平台的不同以不同方式交付：

| 平台 | 交付方式 |
|----------|----------------|
| **CLI** | 图像 URL 以 Markdown `![description](url)` 格式打印 — 点击在浏览器中打开 |
| **Telegram** | 图像作为照片消息发送，提示词作为标题 |
| **Discord** | 图像嵌入在消息中 |
| **Slack** | 消息中包含图像 URL（Slack 会自动展开） |
| **WhatsApp** | 图像作为媒体消息发送 |
| **其他平台** | 纯文本中的图像 URL |

Agent 在其响应中使用 `MEDIA:<url>` 语法，平台适配器会将其转换为适当的格式。

## 限制

- **需要 FAL API 密钥** — 图像生成会在您的 FAL.ai 账户上产生 API 费用
- **无图像编辑功能** — 这仅是文生图，不支持局部重绘或图生图
- **基于 URL 的交付** — 图像以临时的 FAL.ai URL 形式返回，不保存在本地。URL 在一段时间后（通常是几小时）会过期
- **超分辨率放大增加延迟** — 自动 2 倍放大步骤增加了处理时间
- **每次请求最多 4 张图像** — `num_images` 上限为 4