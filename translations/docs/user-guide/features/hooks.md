---
sidebar_position: 6
title: "事件钩子"
description: "在关键生命周期节点运行自定义代码 —— 记录活动、发送警报、发布到 Webhook"
---

# 事件钩子

Hermes 拥有三套钩子系统，可在关键生命周期节点运行自定义代码：

| 系统 | 注册方式 | 运行环境 | 使用场景 |
|--------|---------------|---------|----------|
| **[消息网关钩子](#gateway-event-hooks)** | 在 `~/.hermes/hooks/` 目录下创建 `HOOK.yaml` + `handler.py` | 仅消息网关 | 日志记录、警报、Webhook |
| **[插件钩子](#plugin-hooks)** | 在[插件](/docs/user-guide/features/plugins)中使用 `ctx.register_hook()` | CLI + 消息网关 | 工具拦截、指标收集、防护栏 |
| **[Shell 钩子](#shell-hooks)** | 在 `~/.hermes/config.yaml` 的 `hooks:` 块中指向 Shell 脚本 | CLI + 消息网关 | 用于阻塞、自动格式化、上下文注入的即插即用脚本 |

所有三套系统都是非阻塞的 —— 任何钩子中的错误都会被捕获并记录，永远不会导致 Agent 崩溃。

## 消息网关事件钩子

消息网关钩子在网关（Telegram、Discord、Slack、WhatsApp）运行期间自动触发，不会阻塞主 Agent 流水线。

### 创建钩子

每个钩子是 `~/.hermes/hooks/` 目录下的一个文件夹，包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # 声明要监听哪些事件
    └── handler.py     # Python 处理函数
```

#### HOOK.yaml

```yaml
name: my-hook
description: Log all agent activity to a file
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表决定了哪些事件会触发你的处理函数。你可以订阅任意组合的事件，包括通配符，如 `command:*`。

#### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """Called for each subscribed event. Must be named 'handle'."""
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
- 接收 `event_type` (字符串) 和 `context` (字典) 参数
- 可以是 `async def` 或普通 `def` —— 两者皆可
- 错误会被捕获并记录，永远不会导致 Agent 崩溃

### 可用事件

| 事件 | 触发时机 | 上下文键 |
|-------|---------------|--------------|
| `gateway:startup` | 消息网关进程启动时 | `platforms` (活跃平台名称列表) |
| `session:start` | 创建新的消息会话时 | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | 会话结束时（重置前） | `platform`, `user_id`, `session_key` |
| `session:reset` | 用户执行 `/new` 或 `/reset` 时 | `platform`, `user_id`, `session_key` |
| `agent:start` | Agent 开始处理消息时 | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | 工具调用循环的每次迭代时 | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent 完成处理时 | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | 执行任何斜杠命令时 | `platform`, `user_id`, `command`, `args` |

#### 通配符匹配

注册为 `command:*` 的处理函数会为任何 `command:` 事件（`command:model`、`command:reset` 等）触发。通过一次订阅即可监控所有斜杠命令。

### 示例

#### 长任务 Telegram 警报

当 Agent 执行超过 10 步时，给自己发送一条消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Alert when agent is taking many steps
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
        text = f"⚠️ Agent has been running for {iteration} steps. Last tools: {tools}"
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
description: Log slash command usage
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
description: Notify external service on new sessions
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

### 教程：BOOT.md —— 在每次网关启动时运行启动检查清单

社区中的一个流行模式：在 `~/.hermes/BOOT.md` 放置一个 Markdown 检查清单，让 Agent 在每次网关启动时运行一次。这对于“每次启动时，检查夜间定时任务失败情况，如果有失败则在 Discord 上通知我”，或者“总结过去 24 小时的 deploy.log 并发布到 Slack #ops 频道”非常有用。
本教程展示如何以用户自定义钩子的方式自行构建。Hermes 不提供内置的 BOOT.md 钩子——你可以精确地配置你所需的行为。

#### 我们要构建什么

1. 在 `~/.hermes/BOOT.md` 处创建一个包含自然语言启动指令的文件。
2. 一个在 `gateway:startup` 事件上触发的消息网关钩子，该钩子会使用你消息网关已解析的模型/凭证生成一个一次性 Agent，并执行 BOOT.md 中的指令。
3. 一个 `[SILENT]` 约定，以便当无事可报时，Agent 可以选择不发送消息。

#### 步骤 1：编写你的清单

创建 `~/.hermes/BOOT.md`。像给人类助手下达指令一样编写它：

```markdown
# 启动清单

1. 运行 `hermes cron list` 并检查是否有任何定时任务在夜间失败。
2. 如果有失败的，使用 `send_message` 工具向 Discord #ops 频道发送摘要。
3. 检查 `/opt/app/deploy.log` 在过去 24 小时内是否有任何 ERROR 行。如果有，总结它们并包含在同一条 Discord 消息中。
4. 如果一切正常，仅回复 `[SILENT]` 以便不发送任何消息。
```

Agent 会将其视为其提示词的一部分，因此任何你可以用通俗语言描述的内容都有效——工具调用、shell 命令、发送消息、总结文件。

#### 步骤 2：创建钩子

```text
~/.hermes/hooks/boot-md/
├── HOOK.yaml
└── handler.py
```

**`~/.hermes/hooks/boot-md/HOOK.yaml`**

```yaml
name: boot-md
description: Run ~/.hermes/BOOT.md on gateway startup
events:
  - gateway:startup
```

**`~/.hermes/hooks/boot-md/handler.py`**

```python
"""Run ~/.hermes/BOOT.md on every gateway startup."""

import logging
import threading
from pathlib import Path

logger = logging.getLogger("hooks.boot-md")

BOOT_FILE = Path.home() / ".hermes" / "BOOT.md"


def _build_prompt(content: str) -> str:
    return (
        "You are running a startup boot checklist. Follow the instructions "
        "below exactly.\n\n"
        "---\n"
        f"{content}\n"
        "---\n\n"
        "Execute each instruction. Use the send_message tool to deliver any "
        "messages to platforms like Discord or Slack.\n"
        "If nothing needs attention and there is nothing to report, reply "
        "with ONLY: [SILENT]"
    )


def _run_boot_agent(content: str) -> None:
    """Spawn a one-shot agent and execute the checklist.

    Uses the gateway's resolved model and runtime credentials so this works
    against custom endpoints, aggregators, and OAuth-based providers alike.
    """
    try:
        from gateway.run import _resolve_gateway_model, _resolve_runtime_agent_kwargs
        from run_agent import AIAgent

        agent = AIAgent(
            model=_resolve_gateway_model(),
            **_resolve_runtime_agent_kwargs(),
            platform="gateway",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            max_iterations=20,
        )
        result = agent.run_conversation(_build_prompt(content))
        response = result.get("final_response", "")
        if response and "[SILENT]" not in response:
            logger.info("boot-md completed: %s", response[:200])
        else:
            logger.info("boot-md completed (nothing to report)")
    except Exception as e:
        logger.error("boot-md agent failed: %s", e)


async def handle(event_type: str, context: dict) -> None:
    if not BOOT_FILE.exists():
        return
    content = BOOT_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return

    logger.info("Running BOOT.md (%d chars)", len(content))

    # Background thread so gateway startup isn't blocked on a full agent turn.
    thread = threading.Thread(
        target=_run_boot_agent,
        args=(content,),
        name="boot-md",
        daemon=True,
    )
    thread.start()
```

两个关键行：

- `_resolve_gateway_model()` 读取消息网关当前配置的模型。
- `_resolve_runtime_agent_kwargs()` 以与正常消息网关轮次相同的方式解析提供商凭证——包括 API 密钥、基础 URL、OAuth Token 和凭证池。

没有这些，一个裸的 `AIAgent()` 会回退到内置默认值，并且针对任何非默认端点都会返回 401 错误。

#### 步骤 3：测试它

重启消息网关：

```bash
hermes gateway restart
```

查看日志：

```bash
hermes logs --follow --level INFO | grep boot-md
```

你应该会看到 `Running BOOT.md (N chars)`，然后是 `boot-md completed: ...`（Agent 所做操作的摘要）或者当 Agent 回复 `[SILENT]` 时看到 `boot-md completed (nothing to report)`。

删除 `~/.hermes/BOOT.md` 以禁用清单——钩子保持加载状态，但当文件不存在时会静默跳过。

#### 扩展模式

- **基于日程的清单：** 在 BOOT.md 的指令中根据 `datetime.now().weekday()` 判断（"如果是周一，同时检查每周部署日志"）。指令是自由格式的文本，因此任何 Agent 可以进行推理的内容都是可行的。
- **多个清单：** 将钩子指向不同的文件（`STARTUP.md`、`MORNING.md` 等），并为每个文件注册单独的钩子目录。
- **非 Agent 变体：** 如果不需要完整的 Agent 循环，可以完全跳过 `AIAgent`，让处理程序直接通过 `httpx` 发布固定的通知。更便宜、更快，并且没有提供商依赖。

#### 为什么这不是内置功能

Hermes 的早期版本将此作为内置钩子提供，并在每次消息网关启动时使用裸默认值静默生成一个 Agent。这让使用自定义端点的用户感到意外，并且对于不知道它正在运行的用户来说，该功能是不可见的。将其保留为文档化的模式——由你在你的钩子目录中构建——意味着你可以确切地看到它的作用，并通过编写文件来选择加入。

### 工作原理

1. 在消息网关启动时，`HookRegistry.discover_and_load()` 扫描 `~/.hermes/hooks/`
2. 每个包含 `HOOK.yaml` + `handler.py` 的子目录都会被动态加载
3. 处理程序为其声明的事件进行注册
4. 在每个生命周期点，`hooks.emit()` 触发所有匹配的处理程序
5. 任何处理程序中的错误都会被捕获并记录——损坏的钩子永远不会使 Agent 崩溃
:::info
消息网关钩子仅在**消息网关**（Telegram、Discord、Slack、WhatsApp）中触发。CLI 不会加载消息网关钩子。如需在所有地方都生效的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子

[插件](/docs/user-guide/features/plugins)可以注册在**CLI 和消息网关**会话中均会触发的钩子。这些钩子通过插件 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册。

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

- 回调函数接收**关键字参数**。为了保持向前兼容性，请始终接受 `**kwargs` —— 未来版本可能会添加新参数，而不会破坏你的插件。
- 如果回调函数**崩溃**，它会被记录并跳过。其他钩子和 Agent 会继续正常运行。行为不当的插件永远不会破坏 Agent。
- 有两个钩子的返回值会影响行为：[`pre_tool_call`](#pre_tool_call) 可以**阻止**工具调用，而 [`pre_llm_call`](#pre_llm_call) 可以**注入上下文**到 LLM 调用中。所有其他钩子都是触发后即忘的观察者。

### 快速参考

| 钩子 | 触发时机 | 返回值 |
|------|-----------|---------|
| [`pre_tool_call`](#pre_tool_call) | 任何工具执行之前 | `{"action": "block", "message": str}` 以否决调用 |
| [`post_tool_call`](#post_tool_call) | 任何工具返回之后 | 忽略 |
| [`pre_llm_call`](#pre_llm_call) | 每轮对话一次，在工具调用循环之前 | `{"context": str}` 以在用户消息前添加上下文 |
| [`post_llm_call`](#post_llm_call) | 每轮对话一次，在工具调用循环之后 | 忽略 |
| [`on_session_start`](#on_session_start) | 新会话创建时（仅限第一轮） | 忽略 |
| [`on_session_end`](#on_session_end) | 会话结束时 | 忽略 |
| [`on_session_finalize`](#on_session_finalize) | CLI/消息网关销毁活动会话时（刷新、保存、统计） | 忽略 |
| [`on_session_reset`](#on_session_reset) | 消息网关交换新的会话密钥时（例如 `/new`、`/reset`） | 忽略 |
| [`subagent_stop`](#subagent_stop) | 一个 `delegate_task` 子 Agent 已退出 | 忽略 |
| [`pre_gateway_dispatch`](#pre_gateway_dispatch) | 消息网关收到用户消息后，在认证和分发之前 | `{"action": "skip" \| "rewrite" \| "allow", ...}` 以影响流程 |
| [`pre_approval_request`](#pre_approval_request) | 危险命令需要用户批准，在发送提示/通知之前 | 忽略 |
| [`post_approval_response`](#post_approval_response) | 用户响应了批准提示（或超时） | 忽略 |

---

### `pre_tool_call`

在每次工具执行**之前立即**触发 —— 包括内置工具和插件工具。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`、`"web_search"`、`"read_file"`） |
| `args` | `dict` | 模型传递给该工具的参数 |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发位置：** 在 `model_tools.py` 的 `handle_function_call()` 内部，在工具的处理器运行之前。每次工具调用触发一次 —— 如果模型并行调用了 3 个工具，则此钩子会触发 3 次。

**返回值 —— 否决调用：**

```python
return {"action": "block", "message": "工具调用被阻止的原因"}
```

Agent 将短路该工具调用，并将 `message` 作为错误返回给模型。第一个匹配的阻止指令生效（Python 插件优先注册，然后是 shell 钩子）。任何其他返回值都会被忽略，因此现有的仅作为观察者的回调函数可以保持不变地继续工作。

**使用场景：** 日志记录、审计追踪、工具调用计数器、阻止危险操作、速率限制、按用户策略执行。

**示例 —— 工具调用审计日志：**

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

**示例 —— 对危险工具发出警告：**

```python
DANGEROUS = {"terminal", "write_file", "patch"}

def warn_dangerous(tool_name, **kwargs):
    if tool_name in DANGEROUS:
        print(f"⚠ 正在执行潜在危险的工具: {tool_name}")

def register(ctx):
    ctx.register_hook("pre_tool_call", warn_dangerous)
```

---

### `post_tool_call`

在每次工具执行返回**之后立即**触发。

**回调函数签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 刚刚执行的工具名称 |
| `args` | `dict` | 模型传递给该工具的参数 |
| `result` | `str` | 工具的返回值（始终是一个 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |
| `duration_ms` | `int` | 工具分发所花费的时间，以毫秒为单位（在 `registry.dispatch()` 周围使用 `time.monotonic()` 测量）。 |

**触发位置：** 在 `model_tools.py` 的 `handle_function_call()` 内部，在工具的处理器返回之后。每次工具调用触发一次。如果工具引发了未处理的异常，则**不会**触发（错误会被捕获并作为错误 JSON 字符串返回，并且 `post_tool_call` 会以该错误字符串作为 `result` 触发）。

**返回值：** 忽略。

**使用场景：** 记录工具结果、指标收集、跟踪工具成功率/失败率、延迟仪表板、按工具预算警报、特定工具完成时发送通知。
**示例 — 跟踪工具使用指标：**

```python
from collections import Counter, defaultdict
import json

_tool_counts = Counter()
_error_counts = Counter()
_latency_ms = defaultdict(list)

def track_metrics(tool_name, result, duration_ms=0, **kwargs):
    _tool_counts[tool_name] += 1
    _latency_ms[tool_name].append(duration_ms)
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

在**每个回合触发一次**，在工具调用循环开始之前。这是**唯一一个返回值会被使用的钩子**——它可以向当前回合的用户消息中注入上下文。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户此回合的原始消息（在任何技能注入之前） |
| `conversation_history` | `list` | 完整消息列表的副本（OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 如果是新会话的第一个回合则为 `True`，后续回合为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行的位置：`"cli"`、`"telegram"`、`"discord"` 等。 |

**触发位置：** 在 `run_agent.py` 的 `run_conversation()` 函数内部，在上下文压缩之后，主 `while` 循环之前。每个 `run_conversation()` 调用触发一次（即每个用户回合一次），而不是工具循环内的每次 API 调用一次。

**返回值：** 如果回调函数返回一个包含 `"context"` 键的字典，或者一个普通的非空字符串，则该文本会被追加到当前回合的用户消息中。返回 `None` 表示不注入。

```python
# 注入上下文
return {"context": "回忆起的记忆：\n- 用户喜欢 Python\n- 正在开发 hermes-agent"}

# 普通字符串（等效）
return "回忆起的记忆：\n- 用户喜欢 Python"

# 不注入
return None
```

**上下文注入的位置：** 始终是**用户消息**，而不是系统提示词。这保留了提示词缓存——系统提示词在各个回合中保持相同，因此缓存的 Token 会被重用。系统提示词是 Hermes 的领域（模型指导、工具强制执行、人格、技能）。插件在用户输入旁边贡献上下文。

所有注入的上下文都是**临时的**——仅在 API 调用时添加。会话历史中的原始用户消息永远不会被修改，并且没有任何内容会持久化到会话数据库中。

当**多个插件**返回上下文时，它们的输出会按照插件发现顺序（按目录名字母顺序）用双换行符连接。

**使用场景：** 记忆召回、RAG 上下文注入、防护栏、每回合分析。

**示例 — 记忆召回：**

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

**示例 — 防护栏：**

```python
POLICY = "未经用户明确确认，切勿执行删除文件的命令。"

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

---

### `post_llm_call`

在**每个回合触发一次**，在工具调用循环完成且 Agent 已生成最终响应之后。仅在**成功的**回合触发——如果回合被中断则不触发。

**回调函数签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户此回合的原始消息 |
| `assistant_response` | `str` | Agent 此回合的最终文本响应 |
| `conversation_history` | `list` | 回合完成后完整消息列表的副本 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发位置：** 在 `run_agent.py` 的 `run_conversation()` 函数内部，在工具循环退出并产生最终响应之后。受 `if final_response and not interrupted` 保护——因此当用户中途中断或 Agent 达到迭代限制但未产生响应时，它**不会**触发。

**返回值：** 被忽略。

**使用场景：** 将会话数据同步到外部记忆系统、计算响应质量指标、记录回合摘要、触发后续操作。

**示例 — 同步到外部记忆：**

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

**示例 — 跟踪响应长度：**

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

在创建全新会话时触发**一次**。在会话继续时（当用户在现有会话中发送第二条消息时）**不会**触发。

**回调函数签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发位置：** 在 `run_agent.py` 的 `run_conversation()` 函数内部，在新会话的第一个回合期间——具体是在系统提示词构建之后，工具循环开始之前。判断条件是 `if not conversation_history`（没有先前的消息 = 新会话）。

**返回值：** 忽略。

**使用场景：** 初始化会话作用域的状态、预热缓存、向外部服务注册会话、记录会话开始。

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

在每次 `run_conversation()` 调用的**最后**触发，无论结果如何。如果用户在 Agent 处理中途退出，也会从 CLI 的退出处理程序中触发。

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
1. **`run_agent.py`** — 在每次 `run_conversation()` 调用的末尾，所有清理工作之后。即使回合出错也会触发。
2. **`cli.py`** — 在 CLI 的 atexit 处理程序中，但**仅当**退出发生时 Agent 正在处理中（`_agent_running=True`）。这可以捕获处理过程中的 Ctrl+C 和 `/exit`。在这种情况下，`completed=False` 且 `interrupted=True`。

**返回值：** 忽略。

**使用场景：** 刷新缓冲区、关闭连接、持久化会话状态、记录会话时长、清理在 `on_session_start` 中初始化的资源。

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

**示例 — 会话时长跟踪：**

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

### `on_session_finalize`

当 CLI 或消息网关**销毁**一个活动会话时触发——例如，当用户运行 `/new`、网关垃圾回收了空闲会话，或者 CLI 退出时有一个活动的 Agent。这是在会话身份消失之前，刷新与该即将结束的会话相关的状态的最后机会。

**回调函数签名：**

```python
def my_callback(session_id: str | None, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` 或 `None` | 即将结束的会话 ID。如果不存在活动会话，可能为 `None`。 |
| `platform` | `str` | `"cli"` 或消息平台名称（`"telegram"`、`"discord"` 等）。 |

**触发位置：** 在 `cli.py` 中（执行 `/new` 或 CLI 退出时）和 `gateway/run.py` 中（当会话被重置或垃圾回收时）。在网关端总是与 `on_session_reset` 配对出现。

**返回值：** 忽略。

**使用场景：** 在会话 ID 被丢弃之前持久化最终的会话指标、关闭每个会话的资源、发出最终的遥测事件、清空排队的写入操作。

---

### `on_session_reset`

当网关为活动聊天**交换新的会话密钥**时触发——用户调用了 `/new`、`/reset`、`/clear`，或者适配器在空闲窗口后选取了一个新的会话。这让插件能够对会话状态已被清空这一事实做出反应，而无需等待下一个 `on_session_start`。

**回调函数签名：**

```python
def my_callback(session_id: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的 ID（已经轮换为新的值）。 |
| `platform` | `str` | 消息平台名称。 |

**触发位置：** 在 `gateway/run.py` 中，在新会话密钥分配之后、下一个入站消息被处理之前立即触发。在网关上，顺序是：`on_session_finalize(old_id)` → 交换 → `on_session_reset(new_id)` → 在第一个入站回合时触发 `on_session_start(new_id)`。

**返回值：** 忽略。

**使用场景：** 重置按 `session_id` 键控的每个会话缓存、发出“会话已轮换”的分析数据、准备一个新的状态存储桶。
---

完整教程（包括工具模式、处理程序和高级钩子模式）请参阅 **[构建插件指南](/docs/guides/build-a-hermes-plugin)**。

---

### `subagent_stop`

在 `delegate_task` 完成后，**每个子 Agent 触发一次**。无论你是委派了单个任务还是三个任务，此钩子都会为每个子 Agent 触发一次，并在父线程上串行执行。

**回调函数签名：**

```python
def my_callback(parent_session_id: str, child_role: str | None,
                child_summary: str | None, child_status: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `parent_session_id` | `str` | 委派任务的父 Agent 的会话 ID |
| `child_role` | `str \| None` | 在子 Agent 上设置的编排器角色标签（如果功能未启用则为 `None`） |
| `child_summary` | `str \| None` | 子 Agent 返回给父 Agent 的最终响应 |
| `child_status` | `str` | `"completed"`、`"failed"`、`"interrupted"` 或 `"error"` |
| `duration_ms` | `int` | 运行子 Agent 所花费的挂钟时间，单位毫秒 |

**触发位置：** 在 `tools/delegate_tool.py` 中，在 `ThreadPoolExecutor.as_completed()` 处理完所有子 Future 之后。触发被调度到父线程，因此钩子作者无需考虑并发回调执行。

**返回值：** 忽略。

**使用场景：** 记录编排活动、累计子 Agent 运行时长用于计费、编写委派后审计记录。

**示例 — 记录编排器活动：**

```python
import logging
logger = logging.getLogger(__name__)

def log_subagent(parent_session_id, child_role, child_status, duration_ms, **kwargs):
    logger.info(
        "SUBAGENT parent=%s role=%s status=%s duration_ms=%d",
        parent_session_id, child_role, child_status, duration_ms,
    )

def register(ctx):
    ctx.register_hook("subagent_stop", log_subagent)
```

:::info
在大量委派的情况下（例如，编排器角色 × 5 个叶子节点 × 嵌套深度），`subagent_stop` 每轮会触发多次。请保持回调函数快速执行；将耗时的工作推送到后台队列。
:::

---

### `pre_gateway_dispatch`

在消息网关中，**每个传入的 `MessageEvent` 触发一次**，在内部事件守卫之后，但在身份验证/配对和 Agent 调度**之前**。这是消息网关级消息流策略（仅监听窗口、人工交接、按聊天路由等）的拦截点，这些策略不适合任何单一平台适配器。

**回调函数签名：**

```python
def my_callback(event, gateway, session_store, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `event` | `MessageEvent` | 规范化的入站消息（具有 `.text`、`.source`、`.message_id`、`.internal` 等属性）。 |
| `gateway` | `GatewayRunner` | 活动的消息网关运行器，因此插件可以调用 `gateway.adapters[platform].send(...)` 进行旁路回复（所有者通知等）。 |
| `session_store` | `SessionStore` | 用于通过 `session_store.append_to_transcript(...)` 静默摄取对话记录。 |

**触发位置：** 在 `gateway/run.py` 的 `GatewayRunner._handle_message()` 内部，在计算完 `is_internal` 后立即触发。**内部事件完全跳过此钩子**（它们是系统生成的——后台进程完成等——不得被面向用户的策略拦截）。

**返回值：** `None` 或字典。第一个被识别的操作字典生效；其余插件结果将被忽略。插件回调中的异常会被捕获并记录；发生错误时，消息网关总是会回退到正常调度。

| 返回值 | 效果 |
|--------|--------|
| `{"action": "skip", "reason": "..."}` | 丢弃消息——无 Agent 回复、无配对流程、无身份验证。假定插件已处理该消息（例如，静默摄取到对话记录中）。 |
| `{"action": "rewrite", "text": "new text"}` | 替换 `event.text`，然后使用修改后的事件继续正常调度。适用于将缓冲的环境消息合并为单个提示词。 |
| `{"action": "allow"}` / `None` | 正常调度——运行完整的身份验证 / 配对 / Agent 循环链。 |

**使用场景：** 仅监听的群聊（仅在标记时回复；将环境消息缓冲到上下文中）；人工交接（在所有者手动处理聊天时静默摄取客户消息）；按配置文件速率限制；策略驱动的路由。

**示例 — 静默丢弃未经授权的私聊消息，不触发配对代码：**

```python
def deny_unauthorized_dms(event, **kwargs):
    src = event.source
    if src.chat_type == "dm" and not _is_approved_user(src.user_id):
        return {"action": "skip", "reason": "unauthorized-dm"}
    return None

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", deny_unauthorized_dms)
```

**示例 — 在被提及时将环境消息缓冲区重写为单个提示词：**

```python
_buffers = {}

def buffer_or_rewrite(event, **kwargs):
    key = (event.source.platform, event.source.chat_id)
    buf = _buffers.setdefault(key, [])
    if _bot_mentioned(event.text):
        combined = "\n".join(buf + [event.text])
        buf.clear()
        return {"action": "rewrite", "text": combined}
    buf.append(event.text)
    return {"action": "skip", "reason": "ambient-buffered"}

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", buffer_or_rewrite)
```

---

### `pre_approval_request`

在向用户显示审批请求**之前立即触发**——涵盖所有界面：交互式 CLI、Ink TUI、消息网关平台（Telegram、Discord、Slack、WhatsApp、Matrix 等）和 ACP 客户端（VS Code、Zed、JetBrains 等）。

这是连接自定义通知器的正确位置——例如，一个 macOS 菜单栏应用，弹出允许/拒绝通知；或者一个审计日志，记录每个带有上下文的审批请求。

**回调函数签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    **kwargs,
):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 等待批准的 shell 命令 |
| `description` | `str` | 命令被标记的人类可读原因（当多个模式匹配时合并） |
| `pattern_key` | `str` | 触发审批的主要模式键（例如 `"rm_rf"`、`"sudo"`） |
| `pattern_keys` | `list[str]` | 所有匹配的模式键 |
| `session_key` | `str` | 会话标识符，用于按聊天范围通知 |
| `surface` | `str` | 交互式 CLI/TUI 提示为 `"cli"`，异步平台审批为 `"gateway"` |
**返回值：** 忽略。此处的钩子仅为观察者；它们无法否决或预先回应审批请求。使用 [`pre_tool_call`](#pre_tool_call) 在工具到达审批系统之前阻止它。

**使用场景：** 桌面通知、推送提醒、审计日志记录、Slack webhook、升级路由、指标收集。

**示例 — macOS 桌面通知：**

```python
import subprocess

def notify_approval(command, description, session_key, **kwargs):
    title = "Hermes 需要审批"
    body = f"{description}: {command[:80]}"
    subprocess.Popen([
        "osascript", "-e",
        f'display notification "{body}" with title "{title}"',
    ])

def register(ctx):
    ctx.register_hook("pre_approval_request", notify_approval)
```

---

### `post_approval_response`

在用户响应审批提示（或提示超时）**之后**触发。

**回调签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    choice: str,
    **kwargs,
):
```

参数与 `pre_approval_request` 相同，额外增加：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `choice` | `str` | 取值为 `"once"`、`"session"`、`"always"`、`"deny"` 或 `"timeout"` 之一 |

**返回值：** 忽略。

**使用场景：** 关闭匹配的桌面通知、在审计日志中记录最终决定、更新指标、推进速率限制器。

```python
def log_decision(command, choice, session_key, **kwargs):
    logger.info("approval %s: %s for session %s", choice, command[:60], session_key)

def register(ctx):
    ctx.register_hook("post_approval_response", log_decision)
```

---

## Shell 钩子

在你的 `cli-config.yaml` 中声明 shell 脚本钩子，每当对应的插件钩子事件触发时，Hermes 将在 CLI 和消息网关会话中将其作为子进程运行。无需编写 Python 插件。

当你希望使用一个即插即用的单文件脚本（Bash、Python 或任何带 shebang 的脚本）来实现以下功能时，请使用 shell 钩子：

- **阻止工具调用** — 拒绝危险的 `terminal` 命令、强制执行按目录策略、要求对破坏性的 `write_file` / `patch` 操作进行审批。
- **在工具调用后运行** — 自动格式化 Agent 刚写入的 Python 或 TypeScript 文件、记录 API 调用、触发 CI 工作流。
- **向下一个 LLM 轮次注入上下文** — 将 `git status` 输出、当前工作日或检索到的文档附加到用户消息前（参见 [`pre_llm_call`](#pre_llm_call)）。
- **观察生命周期事件** — 在子 Agent 完成（`subagent_stop`）或会话开始（`on_session_start`）时写入日志行。

通过在 CLI 启动（`hermes_cli/main.py`）和消息网关启动（`gateway/run.py`）时调用 `agent.shell_hooks.register_from_config(cfg)` 来注册 shell 钩子。它们与 Python 插件钩子自然组合 — 两者都通过同一个调度器流转。

### 一览对比

| 维度 | Shell 钩子 | [插件钩子](#plugin-hooks) | [消息网关钩子](#gateway-event-hooks) |
|-----------|-------------|-------------------------------|---------------------------------------|
| 声明位置 | `~/.hermes/config.yaml` 中的 `hooks:` 块 | `plugin.yaml` 插件中的 `register()` | `HOOK.yaml` + `handler.py` 目录 |
| 存放位置 | `~/.hermes/agent-hooks/`（按约定） | `~/.hermes/plugins/<name>/` | `~/.hermes/hooks/<name>/` |
| 语言 | 任意（Bash、Python、Go 二进制文件等） | 仅 Python | 仅 Python |
| 运行环境 | CLI + 消息网关 | CLI + 消息网关 | 仅消息网关 |
| 事件 | `VALID_HOOKS`（包括 `subagent_stop`） | `VALID_HOOKS` | 消息网关生命周期（`gateway:startup`、`agent:*`、`command:*`） |
| 能否阻止工具调用 | 是（`pre_tool_call`） | 是（`pre_tool_call`） | 否 |
| 能否注入 LLM 上下文 | 是（`pre_llm_call`） | 是（`pre_llm_call`） | 否 |
| 同意机制 | 每个 `(事件, 命令)` 对的首次使用提示 | 隐式（信任 Python 插件） | 隐式（信任目录） |
| 进程间隔离 | 是（子进程） | 否（进程内） | 否（进程内） |

### 配置模式

```yaml
hooks:
  <event_name>:                  # 必须在 VALID_HOOKS 中
    - matcher: "<regex>"         # 可选；仅用于 pre/post_tool_call
      command: "<shell command>" # 必需；通过 shlex.split 运行，shell=False
      timeout: <seconds>         # 可选；默认 60，上限 300

hooks_auto_accept: false         # 参见下面的“同意模型”
```

事件名称必须是[插件钩子事件](#plugin-hooks)之一；拼写错误会产生“Did you mean X?”警告并被跳过。单个条目内的未知键将被忽略；缺少 `command` 会发出警告并跳过。`timeout > 300` 会被限制并发出警告。

### JSON 通信协议

每次事件触发时，Hermes 会为每个匹配的钩子（在匹配器允许的情况下）生成一个子进程，将 JSON 负载通过管道传输到 **stdin**，并将 **stdout** 读取为 JSON。

**stdin — 脚本接收的负载：**

```json
{
  "hook_event_name": "pre_tool_call",
  "tool_name":       "terminal",
  "tool_input":      {"command": "rm -rf /"},
  "session_id":      "sess_abc123",
  "cwd":             "/home/user/project",
  "extra":           {"task_id": "...", "tool_call_id": "..."}
}
```

对于非工具事件（`pre_llm_call`、`subagent_stop`、会话生命周期），`tool_name` 和 `tool_input` 为 `null`。`extra` 字典携带所有事件特定的 kwargs（`user_message`、`conversation_history`、`child_role`、`duration_ms` 等）。不可序列化的值会被字符串化而不是被省略。

**stdout — 可选的响应：**

```jsonc
// 阻止 pre_tool_call（两种形式均可接受；内部会规范化）：
{"decision": "block", "reason":  "Forbidden: rm -rf"}   // Claude-Code 风格
{"action":   "block", "message": "Forbidden: rm -rf"}   // Hermes 规范风格

// 为 pre_llm_call 注入上下文：
{"context": "Today is Friday, 2026-04-17"}

// 静默无操作 — 任何空的/不匹配的输出都可以：
```

格式错误的 JSON、非零退出码和超时会记录警告，但永远不会中止 Agent 循环。

### 工作示例
#### 1. 每次写入后自动格式化 Python 文件

```yaml
# ~/.hermes/config.yaml
hooks:
  post_tool_call:
    - matcher: "write_file|patch"
      command: "~/.hermes/agent-hooks/auto-format.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/auto-format.sh
payload="$(cat -)"
path=$(echo "$payload" | jq -r '.tool_input.path // empty')
[[ "$path" == *.py ]] && command -v black >/dev/null && black "$path" 2>/dev/null
printf '{}\n'
```

Agent 在上下文中的文件视图**不会**自动重新读取 —— 重新格式化仅影响磁盘上的文件。后续的 `read_file` 调用会获取格式化后的版本。

#### 2. 阻止破坏性的 `terminal` 命令

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal"
      command: "~/.hermes/agent-hooks/block-rm-rf.sh"
      timeout: 5
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/block-rm-rf.sh
payload="$(cat -)"
cmd=$(echo "$payload" | jq -r '.tool_input.command // empty')
if echo "$cmd" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+/'; then
  printf '{"decision": "block", "reason": "blocked: rm -rf / is not permitted"}\n'
else
  printf '{}\n'
fi
```

#### 3. 在每个回合注入 `git status`（相当于 Claude-Code 的 `UserPromptSubmit`）

```yaml
hooks:
  pre_llm_call:
    - command: "~/.hermes/agent-hooks/inject-cwd-context.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/inject-cwd-context.sh
cat - >/dev/null   # 丢弃标准输入的有效载荷
if status=$(git status --porcelain 2>/dev/null) && [[ -n "$status" ]]; then
  jq --null-input --arg s "$status" \
     '{context: ("Uncommitted changes in cwd:\n" + $s)}'
else
  printf '{}\n'
fi
```

Claude Code 的 `UserPromptSubmit` 事件特意不作为单独的 Hermes 事件实现 —— `pre_llm_call` 在相同位置触发并且已经支持上下文注入。在这里使用它。

#### 4. 记录每个子 Agent 的完成情况

```yaml
hooks:
  subagent_stop:
    - command: "~/.hermes/agent-hooks/log-orchestration.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/log-orchestration.sh
log=~/.hermes/logs/orchestration.log
jq -c '{ts: now, parent: .session_id, extra: .extra}' < /dev/stdin >> "$log"
printf '{}\n'
```

### 同意模型

每个唯一的 `(事件, 命令)` 对在 Hermes 首次遇到时会提示用户批准，然后将决定持久化到 `~/.hermes/shell-hooks-allowlist.json`。后续运行（CLI 或消息网关）会跳过提示。

有三种逃生舱口可以绕过交互式提示 —— 满足任意一种即可：

1. CLI 上的 `--accept-hooks` 标志（例如 `hermes --accept-hooks chat`）
2. 环境变量 `HERMES_ACCEPT_HOOKS=1`
3. `cli-config.yaml` 中的 `hooks_auto_accept: true`

非 TTY 运行（消息网关、定时任务、CI）需要上述三种方式之一 —— 否则任何新添加的钩子将静默保持未注册状态并记录警告。

**脚本编辑会被静默信任。** 允许列表基于确切的命令字符串，而不是脚本的哈希值，因此编辑磁盘上的脚本不会使同意失效。`hermes hooks doctor` 会标记修改时间漂移，以便您发现编辑并决定是否重新批准。

### `hermes hooks` CLI

| 命令 | 功能 |
|---------|--------------|
| `hermes hooks list` | 转储已配置的钩子，包括匹配器、超时和同意状态 |
| `hermes hooks test <事件> [--for-tool X] [--payload-file F]` | 针对合成有效载荷触发每个匹配的钩子并打印解析后的响应 |
| `hermes hooks revoke <命令>` | 移除与 `<命令>` 匹配的每个允许列表条目（在下次重启时生效） |
| `hermes hooks doctor` | 对于每个已配置的钩子：检查执行权限、允许列表状态、修改时间漂移、JSON 输出有效性以及粗略执行时间 |

### 安全性

Shell 钩子以**您的完整用户凭据**运行 —— 与定时任务条目或 Shell 别名处于相同的信任边界。请将 `config.yaml` 中的 `hooks:` 块视为特权配置：

- 仅引用您编写或完全审查过的脚本。
- 将脚本保存在 `~/.hermes/agent-hooks/` 内，以便路径易于审计。
- 在拉取共享配置后重新运行 `hermes hooks doctor`，以便在新添加的钩子注册之前发现它们。
- 如果您的 config.yaml 在团队中进行版本控制，请像审查 CI 配置一样审查更改 `hooks:` 部分的 PR。

### 顺序和优先级

Python 插件钩子和 Shell 钩子都通过同一个 `invoke_hook()` 调度器。Python 插件首先注册（`discover_and_load()`），Shell 钩子其次（`register_from_config()`），因此在平局情况下，Python 的 `pre_tool_call` 阻止决定具有优先权。第一个有效的阻止获胜 —— 一旦任何回调产生带有非空消息的 `{"action": "block", "message": str}`，聚合器就会返回。