---
title: "Kanban Codex Lane"
sidebar_label: "Kanban Codex Lane"
description: "当 Hermes Kanban 工作器希望将 Codex CLI 作为独立的实现通道运行，同时 Hermes 保持对任务生命周期、协调、测试和交接的所有权时使用。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Kanban Codex Lane

当 Hermes Kanban 工作器希望将 Codex CLI 作为独立的实现通道运行，同时 Hermes 保持对任务生命周期、协调、测试和交接的所有权时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/kanban-codex-lane` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `kanban`, `codex`, `worktrees`, `autonomous-agents`, `prediction-market-bot` |
| 相关技能 | [`kanban-worker`](/docs/user-guide/skills/bundled/devops/devops-kanban-worker), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Kanban Codex Lane

## 概述

此技能定义了 Kanban 工作器使用的轻量级 Hermes+Codex 双通道约定。Hermes 始终是任务所有者：它调用 `kanban_show`，决定是否适合使用 Codex，创建或选择一个独立的工作空间，启动并监控 Codex，协调任何差异，运行验证，并写入最终的 `kanban_complete` 或 `kanban_block` 交接。Codex 仅作为输入通道。Codex 的输出不是任务完成信号，不是可信的审查者，也不允许直接写入持久的 Kanban 状态。

此约定存在的目的是让 Hermes 工作器可以在不改变调度器的情况下，使用 Codex 进行有界的实现帮助。调度器仍然必须生成 Hermes 工作器。一个工作器可以选择在其自身运行中生成 Codex，然后在独立审查和测试后接受、部分接受或拒绝该通道。

## 使用时机

当以下所有条件都满足时，使用 Codex 通道：

- Kanban 任务是编码、重构、文档编写、测试或机械迁移任务，且具有明确的验收标准。
- Hermes 可以在一次运行中评估一个有界的差异。
- 仓库可以在独立的 git worktree/分支中复制或检出。
- Codex 退出后，Hermes 可以自行运行相关测试。
- 提示词可以说明所有安全约束和不得更改的文件。

当以下任一条件为真时，请勿使用 Codex 通道：

- 任务需要 Kanban 正文中未捕获的人工判断。
- 工作器缺少仓库访问权限、Codex 认证或协调结果的时间。
- 更改涉及密钥、凭据存储、私人用户数据或生产订单录入系统。
- 一个小的直接编辑比生成另一个 Agent 更快、更安全。
- 任务仅为研究性质，应产生书面交接而非差异。
- 工作器可能仅基于 Codex 的自我报告就标记为完成。

## 所有权规则

1.  Hermes 拥有 Kanban 生命周期。Codex 绝不能调用 `kanban_complete`、`kanban_block`、`kanban_create`、消息网关消息传递或任何 Hermes 看板 CLI 来替代工作器。
2.  Hermes 拥有最终验收权。在审查和验证之前，将 Codex 的提交/差异视为不受信任的补丁。
3.  Hermes 拥有测试执行权。Codex 可以运行测试，但这些运行仅供参考；必须使用仓库的规范包装器从 Hermes 重复进行所需的验证。
4.  Hermes 拥有安全控制权。如果 Codex 更改了安全边界、风险门控、实时交易行为或密钥处理，即使测试通过，也应拒绝该通道。
5.  Hermes 拥有清理权。终止卡住的 Codex 进程，并在不再需要时移除临时工作树。

## 必需的工作树和分支模式

切勿在共享的脏检出中直接运行 Codex。使用将通道与 Kanban 任务关联并保持不受信任的编辑隔离的分支/工作树名称。

推荐变量：

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
BASE="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"
```

创建独立通道：

```bash
git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
git -C "$WORKTREE" status --short --branch
```

如果当前的 Kanban 工作空间已经是为此任务创建的独立 git 工作树，并且 `git status --short` 除了有意的 Hermes 编辑外是干净的，那么你可以在其中创建一个兄弟 Codex 分支。否则，创建一个单独的临时工作树，并在协调后将接受的提交挑选或复制回来。

协调后清理：

```bash
git -C "$REPO" worktree remove "$WORKTREE"
git -C "$REPO" branch -D "$BRANCH"  # 仅在接受的提交被复制/挑选或有意拒绝后执行
```

