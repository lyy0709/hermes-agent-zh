---
sidebar_position: 9
---

# 添加平台适配器

本指南介绍如何向 Hermes 消息网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、企业微信等），以便用户可以通过该服务与 Agent 交互。

:::tip
添加平台有两种方式：
- **插件**（推荐用于社区/第三方）：将插件目录放入 `~/.hermes/plugins/` —— 无需修改任何核心代码。请参阅下面的[插件路径](#插件路径推荐)。
- **内置**：修改代码、配置和文档中的 20 多个文件。使用下面的[内置清单](#逐步检查清单)。
:::

## 架构概述

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ 网关运行器 ↔ AI Agent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter` 并实现：

- **`connect()`** — 建立连接（WebSocket、长轮询、HTTP 服务器等）*(抽象)*
- **`disconnect()`** — 清理并关闭连接 *(抽象)*
- **`send()`** — 向聊天发送文本消息 *(抽象)*
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

插件元数据。`requires_env` 和 `optional_env` 块会自动填充 `hermes config` UI 中的条目（请参阅下面的[在 Hermes 配置中暴露环境变量](#在-hermes-配置中暴露环境变量)）。

```yaml
name: my-platform
label: My Platform
kind: platform
version: 1.0.0
description: My custom messaging platform adapter
author: Your Name
requires_env:
  - MY_PLATFORM_TOKEN          # 纯字符串即可
  - name: MY_PLATFORM_CHANNEL  # 或者使用更丰富的字典以获得更好的用户体验
    description: "Channel to join"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
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


def _env_enablement() -> dict | None:
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {"chat_id": home, "name": "Home"}
    return seed


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
        # Env-driven auto-configuration — seeds PlatformConfig.extra from
        # env vars before adapter construction. See "Env-Driven Auto-
        # Configuration" section below.
        env_enablement_fn=_env_enablement,
        # Cron home-channel delivery support. Lets deliver=my_platform cron
        # jobs route without editing cron/scheduler.py. See "Cron Delivery"
        # section below.
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
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

或者通过环境变量（适配器在 `__init__` 中读取）。

### 插件系统自动处理的内容

当您调用 `ctx.register_platform()` 时，以下集成点会自动为您处理 —— 无需修改核心代码：

| 集成点 | 工作原理 |
|---|---|
| 网关适配器创建 | 在检查内置的 if/elif 链之前，先检查注册表 |
| 配置解析 | `Platform._missing_()` 接受任何平台名称 |
| 已连接平台验证 | 调用注册表的 `validate_config()` |
| 用户授权 | 检查 `allowed_users_env` / `allow_all_env` |
| 仅环境变量自动启用 | `env_enablement_fn` 为 `PlatformConfig.extra` 和 `home_channel` 提供种子数据 |
| 定时任务交付 | `cron_deliver_env_var` 使 `deliver=<name>` 生效 |
| `hermes config` UI 条目 | `plugin.yaml` 中的 `requires_env` / `optional_env` 自动填充 |
| send_message 工具 | 通过活动的网关适配器路由 |
| Webhook 跨平台交付 | 检查注册表中已知的平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 插件平台包含在枚举中 |
| 系统提示词提示 | `platform_hint` 注入到 LLM 上下文中 |
| 消息分块 | `max_message_length` 用于智能分割 |
| PII 脱敏 | `pii_safe` 标志 |
| `hermes status` | 显示带有 `(plugin)` 标签的插件平台 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台出现在各平台配置中 |
| Token 锁（多配置文件） | 在您的 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 插件缺失时记录描述性日志 |
## 环境变量驱动的自动配置

大多数用户通过将环境变量放入 `~/.hermes/.env` 来设置平台，而不是编辑 `config.yaml`。`env_enablement_fn` 钩子允许你的插件在适配器构造**之前**获取这些环境变量，这样 `hermes gateway status`、`get_connected_platforms()` 和定时任务交付就能看到正确的状态，而无需实例化平台 SDK。

```python
def _env_enablement() -> dict | None:
    """从环境变量填充 PlatformConfig.extra。

    由平台注册表在 load_gateway_config() 期间调用。
    当平台未进行最小配置时返回 None —— 调用方随后跳过自动启用。返回一个字典来填充 extras。

    特殊的 'home_channel' 键会被提取出来，并在 PlatformConfig 上成为一个适当的 HomeChannel 数据类；其他所有键都会合并到 PlatformConfig.extra 中。
    """
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {
            "chat_id": home,
            "name": os.getenv("MY_PLATFORM_HOME_CHANNEL_NAME", "Home"),
        }
    return seed


def register(ctx):
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        # ... 其他字段
    )
```

## 定时任务交付

为了让 `deliver=my_platform` 的定时任务路由到已配置的主频道，请将 `cron_deliver_env_var` 设置为保存默认聊天/房间/频道 ID 的环境变量名：

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

调度器在解析 `deliver=my_platform` 任务的主目标时会读取此环境变量，并且在 `_KNOWN_DELIVERY_PLATFORMS` 风格的检查中也会将该平台视为有效的定时任务目标。如果你的 `env_enablement_fn` 填充了一个 `home_channel` 字典（见上文），则其优先级更高 —— `cron_deliver_env_var` 是在环境变量填充之前运行的定时任务的备用方案。

## 在 `hermes config` 中展示环境变量

`hermes_cli/config.py` 在导入时会扫描 `plugins/platforms/*/plugin.yaml`，并自动从 `requires_env` 和（可选的）`optional_env` 块中填充 `OPTIONAL_ENV_VARS`。使用富字典形式来提供适当的描述、提示、密码标志和 URL —— CLI 设置界面会自动获取它们。

```yaml
# plugins/platforms/my_platform/plugin.yaml
name: my_platform-platform
label: My Platform
kind: platform
version: 1.0.0
description: >
  My Platform gateway adapter for Hermes Agent.
author: Your Name
requires_env:
  - name: MY_PLATFORM_TOKEN
    description: "Bot API token from the My Platform console"
    prompt: "My Platform bot token"
    url: "https://my-platform.example.com/bots"
    password: true
  - name: MY_PLATFORM_CHANNEL
    description: "Channel to join (e.g. #hermes)"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery (defaults to MY_PLATFORM_CHANNEL)"
    prompt: "Home channel (or empty)"
    password: false
  - name: MY_PLATFORM_ALLOWED_USERS
    description: "Comma-separated user IDs allowed to talk to the bot"
    prompt: "Allowed users (comma-separated)"
    password: false
```

**支持的字典键：** `name`（必需）、`description`、`prompt`、`url`、`password`（布尔值；当省略时，根据 `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` 后缀自动检测）、`category`（默认为 `"messaging"`）。

纯字符串条目（`- MY_PLATFORM_TOKEN`）仍然有效 —— 它们会从插件的 `label` 自动派生一个通用描述。如果同一个变量的硬编码条目已经存在于 `OPTIONAL_ENV_VARS` 中，则其优先级更高（向后兼容）；plugin.yaml 形式作为备用方案。

### 参考实现

请参阅仓库中的 `plugins/platforms/irc/` 获取完整的工作示例 —— 一个零外部依赖的完整异步 IRC 适配器。

---

## 逐步检查清单（内置路径）

:::note
此检查清单适用于将平台直接添加到 Hermes 核心代码库 —— 通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#插件路径-推荐)。
:::

### 1. 平台枚举

将你的平台添加到 `gateway/config.py` 中的 `Platform` 枚举：

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

三个修改点：

1. **`get_connected_platforms()`** — 添加对您平台所需凭证的检查
2. **`load_gateway_config()`** — 添加 Token 环境变量映射条目：`Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — 将所有 `NEWPLAT_*` 环境变量映射到配置

### 4. 消息网关运行器 (`gateway/run.py`)

五个修改点：

1. **`_create_adapter()`** — 添加一个 `elif platform == Platform.NEWPLAT:` 分支
2. **`_is_user_authorized()` allowed_users 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` allow_all 映射** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **早期环境检查 `_any_allowlist` 元组** — 添加 `"NEWPLAT_ALLOWED_USERS"`
5. **早期环境检查 `_allow_all` 元组** — 添加 `"NEWPLAT_ALLOW_ALL_USERS"`
6. **`_UPDATE_ALLOWED_PLATFORMS` frozenset** — 添加 `Platform.NEWPLAT`

### 5. 跨平台交付

1. **`gateway/platforms/webhook.py`** — 在交付类型元组中添加 `"newplat"`
2. **`cron/scheduler.py`** — 添加到 `_KNOWN_DELIVERY_PLATFORMS` frozenset 和 `_deliver_result()` 平台映射

### 6. CLI 集成

1. **`hermes_cli/config.py`** — 将所有 `NEWPLAT_*` 变量添加到 `_EXTRA_ENV_KEYS`
2. **`hermes_cli/gateway.py`** — 在 `_PLATFORMS` 列表中添加条目，包含 key、label、emoji、token_var、setup_instructions 和 vars
3. **`hermes_cli/platforms.py`** — 添加 `PlatformInfo` 条目，包含 label 和 default_toolset（供 `skills_config` 和 `tools_config` TUI 使用）
4. **`hermes_cli/setup.py`** — 添加 `_setup_newplat()` 函数（可以委派给 `gateway.py`），并在消息平台列表中添加元组
5. **`hermes_cli/status.py`** — 添加平台检测条目：`"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — 在平台检测字典中添加 `"newplat": "NEWPLAT_TOKEN"`

### 7. 工具

1. **`tools/send_message_tool.py`** — 在平台映射中添加 `"newplat": Platform.NEWPLAT`
2. **`tools/cronjob_tools.py`** — 在交付目标描述字符串中添加 `newplat`

### 8. 工具集

1. **`toolsets.py`** — 添加包含 `_HERMES_CORE_TOOLS` 的 `"hermes-newplat"` 工具集定义
2. **`toolsets.py`** — 在 `"hermes-gateway"` 的 includes 列表中添加 `"hermes-newplat"`

### 9. 可选：平台提示

**`agent/prompt_builder.py`** — 如果您的平台有特定的渲染限制（不支持 markdown、消息长度限制等），请在 `_PLATFORM_HINTS` 字典中添加一个条目。这会将平台特定的指导注入到系统提示词中：

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "您正在通过 NewPlat 聊天。它支持 markdown 格式，但有 4000 字符的消息长度限制。"
    ),
}
```

并非所有平台都需要提示——仅当 Agent 的行为应有所不同时才添加。

### 10. 测试

创建 `tests/gateway/test_newplat.py`，覆盖：

- 从配置构建 Adapter
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
| `website/docs/developer-guide/architecture.md` | Adapter 数量 + 列表 |
| `website/docs/developer-guide/gateway-internals.md` | Adapter 文件列表 |

## 功能对等性审计

在将新平台 PR 标记为完成之前，请对照一个已建立的平台运行功能对等性审计：

```bash
# 查找所有提及参考平台的 .py 文件
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# 查找所有提及新平台的 .py 文件
search_files "newplat" output_mode="files_only" file_glob="*.py"

# 第一个集合中存在但第二个集合中不存在的任何文件都是潜在的遗漏点
```

对 `.md` 和 `.ts` 文件重复此操作。调查每个遗漏点——它是一个平台枚举（需要更新）还是一个平台特定的引用（跳过）？

## 常见模式

### 长轮询 Adapter

如果您的 Adapter 使用长轮询（如 Telegram 或 Weixin），请使用轮询循环任务：

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

### 回调/Webhook Adapter

如果平台将消息推送到您的端点（如 WeCom Callback），请运行一个 HTTP 服务器：

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... 启动 aiohttp 服务器
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # 立即确认
```

对于响应截止时间严格的平台（例如，WeCom 的 5 秒限制），请始终立即确认，并通过 API 稍后主动交付 Agent 的回复。Agent 会话运行 3-30 分钟——在回调响应窗口内进行内联回复是不可行的。

### Token 锁

如果 Adapter 使用唯一凭证持有持久连接，请添加一个作用域锁，以防止两个配置文件使用相同的凭证：

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("Token already in use by another profile")
        return False
    # ... 连接

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