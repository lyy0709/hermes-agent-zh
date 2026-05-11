---
sidebar_position: 11
title: "插件 LLM 访问"
description: "通过 ctx.llm 从插件内部运行任何 LLM 调用——聊天或结构化，同步或异步。宿主管理的认证、故障关闭信任门、可选的 JSON Schema 验证。"
---

# 插件 LLM 访问

`ctx.llm` 是插件进行 LLM 调用的受支持方式。
聊天补全、结构化提取、同步、异步、带或不带
图片——相同的接口，相同的信任门，相同的宿主管理的凭证。

当插件需要执行涉及模型但不属于 Agent 对话的
操作时，会使用此功能。例如，一个将工具错误重写为
非工程师可读内容的钩子。一个在排队前翻译入站消息的
消息网关适配器。一个总结长粘贴内容的斜杠命令。
一个评估昨日活动并向状态板写入一行的定时任务。
一个决定消息是否值得唤醒 Agent 的预过滤器。

这些是 Agent 不应参与循环的工作。它们只需要一次
LLM 调用，一个类型化的答案，然后完成。

## 最简单的调用

```python
result = ctx.llm.complete(messages=[{"role": "user", "content": "ping"}])
return result.text
```

这就是一行代码的完整 API。无需密钥，无需提供商配置，无需
SDK 初始化。插件针对用户当前使用的任何提供商和
模型运行——当用户切换提供商时，插件会自动跟随。

## 一个更完整的聊天示例

```python
result = ctx.llm.complete(
    messages=[
        {"role": "system", "content": "将错误重写为非工程师可以据此行动的一个短句。"},
        {"role": "user",   "content": traceback_text},
    ],
    max_tokens=64,
    purpose="hooks.error-rewrite",
)
return result.text
```

`purpose` 是一个自由格式的审计字符串——它会出现在 `agent.log`
和 `result.audit` 中，以便操作员可以看到哪个插件进行了哪个
调用。对于任何频繁触发的调用，它是可选的但建议使用。

## 结构化输出

当插件需要类型化的答案时，切换到结构化通道：

```python
result = ctx.llm.complete_structured(
    instructions="评估此支持回复的紧急程度 (0–1) 并选择一个类别。",
    input=[{"type": "text", "text": message_body}],
    json_schema=TRIAGE_SCHEMA,
    purpose="support.triage",
    temperature=0.0,
    max_tokens=128,
)

if result.parsed["urgency"] > 0.8:
    await dispatch_to_oncall(result.parsed["category"], message_body)
```

宿主向提供商请求 JSON 输出，在本地进行解析作为
后备方案，如果安装了 `jsonschema` 则根据你的模式进行验证，
并在 `result.parsed` 上返回一个 Python 对象。如果模型
无法生成有效的 JSON，`result.parsed` 为 `None`，
`result.text` 则携带原始响应。

## 此通道为你提供的能力

* **一次调用，四种形态。** `complete()` 用于聊天，
  `complete_structured()` 用于类型化的 JSON，`acomplete()` 和
  `acomplete_structured()` 用于 asyncio。相同的参数，相同的结果
  对象。
* **宿主管理的凭证。** OAuth Token、刷新流程、
  凭证池、每任务辅助覆盖——Hermes 已有的每一个凭证
  概念都适用。插件永远看不到 Token；
  宿主通过 `result.audit` 追溯调用归属。
* **有界性。** 单次同步或异步调用。无流式传输，无工具
  循环，无会话状态需要管理。陈述输入，获取
  结果，返回。
* **故障关闭信任。** 你从未配置过的插件不能
  选择自己的提供商、模型、Agent 或存储的凭证。
  默认姿态是“使用用户正在使用的”。操作员在
  `config.yaml` 中为每个插件选择加入特定的覆盖。

## 快速开始

下面是两个完整的插件——一个聊天，一个结构化。两者都打包在
单个 `register(ctx)` 函数内，并且无需外部配置即可针对
用户当前激活的任何模型运行。

### 聊天补全 — `/tldr`

```python
def register(ctx):
    ctx.register_command(
        name="tldr",
        handler=lambda raw: _tldr(ctx, raw),
        description="用一段话总结提供的文本。",
        args_hint="<text>",
    )


def _tldr(ctx, raw_args: str) -> str:
    text = raw_args.strip()
    if not text:
        return "用法: /tldr <要总结的文本>"
    result = ctx.llm.complete(
        messages=[
            {"role": "system",
             "content": "用一段紧凑的段落总结用户的文本。不要前言。"},
            {"role": "user", "content": text},
        ],
        max_tokens=256,
        temperature=0.3,
        purpose="tldr",
    )
    return result.text
```

