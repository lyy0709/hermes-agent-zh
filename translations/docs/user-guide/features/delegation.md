---
sidebar_position: 7
title: "子 Agent 委派"
description: "使用 delegate_task 工具生成具有独立上下文、受限工具集和独立终端会话的子 AIAgent 实例，实现并行工作流"
---

# 子 Agent 委派

`delegate_task` 工具会生成子 AIAgent 实例，这些实例拥有独立的上下文、受限的工具集以及它们自己的终端会话。每个子 Agent 都会开启一个全新的对话并独立工作——只有其最终摘要会进入父 Agent 的上下文。

## 单一任务

```python
delegate_task(
    goal="调试测试失败的原因",
    context="错误：test_foo.py 第 42 行断言失败",
    toolsets=["terminal", "file"]
)
```

## 并行批量任务

最多可同时运行 3 个子 Agent：

```python
delegate_task(tasks=[
    {"goal": "研究主题 A", "toolsets": ["web"]},
    {"goal": "研究主题 B", "toolsets": ["web"]},
    {"goal": "修复构建", "toolsets": ["terminal", "file"]}
])
```

## 子 Agent 上下文工作原理

:::warning 关键：子 Agent 一无所知
子 Agent 从一个**完全全新的对话**开始。它们对父 Agent 的对话历史、之前的工具调用或委派前讨论的任何内容都一无所知。子 Agent 的唯一上下文来自您提供的 `goal` 和 `context` 字段。
:::

这意味着您必须传递子 Agent 所需的**所有**信息：

```python
# 错误 - 子 Agent 不知道“错误”是什么
delegate_task(goal="修复错误")

# 正确 - 子 Agent 拥有所需的所有上下文
delegate_task(
    goal="修复 api/handlers.py 中的 TypeError",
    context="""文件 api/handlers.py 第 47 行有一个 TypeError：
    'NoneType' 对象没有属性 'get'。
    函数 process_request() 从 parse_body() 接收一个字典，
    但当 Content-Type 缺失时，parse_body() 返回 None。
    项目位于 /home/user/myproject，使用 Python 3.11。"""
)
```

子 Agent 会收到一个根据您的目标和上下文构建的、聚焦的系统提示词，指示其完成任务并提供结构化摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

## 实际示例

### 并行研究

同时研究多个主题并收集摘要：

```python
delegate_task(tasks=[
    {
        "goal": "研究 2025 年 WebAssembly 的现状",
        "context": "重点关注：浏览器支持、非浏览器运行时、语言支持",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 2025 年 RISC-V 的采用现状",
        "context": "重点关注：服务器芯片、嵌入式系统、软件生态系统",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 2025 年量子计算的进展",
        "context": "重点关注：纠错突破、实际应用、关键参与者",
        "toolsets": ["web"]
    }
])
```

### 代码审查 + 修复

将审查和修复工作流委派给一个全新的上下文：

```python
delegate_task(
    goal="审查身份验证模块的安全问题并修复发现的问题",
    context="""项目位于 /home/user/webapp。
    身份验证模块文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py。
    项目使用 Flask、PyJWT 和 bcrypt。
    重点关注：SQL 注入、JWT 验证、密码处理、会话管理。
    修复发现的任何问题并运行测试套件 (pytest tests/auth/)。""",
    toolsets=["terminal", "file"]
)
```

### 多文件重构

委派一个大型重构任务，该任务会淹没父 Agent 的上下文：

```python
delegate_task(
    goal="重构 src/ 中的所有 Python 文件，将 print() 替换为适当的日志记录",
    context="""项目位于 /home/user/myproject。
    使用 'logging' 模块，设置 logger = logging.getLogger(__name__)。
    将 print() 调用替换为适当的日志级别：
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - 其他打印 -> logger.info(...)
    不要更改测试文件或 CLI 输出中的 print()。
    之后运行 pytest 以验证没有破坏任何功能。""",
    toolsets=["terminal", "file"]
)
```

## 批量模式详情

当您提供 `tasks` 数组时，子 Agent 使用线程池**并行**运行：

