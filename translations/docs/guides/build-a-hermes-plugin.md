---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "构建一个包含工具、钩子、数据文件和技能的完整 Hermes 插件的分步指南"
---

# 构建 Hermes 插件

本指南将引导您从头开始构建一个完整的 Hermes 插件。最终您将得到一个包含多个工具、生命周期钩子、附带数据文件以及一个捆绑技能的工作插件——涵盖插件系统支持的所有功能。

:::info 不确定需要哪个指南？
Hermes 有几个不同的可插拔接口——有些使用 Python `register_*` API，有些是配置驱动或即插即用目录。请先使用此地图：

| 如果您想添加… | 请阅读 |
|---|---|
| 自定义工具、钩子、斜杠命令、技能或 CLI 子命令 | **本指南**（通用插件接口） |
| **LLM / 推理后端**（新提供商） | [模型提供商插件](/docs/developer-guide/model-provider-plugin) |
| **消息网关通道**（Discord/Telegram/IRC/Teams 等） | [添加平台适配器](/docs/developer-guide/adding-platform-adapters) |
| **记忆后端**（Honcho/Mem0/Supermemory 等） | [记忆提供商插件](/docs/developer-guide/memory-provider-plugin) |
| **上下文压缩引擎** | [上下文引擎插件](/docs/developer-guide/context-engine-plugin) |
| **图像生成后端** | [图像生成提供商插件](/docs/developer-guide/image-gen-provider-plugin) |
| **TTS 后端**（任何 CLI —— Piper, VoxCPM, Kokoro, 语音克隆, …） | [TTS 自定义命令提供商](/docs/user-guide/features/tts#custom-command-providers) —— 配置驱动，无需 Python |
| **STT 后端**（自定义 whisper / ASR CLI） | [语音消息转录](/docs/user-guide/features/tts#voice-message-transcription-stt) —— 将 `HERMES_LOCAL_STT_COMMAND` 设置为 shell 模板 |
| **通过 MCP 的外部工具**（文件系统、GitHub、Linear、任何 MCP 服务器） | [MCP](/docs/user-guide/features/mcp) —— 在 `config.yaml` 中声明 `mcp_servers.<name>` |
| **消息网关事件钩子**（启动时触发、会话事件、命令） | [事件钩子](/docs/user-guide/features/hooks#gateway-event-hooks) —— 将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/<name>/` |
| **Shell 钩子**（在事件上运行 shell 命令） | [Shell 钩子](/docs/user-guide/features/hooks#shell-hooks) —— 在 `config.yaml` 的 `hooks:` 下声明 |
| **额外的技能源**（自定义 GitHub 仓库、私有技能索引） | [技能](/docs/user-guide/features/skills) —— `hermes skills tap add <repo>` · [发布一个 tap](/docs/user-guide/features/skills#publishing-a-custom-skill-tap) |
| 一个一流的**核心**推理提供商（非插件） | [添加提供商](/docs/developer-guide/adding-providers) |

查看完整的[可插拔接口表](/docs/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)，了解所有扩展接口的汇总视图，包括配置驱动（TTS、STT、MCP、shell 钩子）和即插即用目录（消息网关钩子）风格。
:::

## 您将构建什么

一个**计算器**插件，包含两个工具：
- `calculate` —— 计算数学表达式（`2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` —— 单位转换（`100 F → 37.78 C`、`5 km → 3.11 mi`）

外加一个记录每次工具调用的钩子，以及一个捆绑的技能文件。

## 步骤 1：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 步骤 2：编写清单

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: 数学计算器 —— 计算表达式和转换单位
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段列出了插件注册的内容。

您可以添加的可选字段：
```yaml
author: 您的名字
requires_env:          # 根据环境变量控制加载；安装期间会提示
  - SOME_API_KEY       # 简单格式 —— 如果缺失则插件被禁用
  - name: OTHER_KEY    # 丰富格式 —— 安装期间显示描述/URL
    description: "Other 服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

## 步骤 3：编写工具模式

创建 `schemas.py` —— 这是 LLM 用来决定何时调用您的工具的内容：

```python
"""工具模式 —— LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算数学表达式并返回结果。"
        "支持算术（+, -, *, /, **）、函数（sqrt, sin, cos, "
        "log, abs, round, floor, ceil）和常量（pi, e）。"
        "当用户询问任何数学问题时使用此工具。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式（例如 '2**10', 'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在单位之间转换数值。支持长度（m, km, mi, ft, in）、"
        "重量（kg, lb, oz, g）、温度（C, F, K）、数据（B, KB, MB, GB, TB）、"
        "和时间（s, min, hr, day）。"
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
                "description": "源单位（例如 'km', 'lb', 'F', 'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如 'mi', 'kg', 'C', 'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么模式很重要：** `description` 字段是 LLM 决定何时使用您的工具的依据。请具体说明它的功能和使用时机。`parameters` 定义了 LLM 传递的参数。
## 步骤 4：编写工具处理函数

创建 `tools.py` — 这是当 LLM 调用你的工具时实际执行的代码：

```python
"""工具处理函数 — 当 LLM 调用每个工具时运行的代码。"""

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

    处理函数的规则：
    1. 接收 args (dict) — LLM 传递的参数
    2. 执行工作
    3. 返回一个 JSON 字符串 — 总是如此，即使出错
    4. 接受 **kwargs 以保持向前兼容性
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "未提供表达式"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "除以零错误"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"无效表达式: {e}"})


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
    """在单位之间进行转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "需要 value、from_unit 和 to_unit 参数"})

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
1.  **签名：** `def my_handler(args: dict, **kwargs) -> str`
2.  **返回值：** 始终是一个 JSON 字符串。成功和错误都一样。
3.  **永不抛出异常：** 捕获所有异常，改为返回错误 JSON。
4.  **接受 `**kwargs`：** Hermes 未来可能会传递额外的上下文。

## 步骤 5：编写注册代码

创建 `__init__.py` — 这将模式连接到处理函数：

```python
"""计算器插件 — 注册。"""

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
    logger.debug("工具被调用: %s (会话 %s)", tool_name, task_id)


def register(ctx):
    """将模式连接到处理函数并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 这个钩子对所有工具调用都触发，不仅限于我们的
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时被精确调用一次
- `ctx.register_tool()` 将你的工具放入注册表 — 模型立即就能看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册一个 CLI 子命令（例如 `hermes my-plugin <subcommand>`）
- `ctx.register_command()` 注册一个会话内的斜杠命令（例如在 CLI / 消息网关聊天中的 `/myplugin <args>`）— 参见下面的 [注册斜杠命令](#register-slash-commands)
- `ctx.dispatch_tool(name, arguments)` — 调用任何其他工具（内置的或来自其他插件的），并自动连接父 Agent 的上下文（审批、凭据、task_id）。对于需要调用 `terminal`、`read_file` 或任何其他工具（就像模型直接调用一样）的斜杠命令处理函数很有用。
- 如果此函数崩溃，插件将被禁用，但 Hermes 会继续正常运行

**`dispatch_tool` 示例 — 一个通过调用工具来实现的斜杠命令：**

```python
def handle_scan(ctx, argstr):
    """通过注册表调用终端工具来实现 /scan 命令。"""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{argstr}'"})
    return result  # 返回给调用者的聊天界面

def register(ctx):
    ctx.register_command("scan", handle_scan, help="查找匹配通配符的文件")
```
被调度的工具会经过正常的审批、脱敏和预算流水线——这是一个真实的工具调用，而非绕过它们的捷径。

## 第 6 步：测试

启动 Hermes：

```bash
hermes
```

你应该能在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试以下提示词：
```
2 的 16 次方是多少？
将 100 华氏度转换为摄氏度
2 的平方根乘以 π 是多少？
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

## 你的插件最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "我是 calculator，我提供工具和钩子"
├── __init__.py      # 连接：schemas → handlers，注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规范）
└── tools.py         # 实际运行的代码（calculate, unit_convert 函数）
```

四个文件，职责清晰：
- **清单** 声明插件是什么
- **模式** 为 LLM 描述工具
- **处理器** 实现实际逻辑
- **注册** 连接所有部分

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

### 捆绑技能

插件可以附带技能文件，Agent 通过 `skill_view("plugin:skill")` 加载它们。在你的 `__init__.py` 中注册：

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

现在 Agent 可以使用带命名空间的名称加载你的技能：

```python
skill_view("my-plugin:my-workflow")   # → 插件版本
skill_view("my-workflow")              # → 内置版本（不变）
```

**关键特性：**
- 插件技能是**只读的**——它们不会进入 `~/.hermes/skills/` 目录，也不能通过 `skill_manage` 编辑。
- 插件技能**不会**列在系统提示词的 `<available_skills>` 索引中——它们是显式加载的。
- 不带命名空间的技能名称不受影响——命名空间防止了与内置技能的冲突。
- 当 Agent 加载插件技能时，会预置一个捆绑上下文横幅，列出同一插件中的其他技能。

:::tip 旧模式
旧的 `shutil.copy2` 模式（将技能复制到 `~/.hermes/skills/`）仍然有效，但存在与内置技能名称冲突的风险。对于新插件，建议使用 `ctx.register_skill()`。
:::

### 基于环境变量启用

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件将被禁用并显示明确消息。不会崩溃，Agent 中也不会报错——只是显示“Plugin weather disabled (missing: WEATHER_API_KEY)”。

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

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 在安装提示时显示给用户 |
| `url` | 否 | 获取凭据的地址 |
| `secret` | 否 | 如果为 `true`，输入会被隐藏（类似密码字段） |

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

每个钩子都在 **[事件钩子参考](/docs/user-guide/features/hooks#plugin-hooks)** 中有完整文档——回调签名、参数表、每个钩子触发的确切时机以及示例。以下是摘要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/docs/user-guide/features/hooks#pre_tool_call) | 任何工具执行前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/docs/user-guide/features/hooks#post_tool_call) | 任何工具返回后 | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | 忽略 |
| [`pre_llm_call`](/docs/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/docs/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环之后（仅限成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/docs/user-guide/features/hooks#on_session_start) | 新会话创建时（仅限第一轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/docs/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`on_session_finalize`](/docs/user-guide/features/hooks#on_session_finalize) | CLI/消息网关销毁活动会话时 | `session_id: str \| None, platform: str` | 忽略 |
| [`on_session_reset`](/docs/user-guide/features/hooks#on_session_reset) | 消息网关交换新的会话密钥时（`/new`, `/reset`） | `session_id: str, platform: str` | 忽略 |
大多数钩子都是即发即弃的观察者——它们的返回值会被忽略。唯一的例外是 `pre_llm_call`，它可以向对话中注入上下文。

所有回调函数都应接受 `**kwargs` 参数以保证向前兼容性。如果钩子回调崩溃，它会被记录并跳过。其他钩子和 Agent 会继续正常运行。

### `pre_llm_call` 上下文注入

这是唯一一个返回值有意义的钩子。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或一个纯字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这是记忆插件、RAG 集成、防护栏以及任何需要为模型提供额外上下文的插件所使用的机制。

#### 返回格式

```python
# 包含 context 键的字典
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# 纯字符串（等同于上面的字典形式）
return "Recalled memories:\n- User prefers dark mode"

# 返回 None 或不返回 → 不注入（仅作为观察者）
return None
```

任何非 None、非空且包含 `"context"` 键的返回值（或非空纯字符串）都会被收集并附加到当前轮次的用户消息中。

#### 注入机制

注入的上下文是附加到**用户消息**，而不是系统提示词。这是一个深思熟虑的设计选择：

- **提示词缓存保留** — 系统提示词在各轮次间保持相同。Anthropic 和 OpenRouter 会缓存系统提示词前缀，因此保持其稳定可以在多轮对话中节省 75%+ 的输入 Token。如果插件修改了系统提示词，每一轮都会导致缓存未命中。
- **临时性** — 注入仅在 API 调用时发生。对话历史中的原始用户消息永远不会被修改，并且没有任何内容会持久化到会话数据库中。
- **系统提示词是 Hermes 的领域** — 它包含模型特定的指导、工具执行规则、人格指令以及缓存的技能内容。插件通过贡献上下文到用户输入旁边，而不是通过改变 Agent 的核心指令来发挥作用。

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

#### 示例：防护栏插件

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

**活跃提供商门控：** 记忆插件 CLI 命令仅在其提供商是配置中活跃的 `memory.provider` 时才会出现。如果用户没有设置你的提供商，你的 CLI 命令将不会使帮助输出变得杂乱。

### 注册斜杠命令
插件可以注册会话内斜杠命令——用户在对话过程中输入的命令（如 `/lcm status` 或 `/ping`）。这些命令在 CLI 和消息网关（Telegram、Discord 等）中均可使用。

```python
def _handle_status(raw_args: str) -> str:
    """Handler for /mystatus — called with everything after the command name."""
    if raw_args.strip() == "help":
        return "Usage: /mystatus [help|check]"
    return "Plugin status: all systems nominal"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="Show plugin status",
    )
```

注册后，用户可以在任何会话中输入 `/mystatus`。该命令会出现在自动补全、`/help` 输出以及 Telegram 机器人菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 命令名称，不带前导斜杠（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 调用时传入原始参数字符串。也可以是 `async` 函数。 |
| `description` | `str` | 显示在 `/help`、自动补全和 Telegram 机器人菜单中 |

**与 `register_cli_command()` 的主要区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 在会话中通过 `/name` | 在终端中通过 `hermes name` |
| 工作环境 | CLI 会话、Telegram、Discord 等 | 仅限终端 |
| 处理器接收 | 原始参数字符串 | argparse `Namespace` 对象 |
| 使用场景 | 诊断、状态、快速操作 | 复杂的子命令树、设置向导 |

**冲突保护：** 如果插件尝试注册的名称与内置命令（`help`、`model`、`new` 等）冲突，注册将被静默拒绝并记录警告。内置命令始终优先。

**异步处理器：** 消息网关调度器会自动检测并等待异步处理器，因此你可以使用同步或异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"Check result: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="Run async check")
```

### 从斜杠命令调度工具

需要编排工具（通过 `delegate_task` 生成子 Agent、调用 `file_edit` 等）的斜杠命令处理器，应使用 `ctx.dispatch_tool()`，而不是直接访问框架内部。父 Agent 上下文（工作区提示、加载动画、模型继承）会自动连接。

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="Delegate a goal to a subagent",
    )
```

**签名：** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 在工具注册表中注册的工具名称（例如 `"delegate_task"`、`"file_edit"`） |
| `args` | `dict` | 工具参数，与模型发送的格式相同 |
| `parent_agent` | `Agent \| None` | 可选覆盖项。省略时，从当前 CLI Agent 解析（或在消息网关模式下优雅降级） |

**运行时行为：**

- **CLI 模式：** `parent_agent` 从活动的 CLI Agent 解析，因此工作区提示、加载动画和模型选择会按预期继承。
- **消息网关模式：** 没有 CLI Agent，因此工具会优雅降级——工作区从 `TERMINAL_CWD` 读取，且不显示加载动画。
- **显式覆盖：** 如果调用者显式传递了 `parent_agent=`，则会被尊重且不会被覆盖。

这是从插件命令调度工具的公开、稳定接口。插件不应访问 `ctx._cli_ref.agent` 或类似的私有状态。

:::tip
本指南涵盖**通用插件**（工具、钩子、斜杠命令、CLI 命令）。以下部分概述了每种专用插件类型的编写模式；每个部分都链接到其完整指南，以获取字段参考和示例。
:::

## 专用插件类型

Hermes 除了通用插件外，还有五种专用插件类型。每种都以 `plugins/<category>/<name>/`（捆绑）或 `~/.hermes/plugins/<category>/<name>/`（用户）下的目录形式提供。不同类别的契约不同——选择你需要的类型，然后阅读其完整指南。

### 模型提供商插件 —— 添加 LLM 后端

将配置文件放入 `plugins/model-providers/<name>/`：

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme Inference",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
```

首次有任何代码调用 `get_provider_profile()` 或 `list_providers()` 时延迟发现——`auth.py`、`config.py`、`doctor.py`、`models.py`、`runtime_provider.py` 以及 chat_completions 传输层会自动连接到它。用户插件会按名称覆盖捆绑的插件。

**完整指南：** [模型提供商插件](/docs/developer-guide/model-provider-plugin) —— 字段参考、可覆盖的钩子（`prepare_messages`、`build_extra_body`、`build_api_kwargs_extras`、`fetch_models`）、api_mode 选择、认证类型、测试。

### 平台插件 —— 添加消息网关通道

将适配器放入 `plugins/platforms/<name>/`：

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # 从环境变量自动填充 PlatformConfig.extra，以便仅通过环境变量设置的配置
        # 无需 SDK 实例化即可在 `hermes gateway status` 中显示。
        env_enablement_fn=_env_enablement,
        # 选择加入定时任务投递：`deliver=myplatform` 会路由到此变量。
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="You are chatting via MyPlatform. Keep responses concise.",
    )
