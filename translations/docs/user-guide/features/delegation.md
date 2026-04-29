---
sidebar_position: 7
title: "子 Agent 委派"
description: "使用 delegate_task 生成具有独立上下文、受限工具集和独立终端会话的子 AIAgent 实例，实现并行工作流"
---

# 子 Agent 委派

`delegate_task` 工具会生成具有独立上下文、受限工具集和独立终端会话的子 AIAgent 实例。每个子 Agent 都拥有全新的对话并独立工作——只有其最终摘要会进入父 Agent 的上下文。

## 单个任务

```python
delegate_task(
    goal="调试测试失败的原因",
    context="错误：test_foo.py 第 42 行断言失败",
    toolsets=["terminal", "file"]
)
```

## 并行批量任务

默认最多 3 个并发子 Agent（可配置，无硬性上限）：

```python
delegate_task(tasks=[
    {"goal": "研究主题 A", "toolsets": ["web"]},
    {"goal": "研究主题 B", "toolsets": ["web"]},
    {"goal": "修复构建", "toolsets": ["terminal", "file"]}
])
```

## 子 Agent 上下文工作原理

:::warning 关键：子 Agent 一无所知
子 Agent 从一个**全新的对话**开始。它们对父 Agent 的对话历史、之前的工具调用或委派前讨论的任何内容都一无所知。子 Agent 的唯一上下文来自父 Agent 调用 `delegate_task` 时填充的 `goal` 和 `context` 字段。
:::

这意味着父 Agent 必须在调用中传递子 Agent 需要的**所有**信息：

```python
# 错误 - 子 Agent 不知道 "错误" 是什么
delegate_task(goal="修复错误")

# 正确 - 子 Agent 拥有所需的所有上下文
delegate_task(
    goal="修复 api/handlers.py 中的 TypeError",
    context="""文件 api/handlers.py 第 47 行存在 TypeError：
    'NoneType' 对象没有 'get' 属性。
    process_request() 函数从 parse_body() 接收一个字典，
    但当 Content-Type 缺失时，parse_body() 返回 None。
    项目位于 /home/user/myproject，使用 Python 3.11。"""
)
```

子 Agent 会收到一个根据你的目标和上下文构建的聚焦系统提示词，指示其完成任务并提供结构化摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

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

委派一个会淹没父 Agent 上下文的大型重构任务：

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

当你提供 `tasks` 数组时，子 Agent 使用线程池**并行**运行：

- **最大并发数：** 默认 3 个任务（可通过 `delegation.max_concurrent_children` 或 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量配置；下限为 1，无硬性上限）。超过限制的批次会返回工具错误，而不是被静默截断。
- **线程池：** 使用 `ThreadPoolExecutor`，配置的并发限制作为最大工作线程数
- **进度显示：** 在 CLI 模式下，树状视图实时显示每个子 Agent 的工具调用，并带有每个任务的完成行。在消息网关模式下，进度会分批处理并中继到父 Agent 的进度回调
- **结果排序：** 结果按任务索引排序以匹配输入顺序，无论完成顺序如何
- **中断传播：** 中断父 Agent（例如，发送新消息）会中断所有活动的子 Agent

单任务委派直接运行，没有线程池开销。

## 模型覆盖

你可以通过 `config.yaml` 为子 Agent 配置不同的模型——对于将简单任务委派给更便宜/更快的模型很有用：

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

