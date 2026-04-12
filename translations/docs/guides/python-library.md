---
sidebar_position: 5
title: "将 Hermes 用作 Python 库"
description: "将 AIAgent 嵌入到您自己的 Python 脚本、Web 应用或自动化流水线中——无需 CLI"
---

# 将 Hermes 用作 Python 库

Hermes 不仅仅是一个 CLI 工具。您可以直接导入 `AIAgent`，并在您自己的 Python 脚本、Web 应用程序或自动化流水线中以编程方式使用它。本指南将向您展示具体方法。

---

## 安装

直接从代码仓库安装 Hermes：

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git
```

或者使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv pip install git+https://github.com/NousResearch/hermes-agent.git
```

您也可以将其固定在您的 `requirements.txt` 中：

```text
hermes-agent @ git+https://github.com/NousResearch/hermes-agent.git
```

:::tip
将 Hermes 用作库时，需要与 CLI 相同的环境变量。至少需要设置 `OPENROUTER_API_KEY`（如果使用直接提供商访问，则设置 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`）。
:::

---

## 基本用法

使用 Hermes 最简单的方法是 `chat()` 方法——传入一条消息，返回一个字符串：

```python
from run_agent import AIAgent

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)
response = agent.chat("What is the capital of France?")
print(response)
```

`chat()` 在内部处理完整的对话循环——工具调用、重试等所有操作——并仅返回最终的文本响应。

:::warning
将 Hermes 嵌入到您自己的代码中时，请始终设置 `quiet_mode=True`。如果不设置，Agent 会打印 CLI 加载动画、进度指示器和其他终端输出，这会干扰您应用程序的输出。
:::

---

## 完整的对话控制

要对对话进行更多控制，请直接使用 `run_conversation()`。它返回一个包含完整响应、消息历史和元数据的字典：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)

result = agent.run_conversation(
    user_message="Search for recent Python 3.13 features",
    task_id="my-task-1",
)

print(result["final_response"])
print(f"Messages exchanged: {len(result['messages'])}")
```

返回的字典包含：
- **`final_response`** — Agent 的最终文本回复
- **`messages`** — 完整的消息历史记录（系统、用户、助手、工具调用）
- **`task_id`** — 用于 VM 隔离的任务标识符

您还可以传递一个自定义系统消息，以覆盖该次调用的临时系统提示词：

```python
result = agent.run_conversation(
    user_message="Explain quicksort",
    system_message="You are a computer science tutor. Use simple analogies.",
)
```

---

## 配置工具

使用 `enabled_toolsets` 或 `disabled_toolsets` 控制 Agent 可以访问哪些工具集：

```python
# 仅启用 Web 工具（浏览、搜索）
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    enabled_toolsets=["web"],
    quiet_mode=True,
)

# 启用除终端访问外的所有功能
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    disabled_toolsets=["terminal"],
    quiet_mode=True,
)
```

:::tip
当您想要一个最小化、受限制的 Agent 时（例如，研究机器人仅使用网络搜索），请使用 `enabled_toolsets`。当您需要大部分功能但需要限制特定功能时（例如，在共享环境中禁止终端访问），请使用 `disabled_toolsets`。
:::

---

## 多轮对话

通过将消息历史记录传回，在多个轮次中维护对话状态：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)

# 第一轮
result1 = agent.run_conversation("My name is Alice")
history = result1["messages"]

# 第二轮 — Agent 记得上下文
result2 = agent.run_conversation(
    "What's my name?",
    conversation_history=history,
)
print(result2["final_response"])  # "Your name is Alice."
```

`conversation_history` 参数接受先前结果中的 `messages` 列表。Agent 会在内部复制它，因此您的原始列表永远不会被修改。

---

## 保存轨迹

启用轨迹保存功能，以 ShareGPT 格式捕获对话——这对于生成训练数据或调试非常有用：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    save_trajectories=True,
    quiet_mode=True,
)

agent.chat("Write a Python function to sort a list")
# 以 ShareGPT 格式保存到 trajectory_samples.jsonl
```

每个对话都作为单行 JSONL 追加，便于从自动化运行中收集数据集。

---

## 自定义系统提示词

使用 `ephemeral_system_prompt` 设置自定义系统提示词，以指导 Agent 的行为，但**不会**保存到轨迹文件中（保持训练数据干净）：

```python
agent = AIgent(
    model="anthropic/claude-sonnet-4",
    ephemeral_system_prompt="You are a SQL expert. Only answer database questions.",
    quiet_mode=True,
)

response = agent.chat("How do I write a JOIN query?")
print(response)
```