`result.text` 是模型的响应；`result.usage` 携带 Token
计数；`result.provider` 和 `result.model` 携带归属信息。

### 结构化提取 — `/paste-to-tasks`

```python
def register(ctx):
    ctx.register_command(
        name="paste-to-tasks",
        handler=lambda raw: _paste_to_tasks(ctx, raw),
        description="将自由格式的会议记录转换为结构化任务。",
        args_hint="<text>",
    )


_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "owner":  {"type": "string"},
                    "action": {"type": "string"},
                    "due":    {"type": "string", "description": "ISO 日期或空"},
                },
                "required": ["action"],
            },
        },
    },
    "required": ["tasks"],
}


def _paste_to_tasks(ctx, raw_args: str) -> str:
    if not raw_args.strip():
        return "用法: /paste-to-tasks <会议记录>"
    result = ctx.llm.complete_structured(
        instructions=(
            "从这些会议记录中提取具体的行动项。"
            "每个可执行的行对应一个任务。如果未指定负责人，则将 'owner' 留空。"
        ),
        input=[{"type": "text", "text": raw_args}],
        json_schema=_TASKS_SCHEMA,
        schema_name="meeting.tasks",
        purpose="paste-to-tasks",
        temperature=0.0,
        max_tokens=512,
    )
    if result.parsed is None:
        return f"无法解析响应。原始输出:\n{result.text}"
    lines = [f"- [{t.get('owner') or '?'}] {t['action']}" for t in result.parsed["tasks"]]
    return "\n".join(lines) or "(未找到任务)"
```
第三个工作示例，这次包含图像输入，位于
[`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example)
仓库（参考插件的配套仓库——不随 hermes-agent 本身捆绑）。关于异步接口（`acomplete()` / `acomplete_structured()` 与 `asyncio.gather()`），请参见同一仓库中的
[`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example)。

## 何时使用哪个

| 你想要… | 使用 |
|---|---|
| 自由格式的文本响应（翻译、摘要、重写、生成） | `complete()` |
| 多轮提示词（系统提示 + 少量示例 + 用户输入） | `complete()` |
| 返回类型化字典，并根据模式验证 | `complete_structured()` |
| 图像或文本输入，并返回类型化字典 | `complete_structured()` |
| 在异步代码中进行相同调用（消息网关适配器、异步钩子） | `acomplete()` / `acomplete_structured()` |

其他所有方面——提供商选择、模型解析、认证、回退、超时、视觉路由——在所有四个方法中都是相同的。

## API 接口

`ctx.llm` 是 `agent.plugin_llm.PluginLlm` 的一个实例。

### `complete()`

```python
result = ctx.llm.complete(
    messages=[{"role": "user", "content": "Hi"}],
    provider=None,         # 可选，受控 — Hermes 提供商 ID（例如 "openrouter"）
    model=None,            # 可选，受控 — 该提供商期望的任何字符串
    temperature=None,
    max_tokens=None,
    timeout=None,          # 秒
    agent_id=None,         # 可选，受控
    profile=None,          # 可选，受控 — 显式的认证配置文件名称
    purpose="optional-audit-string",
)
# → PluginLlmCompleteResult(text, provider, model, agent_id, usage, audit)
```

普通的聊天补全。`messages` 是标准的 OpenAI 格式——一个 `{"role": "...", "content": "..."}` 字典列表。多轮提示词（系统提示 + 少量用户/助手示例对 + 最终用户输入）的工作方式与 OpenAI SDK 完全相同。

`provider=` 和 `model=` 是独立的，并且遵循与主机主配置（`model.provider` + `model.model`）相同的格式。仅设置 `model=` 可以在用户当前活跃的提供商上使用不同的模型。同时设置两者可以完全切换提供商。任何未经操作员选择启用的参数都会引发 `PluginLlmTrustError`。

### `complete_structured()`

