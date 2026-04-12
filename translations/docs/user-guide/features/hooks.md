---
sidebar_position: 6
title: "事件钩子"
description: "在关键生命周期节点运行自定义代码 —— 记录活动、发送警报、发布到 Webhook"
---

# 事件钩子

Hermes 拥有两套钩子系统，可在关键生命周期节点运行自定义代码：

| 系统 | 注册方式 | 运行环境 | 使用场景 |
|--------|---------------|---------|----------|
| **[消息网关钩子](#gateway-event-hooks)** | 在 `~/.hermes/hooks/` 目录下的 `HOOK.yaml` + `handler.py` | 仅消息网关 | 日志记录、警报、Webhook |
| **[插件钩子](#plugin-hooks)** | 在[插件](/docs/user-guide/features/plugins)中使用 `ctx.register_hook()` | CLI + 消息网关 | 工具拦截、指标、防护栏 |

两套系统都是非阻塞的 —— 任何钩子中的错误都会被捕获并记录，永远不会导致 Agent 崩溃。

## 消息网关事件钩子

消息网关钩子在网关（Telegram、Discord、Slack、WhatsApp）运行期间自动触发，不会阻塞主 Agent 流水线。

### 创建钩子

每个钩子是 `~/.hermes/hooks/` 下的一个目录，包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # 声明要监听哪些事件
    └── handler.py     # Python 处理函数
```

#### HOOK.yaml

```yaml
name: my-hook
description: 将所有 Agent 活动记录到文件
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表决定了哪些事件会触发你的处理函数。你可以订阅任意组合的事件，包括通配符如 `command:*`。

#### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """为每个订阅的事件调用。必须命名为 'handle'。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**处理函数规则：**
- 必须命名为 `handle`
- 接收 `event_type`（字符串）和 `context`（字典）参数
- 可以是 `async def` 或普通的 `def` —— 两者都有效
- 错误会被捕获并记录，永远不会导致 Agent 崩溃

### 可用事件

| 事件 | 触发时机 | 上下文键 |
|-------|---------------|--------------|
| `gateway:startup` | 消息网关进程启动时 | `platforms`（活跃平台名称列表） |
| `session:start` | 创建新的消息会话时 | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | 会话结束时（重置之前） | `platform`, `user_id`, `session_key` |
| `session:reset` | 用户执行 `/new` 或 `/reset` 时 | `platform`, `user_id`, `session_key` |
| `agent:start` | Agent 开始处理消息时 | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | 工具调用循环的每次迭代时 | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent 完成处理时 | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | 执行任何斜杠命令时 | `platform`, `user_id`, `command`, `args` |

#### 通配符匹配

注册了 `command:*` 的处理函数会为任何 `command:` 事件（`command:model`、`command:reset` 等）触发。通过一次订阅即可监控所有斜杠命令。

### 示例

#### 启动检查清单 (BOOT.md) —— 内置

消息网关附带一个内置的 `boot-md` 钩子，它会在每次启动时查找 `~/.hermes/BOOT.md`。如果文件存在，Agent 会在后台会话中运行其指令。无需安装 —— 只需创建文件。

**创建 `~/.hermes/BOOT.md`：**

```markdown
# 启动检查清单

1. 检查是否有定时任务在夜间失败 —— 运行 `hermes cron list`
2. 向 Discord #general 频道发送消息，内容为 "Gateway restarted, all systems go"
3. 检查 /opt/app/deploy.log 在过去 24 小时内是否有任何错误
```

Agent 会在后台线程中运行这些指令，因此不会阻塞网关启动。如果无需关注任何事项，Agent 会回复 `[SILENT]` 且不发送任何消息。

:::tip
没有 BOOT.md？钩子会静默跳过 —— 零开销。当你需要启动自动化时创建文件，不需要时删除它。
:::

#### 长任务 Telegram 警报

当 Agent 执行超过 10 步时向自己发送消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 当 Agent 执行过多步骤时发出警报
events:
  - agent:step
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
import os
import httpx

THRESHOLD = 10
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_HOME_CHANNEL")

async def handle(event_type: str, context: dict):
    iteration = context.get("iteration", 0)
    if iteration == THRESHOLD and BOT_TOKEN and CHAT_ID:
        tools = ", ".join(context.get("tool_names", []))
        text = f"⚠️ Agent 已运行 {iteration} 步。最后使用的工具: {tools}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text},
            )
```

#### 命令使用记录器

跟踪使用了哪些斜杠命令：

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: 记录斜杠命令使用情况
events:
  - command:*
```

```python
# ~/.hermes/hooks/command-logger/handler.py
import json
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".hermes" / "logs" / "command_usage.jsonl"

def handle(event_type: str, context: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "command": context.get("command"),
        "args": context.get("args"),
        "platform": context.get("platform"),
        "user": context.get("user_id"),
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

#### 会话启动 Webhook

在新会话开始时向外部服务发送 POST 请求：

```yaml
# ~/.hermes/hooks/session-webhook/HOOK.yaml
name: session-webhook
description: 在新会话时通知外部服务
events:
  - session:start
  - session:reset
```
```python
# ~/.hermes/hooks/session-webhook/handler.py
import httpx

WEBHOOK_URL = "https://your-service.example.com/hermes-events"

async def handle(event_type: str, context: dict):
    async with httpx.AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={
            "event": event_type,
            **context,
        }, timeout=5)
