---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "构建一个包含工具、钩子、数据文件和技能的完整 Hermes 插件的分步指南"
---

# 构建 Hermes 插件

本指南将引导您从头开始构建一个完整的 Hermes 插件。最终您将获得一个包含多个工具、生命周期钩子、附带数据文件以及一个捆绑技能的工作插件——涵盖插件系统支持的所有功能。

## 您将构建什么

一个**计算器**插件，包含两个工具：
- `calculate` — 计算数学表达式 (`2**16`, `sqrt(144)`, `pi * 5**2`)
- `unit_convert` — 单位转换 (`100 F → 37.78 C`, `5 km → 3.11 mi`)

此外，还包括一个记录每次工具调用的钩子，以及一个捆绑的技能文件。

## 步骤 1：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 步骤 2：编写清单文件

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: 数学计算器 — 计算表达式和转换单位
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段列出了插件注册的内容。

您可以添加的可选字段：
```yaml
author: Your Name
requires_env:          # 根据环境变量控制加载；安装期间会提示
  - SOME_API_KEY       # 简单格式 — 如果缺失则插件被禁用
  - name: OTHER_KEY    # 丰富格式 — 安装期间显示描述/URL
    description: "Other 服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

## 步骤 3：编写工具模式

创建 `schemas.py` — 这是 LLM 读取以决定何时调用您的工具的内容：

```python
"""工具模式 — LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算数学表达式并返回结果。"
        "支持算术运算 (+, -, *, /, **)、函数 (sqrt, sin, cos, "
        "log, abs, round, floor, ceil) 和常量 (pi, e)。"
        "当用户询问任何数学问题时使用此工具。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式（例如：'2**10', 'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在单位之间转换数值。支持长度 (m, km, mi, ft, in)、"
        "重量 (kg, lb, oz, g)、温度 (C, F, K)、数据 (B, KB, MB, GB, TB) "
        "和时间 (s, min, hr, day)。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "要转换的数值",
            },
            "from_unit": {
                "type": "string",
                "description": "源单位（例如：'km', 'lb', 'F', 'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如：'mi', 'kg', 'C', 'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么模式很重要：** `description` 字段是 LLM 决定何时使用您的工具的依据。请具体说明它的功能和使用时机。`parameters` 定义了 LLM 传递的参数。

## 步骤 4：编写工具处理程序

创建 `tools.py` — 这是当 LLM 调用您的工具时实际执行的代码：

```python
"""工具处理程序 — 当 LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式求值的安全全局变量 — 无文件/网络访问权限
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """安全地计算数学表达式。

    处理程序的规则：
    1. 接收 args (dict) — LLM 传递的参数
    2. 执行工作
    3. 返回 JSON 字符串 — 即使出错也始终返回
    4. 接受 **kwargs 以保持向前兼容性
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "未提供表达式"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "除以零"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"无效: {e}"})


# 转换表 — 值以基本单位表示
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # 归一化到摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换到目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "需要 value、from_unit 和 to_unit"})

    try:
        # 温度转换
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # 基于比率的转换
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"无法转换 {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"转换失败: {e}"})
```
**处理函数的关键规则：**
1. **签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终是一个 JSON 字符串。成功和错误情况都是如此。
3. **永不抛出异常：** 捕获所有异常，返回错误 JSON 代替。
4. **接受 `**kwargs`：** Hermes 未来可能会传递额外的上下文。

## 步骤 5：编写注册代码

创建 `__init__.py` — 这个文件将模式与处理函数连接起来：

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：在每次工具调用后运行（不仅限于我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """将模式连接到处理函数并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 这个钩子会为所有工具调用触发，而不仅限于我们的工具
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时恰好调用一次
- `ctx.register_tool()` 将你的工具放入注册表 — 模型会立即看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册一个 CLI 子命令（例如 `hermes my-plugin <subcommand>`）
- 如果此函数崩溃，插件将被禁用，但 Hermes 会继续正常运行

## 步骤 6：测试它

启动 Hermes：