```python
result = ctx.llm.complete_structured(
    instructions="What you want extracted.",
    input=[
        {"type": "text",  "text": "..."},
        {"type": "image", "data": b"...", "mime_type": "image/png"},
        {"type": "image", "url":  "https://..."},
    ],
    json_schema={...},     # 可选 — 触发解析结果 + 验证
    json_mode=False,       # 在没有模式的情况下设置为 True 以请求 JSON 输出
    schema_name=None,      # 可选的人类可读模式名称
    system_prompt=None,
    provider=None,         # 可选，受控
    model=None,            # 可选，受控
    temperature=None,
    max_tokens=None,
    timeout=None,
    agent_id=None,
    profile=None,
    purpose=None,
)
# → PluginLlmStructuredResult(text, provider, model, agent_id,
#                             usage, parsed, content_type, audit)
```

输入是类型化的文本或图像块（原始字节会自动进行 base64 编码为 `data:` URL）。当提供了 `json_schema` 或 `json_mode=True` 时，主机会通过 `response_format` 请求 JSON 输出，在本地解析作为回退，并在安装了 `jsonschema` 的情况下根据你的模式进行验证。

* `result.content_type == "json"` — `result.parsed` 是一个符合你模式的 Python 对象。
* `result.content_type == "text"` — 解析或验证失败；检查 `result.text` 以获取原始模型响应。

### 异步

```python
result = await ctx.llm.acomplete(messages=...)
result = await ctx.llm.acomplete_structured(instructions=..., input=...)
```

参数和结果类型与其同步对应项相同。在消息网关适配器、异步钩子或任何已经在 asyncio 循环上运行的插件代码中使用这些方法。

### 结果属性

```python
@dataclass
class PluginLlmCompleteResult:
    text: str                    # 助手的响应
    provider: str                # 例如 "openrouter", "anthropic"
    model: str                   # 提供商为此调用返回的任何字符串
    agent_id: str                # 使用了谁的模型/认证
    usage: PluginLlmUsage        # Token + 缓存 + 成本估算
    audit: Dict[str, Any]        # plugin_id, purpose, profile

@dataclass
class PluginLlmStructuredResult(PluginLlmCompleteResult):
    parsed: Optional[Any]        # 当 content_type == "json" 时的 JSON 对象
    content_type: str            # "json" 或 "text"
    # 当提供 schema_name 时，audit 也会携带它
```

`usage` 携带 `input_tokens`、`output_tokens`、`total_tokens`、`cache_read_tokens`、`cache_write_tokens` 和 `cost_usd`（当提供商返回这些字段时）。

## 信任门控

默认行为是失败关闭。在没有 `plugins.entries` 配置块的情况下，插件可以：

* 针对用户当前活跃的提供商和模型运行四种方法中的任何一种，
* 设置请求整形参数（`temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`），

…仅此而已。`provider=`、`model=`、`agent_id=` 和 `profile=` 参数会引发 `PluginLlmTrustError`，直到操作员选择启用。

**大多数插件永远不需要此部分。** 一个只调用 `ctx.llm.complete(messages=...)` 且没有覆盖的插件，会针对用户当前活跃的任何配置运行，并且无需配置即可工作。下面的配置块仅当插件特别希望固定使用与用户不同的模型或提供商时才相关。

```yaml
plugins:
  entries:
    my-plugin:
      llm:
        # 允许此插件选择不同的 Hermes 提供商
        # （必须是 Hermes 已经知道的提供商——与 `hermes model` 和 config.yaml model.provider 中的名称相同）。
        allow_provider_override: true

        # 可选地限制允许哪些提供商。使用 ["*"] 表示任何提供商。
        allowed_providers:
          - openrouter
          - anthropic

        # 允许此插件请求特定的模型。
        allow_model_override: true

        # 可选地限制允许哪些模型。使用 ["*"] 表示任何模型。
        # 模型与插件发送的任何字符串进行字面匹配——Hermes 不会进行任何查找。
        allowed_models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-5-haiku

        # 允许跨 Agent 调用（罕见）。
        allow_agent_id_override: false

        # 允许插件请求特定的存储认证配置文件
        # （例如，同一提供商上的不同 OAuth 账户）。
        allow_profile_override: false
```
插件 ID 是扁平插件的清单 `name:` 字段，或者是嵌套插件的路径派生键（例如 `image_gen/openai`、`memory/honcho` 等）。

### 权限控制门强制执行的内容

| 覆盖项        | 默认值 | 配置键                          |
| --------------- | ------- | -------------------------------- |
| `provider=`     | 拒绝    | `allow_provider_override: true`  |
| ↳ 允许列表     | —       | `allowed_providers: [...]`       |
| `model=`        | 拒绝    | `allow_model_override: true`     |
| ↳ 允许列表     | —       | `allowed_models: [...]`          |
| `agent_id=`     | 拒绝    | `allow_agent_id_override: true`  |
| `profile=`      | 拒绝    | `allow_profile_override: true`   |

