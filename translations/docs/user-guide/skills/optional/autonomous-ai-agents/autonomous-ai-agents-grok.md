---
title: "Grok — 将编码任务委派给 xAI Grok Build CLI（功能开发、PR 处理）"
sidebar_label: "Grok"
description: "将编码任务委派给 xAI Grok Build CLI（功能开发、PR 处理）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Grok

将编码任务委派给 xAI Grok Build CLI（功能开发、PR 处理）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/autonomous-ai-agents/grok` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/grok` |
| 版本 | `0.1.0` |
| 作者 | Matt Maximo (MattMaximo), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Grok`, `xAI`, `Code-Review`, `Refactoring`, `Automation` |
| 相关技能 | [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Grok Build CLI — Hermes 编排指南

通过 Hermes 终端将编码任务委派给 [Grok Build](https://docs.x.ai/build/overview)（xAI 的自主编码 Agent CLI，即 `grok` 命令）。Grok 可以读取文件、编写代码、运行 shell 命令、生成子 Agent 以及管理 git 工作流。它有三种运行方式：交互式 TUI、**无头模式** (`-p`) 和通过 JSON-RPC 作为 **ACP Agent**。

这是继 `codex` 和 `claude-code` 之后的第三个同类技能。编排模式几乎完全相同 — **对于一次性任务，优先使用无头模式 `-p`**，对于交互式会话则使用 PTY。

## 使用场景

- 构建功能
- 重构代码
- PR 审查
- 批量问题修复
- 任何你原本会使用 Codex / Claude Code 但希望使用 Grok 的任务

## 先决条件

- **安装（推荐）：** `npm install -g @xai-official/grok`
  - 官方安装程序 `curl -fsSL https://x.ai/cli/install.sh | bash` 也有效，但 `x.ai` 主机在某些环境中受 Cloudflare 墙限制。npm 路径完全避免了这种依赖。
- **认证 — SuperGrok / X Premium+ 订阅（主要路径）：**
  - 运行一次 `grok login` → 打开浏览器进行 OAuth → Token 缓存在 `~/.grok/auth.json` 中。这会使用你的 **SuperGrok 或 X Premium+** 订阅（无需按 Token 计费的 API 账单）。
  - 通过查找 `~/.grok/auth.json` 或运行一个简单的无头冒烟测试来检查登录状态：`grok --no-auto-update -p "Say ok."`
  - 在 TUI 中，`/logout` 退出登录，`/login`（或重新启动）重新登录。
- **无需 git 仓库** — 与 Codex 不同，Grok 在 git 目录外也能正常运行（适用于临时/一次性任务）。
- **与 Claude Code / AGENTS.md 兼容，无需配置** — Grok 会自动读取 `CLAUDE.md`、`.claude/`（技能、Agent、MCP、钩子、规则）以及 `AGENTS.md` 系列文件。现有项目上下文直接生效。

> **API 密钥回退方案（非此用户的默认方案）：** Grok 也支持设置 `XAI_API_KEY` 环境变量，通过 `api.x.ai` 进行按量计费。仅在 `grok login` / SuperGrok 认证不可用时使用此方案。订阅路径（`grok login`）是此处预期的设置。

## 两种编排模式

### 模式 1：无头模式 (`-p`) — 非交互式（推荐）

运行一次性任务，打印结果，然后退出。没有 PTY，无需导航交互对话框。这是最简洁的集成路径 — 类似于 `claude -p` 和 `codex exec`。

```
terminal(command="grok --no-auto-update -p 'Add a dark mode toggle to settings'", workdir="/path/to/project", timeout=180)
```

在自动化中始终传递 `--no-auto-update` 以跳过后台更新检查。

**何时使用无头模式：**
- 一次性编码任务（修复错误、添加功能、重构）
- CI/CD 自动化和脚本编写
- 使用 `--output-format json` 进行结构化输出解析
- 任何不需要多轮对话的任务

### 模式 2：交互式 PTY — 多轮 TUI 会话

TUI 是一个全屏、支持鼠标交互的应用程序。使用 `pty=true` 驱动它。为了进行稳健的监控/输入，请使用 tmux（与 `claude-code` 技能相同的模式）。

```
# 在 tmux 会话中启动以进行 capture-pane 监控
terminal(command="tmux new-session -d -s grok-work -x 140 -y 40")
terminal(command="tmux send-keys -t grok-work 'cd /path/to/project && grok' Enter")

# 等待启动，然后发送任务
terminal(command="sleep 5 && tmux send-keys -t grok-work 'Refactor the auth module to use JWT' Enter")

# 监控进度
terminal(command="sleep 15 && tmux capture-pane -t grok-work -p -S -50")

# 完成后退出
terminal(command="tmux send-keys -t grok-work '/quit' Enter && sleep 1 && tmux kill-session -t grok-work")
```

