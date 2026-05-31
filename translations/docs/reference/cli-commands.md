---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考

本页面涵盖从 shell 运行的**终端命令**。

关于聊天内的斜杠命令，请参阅[斜杠命令参考](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile <name>`, `-p <name>` | 选择本次调用使用的 Hermes 配置文件。覆盖由 `hermes profile use` 设置的粘性默认值。 |
| `--resume <session>`, `-r <session>` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或恢复标题匹配的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git 工作树中启动，用于并行 Agent 工作流。 |
| `--yolo` | 绕过危险命令的确认提示。 |
| `--pass-session-id` | 在 Agent 的系统提示词中包含会话 ID。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 并回退到内置默认值。`.env` 中的凭据仍会被加载。 |
| `--ignore-rules` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能的自动注入。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等同于 `HERMES_TUI=1`。 |
| `--dev` | 与 `--tui` 一起使用：通过 `tsx` 直接运行 TypeScript 源代码，而非预构建的包（供 TUI 贡献者使用）。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes fallback` | 管理当主模型出错时尝试的备用提供商。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes proxy` | 本地 OpenAI 兼容代理，用于附加 OAuth 提供商凭据。参见[订阅代理](../user-guide/features/subscription-proxy.md)。 |
| `hermes lsp` | 管理语言服务器协议集成（用于 write_file/patch 的语义诊断）。 |
| `hermes setup` | 全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置和配对 WhatsApp 桥接。 |
| `hermes slack` | Slack 助手（当前：生成包含每个命令作为原生斜杠命令的应用清单）。 |
| `hermes auth` | 管理凭据 — 添加、列出、移除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** — 请改用 `hermes auth`。 |
| `hermes send` | 向已配置的消息平台（Telegram、Discord、Slack、Signal、SMS、…）发送一次性消息。适用于 shell 脚本、定时任务、CI 钩子和监控守护进程 — 无 Agent 循环，无 LLM。 |
| `hermes secrets` | 管理外部密钥源（当前为 Bitwarden Secrets Manager），用于在进程启动时拉取 API 密钥，而非从 `~/.hermes/.env` 读取。 |
| `hermes migrate` | 诊断并（可选）重写 `config.yaml` 以替换对已停用模型或已弃用设置的引用（例如 `migrate xai`）。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查和触发定时任务调度器。 |
| `hermes kanban` | 多配置文件协作看板（任务、链接、调度器）。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 Webhook 订阅。 |
| `hermes hooks` | 检查、批准或移除在 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes security audit` | 按需对 venv、插件需求和固定的 MCP 服务器进行供应链审计（OSV.dev）。 |
| `hermes dump` | 用于支持/调试的可复制粘贴的设置摘要。 |
| `hermes prompt-size` | 显示系统提示词 + 工具模式（技能索引、记忆、配置文件）的字节细分。离线运行。 |
| `hermes debug` | 调试工具 — 为支持目的上传日志和系统信息。 |
| `hermes backup` | 将 Hermes 主目录备份到 zip 文件。 |
| `hermes checkpoints` | 检查 / 清理 / 清除 `~/.hermes/checkpoints/`（由 `/rollback` 使用的影子存储）。不带参数运行以获取状态概览。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes bundles` | 将多个技能分组到单个 `/<name>` 斜杠命令下。参见[技能包](../user-guide/features/skills.md#skill-bundles)。 |
| `hermes curator` | 后台技能维护 — 状态、运行、暂停、固定。参见[策展人](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部记忆提供商。插件特定的子命令（例如 `hermes honcho`）在其提供商激活时会自动注册。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行以进行编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes portal` | Nous Portal 状态、订阅链接和工具网关路由。参见[工具网关](../user-guide/features/tool-gateway.md)。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes computer-use` | 安装或检查 cua-driver 后端（macOS 计算机使用）。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 Token/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移助手。 |
| `hermes dashboard` | 启动用于管理配置、API 密钥和会话的 Web 仪表板。 |
| `hermes profile` | 管理配置文件 — 多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖项（git 安装），或检查 PyPI 并执行 `pip install --upgrade`（pip 安装）。`--check` 预览而不安装；`--backup` 在拉取前创建 `HERMES_HOME` 快照。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |
## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|--------|-------------|
| `-q`, `--query "..."` | 单次、非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用逗号分隔的工具集。 |
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`google-gemini-cli`、`huggingface`、`novita`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`xai-oauth`（别名 `grok-oauth`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`azure-foundry`、`lmstudio`、`stepfun`、`tencent-tokenhub`（别名 `tencent`、`tokenhub`）。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：抑制横幅/旋转器/工具预览。 |
| `--image <path>` | 为单次查询附加本地图片。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复一个会话。 |
| `--worktree` | 为此运行创建一个隔离的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传递到系统提示词中。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 并使用内置默认值。`.env` 中的凭据仍会被加载。适用于隔离的 CI 运行、可复现的错误报告和第三方集成。 |
| `--ignore-rules` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、持久记忆和预加载技能的自动注入。与 `--ignore-user-config` 结合使用可实现完全隔离的运行。 |
| `--source <tag>` | 用于过滤的会话来源标签（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，使用 `tool`。 |
| `--max-turns <N>` | 每次对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
hermes chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
```

### `hermes -z <prompt>` — 脚本化单次运行

对于编程调用者（shell 脚本、CI、定时任务、父进程通过管道输入提示词），`hermes -z` 是最纯粹的单次运行入口点：**单次提示词输入，最终响应文本输出，stdout 或 stderr 上不输出任何其他内容。** 没有横幅，没有旋转器，没有工具预览，没有 `Session:` 行——只有 Agent 的最终回复作为纯文本。

```bash
hermes -z "What's the capital of France?"
# → Paris.

# 父脚本可以干净地捕获响应：
answer=$(hermes -z "summarize this" < /path/to/file.txt)
```

每次运行的覆盖选项（不修改 `~/.hermes/config.yaml`）：

| 标志 | 等效环境变量 | 用途 |
|---|---|---|
| `-m` / `--model <model>` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider <provider>` | _(无)_ | 覆盖本次运行的提供商 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# 或：
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的 Agent，相同的工具，相同的技能——只是去掉了所有交互/装饰层。如果你也需要工具输出在记录中，请改用 `hermes chat -q`；`-z` 明确用于“我只想要最终答案”。

## `hermes model`

交互式提供商 + 模型选择器。**此命令用于添加新提供商、设置 API 密钥和运行 OAuth 流程。** 从你的终端运行它——而不是从活跃的 Hermes 聊天会话内部。

```bash
hermes model
```

在以下情况下使用此命令：
- **添加新提供商**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录支持 OAuth 的提供商（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新默认值保存到配置中

:::warning hermes model 与 /model — 了解区别
**`hermes model`**（从你的终端运行，在任何 Hermes 会话之外）是**完整的提供商设置向导**。它可以添加新提供商、运行 OAuth 流程、提示输入 API 密钥和配置端点。

**`/model`**（在活跃的 Hermes 聊天会话中键入）只能**在你已设置的提供商和模型之间切换**。它不能添加新提供商、运行 OAuth 或提示输入 API 密钥。

**如果你需要添加新提供商：** 首先退出你的 Hermes 会话（`Ctrl+C` 或 `/quit`），然后从你的终端提示符运行 `hermes model`。
:::

### `/model` 斜杠命令（会话中）

在不离开会话的情况下在已配置的模型之间切换：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在你的自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

默认情况下，`/model` 的更改**仅应用于当前会话**。添加 `--global` 以将更改持久化到 `config.yaml`：

```
/model claude-sonnet-4 --global     # 切换并保存为新的默认值
```

:::info 如果我只能看到 OpenRouter 模型怎么办？
如果你只配置了 OpenRouter，`/model` 将只显示 OpenRouter 模型。要添加其他提供商（Anthropic、DeepSeek、Copilot 等），请退出你的会话并从终端运行 `hermes model`。
:::
提供商和基础 URL 的更改会自动持久化到 `config.yaml`。当切换离开自定义端点时，过时的基础 URL 会被清除，以防止其泄漏到其他提供商。

## `hermes gateway`

```bash
hermes gateway <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `run` | 在前台运行消息网关。推荐用于 WSL、Docker 和 Termux。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止服务（或前台进程）。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `list` | 列出**所有配置文件**以及每个配置文件的消息网关当前是否正在运行（如果可用，会显示 PID）。当您并行运行多个配置文件并希望获得一个概览时非常方便。 |
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--all` | 在 `start` / `restart` / `stop` 操作时：作用于**每个配置文件**的消息网关，而不仅仅是活动的 `HERMES_HOME`。如果您并行运行多个配置文件，并希望在 `hermes update` 后重启所有网关，这很有用。 |
| `--no-supervise` | 在 `run` 操作时：在 s6-overlay Docker 镜像内部，选择退出自动监管，使用 pre-s6 前台语义——消息网关作为容器的主进程运行，没有自动重启。在 s6 镜像外部无效。相当于设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。 |

:::tip WSL 用户
使用 `hermes gateway run` 而不是 `hermes gateway start` —— WSL 的 systemd 支持不可靠。可以将其包装在 tmux 中以实现持久化：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes lsp`

```bash
hermes lsp <子命令>
```

管理语言服务器协议集成。LSP 在后台运行真正的语言服务器（pyright、gopls、rust-analyzer 等），并将其诊断信息提供给 `write_file` 和 `patch` 使用的写入后检查。此功能受 git 工作区检测限制——仅当当前工作目录或编辑的文件位于 git 工作树内时，LSP 才会运行。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示服务状态、配置的服务器、安装状态。 |
| `list` | 打印支持的服务器注册表。传递 `--installed-only` 以跳过缺失的服务器。 |
| `install <id>` | 主动安装一个服务器的二进制文件。 |
| `install-all` | 安装每个具有已知自动安装方法的服务器。 |
| `restart` | 关闭正在运行的客户端，以便下次编辑时重新启动。 |
| `which <id>` | 打印一个服务器的解析后的二进制路径。 |

完整指南、支持的语言和配置选项，请参阅 [LSP — 语义诊断](/user-guide/features/lsp)。

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure] [--portal]
```

**最简单路径：** `hermes setup --portal` —— 通过 OAuth 登录 Nous Portal 并一键启用 [工具网关](../user-guide/features/tool-gateway.md)。

**首次运行：** 启动首次使用向导。

**返回用户（已配置）：** 直接进入完整的重新配置向导——每个提示都显示您当前的值为其默认值，按 Enter 键保留或输入新值。没有菜单。

跳转到某个部分，而不是完整的向导：

| 部分 | 描述 |
|---------|-------------|
| `model` | 提供商和模型设置。 |
| `terminal` | 终端后端和沙盒设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | Agent 行为设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--quick` | 针对返回用户运行：仅提示缺失或未设置的项。跳过您已配置的项。 |
| `--non-interactive` | 使用默认值/环境变量值，无需提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |
| `--reconfigure` | 向后兼容的别名——在现有安装上运行不带参数的 `hermes setup` 现在默认执行此操作。 |
| `--portal` | 一键式 Nous Portal 设置：通过 OAuth 登录，将 Nous 设置为推理提供商，并启用 [工具网关](../user-guide/features/tool-gateway.md)。跳过向导的其余部分。 |