```
```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform 消息网关适配器
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "来自 MyPlatform 控制台的 Bot Token"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "定时任务消息的默认频道"
    password: false
```

**完整指南：** [添加平台适配器](/docs/developer-guide/adding-platform-adapters) — 完整的 `BasePlatformAdapter` 契约、消息路由、认证门控、设置向导集成。查看 `plugins/platforms/irc/` 获取一个仅使用标准库的工作示例。

### 记忆提供商插件 — 添加跨会话知识后端

将 `MemoryProvider` 的实现放入 `plugins/memory/<name>/`：

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_message, assistant_response, **kwargs) -> None:
        ...

    def prefetch(self, query: str, **kwargs) -> str | None:
        ...

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

记忆提供商是单选的一—同一时间只有一个处于活动状态，通过 `config.yaml` 中的 `memory.provider` 选择。

**完整指南：** [记忆提供商插件](/docs/developer-guide/memory-provider-plugin) — 完整的 `MemoryProvider` 抽象基类、线程契约、配置文件隔离、通过 `cli.py` 注册 CLI 命令。

### 上下文引擎插件 — 替换上下文压缩器

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def should_compress(self, messages, model) -> bool: ...
    def compress(self, messages, model) -> list[dict]: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

上下文引擎是单选的一—通过 `config.yaml` 中的 `context.engine` 选择。

**完整指南：** [上下文引擎插件](/docs/developer-guide/context-engine-plugin)。

### 图像生成后端

将提供商放入 `plugins/image_gen/<name>/`：

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, **kwargs) -> str: ...   # 返回图片路径

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: 自定义图像生成后端
```