- **最大并发数：** 3 个任务（如果 `tasks` 数组更长，则截断为 3）
- **线程池：** 使用带有 `MAX_CONCURRENT_CHILDREN = 3` 个工作线程的 `ThreadPoolExecutor`
- **进度显示：** 在 CLI 模式下，树状视图实时显示每个子 Agent 的工具调用，并带有每项任务的完成行。在消息网关模式下，进度会分批处理并中继到父 Agent 的进度回调函数
- **结果排序：** 结果按任务索引排序，以匹配输入顺序，无论完成顺序如何
- **中断传播：** 中断父 Agent（例如，发送新消息）会中断所有活动的子 Agent

单任务委派直接运行，没有线程池开销。

## 模型覆盖

您可以通过 `config.yaml` 为子 Agent 配置不同的模型——这对于将简单任务委派给更便宜/更快的模型很有用：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 用于子 Agent 的更便宜模型
  provider: "openrouter"              # 可选：将子 Agent 路由到不同的提供商
```

如果省略，子 Agent 使用与父 Agent 相同的模型。

## 工具集选择技巧

`toolsets` 参数控制子 Agent 可以访问哪些工具。根据任务选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、文档查找 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、无需执行的代码审查 |
| `["terminal"]` | 系统管理、进程管理 |

某些工具集**始终被阻止**用于子 Agent，无论您指定什么：
- `delegation` — 禁止递归委派（防止无限生成）
- `clarify` — 子 Agent 无法与用户交互
- `memory` — 无法写入共享持久记忆
- `code_execution` — 子 Agent 应逐步推理
- `send_message` — 无跨平台副作用（例如，发送 Telegram 消息）

## 最大迭代次数

每个子 Agent 都有一个迭代限制（默认值：50），用于控制它可以进行多少次工具调用轮次：

```python
delegate_task(
    goal="快速文件检查",
    context="检查 /etc/nginx/nginx.conf 是否存在并打印其前 10 行",
    max_iterations=10  # 简单任务，不需要很多轮次
)
```

## 深度限制

委派有**深度限制为 2**——父 Agent（深度 0）可以生成子 Agent（深度 1），但子 Agent 无法进一步委派。这可以防止失控的递归委派链。

## 关键特性

- 每个子 Agent 获得其**自己的终端会话**（与父 Agent 分开）
- **无嵌套委派** — 子 Agent 无法进一步委派（无孙 Agent）
- 子 Agent**无法**调用：`delegate_task`, `clarify`, `memory`, `send_message`, `execute_code`
- **中断传播** — 中断父 Agent 会中断所有活动的子 Agent
- 只有最终摘要进入父 Agent 的上下文，从而保持 Token 使用效率
- 子 Agent 继承父 Agent 的 **API 密钥、提供商配置和凭证池**（支持在达到速率限制时进行密钥轮换）

## 委派 vs execute_code

| 因素 | delegate_task | execute_code |
|--------|--------------|-------------|
| **推理** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的独立对话 | 无对话，仅脚本 |
| **工具访问** | 所有未被阻止的工具，附带推理 | 通过 RPC 的 7 个工具，无推理 |
| **并行性** | 最多 3 个并发子 Agent | 单个脚本 |
| **最适合** | 需要判断的复杂任务 | 机械化的多步骤流水线 |
| **Token 成本** | 更高（完整的 LLM 循环） | 更低（仅返回标准输出） |
| **用户交互** | 无（子 Agent 无法澄清） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当您需要机械化的数据处理或脚本化工作流时，使用 `execute_code`。

## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子 Agent 的最大轮次（默认值：50）
  default_toolsets: ["terminal", "file", "web"]  # 默认工具集
  model: "google/gemini-3-flash-preview"             # 可选的提供商/模型覆盖
  provider: "openrouter"                             # 可选的内置提供商

# 或者使用直接的自定义端点而不是提供商：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
```

:::tip
Agent 会根据任务复杂性自动处理委派。您无需明确要求它委派——它会在有意义时自动执行。
:::