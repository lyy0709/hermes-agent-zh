---
sidebar_position: 9
---

# 添加平台适配器

本指南介绍如何向 Hermes 消息网关添加新的消息平台。平台适配器将 Hermes 连接到外部消息服务（Telegram、Discord、企业微信等），以便用户可以通过该服务与 Agent 交互。

:::tip
添加平台有两种方式：
- **插件**（推荐用于社区/第三方）：将插件目录放入 `~/.hermes/plugins/` —— 无需修改任何核心代码。请参阅下面的[插件路径](#插件路径推荐)。
- **内置**：修改代码、配置和文档中的 20 多个文件。请使用下面的[内置清单](#逐步检查清单)。
:::

## 架构概述

```
用户 ↔ 消息平台 ↔ 平台适配器 ↔ 网关运行器 ↔ AI Agent
```

每个适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter`，并实现：

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
        # 连接到平台 API，启动监听器
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # 通过平台 API 发送消息
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
    """插件入口点 —— 由 Hermes 插件系统调用。"""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # 环境变量驱动的自动配置 —— 在适配器构造之前，从环境变量填充 PlatformConfig.extra。
        # 请参阅下面的“环境变量驱动的自动配置”部分。
        env_enablement_fn=_env_enablement,
        # Cron 定时任务主频道投递支持。使 deliver=my_platform 的 cron 任务无需编辑 cron/scheduler.py 即可路由。
        # 请参阅下面的“Cron 定时任务投递”部分。
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
        # 每个平台的用户授权环境变量
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # 智能分块的消息长度限制（0 = 无限制）
        max_message_length=4000,
        # 注入到系统提示词中的 LLM 指导信息
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
        ),
        # 显示
        emoji="💬",
    )

    # 可选：注册平台特定的工具
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
| 仅环境变量自动启用 | `env_enablement_fn` 填充 `PlatformConfig.extra` + `home_channel` |
| Cron 定时任务投递 | `cron_deliver_env_var` 使 `deliver=<name>` 生效 |
| `hermes config` UI 条目 | `plugin.yaml` 中的 `requires_env` / `optional_env` 自动填充 |
| send_message 工具 | 通过活动的网关适配器路由 |
| Webhook 跨平台投递 | 检查注册表以识别已知平台 |
| `/update` 命令访问 | `allow_update_command` 标志 |
| 频道目录 | 插件平台包含在枚举中 |
| 系统提示词提示 | `platform_hint` 注入到 LLM 上下文 |
| 消息分块 | `max_message_length` 用于智能分割 |
| PII 信息脱敏 | `pii_safe` 标志 |
| `hermes status` | 显示带有 `(plugin)` 标签的插件平台 |
| `hermes gateway setup` | 插件平台出现在设置菜单中 |
| `hermes tools` / `hermes skills` | 插件平台出现在每个平台的配置中 |
| Token 锁（多配置文件） | 在您的 `connect()` 中使用 `acquire_scoped_lock()` |
| 孤立配置警告 | 插件缺失时记录描述性日志 |
## 基于环境变量的自动配置

大多数用户通过将环境变量放入 `~/.hermes/.env` 来设置平台，而不是编辑 `config.yaml`。`env_enablement_fn` 钩子允许你的插件在适配器构建**之前**获取这些环境变量，因此 `hermes gateway status`、`get_connected_platforms()` 和定时任务交付都能看到正确的状态，而无需实例化平台 SDK。

```python
def _env_enablement() -> dict | None:
    """从环境变量初始化 PlatformConfig.extra。

    由平台注册表在 load_gateway_config() 期间调用。
    当平台未进行最小配置时返回 None —— 调用方随后跳过自动启用。返回一个字典来初始化 extras。

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

调度器在解析 `deliver=my_platform` 任务的主目标时会读取此环境变量，并且在 `_KNOWN_DELIVERY_PLATFORMS` 风格的检查中也会将该平台视为有效的定时任务目标。如果你的 `env_enablement_fn` 初始化了一个 `home_channel` 字典（见上文），则其优先级更高 —— `cron_deliver_env_var` 是在环境变量初始化之前运行的定时任务的备用方案。

### 进程外定时任务交付

`cron_deliver_env_var` 使你的平台成为可识别的 `deliver=` 目标。为了使定时任务在与消息网关分离的进程中（即 `hermes cron run` 与 `hermes gateway` 分离）运行时实际发送成功，请注册一个 `standalone_sender_fn`：

```python
async def _standalone_send(
    pconfig,
    chat_id,
    message,
    *,
    thread_id=None,
    media_files=None,
    force_document=False,
):
    """打开一个临时连接 / 获取新的 Token，发送消息，然后关闭。"""
    # ... 打开连接，发送消息，返回结果 ...
    return {"success": True, "message_id": "..."}
    # 或 {"error": "..."}

ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
    standalone_sender_fn=_standalone_send,
)
```

为什么需要这个钩子：内置平台（Telegram、Discord、Slack 等）在 `tools/send_message_tool.py` 中提供了直接的 REST 辅助函数，因此定时任务可以在不持有同一进程中的消息网关的情况下进行交付。插件平台历史上依赖于 `_gateway_runner_ref()`，该函数在消息网关进程外返回 `None`，因此如果没有 `standalone_sender_fn`，定时任务端的发送会失败并提示 `No live adapter for platform '<name>'`。

该函数接收与实时适配器相同的 `pconfig` 和 `chat_id`，以及可选的 `thread_id`、`media_files` 和 `force_document` 关键字参数。返回 `{"success": True, "message_id": ...}` 被视为成功交付；返回 `{"error": "..."}` 会在定时任务的 `delivery_errors` 中显示该消息。函数内部引发的异常会被调度器捕获并报告为 `Plugin standalone send failed: <reason>`。参考实现位于 `plugins/platforms/{irc,teams,google_chat}/adapter.py`。

## 在 `hermes config` 中展示环境变量

`hermes_cli/config.py` 在导入时扫描 `plugins/platforms/*/plugin.yaml`，并根据 `requires_env` 和（可选的）`optional_env` 块自动填充 `OPTIONAL_ENV_VARS`。使用富字典形式来提供适当的描述、提示、密码标志和 URL —— CLI 设置界面会自动获取它们。

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

**支持的字典键：** `name`（必需）、`description`、`prompt`、`url`、`password`（布尔值；当省略时，会根据 `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` 后缀自动检测）、`category`（默认为 `"messaging"`）。

纯字符串条目（`- MY_PLATFORM_TOKEN`）仍然有效 —— 它们会获得一个从插件的 `label` 自动派生的通用描述。如果 `OPTIONAL_ENV_VARS` 中已存在同一变量的硬编码条目，则其优先级更高（向后兼容）；plugin.yaml 形式作为备用方案。

## 平台特定的慢速 LLM 用户体验

某些平台有限制，会改变慢速 LLM 响应的呈现方式：
- **LINE** 会签发一个一次性*回复令牌*，该令牌在入站事件发生后约 60 秒过期。使用该令牌回复是免费的；回退到计费的 Push API 则不是。如果 LLM 在截止时间前未完成，选择将是“消耗付费的 Push 配额”或“在回复令牌过期前用更聪明的方式处理它”。
- **WhatsApp** 在 24 小时后将会话标记为非活动状态，此后只接受模板消息。
- **SMS** 没有输入指示器或渐进式更新的概念——长回复只会让机器人看起来像是离线了。

这些是基础的 `BasePlatformAdapter` 无法预见的真实约束。插件接口有意留出空间，让适配器可以在基础的打字循环之上叠加平台特定的用户体验，而无需扩展参数列表。

### 模式：子类化 `_keep_typing` 以叠加运行中的用户体验

`BasePlatformAdapter._keep_typing` 是输入指示器的心跳——它在 LLM 生成时作为后台任务运行，并在响应送达时取消。要在某个阈值（例如在 45 秒时发送一个“仍在思考”的气泡）叠加平台特定的行为，请在适配器中重写 `_keep_typing`，安排你自己的任务与 `super()._keep_typing()` 并行运行，并在 `finally` 中清理它：

```python
class LineAdapter(BasePlatformAdapter):
    async def _keep_typing(self, chat_id: str, *args, **kwargs) -> None:
        if self.slow_response_threshold <= 0:
            await super()._keep_typing(chat_id, *args, **kwargs)
            return

        async def _fire_at_threshold() -> None:
            try:
                await asyncio.sleep(self.slow_response_threshold)
            except asyncio.CancelledError:
                raise
            # 在此处执行平台特定的工作——对于 LINE，使用缓存的回复令牌发送一个模板按钮“获取答案”气泡，
            # 以便用户稍后可以通过来自回调查调用的新（免费）回复令牌获取缓存的响应。
            await self._send_slow_response_button(chat_id)

        side_task = asyncio.create_task(_fire_at_threshold())
        try:
            await super()._keep_typing(chat_id, *args, **kwargs)
        finally:
            if not side_task.done():
                side_task.cancel()
                try:
                    await side_task
                except (asyncio.CancelledError, Exception):
                    pass
```

关键点：

- **始终 `await super()._keep_typing(...)`。** 打字心跳本身是有用的——不要替换它，而是在它之上叠加。
- **在 `finally` 中清理侧任务。** 当 LLM 完成（或 `/stop` 取消运行）时，消息网关会取消打字任务。你的侧任务也必须观察该取消，否则它会残留，并可能在响应已经送达后触发。
- **与 `interrupt_session_activity` 配对使用**，以在用户发出 `/stop` 时解决任何孤立的用户体验状态。对于 LINE，这意味着将回调查缓存条目从 `PENDING` 转换为 `ERROR`，以便持久的“获取答案”按钮传递“运行被中断”的消息，而不是循环。

### 模式：子类化 `send` 以通过缓存路由而不是立即发送

如果你的慢响应用户体验将响应缓存以供稍后检索（LINE 的回调流程），你的 `send` 重写需要识别三种模式：

1. **此聊天的待处理回调处于活动状态** → 将响应缓存在 request_id 下，不发送任何可见内容。
2. **系统繁忙确认**（`⚡ Interrupting`、`⏳ Queued`、`⏩ Steered`）→ 绕过缓存并可见地发送，以便用户看到消息网关对其输入的响应。
3. **正常响应** → 像往常一样通过回复令牌或推送发送。

```python
async def send(self, chat_id: str, content: str, **kw) -> SendResult:
    if _is_system_bypass(content):
        return await self._send_text_chunks(chat_id, content, force_push=False)
    pending_rid = self._pending_buttons.get(chat_id)
    if pending_rid:
        self._cache.set_ready(pending_rid, content)
        return SendResult(success=True, message_id=pending_rid)
    return await self._send_text_chunks(chat_id, content, force_push=False)
```

`_SYSTEM_BYPASS_PREFIXES` 是消息网关自身的繁忙确认前缀（`⚡`、`⏳`、`⏩`、`💾`）。无论缓存的用户体验状态如何，始终让这些内容可见地通过。

### 何时适用此模式

在以下情况下使用打字循环重写方法：

- 平台的出站 API 有严格的时间窗口约束（一次性回复令牌、过期的粘性会话等）**并且**
- 在该平台上，*可见的运行中气泡*是可接受的用户体验。

在以下情况下使用更简单的 `slow_response_threshold = 0` 始终推送路径：

- 平台没有有意义的免费与付费区别，**或者**
- 用户社区更喜欢“加载中… 加载中… 完成”这种静默然后响应的方式，而不是交互式的中间气泡。

LINE 两者都支持：阈值默认为 45 秒以进行免费回调获取，而 `LINE_SLOW_RESPONSE_THRESHOLD=0` 则恢复为“始终回退到推送”。

### 参考实现

查看 `plugins/platforms/line/adapter.py` 以获取完整的 LINE 回调实现——一个 `RequestCache` 状态机（`PENDING → READY → DELIVERED`，加上用于 `/stop` 的 `ERROR`），一个在阈值触发模板按钮气泡的 `_keep_typing` 重写，一个通过缓存路由的 `send` 重写，以及一个解决孤立 PENDING 条目的 `interrupt_session_activity` 重写。

### 参考实现（插件路径）

查看仓库中的 `plugins/platforms/irc/` 获取一个完整的工作示例——一个零外部依赖的完整异步 IRC 适配器。`plugins/platforms/teams/` 涵盖了 Bot Framework / Adaptive Cards，`plugins/platforms/google_chat/` 涵盖了基于 OAuth 的 REST API，`plugins/platforms/line/` 涵盖了具有平台特定慢 LLM 用户体验的 Webhook 驱动的 Messaging API。

---

## 逐步检查清单（内置路径）

:::note
此检查清单适用于将平台直接添加到 Hermes 核心代码库——通常由核心贡献者为官方支持的平台完成。社区/第三方平台应使用上面的[插件路径](#插件路径-推荐)。
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

1.  **`get_connected_platforms()`** — 为你的平台添加所需凭据的检查
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

1.  **`toolsets.py`** — 添加包含 `_HERMES_CORE_TOOLS` 的 `"hermes-newplat"` 工具集定义
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

## 功能对等性审计

在将新平台 PR 标记为完成之前，请对照一个已建立的平台进行功能对等性审计：

```bash
# 查找所有提及参考平台的 .py 文件
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# 查找所有提及新平台的 .py 文件
search_files "newplat" output_mode="files_only" file_glob="*.py"

# 第一组中存在但第二组中不存在的任何文件都是潜在的遗漏点
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

对于响应截止时间严格的平台（例如，WeCom 的 5 秒限制），请始终立即确认，并稍后通过 API 主动发送 Agent 的回复。Agent 会话运行时间为 3 到 30 分钟——在回调响应窗口内进行内联回复是不可行的。

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