**完整指南：** [图像生成提供商插件](/docs/developer-guide/image-gen-provider-plugin) — 完整的 `ImageGenProvider` 抽象基类、`list_models()` / `get_setup_schema()` 元数据、`success_response()`/`error_response()` 辅助函数、base64 与 URL 输出、用户覆盖、pip 分发。

**参考示例：** `plugins/image_gen/openai/` (通过 OpenAI SDK 的 DALL-E / GPT-Image), `plugins/image_gen/openai-codex/`, `plugins/image_gen/xai/` (Grok 图像生成)。

## 非 Python 扩展接口

Hermes 也接受完全不是 Python 插件的扩展。这些在[可插拔接口表](/docs/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)中展示；以下部分简要概述了每种编写风格。

### MCP 服务器 — 注册外部工具

模型上下文协议 (MCP) 服务器无需任何 Python 插件即可将自己的工具注册到 Hermes。在 `~/.hermes/config.yaml` 中声明它们：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

Hermes 在启动时连接到每个服务器，列出其工具，并将它们与内置工具一起注册。LLM 看到的它们与任何其他工具完全相同。**完整指南：** [MCP](/docs/user-guide/features/mcp)。

### 消息网关事件钩子 — 在生命周期事件上触发

将清单 + 处理器放入 `~/.hermes/hooks/<name>/`：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 当长任务完成时发送推送通知
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # 发送通知 …
        pass
