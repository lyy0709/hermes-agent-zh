---
sidebar_position: 11
title: "图像生成提供商插件"
description: "如何为 Hermes Agent 构建图像生成后端插件"
---

# 构建图像生成提供商插件

图像生成提供商插件注册一个后端，用于处理每个 `image_generate` 工具调用——DALL·E、gpt-image、Grok、Flux、Imagen、Stable Diffusion、fal、Replicate、本地 ComfyUI 设备，任何后端。内置的提供商（OpenAI、OpenAI-Codex、xAI）都以插件形式提供。你可以通过将目录放入 `plugins/image_gen/<name>/` 来添加新的提供商，或覆盖捆绑的提供商。

:::tip
图像生成是 Hermes 支持的几种**后端插件**之一。其他（具有更专业 ABC 的）插件包括：[记忆提供商插件](/docs/developer-guide/memory-provider-plugin)、[上下文引擎插件](/docs/developer-guide/context-engine-plugin) 和 [模型提供商插件](/docs/developer-guide/model-provider-plugin)。通用工具/钩子/CLI 插件位于 [构建 Hermes 插件](/docs/guides/build-a-hermes-plugin)。
:::

## 发现机制如何工作

Hermes 在三个位置扫描图像生成后端：

1. **捆绑插件** — `<repo>/plugins/image_gen/<name>/`（自动加载，`kind: backend`，始终可用）
2. **用户插件** — `~/.hermes/plugins/image_gen/<name>/`（通过 `plugins.enabled` 选择启用）
3. **Pip 包** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数调用 `ctx.register_image_gen_provider(...)` —— 这将其放入 `agent/image_gen_registry.py` 中的注册表。活动提供商由 `config.yaml` 中的 `image_gen.provider` 选择；`hermes tools` 引导用户完成选择。

`image_generate` 工具包装器向注册表请求活动提供商并分派到那里。如果没有注册提供商，该工具会显示一个有用的错误，指向 `hermes tools`。

## 目录结构

```
plugins/image_gen/my-backend/
├── __init__.py      # ImageGenProvider 子类 + register()
└── plugin.yaml      # 包含 kind: backend 的清单
```

捆绑插件到此为止就完成了。位于 `~/.hermes/plugins/image_gen/<name>/` 的用户插件需要添加到 `config.yaml` 中的 `plugins.enabled`（或运行 `hermes plugins enable <name>`）。

## ImageGenProvider ABC

子类化 `agent.image_gen_provider.ImageGenProvider`。唯一必需的成员是 `name` 属性和 `generate()` 方法 —— 其他所有内容都有合理的默认值：

```python
# plugins/image_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)


class MyBackendImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        # 在 image_gen.provider 配置中使用的稳定 ID。小写，无空格。
        return "my-backend"

    @property
    def display_name(self) -> str:
        # 在 `hermes tools` 中显示的人类可读标签。如果省略，默认为 name.title()。
        return "My Backend"

    def is_available(self) -> bool:
        # 如果凭据或依赖项缺失，则返回 False。
        # 工具的可用性检查门在分派前调用此方法。
        if not os.environ.get("MY_BACKEND_API_KEY"):
            return False
        try:
            import my_backend_sdk  # noqa: F401
        except ImportError:
            return False
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        # 在 `hermes tools` 模型选择器中显示的目录。
        return [
            {
                "id": "my-model-fast",
                "display": "My Model (Fast)",
                "speed": "~5s",
                "strengths": "Quick iteration",
                "price": "$0.01/image",
            },
            {
                "id": "my-model-hq",
                "display": "My Model (HQ)",
                "speed": "~30s",
                "strengths": "Highest fidelity",
                "price": "$0.04/image",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "my-model-fast"

    def get_setup_schema(self) -> Dict[str, Any]:
        # `hermes tools` 选择器的元数据 —— 设置时需要提示的键。
        return {
            "name": "My Backend",
            "badge": "paid",        # 可选；在选择器中显示为短标签
            "tag": "One-line description shown under the name",
            "env_vars": [
                {
                    "key": "MY_BACKEND_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://my-backend.example.com/api-keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect_ratio = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="Prompt is required",
                error_type="invalid_input",
                provider=self.name,
                prompt="",
                aspect_ratio=aspect_ratio,
            )

        # 模型选择优先级：环境变量 → 配置 → 默认值。内置 openai 插件中的辅助函数
        # _resolve_model() 是一个很好的参考。
        model_id = kwargs.get("model") or self.default_model() or "my-model-fast"

        try:
            import my_backend_sdk
            client = my_backend_sdk.Client(api_key=os.environ["MY_BACKEND_API_KEY"])
            result = client.generate(
                prompt=prompt,
                model=model_id,
                aspect_ratio=aspect_ratio,
            )

            # 支持两种格式：
            #   - URL 字符串：将其作为 `image` 返回
            #   - base64 数据：通过 save_b64_image() 保存到 $HERMES_HOME/cache/images/ 下
            if result.get("image_b64"):
                path = save_b64_image(
                    result["image_b64"],
                    prefix=self.name,
                    extension="png",
                )
                image = str(path)
            else:
                image = result["image_url"]

            return success_response(
                image=image,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                provider=self.name,
            )
        except Exception as exc:
            return error_response(
                error=str(exc),
                error_type=type(exc).__name__,
                provider=self.name,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
            )


def register(ctx) -> None:
    """插件入口点 —— 在加载时调用一次。"""
    ctx.register_image_gen_provider(MyBackendImageGenProvider())
```

