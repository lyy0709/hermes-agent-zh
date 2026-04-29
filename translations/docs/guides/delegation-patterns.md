---
sidebar_position: 13
title: "委派与并行工作"
description: "何时以及如何使用子Agent委派——并行研究、代码审查和多文件工作的模式"
---

# 委派与并行工作

Hermes 可以生成隔离的子Agent来并行处理任务。每个子Agent都有自己的对话、终端会话和工具集。只有最终摘要会返回——中间的工具调用永远不会进入你的上下文窗口。

完整功能参考，请参见[子Agent委派](/docs/user-guide/features/delegation)。

---

## 何时进行委派

**适合委派的任务：**
- 推理密集的子任务（调试、代码审查、研究综合）
- 会因中间数据而淹没你上下文的任务
- 并行的独立工作流（同时进行研究A和B）
- 需要Agent不带偏见地处理的新上下文任务

**使用其他方法：**
- 单一工具调用 → 直接使用工具
- 步骤间有逻辑的机械性多步骤工作 → `execute_code`
- 需要用户交互的任务 → 子Agent无法使用 `clarify`
- 快速文件编辑 → 直接进行
- 必须比当前轮次更持久的长期运行工作 → 使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。`delegate_task` 是**同步的**：如果父轮次被中断，活动的子任务将被取消，其工作将被丢弃。

---

## 模式：并行研究

同时研究三个主题并获取结构化摘要：

```
并行研究以下三个主题：
1. WebAssembly 在浏览器外的当前状态
2. 2025年RISC-V服务器芯片的采用情况
3. 实用的量子计算应用

重点关注近期发展和关键参与者。
```

在幕后，Hermes 使用：

```python
delegate_task(tasks=[
    {
        "goal": "研究2025年浏览器外的WebAssembly",
        "context": "重点关注：运行时（Wasmtime, Wasmer）、云/边缘用例、WASI进展",
        "toolsets": ["web"]
    },
    {
        "goal": "研究RISC-V服务器芯片的采用情况",
        "context": "重点关注：已发货的服务器芯片、云提供商采用情况、软件生态系统",
        "toolsets": ["web"]
    },
    {
        "goal": "研究实用的量子计算应用",
        "context": "重点关注：纠错突破、实际用例、关键公司",
        "toolsets": ["web"]
    }
])
```

三者同时运行。每个子Agent独立搜索网络并返回摘要。然后父Agent将它们综合成一份连贯的简报。

---

## 模式：代码审查

将安全审查委派给一个具有新上下文的子Agent，使其不带先入之见地审查代码：

```
审查 src/auth/ 处的身份验证模块是否存在安全问题。
检查SQL注入、JWT验证问题、密码处理和会话管理。
修复发现的任何问题并运行测试。
```

关键是 `context` 字段——它必须包含子Agent所需的一切：

```python
delegate_task(
    goal="审查 src/auth/ 的安全问题并修复发现的任何问题",
    context="""项目位于 /home/user/webapp。Python 3.11, Flask, PyJWT, bcrypt。
    身份验证文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py
    测试命令：pytest tests/auth/ -v
    重点关注：SQL注入、JWT验证、密码哈希、会话管理。
    修复发现的问题并验证测试通过。""",
    toolsets=["terminal", "file"]
)
```

:::warning 上下文问题
子Agent对你的对话**一无所知**。它们完全从零开始。如果你委派“修复我们正在讨论的bug”，子Agent根本不知道你指的是哪个bug。务必明确传递文件路径、错误消息、项目结构和约束条件。
:::

---

## 模式：比较备选方案

并行评估同一问题的多种方法，然后选择最佳方案：

```
我需要为我们的Django应用添加全文搜索。并行评估三种方法：
1. PostgreSQL tsvector（内置）
2. 通过 django-elasticsearch-dsl 使用 Elasticsearch
3. 通过 meilisearch-python 使用 Meilisearch

针对每种方法：设置复杂性、查询能力、资源需求和维护开销。比较它们并推荐一种。
```

每个子Agent独立研究一个选项。由于它们是隔离的，不存在交叉污染——每个评估都基于其自身优点。父Agent获得所有三个摘要并进行比较。

---

## 模式：多文件重构

将大型重构任务拆分给并行的子Agent，每个子Agent处理代码库的不同部分：

```python
delegate_task(tasks=[
    {
        "goal": "重构所有API端点处理程序以使用新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文件：src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        旧格式：return {"data": result, "status": "ok"}
        新格式：return APIResponse(data=result, status=200).to_dict()
        导入：from src.responses import APIResponse
        之后运行测试：pytest tests/handlers/ -v""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新所有客户端SDK方法以处理新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文件：sdk/python/client.py, sdk/python/models.py
        旧解析：result = response.json()["data"]
        新解析：result = response.json()["data"]（键相同，但添加状态码检查）
        同时更新 sdk/python/tests/test_client.py""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新API文档以反映新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文档位于：docs/api/。格式：带有代码示例的Markdown。
        将所有响应示例从旧格式更新为新格式。
        在 docs/api/overview.md 中添加一个'响应格式'部分来解释模式。""",
        toolsets=["terminal", "file"]
    }
])
```

