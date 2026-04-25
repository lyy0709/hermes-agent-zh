---
title: "Claude Code — 将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）"
sidebar_label: "Claude Code"
description: "将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Claude Code

将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）。用于构建功能、重构、PR 审查和迭代式编码。需要安装 claude CLI。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/claude-code` |
| 版本 | `2.2.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `Coding-Agent`, `Claude`, `Anthropic`, `Code-Review`, `Refactoring`, `PTY`, `Automation` |
| 相关技能 | [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Claude Code — Hermes 编排指南

通过 Hermes 终端将编码任务委派给 [Claude Code](https://code.claude.com/docs/en/cli-reference)（Anthropic 的自主编码 Agent CLI）。Claude Code v2.x 可以自主读取文件、编写代码、运行 shell 命令、生成子 Agent 以及管理 git 工作流。

## 先决条件

- **安装：** `npm install -g @anthropic-ai/claude-code`
- **认证：** 运行一次 `claude` 以登录（Pro/Max 用户使用浏览器 OAuth，或设置 `ANTHROPIC_API_KEY`）
- **控制台认证：** `claude auth login --console` 用于 API 密钥计费
- **SSO 认证：** `claude auth login --sso` 用于企业版
- **检查状态：** `claude auth status`（JSON）或 `claude auth status --text`（人类可读）
- **健康检查：** `claude doctor` — 检查自动更新器和安装健康状况
- **版本检查：** `claude --version`（需要 v2.x+）
- **更新：** `claude update` 或 `claude upgrade`

## 两种编排模式

Hermes 以两种根本不同的方式与 Claude Code 交互。请根据任务选择。

### 模式 1：打印模式 (`-p`) — 非交互式（大多数任务的首选）

打印模式运行一次性任务，返回结果并退出。不需要 PTY。没有交互式提示。这是最简洁的集成路径。

```
terminal(command="claude -p '为 src/ 中的所有 API 调用添加错误处理' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**何时使用打印模式：**
- 一次性编码任务（修复 bug、添加功能、重构）
- CI/CD 自动化和脚本编写
- 使用 `--json-schema` 进行结构化数据提取
- 管道输入处理（`cat file | claude -p "分析此文件"`）
- 任何不需要多轮对话的任务

**打印模式跳过所有交互式对话框** — 没有工作区信任提示，没有权限确认。这使其非常适合自动化。

### 模式 2：通过 tmux 进行交互式 PTY — 多轮会话

交互式模式提供一个完整的对话式 REPL，您可以发送后续提示、使用斜杠命令并实时观看 Claude 工作。**需要 tmux 编排。**

```
# 启动一个 tmux 会话
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# 在其中启动 Claude Code
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# 等待启动，然后发送您的任务
# （欢迎屏幕后大约等待 3-5 秒）
terminal(command="sleep 5 && tmux send-keys -t claude-work '重构认证模块以使用 JWT Token' Enter")

# 通过捕获窗格来监控进度
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# 发送后续任务
terminal(command="tmux send-keys -t claude-work '现在为新 JWT 代码添加单元测试' Enter")

# 完成后退出
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**何时使用交互式模式：**
- 多轮迭代工作（重构 → 审查 → 修复 → 测试循环）
- 需要人工参与决策的任务
- 探索性编码会话
- 当您需要使用 Claude 的斜杠命令时（`/compact`, `/review`, `/model`）

## PTY 对话框处理（交互式模式的关键）

Claude Code 在首次启动时最多会显示两个确认对话框。您必须通过 tmux send-keys 处理这些对话框：

### 对话框 1：工作区信任（首次访问目录时）
```
❯ 1. 是的，我信任此文件夹    ← 默认（只需按 Enter）
  2. 不，退出
```
**处理方式：** `tmux send-keys -t <session> Enter` — 默认选择是正确的。

### 对话框 2：绕过权限警告（仅在使用 --dangerously-skip-permissions 时出现）
```
❯ 1. 不，退出                    ← 默认（错误的选择！）
  2. 是的，我接受
```
**处理方式：** 必须先向下导航，然后按 Enter：
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### 健壮的对话框处理模式
```
# 启动并绕过权限
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"你的任务\"' Enter")

# 处理信任对话框（按 Enter 选择默认的“是”）
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# 处理权限对话框（向下然后按 Enter 选择“是的，我接受”）
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# 现在等待 Claude 工作
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**注意：** 首次接受某个目录的信任后，信任对话框将不再出现。只有权限对话框会在每次使用 `--dangerously-skip-permissions` 时重复出现。

## CLI 子命令

| 子命令 | 用途 |
|------------|---------|
| `claude` | 启动交互式 REPL |
| `claude "查询"` | 使用初始提示启动 REPL |
| `claude -p "查询"` | 打印模式（非交互式，完成后退出） |
| `cat file \| claude -p "查询"` | 将内容作为 stdin 上下文管道传输 |
| `claude -c` | 继续此目录中最近的对话 |
| `claude -r "id"` | 按 ID 或名称恢复特定会话 |
| `claude auth login` | 登录（添加 `--console` 用于 API 计费，`--sso` 用于企业版） |
| `claude auth status` | 检查登录状态（返回 JSON；`--text` 用于人类可读格式） |
| `claude mcp add <name> -- <cmd>` | 添加 MCP 服务器 |
| `claude mcp list` | 列出已配置的 MCP 服务器 |
| `claude mcp remove <name>` | 移除 MCP 服务器 |
| `claude agents` | 列出已配置的 Agent |
| `claude doctor` | 对安装和自动更新器运行健康检查 |
| `claude update` / `claude upgrade` | 将 Claude Code 更新到最新版本 |
| `claude remote-control` | 启动服务器以从 claude.ai 或移动应用控制 Claude |
| `claude install [target]` | 安装原生构建（稳定版、最新版或特定版本） |
| `claude setup-token` | 设置长期有效的认证 Token（需要订阅） |
| `claude plugin` / `claude plugins` | 管理 Claude Code 插件 |
| `claude auto-mode` | 检查自动模式分类器配置 |
## 打印模式深度解析

### 结构化 JSON 输出
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

返回一个 JSON 对象：
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603, ... },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**关键字段：** `session_id` 用于恢复会话，`num_turns` 用于统计代理式循环次数，`total_cost_usd` 用于跟踪花费，`subtype` 用于检测成功/错误（`success`、`error_max_turns`、`error_budget`）。

### 流式 JSON 输出
要实现实时的 Token 流式传输，请使用 `stream-json` 格式并配合 `--verbose` 参数：
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

返回换行分隔的 JSON 事件。可以使用 jq 过滤以获取实时文本：
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

流事件包含 `system/api_retry` 类型，其中包含 `attempt`、`max_retries` 和 `error` 字段（例如 `rate_limit`、`billing_error`）。

### 双向流式传输
要实现实时的输入和输出流式传输：
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages` 参数会将用户消息重新发送到标准输出以进行确认。

### 管道输入
```
# 通过管道传输文件进行分析
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# 通过管道传输多个文件
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# 通过管道传输命令输出
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### 用于结构化提取的 JSON 模式
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

从 JSON 结果中解析 `structured_output`。Claude 在返回之前会根据模式验证输出。

### 会话恢复
```
# 开始一个任务
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# 使用会话 ID 恢复
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# 或者恢复同一目录中最近的会话
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# 派生一个会话（新 ID，保留历史记录）
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```

### 用于 CI/脚本的裸模式
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` 模式会跳过钩子、插件、MCP 发现和 CLAUDE.md 加载。启动速度最快。需要设置 `ANTHROPIC_API_KEY`（跳过 OAuth）。

要在裸模式中有选择地加载上下文：
| 要加载的内容 | 标志 |
|---------|------|
| 系统提示词附加内容 | `--append-system-prompt "text"` 或 `--append-system-prompt-file path` |
| 设置 | `--settings <file-or-json>` |
| MCP 服务器 | `--mcp-config <file-or-json>` |
| 自定义 Agent | `--agents '<json>'` |

### 过载时的备用模型
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
当默认模型过载时，自动回退到指定的模型（仅限打印模式）。

## 完整的 CLI 标志参考

### 会话与执行环境
| 标志 | 作用 |
|------|--------|
| `-p, --print` | 非交互式单次模式（完成后退出） |
| `-c, --continue` | 恢复当前目录中最近的对话 |
| `-r, --resume <id>` | 通过 ID 或名称恢复特定会话（如果未提供 ID，则显示交互式选择器） |
| `--fork-session` | 恢复时，创建新的会话 ID 而不是重用原始 ID |
| `--session-id <uuid>` | 为对话使用特定的 UUID |
| `--no-session-persistence` | 不将会话保存到磁盘（仅限打印模式） |
| `--add-dir <paths...>` | 授予 Claude 访问额外工作目录的权限 |
| `-w, --worktree [name]` | 在 `.claude/worktrees/<name>` 处的独立 git 工作树中运行 |
| `--tmux` | 为工作树创建一个 tmux 会话（需要 `--worktree`） |
| `--ide` | 启动时自动连接到有效的 IDE |
| `--chrome` / `--no-chrome` | 启用/禁用 Chrome 浏览器集成以进行 Web 测试 |
| `--from-pr [number]` | 恢复链接到特定 GitHub PR 的会话 |
| `--file <specs...>` | 启动时要下载的文件资源（格式：`file_id:relative_path`） |

### 模型与性能
| 标志 | 作用 |
|------|--------|
| `--model <alias>` | 模型选择：`sonnet`、`opus`、`haiku`，或完整名称如 `claude-sonnet-4-6` |
| `--effort <level>` | 推理深度：`low`、`medium`、`high`、`max`、`auto` | 两者 |
| `--max-turns <n>` | 限制代理式循环次数（仅限打印模式；防止失控） |
| `--max-budget-usd <n>` | 以美元为单位限制 API 花费（仅限打印模式） |
| `--fallback-model <model>` | 当默认模型过载时自动回退（仅限打印模式） |
| `--betas <betas...>` | 要包含在 API 请求中的 Beta 头信息（仅限 API 密钥用户） |

### 权限与安全
| 标志 | 作用 |
|------|--------|
| `--dangerously-skip-permissions` | 自动批准所有工具使用（文件写入、bash、网络等） |
| `--allow-dangerously-skip-permissions` | 启用绕过权限作为*选项*，但不默认启用 |
| `--permission-mode <mode>` | `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` |
| `--allowedTools <tools...>` | 白名单特定工具（逗号或空格分隔） |
| `--disallowedTools <tools...>` | 黑名单特定工具 |
| `--tools <tools...>` | 覆盖内置工具集（`""` = 无，`"default"` = 全部，或工具名称） |
### 输出与输入格式
| 标志 | 效果 |
|------|--------|
| `--output-format <fmt>` | `text`（默认）、`json`（单个结果对象）、`stream-json`（换行分隔） |
| `--input-format <fmt>` | `text`（默认）或 `stream-json`（实时流式输入） |
| `--json-schema <schema>` | 强制输出符合指定模式的 JSON |
| `--verbose` | 输出完整的逐轮对话 |
| `--include-partial-messages` | 包含到达的部分消息块（stream-json + print） |
| `--replay-user-messages` | 在 stdout 上重新发送用户消息（stream-json 双向） |

### 系统提示词与上下文
| 标志 | 效果 |
|------|--------|
| `--append-system-prompt <text>` | **追加**到默认系统提示词（保留内置功能） |
| `--append-system-prompt-file <path>` | **追加**文件内容到默认系统提示词 |
| `--system-prompt <text>` | **替换**整个系统提示词（通常使用 --append） |
| `--system-prompt-file <path>` | **替换**系统提示词为文件内容 |
| `--bare` | 跳过钩子、插件、MCP 发现、CLAUDE.md、OAuth（最快启动） |
| `--agents '<json>'` | 动态定义自定义子 Agent（JSON 格式） |
| `--mcp-config <path>` | 从 JSON 文件加载 MCP 服务器（可重复） |
| `--strict-mcp-config` | 仅使用 `--mcp-config` 指定的 MCP 服务器，忽略所有其他 MCP 配置 |
| `--settings <file-or-json>` | 从 JSON 文件或内联 JSON 加载额外设置 |
| `--setting-sources <sources>` | 逗号分隔的加载源：`user`、`project`、`local` |
| `--plugin-dir <paths...>` | 仅为此会话从目录加载插件 |
| `--disable-slash-commands` | 禁用所有技能/斜杠命令 |

### 调试
| 标志 | 效果 |
|------|--------|
| `-d, --debug [filter]` | 启用调试日志，可选类别过滤器（例如 `"api,hooks"`、`"!1p,!file"`） |
| `--debug-file <path>` | 将调试日志写入文件（隐式启用调试模式） |

### Agent 团队
| 标志 | 效果 |
|------|--------|
| `--teammate-mode <mode>` | Agent 团队显示方式：`auto`、`in-process` 或 `tmux` |
| `--brief` | 启用 `SendUserMessage` 工具用于 Agent 与用户通信 |

### --allowedTools / --disallowedTools 的工具名称语法
```
Read                    # 所有文件读取
Edit                    # 文件编辑（现有文件）
Write                   # 文件创建（新文件）
Bash                    # 所有 shell 命令
Bash(git *)             # 仅 git 命令
Bash(git commit *)      # 仅 git commit 命令
Bash(npm run lint:*)    # 通配符模式匹配
WebSearch               # 网络搜索能力
WebFetch                # 网页抓取
mcp__<server>__<tool>   # 特定 MCP 工具
```

## 设置与配置

### 设置层级（优先级从高到低）
1. **CLI 标志** — 覆盖所有设置
2. **本地项目：** `.claude/settings.local.json`（个人，gitignored）
3. **项目：** `.claude/settings.json`（共享，git-tracked）
4. **用户：** `~/.claude/settings.json`（全局）

### 设置中的权限
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### 记忆文件（CLAUDE.md）层级
1. **全局：** `~/.claude/CLAUDE.md` — 适用于所有项目
2. **项目：** `./CLAUDE.md` — 项目特定上下文（git-tracked）
3. **本地：** `.claude/CLAUDE.local.md` — 个人项目覆盖（gitignored）

在交互模式下使用 `#` 前缀快速添加到记忆：`# 始终使用 2 空格缩进`。

## 交互式会话：斜杠命令

### 会话与上下文
| 命令 | 用途 |
|---------|---------|
| `/help` | 显示所有命令（包括自定义和 MCP 命令） |
| `/compact [focus]` | 压缩上下文以节省 Token；CLAUDE.md 在压缩后保留。例如：`/compact focus on auth logic` |
| `/clear` | 清空对话历史，重新开始 |
| `/context` | 以彩色网格可视化上下文使用情况，并提供优化建议 |
| `/cost` | 查看 Token 使用情况，按模型和缓存命中率细分 |
| `/resume` | 切换到或恢复另一个会话 |
| `/rewind` | 回退到对话或代码中的先前检查点 |
| `/btw <question>` | 提出一个附带问题，不计入上下文成本 |
| `/status` | 显示版本、连接性和会话信息 |
| `/todos` | 列出对话中跟踪的待办事项 |
| `/exit` 或 `Ctrl+D` | 结束会话 |

### 开发与审查
| 命令 | 用途 |
|---------|---------|
| `/review` | 请求对当前更改进行代码审查 |
| `/security-review` | 对当前更改执行安全分析 |
| `/plan [description]` | 进入计划模式，自动开始任务规划 |
| `/loop [interval]` | 在会话内安排重复任务 |
| `/batch` | 为大型并行更改自动创建工作树（5-30 个工作树） |

### 配置与工具
| 命令 | 用途 |
|---------|---------|
| `/model [model]` | 在会话中切换模型（使用方向键调整推理力度） |
| `/effort [level]` | 设置推理力度：`low`、`medium`、`high`、`max` 或 `auto` |
| `/init` | 为项目记忆创建 CLAUDE.md 文件 |
| `/memory` | 打开 CLAUDE.md 进行编辑 |
| `/config` | 打开交互式设置配置 |
| `/permissions` | 查看/更新工具权限 |
| `/agents` | 管理专门的子 Agent |
| `/mcp` | 管理 MCP 服务器的交互式 UI |
| `/add-dir` | 添加额外的工作目录（适用于 monorepo） |
| `/usage` | 显示计划限制和速率限制状态 |
| `/voice` | 启用按住说话语音模式（20 种语言；按住空格键录音，松开发送） |
| `/release-notes` | 版本发布说明的交互式选择器 |

### 自定义斜杠命令
创建 `.claude/commands/<name>.md`（项目共享）或 `~/.claude/commands/<name>.md`（个人）：

```markdown
# .claude/commands/deploy.md
运行部署流水线：
1. 运行所有测试
2. 构建 Docker 镜像
3. 推送到注册表
4. 更新 $ARGUMENTS 环境（默认：staging）
```
用法：`/deploy production` — `$ARGUMENTS` 会被替换为用户输入。

### 技能（自然语言调用）
与斜杠命令（手动调用）不同，`.claude/skills/` 目录下的技能是 Markdown 指南，当任务匹配时，Claude 会自动通过自然语言调用它们：

```markdown
# .claude/skills/database-migration.md
当被要求创建或修改数据库迁移时：
1. 使用 Alembic 生成迁移
2. 始终创建回滚函数
3. 针对本地数据库副本测试迁移
```

## 交互式会话：键盘快捷键

### 通用控制
| 按键 | 操作 |
|-----|--------|
| `Ctrl+C` | 取消当前输入或生成 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+R` | 反向搜索命令历史 |
| `Ctrl+B` | 将运行中的任务置于后台 |
| `Ctrl+V` | 将图片粘贴到对话中 |
| `Ctrl+O` | 转录模式 — 查看 Claude 的思考过程 |
| `Ctrl+G` 或 `Ctrl+X Ctrl+E` | 在外部编辑器中打开提示词 |
| `Esc Esc` | 回滚对话或代码状态 / 总结 |

### 模式切换
| 按键 | 操作 |
|-----|--------|
| `Shift+Tab` | 循环切换权限模式（普通 → 自动接受 → 计划） |
| `Alt+P` | 切换模型 |
| `Alt+T` | 切换思考模式 |
| `Alt+O` | 切换快速模式 |

### 多行输入
| 按键 | 操作 |
|-----|--------|
| `\` + `Enter` | 快速换行 |
| `Shift+Enter` | 换行（替代方式） |
| `Ctrl+J` | 换行（替代方式） |

### 输入前缀
| 前缀 | 操作 |
|--------|--------|
| `!` | 直接执行 bash，绕过 AI（例如 `!npm test`）。单独使用 `!` 可切换 shell 模式。 |
| `@` | 引用文件/目录并自动补全（例如 `@./src/api/`） |
| `#` | 快速添加到 CLAUDE.md 记忆（例如 `# 使用 2 空格缩进`） |
| `/` | 斜杠命令 |

### 专业提示："ultrathink"
在提示词中使用关键词 "ultrathink"，以在特定轮次中启用最大推理努力。无论当前的 `/effort` 设置如何，这都会触发最深的思考模式。

## PR 审查模式

### 快速审查（打印模式）
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

### 深度审查（交互式 + 工作树）
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # 信任对话框
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

### 根据编号进行 PR 审查
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### 使用 tmux 的 Claude 工作树
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
在 `.claude/worktrees/feature-x` 创建一个隔离的 git 工作树，并为其创建一个 tmux 会话。如果可用，则使用 iTerm2 原生窗格；添加 `--tmux=classic` 以使用传统的 tmux。

## 并行 Claude 实例

同时运行多个独立的 Claude 任务：

```
# 任务 1：修复后端
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# 任务 2：编写测试
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# 任务 3：更新文档
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# 监控所有任务
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## CLAUDE.md — 项目上下文文件

Claude Code 会自动从项目根目录加载 `CLAUDE.md`。用它来持久化项目上下文：

```markdown
# 项目：我的 API

## 架构
- 使用 SQLAlchemy ORM 的 FastAPI 后端
- PostgreSQL 数据库，Redis 缓存
- 使用 pytest 进行测试，目标覆盖率 90%

## 关键命令
- `make test` — 运行完整测试套件
- `make lint` — ruff + mypy
- `make dev` — 在 :8000 端口启动开发服务器

## 代码标准
- 所有公共函数都使用类型提示
- 使用 Google 风格的文档字符串
- YAML 使用 2 空格缩进，Python 使用 4 空格缩进
- 不使用通配符导入
```

**要具体。** 与其说"编写好代码"，不如说"JS 使用 2 空格缩进"或"测试文件后缀使用 `.test.ts`"。具体的指令可以节省修正周期。

### 规则目录（模块化的 CLAUDE.md）
对于有很多规则的项目，使用规则目录，而不是一个庞大的 CLAUDE.md：
- **项目规则：** `.claude/rules/*.md` — 团队共享，git 跟踪
- **用户规则：** `~/.claude/rules/*.md` — 个人，全局

规则目录中的每个 `.md` 文件都会作为额外的上下文加载。这比把所有内容都塞进一个 CLAUDE.md 文件更清晰。

### 自动记忆
Claude 会自动将学到的项目上下文存储在 `~/.claude/projects/<project>/memory/`。
- **限制：** 每个项目 25KB 或 200 行
- 这与 CLAUDE.md 是分开的 — 这是 Claude 自己在跨会话中积累的关于项目的笔记

## 自定义子 Agent

在 `.claude/agents/`（项目）、`~/.claude/agents/`（个人）或通过 `--agents` CLI 标志（会话）中定义专门的 Agent：

### Agent 位置优先级
1. `.claude/agents/` — 项目级别，团队共享
2. `--agents` CLI 标志 — 会话特定，动态
3. `~/.claude/agents/` — 用户级别，个人

### 创建 Agent
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
你是一名资深安全工程师。审查代码中的以下问题：
- 注入漏洞（SQL、XSS、命令注入）
- 认证/授权缺陷
- 代码中的密钥
- 不安全的反序列化
```
通过以下方式调用：`@security-reviewer review the auth module`

### 通过 CLI 动态创建 Agent
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude 可以编排多个 Agent："使用 @db-expert 来优化查询，然后使用 @security 来审计更改。"

## 钩子 — 基于事件的自动化

在 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（全局）中配置：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### 全部 8 种钩子类型
| 钩子 | 触发时机 | 常见用途 |
|------|--------------|------------|
| `UserPromptSubmit` | 在 Claude 处理用户提示词之前 | 输入验证、日志记录 |
| `PreToolUse` | 在工具执行之前 | 安全门禁、阻止危险命令（exit 2 = 阻止） |
| `PostToolUse` | 在工具执行完成后 | 自动格式化代码、运行 linter |
| `Notification` | 在权限请求或等待输入时 | 桌面通知、警报 |
| `Stop` | 当 Claude 完成一个响应时 | 完成日志记录、状态更新 |
| `SubagentStop` | 当子 Agent 完成时 | Agent 编排 |
| `PreCompact` | 在上下文记忆被清除之前 | 备份会话记录 |
| `SessionStart` | 当会话开始时 | 加载开发上下文（例如，`git status`） |

### 钩子环境变量
| 变量 | 内容 |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | 当前项目路径 |
| `CLAUDE_FILE_PATHS` | 正在被修改的文件 |
| `CLAUDE_TOOL_INPUT` | 工具参数（JSON 格式） |

### 安全钩子示例
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP 集成

为数据库、API 和服务添加外部工具服务器：

```
# GitHub 集成
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL 查询
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer 用于网页测试
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP 作用域
| 标志 | 作用域 | 存储位置 |
|------|-------|---------|
| `-s user` | 全局（所有项目） | `~/.claude.json` |
| `-s local` | 此项目（个人） | `.claude/settings.local.json`（被 git 忽略） |
| `-s project` | 此项目（团队共享） | `.claude/settings.json`（被 git 跟踪） |

### 打印/CI 模式下的 MCP
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` 会忽略所有 MCP 服务器，除了来自 `--mcp-config` 的服务器。

在聊天中引用 MCP 资源：`@github:issue://123`

### MCP 限制与调优
- **工具描述：** 每个服务器的工具描述和服务器指令上限为 2KB
- **结果大小：** 默认有上限；使用 `maxResultSizeChars` 注解允许最多 **500K** 字符用于大输出
- **输出 Token：** `export MAX_MCP_OUTPUT_TOKENS=50000` — 限制 MCP 服务器的输出，防止上下文溢出
- **传输方式：** `stdio`（本地进程）、`http`（远程）、`sse`（服务器发送事件）

## 监控交互式会话

### 读取 TUI 状态
```
# 定期捕获以检查 Claude 是否仍在工作或等待输入
terminal(command="tmux capture-pane -t dev -p -S -10")
```

寻找以下指示器：
- 底部的 `❯` = 等待你的输入（Claude 已完成或正在提问）
- `●` 行 = Claude 正在主动使用工具（读取、写入、运行命令）
- `⏵⏵ bypass permissions on` = 状态栏显示权限模式
- `◐ medium · /effort` = 状态栏中当前的努力级别
- `ctrl+o to expand` = 工具输出被截断（可以交互式展开）

### 上下文窗口健康度
在交互模式下使用 `/context` 查看上下文使用情况的彩色网格。关键阈值：
- **&lt; 70%** — 正常操作，完全精度
- **70-85%** — 精度开始下降，考虑使用 `/compact`
- **> 85%** — 幻觉风险显著增加，使用 `/compact` 或 `/clear`

## 环境变量

| 变量 | 效果 |
|----------|--------|
| `ANTHROPIC_API_KEY` | 用于身份验证的 API 密钥（OAuth 的替代方案） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 默认努力级别：`low`、`medium`、`high`、`max` 或 `auto` |
| `MAX_THINKING_TOKENS` | 限制思考 Token（设置为 `0` 以完全禁用思考） |
| `MAX_MCP_OUTPUT_TOKENS` | 限制 MCP 服务器的输出（默认值可变；例如设置为 `50000`） |
| `CLAUDE_CODE_NO_FLICKER=1` | 启用备用屏幕渲染以消除终端闪烁 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 从子进程中剥离凭据以确保安全 |

## 成本与性能提示

1.  **使用 `--max-turns`** 在打印模式中防止无限循环。对于大多数任务，从 5-10 开始。
2.  **使用 `--max-budget-usd`** 进行成本上限控制。注意：系统提示词缓存创建的最低成本约为 0.05 美元。
3.  **使用 `--effort low`** 处理简单任务（更快、更便宜）。对于复杂推理，使用 `high` 或 `max`。
4.  **使用 `--bare`** 用于 CI/脚本，以跳过插件/钩子发现的开销。
5.  **使用 `--allowedTools`** 限制为仅需要的工具（例如，对于代码审查，仅允许 `Read`）。
6.  **在交互式会话中，当上下文变大时使用 `/compact`**。
7.  **当只需要分析已知内容时，使用管道输入**，而不是让 Claude 读取文件。
8.  **使用 `--model haiku`** 处理简单任务（更便宜），使用 `--model opus` 处理复杂的多步骤工作。
9.  **在打印模式中使用 `--fallback-model haiku`**，以优雅地处理模型过载。
10. **为不同的任务启动新会话** — 会话持续 5 小时；新的上下文更高效。
11. **在 CI 中使用 `--no-session-persistence`**，以避免在磁盘上累积已保存的会话。
## 注意事项与常见问题

1. **交互模式必须使用 tmux** — Claude Code 是一个完整的 TUI 应用。虽然在 Hermes 终端中单独使用 `pty=true` 可以工作，但 tmux 提供了用于监控的 `capture-pane` 和用于输入的 `send-keys`，这对于编排至关重要。
2. **`--dangerously-skip-permissions` 对话框默认选择 "No, exit"** — 你必须按向下键然后按回车键才能接受。打印模式 (`-p`) 会完全跳过此对话框。
3. **`--max-budget-usd` 最低约为 $0.05** — 仅创建系统提示词缓存就需要这么多成本。设置更低的值会立即报错。
4. **`--max-turns` 仅适用于打印模式** — 在交互式会话中会被忽略。
5. **Claude 可能使用 `python` 而不是 `python3`** — 在没有 `python` 符号链接的系统上，Claude 的 bash 命令第一次尝试会失败，但会自我纠正。
6. **恢复会话需要相同的目录** — `--continue` 会查找当前工作目录下最近的会话。
7. **`--json-schema` 需要足够的 `--max-turns`** — Claude 必须在生成结构化输出之前读取文件，这需要多个回合。
8. **信任对话框每个目录只出现一次** — 仅首次出现，之后会被缓存。
9. **后台 tmux 会话会持续存在** — 完成后务必使用 `tmux kill-session -t <name>` 进行清理。
10. **斜杠命令（如 `/commit`）仅在交互模式下有效** — 在 `-p` 模式下，请用自然语言描述任务。
11. **`--bare` 跳过 OAuth** — 需要设置 `ANTHROPIC_API_KEY` 环境变量或在设置中配置 `apiKeyHelper`。
12. **上下文退化是真实存在的** — 当上下文窗口使用率超过 70% 时，AI 输出质量会明显下降。使用 `/context` 进行监控，并主动使用 `/compact`。

## Hermes Agent 规则

1. **对于单一任务，优先使用打印模式 (`-p`)** — 更简洁，无需处理对话框，输出结构化
2. **对于多回合交互式工作，使用 tmux** — 这是编排 TUI 的唯一可靠方式
3. **始终设置 `workdir`** — 让 Claude 专注于正确的项目目录
4. **在打印模式下设置 `--max-turns`** — 防止无限循环和成本失控
5. **监控 tmux 会话** — 使用 `tmux capture-pane -t <session> -p -S -50` 检查进度
6. **寻找 `❯` 提示符** — 表示 Claude 正在等待输入（已完成或正在提问）
7. **清理 tmux 会话** — 完成后将其终止，避免资源泄漏
8. **向用户报告结果** — 完成后，总结 Claude 做了什么以及发生了哪些变化
9. **不要终止缓慢的会话** — Claude 可能正在进行多步骤工作；请检查进度
10. **使用 `--allowedTools`** — 将能力限制在任务实际需要的范围内