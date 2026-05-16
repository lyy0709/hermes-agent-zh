---
title: "看板工作者 — Hermes 看板工作者的常见陷阱、示例和边界情况"
sidebar_label: "看板工作者"
description: "Hermes 看板工作者的常见陷阱、示例和边界情况"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# 看板工作者

Hermes 看板工作者的常见陷阱、示例和边界情况。生命周期本身会作为 KANBAN_GUIDANCE（来自 agent/prompt_builder.py）自动注入到每个工作者的系统提示词中；当您需要深入了解特定场景时，加载此技能。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-worker` |
| 版本 | `2.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `kanban`, `multi-agent`, `collaboration`, `workflow`, `pitfalls` |
| 相关技能 | [`kanban-orchestrator`](/docs/user-guide/skills/bundled/devops/devops-kanban-orchestrator) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 看板工作者 — 陷阱与示例

> 您看到此技能是因为 Hermes 看板调度器将您作为工作者生成，并使用了 `--skills kanban-worker` — 它会在每个被调度的工作者中自动加载。**生命周期**（6 个步骤：定位 → 工作 → 心跳 → 阻塞/完成）也存在于自动注入到您系统提示词中的 `KANBAN_GUIDANCE` 块中。此技能提供了更深入的细节：良好的交接形式、重试诊断、边界情况。

## 工作空间处理

您的工作空间类型决定了您应在 `$HERMES_KANBAN_WORKSPACE` 中的行为方式：

| 类型 | 说明 | 如何工作 |
|---|---|---|
| `scratch` | 全新的临时目录，您独享 | 自由读写；任务归档后会被垃圾回收。 |
| `dir:<path>` | 共享的持久目录 | 其他运行将读取您写入的内容。将其视为长期存在的状态。路径保证是绝对的（内核拒绝相对路径）。 |
| `worktree` | 已解析路径下的 Git 工作树 | 如果 `.git` 不存在，请先从主仓库运行 `git worktree add <path> <branch>`，然后 cd 并正常工作。在此处提交工作。 |

## 租户隔离

如果设置了 `$HERMES_TENANT`，则该任务属于一个租户命名空间。在读取或写入持久记忆时，请在记忆条目前加上租户前缀，以防止上下文在租户间泄露：

- 正确：`business-a: Acme 是我们最大的客户`
- 错误（泄露）：`Acme 是我们最大的客户`

## 良好的摘要 + 元数据形式

`kanban_complete(summary=..., metadata=...)` 交接是下游工作者读取您所做工作的方式。有效的模式：

**编码任务：**
```python
kanban_complete(
    summary="已交付速率限制器 — 令牌桶，基于 user_id 的键，IP 回退，14 个测试通过",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id 为主，IP 回退用于未认证请求"],
    },
)
```

**需要人工审查的编码任务（review-required）：**

对于大多数更改代码的任务，在人工审查者看过之前，工作并非真正*完成*。应阻塞而非完成，`reason` 前缀为 `review-required: `，以便仪表板将该行标记为需要审查。首先将结构化元数据（更改的文件、测试计数、差异/PR 网址）放入评论中，因为 `kanban_block` 仅携带人类可读的原因 — 评论是持久的注释渠道。审查者要么批准并运行 `hermes kanban unblock <id>`（这将重新生成您，并附带评论线程以供任何后续操作），要么通过另一条评论要求更改。

```python
import json

kanban_comment(
    body="review-required 交接:\n" + json.dumps({
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "diff_path": "/path/to/worktree",  # 或推送后的 PR 网址
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    }, indent=2),
)
kanban_block(
    reason="review-required: 速率限制器已交付，14/14 个测试通过 — 在合并前需要审查 user_id/IP 回退选择",
)
```

仅当任务真正结束时才使用 `kanban_complete` — 例如，单行拼写错误修复、无功能影响的文档更改，或产物本身就是撰写内容的研究任务。