```

### 工作原理

1. 消息网关启动时，`HookRegistry.discover_and_load()` 会扫描 `~/.hermes/hooks/` 目录
2. 每个包含 `HOOK.yaml` 和 `handler.py` 的子目录都会被动态加载
3. 处理器会为其声明的事件进行注册
4. 在每个生命周期节点，`hooks.emit()` 会触发所有匹配的处理器
5. 任何处理器中的错误都会被捕获并记录——一个损坏的钩子永远不会导致 Agent 崩溃

:::info
消息网关钩子仅在**消息网关**（Telegram、Discord、Slack、WhatsApp）中触发。CLI 不会加载消息网关钩子。对于需要在所有地方都生效的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子

[插件](/docs/user-guide/features/plugins)可以注册在**CLI 和消息网关**会话中都能触发的钩子。这些钩子通过插件 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册。

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", my_tool_observer)
    ctx.register_hook("post_tool_call", my_tool_logger)
    ctx.register_hook("pre_llm_call", my_memory_callback)
    ctx.register_hook("post_llm_call", my_sync_callback)
    ctx.register_hook("on_session_start", my_init_callback)
    ctx.register_hook("on_session_end", my_cleanup_callback)
```

**所有钩子的通用规则：**

- 回调函数接收**关键字参数**。为了保持向前兼容性，请始终接受 `**kwargs`——未来版本可能会添加新参数，而不会破坏你的插件。
- 如果回调函数**崩溃**，它会被记录并跳过。其他钩子和 Agent 会继续正常运行。行为不当的插件永远不会破坏 Agent。
- 所有钩子都是**触发即忘的观察者**，其返回值会被忽略——除了 `pre_llm_call`，它可以[注入上下文](#pre_llm_call)。

### 快速参考

| 钩子 | 触发时机 | 返回值 |
|------|-----------|---------|
| [`pre_tool_call`](#pre_tool_call) | 在任何工具执行之前 | 忽略 |
| [`post_tool_call`](#post_tool_call) | 在任何工具返回之后 | 忽略 |
| [`pre_llm_call`](#pre_llm_call) | 每轮一次，在工具调用循环之前 | 上下文注入 |
| [`post_llm_call`](#post_llm_call) | 每轮一次，在工具调用循环之后 | 忽略 |
| [`on_session_start`](#on_session_start) | 新会话创建时（仅第一轮） | 忽略 |
| [`on_session_end`](#on_session_end) | 会话结束时 | 忽略 |

---

### `pre_tool_call`

在每次工具执行**之前立即**触发——无论是内置工具还是插件工具。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`、`"web_search"`、`"read_file"`） |
| `args` | `dict` | 模型传递给该工具的参数 |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发位置：** 在 `model_tools.py` 中，`handle_function_call()` 函数内部，在工具的处理器运行之前。每次工具调用触发一次——如果模型并行调用了 3 个工具，则此钩子会触发 3 次。

**返回值：** 忽略。

**使用场景：** 日志记录、审计追踪、工具调用计数器、阻止危险操作（打印警告）、速率限制。

**示例——工具调用审计日志：**

```python
import json, logging
from datetime import datetime

logger = logging.getLogger(__name__)

def audit_tool_call(tool_name, args, task_id, **kwargs):
    logger.info("TOOL_CALL session=%s tool=%s args=%s",
                task_id, tool_name, json.dumps(args)[:200])

def register(ctx):
    ctx.register_hook("pre_tool_call", audit_tool_call)
```

**示例——对危险工具发出警告：**

```python
DANGEROUS = {"terminal", "write_file", "patch"}

def warn_dangerous(tool_name, **kwargs):
    if tool_name in DANGEROUS:
        print(f"⚠ Executing potentially dangerous tool: {tool_name}")

def register(ctx):
    ctx.register_hook("pre_tool_call", warn_dangerous)
```

---

### `post_tool_call`

在每次工具执行返回**之后立即**触发。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 刚刚执行的工具名称 |
| `args` | `dict` | 模型传递给该工具的参数 |
| `result` | `str` | 工具的返回值（始终是 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发位置：** 在 `model_tools.py` 中，`handle_function_call()` 函数内部，在工具的处理器返回之后。每次工具调用触发一次。如果工具引发了未处理的异常，则**不会**触发（错误会被捕获并作为错误 JSON 字符串返回，然后 `post_tool_call` 会以该错误字符串作为 `result` 触发）。

**返回值：** 忽略。

**使用场景：** 记录工具结果、指标收集、跟踪工具成功率/失败率、在特定工具完成时发送通知。

**示例——跟踪工具使用指标：**

```python
from collections import Counter
import json

_tool_counts = Counter()
_error_counts = Counter()

def track_metrics(tool_name, result, **kwargs):
    _tool_counts[tool_name] += 1
    try:
        parsed = json.loads(result)
        if "error" in parsed:
            _error_counts[tool_name] += 1
    except (json.JSONDecodeError, TypeError):
        pass

def register(ctx):
    ctx.register_hook("post_tool_call", track_metrics)
```

---

### `pre_llm_call`

**每轮触发一次**，在工具调用循环开始之前。这是**唯一一个返回值会被使用的钩子**——它可以向当前轮次的用户消息中注入上下文。

**回调函数签名：**
```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 本轮对话用户的原始消息（在任何技能注入之前） |
| `conversation_history` | `list` | 完整消息列表的副本（OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 如果是新会话的第一轮对话则为 `True`，后续轮次为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行的位置：`"cli"`、`"telegram"`、`"discord"` 等 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 函数内，在上下文压缩之后、主 `while` 循环之前。每次调用 `run_conversation()` 时触发一次（即每轮用户对话一次），而不是在工具循环内的每次 API 调用时触发。

**返回值：** 如果回调函数返回一个包含 `"context"` 键的字典，或者一个普通的非空字符串，则该文本会被附加到当前轮次的用户消息中。返回 `None` 表示不注入任何内容。

```python
# 注入上下文
return {"context": "回忆起的记忆：\n- 用户喜欢 Python\n- 正在开发 hermes-agent"}

# 纯字符串（等效）
return "回忆起的记忆：\n- 用户喜欢 Python"

# 不注入
return None
```

**上下文注入的位置：** 始终是**用户消息**，而不是系统提示词。这可以保留提示词缓存——系统提示词在各轮对话中保持相同，因此缓存的 Token 会被重用。系统提示词是 Hermes 的领域（模型指导、工具强制执行、人格、技能）。插件在用户输入旁边贡献上下文。

所有注入的上下文都是**临时的**——仅在 API 调用时添加。对话历史中的原始用户消息永远不会被修改，并且没有任何内容会持久化到会话数据库中。

当**多个插件**返回上下文时，它们的输出会按照插件发现顺序（按目录名称字母顺序）用双换行符连接。

**使用场景：** 记忆召回、RAG 上下文注入、护栏、每轮分析。

**示例——记忆召回：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall(session_id, user_message, is_first_turn, **kwargs):
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None
        text = "回忆起的上下文：\n" + "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None

def register(ctx):
    ctx.register_hook("pre_llm_call", recall)
```

**示例——护栏：**

```python
POLICY = "未经用户明确确认，切勿执行删除文件的命令。"

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

---

### `post_llm_call`

在工具调用循环完成且 Agent 已生成最终响应后，**每轮对话触发一次**。仅在**成功**的轮次触发——如果对话轮次被中断则不触发。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 本轮对话用户的原始消息 |
| `assistant_response` | `str` | Agent 本轮对话的最终文本响应 |
| `conversation_history` | `list` | 本轮对话完成后完整消息列表的副本 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 函数内，在工具循环退出并产生最终响应之后。受 `if final_response and not interrupted` 保护——因此当用户中途中断对话，或者 Agent 达到迭代限制但未产生响应时，它**不会**触发。

**返回值：** 忽略。

**使用场景：** 将会话数据同步到外部记忆系统、计算响应质量指标、记录对话轮次摘要、触发后续操作。

**示例——同步到外部记忆：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def sync_memory(session_id, user_message, assistant_response, **kwargs):
    try:
        httpx.post(f"{MEMORY_API}/store", json={
            "session_id": session_id,
            "user": user_message,
            "assistant": assistant_response,
        }, timeout=5)
    except Exception:
        pass  # 尽力而为

def register(ctx):
    ctx.register_hook("post_llm_call", sync_memory)
```

**示例——跟踪响应长度：**

```python
import logging
logger = logging.getLogger(__name__)

def log_response_length(session_id, assistant_response, model, **kwargs):
    logger.info("RESPONSE session=%s model=%s chars=%d",
                session_id, model, len(assistant_response or ""))

def register(ctx):
    ctx.register_hook("post_llm_call", log_response_length)
```

---

### `on_session_start`

在创建全新会话时触发**一次**。在会话继续时（当用户在现有会话中发送第二条消息时）**不**触发。

**回调函数签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 函数内，在新会话的第一轮对话期间——具体是在系统提示词构建之后、工具循环开始之前。检查条件是 `if not conversation_history`（没有先前的消息 = 新会话）。
**返回值：** 忽略。

**使用场景：** 初始化会话范围内的状态、预热缓存、向外部服务注册会话、记录会话开始。

**示例 — 初始化会话缓存：**

```python
_session_caches = {}

def init_session(session_id, model, platform, **kwargs):
    _session_caches[session_id] = {
        "model": model,
        "platform": platform,
        "tool_calls": 0,
        "started": __import__("datetime").datetime.now().isoformat(),
    }

def register(ctx):
    ctx.register_hook("on_session_start", init_session)
```

---

### `on_session_end`

在每次 `run_conversation()` 调用的**最终阶段**触发，无论结果如何。如果用户在 Agent 处理中途退出，也会从 CLI 的退出处理程序中触发。

**回调函数签名：**

```python
def my_callback(session_id: str, completed: bool, interrupted: bool,
                model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 会话的唯一标识符 |
| `completed` | `bool` | 如果 Agent 产生了最终响应，则为 `True`，否则为 `False` |
| `interrupted` | `bool` | 如果回合被中断（用户发送了新消息、`/stop` 或退出），则为 `True` |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发位置：** 在两个地方：
1. **`run_agent.py`** — 在每次 `run_conversation()` 调用结束时，所有清理工作之后。即使回合出错，也总是会触发。
2. **`cli.py`** — 在 CLI 的 atexit 处理程序中，但**仅当**退出发生时 Agent 正在处理中（`_agent_running=True`）。这可以捕获处理过程中的 Ctrl+C 和 `/exit`。在这种情况下，`completed=False` 且 `interrupted=True`。

**返回值：** 忽略。

**使用场景：** 刷新缓冲区、关闭连接、持久化会话状态、记录会话持续时间、清理在 `on_session_start` 中初始化的资源。

**示例 — 刷新和清理：**

```python
_session_caches = {}

def cleanup_session(session_id, completed, interrupted, **kwargs):
    cache = _session_caches.pop(session_id, None)
    if cache:
        # 将累积的数据刷新到磁盘或外部服务
        status = "completed" if completed else ("interrupted" if interrupted else "failed")
        print(f"Session {session_id} ended: {status}, {cache['tool_calls']} tool calls")

def register(ctx):
    ctx.register_hook("on_session_end", cleanup_session)
```

**示例 — 会话持续时间跟踪：**

```python
import time, logging
logger = logging.getLogger(__name__)

_start_times = {}

def on_start(session_id, **kwargs):
    _start_times[session_id] = time.time()

def on_end(session_id, completed, interrupted, **kwargs):
    start = _start_times.pop(session_id, None)
    if start:
        duration = time.time() - start
        logger.info("SESSION_DURATION session=%s seconds=%.1f completed=%s interrupted=%s",
                     session_id, duration, completed, interrupted)

def register(ctx):
    ctx.register_hook("on_session_start", on_start)
    ctx.register_hook("on_session_end", on_end)
```

---

完整的演练，包括工具模式、处理程序和高级钩子模式，请参阅 **[构建插件指南](/docs/guides/build-a-hermes-plugin)**。