如果工作树需要作为审查的工件，请保留它；将其记录在 `codex_lane.artifacts` 中，并在交接时提及。

## Codex 能力检查

在生成 Codex 之前运行这些检查。缺少 Codex 是跳过通道的正常理由，如果 Hermes 可以直接执行任务，则不是任务阻塞项。

```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

如果需要 `/goal` 支持，请在检查可用性后启用或使用功能标志启动：

```bash
codex features enable goals || true
codex --enable goals --version
```

认证可以通过 `OPENAI_API_KEY` 或 Codex CLI OAuth 状态（通常是 `~/.codex/auth.json`）进行。请勿打印 Token 文件。缺少 `OPENAI_API_KEY` 并不能证明认证不可用。

## 模式选择
对于有界单次编辑，使用 `codex exec`，Codex 应自行退出：

```python
terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

仅当更广泛的多步骤工作受益于持久性目标跟踪时，才使用 Codex 的 `/goal` 命令。在 PTY/tmux 会话中交互式启动，或者如果该功能默认禁用，则使用 `codex --enable goals` 启动。保持目标自包含：仓库路径、任务 ID、安全约束、允许范围、验收标准、测试和提交预期。

粘贴到 Codex 中的示例 `/goal` 目标文本：

```text
/goal 仅在此仓库中工作：<WORKTREE>。任务：<TASK_ID> <TITLE>。
Hermes 拥有看板生命周期；不要调用 Hermes 的看板工具或消息传递。
在分支 <BRANCH> 上创建小型提交。遵循提示中的 PMB 安全约束。
运行请求的验证命令并报告确切的输出。生成差异和摘要后停止。
```

对于 prediction-market-bot 或安全敏感的仓库，不要使用 `--yolo`。优先在隔离的工作树内使用 `--full-auto`，然后依赖 Hermes 进行协调。

## 提示词构建

对于 prediction-market-bot 的工作，使用 `templates/pmb-codex-lane-prompt.md` 处的链接模板。对于其他仓库，保持相同的结构，并将 PMB 特定的安全块替换为仓库特定的不变量。

每个 Codex 提示词必须包含：

- `task_id`、标题和完整的看板验收标准。
- 仓库路径、工作树路径、分支名称和允许的文件范围。
- 明确声明：Hermes 拥有看板生命周期；Codex 仅作为输入通道。
- 要求的输出：简洁摘要、更改的文件、提交、运行的测试和已知风险。
- 禁止的操作：访问密钥、外部消息传递、看板变更、无关的重构、除非必需否则升级依赖项。
- Codex 可以运行的验证命令以及 Hermes 之后将运行的命令。

对于 PMB，逐字包含这些强制性的安全约束：

```text
PMB 安全约束：
- live-SIM 仅为模拟；不要添加或启用实时的 REST 订单录入。
- 切勿使用市价单。
- 不要添加执行交叉或绕过价格/风险检查。
- 不要伪造被动成交、成交、盈亏、订单状态或对账证据。
- 不要削弱风险门控、限制、紧急停止开关或故障关闭行为。
- 除非明确要求，否则将研究/选择逻辑保持在 C++ 热路径之外。
- 不要读取、打印、写入或要求密钥/令牌/凭据。
```

## 监控、超时和终止行为

在后台使用 PTY 和完成通知启动长时间的 Codex 通道：

```python
result = terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
session_id = result["session_id"]
```

在不干扰的情况下进行监控：

```python
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)
```

对于超过两分钟的通道，每隔几分钟发送一次看板心跳，例如 `kanban_heartbeat(note="Codex 通道在 <WORKTREE> 中运行；等待测试/差异")`。

终止条件：

- 在任务剩余的运行时间预算内没有有用的输出。
- Codex 请求密钥、生产凭据或外部权限。
- Codex 尝试修改工作树之外的文件。
- Codex 开始进行无关的重写或依赖项变更。
- Codex 在接近工作进程超时时仍在运行，且不存在安全的部分工件。

终止命令：

```python
process(action="kill", session_id=session_id)
```

