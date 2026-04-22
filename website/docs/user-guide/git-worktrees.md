---
sidebar_position: 3
sidebar_label: "Git Worktrees"
title: "Git Worktrees"
description: "使用 git worktrees 和隔离的代码检出，在同一仓库上安全地运行多个 Hermes Agent"
---

# Git Worktrees

Hermes Agent 经常用于大型、长期存在的代码仓库。当您想要：

- 在同一项目上**并行运行多个 Agent**，或者
- 将实验性的重构与主分支隔离时，

Git **worktrees** 是为每个 Agent 提供其独立代码检出的最安全方式，而无需复制整个仓库。

本页展示了如何将 worktrees 与 Hermes 结合使用，以便每个会话都有一个干净、隔离的工作目录。

## 为什么在 Hermes 中使用 Worktrees？

Hermes 将**当前工作目录**视为项目根目录：

- CLI：运行 `hermes` 或 `hermes chat` 的目录
- 消息网关：由 `MESSAGING_CWD` 设置的目录

如果您在**同一个代码检出**中运行多个 Agent，它们的更改可能会相互干扰：

- 一个 Agent 可能会删除或重写另一个 Agent 正在使用的文件。
- 更难理解哪些更改属于哪个实验。

使用 worktrees，每个 Agent 获得：

- 其**自己的分支和工作目录**
- 其**自己的 Checkpoint Manager 历史记录**，用于 `/rollback`

另请参阅：[检查点和 /rollback](./checkpoints-and-rollback.md)。

## 快速开始：创建 Worktree

从您的主仓库（包含 `.git/` 的目录）中，为功能分支创建一个新的 worktree：

```bash
# 从主仓库根目录
cd /path/to/your/repo

# 在 ../repo-feature 中创建新分支和 worktree
git worktree add ../repo-feature feature/hermes-experiment
```

这将创建：

- 一个新目录：`../repo-feature`
- 一个新分支：`feature/hermes-experiment`，检出到该目录

现在您可以 `cd` 进入新的 worktree 并在那里运行 Hermes：

```bash
cd ../repo-feature

# 在 worktree 中启动 Hermes
hermes
```

Hermes 将：

- 将 `../repo-feature` 视为项目根目录。
- 使用该目录处理上下文文件、代码编辑和工具。
- 使用一个**独立的检查点历史记录**用于 `/rollback`，其范围限定在此 worktree。

## 并行运行多个 Agent

您可以创建多个 worktrees，每个都有其自己的分支：

```bash
cd /path/to/your/repo

git worktree add ../repo-experiment-a feature/hermes-a
git worktree add ../repo-experiment-b feature/hermes-b
```

在单独的终端中：

```bash
# 终端 1
cd ../repo-experiment-a
hermes

# 终端 2
cd ../repo-experiment-b
hermes
```

每个 Hermes 进程：

- 在其自己的分支上工作（`feature/hermes-a` 与 `feature/hermes-b`）。
- 在不同的影子仓库哈希（根据 worktree 路径派生）下写入检查点。
- 可以独立使用 `/rollback` 而不影响另一个。

这在以下情况下特别有用：

- 运行批量重构。
- 尝试同一任务的不同方法。
- 将 CLI + 网关会话配对以针对同一上游仓库。

## 安全地清理 Worktrees

当您完成实验时：

1.  决定是保留还是丢弃工作成果。
2.  如果想保留：
    - 像往常一样将分支合并到主分支。
3.  移除 worktree：

```bash
cd /path/to/your/repo

# 移除 worktree 目录及其引用
git worktree remove ../repo-feature
```

注意：

- `git worktree remove` 会拒绝移除包含未提交更改的 worktree，除非您强制移除。
- 移除 worktree **不会**自动删除分支；您可以使用常规的 `git branch` 命令删除或保留分支。
- `~/.hermes/checkpoints/` 下的 Hermes 检查点数据在移除 worktree 时不会自动清理，但通常非常小。

## 最佳实践

- **每个 Hermes 实验使用一个 worktree**
  - 为每个实质性更改创建一个专用的分支/worktree。
  - 这可以使差异保持聚焦，并使 PR 小而易于审查。
- **根据实验命名分支**
  - 例如：`feature/hermes-checkpoints-docs`、`feature/hermes-refactor-tests`。
- **频繁提交**
  - 使用 git 提交来标记高级里程碑。
  - 使用[检查点和 /rollback](./checkpoints-and-rollback.md) 作为工具驱动编辑之间的安全网。
- **在使用 worktrees 时，避免从裸仓库根目录运行 Hermes**
  - 更推荐使用 worktree 目录，这样每个 Agent 都有明确的范围。

## 使用 `hermes -w`（自动 Worktree 模式）

Hermes 有一个内置的 `-w` 标志，可以**自动创建一个一次性的 git worktree** 及其自己的分支。您无需手动设置 worktrees —— 只需 `cd` 进入您的仓库并运行：

```bash
cd /path/to/your/repo
hermes -w
```

Hermes 将：

- 在您的仓库内的 `.worktrees/` 下创建一个临时 worktree。
- 检出到一个隔离的分支（例如 `hermes/hermes-<hash>`）。
- 在该 worktree 内运行完整的 CLI 会话。

这是获得 worktree 隔离的最简单方法。您还可以将其与单个查询结合使用：

```bash
hermes -w -q "Fix issue #123"
```

对于并行 Agent，打开多个终端并在每个终端中运行 `hermes -w` —— 每次调用都会自动获得其自己的 worktree 和分支。

## 总结

- 使用 **git worktrees** 为每个 Hermes 会话提供其自己干净的代码检出。
- 使用**分支**来捕获实验的高级历史记录。
- 使用**检查点 + `/rollback`** 来恢复每个 worktree 内的错误。

这种组合为您提供：

- 强有力的保证，确保不同的 Agent 和实验不会相互干扰。
- 快速的迭代周期，并能轻松从错误的编辑中恢复。
- 干净、易于审查的拉取请求。