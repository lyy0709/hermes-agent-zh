---
sidebar_position: 7
title: "消息网关内部原理"
description: "消息网关如何启动、授权用户、路由会话和传递消息"
---

# 消息网关内部原理

消息网关是一个长期运行的进程，通过统一的架构将 Hermes 连接到 14 个以上的外部消息平台。

## 关键文件

| 文件 | 用途 |
|------|---------|
| `gateway/run.py` | `GatewayRunner` — 主循环、斜杠命令、消息分发（约 9,000 行） |
| `gateway/session.py` | `SessionStore` — 对话持久化和会话密钥构建 |
| `gateway/delivery.py` | 向目标平台/渠道发送出站消息 |
| `gateway/pairing.py` | 用于用户授权的私聊配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射到人类可读的名称，用于定时任务交付 |
| `gateway/hooks.py` | 钩子发现、加载和生命周期事件分发 |
| `gateway/mirror.py` | 为 `send_message` 实现跨会话消息镜像 |
| `gateway/status.py` | 用于配置文件作用域网关实例的 Token 锁管理 |
| `gateway/builtin_hooks/` | 始终注册的钩子（例如，BOOT.md 系统提示词钩子） |
| `gateway/platforms/` | 平台适配器（每个消息平台一个） |

## 架构概述

```text
┌─────────────────────────────────────────────────┐
│                 GatewayRunner                     │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram  │  │ Discord  │  │  Slack   │  ...  │
│  │ Adapter   │  │ Adapter  │  │ Adapter  │       │
│  └─────┬─────┘  └─────┬────┘  └─────┬────┘       │
│        │              │              │             │
│        └──────────────┼──────────────┘             │
│                       ▼                            │
│              _handle_message()                     │
│                       │                            │
│          ┌────────────┼────────────┐               │
│          ▼            ▼            ▼               │
│   Slash command   AIAgent      Queue/BG            │
│    dispatch       creation     sessions            │
│                       │                            │
│                       ▼                            │
│              SessionStore                          │
│           (SQLite persistence)                     │
└─────────────────────────────────────────────────┘
```

## 消息流

当来自任何平台的消息到达时：

1. **平台适配器** 接收原始事件，将其规范化为 `MessageEvent`
2. **基础适配器** 检查活动会话守卫：
   - 如果此会话的 Agent 正在运行 → 将消息排队，设置中断事件
   - 如果是 `/approve`、`/deny`、`/stop` → 绕过守卫（内联分发）
3. **GatewayRunner._handle_message()** 接收事件：
   - 通过 `_session_key_for_source()` 解析会话密钥（格式：`agent:main:{platform}:{chat_type}:{chat_id}`）
   - 检查授权（见下文授权部分）
   - 检查是否为斜杠命令 → 分发给命令处理器
   - 检查 Agent 是否已在运行 → 拦截如 `/stop`、`/status` 等命令
   - 否则 → 创建 `AIAgent` 实例并运行对话
4. **响应** 通过平台适配器发送回去

### 会话密钥格式

会话密钥编码了完整的路由上下文：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程的平台（Telegram 论坛主题、Discord 线程、Slack 线程）可能在 `chat_id` 部分包含线程 ID。**切勿手动构建会话密钥** — 始终使用 `gateway/session.py` 中的 `build_session_key()`。

### 两级消息守卫

当 Agent 正在主动运行时，传入的消息会经过两个连续的守卫：

1. **第 1 级 — 基础适配器** (`gateway/platforms/base.py`)：检查 `_active_sessions`。如果会话处于活动状态，则将消息排队到 `_pending_messages` 中并设置中断事件。这会在消息*到达*网关运行器之前捕获它们。

2. **第 2 级 — 网关运行器** (`gateway/run.py`)：检查 `_running_agents`。拦截特定命令（`/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`）并将其路由到适当位置。其他所有内容都会触发 `running_agent.interrupt()`。

当 Agent 被阻塞时必须到达运行器的命令（如 `/approve`）通过 `await self._message_handler(event)` **内联**分发 — 它们绕过后台任务系统以避免竞态条件。

## 授权

网关使用多层授权检查，按顺序评估：

1. **每平台允许所有标志**（例如，`TELEGRAM_ALLOW_ALL_USERS`）— 如果设置，该平台上的所有用户都被授权
2. **平台允许列表**（例如，`TELEGRAM_ALLOWED_USERS`）— 逗号分隔的用户 ID
3. **私聊配对** — 已认证用户可以通过配对码配对新用户
4. **全局允许所有** (`GATEWAY_ALLOW_ALL_USERS`) — 如果设置，所有平台的所有用户都被授权
5. **默认：拒绝** — 未授权用户被拒绝

### 私聊配对流程

```text
管理员：/pair
网关："配对码：ABC123。与用户分享。"
新用户：ABC123
网关："已配对！您现在已获得授权。"
```

配对状态持久化在 `gateway/pairing.py` 中，并在重启后保留。

## 斜杠命令分发

网关中的所有斜杠命令都通过相同的解析流水线：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 将输入映射到规范名称（处理别名、前缀匹配）
2. 规范名称根据 `GATEWAY_KNOWN_COMMANDS` 进行检查
3. `_handle_message()` 中的处理器根据规范名称进行分发
4. 某些命令受配置限制（`CommandDef` 上的 `gateway_config_gate`）

### 运行中 Agent 守卫