```

事件包括 `gateway:startup`, `session:start`, `session:end`, `session:reset`, `agent:start`, `agent:step`, `agent:end` 以及通配符 `command:*`。钩子中的错误会被捕获并记录 — 它们永远不会阻塞主流水线。

**完整指南：** [消息网关事件钩子](/docs/user-guide/features/hooks#gateway-event-hooks)。

### Shell 钩子 — 在工具调用时运行 shell 命令

如果你只想在工具触发时运行脚本（用于通知、审计日志、桌面提醒、自动格式化），请在 `config.yaml` 中使用 shell 钩子 — 无需 Python：

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send 'Tool ran: {tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

支持与 Python 插件钩子相同的所有事件 (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`, `pre_gateway_dispatch`)，并为 `pre_tool_call` 阻塞决策提供结构化的 JSON 输出。

**完整指南：** [Shell 钩子](/docs/user-guide/features/hooks#shell-hooks)。

### 技能源 — 添加自定义技能注册表

如果你维护一个技能的 GitHub 仓库（或者想从内置源之外的社区索引中拉取），可以将其添加为一个 **tap**：
```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

发布你自己的 tap 只需要一个包含 `skills/<skill-name>/SKILL.md` 目录的 GitHub 仓库——无需服务器或注册中心。

**完整指南：** [技能中心](/docs/user-guide/features/skills#skills-hub) · [发布自定义 tap](/docs/user-guide/features/skills#publishing-a-custom-skill-tap)（仓库结构、最小示例、非默认路径、信任级别）。

### 通过命令模板实现 TTS / STT

任何读写音频或文本的 CLI 都可以通过 `config.yaml` 接入——无需 Python 代码：

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

对于 STT，将 `HERMES_LOCAL_STT_COMMAND` 指向一个 shell 模板。支持的占位符：`{input_path}`、`{output_path}`、`{format}`、`{voice}`、`{model}`、`{speed}`（TTS）；`{input_path}`、`{output_dir}`、`{language}`、`{model}`（STT）。任何与路径交互的 CLI 自动成为一个插件。

**完整指南：** [TTS 自定义命令提供商](/docs/user-guide/features/tts#custom-command-providers) · [STT](/docs/user-guide/features/tts#voice-message-transcription-stt)。

## 通过 pip 分发

要公开分享插件，请在你的 Python 包中添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 插件将在下次 hermes 启动时自动发现
```

## 为 NixOS 分发

如果你提供了包含入口点的 `pyproject.toml`，NixOS 用户可以声明式地安装你的插件：

**入口点插件**（推荐用于分发）：
```nix
# 用户的 configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

**目录插件**（无需 `pyproject.toml`）：
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

有关完整文档（包括覆盖层用法和冲突检查），请参阅 [Nix 设置指南](/docs/getting-started/nix-setup#plugins)。

## 常见错误

**处理器未返回 JSON 字符串：**
```python
# 错误 — 返回字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理器签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递额外上下文会中断
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**处理器抛出异常：**
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
"description": "评估数学表达式。用于算术、三角函数、对数。支持：+, -, *, /, **, sqrt, sin, cos, log, pi, e。"
```