## `hermes portal`

```bash
hermes portal [status|open|tools]
```

检查 Nous Portal 认证、工具网关路由，并访问订阅页面。不带子命令的调用运行 `status`。

| 子命令 | 描述 |
|------------|-------------|
| `status`（默认） | Portal 认证状态 + 每个工具的工具网关路由摘要。当未给出子命令时也会显示。 |
| `open` | 在默认浏览器中打开 `portal.nousresearch.com/manage-subscription`。 |
| `tools` | 列出每个工具网关合作伙伴（Firecrawl、FAL、OpenAI TTS、Browser Use、Modal）以及哪些是通过 Nous 路由的。 |

关于网关本身的配置，请参阅 [工具网关](../user-guide/features/tool-gateway.md)。关于一键设置路径，请参阅上面的 `hermes setup --portal`。

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes slack`

```bash
hermes slack manifest              # 将清单打印到 stdout
hermes slack manifest --write      # 写入 ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # 仅输出 features.slash_commands 数组
```

生成一个 Slack 应用清单，将 `COMMAND_REGISTRY` 中的每个网关命令（`/btw`、`/stop`、`/model` 等）注册为 Slack 的一级斜杠命令——与 Discord 和 Telegram 功能对等。将输出粘贴到您的 Slack 应用配置中，位置在 [https://api.slack.com/apps](https://api.slack.com/apps) → 您的应用 → **Features → App Manifest → Edit**，然后 **Save**。如果范围或斜杠命令发生更改，Slack 会提示重新安装。

| 标志 | 默认值 | 用途 |
|------|---------|---------|
| `--write [PATH]` | stdout | 写入文件而不是 stdout。单独的 `--write` 写入 `$HERMES_HOME/slack-manifest.json`。 |
| `--name NAME` | `Hermes` | Slack 中 Bot 的显示名称。 |
| `--description DESC` | 默认描述 | 在 Slack 应用目录中显示的 Bot 描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands`，用于合并到手动维护的清单中。 |
执行 `hermes update` 后，再次运行 `hermes slack manifest --write` 以获取任何新命令。

## `hermes send`

```bash
hermes send --to <target> "message text"
hermes send --to <target> --file <path>
echo "message" | hermes send --to <target>
hermes send --list [platform]
```

向已配置的消息平台发送一次性消息，无需启动 Agent 或消息网关循环。复用消息网关已配置的凭据（`~/.hermes/.env` + `~/.hermes/config.yaml`），以便运维脚本、定时任务、CI 钩子和监控守护进程可以发布状态更新，而无需重新实现每个平台的 REST 客户端。

对于使用机器人令牌的平台（Telegram、Discord、Slack、Signal、SMS、WhatsApp-CloudAPI），无需运行消息网关——`hermes send` 直接与平台的 REST 端点通信。需要持久化适配器的插件平台仍然需要运行中的消息网关。