每个覆盖项都是独立控制的。授予 `allow_model_override` **不会**同时授予 `allow_provider_override` —— 一个被信任可以选取模型的插件，除非也获得了 provider 权限，否则仍然会被限制使用用户当前激活的提供商。

### 权限控制门无需强制执行的内容

*   请求塑造参数 —— `temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`、`schema_name`、`json_mode` —— 始终是允许的；它们不涉及选择凭据或路由。
*   默认拒绝的立场意味着未配置的插件仍然可以完成有用的工作 —— 它只是针对当前激活的提供商和模型运行。操作员只需要为那些希望进行更精细路由的插件考虑 `plugins.entries`。

## 由宿主负责的内容

以下是 `ctx.llm` 为插件处理的所有事项的完整列表，你无需操心：

*   **提供商解析。** 从用户配置（或受信任时的显式覆盖）中读取 `model.provider` + `model.model`。
*   **认证。** 从 `~/.hermes/auth.json` / 环境变量中提取 API 密钥、OAuth Token 或刷新 Token，包括配置了凭据池的情况。插件永远看不到它们。
*   **视觉模型路由。** 当提供图像输入且用户当前的文本模型仅支持文本时，宿主会自动回退到配置的视觉模型。
*   **回退链。** 如果用户的主要提供商返回 5xx 或 429 错误，请求会在向插件返回错误之前，经过 Hermes 通常的、支持聚合器的回退机制。
*   **超时。** 遵守你的 `timeout=` 参数，回退到 `auxiliary.<task>.timeout` 配置或全局辅助默认值。
*   **JSON 塑造。** 当你请求 JSON 时，向提供商发送 `response_format`，如果提供商返回了代码块形式的响应，则在本地重新解析。
*   **模式验证。** 当安装了 `jsonschema` 时，根据你的 `json_schema` 进行验证；否则记录调试信息并跳过严格验证。
*   **审计日志。** 每次调用都会向 `agent.log` 写入一行 INFO 级别的日志，包含插件 ID、提供商/模型、目的和 Token 总数。

## 由插件负责的内容

*   **请求结构。** 聊天的 `messages`，结构化的 `instructions` + `input`。插件构建提示词；宿主运行它。
*   **模式。** 你希望返回的任何结构。宿主不会为你推断。
*   **错误处理。** `complete_structured()` 在输入为空和模式验证失败时引发 `ValueError`。当信任门拒绝覆盖时，会触发 `PluginLlmTrustError`。其他任何情况（提供商 5xx 错误、未配置凭据、超时）都会引发 `auxiliary_client.call_llm()` 所引发的任何异常。
*   **成本。** 每次调用都针对用户付费的提供商运行。不要不加思索地为每条网关消息循环调用 `complete()`，而不考虑 Token 开销。

## 这在插件接口中的定位

现有的 `ctx.*` 方法扩展了现有的 Hermes 子系统：

| `ctx.register_tool` | 添加 Agent 可以调用的工具 |
| `ctx.register_platform` | 连接新的消息网关适配器 |
| `ctx.register_image_gen_provider` | 替换图像生成后端 |
| `ctx.register_memory_provider` | 替换记忆后端 |
| `ctx.register_context_engine` | 替换上下文压缩器 |
| `ctx.register_hook` | 观察生命周期事件 |

`ctx.llm` 是第一个允许插件**带外**运行用户正在与之对话的同一模型的接口，无需依赖上述任何功能。这是它唯一的工作。如果你的插件需要注册一个供 Agent 调用的工具，请使用 `register_tool`。如果它需要对生命周期事件做出反应，请使用 `register_hook`。如果它需要出于任何原因（无论是否结构化）进行自己的模型调用 —— 请使用 `ctx.llm`。

## 参考

*   实现：[`agent/plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/plugin_llm.py)
*   测试：[`tests/agent/test_plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_plugin_llm.py)
*   参考插件（配套仓库）：
    *   [`plugin-llm-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) —— 带图像输入的同步结构化提取
    *   [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example) —— 使用 `asyncio.gather()` 的异步示例
*   辅助客户端（底层引擎）：请参阅 [Provider Runtime](/docs/developer-guide/provider-runtime)。