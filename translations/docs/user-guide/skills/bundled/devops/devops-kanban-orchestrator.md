---
title: "看板编排器"
sidebar_label: "看板编排器"
description: "用于通过看板路由工作的编排器配置文件的分解手册 + 专家名册约定 + 防诱惑规则"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 看板编排器

用于通过看板路由工作的编排器配置文件的分解手册 + 专家名册约定 + 防诱惑规则。"不要自己动手做"规则和基本生命周期已自动注入到每个看板工作者的系统提示词中；当你专门扮演编排器角色时，此技能是更深入的手册。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-orchestrator` |
| 版本 | `2.0.0` |
| 标签 | `kanban`, `multi-agent`, `orchestration`, `routing` |
| 相关技能 | [`kanban-worker`](/docs/user-guide/skills/bundled/devops/devops-kanban-worker) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 看板编排器 — 分解手册

> **核心工作者生命周期**（包括 `kanban_create` 扇出模式和"分解，不执行"规则）通过 `KANBAN_GUIDANCE` 系统提示词块自动注入到每个看板流程中。当你是一个整个工作就是路由的编排器配置文件时，此技能是更深入的手册。

## 何时使用看板（相对于直接完成工作）

当以下任何一项为真时，创建看板任务：

1.  **需要多个专家。** 研究 + 分析 + 写作是三个配置文件。
2.  **工作应能在崩溃或重启后继续。** 长时间运行、重复或重要的工作。
3.  **用户可能想要介入。** 任何步骤中都可以有人参与。
4.  **多个子任务可以并行运行。** 扇出以提高速度。
5.  **预期有审查/迭代。** 审查者配置文件在起草者输出上循环。
6.  **审计跟踪很重要。** 看板行在 SQLite 中永久保存。

如果*以上都不适用*——它是一个小型的、一次性的推理任务——请改用 `delegate_task` 或直接回答用户。

## 防诱惑规则

你的工作描述是"路由，不执行"。强制执行此点的规则：

-   **不要自己执行工作。** 你的受限工具集通常甚至不包括用于实现的终端/文件/代码/网络。如果你发现自己"只是快速修复一下"——请停止并为合适的专家创建一个任务。
-   **对于任何具体任务，创建一个看板任务并分配它。** 每次都这样做。
-   **如果没有合适的专家，询问用户要创建哪个配置文件。** 不要默认在"差不多"的情况下自己动手。
-   **分解、路由和总结——这就是全部工作。**

## 标准专家名册（约定）

除非用户的设置自定义了配置文件，否则假设这些存在。根据用户实际拥有的配置进行调整——如果不确定，请询问。

| 配置文件 | 职责 | 典型工作空间 |
|---|---|---|
| `researcher` | 阅读来源，收集事实，撰写发现 | `scratch` |
| `analyst` | 综合、排序、去重。消耗多个 `researcher` 输出 | `scratch` |
| `writer` | 以用户的口吻起草文本 | `scratch` 或 `dir:` 进入其 Obsidian 知识库 |
| `reviewer` | 阅读输出，留下发现，批准把关 | `scratch` |
| `backend-eng` | 编写服务器端代码 | `worktree` |
| `frontend-eng` | 编写客户端代码 | `worktree` |
| `ops` | 运行脚本，管理服务，处理部署 | `dir:` 进入运维脚本仓库 |
| `pm` | 编写规范、验收标准 | `scratch` |

## 分解手册

### 步骤 1 — 理解目标

如果目标不明确，请提出澄清问题。提问成本低；生成错误的团队成本高。

### 步骤 2 — 草拟任务图

在创建任何内容之前，大声（在你的回复中向用户）草拟图表。以"分析我们是否应该迁移到 Postgres"为例：

```
T1  researcher        研究：Postgres 成本 vs 当前
T2  researcher        研究：Postgres 性能 vs 当前
T3  analyst           综合迁移建议       parents: T1, T2
T4  writer            起草决策备忘录     parents: T3
```

向用户展示此图。在创建任何内容之前，让他们纠正。

### 步骤 3 — 创建任务并链接

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="researcher",
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="researcher",
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="analyst",
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="writer",
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` 控制晋升——子任务保持在 `todo` 状态，直到每个父任务都达到 `done`，然后自动晋升到 `ready`。无需手动协调；调度器和依赖引擎会处理。

### 步骤 4 — 完成你自己的任务

如果你自己是作为一个任务生成的（例如，`planner` 配置文件被分配了 `T0: "investigate Postgres migration"`），请用你所创建内容的摘要来标记它完成：

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 researchers parallel, 1 analyst on their outputs, 1 writer on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "researcher", "parents": []},
            "T2": {"assignee": "researcher", "parents": []},
            "T3": {"assignee": "analyst", "parents": ["T1", "T2"]},
            "T4": {"assignee": "writer", "parents": ["T3"]},
        },
    },
)
```

### 步骤 5 — 向用户报告

用简单的语言告诉他们你创建了什么：

> 我已排队 4 个任务：
> - **T1** (researcher): 成本比较
> - **T2** (researcher): 性能比较，与 T1 并行
> - **T3** (analyst): 综合 T1 + T2 形成建议
> - **T4** (writer): 将 T3 转化为 CTO 备忘录
>
> 调度器现在将处理 T1 和 T2。T3 在两者都完成后开始。当 T4 完成时，你会收到一个消息网关的 ping。使用仪表板或 `hermes kanban tail <id>` 来跟进。

## 常见模式

**扇出 + 扇入（研究 → 综合）：** N 个没有父任务的 `researcher` 任务，一个以所有它们为父任务的 `analyst` 任务。

**带关卡的流水线：** `pm → backend-eng → reviewer`。每个阶段的 `parents=[previous_task]`。审查者阻塞或完成；如果审查者阻塞，操作员会提供反馈并重新生成。

**同配置文件队列：** 50 个任务，都分配给 `translator`，它们之间没有依赖关系。调度器串行处理——翻译器按优先级顺序处理它们，在自己的记忆中积累经验。

**人机交互：** 任何任务都可以 `kanban_block()` 以等待输入。在 `/unblock` 后调度器重新生成。评论线程承载完整的上下文。

## 陷阱

**重新分配 vs. 新任务。** 如果审查者因"需要修改"而阻塞，请创建一个从审查者任务链接的**新**任务——不要带着严厉的表情重新运行同一个任务。新任务分配给原始实现者配置文件。

**链接的参数顺序。** `kanban_link(parent_id=..., child_id=...)` — 父任务在前。混淆它们会导致错误的任务降级到 `todo`。

**如果图形结构依赖于中间发现，不要预先创建整个图。** 如果 T3 的结构取决于 T1 和 T2 的发现，让 T3 作为一个"综合发现"任务存在，其自己的第一步是读取父任务的交接并计划其余部分。编排器可以生成编排器。

**租户继承。** 如果你的环境中设置了 `HERMES_TENANT`，在每个 `kanban_create` 调用中传递 `tenant=os.environ.get("HERMES_TENANT")`，以便子任务保持在同一个命名空间中。