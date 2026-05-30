---
title: "Antigravity Cli — 操作 Antigravity CLI (agy)：插件、认证、沙盒"
sidebar_label: "Antigravity Cli"
description: "操作 Antigravity CLI (agy)：插件、认证、沙盒"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Antigravity Cli

操作 Antigravity CLI (agy)：插件、认证、沙盒。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/antigravity-cli` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/antigravity-cli` |
| 版本 | `0.1.0` |
| 作者 | Tony Simons (asimons81), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Antigravity`, `CLI`, `Auth`, `Plugins`, `Sandbox` |
| 相关技能 | [`grok`](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Antigravity CLI (`agy`)

Antigravity CLI 的操作指南，通过 `agy` 调用。所有 `agy` 命令都通过 Hermes 的 `terminal` 工具运行；使用 `read_file` 检查其配置和日志。此技能是参考 + 流程说明 — 它不包装网络 API，因此 Hermes 本身无需进行认证。

## 使用时机

- 安装、更新或冒烟测试 `agy` 二进制文件
- 驱动非交互式的 `agy --print` / `agy -p` 一次性任务
- 调试 Antigravity 认证、沙盒、权限或插件状态
- 读取 Antigravity 设置、快捷键绑定、会话或日志

## 心智模型

Antigravity 有两层 — 请区分它们，否则指导会出错：

1.  **Shell 包装器命令** — `agy help`, `agy install`, `agy plugin`, `agy update`, `agy changelog`。通过 `terminal` 工具运行这些命令。
2.  **交互式会话内斜杠命令** — `/config`, `/permissions`, `/skills`, `/agents` 等。这些仅存在于运行的 `agy` TUI 会话内部，而非 shell 包装器上。

`agy help` 显示的是 shell 包装器的表面命令，**不是**会话内的斜杠命令。

## 先决条件

-   `agy` 二进制文件在 PATH 中。通过 `terminal` 工具验证：`command -v agy && agy --version`。
-   此技能不需要环境变量或 API 密钥 — Antigravity 通过操作系统密钥环 / 浏览器登录管理其自身的认证（见下文认证部分）。

## 如何运行

通过 `terminal` 工具调用每个 `agy` 命令。示例：

```
terminal(command="agy --version")
terminal(command="agy help")
terminal(command="agy plugin list")
terminal(command="agy --print 'Summarize the repo in 3 bullets'", workdir="/path/to/project")
```

对于交互式多轮 TUI 会话，使用 `pty=true`（以及 tmux 用于捕获/监控）启动 `agy`，与 `codex` / `claude-code` 技能使用的模式相同。对于一次性冒烟测试和脚本化提示词，优先使用 `agy --print`（非交互式）。

要检查 Antigravity 自身的文件，请对下文“核心路径”下的路径使用 `read_file` — 不要通过终端使用 `cat` 命令。

## 核心路径

-   二进制文件 / 入口点：`agy`
-   应用数据目录：`~/.gemini/antigravity-cli/`
-   设置文件：`~/.gemini/antigravity-cli/settings.json`
-   快捷键绑定文件：`~/.gemini/antigravity-cli/keybindings.json`
-   日志：`~/.gemini/antigravity-cli/log/cli-*.log`
-   会话：`~/.gemini/antigravity-cli/conversations/`
-   大脑产物：`~/.gemini/antigravity-cli/brain/`
-   历史记录：`~/.gemini/antigravity-cli/history.jsonl`
-   插件暂存区：`~/.gemini/antigravity-cli/plugins/<plugin_name>/`

## 快速参考

### 包装器命令
- `agy changelog`
- `agy help`
- `agy install`
- `agy plugin` / `agy plugins`
- `agy update`

### 常用标志
- `--add-dir`
- `--continue` / `-c`
- `--conversation`
- `--dangerously-skip-permissions`
- `--print` / `-p`
- `--print-timeout`
- `--prompt`
- `--prompt-interactive` / `-i`
- `--sandbox`
- `--log-file`
- `--version`

### 插件子命令 (`agy plugin --help`)
- `list`, `import [source]`, `install <target>`, `uninstall <name>`, `enable <name>`, `disable <name>`, `validate [path]`, `link <mp> <target>`, `help`

### 安装标志 (`agy install --help`)
- `--dir`, `--skip-aliases`, `--skip-path`

### 会话内斜杠命令
-   **会话控制：** `/resume` (`/switch`), `/rewind` (`/undo`), `/rename <name>`, `/clear`, `/fork`, `/reset`, `/new`
-   **设置与工具：** `/config`, `/settings`, `/permissions`, `/model`, `/keybindings`, `/statusline`, `/tasks`, `/skills`, `/mcp`, `/open <path>`, `/usage`, `/logout`, `/agents`
-   **提示词助手：** `@` 路径自动补全，`esc esc` 清除提示词（非流式输出时），`!` 直接运行终端命令，`?` 打开帮助

## 设置和权限

### 常用设置键 (`settings.json`)
- `allowNonWorkspaceAccess`
- `colorScheme`
- `permissions.allow`
- `trustedWorkspaces`

### 权限模式
`request-review`, `always-proceed`, `strict`, `proceed-in-sandbox`.

### 沙盒行为
- `enableTerminalSandbox` 是 `settings.json` 中的一个布尔值；默认为 `false`。
-   启动时覆盖项（`--sandbox`, `--dangerously-skip-permissions`）可以为当前会话覆盖持久化设置。

## 认证行为

-   CLI 首先尝试操作系统安全密钥环。
-   如果没有保存的会话，则回退到基于浏览器的 Google 登录。
-   本地会打开默认浏览器；通过 SSH 时，它会打印一个授权 URL 并期望粘贴回授权码。
-   `/logout` 会移除保存的凭据。

## 插件

-   插件暂存在 `~/.gemini/antigravity-cli/plugins/<plugin_name>/` 下。
-   它们可以捆绑技能、Agent、规则、MCP 服务器和钩子。
-   `agy plugin list` 返回没有导入的插件是有效的空状态。

## 常见陷阱

-   `agy help` 显示的是包装器命令，而非交互式斜杠命令。
-   `agy --version` 是安全的非交互式版本检查；`agy version` 是交互式的，没有真实的 TTY 可能会失败。
-   查找故障的首选位置：`~/.gemini/antigravity-cli/log/cli-*.log`（使用 `read_file` 读取）。
-   不要混淆持久化的 JSON 设置与启动时覆盖项。
-   `~/.gemini/antigravity-cli/bin/agentapi` 是 `agy agentapi` 的一个薄包装器。
-   在 WSL 上，Token 存储是基于文件的，因此认证问题通常是本地文件 / 会话状态问题，而非仅浏览器问题。
-   工作空间标识可能取决于启动目录和 `.antigravitycli` 项目标记。

## 验证

确认安装真实且可用，全部通过 `terminal` 工具完成（使用 `read_file` 读取文件）：

1.  `terminal(command="command -v agy")`
2.  `terminal(command="agy --version")`
3.  `terminal(command="agy help")`
4.  `terminal(command="agy plugin list")`
5.  `read_file` 读取 `~/.gemini/antigravity-cli/settings.json`
6.  `read_file` 读取最新的 `~/.gemini/antigravity-cli/log/cli-*.log`
7.  如果需要，`read_file` 读取 `~/.gemini/antigravity-cli/keybindings.json`

## 支持文件

-   `references/cli-docs.md` — 来自入门指南、使用方法和功能文档的浓缩笔记。