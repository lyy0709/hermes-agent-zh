---
sidebar_position: 12
title: "Web 搜索提供商插件"
description: "如何为 Hermes Agent 构建一个 web 搜索/提取/深度抓取后端插件"
---

# 构建 Web 搜索提供商插件

Web 搜索提供商插件注册一个后端，用于处理 `web_search`、`web_extract` 以及（可选的）深度抓取工具调用。内置的提供商 —— Firecrawl、SearXNG、Tavily、Exa、Parallel、Brave Search（免费版）、xAI 和 DDGS —— 都以插件形式打包在 `plugins/web/<name>/` 目录下。您可以通过在它们旁边放置一个目录来添加新的提供商，或者覆盖捆绑的提供商。

:::tip
Web 搜索是 Hermes 支持的几种**后端插件**之一。其他插件（有各自的抽象基类）包括：[图像生成提供商插件](/developer-guide/image-gen-provider-plugin)、[视频生成提供商插件](/developer-guide/video-gen-provider-plugin)、[记忆提供商插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin) 和 [模型提供商插件](/developer-guide/model-provider-plugin)。通用工具/钩子/CLI 插件位于 [构建 Hermes 插件](/guides/build-a-hermes-plugin) 中。
:::

## 发现机制如何工作

Hermes 在三个位置扫描 Web 搜索后端：

1.  **捆绑插件** — `<repo>/plugins/web/<name>/`（自动加载，`kind: backend`，始终可用）
2.  **用户插件** — `~/.hermes/plugins/web/<name>/`（通过 `plugins.enabled` 或 `hermes plugins enable <name>` 选择启用）
3.  **Pip 包** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数会调用 `ctx.register_web_search_provider(...)` —— 这将实例放入 `agent/web_search_registry.py` 中的注册表。每个功能的活动提供商由配置选择：

| 功能 | 配置键 | 回退到 |
|---|---|---|
| `web_search` | `web.search_backend` | `web.backend` |
| `web_extract` | `web.extract_backend` | `web.backend` |
| `web_extract` 内部的深度抓取模式 | `web.extract_backend` | `web.backend` |

当两个键都未设置时，Hermes 会根据环境中存在的 API 密钥/URL 自动检测后端。`hermes tools` 会引导用户完成选择。

## 目录结构

```
plugins/web/my-backend/
├── __init__.py     # register() 入口点
├── provider.py     # WebSearchProvider 子类
└── plugin.yaml     # 包含 kind: backend 和 provides_web_providers 的清单
```

`brave_free/` 和 `ddgs/` 是代码库中最小的参考实现 —— `brave_free` 用于需要 API 密钥的仅搜索提供商，`ddgs` 用于无需密钥、惰性安装其 SDK 的提供商。

## WebSearchProvider 抽象基类

继承 `agent.web_search_provider.WebSearchProvider`。唯一必需的成员是 `name`、`is_available()` 以及您实现的 `search()` / `extract()` / `crawl()` 中的任意一个。

```python
# plugins/web/my-backend/provider.py
from __future__ import annotations

import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider


class MyBackendWebSearchProvider(WebSearchProvider):
    """针对 My Backend HTTP API 的最小化仅搜索提供商。"""

    @property
    def name(self) -> str:
        # 在 web.search_backend / web.extract_backend / web.backend 配置键中使用的稳定 ID。
        # 小写，无空格；允许连字符。
        return "my-backend"

    @property
    def display_name(self) -> str:
        # 在 `hermes tools` 中显示的人类可读标签。默认为 `name`。
        return "My Backend"

    def is_available(self) -> bool:
        # 廉价检查 —— 环境变量存在、可选依赖可导入等。
        # 禁止进行网络调用（在每次 `hermes tools` 绘制时运行）。
        return bool(os.getenv("MY_BACKEND_API_KEY", "").strip())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        import httpx

        api_key = os.environ["MY_BACKEND_API_KEY"]
        try:
            resp = httpx.get(
                "https://api.example.com/search",
                params={"q": query, "count": max(1, min(int(limit), 20))},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            return {"success": False, "error": str(exc)}

        # 响应格式是固定的 —— 参见下面的“响应格式”。
        return {
            "success": True,
            "data": {
                "web": [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("snippet", ""),
                        "position": idx + 1,
                    }
                    for idx, item in enumerate(data.get("results", []))
                ],
            },
        }
```

```python
# plugins/web/my-backend/__init__.py
from plugins.web.my_backend.provider import MyBackendWebSearchProvider


def register(ctx) -> None:
    """插件入口点 —— 在加载时调用一次。"""
    ctx.register_web_search_provider(MyBackendWebSearchProvider())
```

## plugin.yaml

```yaml
name: web-my-backend
version: 1.0.0
description: "My Backend web 搜索 —— Bearer 认证 REST API"
author: Your Name
kind: backend
provides_web_providers:
  - my-backend
requires_env:
  - MY_BACKEND_API_KEY
```