| 选项 | 描述 |
|--------|-------------|
| `-t`, `--to <TARGET>` | 发送目标。格式：`platform`（使用主频道）、`platform:chat_id`、`platform:chat_id:thread_id` 或 `platform:#channel-name`。示例：`telegram`、`telegram:-1001234567890`、`discord:#ops`、`slack:C0123ABCD`、`signal:+15551234567`。 |
| `-f`, `--file <PATH>` | 从 `PATH` 读取消息正文。传递 `-` 以强制从 stdin 读取。 |
| `-s`, `--subject <LINE>` | 在消息正文前添加主题/标题行。 |
| `-l`, `--list [platform]` | 列出所有平台（或仅给定平台）的已配置目标。 |
| `-q`, `--quiet` | 成功时抑制 stdout 输出——在脚本中很有用（仅依赖退出码）。 |
| `--json` | 输出原始 JSON 结果，而非人类可读的输出。 |

如果既没有提供位置参数 `message` 也没有提供 `--file`，当 stdin 不是 TTY 时，`hermes send` 会从 stdin 读取。退出码：成功为 `0`，投递/后端失败为 `1`，使用错误为 `2`。

示例：

```bash
hermes send --to telegram "deploy finished"
echo "RAM 92%" | hermes send --to telegram:-1001234567890
hermes send --to discord:#ops --file /tmp/report.md
hermes send --to slack:#eng --subject "[CI]" --file build.log
hermes send --list                  # 所有平台
hermes send --list telegram         # 按平台筛选
```


## `hermes secrets`

```bash
hermes secrets bitwarden <subcommand>
hermes secrets bw <subcommand>          # 短别名
```

在进程启动时从外部密钥管理器拉取 API 密钥，而不是将它们存储在 `~/.hermes/.env` 中。目前支持 **Bitwarden Secrets Manager**。完整指南请参阅：[Bitwarden 集成](../user-guide/secrets/bitwarden.md)。

`bitwarden`（别名 `bw`）子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式向导：安装固定的 `bws` 二进制文件，存储访问令牌，并选择一个项目。接受 `--project-id`、`--access-token` 和 `--server-url` 用于非交互式使用。 |
| `status` | 显示当前配置、二进制文件路径/版本以及上次获取信息。 |
| `sync` | 立即获取密钥并报告更改内容。添加 `--apply` 以实际将密钥导出到当前 shell 的执行环境中（默认为试运行）。 |
| `install` | 下载并验证固定的 `bws` 二进制文件。`--force` 即使已存在托管副本也会重新下载。 |
| `disable` | 关闭 Bitwarden 集成。 |


## `hermes migrate`

```bash
hermes migrate <type>
```

诊断并（可选）重写活动的 `config.yaml`，以替换对已停用模型或已弃用设置的引用。在进行任何重写之前，会为原始 `config.yaml` 创建带时间戳的备份（使用 `--no-backup` 跳过）。

| 子命令 | 描述 |
|------------|-------------|
| `xai` | 扫描 `config.yaml` 中引用的计划于 2026 年 5 月 15 日停用的 xAI 模型，并（使用 `--apply`）根据 xAI 迁移指南将它们就地重写为官方替代品。默认为试运行。 |

迁移子命令的通用标志：

| 标志 | 描述 |
|------|-------------|
| `--apply` | 就地重写 `config.yaml`（默认：试运行，不写入）。 |
| `--no-backup` | 应用时跳过为 `config.yaml` 创建带时间戳的备份。 |

> 不要与 `hermes claw migrate`（将 OpenClaw 配置一次性导入 Hermes）混淆——`hermes migrate` 是顶层的配置重写命令。


## `hermes proxy`

```bash
hermes proxy <subcommand>
```

运行一个本地的 OpenAI 兼容 HTTP 服务器，将请求转发到经过 OAuth 认证的上游提供商（例如 Nous Portal、xAI）。外部应用程序可以使用任何持有者令牌指向该代理；代理在转发时附加您真实的 OAuth 凭据。完整指南请参阅：[订阅代理](../user-guide/features/subscription-proxy.md)。

| 子命令 | 描述 |
|------------|-------------|
| `start` | 在前台运行代理。标志：`--provider <nous\|xai>`（默认 `nous`）、`--host <addr>`（默认 `127.0.0.1`；使用 `0.0.0.0` 在 LAN 上公开）、`--port <int>`（默认 `8645`）。 |
| `status` | 显示哪些代理上游已就绪（凭据存在，OAuth 有效）。 |
| `providers` | 列出可用的代理上游提供商。 |


## `hermes security`

```bash
hermes security <subcommand>
```