## plugin.yaml

```yaml
name: my-backend
version: 1.0.0
description: My image backend — text-to-image via My Backend SDK
author: Your Name
kind: backend
requires_env:
  - MY_BACKEND_API_KEY
```

`kind: backend` 是将插件路由到图像生成注册路径的原因。`requires_env` 在 `hermes plugins install` 期间会提示。

## ABC 参考

完整契约在 `agent/image_gen_provider.py` 中。你通常需要重写的方法：

| 成员 | 必需 | 默认值 | 目的 |
|---|---|---|---|
| `name` | ✅ | — | 在 `image_gen.provider` 配置中使用的稳定 ID |
| `display_name` | — | `name.title()` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | — | `True` | 用于检查缺失凭据/依赖项的门 |
| `list_models()` | — | `[]` | 用于 `hermes tools` 模型选择器的目录 |
| `default_model()` | — | `list_models()` 中的第一个 | 未配置模型时的后备 |
| `get_setup_schema()` | — | 最小化 | 选择器元数据 + 环境变量提示 |
| `generate(prompt, aspect_ratio, **kwargs)` | ✅ | — | 调用 |

## 响应格式

`generate()` 必须返回一个通过 `success_response()` 或 `error_response()` 构建的字典。两者都位于 `agent/image_gen_provider.py` 中。

**成功：**
```python
success_response(
    image=<url-or-absolute-path>,
    model=<model-id>,
    prompt=<echoed-prompt>,
    aspect_ratio="landscape" | "square" | "portrait",
    provider=<your-provider-name>,
    extra={...},  # 可选的后端特定字段
)
```

**错误：**
```python
error_response(
    error="human-readable message",
    error_type="provider_error" | "invalid_input" | "<exception class name>",
    provider=<your-provider-name>,
    model=<model-id>,
    prompt=<prompt>,
    aspect_ratio=<resolved aspect>,
)
```

工具包装器将字典 JSON 序列化并交给 LLM。错误作为工具结果显示；LLM 决定如何向用户解释它们。

## 处理 base64 与 URL 输出

一些后端返回图像 URL（fal、Replicate）；另一些返回 base64 负载（OpenAI gpt-image-2）。对于 base64 情况，使用 `save_b64_image()` —— 它将写入 `$HERMES_HOME/cache/images/<prefix>_<timestamp>_<uuid>.<ext>` 并返回绝对 `Path`。将该路径（作为 `str`）作为 `success_response()` 中的 `image=` 传递。消息网关传递（Telegram 照片气泡、Discord 附件）能识别 URL 和绝对路径。

## 用户覆盖

将用户插件放在 `~/.hermes/plugins/image_gen/<name>/`，其 `name` 属性与捆绑插件相同，并通过 `hermes plugins enable <name>` 启用 —— 注册表遵循“后写优先”原则，因此你的版本会替换内置版本。这对于将 `openai` 插件指向私有代理，或换入自定义模型目录很有用。

## 测试

```bash
export HERMES_HOME=/tmp/hermes-imggen-test
mkdir -p $HERMES_HOME/plugins/image_gen/my-backend
# …将 __init__.py + plugin.yaml 复制到该目录…

export MY_BACKEND_API_KEY=your-test-key
hermes plugins enable my-backend

# 将其选为活动提供商
echo "image_gen:" >> $HERMES_HOME/config.yaml
echo "  provider: my-backend" >> $HERMES_HOME/config.yaml

# 测试它
hermes -z "Generate an image of a corgi in a spacesuit"
```

或交互式：`hermes tools` → "Image Generation" → 选择 `my-backend` → 如果提示则输入 API 密钥。

## 参考实现

- **`plugins/image_gen/openai/__init__.py`** — gpt-image-2 的低/中/高等级作为三个虚拟模型 ID，共享一个具有不同 `quality` 参数的 API 模型。在单一后端下分层模型 + config.yaml 优先级链的良好示例。
- **`plugins/image_gen/xai/__init__.py`** — 通过 xAI 的 Grok Imagine。不同的格式（URL 输出，更简单的目录）。
- **`plugins/image_gen/openai-codex/__init__.py`** — Codex 风格的 Responses API 变体，重用 OpenAI SDK 但使用不同的路由基础 URL。

## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-imggen = "my_backend_imggen_package"
```

`my_backend_imggen_package` 必须公开一个顶层的 `register` 函数。有关完整设置，请参阅通用插件指南中的 [通过 pip 分发](/docs/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

- [图像生成](/docs/user-guide/features/image-generation) —— 面向用户的功能文档
- [插件概述](/docs/user-guide/features/plugins) —— 所有插件类型一览
- [构建 Hermes 插件](/docs/guides/build-a-hermes-plugin) —— 通用工具/钩子/斜杠命令指南