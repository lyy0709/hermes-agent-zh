---
sidebar_position: 8
sidebar_label: "检查点与回滚"
title: "检查点与 /rollback"
description: "使用影子 Git 仓库和自动快照为破坏性操作提供文件系统安全网"
---

# 检查点与 `/rollback`

Hermes Agent 会在**破坏性操作**之前自动为你的项目创建快照，并允许你通过一条命令恢复。检查点**默认启用**——当没有文件修改工具触发时，其开销为零。

这个安全网由一个内部的**检查点管理器**提供支持，它在 `~/.hermes/checkpoints/` 下维护一个独立的影子 Git 仓库——你的真实项目 `.git` 永远不会被触及。

## 什么会触发检查点

检查点在以下操作之前自动创建：

- **文件工具** — `write_file` 和 `patch`
- **破坏性终端命令** — `rm`、`mv`、`sed -i`、`truncate`、`shred`、输出重定向 (`>`) 以及 `git reset`/`clean`/`checkout`

Agent 在**每个目录每轮对话中最多创建一个检查点**，因此长时间运行的会话不会产生大量快照。

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `/rollback` | 列出所有检查点及其变更统计信息 |
| `/rollback <N>` | 恢复到检查点 N（同时撤销最后一轮聊天） |
| `/rollback diff <N>` | 预览检查点 N 与当前状态之间的差异 |
| `/rollback <N> <file>` | 从检查点 N 恢复单个文件 |

## 检查点工作原理

从高层次看：

- Hermes 检测到工具即将**修改**工作树中的文件。
- 每轮对话（每个目录）一次，它会：
  - 为文件解析出一个合理的项目根目录。
  - 初始化或重用与该目录绑定的**影子 Git 仓库**。
  - 暂存并提交当前状态，附带简短、人类可读的原因说明。
- 这些提交构成了检查点历史，你可以通过 `/rollback` 检查和恢复。

```mermaid
flowchart LR
  user["用户命令\n(hermes, gateway)"]
  agent["AIAgent\n(run_agent.py)"]
  tools["文件与终端工具"]
  cpMgr["CheckpointManager"]
  shadowRepo["影子 git 仓库\n~/.hermes/checkpoints/<hash>"]

  user --> agent
  agent -->|"工具调用"| tools
  tools -->|"修改前\nensure_checkpoint()"| cpMgr
  cpMgr -->|"git add/commit"| shadowRepo
  cpMgr -->|"OK / 跳过"| tools
  tools -->|"应用更改"| agent
```

## 配置

检查点默认启用。在 `~/.hermes/config.yaml` 中配置：

```yaml
checkpoints:
  enabled: true          # 总开关 (默认: true)
  max_snapshots: 50      # 每个目录的最大检查点数

  # 自动维护（可选）：在启动时扫描 ~/.hermes/checkpoints/
  # 并删除那些工作目录已不存在（孤儿）或其最新提交早于 retention_days 的影子仓库。
  # 通过 ~/.hermes/checkpoints/ 内的 .last_prune 标记追踪，最多每 min_interval_hours 运行一次。
  auto_prune: false           # 默认关闭 — 启用以回收磁盘空间
  retention_days: 7
  delete_orphans: true        # 删除工作目录已不存在的仓库
  min_interval_hours: 24
```

要禁用：

```yaml
checkpoints:
  enabled: false
```

禁用后，检查点管理器将不执行任何操作，且从不尝试 Git 操作。

## 列出检查点

在 CLI 会话中：

```
/rollback
```

Hermes 会响应一个格式化的列表，显示变更统计信息：

```text
📸 检查点列表，项目路径：/path/to/project:

  1. 4270a8c  2026-03-16 04:36  patch 之前  (1 个文件, +1/-0)
  2. eaf4c1f  2026-03-16 04:35  write_file 之前
  3. b3f9d2e  2026-03-16 04:34  终端命令之前: sed -i s/old/new/ config.py  (1 个文件, +1/-1)

  /rollback <N>             恢复到检查点 N
  /rollback diff <N>        预览自检查点 N 以来的更改
  /rollback <N> <file>      从检查点 N 恢复单个文件
```

每个条目显示：

- 短哈希值
- 时间戳
- 原因（触发快照的操作）
- 变更摘要（更改的文件数、插入/删除行数）

## 使用 `/rollback diff` 预览更改

在决定恢复之前，预览自某个检查点以来的更改：

```
/rollback diff 1
```

这将显示一个 git diff 统计摘要，然后是实际的差异：

```text
test.py | 2 +-
 1 个文件被修改，1 行插入(+)，1 行删除(-)

diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1 +1 @@
-print('original content')
+print('modified content')
```

过长的差异输出会被限制在 80 行以内，以避免淹没终端。

## 使用 `/rollback` 恢复

通过编号恢复到某个检查点：

```
/rollback 1
```

在幕后，Hermes 会：

1. 验证目标提交存在于影子仓库中。
2. 为当前状态创建一个**回滚前快照**，以便你稍后可以“撤销撤销操作”。
3. 恢复工作目录中受跟踪的文件。
4. **撤销最后一轮对话**，使 Agent 的上下文与恢复后的文件系统状态匹配。

成功后：

```text
✅ 已恢复到检查点 4270a8c5: patch 之前
已自动保存回滚前快照。
(^_^)b 撤销了 4 条消息。已移除："Now update test.py to ..."
  历史记录中剩余 4 条消息。
  已撤销聊天轮次以匹配恢复的文件状态。
```

对话撤销确保 Agent 不会“记住”已被回滚的更改，避免在下一轮对话中产生混淆。

## 单文件恢复

仅从检查点恢复一个文件，而不影响目录中的其他文件：

```
/rollback 1 src/broken_file.py
```

当 Agent 修改了多个文件但只需要恢复其中一个时，这非常有用。

## 安全与性能防护

为了确保检查点功能安全且快速，Hermes 应用了多项防护措施：

- **Git 可用性** — 如果在 `PATH` 中找不到 `git`，检查点将透明地禁用。
- **目录范围** — Hermes 会跳过范围过大的目录（根目录 `/`、家目录 `$HOME`）。
- **仓库大小** — 文件数超过 50,000 的目录会被跳过，以避免缓慢的 Git 操作。
- **无变更快照** — 如果自上次快照以来没有更改，则跳过检查点。
- **非致命错误** — 检查点管理器内的所有错误都记录在调试级别；你的工具将继续运行。

## 检查点存储位置

所有影子仓库都位于：

```text
~/.hermes/checkpoints/
  ├── <hash1>/   # 对应一个工作目录的影子 git 仓库
  ├── <hash2>/
  └── ...
```

每个 `<hash>` 由工作目录的绝对路径派生而来。在每个影子仓库内，你会发现：

- 标准的 Git 内部文件（`HEAD`、`refs/`、`objects/`）
- 一个包含精选忽略列表的 `info/exclude` 文件
- 一个指向原始项目根目录的 `HERMES_WORKDIR` 文件

通常你永远不需要手动操作这些文件。

## 最佳实践

- **保持检查点启用** — 它们默认开启，并且在没有文件被修改时开销为零。
- **恢复前使用 `/rollback diff`** — 预览将要更改的内容以选择正确的检查点。
- **当只想撤销 Agent 驱动的更改时，使用 `/rollback` 而非 `git reset`**。
- **与 Git worktrees 结合使用以获得最大安全性** — 将每个 Hermes 会话放在其自己的 worktree/分支中，并将检查点作为额外保护层。

关于在同一仓库上并行运行多个 Agent，请参阅 [Git worktrees](./git-worktrees.md) 指南。