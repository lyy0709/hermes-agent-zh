---
title: "看板工作者 — Hermes 看板工作者的常见陷阱、示例与边界情况"
sidebar_label: "看板工作者"
description: "Hermes 看板工作者的常见陷阱、示例与边界情况"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# 看板工作者

Hermes 看板工作者的常见陷阱、示例与边界情况。生命周期本身会作为 KANBAN_GUIDANCE（来自 agent/prompt_builder.py）自动注入到每个工作者的系统提示词中；当您需要深入了解特定场景的细节时，才需要加载此技能。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-worker` |
| 版本 | `2.0.0` |
| 标签 | `kanban`, `multi-agent`, `collaboration`, `workflow`, `pitfalls` |
| 相关技能 | [`kanban-orchestrator`](/docs/user-guide/skills/bundled/devops/devops-kanban-orchestrator) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 看板工作者 — 陷阱与示例

> 您看到此技能是因为 Hermes 看板调度器以 `--skills kanban-worker` 将您生成为工作者 — 每个被调度的工作者都会自动加载它。**生命周期**（6个步骤：定位 → 工作 → 心跳 → 阻塞/完成）也存在于自动注入到您系统提示词中的 `KANBAN_GUIDANCE` 块中。此技能提供更深入的细节：良好的交接格式、重试诊断、边界情况。

## 工作空间处理

您的工作空间类型决定了您应在 `$HERMES_KANBAN_WORKSPACE` 中的行为方式：

| 类型 | 说明 | 工作方式 |
|---|---|---|
| `scratch` | 全新的临时目录，您独享 | 自由读写；任务归档后会被垃圾回收。 |
| `dir:<路径>` | 共享的持久化目录 | 其他运行会读取您写入的内容。将其视为长期存在的状态。路径保证是绝对的（内核会拒绝相对路径）。 |
| `worktree` | 指定路径下的 Git 工作树 | 如果 `.git` 不存在，请先从主仓库运行 `git worktree add <路径> <分支>`，然后 cd 并正常工作。在此处提交工作。 |

## 租户隔离

如果设置了 `$HERMES_TENANT`，则该任务属于一个租户命名空间。读取或写入持久化记忆时，请在记忆条目前加上租户前缀，以防止上下文在租户间泄露：

- 正确：`business-a: Acme 是我们最大的客户`
- 错误（泄露）：`Acme 是我们最大的客户`

## 良好的摘要与元数据格式

`kanban_complete(summary=..., metadata=...)` 交接是下游工作者读取您工作成果的方式。有效的模式：

**编码任务：**
```python
kanban_complete(
    summary="已交付速率限制器 — 令牌桶，基于 user_id 的键，带 IP 回退，14 个测试通过",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id 为主键，IP 用于未认证请求的回退"],
    },
)
```

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
    summary="审查了 PR #123；发现 2 个阻塞性问题（/search 中的 SQL 注入，/settings 缺少 CSRF）",
    metadata={
        "pr_number": 123,
        "findings": [
            {"severity": "critical", "file": "api/search.py", "line": 42, "issue": "原始 SQL 拼接"},
            {"severity": "high", "file": "api/settings.py", "issue": "缺少 CSRF 中间件"},
        ],
        "approved": False,
    },
)
```

塑造 `metadata`，以便下游解析器（审查者、聚合器、调度器）无需重新阅读您的文本即可使用它。

## 能快速得到回复的阻塞原因

差：`"卡住了"` — 人类没有上下文。

好：用一句话说明您需要的具体决策。将更长的上下文作为评论留下。

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="完整上下文：我从 Cloudflare 头部获取了用户 IP，但有些用户在 NAT 后面，有数千个对等点。仅基于 IP 作为键会导致误报。",
)
kanban_block(reason="速率限制键选择：IP（简单，NAT 不安全）还是 user_id（需要认证，跳过匿名端点）？")
```

阻塞消息会显示在仪表板/消息网关通知器中。评论是人类打开任务时阅读的更深层上下文。

## 值得发送的心跳

好的心跳会说明进度：`"第 12/50 轮，损失 0.31"`、`"已扫描 1.2M/2.4M 行"`、`"已上传 47/120 个视频"`。

差的心跳：`"仍在工作"`、空注释、亚秒级间隔。最多每隔几分钟一次；对于约 2 分钟以下的任务，可以完全跳过。

## 重试场景

如果您打开任务并且 `kanban_show` 返回带有已关闭运行的 `runs: [...]`，那么您是一次重试。先前运行的 `outcome` / `summary` / `error` 会告诉您什么没有成功。不要重复那条路径。典型的重试诊断：

- `outcome: "timed_out"` — 先前的尝试达到了 `max_runtime_seconds`。您可能需要将工作分块或缩短它。
- `outcome: "crashed"` — 内存不足或段错误。减少内存占用。
- `outcome: "spawn_failed"` + `error: "..."` — 通常是配置文件问题（缺少凭证，错误的 PATH）。通过 `kanban_block` 询问人类，而不是盲目重试。
- `outcome: "reclaimed"` + `summary: "task archived..."` — 操作员在先前运行期间归档了任务；您可能根本不应该运行，请仔细检查状态。
- `outcome: "blocked"` — 先前的尝试被阻塞；现在线程中应该有解除阻塞的评论。

## 禁止事项

- 不要将 `delegate_task` 作为 `kanban_create` 的替代品。`delegate_task` 用于您运行内部的短期推理子任务；`kanban_create` 用于跨 Agent 的交接，其生命周期超过一次 API 循环。
- 除非任务正文说明，否则不要修改 `$HERMES_KANBAN_WORKSPACE` 之外的文件。
- 不要创建分配给自己的后续任务 — 应分配给正确的专家。
- 不要完成您实际上未完成的任务。应将其阻塞。

## 陷阱

**任务状态可能在调度和您启动之间发生变化。** 在调度器认领任务到您的进程实际启动之间，任务可能已被阻塞、重新分配或归档。始终先执行 `kanban_show`。如果它报告 `blocked` 或 `archived`，请停止 — 您不应该运行。

**工作空间可能有过时的产物。** 特别是 `dir:` 和 `worktree` 工作空间可能包含先前运行的文件。阅读评论线程 — 它通常会解释您为何再次运行以及工作空间处于什么状态。

**当有指导可用时，不要依赖 CLI。** `kanban_*` 工具在所有终端后端（Docker、Modal、SSH）中都能工作。从您的终端工具执行 `hermes kanban <动词>` 在容器化后端会失败，因为 CLI 未安装在那里。如有疑问，请使用工具。

## CLI 回退（用于脚本）

每个工具都有供人类操作员和脚本使用的 CLI 等效命令：
- `kanban_show` ↔ `hermes kanban show <id> --json`
- `kanban_complete` ↔ `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block <id> "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee <profile> [--parent <id>]`
- 等等。

在 Agent 内部使用工具；CLI 是为终端前的人类准备的。