**无头但内联输出的技巧：** 如果你想要 TUI 风格的输出，但又不想全屏 alt-screen 接管（例如，为了更清晰的日志），可以添加 `--no-alt-screen`。对于纯自动化，无头模式 `-p` 仍然比 TUI 更简洁。

## 无头模式深入探讨

### 常用标志

| 标志 | 效果 |
|------|--------|
| `-p, --single <PROMPT>` | 发送一个提示词，以无头模式运行，然后退出 |
| `-m, --model <MODEL>` | 选择模型 |
| `-s, --session-id <ID>` | 创建或恢复一个命名的无头会话 |
| `-r, --resume <ID>` | 恢复现有会话 |
| `-c, --continue` | 在当前目录中继续最近的会话 |
| `--cwd <PATH>` | 设置工作目录 |
| `--output-format <FMT>` | `plain`（默认）、`json` 或 `streaming-json` |
| `--always-approve` | 自动批准所有工具执行（相当于 `--full-auto` / `--yolo`） |
| `--no-alt-screen` | 内联运行，不进行全屏 TUI 接管 |
| `--no-auto-update` | 跳过后台更新检查（在所有自动化中使用） |

### 输出格式

- `plain` — 人类可读的文本（默认）
- `json` — 运行结束时的一个 JSON 对象（可清晰地解析结果）
- `streaming-json` — 新行分隔的 JSON 事件，随到达而输出
```
# 用于解析的结构化结果
terminal(command="grok --no-auto-update -p '列出 src/ 目录中的所有 TODO 注释' --output-format json", workdir="/project", timeout=120)

# 用于自主构建的自动批准
terminal(command="grok --no-auto-update --always-approve -p '重构数据库层并运行测试'", workdir="/project", timeout=300)
```

### 后台模式（长任务）

```
# 在后台无头启动
terminal(command="grok --no-auto-update --always-approve -p '重构认证模块'", workdir="/project", background=true, notify_on_complete=true)
# 返回 session_id

# 监控
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 必要时终止
process(action="kill", session_id="<id>")
```

对于交互式（TUI）后台会话，使用 `pty=true` + tmux，并通过 `tmux capture-pane` 进行监控，与 `claude-code` / `codex` 技能完全相同。

### 会话延续

```
# 启动一个命名会话
terminal(command="grok --no-auto-update -s refactor-db -p '开始重构数据库层' --always-approve", workdir="/project", timeout=240)

# 稍后恢复
terminal(command="grok --no-auto-update -r refactor-db -p '现在添加连接池' --always-approve", workdir="/project", timeout=180)

# 或者继续此目录中最近的会话
terminal(command="grok --no-auto-update -c -p '你上次修改了什么？'", workdir="/project", timeout=60)
```

## 只读审计 → Markdown 笔记模式

让 Grok 审查本地工件并返回干净的 markdown 笔记（用于 Obsidian 或仓库），而不修改任何内容：

1.  首先使用 Hermes 工具（`read_file`、`write_file`）准备稳定的输入文件。将相关上下文快照到临时文件中，而不是转储原始路径。
2.  运行 Grok 无头模式，**不带** `--always-approve` 参数，使其无法自动写入，并要求 `仅 markdown，无前言`。
3.  使用 `write_file()` 将 Grok 的 stdout 直接保存到目标笔记中。

```
grok --no-auto-update -p "读取 /tmp/current.md 和 /tmp/inventory.md。仅生成 markdown，无前言。输出一个标题为 'Cleanup Review' 的干净笔记。" --output-format plain
```

**陷阱（与 Claude Code 相同）：** 对于文档重写，一个宽松的“重写这个”提示词可能会返回变更摘要而不是完整的文件。相反：通过管道传入文件，并要求 `仅返回完整的修订版 markdown 文档。无介绍，无解释，无代码块。立即以 '# 标题' 开始。` 在覆盖目标文件之前，使用 `read_file()` 验证前几行。

## PR 审查模式

### 快速审查（无头模式）

```
terminal(command="cd /path/to/repo && git diff main...feature-branch | grok --no-auto-update -p '审查此差异中的错误、安全问题和风格问题。要彻底。'", timeout=120)
```

### 克隆到临时目录审查（安全，不修改仓库）

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && grok --no-auto-update -p '审查与 origin/main 的变更。检查错误、安全、竞态条件、缺失的测试。'", pty=true, timeout=300)
```

### 发布审查

```
terminal(command="gh pr comment 42 --body '<审查文本>'", workdir="/path/to/repo")
```

## 使用 Worktrees 并行修复问题

```
# 创建工作树
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# 在每个工作树中启动 Grok 无头模式（后台）
terminal(command="grok --no-auto-update --always-approve -p '修复问题 #78: <描述>。完成后提交。'", workdir="/tmp/issue-78", background=true, notify_on_complete=true)
terminal(command="grok --no-auto-update --always-approve -p '修复问题 #99: <描述>。完成后提交。'", workdir="/tmp/issue-99", background=true, notify_on_complete=true)

