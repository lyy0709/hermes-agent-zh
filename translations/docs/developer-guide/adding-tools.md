---
sidebar_position: 2
title: "添加工具"
description: "如何为 Hermes Agent 添加新工具 —— 包括模式定义、处理器、注册以及工具集"
---

# 添加工具

在编写工具之前，先问自己：**这应该是一个[技能](creating-skills.md)吗？**

:::warning 仅限内置核心工具
本页面适用于向代码仓库本身添加 **内置的 Hermes 工具**。
如果你想要一个个人的、项目本地的或其他自定义工具，而**不修改** Hermes 核心代码，请使用插件方式：

- [插件](/user-guide/features/plugins)
- [构建 Hermes 插件](/guides/build-a-hermes-plugin)

对于大多数自定义工具创建，请默认使用插件。只有当你明确想要在 `tools/` 和 `toolsets.py` 中发布一个新的内置工具时，才遵循本页面。
:::

当一个能力可以表达为指令 + shell 命令 + 现有工具时（例如 arXiv 搜索、git 工作流、Docker 管理、PDF 处理），将其设为 **技能**。

当一个能力需要与 API 密钥进行端到端集成、需要自定义处理逻辑、处理二进制数据或流式处理时（例如浏览器自动化、TTS、视觉分析），将其设为 **工具**。

## 概述

添加一个工具涉及 **2 个文件**：

1.  **`tools/your_tool.py`** — 处理器、模式定义、检查函数、`registry.register()` 调用
2.  **`toolsets.py`** — 将工具名称添加到 `_HERMES_CORE_TOOLS`（或特定的工具集）

任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会在启动时自动发现 —— 无需手动维护导入列表。

## 步骤 1：创建内置工具文件

每个工具文件都遵循相同的结构：

```python
# tools/weather_tool.py
"""Weather Tool -- look up current weather for a location."""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- 可用性检查 ---

def check_weather_requirements() -> bool:
    """Return True if the tool's dependencies are available."""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- 处理器 ---

def weather_tool(location: str, units: str = "metric") -> str:
    """Fetch weather for a location. Returns JSON string."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not configured"})
    try:
        # ... call weather API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- 模式定义 ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates (e.g. 'London' or '51.5,-0.1')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (default: metric)",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- 注册 ---

from tools.registry import registry

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool(
        location=args.get("location", ""),
        units=args.get("units", "metric")),
    check_fn=check_weather_requirements,
    requires_env=["WEATHER_API_KEY"],
)
```

### 关键规则

:::danger 重要
- 处理器 **必须** 返回一个 JSON 字符串（通过 `json.dumps()`），绝不能返回原始字典
- 错误 **必须** 以 `{"error": "message"}` 的形式返回，绝不能作为异常抛出
- `check_fn` 在构建工具定义时被调用 —— 如果它返回 `False`，该工具会被静默排除
- `handler` 接收 `(args: dict, **kwargs)` 参数，其中 `args` 是 LLM 的工具调用参数
:::

## 步骤 2：将内置工具添加到工具集

在 `toolsets.py` 中，添加工具名称：

```python
# 如果它应该在所有平台（CLI + 消息传递）上可用：
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- 在此处添加
]

# 或者创建一个新的独立工具集：
"weather": {
    "description": "Weather lookup tools",
    "tools": ["weather"],
    "includes": []
},
```

## ~~步骤 3：添加发现导入~~（不再需要）

包含顶层 `registry.register()` 调用的工具模块会被 `tools/registry.py` 中的 `discover_builtin_tools()` 自动发现。无需手动维护导入列表 —— 只需在 `tools/` 中创建你的文件，它就会在启动时被拾取。

## 异步处理器

如果你的处理器需要异步代码，请用 `is_async=True` 标记：

```python
async def weather_tool_async(location: str) -> str:
    async with aiohttp.ClientSession() as session:
        ...
    return json.dumps(result)

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool_async(args.get("location", "")),
    check_fn=check_weather_requirements,
    is_async=True,  # 注册表会自动调用 _run_async()
)
```

注册表透明地处理异步桥接 —— 你永远不需要自己调用 `asyncio.run()`。

## 需要 task_id 的处理器

管理每个会话状态的工具通过 `**kwargs` 接收 `task_id`：

```python
def _handle_weather(args, **kw):
    task_id = kw.get("task_id")
    return weather_tool(args.get("location", ""), task_id=task_id)

registry.register(
    name="weather",
    ...
    handler=_handle_weather,
)
```

## 被 Agent 循环拦截的工具

有些工具（`todo`、`memory`、`session_search`、`delegate_task`）需要访问每个会话的 Agent 状态。这些工具在到达注册表之前会被 `run_agent.py` 拦截。注册表仍然保存它们的模式定义，但如果绕过了拦截，`dispatch()` 会返回一个回退错误。

## 可选：设置向导集成

如果你的工具需要 API 密钥，请将其添加到 `hermes_cli/config.py`：

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "Weather API key for weather lookup",
        "prompt": "Weather API key",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## 检查清单

- [ ] 已创建包含处理器、模式定义、检查函数和注册的工具文件
- [ ] 已添加到 `toolsets.py` 中适当的工具集
- [ ] 已确认这确实应该是一个内置/核心工具，而不是一个插件
- [ ] 处理器返回 JSON 字符串，错误以 `{"error": "..."}` 形式返回
- [ ] 可选：已将 API 密钥添加到 `hermes_cli/config.py` 的 `OPTIONAL_ENV_VARS` 中
- [ ] 可选：已添加到 `toolset_distributions.py` 以进行批量处理
- [ ] 已使用 `hermes chat -q "Use the weather tool for London"` 测试