某些工具集无论你指定什么，都对子 Agent 被阻止：
- `delegation` — 对叶子子 Agent 被阻止（默认）。为 `role="orchestrator"` 的子 Agent 保留，受 `max_spawn_depth` 限制——请参阅下面的[深度限制和嵌套编排](#深度限制和嵌套编排)。
- `clarify` — 子 Agent 无法与用户交互
- `memory` — 无法写入共享持久记忆
- `code_execution` — 子 Agent 应该逐步推理
- `send_message` — 无跨平台副作用（例如，发送 Telegram 消息）

## 最大迭代次数

每个子 Agent 都有一个迭代限制（默认：50），控制它可以进行多少次工具调用轮次：

```python
delegate_task(
    goal="快速文件检查",
    context="检查 /etc/nginx/nginx.conf 是否存在并打印其前 10 行",
    max_iterations=10  # 简单任务，不需要很多轮次
)
```

## 深度限制和嵌套编排

默认情况下，委派是**扁平**的：父 Agent（深度 0）生成子 Agent（深度 1），而这些子 Agent 无法进一步委派。这可以防止失控的递归委派。

对于多阶段工作流（研究 → 合成，或子问题的并行编排），父 Agent 可以生成**编排器**子 Agent，这些子 Agent*可以*委派自己的工作者：

```python
delegate_task(
    goal="调查三种代码审查方法并推荐一种",
    role="orchestrator",  # 允许此子 Agent 生成自己的工作者
    context="...",
)
```

- `role="leaf"`（默认）：子 Agent 无法进一步委派——与扁平委派行为相同。
- `role="orchestrator"`：子 Agent 保留 `delegation` 工具集。受 `delegation.max_spawn_depth` 控制（默认 **1** = 扁平，因此 `role="orchestrator"` 在默认情况下无效）。将 `max_spawn_depth` 提高到 2 以允许编排器子 Agent 生成叶子孙 Agent；提高到 3 允许三个级别（上限）。
- `delegation.orchestrator_enabled: false`：全局关闭开关，无论 `role` 参数如何，强制每个子 Agent 成为 `leaf`。

**成本警告：** 当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树最多可以达到 3×3×3 = 27 个并发叶子 Agent。每个额外的级别都会成倍增加支出——请有意识地提高 `max_spawn_depth`。

## 生命周期和持久性

:::warning delegate_task 是同步的——不持久
`delegate_task` 在**父 Agent 的当前轮次内**运行。它会阻塞父 Agent，直到每个子 Agent 完成（或被取消）。它**不是**后台作业队列：

- 如果父 Agent 被中断（用户发送新消息、`/stop`、`/new`），所有活动的子 Agent 都会被取消并返回 `status="interrupted"`。它们正在进行的工作将被丢弃。
- 子 Agent 在父 Agent 轮次结束后**不会**继续运行。
- 被取消的子 Agent 会返回结构化结果（`status="interrupted"`，`exit_reason="interrupted"`），但由于父 Agent 也被中断，该结果通常永远不会进入用户可见的回复中。

对于必须能在中断后存活或比当前轮次更持久的**持久性长时间运行工作**，请使用：

- `cronjob` (action=`create`) — 安排单独的 Agent 运行；不受父轮次中断影响。
- `terminal(background=True, notify_on_complete=True)` — 长时间运行的 shell 命令，在 Agent 执行其他操作时继续运行。
:::

## 关键特性

- 每个子 Agent 获得其**自己的终端会话**（与父 Agent 分开）
- **嵌套委派是选择加入的** — 只有 `role="orchestrator"` 的子 Agent 可以进一步委派，并且只有当 `max_spawn_depth` 从其默认值 1（扁平）提高时才允许。使用 `orchestrator_enabled: false` 全局禁用。
- 叶子子 Agent**无法**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。编排器子 Agent 保留 `delegate_task`，但仍无法使用其他四个工具。
- **中断传播** — 中断父 Agent 会中断所有活动的子 Agent（包括编排器下的孙 Agent）
- 只有最终摘要进入父 Agent 的上下文，保持 Token 使用效率
- 子 Agent 继承父 Agent 的 **API 密钥、提供商配置和凭证池**（支持在达到速率限制时进行密钥轮换）

## 委派 vs execute_code

| 因素 | delegate_task | execute_code |
|--------|--------------|-------------|
| **推理** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的独立对话 | 无对话，仅脚本 |
| **工具访问** | 所有未被阻止的工具，附带推理 | 通过 RPC 的 7 个工具，无推理 |
| **并行性** | 默认 3 个并发子 Agent（可配置） | 单个脚本 |
| **最适合** | 需要判断的复杂任务 | 机械的多步骤流水线 |
| **Token 成本** | 更高（完整的 LLM 循环） | 更低（仅返回 stdout） |
| **用户交互** | 无（子 Agent 无法澄清） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当你需要机械数据处理或脚本化工作流时，使用 `execute_code`。

## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子 Agent 的最大轮次（默认：50）
  # max_concurrent_children: 3              # 每批次的并行子 Agent 数（默认：3）
  # max_spawn_depth: 1                      # 树深度（1-3，默认 1 = 扁平）。提高到 2 以允许编排器子 Agent 生成叶子 Agent；3 表示三个级别。
  # orchestrator_enabled: true              # 禁用以强制所有子 Agent 为叶子角色。
  model: "google/gemini-3-flash-preview"             # 可选的提供商/模型覆盖
  provider: "openrouter"                             # 可选的内置提供商

# 或者使用直接的自定义端点而不是提供商：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
```

:::tip
Agent 会根据任务复杂性自动处理委派。你不需要明确要求它委派——它会在有意义时自动进行。
:::