# 监控
process(action="list")

# 完成后：推送并打开 PR
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# 清理
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## 有用的子命令和 TUI 命令

| 命令 | 用途 |
|---------|---------|
| `grok` | 启动交互式 TUI |
| `grok -p "查询"` | 无头单次执行 |
| `grok login` / `grok logout` | 登录 / 登出（SuperGrok / X Premium+ OAuth） |
| `grok inspect` | 显示 Grok 在 cwd 中发现了什么：配置源、指令、技能、插件、钩子、MCP 服务器 |
| `grok agent stdio` | 通过 JSON-RPC 作为 ACP Agent 运行（用于 IDE/工具集成） |
| `grok update` | 更新 CLI（需要 `x.ai` 主机；在自动化中跳过） |

TUI 斜杠命令（仅限交互式）：`/model <名称>`、`/always-approve`、`/plan`、`/context`、`/compact`、`/resume`、`/sessions`、`/fork`、`/usage`、`/quit`。`Shift+Tab` 循环切换会话模式（包括计划模式，该模式会阻止除会话计划文件外的写入工具）。

## 配置 (`~/.grok/config.toml`)

```toml
[cli]
auto_update = false          # 持久化跳过后台更新检查

[ui]
permission_mode = "ask"      # 或 "always-approve" 以默认跳过工具提示

[models]
default = "grok-build-0.1"
```

将全局首选项放在 `~/.grok/config.toml` 中（而不是项目范围的 `.grok/config.toml`）。`permission_mode` 取代了旧的 `approval_mode` / `yolo = true` 键。

## 陷阱与注意事项

1.  **身份验证受订阅限制。** `grok login` 需要 SuperGrok 或 X Premium+ 订阅。如果登录失败或没有 `~/.grok/auth.json`，请确认订阅处于活动状态，然后再回退到 `XAI_API_KEY`。
2.  **不要混淆 Hermes 的 xAI 身份验证与 `grok` CLI 的身份验证。** Hermes 的 `x_search` 使用其自身的 xAI OAuth 运行；独立的 `grok` CLI 在 `~/.grok/auth.json` 中有单独的 Token。`x_search` 正常工作**并不**意味着 `grok` 已登录。
3.  **在自动化中始终传递 `--no-auto-update`** — 否则 Grok 会联系服务器进行更新检查（并且 `x.ai`/`storage.googleapis.com` 可能无法访问）。
4.  **优先使用 npm install 而不是 curl 安装程序** — `npm install -g @xai-official/grok` 可以避免被 Cloudflare 墙住的 `x.ai` 主机。
5.  **`--always-approve` 是自主构建的开关。** 没有它，无头运行可能会因等待工具批准提示而停滞。对于只读审查/审计工作，请有意省略它，这样 Grok 就无法修改文件。
6.  **无头模式 `-p` 会跳过 TUI 对话框**；TUI 需要 `pty=true`（+ tmux 用于监控），就像 Claude Code 一样。
7.  **使用 `--no-alt-screen`**，如果你内联运行 TUI 并且全屏 alt-screen 接管扰乱了捕获的输出。
8.  **不需要 git 仓库**，但对于 PR/提交工作流，你仍然需要一个 — 对于临时提交任务，使用 `mktemp -d && git init`。
9.  **完成后用 `tmux kill-session -t <name>` 清理 tmux 会话**。
## Hermes Agent 规则

1. **优先使用无头模式 `-p` 处理单一任务** —— 集成最简洁，可通过 `--output-format json` 输出结构化结果。
2. **始终设置 `workdir`（或 `--cwd`）**，以便 Grok 定位到正确的项目。
3. **在每次自动化调用中传递 `--no-auto-update`**。
4. **仅在需要 Grok 自主写入时使用 `--always-approve`**；对于只读审查和审计，请省略此参数。
5. **使用 `background=true, notify_on_complete=true` 将长任务置于后台运行**，并通过 `process` 工具进行监控。
6. **使用 tmux 进行多轮交互式工作**，并使用 `tmux capture-pane -t <session> -p -S -50` 进行监控。
7. **在依赖认证前进行验证** —— 检查 `~/.grok/auth.json` 或运行一个简单的 `grok -p "Say ok."` 冒烟测试；不要假设 Hermes 的 xAI 认证会自动继承。
8. **向用户报告结果** —— 总结 Grok 所做的更改以及剩余的工作。