这对于构建专门的 Agent 非常理想——代码审查员、文档编写员、SQL 助手——所有这些都使用相同的基础工具。

---

## 批量处理

为了并行运行许多提示词，Hermes 包含了 `batch_runner.py`。它管理并发的 `AIAgent` 实例，并提供适当的资源隔离：

```bash
python batch_runner.py --input prompts.jsonl --output results.jsonl
```

每个提示词都有自己的 `task_id` 和隔离的执行环境。如果您需要自定义批量逻辑，可以直接使用 `AIAgent` 构建自己的逻辑：

```python
import concurrent.futures
from run_agent import AIAgent

prompts = [
    "Explain recursion",
    "What is a hash table?",
    "How does garbage collection work?",
]

def process_prompt(prompt):
    # 为每个任务创建一个新的 Agent 以确保线程安全
    agent = AIAgent(
        model="anthropic/claude-sonnet-4",
        quiet_mode=True,
        skip_memory=True,
    )
    return agent.chat(prompt)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))

for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}\nA: {result}\n")
```

:::warning
始终为每个线程或任务创建**一个新的 `AIAgent` 实例**。Agent 维护的内部状态（对话历史、工具会话、迭代计数器）不是线程安全的，不能共享。
:::

---

## 集成示例

### FastAPI 端点

```python
from fastapi import FastAPI
from pydantic import BaseModel
from run_agent import AIAgent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "anthropic/claude-sonnet-4"

@app.post("/chat")
async def chat(request: ChatRequest):
    agent = AIAgent(
        model=request.model,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )
    response = agent.chat(request.message)
    return {"response": response}
```

### Discord 机器人

```python
import discord
from run_agent import AIAgent

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hermes "):
        query = message.content[8:]
        agent = AIAgent(
            model="anthropic/claude-sonnet-4",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            platform="discord",
        )
        response = agent.chat(query)
        await message.channel.send(response[:2000])

client.run("YOUR_DISCORD_TOKEN")
```

### CI/CD 流水线步骤

```python
#!/usr/bin/env python3
"""CI step: auto-review a PR diff."""
import subprocess
from run_agent import AIAgent

diff = subprocess.check_output(["git", "diff", "main...HEAD"]).decode()

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
    skip_context_files=True,
    skip_memory=True,
    disabled_toolsets=["terminal", "browser"],
)

review = agent.chat(
    f"Review this PR diff for bugs, security issues, and style problems:\n\n{diff}"
)
print(review)
```

---

## 关键构造函数参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `model` | `str` | `"anthropic/claude-opus-4.6"` | OpenRouter 格式的模型 |
| `quiet_mode` | `bool` | `False` | 抑制 CLI 输出 |
| `enabled_toolsets` | `List[str]` | `None` | 白名单特定工具集 |
| `disabled_toolsets` | `List[str]` | `None` | 黑名单特定工具集 |
| `save_trajectories` | `bool` | `False` | 将对话保存到 JSONL |
| `ephemeral_system_prompt` | `str` | `None` | 自定义系统提示词（不保存到轨迹） |
| `max_iterations` | `int` | `90` | 每次对话的最大工具调用迭代次数 |
| `skip_context_files` | `bool` | `False` | 跳过加载 AGENTS.md 文件 |
| `skip_memory` | `bool` | `False` | 禁用持久化记忆读写 |
| `api_key` | `str` | `None` | API 密钥（回退到环境变量） |
| `base_url` | `str` | `None` | 自定义 API 端点 URL |
| `platform` | `str` | `None` | 平台提示（`"discord"`、`"telegram"` 等） |

---

## 重要说明

:::tip
- 如果您不希望从工作目录加载 `AGENTS.md` 文件到系统提示词中，请设置 **`skip_context_files=True`**。
- 设置 **`skip_memory=True`** 以防止 Agent 读取或写入持久化记忆——推荐用于无状态的 API 端点。
- `platform` 参数（例如 `"discord"`、`"telegram"`）会注入特定于平台的格式化提示，以便 Agent 调整其输出样式。
:::

:::warning
- **线程安全**：为每个线程或任务创建一个 `AIAgent`。切勿在并发调用之间共享实例。
- **资源清理**：当对话结束时，Agent 会自动清理资源（终端会话、浏览器实例）。如果您在长时间运行的进程中运行，请确保每次对话正常完成。
- **迭代限制**：默认的 `max_iterations=90` 很宽松。对于简单的问答用例，请考虑降低它（例如 `max_iterations=10`），以防止失控的工具调用循环并控制成本。
:::