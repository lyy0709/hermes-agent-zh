---
sidebar_position: 12
title: "视频生成提供商插件"
description: "如何为 Hermes Agent 构建视频生成后端插件"
---

# 构建视频生成提供商插件

视频生成提供商插件注册一个后端，用于处理每个 `video_generate` 工具调用。内置的提供商（xAI、FAL）以插件形式提供。通过将目录放入 `plugins/video_gen/<name>/` 来添加新的提供商插件，或覆盖捆绑的插件。

:::tip
视频生成插件几乎逐行镜像了[图像生成提供商插件](/developer-guide/image-gen-provider-plugin) —— 如果你已经构建过图像生成后端，那么你已经了解了其结构。主要区别在于：一个用于声明模态/宽高比/时长的 `capabilities()` 方法，以及一个路由约定（传递 `image_url` 以使用图像到视频，省略它则使用文本到视频 —— 提供商在内部选择正确的端点）。
:::

## 统一接口（一个工具，两种模态）

`video_generate` 工具通过一个参数暴露两种模态：

- **文本到视频** —— 仅使用 `prompt` 调用。提供商路由到其文本到视频端点。
- **图像到视频** —— 使用 `prompt` + `image_url` 调用。提供商路由到其图像到视频端点。

编辑和扩展功能被有意排除在范围之外。大多数后端不支持这些功能，这种不一致性将迫使每个后端的描述性文字进入 Agent 的工具描述中。

## 发现机制如何工作

Hermes 在三个位置扫描视频生成后端：

1. **捆绑的** —— `<repo>/plugins/video_gen/<name>/`（通过 `kind: backend` 自动加载）
2. **用户的** —— `~/.hermes/plugins/video_gen/<name>/`（通过 `plugins.enabled` 选择启用）
3. **Pip 安装的** —— 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数调用 `ctx.register_video_gen_provider(...)`。活动的提供商由 `config.yaml` 中的 `video_gen.provider` 选择；`hermes tools` → Video Generation 会引导用户完成选择。与 `image_generate` 不同，没有内置的遗留后端 —— 每个提供商都是一个插件。

## 目录结构

```
plugins/video_gen/my-backend/
├── __init__.py      # VideoGenProvider 子类 + register()
└── plugin.yaml      # 包含 kind: backend 的清单文件
```

## VideoGenProvider 抽象基类

继承 `agent.video_gen_provider.VideoGenProvider`。必需项：`name` 属性和 `generate()` 方法。

```python
# plugins/video_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.video_gen_provider import (
    VideoGenProvider,
    error_response,
    success_response,
)


class MyVideoGenProvider(VideoGenProvider):
    @property
    def name(self) -> str:
        return "my-backend"

    @property
    def display_name(self) -> str:
        return "My Backend"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self) -> List[Dict[str, Any]]:
        # 每个条目是一个模型系列 —— 用户只需选择一次的名称。
        # 你的提供商的 generate() 根据是否传递了 image_url 在系列内路由。
        return [
            {
                "id": "fast",
                "display": "Fast",
                "speed": "~30s",
                "strengths": "Cheapest tier",
                "price": "$0.05/s",
                "modalities": ["text", "image"],  # 建议性信息
            },
        ]

    def default_model(self) -> Optional[str]:
        return "fast"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "modalities": ["text", "image"],
            "aspect_ratios": ["16:9", "9:16"],
            "resolutions": ["720p", "1080p"],
            "min_duration": 1,
            "max_duration": 10,
            "supports_audio": False,
            "supports_negative_prompt": True,
            "max_reference_images": 0,
        }

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "My Backend",
            "badge": "paid",
            "tag": "在 `hermes tools` 中显示的简短描述",
            "env_vars": [
                {
                    "key": "MY_API_KEY",
                    "prompt": "My Backend API 密钥",
                    "url": "https://mybackend.example.com/keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        duration: Optional[int] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        negative_prompt: Optional[str] = None,
        audio: Optional[bool] = None,
        seed: Optional[int] = None,
        **kwargs: Any,  # 始终忽略未知的 kwargs 以保持向前兼容性
    ) -> Dict[str, Any]:
        # 路由：根据 image_url 的存在选择端点。
        if image_url:
            endpoint = "my-backend/image-to-video"
            modality_used = "image"
        else:
            endpoint = "my-backend/text-to-video"
            modality_used = "text"

        # ... 调用你的 API ...

        return success_response(
            video="https://your-cdn/output.mp4",
            model=model or "fast",
            prompt=prompt,
            modality=modality_used,
            aspect_ratio=aspect_ratio,
            duration=duration or 5,
            provider=self.name,
        )


def register(ctx) -> None:
    ctx.register_video_gen_provider(MyVideoGenProvider())
```