```bash
hermes
```

你应该能在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试以下提示：
```
2 的 16 次方是多少？
将 100 华氏度转换为摄氏度
2 的平方根乘以 pi 是多少？
1.5 太字节是多少吉字节？
```

检查插件状态：
```
/plugins
```

输出：
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

## 你的插件的最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "我是 calculator，我提供工具和钩子"
├── __init__.py      # 连接：模式 → 处理函数，注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规范）
└── tools.py         # 实际运行的代码（calculate, unit_convert 函数）
```

四个文件，职责清晰：
- **清单** 声明插件是什么
- **模式** 为 LLM 描述工具
- **处理函数** 实现实际逻辑
- **注册** 将所有内容连接起来

## 插件还能做什么？

### 附带数据文件

将任何文件放在你的插件目录中，并在导入时读取它们：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 捆绑一个技能

包含一个 `skill.md` 文件并在注册期间安装它：

```python
import shutil
from pathlib import Path

def _install_skill():
    """在首次加载时，将我们的技能复制到 ~/.hermes/skills/。"""
    try:
        from hermes_cli.config import get_hermes_home
        dest = get_hermes_home() / "skills" / "my-plugin" / "SKILL.md"
    except Exception:
        dest = Path.home() / ".hermes" / "skills" / "my-plugin" / "SKILL.md"

    if dest.exists():
        return  # 不覆盖用户编辑的内容

    source = Path(__file__).parent / "skill.md"
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

def register(ctx):
    ctx.register_tool(...)
    _install_skill()
```

### 基于环境变量启用

如果你的插件需要一个 API 密钥：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件将被禁用并显示明确的消息。不会崩溃，Agent 中也不会出错 — 只是显示 "Plugin weather disabled (missing: WEATHER_API_KEY)"。

当用户运行 `hermes plugins install` 时，系统会**交互式地提示**输入任何缺失的 `requires_env` 变量。值会自动保存到 `.env` 文件中。

为了获得更好的安装体验，可以使用带有描述和注册 URL 的丰富格式：

```yaml
# plugin.yaml — 丰富格式
requires_env:
  - name: WEATHER_API_KEY
    description: "OpenWeather 的 API 密钥"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 是否必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 在安装提示时显示给用户 |
| `url` | 否 | 获取凭据的地址 |
| `secret` | 否 | 如果为 `true`，输入将被隐藏（类似密码字段） |

两种格式可以在同一个列表中混合使用。已设置的变量会被静默跳过。

### 条件性工具可用性

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = 工具对模型隐藏
)
```

### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考

每个钩子都在 **[事件钩子参考](/docs/user-guide/features/hooks#plugin-hooks)** 中有完整文档 — 回调签名、参数表、每个钩子触发的确切时机以及示例。以下是摘要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/docs/user-guide/features/hooks#pre_tool_call) | 在任何工具执行之前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/docs/user-guide/features/hooks#post_tool_call) | 在任何工具返回之后 | `tool_name: str, args: dict, result: str, task_id: str` | 忽略 |
| [`pre_llm_call`](/docs/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/docs/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环之后（仅限成功的轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/docs/user-guide/features/hooks#on_session_start) | 新会话创建时（仅限第一轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/docs/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`pre_api_request`](/docs/user-guide/features/hooks#pre_api_request) | 每次向 LLM 提供商发送 HTTP 请求之前 | `method: str, url: str, headers: dict, body: dict` | 忽略 |
| [`post_api_request`](/docs/user-guide/features/hooks#post_api_request) | 每次从 LLM 提供商收到 HTTP 响应之后 | `method: str, url: str, status_code: int, response: dict` | 忽略 |
大多数钩子都是触发即忘的观察者——它们的返回值会被忽略。唯一的例外是 `pre_llm_call`，它可以向对话中注入上下文。

所有回调函数都应接受 `**kwargs` 参数以保证向前兼容性。如果钩子回调崩溃，它会被记录并跳过。其他钩子和 Agent 会继续正常运行。

### `pre_llm_call` 上下文注入

这是唯一一个返回值有意义的钩子。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或一个纯字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这是记忆插件、RAG 集成、护栏以及任何需要为模型提供额外上下文的插件所使用的机制。

#### 返回格式

```python
# 带 context 键的字典
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# 纯字符串（等同于上面的字典形式）
return "Recalled memories:\n- User prefers dark mode"