终止后，检查 `git status --short`，仅在安全的情况下保留有用的补丁，并记录 `codex_lane.result: timed_out` 或 `rejected` 以及具体的 `rejected_reason`。

## 协调检查清单

Hermes 在接受任何 Codex 通道结果之前必须执行此检查清单：

- [ ] `git -C <WORKTREE> status --short --branch` 仅显示预期的文件。
- [ ] Hermes 已审查 `git -C <WORKTREE> diff --stat` 和 `git diff`。
- [ ] 不包含密钥、凭据、生成的缓存、无关数据或本地工件。
- [ ] PMB 安全约束得到保留：没有实时的 REST 订单录入、没有市价单、没有执行交叉、没有伪造的被动成交/盈亏、没有削弱风险门控、没有密钥。
- [ ] Codex 的提交足够小，可以干净地进行拣选或压缩。
- [ ] Hermes 自己运行了规范测试，对于 Hermes Agent 使用 `scripts/run_tests.sh`，对于其他仓库使用仓库文档中记录的包装脚本。
- [ ] 任何 Codex 运行的测试都与 Hermes 运行的测试分开列出。
- [ ] 已接受的提交/差异已应用到 Hermes 拥有的工作空间/分支。
- [ ] 被拒绝或部分的工作有具体原因，如果有用则包含工件路径。

验收结果：

- `accepted`：Codex 的差异/提交已审查、应用并验证。
- `partial`：部分 Codex 工作在接受编辑或拣选后被接受；被拒绝的部分已记录。
- `rejected`：没有 Codex 更改被接受；原因已记录。
- `timed_out`：Codex 超出了通道预算；可能存在也可能不存在有用的工件。

## kanban_complete 元数据模式

对于考虑使用通道的每个任务，在 `metadata.codex_lane` 下包含此对象。如果未使用 Codex，则设置 `used: false`，并在 `rejected_reason` 或同级的 `notes` 字段中解释原因。

```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/absolute/path/to/codex/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "command": "codex exec --full-auto ...",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>", "<sha2>"],
    "rejected_reason": "完全接受时为空；否则为具体原因",
    "tests_run": [
      {"command": "scripts/run_tests.sh tests/tools/test_x.py", "exit_code": 0, "owner": "hermes"},
      {"command": "codex-reported: npm test", "exit_code": 0, "owner": "codex"}
    ],
    "artifacts": ["/absolute/path/to/log-or-patch"]
  }
}
```
对于有意跳过 Codex 的任务：

```json
{
  "codex_lane": {
    "used": false,
    "mode": "skipped",
    "worktree": null,
    "branch": null,
    "command": null,
    "result": "rejected",
    "accepted_commits": [],
    "rejected_reason": "Direct Hermes edit was smaller and safer than spawning Codex.",
    "tests_run": [],
    "artifacts": []
  }
}
```

## 常见陷阱

1.  将 Codex 的自述报告当作验证。始终检查 `git diff` 并从 Hermes 重新运行测试。
2.  在用户脏的主检出分支中运行 Codex。始终在工作树/分支中进行隔离。
3.  让 Codex 拥有看板。Codex 可以总结进度，但看板状态应由 Hermes 写入。
4.  在提示词中忘记 PMB 安全约束。缺少安全文本是车道设置失败。
5.  使用 `/goal` 进行快速编辑。除非需要持久的多步骤延续，否则更推荐使用 `codex exec`。
6.  未记录原因就终止卡住的车道。`rejected_reason` 必须解释该决定。
7.  因为测试通过就接受广泛的、不相关的清理。应拒绝或仅挑选出范围内的更改。

## 验证清单

- [ ] 仅在检查了 `command -v codex`、`codex --version` 以及可选的目标功能后，才跳过或启动 Codex。
- [ ] Codex 仅在隔离的工作树/分支中运行。
- [ ] 提示词包含了任务范围、所有权规则、适用的 PMB 安全约束以及验证命令。
- [ ] Hermes 审查了 `git diff` 和安全敏感文件。
- [ ] Hermes 独立运行了规范测试。
- [ ] `kanban_complete.metadata.codex_lane` 遵循上述模式。
- [ ] 清理了临时进程和不必要的工作树。