针对 [OSV.dev](https://osv.dev) 的按需漏洞扫描。涵盖 Hermes venv（已安装的 PyPI 发行版）、`~/.hermes/plugins/` 下插件声明的 Python 依赖项以及 `config.yaml` 中固定的 `npx`/`uvx` MCP 服务器。**不**扫描全局安装的包或编辑器/浏览器扩展。

| 子命令 | 描述 |
|------------|-------------|
| `audit` | 运行一次性供应链审计。 |

`audit` 标志：

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--json` | 关闭 | 输出机器可读的 JSON，而非人类可读的文本。 |
| `--fail-on <level>` | `critical` | 当任何发现达到此严重性级别（`low`、`moderate`、`high`、`critical`）时，以非零状态退出。 |
| `--skip-venv` | 关闭 | 跳过扫描 Hermes Python venv。 |
| `--skip-plugins` | 关闭 | 跳过扫描插件的需求文件。 |
| `--skip-mcp` | 关闭 | 跳过扫描 `config.yaml` 中固定的 MCP 服务器。 |
## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭证，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth`

管理用于同提供商密钥轮换的凭证池。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有凭证池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭证
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
hermes auth status anthropic                             # 显示提供商的认证状态
hermes auth logout anthropic                             # 登出并清除存储的认证状态
hermes auth spotify                                      # 通过 PKCE 为 Hermes 认证 Spotify
```

子命令：`add`、`list`、`remove`、`reset`、`status`、`logout`、`spotify`。不带子命令调用时，将启动交互式管理向导。

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可共享的脱敏格式显示所有详细信息。 |
| `--deep` | 运行可能需要更长时间的深度检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示计划任务。 |
| `create` / `add` | 根据提示词创建计划任务，可选地通过重复的 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划、提示词、名称、交付方式、重复次数或附加技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复暂停的任务并计算其下一次未来运行时间。 |
| `run` | 在下一个调度器周期触发任务。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行一次到期的任务并退出。 |

## `hermes kanban`

```bash
hermes kanban [--board <slug>] <action> [options]
```

多配置文件、多项目协作看板。每个安装可以托管多个看板（每个项目、仓库或领域一个）；每个看板都是一个独立的队列，拥有自己的 SQLite 数据库和调度器作用域。新安装开始时有一个名为 `default` 的看板，其数据库为 `~/.hermes/kanban.db` 以保持向后兼容；其他看板位于 `~/.hermes/kanban/boards/<slug>/kanban.db`。消息网关内嵌的调度器每个周期都会扫描每个看板。

**全局标志（适用于以下所有操作）：**

| 标志 | 用途 |
|------|---------|
| `--board <slug>` | 对特定看板进行操作。默认为当前看板（通过 `hermes kanban boards switch`、`HERMES_KANBAN_BOARD` 环境变量或 `default` 设置）。 |

**这是人工/脚本操作界面。** 由调度器生成的 Agent 工作者通过专用的 `kanban_*` [工具集](/user-guide/features/kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_complete`、`kanban_block`、`kanban_create`、`kanban_link`、`kanban_comment`、`kanban_heartbeat`；编排器配置文件还拥有 `kanban_list` 和 `kanban_unblock`）来驱动看板，而不是通过 shell 调用 `hermes kanban`。工作者的环境中固定设置了 `HERMES_KANBAN_BOARD`，因此它们实际上无法看到其他看板。

| 操作 | 用途 |
|--------|---------|
| `init` | 如果缺失则创建 `kanban.db`。幂等操作。 |
| `boards list` / `boards ls` | 列出所有看板及其任务计数。`--json`、`--all`（包含已归档的）。 |
| `boards create <slug>` | 创建新看板。标志：`--name`、`--description`、`--icon`、`--color`、`--switch`（设为活动）。Slug 为 kebab-case，自动转为小写。 |
| `boards switch <slug>` / `boards use` | 将 `<slug>` 持久化为活动看板（写入 `~/.hermes/kanban/current`）。 |
| `boards show` / `boards current` | 打印当前活动看板的名称、数据库路径和任务计数。 |
| `boards rename <slug> "<name>"` | 更改看板的显示名称。Slug 不可变。 |
| `boards rm <slug>` | 归档（默认）或硬删除看板。`--delete` 跳过归档步骤。已归档的看板移动到 `boards/_archived/<slug>-<ts>/`。对 `default` 看板拒绝此操作。 |
| `create "<title>"` | 在活动看板上创建新任务。标志：`--body`、`--assignee`、`--parent`（可重复）、`--workspace scratch\|worktree\|dir:<path>`、`--tenant`、`--priority`、`--triage`、`--idempotency-key`、`--max-runtime`、`--max-retries`、`--skill`（可重复）。 |
| `list` / `ls` | 列出活动看板上的任务。使用 `--mine`、`--assignee`、`--status`、`--tenant`、`--archived`、`--json` 进行过滤。 |
| `show <id>` | 显示任务及其评论和事件。`--json` 用于机器输出。 |
| `assign <id> <profile>` | 分配或重新分配。使用 `none` 取消分配。任务运行时拒绝此操作。 |
| `link <parent> <child>` | 添加依赖关系。检测循环依赖。两个任务必须在同一看板上。 |
| `unlink <parent> <child>` | 移除依赖关系。 |
| `claim <id>` | 原子性地认领一个就绪任务。打印解析出的工作空间路径。 |
| `comment <id> "<text>"` | 追加评论。下一个认领该任务的工作者会将其作为 `kanban_show()` 响应的一部分读取。 |
| `complete <id>` | 标记任务完成。标志：`--result`、`--summary`、`--metadata`。 |
| `block <id> "<reason>"` | 标记任务因需要人工输入而阻塞。同时将原因作为评论追加。 |
| `schedule <id> "<reason>"` | 将时间延迟/后续工作放入 `scheduled` 状态，使其不显示为人工阻塞项。 |
| `unblock <id>` | 将阻塞或计划中的任务返回到就绪状态（如果依赖项仍未完成，则返回到 `todo` 状态）。 |
| `archive <id>` | 从默认列表中隐藏。`gc` 将移除临时工作空间。 |
| `tail <id>` | 跟随任务的事件流。 |
| `dispatch` | 在活动看板上进行一次调度器遍历。标志：`--dry-run`、`--max N`、`--failure-limit N`、`--json`。 |
| `context <id>` | 打印工作者将看到的完整上下文（标题 + 正文 + 父任务结果 + 评论）。 |
| `specify <id>` / `specify --all` | 通过辅助 LLM 将待处理列中的任务具体化为详细规格（标题 + 包含目标、方法、验收标准的正文），然后将其提升到 `todo` 状态。标志：`--tenant`（将 `--all` 限制在一个租户内）、`--author`、`--json`。在 `config.yaml` 的 `auxiliary.triage_specifier` 下配置模型。 |
| `decompose <id>` / `decompose --all` | 将待处理列中的任务分解为由描述路由到专家配置文件的子任务图（编排器驱动的路径）。当 LLM 认为任务无法从分解中受益时，回退到 specify 风格的单任务提升。标志与 `specify` 相同。在 `config.yaml` 的 `auxiliary.kanban_decomposer` 下配置模型。当 `kanban.auto_decompose: true`（默认）时，每个调度器周期也会自动运行。参见[自动与手动编排](/user-guide/features/kanban#auto-vs-manual-orchestration)。 |
| `gc` | 移除已归档任务的临时工作空间。 |
示例：

```bash
# 创建第二个看板并添加任务，无需切换当前看板。
hermes kanban boards create atm10-server --name "ATM10 Server" --icon 🎮
hermes kanban --board atm10-server create "Restart server" --assignee ops

# 为后续调用切换活动看板。
hermes kanban boards switch atm10-server
hermes kanban list                  # 显示 atm10-server 看板的任务

# 归档看板（可恢复）或硬删除它。
hermes kanban boards rm atm10-server
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（优先级从高到低）：`--board <slug>` 标志 → `HERMES_KANBAN_BOARD` 环境变量 → `~/.hermes/kanban/current` 文件 → `default`。

所有操作也可在消息网关中作为斜杠命令使用（`/kanban …`），具有相同的参数界面——包括 `boards` 子命令和 `--board` 标志。

关于完整设计——与 Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise 的比较、八种协作模式、四个用户故事、并发正确性证明——请参阅仓库中的 `docs/hermes-kanban-v1-spec.pdf` 或 [Kanban 用户指南](/user-guide/features/kanban)。

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动 Agent 激活的动态 Webhook 订阅。需要在配置中启用 webhook 平台——如果未配置，则打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 Webhook 路由。返回用于在你的服务上配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。来自 config.yaml 的静态路由不受影响。 |
| `test` | 发送测试 POST 请求以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 包含 `{dot.notation}` 负载引用的提示词模板。 |
| `--events` | 要接受的事件类型，逗号分隔（例如 `issues,pull_request`）。空值 = 全部。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 为 Agent 运行加载的技能名称，逗号分隔。 |
| `--deliver` | 交付目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台交付的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略则自动生成。 |
| `--deliver-only` | 跳过 Agent——将渲染后的 `--prompt` 作为字面消息交付。零 LLM 成本，亚秒级交付。要求 `--deliver` 是一个真实目标（非 `log`）。 |

订阅持久化到 `~/.hermes/webhook_subscriptions.json`，并由 webhook 适配器热重载，无需重启消息网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 在可能的情况下尝试自动修复。 |

## `hermes dump`

```bash
hermes dump [--show-keys]
```

输出整个 Hermes 设置的紧凑、纯文本摘要。设计用于在请求支持时复制粘贴到 Discord、GitHub issues 或 Telegram 中——无 ANSI 颜色，无特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏后的 API 密钥前缀（前 4 个和后 4 个字符），而不仅仅是 `set`/`not set`。 |

### 包含的内容

| 部分 | 详情 |
|---------|---------|
| **头部** | Hermes 版本、发布日期、git 提交哈希 |
| **环境** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **身份** | 活动配置文件名称、HERMES_HOME 路径 |
| **模型** | 配置的默认模型和提供商 |
| **终端** | 后端类型（local、docker、ssh 等） |
| **API 密钥** | 所有 22 个提供商/工具 API 密钥的存在性检查 |
| **功能** | 启用的工具集、MCP 服务器数量、记忆提供商 |
| **服务** | 消息网关状态、配置的消息平台 |
| **工作负载** | 定时任务数量、已安装技能数量 |
| **配置覆盖** | 任何与默认值不同的配置值 |

### 示例输出

```
--- hermes dump ---
version:          0.8.0 (2026.4.8) [af4abd2f]
os:               Linux 6.14.0-37-generic x86_64
python:           3.11.14
openai_sdk:       2.24.0
profile:          default
hermes_home:      ~/.hermes
model:            anthropic/claude-opus-4.6
provider:         openrouter
terminal:         local

api_keys:
  openrouter           set
  openai               not set
  anthropic            set
  nous                 not set
  firecrawl            set
  ...

features:
  toolsets:           all
  mcp_servers:        0
  memory_provider:    built-in
  gateway:            running (systemd)
  platforms:          telegram, discord
  cron_jobs:          3 active / 5 total
  skills:             42

config_overrides:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### 使用时机

- 在 GitHub 上报告 bug 时——将 dump 粘贴到你的 issue 中
- 在 Discord 中寻求帮助时——在代码块中分享它
- 将你的设置与他人的进行比较时
- 当某些功能不正常时进行快速完整性检查

:::tip
`hermes dump` 专门为分享而设计。要进行交互式诊断，请使用 `hermes doctor`。要获得可视化概览，请使用 `hermes status`。
:::

## `hermes debug`

```bash
hermes debug share [options]
```

将调试报告（系统信息 + 最近日志）上传到粘贴服务并获取可分享的 URL。适用于快速支持请求——包含帮助者诊断问题所需的一切。

| 选项 | 描述 |
|--------|-------------|
| `--lines <N>` | 每个日志文件包含的日志行数（默认：200）。 |
| `--expire <days>` | 粘贴过期天数（默认：7）。 |
| `--local` | 在本地打印报告而不是上传。 |

报告包括系统信息（操作系统、Python 版本、Hermes 版本）、最近的 Agent 和消息网关日志（每个文件限制 512 KB）以及脱敏的 API 密钥状态。密钥始终被脱敏——不会上传任何秘密信息。
粘贴服务尝试顺序：paste.rs, dpaste.com。

### 示例

```bash
hermes debug share              # 上传调试报告，打印 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 保留粘贴 30 天
hermes debug share --local      # 将报告打印到终端（不上传）
```

## `hermes backup`

```bash
hermes backup [options]
```

创建 Hermes 配置、技能、会话和数据的 zip 归档。备份排除 hermes-agent 代码库本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output <path>` | zip 文件的输出路径（默认：`~/hermes-backup-<timestamp>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅包含关键状态文件（config.yaml, state.db, .env, auth, cron jobs）。比完整备份快得多。 |
| `-l`, `--label <name>` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 运行时也能正常工作（WAL 模式安全）。

**zip 文件中排除的内容：**

- `*.db-wal`, `*.db-shm`, `*.db-journal` — SQLite 的 WAL / 共享内存 / 日志附属文件。`*.db` 文件已通过 `sqlite3.backup()` 获得一致快照；附带这些活动的附属文件会让恢复操作看到未完全提交的状态。
- `checkpoints/` — 每个会话的轨迹缓存。按哈希键存储并按会话重新生成；无论如何也无法干净地移植到另一个安装。
- `hermes-agent` 代码本身（这是用户数据备份，不是仓库快照）。

### 示例

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到指定路径
hermes backup --quick                   # 仅状态的快速快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes checkpoints`

```bash
hermes checkpoints [COMMAND]
```

检查和管理 `~/.hermes/checkpoints/` 处的影子 git 存储 — 会话内 `/rollback` 命令背后的存储层。可随时安全运行；不需要 Agent 正在运行。

| 子命令 | 描述 |
|------------|-------------|
| `status` (默认) | 显示总大小、项目数量和每个项目的明细。单独的 `hermes checkpoints` 命令等效于此。 |
| `list` | `status` 的别名。 |
| `prune` | 强制执行清理扫描 — 删除孤立和过期的项目，对存储进行垃圾回收，强制执行大小上限。忽略 24 小时幂等性标记。 |
| `clear` | 删除整个检查点基础目录。不可逆；除非使用 `-f`，否则会请求确认。 |
| `clear-legacy` | 仅删除由 v1→v2 迁移产生的 `legacy-<timestamp>/` 归档。 |

### 选项

| 选项 | 子命令 | 描述 |
|--------|------------|-------------|
| `--limit N` | `status`, `list` | 要列出的最大项目数（默认 20）。 |
| `--retention-days N` | `prune` | 删除 `last_touch` 早于 N 天的项目（默认 7）。 |
| `--max-size-mb N` | `prune` | 在孤立/过期项目清理之后，按项目删除最旧的提交，直到总存储大小 ≤ N MB（默认 500）。 |
| `--keep-orphans` | `prune` | 跳过删除工作目录已不存在的项目。 |
| `-f`, `--force` | `clear`, `clear-legacy` | 跳过确认提示。 |

### 示例

```bash
hermes checkpoints                                  # 状态概览
hermes checkpoints prune --retention-days 3         # 激进清理
hermes checkpoints prune --max-size-mb 200          # 收紧一次大小上限
hermes checkpoints clear-legacy -f                  # 删除 v1 归档目录
hermes checkpoints clear -f                         # 清除所有内容
```

有关完整架构和会话内命令，请参阅[检查点和 `/rollback`](../user-guide/checkpoints-and-rollback.md)。

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将先前创建的 Hermes 备份恢复到你的 Hermes 主目录。归档中的所有文件都会覆盖 Hermes 主目录中的现有文件；`--force` 仅跳过在目标已存在 Hermes 安装时触发的确认提示。

| 选项 | 描述 |
|--------|-------------|
| `-f`, `--force` | 跳过现有安装的确认提示。 |

:::warning
导入前请停止消息网关，以避免与正在运行的进程发生冲突。
:::

### 示例
```bash
hermes import ~/hermes-backup-20260423.zip           # 覆盖现有配置前提示
hermes import ~/hermes-backup-20260423.zip --force   # 不提示直接覆盖
```

## `hermes logs`

```bash
hermes logs [log_name] [options]
```

查看、跟踪和过滤 Hermes 日志文件。所有日志都存储在 `~/.hermes/logs/` 中（对于非默认配置文件，存储在 `<profile>/logs/` 中）。

### 日志文件

| 名称 | 文件 | 捕获内容 |
|------|------|-----------------|
| `agent` (默认) | `agent.log` | 所有 Agent 活动 — API 调用、工具调度、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 — agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息分发、webhook 事件 |

### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或使用 `list` 显示可用文件及其大小。 |
| `-n`, `--lines <N>` | 要显示的行数（默认：50）。 |
| `-f`, `--follow` | 实时跟踪日志，类似于 `tail -f`。按 Ctrl+C 停止。 |
| `--level <LEVEL>` | 要显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session <ID>` | 过滤包含会话 ID 子字符串的行。 |
| `--since <TIME>` | 显示从相对时间之前开始的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |
| `--component <NAME>` | 按组件过滤：`gateway`、`agent`、`tools`、`cli`、`cron`。 |

### 示例

```bash
# 查看 agent.log 的最后 50 行（默认）
hermes logs

# 实时跟踪 agent.log
hermes logs -f

# 查看 gateway.log 的最后 100 行
hermes logs gateway -n 100

# 仅显示过去一小时的警告和错误
hermes logs --level WARNING --since 1h

# 按特定会话过滤
hermes logs --session abc123

# 从 30 分钟前开始跟踪 errors.log
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```
### 过滤

过滤器可以组合使用。当多个过滤器同时生效时，日志行必须通过**所有**过滤器才会被显示：

```bash
# 显示过去 2 小时内包含会话 "tg-12345" 的 WARNING 及以上级别的日志行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 生效时，无法解析时间戳的行也会被包含（它们可能是多行日志条目的续行）。当 `--level` 生效时，无法检测级别的行也会被包含。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转——查找 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示包括轮转文件在内的所有日志文件。

## `hermes prompt-size`

```bash
hermes prompt-size [--platform <name>] [--json]
```

报告一个新会话的固定提示词预算——即在每次 API 调用中，在任何对话内容*之前*发送的内容。当下游适配器或代理的提示词预算比模型的上下文窗口更紧张时，或者当你想查看哪个模块（技能索引、记忆、个人资料）占主导地位时，这很有用。

它会构建与 Agent 相同的系统提示词，然后进行分解：

- **系统提示词总计** — 完整组装的提示词（身份、指导、技能索引、上下文文件、记忆、个人资料、时间戳）。
- **技能索引** — `<available_skills>` 块。当安装了许多技能时，这通常是最大的单个块。
- **记忆** 和 **用户个人资料** — 你的 `MEMORY.md` / `USER.md` 快照。
- **提示词层级** — 稳定层 / 上下文层 / 易变层，与 Hermes 为缓存友好性而分层提示词的方式相匹配。
- **工具模式** — 所有已启用工具的 JSON（每次调用固定负载的另一半）。

完全离线运行——无需 API 调用，无需配置凭据即可工作。

```bash
# 为 CLI 平台提供人类可读的分解（默认）
hermes prompt-size

# 模拟消息传递平台的提示词（不同的平台提示）
hermes prompt-size --platform telegram

# 为脚本提供机器可读的输出
hermes prompt-size --json
```

:::tip
技能索引和工具模式的大小随你启用的技能和工具数量而变化。要缩小提示词，请禁用未使用的工具集 (`hermes tools`) 或卸载不需要的技能 (`hermes skills`)。当前目录中的上下文文件 (AGENTS.md, .cursorrules) 也会计入总量。
:::

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set <key> <value>` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式地添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <platform> <code>` | 批准一个配对码。 |
| `revoke <platform> <user-id>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 分页浏览技能注册表。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装一个技能。 |
| `inspect` | 预览一个技能而不安装它。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 在有可用更新时，重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除一个通过 hub 安装的技能。 |
| `reset` | 通过清除其清单条目，解除被标记为 `user_modified` 的捆绑技能的锁定状态。使用 `--restore` 时，还会用捆绑版本替换用户副本。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式地启用/禁用技能配置。 |

常见示例：

```bash
hermes skills browse
hermes skills browse --source official
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect official/security/1password
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install official/migration/openclaw-migration
hermes skills install skills-sh/anthropics/skills/pdf --force
hermes skills install https://sharethis.chat/SKILL.md                     # 直接 URL（单文件 SKILL.md）
hermes skills install https://example.com/SKILL.md --name my-skill        # 当 frontmatter 中没有名称时覆盖名称
hermes skills check
hermes skills update
hermes skills config
hermes skills reset google-workspace
hermes skills reset google-workspace --restore --yes
```

注意：
- `--force` 可以覆盖第三方/社区技能的非危险策略阻止。
- `--force` 不会覆盖 `dangerous` 扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向暴露 `/.well-known/skills/index.json` 的站点。
- `--source browse-sh` 搜索 [browse.sh](https://browse.sh) 的 200 多个特定站点浏览器自动化技能目录。标识符类似于 `browse-sh/airbnb.com/search-listings-ddgioa`。
- 传递一个 `http(s)://…/*.md` URL 会直接安装一个单文件 SKILL.md。当 frontmatter 中没有 `name:` 且 URL 段不是有效标识符时，交互式终端会提示输入名称；非交互式界面（TUI 内的 `/skills install`，消息网关平台）则需要使用 `--name <x>`。

## `hermes bundles`

```bash
hermes bundles <subcommand>
```

技能捆绑包将多个技能分组在一个 `/<bundle-name>` 斜杠命令下。调用捆绑包会将每个引用的技能加载到单个组合的用户消息中。存储位置：`~/.hermes/skill-bundles/<slug>.yaml`。有关 YAML 模式和行为，请参阅 [技能捆绑包](../user-guide/features/skills.md#skill-bundles)。
## `hermes bundles`

```bash
hermes bundles <subcommand>
```

管理技能包。技能包是预定义的技能集合，可以通过一个命令加载。技能包文件存储在 `~/.hermes/skill-bundles/` 目录中。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出已安装的技能包（未指定子命令时的默认行为） |
| `show <name>` | 显示一个技能包的名称、描述、包含的技能和文件路径 |
| `create <name>` | 创建一个新的技能包。传递 `--skill <id>`（可重复）或省略以进行交互式输入。支持 `--description`、`--instruction`、`--force` 选项。 |
| `delete <name>` | 删除技能包文件 |
| `reload` | 重新扫描 `~/.hermes/skill-bundles/` 目录并报告新增/移除的技能包 |

示例：

```bash
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work"

hermes bundles list
hermes bundles show backend-dev
hermes bundles delete backend-dev
```

在聊天会话中，`/bundles` 列出已安装的技能包，`/<bundle-name>` 加载一个技能包。

## `hermes curator`

```bash
hermes curator <subcommand>
```

策展器是一个辅助模型的背景任务，定期审查 Agent 创建的技能，清理过时的技能，合并重叠的技能，并归档废弃的技能。捆绑安装和从 Hub 安装的技能永远不会被触及。归档的技能可以恢复；永远不会自动删除。

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示策展器状态和技能统计信息 |
| `run` | 立即触发策展器审查（阻塞直到 LLM 处理完成） |
| `run --background` | 在后台线程中启动 LLM 处理并立即返回 |
| `run --dry-run` | 仅预览 — 生成审查报告但不进行任何修改 |
| `backup` | 手动创建 `~/.hermes/skills/` 的 tar.gz 快照（策展器在每次实际运行前也会自动创建快照） |
| `rollback` | 从快照恢复 `~/.hermes/skills/`（默认为最新的快照） |
| `rollback --list` | 列出可用的快照 |
| `rollback --id <ts>` | 按 ID 恢复特定的快照 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停策展器直到恢复 |
| `resume` | 恢复已暂停的策展器 |
| `pin <skill>` | 固定一个技能，使策展器永远不会自动转换它 |
| `unpin <skill>` | 取消固定一个技能 |
| `restore <skill>` | 恢复一个已归档的技能 |
| `archive <skill>` | 手动归档一个技能 |
| `prune` | 手动清理策展器通常会清理的技能 |
| `list-archived` | 列出已归档的技能（可通过 `restore` 恢复） |

在新安装时，第一次计划的运行会推迟一个完整的 `interval_hours`（默认为 7 天）— 消息网关不会在 `hermes update` 后的第一次触发时立即进行策展。在此之前，可以使用 `hermes curator run --dry-run` 进行预览。

有关行为和配置，请参阅 [策展器](../user-guide/features/curator.md)。

## `hermes fallback`

```bash
hermes fallback <subcommand>
```

管理备用提供商链。当主模型因速率限制、过载或连接错误而失败时，会按顺序尝试备用提供商。

| 子命令 | 描述 |
|------------|-------------|
| `list` (别名: `ls`) | 显示当前的备用链（未指定子命令时的默认行为） |
| `add` | 选择一个提供商 + 模型（与 `hermes model` 相同的选择器）并追加到链中 |
| `remove` (别名: `rm`) | 从链中选择一个条目删除 |
| `clear` | 移除所有备用条目 |

请参阅 [备用提供商](../user-guide/features/fallback-providers.md)。

## `hermes hooks`

```bash
hermes hooks <subcommand>
```

检查在 `~/.hermes/config.yaml` 中声明的 shell 脚本钩子，使用合成负载测试它们，并管理位于 `~/.hermes/shell-hooks-allowlist.json` 的首次使用同意允许列表。

| 子命令 | 描述 |
|------------|-------------|
| `list` (别名: `ls`) | 列出已配置的钩子及其匹配器、超时和同意状态 |
| `test <event>` | 使用合成负载触发匹配 `<event>` 的每个钩子 |
| `revoke` (别名: `remove`, `rm`) | 移除命令的允许列表条目（在下次重启时生效） |
| `doctor` | 检查每个已配置的钩子：执行权限、允许列表、修改时间漂移、JSON 有效性以及合成运行计时 |

有关事件签名和负载结构，请参阅 [钩子](../user-guide/features/hooks.md)。

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置和管理外部记忆提供商插件。可用的提供商：honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory。一次只能激活一个外部提供商。内置记忆（MEMORY.md/USER.md）始终处于活动状态。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供商选择和配置。 |
| `status` | 显示当前记忆提供商配置。 |
| `off` | 禁用外部提供商（仅使用内置记忆）。 |

:::info 提供商特定的子命令
当外部记忆提供商处于活动状态时，它可能会注册自己的顶级 `hermes <provider>` 命令，用于提供商特定的管理（例如，当 Honcho 激活时，使用 `hermes honcho`）。非活动状态的提供商不会暴露其子命令。运行 `hermes --help` 查看当前已连接的命令。
:::

## `hermes acp`

```bash
hermes acp
```

将 Hermes 作为 ACP（Agent Client Protocol）stdio 服务器启动，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

首先安装支持：

```bash
pip install -e '.[acp]'
```

请参阅 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部原理](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP（Model Context Protocol）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* 或 `picker` | 交互式目录选择器 — 浏览 Nous 批准的 MCP 并进行安装/启用/禁用。 |
| `catalog` | 列出 Nous 批准的 MCP（纯文本，可编写脚本）。 |
| `install <name>` | 安装目录条目（例如 `hermes mcp install n8n`）。 |
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 — 将会话暴露给其他 Agent。 |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个自定义 MCP 服务器，并自动发现工具。 |
| `remove <name>` (别名: `rm`) | 从配置中移除一个 MCP 服务器。 |
| `list` (别名: `ls`) | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与 MCP 服务器的连接。 |
| `configure <name>` (别名: `config`) | 切换服务器的工具选择。 |
| `login <name>` | 强制为基于 OAuth 的 MCP 服务器重新进行身份验证。 |
请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

统一的插件管理——通用插件、记忆提供商和上下文引擎集中管理。不带子命令运行 `hermes plugins` 会打开一个复合交互式界面，包含两个部分：

- **通用插件** —— 多选复选框，用于启用/禁用已安装的插件
- **提供商插件** —— 用于记忆提供商和上下文引擎的单选配置。按 ENTER 键打开类别对应的单选选择器。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 复合交互式 UI —— 通用插件开关 + 提供商插件配置。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <name>` | 拉取已安装插件的最新更改。 |
| `remove <name>` (别名：`rm`, `uninstall`) | 移除已安装的插件。 |
| `enable <name>` | 启用已禁用的插件。 |
| `disable <name>` | 禁用插件但不移除它。 |
| `list` (别名：`ls`) | 列出已安装的插件及其启用/禁用状态。 |

提供商插件的选择会保存到 `config.yaml`：
- `memory.provider` —— 活跃的记忆提供商（空 = 仅内置）
- `context.engine` —— 活跃的上下文引擎 (`"compressor"` = 内置默认值)

通用插件的禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下。

请参阅 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

不带 `--summary` 选项时，此命令会启动交互式的按平台工具配置 UI。

## `hermes computer-use`

```bash
hermes computer-use <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `install` | 运行上游 cua-driver 安装程序（仅限 macOS）。 |
| `install --upgrade` | 即使 cua-driver 已在 PATH 上，也重新运行安装程序。上游脚本总是拉取最新版本，因此这会执行原地升级。 |
| `status` | 打印 `cua-driver` 是否在 `$PATH` 上以及安装的版本。 |

`hermes computer-use install` 是用于安装 `computer_use` 工具集使用的 [cua-driver](https://github.com/trycua/cua) 二进制文件的稳定入口点。它运行与 `hermes tools` 在您首次启用计算机使用时调用的相同上游安装程序，因此，如果工具集开关没有触发安装（例如，在返回用户设置中），重新运行安装是安全的。

如果 cua-driver 在 PATH 上，`hermes update` 会在更新结束时自动重新运行上游安装程序，因此大多数用户不需要手动调用 `--upgrade`。当上游发布了您希望立即获取的修复程序，而不想等待下一次 Hermes 更新时，请使用它。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 带有搜索和恢复功能的交互式会话选择器。 |
| `export <output> [--session-id ID]` | 将会话导出为 JSONL。 |
| `delete <session-id>` | 删除一个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储统计信息。 |
| `rename <session-id> <title>` | 设置或更改会话标题。 |

## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 描述 |
|--------|-------------|
| `--days <n>` | 分析最近 `n` 天（默认值：30）。 |
| `--source <platform>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将您的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取并写入 `~/.hermes`。自动检测旧目录名称（`~/.clawdbot`、`~/.moltbot`）和配置文件名称（`clawdbot.json`、`moltbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，但不写入任何内容。 |
| `--preset <name>` | 迁移预设：`full`（所有兼容设置）或 `user-data`（排除基础设施配置）。两种预设均不导入密钥——需要显式传递 `--migrate-secrets`。 |
| `--overwrite` | 在冲突时覆盖现有的 Hermes 文件（默认：当计划存在冲突时拒绝应用）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥。即使在 `--preset full` 下也需要。 |
| `--no-backup` | 跳过 `~/.hermes/` 的迁移前 zip 快照（默认情况下，在应用前会将单个还原点存档写入 `~/.hermes/backups/pre-migration-*.zip`；可通过 `hermes import` 恢复）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认值：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作空间指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖 30 多个类别，包括人格、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么**直接导入**到 Hermes 的等效项中，要么**存档**以供手动审查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台 Token 和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认值（推理努力程度、压缩、人工延迟、时区、沙盒）、会话重置策略、批准规则、TTS 配置、浏览器设置、工具设置、执行超时、命令允许列表、消息网关配置以及来自 3 个来源的 API 密钥。
**已归档待人工审核：** 定时任务、插件、钩子/webhook、记忆后端（QMD）、技能注册表配置、UI/身份、日志记录、多 Agent 设置、通道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析** 按优先级顺序检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有 Token 字段都处理纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理详情以及迁移后检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移（所有兼容设置，不含密钥）
hermes claw migrate --preset full

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full --migrate-secrets

# 仅迁移用户数据（不含密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动 Web 仪表盘 —— 一个基于浏览器的 UI，用于管理配置、API 密钥和监控会话。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。嵌入式浏览器聊天标签页需要 `--tui` 加上 `pty` 额外依赖项。完整文档请参阅 [Web 仪表盘](/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 描述 |
|--------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--tui` | 关闭 | 通过在 PTY/WebSocket 桥接后运行 `hermes --tui` 来启用浏览器内的聊天标签页。需要 `pip install 'hermes-agent[web,pty]'` 以及 POSIX PTY 环境，例如 Linux、macOS 或 WSL2。 |
| `--insecure` | 关闭 | 允许绑定到非本地主机地址。会在网络上暴露仪表盘凭据；仅在受信任的网络控制后使用。 |
| `--stop` | — | 停止正在运行的 `hermes dashboard` 进程并退出。 |
| `--status` | — | 列出正在运行的 `hermes dashboard` 进程并退出。 |

```bash
# 默认 —— 在浏览器中打开 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open

# 启用浏览器聊天标签页
hermes dashboard --tui
```

## `hermes profile`

```bash
hermes profile <子命令>
```

管理配置文件 —— 多个独立的 Hermes 实例，每个实例都有自己的配置、会话、技能和主目录。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use <名称>` | 设置一个粘性默认配置文件。 |
| `create <名称> [--clone] [--clone-all] [--clone-from <源>] [--no-alias]` | 创建新的配置文件。`--clone` 从活动配置文件复制配置、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置文件。 |
| `delete <名称> [-y]` | 删除配置文件。 |
| `show <名称>` | 显示配置文件详情（主目录、配置等）。 |
| `alias <名称> [--remove] [--name 名称]` | 管理用于快速访问配置文件的包装脚本。 |
| `rename <旧名称> <新名称>` | 重命名配置文件。 |
| `export <名称> [-o 文件]` | 将配置文件导出到 `.tar.gz` 归档文件（本地备份）。 |
| `import <归档文件> [--name 名称]` | 从 `.tar.gz` 归档文件导入配置文件（本地恢复）。 |
| `install <源> [--name 名称] [--alias] [--force] [-y]` | 从 git URL 或本地目录安装配置文件分发版。 |
| `update <名称> [--force-config] [-y]` | 重新拉取分发版；保留用户数据（记忆、会话、认证信息）。 |
| `info <名称>` | 显示配置文件的分发清单（版本、要求、来源）。 |

示例：

```bash
hermes profile list
hermes profile create work --clone
hermes profile use work
hermes profile alias work --name h-work
hermes profile export work -o work-backup.tar.gz
hermes profile import work-backup.tar.gz --name restored
hermes profile install github.com/user/my-distro --alias
hermes profile update work
hermes -p work chat -q "来自工作配置文件的问候"
```

## `hermes completion`

```bash
hermes completion [bash|zsh|fish]
```

将 shell 自动补全脚本打印到标准输出。在你的 shell 配置文件中加载输出，即可获得 Hermes 命令、子命令和配置文件名称的 Tab 键自动补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc

# Fish
hermes completion fish > ~/.config/fish/completions/hermes.fish
```

## `hermes update`

```bash
hermes update [--gateway] [--check] [--no-backup] [--backup] [--yes]
```

拉取最新的 `hermes-agent` 代码并在你的虚拟环境中重新安装依赖项，然后重新运行安装后钩子（MCP 服务器、技能同步、自动补全安装）。可在运行中的安装上安全执行。

**pip 安装：** `hermes update` 会自动检测基于 pip 的安装 —— 它会查询 PyPI 获取最新版本，并运行 `pip install --upgrade hermes-agent` 而不是 `git pull`。PyPI 发布跟踪的是带标签的版本（主要/次要版本），而不是 `main` 分支上的每次提交。使用 `--check` 可以查看是否有更新的 PyPI 版本可用，而无需安装。

| 选项 | 描述 |
|--------|-------------|
| `--gateway` | 消息传递 `/update` 命令使用的内部模式。使用基于文件的 IPC 进行提示词和进度流传输，而不是从终端标准输入读取。不是网关重启标志。 |
| `--check` | 检查是否有更新可用，但不进行拉取、安装依赖项或重启任何内容。 |
| `--no-backup` | 跳过本次运行的更新前备份，即使 `config.yaml` 中启用了 `updates.pre_update_backup`。 |
| `--backup` | 在拉取之前创建 `HERMES_HOME`（配置、认证信息、会话、技能、配对数据）的带标签的更新前快照。默认是**关闭**的 —— 之前总是备份的行为会给大型主目录的每次更新增加数分钟时间。可以通过在 `config.yaml` 中设置 `updates.pre_update_backup: true` 来永久开启它。 |
| `--yes`, `-y` | 对于交互式提示（例如配置迁移和存储恢复）假设回答为“是”。API 密钥输入会被跳过；请单独运行 `hermes config migrate` 来处理这些。 |
其他行为：

- **消息网关重启**。成功更新后，Hermes 会尝试自动重启所有正在运行的消息网关配置文件，以便它们加载新代码。当你想在不应用更新的情况下重启消息网关时，请使用 `hermes gateway restart`。
- **配对数据快照**。即使 `--backup` 关闭，`hermes update` 也会在 `git pull` 之前对 `~/.hermes/pairing/` 和飞书评论规则进行轻量级快照。如果拉取操作重写了你正在编辑的文件，你可以使用 `hermes backup restore --state pre-update` 回滚。
- **遗留 `hermes.service` 警告**。如果 Hermes 检测到重命名前的 `hermes.service` systemd 单元（而不是当前的 `hermes-gateway.service`），它会打印一次性的迁移提示，以便你避免 flap-loop 问题。
- **退出码**。成功时为 `0`，拉取/安装/安装后错误时为 `1`，当意外的 working-tree 更改阻止 `git pull` 时为 `2`。

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes postinstall` | 内部引导程序。在 `pip install hermes-agent`（或 pip 安装时的 `hermes update`）之后运行一次，以安装 pip 无法提供的非 Python 依赖项 — Node.js 运行时、无头浏览器、ripgrep、ffmpeg — 然后如果配置文件尚未配置，则触发 `hermes setup`。可以安全地重新运行，具有幂等性。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选择删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)