在 Agent 处理时**不得**执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent 正在运行 — 请等待其完成或先使用 /stop。"
```

绕过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）有特殊处理。

## 配置源

网关从多个源读取配置：

| 源 | 提供内容 |
|--------|-----------------|
| `~/.hermes/.env` | API 密钥、机器人令牌、平台凭据 |
| `~/.hermes/config.yaml` | 模型设置、工具配置、显示选项 |
| 环境变量 | 覆盖上述任何配置 |

与 CLI（使用带有硬编码默认值的 `load_cli_config()`）不同，网关通过 YAML 加载器直接读取 `config.yaml`。这意味着存在于 CLI 默认字典中但不在用户配置文件中的配置键可能在 CLI 和网关之间表现不同。

## 平台适配器

每个消息平台在 `gateway/platforms/` 中都有一个适配器：

```text
gateway/platforms/
├── base.py              # BaseAdapter — 所有平台的共享逻辑
├── telegram.py          # Telegram Bot API（长轮询或 webhook）
├── discord.py           # 通过 discord.py 的 Discord 机器人
├── slack.py             # Slack Socket Mode
├── whatsapp.py          # WhatsApp Business Cloud API
├── signal.py            # 通过 signal-cli REST API 的 Signal
├── matrix.py            # 通过 mautrix 的 Matrix（可选 E2EE）
├── mattermost.py        # Mattermost WebSocket API
├── email.py             # 通过 IMAP/SMTP 的电子邮件
├── sms.py               # 通过 Twilio 的短信
├── dingtalk.py          # 钉钉 WebSocket
├── feishu.py            # 飞书/Lark WebSocket 或 webhook
├── wecom.py             # 企业微信（WeChat Work）回调
├── weixin.py            # 通过 iLink Bot API 的微信（个人微信）
├── bluebubbles.py       # 通过 BlueBubbles macOS 服务器的 Apple iMessage
├── webhook.py           # 入站/出站 webhook 适配器
├── api_server.py        # REST API 服务器适配器
└── homeassistant.py     # Home Assistant 对话集成
```

适配器实现了一个通用接口：
- `connect()` / `disconnect()` — 生命周期管理
- `send_message()` — 出站消息传递
- `on_message()` — 入站消息规范化 → `MessageEvent`

### Token 锁

使用唯一凭据连接的适配器在 `connect()` 中调用 `acquire_scoped_lock()`，在 `disconnect()` 中调用 `release_scoped_lock()`。这可以防止两个配置文件同时使用同一个机器人令牌。

## 传递路径

出站传递 (`gateway/delivery.py`) 处理：

- **直接回复** — 将响应发送回原始聊天
- **主频道传递** — 将定时任务输出和后台结果路由到配置的主频道
- **显式目标传递** — `send_message` 工具指定 `telegram:-1001234567890`
- **跨平台传递** — 传递到与原始消息不同的平台

定时任务传递**不**镜像到网关会话历史记录中 — 它们仅存在于自己的定时任务会话中。这是一个深思熟虑的设计选择，以避免消息交替违规。

## 钩子

网关钩子是响应生命周期事件的 Python 模块：

### 网关钩子事件

| 事件 | 触发时机 |
|-------|-----------|
| `gateway:startup` | 网关进程启动 |
| `session:start` | 新对话会话开始 |
| `session:end` | 会话完成或超时 |
| `session:reset` | 用户使用 `/new` 重置会话 |
| `agent:start` | Agent 开始处理消息 |
| `agent:step` | Agent 完成一次工具调用迭代 |
| `agent:end` | Agent 完成并返回响应 |
| `command:*` | 执行任何斜杠命令 |

钩子从 `gateway/builtin_hooks/`（始终活动）和 `~/.hermes/hooks/`（用户安装）中发现。每个钩子都是一个包含 `HOOK.yaml` 清单和 `handler.py` 的目录。

## 记忆提供商集成

当启用记忆提供商插件（例如，Honcho）时：

1. 网关为每条消息创建一个带有会话 ID 的 `AIAgent`
2. `MemoryManager` 使用会话上下文初始化提供商
3. 提供商工具（例如，`honcho_profile`、`viking_search`）通过以下方式路由：

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 在会话结束/重置时，触发 `on_session_end()` 进行清理和最终数据刷新

### 记忆刷新生命周期

当会话被重置、恢复或过期时：
1. 内置记忆被刷新到磁盘
2. 触发记忆提供商的 `on_session_end()` 钩子
3. 运行一个临时的 `AIAgent` 进行仅记忆的对话轮次
4. 然后上下文被丢弃或存档

## 后台维护

网关在消息处理的同时运行定期维护：

- **定时任务触发** — 检查作业计划并触发到期的作业
- **会话过期** — 在超时后清理被遗弃的会话
- **记忆刷新** — 在会话过期前主动刷新记忆
- **缓存刷新** — 刷新模型列表和提供商状态

## 进程管理

网关作为一个长期运行的进程运行，通过以下方式管理：

- `hermes gateway start` / `hermes gateway stop` — 手动控制
- `systemctl` (Linux) 或 `launchctl` (macOS) — 服务管理
- `~/.hermes/gateway.pid` 处的 PID 文件 — 配置文件作用域的进程跟踪

**配置文件作用域与全局**：`start_gateway()` 使用配置文件作用域的 PID 文件。`hermes gateway stop` 仅停止当前配置文件的网关。`hermes gateway stop --all` 使用全局 `ps aux` 扫描来终止所有网关进程（在更新期间使用）。

## 相关文档

- [会话存储](./session-storage.md)
- [定时任务内部原理](./cron-internals.md)
- [ACP 内部原理](./acp-internals.md)
- [Agent 循环内部原理](./agent-loop.md)
- [消息网关（用户指南）](/docs/user-guide/messaging)