# 返回 None 或不返回 → 不注入（仅作为观察者）
return None
```

任何非 None、非空且包含 `"context"` 键的返回值（或纯非空字符串）都会被收集并附加到当前轮次的用户消息中。

#### 注入机制

注入的上下文是附加到**用户消息**，而不是系统提示词。这是一个深思熟虑的设计选择：

- **提示词缓存保留** — 系统提示词在各轮次间保持相同。Anthropic 和 OpenRouter 会缓存系统提示词前缀，因此保持其稳定可以在多轮对话中节省 75% 以上的输入 Token。如果插件修改了系统提示词，每一轮都会导致缓存未命中。
- **临时性** — 注入仅在 API 调用时发生。对话历史中的原始用户消息永远不会被修改，也不会持久化到会话数据库中。
- **系统提示词是 Hermes 的领域** — 它包含模型特定的指导、工具强制执行规则、人格指令以及缓存的技能内容。插件通过提供与用户输入并行的上下文来做出贡献，而不是通过改变 Agent 的核心指令。

#### 示例：记忆召回插件

```python
"""Memory plugin — recalls relevant context from a vector store."""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """Called before each LLM turn. Returns recalled memories."""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # nothing to inject

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # fail silently, don't break the agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：护栏插件

```python
"""Guardrails plugin — enforces content policies."""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """Injects policy text into every turn."""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅观察钩子（无注入）

```python
"""Analytics plugin — tracks turn metadata without injecting context."""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """Fires before each LLM call. Returns None — no context injected."""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # No return → no injection

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文

当多个插件从 `pre_llm_call` 返回上下文时，它们的输出会用双换行符连接起来，并一起附加到用户消息中。顺序遵循插件发现顺序（按插件目录名称字母顺序）。

### 注册 CLI 命令

插件可以添加自己的 `hermes <plugin>` 子命令树：

```python
def _my_command(args):
    """Handler for hermes my-plugin <subcommand>."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """Build the argparse tree for hermes my-plugin."""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show plugin status")
    subs.add_parser("config", help="Show plugin config")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="Manage my plugin",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册后，用户可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**记忆提供商插件**使用基于约定的方法：在你的插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。记忆插件发现系统会自动找到它——不需要调用 `ctx.register_cli_command()`。详情请参阅[记忆提供商插件指南](/docs/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活跃提供商门控：** 记忆插件 CLI 命令仅在其提供商是配置中活跃的 `memory.provider` 时才会出现。如果用户没有设置你的提供商，你的 CLI 命令就不会在帮助输出中造成混乱。

:::tip
本指南涵盖**通用插件**（工具、钩子、CLI 命令）。对于专门的插件类型，请参阅：
- [记忆提供商插件](/docs/developer-guide/memory-provider-plugin) — 跨会话知识后端
- [上下文引擎插件](/docs/developer-guide/context-engine-plugin) — 替代的上下文管理策略
:::
### 通过 pip 分发

要公开分享插件，请向你的 Python 包添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 插件将在下次 hermes 启动时自动发现
```

## 常见错误

**处理程序未返回 JSON 字符串：**
```python
# 错误 — 返回字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理程序签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递额外的上下文会中断
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**处理程序抛出异常：**
```python
# 错误 — 异常传播，工具调用失败
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# 正确 — 捕获并返回错误 JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**模式描述过于模糊：**
```python
# 差 — 模型不知道何时使用它
"description": "Does stuff"

# 好 — 模型确切知道何时以及如何使用
"description": "计算数学表达式。用于算术、三角函数、对数。支持：+, -, *, /, **, sqrt, sin, cos, log, pi, e。"
```