| 键 | 用途 |
|---|---|
| `kind: backend` | 将插件路由到后端加载路径 |
| `provides_web_providers` | 此插件注册的提供商 `name` 列表 —— 加载器使用此列表在 `hermes tools` 中宣传插件，甚至在 `register()` 运行之前 |
| `requires_env` | 在 `hermes plugins install` 期间交互式提示输入凭据（有关丰富格式，请参阅 [构建 Hermes 插件](/guides/build-a-hermes-plugin#gate-on-environment-variables)） |

## 抽象基类参考

完整契约在 `agent/web_search_provider.py` 中。您可以重写的方法：

| 成员 | 必需 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 在 `web.*_backend` 配置中使用的稳定 ID |
| `display_name` | — | `name` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | ✅ | — | 廉价的可用性检查 —— 环境变量、可选依赖 |
| `supports_search()` | — | `True` | `web_search` 路由的能力标志 |
| `supports_extract()` | — | `False` | `web_extract` 路由的能力标志 |
| `search(query, limit)` | 条件性 | 抛出异常 | 当 `supports_search()` 返回 `True` 时必需 |
| `extract(urls, **kwargs)` | 条件性 | 抛出异常 | 当 `supports_extract()` 返回 `True` 时必需 |

提供商可以在单个类中宣传多种功能 —— Firecrawl、Tavily、Exa 和 Parallel 都实现了搜索和提取。Brave Search 和 DDGS 是仅搜索的；SearXNG 是仅搜索的，并记录了“与提取提供商配对使用”的工作流。

## 响应格式

工具包装器期望一个固定的信封格式，这样它就不需要在后端之间进行转换。

**搜索成功：**

```python
{
    "success": True,
    "data": {
        "web": [
            {"title": str, "url": str, "description": str, "position": int},
            ...
        ],
    },
}
```

**提取成功：**

```python
{
    "success": True,
    "data": [
        {
            "url": str,
            "title": str,
            "content": str,
            "raw_content": str,
            "metadata": dict,    # 可选
            "error": str,        # 可选，仅在每个 URL 失败时出现
        },
        ...
    ],
}
```

**任一功能，失败时：**

```python
{"success": False, "error": "人类可读的消息"}
```

`search()` 和 `extract()` 都可以是 `async def` —— 调度器通过 `inspect.iscoroutinefunction` 检测协程函数并相应地进行等待。对于小型后端，执行阻塞 I/O（HTTP、SDK 调用）的同步实现是可以的；调度器会处理线程。

## 能力标志

Hermes 根据 `supports_*` 标志将调用路由到正确的提供商。常见的多提供商设置：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "brave-free"     # 仅搜索，快速，免费 2k/月
  extract_backend: "firecrawl"     # 提取 + 抓取，付费配额
```

当 `web.search_backend` 或 `web.extract_backend` 未设置时，两者都会回退到 `web.backend`。当该值也未设置时，Hermes 会根据环境变量的存在情况，选择第一个支持所请求功能的可用提供商。

如果您的提供商仅支持一种功能，请将其他标志保留为默认值（`False`），注册表将跳过该工具 —— 当用户仅将 X 用于搜索并要求 Agent 提取时，他们不会看到误导性的“提供商 X 失败”错误。

## Hermes 如何将其连接到工具

`web_search` 和 `web_extract` 工具位于 `tools/web_tools.py` 中。在调用时，它们：

1.  读取相关的配置键（`web_search` 对应 `web.search_backend`，`web_extract` 对应 `web.extract_backend`）
2.  向注册表请求具有该 `name` 的提供商
3.  检查 `is_available()` 和匹配的 `supports_*()` 标志
4.  分派到 `search()` / `extract()` / `crawl()`，如果方法是协程则等待
5.  JSON 序列化响应信封并将其交还给 LLM

错误会作为工具结果出现；LLM 决定如何解释它们。如果没有注册提供商（或者每个可用提供商都未通过能力检查），工具会返回一个有用的错误，指向 `hermes tools`。

## 惰性安装可选依赖

如果您的提供商包装了第三方 SDK（就像 DDGS 使用 `ddgs` 包那样），请不要在模块顶层 `import` 它。在 `is_available()` 或 `search()` 内部使用 `tools.lazy_deps.ensure(...)` —— Hermes 将在首次使用时安装该包，由 `security.allow_lazy_installs` 控制。有关安全模型，请参阅 [构建 Hermes 插件 → 惰性安装](/guides/build-a-hermes-plugin#lazy-install-optional-python-dependencies)。

## 参考实现

-   **`plugins/web/brave_free/`** —— 小型、需要 API 密钥、仅搜索的 HTTP 提供商。良好的起始模板。
-   **`plugins/web/ddgs/`** —— 无需密钥、惰性安装其 SDK 的提供商。对于包装 Python 包的后端很有用的模式。
-   **`plugins/web/firecrawl/`** —— 完整的多功能提供商（搜索 + 提取 + 抓取），具有多种格式模式。
-   **`plugins/web/searxng/`** —— 自托管、URL 配置的后端，无需认证。
-   **`plugins/web/xai/`** —— 通过 Grok 的服务器端 `web_search` 工具进行 LLM 支持的搜索。展示了如何重用现有的 OAuth/环境变量凭据界面（`tools/xai_http.py`）而不添加新的环境变量，以及如何编写一个廉价的 `is_available()` 来遵守无网络契约。

## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-web = "my_backend_web_package"
```

`my_backend_web_package` 必须暴露一个顶层的 `register` 函数。有关完整设置，请参阅通用插件指南中的 [通过 pip 分发](/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

-   [Web 搜索](/user-guide/features/web-search) —— 面向用户的功能文档和每个后端的配置
-   [插件概述](/user-guide/features/plugins) —— 所有插件类型一览
-   [构建 Hermes 插件](/guides/build-a-hermes-plugin) —— 通用工具/钩子/斜杠命令指南