---
sidebar_position: 7
title: "子 Agent 委派"
description: "使用 delegate_task 生成具有独立上下文、受限工具集和独立终端会话的子 AIAgent 实例，实现并行工作流"
---

# 子 Agent 委派

`delegate_task` 工具会生成子 AIAgent 实例，这些实例拥有独立的上下文、受限的工具集以及它们自己的终端会话。每个子 Agent 都从一个全新的对话开始并独立工作——只有其最终摘要会进入父 Agent 的上下文。

## 单个任务

```python
delegate_task(
    goal="调试测试失败的原因",
    context="错误：test_foo.py 第 42 行的断言失败",
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
# 错误 - 子 Agent 不知道 "the error" 是什么
delegate_task(goal="修复错误")

# 正确 - 子 Agent 拥有其所需的所有上下文
delegate_task(
    goal="修复 api/handlers.py 中的 TypeError",
    context="""文件 api/handlers.py 第 47 行有一个 TypeError：
    'NoneType' 对象没有 'get' 属性。
    函数 process_request() 从 parse_body() 接收一个字典，
    但当 Content-Type 缺失时，parse_body() 返回 None。
    项目位于 /home/user/myproject，使用 Python 3.11。"""
)
```

子 Agent 会收到一个根据你的目标和上下文构建的、聚焦的系统提示词，指示它完成任务并提供结构化的摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

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
        "context": "重点关注：纠错突破、实际应用、主要参与者",
        "toolsets": ["web"]
    }
])
```

### 代码审查 + 修复

将审查和修复工作流委派给一个全新的上下文：

```python
delegate_task(
    goal="审查身份验证模块是否存在安全问题并修复发现的问题",
    context="""项目位于 /home/user/webapp。
    身份验证模块文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py。
    项目使用 Flask、PyJWT 和 bcrypt。
    重点关注：SQL 注入、JWT 验证、密码处理、会话管理。
    修复发现的任何问题并运行测试套件（pytest tests/auth/）。""",
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

当你提供一个 `tasks` 数组时，子 Agent 会使用线程池**并行**运行：

- **最大并发数：** 默认 3 个任务（可通过 `delegation.max_concurrent_children` 或 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量配置；下限为 1，无硬性上限）。超过限制的批次会返回工具错误，而不是被静默截断。
- **线程池：** 使用 `ThreadPoolExecutor`，配置的并发限制作为最大工作线程数
- **进度显示：** 在 CLI 模式下，树状视图实时显示每个子 Agent 的工具调用，并带有每个任务的完成行。在消息网关模式下，进度会分批处理并中继到父 Agent 的进度回调函数
- **结果排序：** 无论完成顺序如何，结果都按任务索引排序以匹配输入顺序
- **中断传播：** 中断父 Agent（例如，发送新消息）会中断所有活动的子 Agent

单任务委派直接运行，没有线程池开销。

## 模型覆盖

你可以通过 `config.yaml` 为子 Agent 配置不同的模型——这对于将简单任务委派给更便宜/更快的模型很有用：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 用于子 Agent 的更便宜模型
  provider: "openrouter"              # 可选：将子 Agent 路由到不同的提供商
```

如果省略，子 Agent 将使用与父 Agent 相同的模型。

## 工具集选择技巧

`toolsets` 参数控制子 Agent 可以访问哪些工具。根据任务选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、文档查找 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、无需执行的代码审查 |
| `["terminal"]` | 系统管理、进程管理 |
无论你如何指定，某些工具集对子 Agent 始终是禁用的：
- `delegation` — 对叶子子 Agent 禁用（默认）。为 `role="orchestrator"` 的子 Agent 保留，但受 `max_spawn_depth` 限制 — 参见下面的[深度限制与嵌套编排](#深度限制与嵌套编排)。
- `clarify` — 子 Agent 无法与用户交互
- `memory` — 无法写入共享的持久化记忆
- `code_execution` — 子 Agent 应逐步推理
- `send_message` — 无跨平台副作用（例如，发送 Telegram 消息）

## 最大迭代次数

每个子 Agent 都有一个迭代限制（默认：50），用于控制其可以进行多少次工具调用轮次：

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # 简单任务，不需要很多轮次
)
```

## 子 Agent 超时

如果子 Agent 静默时间超过 `delegation.child_timeout_seconds` 的挂钟秒数，则会被视为卡住并终止。默认值为 **600**（10 分钟）— 比早期版本的 300 秒有所提高，因为处理非平凡研究任务的高推理模型在思考过程中会被终止。请根据具体安装进行调整：

```yaml
delegation:
  child_timeout_seconds: 600   # 默认值
```

对于快速的本地模型，可以降低此值；对于处理难题的慢速推理模型，可以提高此值。计时器在子 Agent 每次进行 API 调用或工具调用时重置 — 只有真正空闲的工作者才会触发终止。

:::tip 零调用超时的诊断转储
如果一个子 Agent 在进行了 **零次** API 调用后超时（通常是：提供商不可达、身份验证失败或工具模式拒绝），`delegate_task` 会将结构化诊断信息写入 `~/.hermes/logs/subagent-timeout-<session>-<timestamp>.log`，其中包含子 Agent 的配置快照、凭据解析跟踪以及任何早期错误消息。这比之前的静默超时行为更容易进行根本原因分析。
:::

## 监控运行中的子 Agent (`/agents`)

TUI 提供了一个 `/agents` 覆盖层（别名 `/tasks`），它将递归的 `delegate_task` 扇出转变为一流的审计界面：

- 运行中和最近完成的子 Agent 的实时树状视图，按父级分组
- 每个分支的成本、Token 和文件接触汇总
- 终止和暂停控制 — 在运行中取消特定子 Agent 而不中断其兄弟 Agent
- 事后审查：逐步查看每个子 Agent 的逐轮历史记录，即使它们已返回父级

经典 CLI 仅将 `/agents` 打印为文本摘要；TUI 才是覆盖层大放异彩的地方。参见 [TUI — 斜杠命令](/docs/user-guide/tui#slash-commands)。

## 深度限制与嵌套编排

默认情况下，委派是**扁平**的：父级（深度 0）生成子级（深度 1），而这些子级无法进一步委派。这可以防止失控的递归委派。

对于多阶段工作流（研究 → 合成，或子问题的并行编排），父级可以生成**编排器**子级，这些子级*可以*委派自己的工作者：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # 允许此子级生成自己的工作者
    context="...",
)
```

- `role="leaf"`（默认）：子级无法进一步委派 — 与扁平委派行为相同。
- `role="orchestrator"`：子级保留 `delegation` 工具集。受 `delegation.max_spawn_depth` 控制（默认 **1** = 扁平，因此 `role="orchestrator"` 在默认情况下无效）。将 `max_spawn_depth` 提高到 2 以允许编排器子级生成叶子孙级；提高到 3 则允许三个层级（上限）。
- `delegation.orchestrator_enabled: false`：全局关闭开关，无论 `role` 参数如何，强制每个子级为 `leaf`。

**成本警告：** 当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树状结构最多可达到 3×3×3 = 27 个并发叶子 Agent。每增加一个层级都会成倍增加开销 — 请有意识地提高 `max_spawn_depth`。

## 生命周期与持久性

:::warning delegate_task 是同步的 — 不具备持久性
`delegate_task` 在**父级当前轮次内**运行。它会阻塞父级，直到每个子级完成（或被取消）。它**不是**后台作业队列：

- 如果父级被中断（用户发送新消息、`/stop`、`/new`），所有活动子级都会被取消并返回 `status="interrupted"`。它们正在进行的工作将被丢弃。
- 子级在父级轮次结束后**不会**继续运行。
- 被取消的子级会返回一个结构化结果（`status="interrupted"`，`exit_reason="interrupted"`），但由于父级也被中断，该结果通常永远不会出现在用户可见的回复中。

对于必须能在中断后存活或比当前轮次更持久的**持久性长时间运行工作**，请使用：

- `cronjob` (action=`create`) — 调度一个单独的 Agent 运行；不受父级轮次中断影响。
- `terminal(background=True, notify_on_complete=True)` — 长时间运行的 shell 命令，在 Agent 执行其他操作时保持运行。
:::

## 关键特性

- 每个子 Agent 拥有其**独立的终端会话**（与父级分离）
- **嵌套委派是选择加入的** — 只有 `role="orchestrator"` 的子级可以进一步委派，并且仅在 `max_spawn_depth` 从其默认值 1（扁平）提高时才允许。使用 `orchestrator_enabled: false` 全局禁用。
- 叶子子 Agent **无法**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。编排器子级保留 `delegate_task`，但仍无法使用其他四个工具。
- **中断传播** — 中断父级会中断所有活动子级（包括编排器下的孙级）
- 只有最终摘要会进入父级的上下文，从而保持 Token 使用效率
- 子 Agent 继承父级的 **API 密钥、提供商配置和凭据池**（支持在达到速率限制时进行密钥轮换）

## 委派与 execute_code 对比

| 因素 | delegate_task | execute_code |
|--------|--------------|-------------|
| **推理** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的隔离对话 | 无对话，仅脚本 |
| **工具访问** | 所有未被禁用的工具，附带推理 | 通过 RPC 的 7 个工具，无推理 |
| **并行性** | 默认 3 个并发子 Agent（可配置） | 单个脚本 |
| **最适合** | 需要判断的复杂任务 | 机械化的多步骤流水线 |
| **Token 成本** | 较高（完整的 LLM 循环） | 较低（仅返回 stdout） |
| **用户交互** | 无（子 Agent 无法澄清） | 无 |
**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当你需要进行机械的数据处理或脚本化的工作流时，使用 `execute_code`。

## 配置

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 50                        # 每个子任务的最大轮次（默认：50）
  # max_concurrent_children: 3              # 每批次并行子任务数（默认：3）
  # max_spawn_depth: 1                      # 树深度（1-3，默认 1 = 扁平）。设置为 2 以允许编排器子任务生成叶子任务；3 表示三层。
  # orchestrator_enabled: true              # 禁用此项以强制所有子任务为叶子角色。
  model: "google/gemini-3-flash-preview"             # 可选的提供商/模型覆盖
  provider: "openrouter"                             # 可选的内置提供商

# 或者使用直接的自定义端点代替提供商：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
```

:::tip
Agent 会根据任务复杂度自动处理委派。你不需要明确要求它进行委派——它会在合适的时候自动进行。
:::