## 插件清单

```yaml
# plugins/video_gen/my-backend/plugin.yaml
name: my-backend
version: 1.0.0
description: "我的视频生成后端"
author: Your Name
kind: backend
requires_env:
  - MY_API_KEY
```

## `video_generate` 模式

该工具为每个后端暴露一个统一的模式。提供商忽略它们不支持的参数。

| 参数 | 作用 |
|---|---|
| `prompt` | 文本指令（必需） |
| `image_url` | 设置时 → 图像到视频；省略时 → 文本到视频 |
| `reference_image_urls` | 风格/角色参考（取决于提供商） |
| `duration` | 秒数 —— 提供商会进行限制 |
| `aspect_ratio` | `"16:9"`、`"9:16"`、`"1:1"`、... —— 提供商会进行限制 |
| `resolution` | `"480p"` / `"540p"` / `"720p"` / `"1080p"` —— 提供商会进行限制 |
| `negative_prompt` | 要避免的内容（仅 Pixverse/Kling） |
| `audio` | 原生音频（Veo3 / Pixverse 定价层级） |
| `seed` | 可重现性 |
| `model` | 覆盖活动模型/系列 |

提供商的 `capabilities()` 声明了支持哪些参数。Agent 在工具描述中看到活动后端的支持能力，当用户通过 `hermes tools` 更改后端时，描述会动态重建。

## 模型系列和端点路由（FAL 模式）

当你的后端每个“模型”有多个端点时 —— 例如 FAL，其中每个系列（Veo 3.1、Pixverse v6、Kling O3）都有一个 `/text-to-video` 和一个 `/image-to-video` URL —— 将每个**系列**表示为一个目录条目。你的 `generate()` 根据是否传递了 `image_url` 来选择正确的端点：

```python
FAMILIES = {
    "veo3.1": {
        "text_endpoint": "fal-ai/veo3.1",
        "image_endpoint": "fal-ai/veo3.1/image-to-video",
        # ... 系列特定的能力标志 ...
    },
}

def generate(self, prompt, *, image_url=None, model=None, **kwargs):
    family_id, family = _resolve_family(model)
    endpoint = family["image_endpoint"] if image_url else family["text_endpoint"]
    # ... 根据系列声明的能力标志构建有效载荷，调用端点 ...
```

用户在 `hermes tools` 中一次性选择 `veo3.1`。Agent 从不考虑端点 —— 它只是传递（或不传递）`image_url`。

## 选择优先级

对于每个实例的模型旋钮（参见 `plugins/video_gen/fal/__init__.py`）：

1. 工具调用中的 `model=` 关键字
2. `<PROVIDER>_VIDEO_MODEL` 环境变量
3. `config.yaml` 中的 `video_gen.<provider>.model`
4. `config.yaml` 中的 `video_gen.model`（当它是你的 ID 之一时）
5. 提供商的 `default_model()`

## 响应格式

`success_response()` 和 `error_response()` 生成每个后端返回的字典格式。使用它们 —— 不要手动构建字典。

成功键：`success`、`video`（URL 或绝对路径）、`model`、`prompt`、`modality`（`"text"` 或 `"image"`）、`aspect_ratio`、`duration`、`provider`，以及 `extra`。

错误键：`success`、`video`（None）、`error`、`error_type`、`model`、`prompt`、`aspect_ratio`、`provider`。

## 保存生成物件的路径

如果你的后端返回 base64，使用 `save_b64_video()` 将其写入 `$HERMES_HOME/cache/videos/` 下。对于通过后续 HTTP 获取的原始字节，使用 `save_bytes_video()`。否则直接返回上游 URL —— 消息网关在交付时会解析远程 URL。

## 测试

在 `tests/plugins/video_gen/test_<name>_plugin.py` 下放置一个冒烟测试。xAI 和 FAL 的测试展示了模式 —— 注册、验证目录、使用和不使用 `image_url` 进行路由测试、断言在缺少认证时返回清晰的错误响应。