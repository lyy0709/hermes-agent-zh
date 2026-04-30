---
sidebar_position: 9
---

# 添加平台适配器

本指南介绍如何向 Hermes 消息网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、企业微信等），以便用户可以通过该服务与 Agent 交互。

:::tip
添加平台有两种方式：
- **插件方式**（推荐社区/第三方使用）：将插件目录放入 `~/.hermes/plugins/` —— 无需修改任何核心代码。请参阅下面的[插件路径](#插件路径推荐)。
- **内置方式**：修改代码、配置和文档中的 20 多个文件。使用下面的[内置清单](#逐步检查清单)。
:::

## 架构概述

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ 网关运行器 ↔ AI Agent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*(抽象方法)*
- **`disconnect()`** — 清理并关闭连接 *(抽象方法)*
- **`send()`** — 向聊天发送文本消息 *(抽象方法)*
- **`send_typing()`** — 显示“正在输入”指示器（可选覆盖）
- **`get_chat_info()`** — 返回聊天元数据（可选覆盖）

入站消息由适配器接收，并通过 `self.handle_message(event)` 转发，基类会将其路由到网关运行器。

## 插件路径（推荐）

插件系统允许您在不修改任何 Hermes 核心代码的情况下添加平台适配器。您的插件是一个包含两个文件的目录：

```
~/.hermes/plugins/my-platform/
  PLUGIN.yaml      # 插件元数据
  adapter.py       # 适配器类 + register() 入口点
```

### PLUGIN.yaml

```yaml
name: my-platform
version: 1.0.0
description: My custom messaging platform adapter
requires_env:
  - MY_PLATFORM_TOKEN
  - MY_PLATFORM_CHANNEL
```

### adapter.py

```python
import os
from gateway.platforms.base import (
    BasePlatformAdapter, SendResult, MessageEvent, MessageType,
)
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self) -> bool:
        # Connect to the platform API, start listeners
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}


def check_requirements() -> bool:
    return bool(os.getenv("MY_PLATFORM_TOKEN"))


def validate_config(config) -> bool:
    extra = getattr(config, "extra", {}) or {}
    return bool(os.getenv("MY_PLATFORM_TOKEN") or extra.get("token"))


def register(ctx):
    """Plugin entry point — called by the Hermes plugin system."""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # Per-platform user authorization env vars
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # Message length limit for smart chunking (0 = no limit)
        max_message_length=4000,
        # LLM guidance injected into system prompt
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
        ),
        # Display
        emoji="💬",
    )

    # Optional: register platform-specific tools
    ctx.register_tool(
        name="my_platform_search",
        toolset="my_platform",
        schema={...},
        handler=my_search_handler,
    )
```

### 配置

用户在 `config.yaml` 中配置平台：

```yaml
gateway:
  platforms:
    my_platform:
      enabled: true
      extra:
        token: "..."
        channel: "#general"
```

或者通过环境变量配置（适配器在 `__init__` 中读取）。

### 插件系统自动处理的内容

当您调用 `ctx.register_platform()` 时，以下集成点会自动为您处理 —— 无需修改核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 在内置的 if/elif 链之前检查注册表 |
| 配置解析 | `Platform._missing_()` 接受任何平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` |
| 用户授权 | 检查 `allowed_users_env` / `allow_all_env` |
| 定时任务投递 | `Platform()` 解析任何已注册的名称 |
| send_message 工具 | 通过活动的网关适配器路由 |
| Webhook 跨平台投递 | 检查注册表以识别已知平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 插件平台包含在枚举中 |
| 系统提示词提示 | `platform_hint` 注入到 LLM 上下文中 |
| 消息分块 | `max_message_length` 用于智能分割 |
| PII 脱敏 | `pii_safe` 标志 |
| `hermes status` | 显示带有 `(plugin)` 标签的插件平台 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台出现在每平台配置中 |
| Token 锁（多配置文件） | 在您的 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 插件缺失时提供描述性日志 |

### 参考实现

请参阅仓库中的 `plugins/platforms/irc/` 获取一个完整的工作示例 —— 一个零外部依赖的完整异步 IRC 适配器。

---

## 逐步检查清单（内置路径）

:::note
此清单适用于将平台直接添加到 Hermes 核心代码库 —— 通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#插件路径推荐)。
:::
### 1. 平台枚举

在 `gateway/config.py` 的 `Platform` 枚举中添加你的平台：

```python
class Platform(str, Enum):
    # ... 现有平台 ...
    NEWPLAT = "newplat"
```

### 2. 适配器文件

创建 `gateway/platforms/newplat.py`：

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

def check_newplat_requirements() -> bool:
    """如果依赖项可用则返回 True。"""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # 从 config.extra 字典读取配置
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self) -> bool:
        # 建立连接，开始轮询/webhook
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._running = False
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # 通过平台 API 发送消息
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}
```

对于入站消息，构建一个 `MessageEvent` 并调用 `self.handle_message(event)`：

```python
source = self.build_source(
    chat_id=chat_id,
    chat_name=name,
    chat_type="dm",  # 或 "group"
    user_id=user_id,
    user_name=user_name,
)
event = MessageEvent(
    text=content,
    message_type=MessageType.TEXT,
    source=source,
    message_id=msg_id,
)
await self.handle_message(event)
```

### 3. 消息网关配置 (`gateway/config.py`)

三个接触点：

1.  **`get_connected_platforms()`** — 为你的平台添加所需凭证的检查
2.  **`load_gateway_config()`** — 添加 Token 环境变量映射条目：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3.  **`_apply_env_overrides()`** — 将所有 `NEWPLAT_*` 环境变量映射到配置

### 4. 消息网关运行器 (`gateway/run.py`)

五个接触点：

1.  **`_create_adapter()`** — 添加一个 `elif platform == Platform.NEWPLAT:` 分支
2.  **`_is_user_authorized()` allowed_users 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3.  **`_is_user_authorized()` allow_all 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4.  **早期环境检查 `_any_allowlist` 元组** — 添加 `"NEWPLAT_ALLOWED_USERS"`
5.  **早期环境检查 `_allow_all` 元组** — 添加 `"NEWPLAT_ALLOW_ALL_USERS"`
6.  **`_UPDATE_ALLOWED_PLATFORMS` frozenset** — 添加 `Platform.NEWPLAT`

### 5. 跨平台投递

1.  **`gateway/platforms/webhook.py`** — 在投递类型元组中添加 `"newplat"`
2.  **`cron/scheduler.py`** — 添加到 `_KNOWN_DELIVERY_PLATFORMS` frozenset 和 `_deliver_result()` 平台映射

### 6. CLI 集成

1.  **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS`
2.  **`hermes_cli/gateway.py`** — 在 `_PLATFORMS` 列表中添加条目，包含 key、label、emoji、token_var、setup_instructions 和 vars
3.  **`hermes_cli/platforms.py`** — 添加 `PlatformInfo` 条目，包含 label 和 default_toolset（供 `skills_config` 和 `tools_config` TUI 使用）
4.  **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可以委托给 `gateway.py`）并在消息平台列表中添加元组
5.  **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6.  **`hermes_cli/dump.py`** — 在平台检测字典中添加 `"newplat": "NEWPLAT_TOKEN"`

### 7. 工具

1.  **`tools/send_message_tool.py`** — 在平台映射中添加 `"newplat": Platform.NEWPLAT`
2.  **`tools/cronjob_tools.py`** — 在投递目标描述字符串中添加 `newplat`

### 8. 工具集

1.  **`toolsets.py`** — 添加 `"hermes-newplat"` 工具集定义，包含 `_HERMES_CORE_TOOLS`
2.  **`toolsets.py`** — 在 `"hermes-gateway"` 的 includes 列表中添加 `"hermes-newplat"`

### 9. 可选：平台提示

**`agent/prompt_builder.py`** — 如果你的平台有特定的渲染限制（不支持 markdown、消息长度限制等），请在 `_PLATFORM_HINTS` 字典中添加一个条目。这会将平台特定的指导注入到系统提示词中：

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "你正在通过 NewPlat 聊天。它支持 markdown 格式，但有 4000 字符的消息长度限制。"
    ),
}
```

并非所有平台都需要提示——只有当 Agent 的行为需要有所不同时才添加。

### 10. 测试

创建 `tests/gateway/test_newplat.py`，覆盖：

- 从配置构建适配器
- 消息事件构建
- 发送方法（模拟外部 API）
- 平台特定功能（加密、路由等）

### 11. 文档

| 文件 | 需要添加的内容 |
|------|-------------|
| `website/docs/user-guide/messaging/newplat.md` | 完整的平台设置页面 |
| `website/docs/user-guide/messaging/index.md` | 平台对比表、架构图、工具集表、安全部分、下一步链接 |
| `website/docs/reference/environment-variables.md` | 所有 NEWPLAT_* 环境变量 |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat 工具集 |
| `website/docs/integrations/index.md` | 平台链接 |
| `website/sidebars.ts` | 文档页面的侧边栏条目 |
| `website/docs/developer-guide/architecture.md` | 适配器数量 + 列表 |
| `website/docs/developer-guide/gateway-internals.md` | 适配器文件列表 |

## 功能对等性审查

在将新平台 PR 标记为完成之前，请对照一个已建立的平台进行功能对等性审查：

```bash
# 查找所有提及参考平台的 .py 文件
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# 查找所有提及新平台的 .py 文件
search_files "newplat" output_mode="files_only" file_glob="*.py"

# 出现在第一组但不在第二组中的任何文件都是潜在的遗漏点
```

对 `.md` 和 `.ts` 文件重复此操作。调查每个遗漏点——它是平台枚举（需要更新）还是平台特定的引用（跳过）？
## 常见模式

### 长轮询适配器

如果你的适配器使用长轮询（如 Telegram 或 Weixin），请使用轮询循环任务：

```python
async def connect(self):
    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()

async def _poll_loop(self):
    while self._running:
        messages = await self._fetch_updates()
        for msg in messages:
            await self.handle_message(self._build_event(msg))
```

### 回调/Webhook 适配器

如果平台将消息推送到你的端点（如 WeCom Callback），请运行一个 HTTP 服务器：

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... start aiohttp server
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # 立即确认
```

对于响应截止时间严格的平台（例如，WeCom 的 5 秒限制），请始终立即确认，然后稍后通过 API 主动发送 Agent 的回复。Agent 会话运行时间为 3 到 30 分钟——在回调响应窗口内进行内联回复是不可行的。

### Token 锁

如果适配器使用唯一的凭证持有持久连接，请添加一个作用域锁，以防止两个配置文件使用相同的凭证：

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("Token already in use by another profile")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## 参考实现

| 适配器 | 模式 | 复杂度 | 适合参考 |
|---------|---------|------------|-------------------|
| `bluebubbles.py` | REST + webhook | 中等 | 简单的 REST API 集成 |
| `weixin.py` | 长轮询 + CDN | 高 | 媒体处理、加密 |
| `wecom_callback.py` | 回调/webhook | 中等 | HTTP 服务器、AES 加密、多应用 |
| `telegram.py` | 长轮询 + Bot API | 高 | 功能齐全的适配器，支持群组、线程 |