:::tip
每个子Agent都有自己的终端会话。只要它们编辑的是不同的文件，它们就可以在同一个项目目录中工作而不会相互干扰。如果两个子Agent可能接触同一个文件，请在并行工作完成后自己处理该文件。
:::

---

## 模式：收集然后分析

使用 `execute_code` 进行机械的数据收集，然后将推理密集的分析任务委派出去：

```python
# 步骤1：机械收集（此处使用 execute_code 更好——无需推理）
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# 从最相关的5个结果中提取完整内容
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# 保存以供分析步骤使用
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"收集了 {len(results)} 个结果，提取了 {len(content['results'])} 个页面")
""")

# 步骤2：推理密集的分析（此处委派更好）
delegate_task(
    goal="分析AI融资数据并撰写市场报告",
    context="""原始数据位于 /tmp/ai-funding-data.json，包含关于2026年第一季度AI融资、收购和IPO的搜索结果和提取的网页。
    撰写一份结构化的市场报告：关键交易、趋势、重要参与者和展望。重点关注超过1亿美元的交易。""",
    toolsets=["terminal", "file"]
)
```

这通常是最有效的模式：`execute_code` 以低成本处理10多个顺序工具调用，然后一个子Agent在干净的上下文中执行单个昂贵的推理任务。

---

## 工具集选择

根据子Agent的需求选择工具集：

| 任务类型 | 工具集 | 原因 |
|-----------|----------|-----|
| 网络研究 | `["web"]` | 仅 web_search + web_extract |
| 代码工作 | `["terminal", "file"]` | Shell访问 + 文件操作 |
| 全栈工作 | `["terminal", "file", "web"]` | 除消息传递外的一切 |
| 只读分析 | `["file"]` | 只能读取文件，无shell |

限制工具集可以保持子Agent专注，并防止意外的副作用（例如研究子Agent运行shell命令）。

---

## 约束

- **默认3个并行任务**：批处理默认使用3个并发子Agent（可通过 config.yaml 中的 `delegation.max_concurrent_children` 配置，无硬性上限，只有下限为1）
- **嵌套委派需手动启用**：叶子子Agent（默认）不能调用 `delegate_task`、`clarify`、`memory`、`send_message` 或 `execute_code`。编排器子Agent（`role="orchestrator"`）保留 `delegate_task` 以进行进一步委派，但仅在 `delegation.max_spawn_depth` 提高到默认值1以上时（支持1-3）；其他四个仍然被阻止。通过 `delegation.orchestrator_enabled: false` 全局禁用。

### 调整并发性和深度

| 配置 | 默认值 | 范围 | 效果 |
|--------|---------|-------|--------|
| `max_concurrent_children` | 3 | >=1 | 每次 `delegate_task` 调用的并行批处理大小 |
| `max_spawn_depth` | 1 | 1-3 | 可以生成多少层委派级别 |

示例：运行30个并行工作器并带有嵌套子Agent：

```yaml
delegation:
  max_concurrent_children: 30
  max_spawn_depth: 2
```

- **独立的终端** —— 每个子Agent都有自己的终端会话，具有独立的工作目录和状态
- **无对话历史** —— 子Agent只能看到父Agent调用 `delegate_task` 时传递的 `goal` 和 `context`
- **默认50次迭代** —— 对于简单任务，设置较低的 `max_iterations` 以节省成本
- **非持久性** —— `delegate_task` 是同步的，并在父轮次内运行。如果父轮次被中断（新用户消息、`/stop`、`/new`），所有活动的子任务将被取消（`status="interrupted"`），其工作将被丢弃。对于必须比当前轮次更持久的工作，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

---

## 技巧

**目标要具体。** “修复bug”太模糊。“修复 api/handlers.py 第47行中 process_request() 从 parse_body() 接收到 None 的 TypeError”为子Agent提供了足够的工作信息。

**包含文件路径。** 子Agent不知道你的项目结构。始终包含相关文件、项目根目录和测试命令的绝对路径。

**利用委派实现上下文隔离。** 有时你需要一个新的视角。委派迫使你清晰地阐述问题，而子Agent会在没有对话中积累的假设的情况下处理它。

**检查结果。** 子Agent摘要仅仅是摘要。如果子Agent说“修复了bug并且测试通过”，请通过自己运行测试或阅读差异来验证。

---

*完整的委派参考——所有参数、ACP集成和高级配置——请参见[子Agent委派](/docs/user-guide/features/delegation)。*