**研究任务：**
```python
kanban_complete(
    summary="审查了 3 个竞争库；vLLM 在吞吐量上胜出，SGLang 在延迟上胜出，Tensorrt-LLM 在内存效率上胜出",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

**审查任务：**
```python
kanban_complete(
    summary="审查了 PR #123；发现 2 个阻塞问题（/search 中的 SQL 注入，/settings 缺少 CSRF）",
    metadata={
        "pr_number": 123,
        "findings": [
            {"severity": "critical", "file": "api/search.py", "line": 42, "issue": "raw SQL concat"},
            {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"},
        ],
        "approved": False,
    },
)
```

塑造 `metadata`，以便下游解析器（审查者、聚合器、调度器）无需重新阅读您的文本即可使用它。

## 认领您实际创建的卡片

如果您的运行产生了新的看板任务（通过 `kanban_create`），请在 `kanban_complete` 的 `created_cards` 中传递这些 id。内核会验证每个 id 是否存在且由您的配置文件创建；任何虚假 id 都会导致完成被错误阻止，并列出出错原因，且被拒绝的尝试会永久记录在任务的事件日志中。**仅列出您从成功的 `kanban_create` 返回值中捕获的 id — 切勿从文本中编造 id，切勿粘贴之前运行的 id，切勿认领其他工作者创建的卡片。**

```python
# 正确 — 捕获返回值，然后认领它们。
c1 = kanban_create(title="修复 SQL 注入", assignee="security-worker")
c2 = kanban_create(title="修复 CSRF 中间件", assignee="web-worker")

kanban_complete(
    summary="审查完成；为两个发现生成了修复任务。",
    metadata={"pr_number": 123, "approved": False},
    created_cards=[c1["task_id"], c2["task_id"]],
)
```

```python
# 错误 — 认领您没有捕获返回值的 id。
kanban_complete(
    summary="创建了修复卡片 t_a1b2c3d4, t_deadbeef",  # 幻觉产生的
    created_cards=["t_a1b2c3d4", "t_deadbeef"],                   # → 网关拒绝
)
```

如果 `kanban_create` 调用失败（异常，tool_error），则卡片**未**创建 — 不要为其包含虚假 id。重试创建，或在摘要中提及失败并省略 id。文本扫描过程也会捕获您自由格式摘要中无法解析的 `t_<hex>` 引用；这些不会阻止完成，但会在仪表板的任务中显示为警告。

## 能快速得到回复的阻塞原因

错误：`"卡住了"` — 人类没有上下文。

正确：一句话说明您需要的具体决定。将更长的上下文作为评论留下。

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="完整上下文：我有来自 Cloudflare 头的用户 IP，但有些用户在具有数千个对等点的 NAT 后面。仅基于 IP 键控会导致误报。",
)
kanban_block(reason="速率限制键选择：IP（简单，NAT 不安全）还是 user_id（需要认证，跳过匿名端点）？")
```

阻塞消息是出现在仪表板/消息网关通知器中的内容。评论是人类打开任务时阅读的更深层上下文。

## 值得发送的心跳

良好的心跳会说明进度：`"第 12/50 轮，损失 0.31"`、`"已扫描 1.2M/2.4M 行"`、`"已上传 47/120 个视频"`。

糟糕的心跳：`"仍在工作"`、空注释、亚秒级间隔。最多每隔几分钟一次；对于约 2 分钟以下的任务，完全跳过。

## 重试场景

如果您打开任务，`kanban_show` 返回 `runs: [...]` 且包含一个或多个已关闭的运行，那么您是一次重试。先前运行的 `outcome` / `summary` / `error` 会告诉您什么没有成功。不要重复那条路径。典型的重试诊断：

- `outcome: "timed_out"` — 先前的尝试达到了 `max_runtime_seconds`。您可能需要分块处理工作或缩短时间。
- `outcome: "crashed"` — 内存不足或段错误。减少内存占用。
- `outcome: "spawn_failed"` + `error: "..."` — 通常是配置文件问题（缺少凭据，错误的 PATH）。通过 `kanban_block` 询问人类，而不是盲目重试。
- `outcome: "reclaimed"` + `summary: "task archived..."` — 操作员在先前运行期间归档了任务；您可能根本不应该运行，请仔细检查状态。
- `outcome: "blocked"` — 先前的尝试被阻塞；现在解除阻塞的评论应该已经在评论线程中。

## 禁止事项

- 调用 `delegate_task` 作为 `kanban_create` 的替代品。`delegate_task` 用于您运行中的短期推理子任务；`kanban_create` 用于跨 Agent 的交接，其生命周期超过一个 API 循环。
- 修改 `$HERMES_KANBAN_WORKSPACE` 之外的文件，除非任务正文说明要这样做。
- 创建分配给自己的后续任务 — 应分配给正确的专家。
- 完成您实际上未完成的任务。应阻塞它。

## 陷阱

**任务状态可能在调度和您启动之间发生变化。** 在调度器认领任务和您的进程实际启动之间，任务可能已被阻塞、重新分配或归档。始终先运行 `kanban_show`。如果它报告 `blocked` 或 `archived`，请停止 — 您不应该运行。

**工作空间可能有过时的产物。** 特别是 `dir:` 和 `worktree` 工作空间可能包含先前运行的文件。阅读评论线程 — 它通常会解释您为何再次运行以及工作空间处于何种状态。

**当有指导可用时，不要依赖 CLI。** `kanban_*` 工具在所有终端后端（Docker、Modal、SSH）中都能工作。从您的终端工具运行 `hermes kanban <verb>` 在容器化后端会失败，因为 CLI 未安装在那里。如有疑问，请使用工具。

## CLI 回退（用于脚本）

每个工具都有供操作员和脚本使用的 CLI 等效命令：
- `kanban_show` ↔ `hermes kanban show <id> --json`
- `kanban_complete` ↔ `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block <id> "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee <profile> [--parent <id>]`
- 等等。

在 Agent 内部使用工具；CLI 供终端前的人类使用。