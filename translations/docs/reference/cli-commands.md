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
| `--pass-session-id` | 将会话 ID 包含在 Agent 的系统提示词中。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 并回退到内置默认值。`.env` 中的凭据仍会被加载。 |
| `--ignore-rules` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能的自动注入。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等同于 `HERMES_TUI=1`。 |
| `--dev` | 与 `--tui` 一起使用：通过 `tsx` 直接运行 TypeScript 源码，而非预构建的包（供 TUI 贡献者使用）。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes fallback` | 管理在主模型出错时尝试的备用提供商。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置和配对 WhatsApp 桥接。 |
| `hermes slack` | Slack 助手（当前：生成应用清单，将每个命令作为原生斜杠命令）。 |
| `hermes auth` | 管理凭据 — 添加、列出、移除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** — 请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查和触发定时任务调度器。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 Webhook 订阅。 |
| `hermes hooks` | 检查、批准或移除在 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes dump` | 用于支持/调试的可复制粘贴的设置摘要。 |
| `hermes debug` | 调试工具 — 为支持目的上传日志和系统信息。 |
| `hermes backup` | 将 Hermes 主目录备份到 zip 文件。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes curator` | 后台技能维护 — 状态、运行、暂停、固定。参见 [Curator](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部记忆提供商。插件特定的子命令（例如 `hermes honcho`）在其提供商激活时会自动注册。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 Token/成本/活动分析。 |
| `hermes fallback` | 备用提供商链的交互式管理器。 |
| `hermes claw` | OpenClaw 迁移助手。 |
| `hermes dashboard` | 启动用于管理配置、API 密钥和会话的 Web 仪表板。 |
| `hermes profile` | 管理配置文件 — 多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。`--check` 打印提交差异而不拉取；`--backup` 在拉取前创建 `HERMES_HOME` 快照。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|--------|-------------|
| `-q`, `--query "..."` | 一次性、非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用逗号分隔的工具集。 |
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`google-gemini-cli`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`alibaba-coding-plan` (别名 `alibaba_coding`)、`deepseek`、`nvidia`、`ollama-cloud`、`xai` (别名 `grok`)、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry`、`tencent-tokenhub` (别名 `tencent`、`tokenhub`)。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：抑制横幅/旋转器/工具预览。 |
| `--image <path>` | 将本地图片附加到单个查询。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为此运行创建隔离的 git 工作树。 |
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
hermes chat -q "总结最新的 PR"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "只返回 JSON"
hermes chat --worktree -q "审查此仓库并开启一个 PR"
hermes chat --ignore-user-config --ignore-rules -q "不使用我的个人设置进行复现"
```

### `hermes -z <prompt>` — 脚本化单次调用

对于程序化调用者（shell 脚本、CI、定时任务、父进程通过管道输入提示词），`hermes -z` 是最纯粹的单次调用入口点：**单条提示词输入，最终响应文本输出，标准输出或标准错误上无其他内容。** 没有横幅，没有加载动画，没有工具预览，没有 `Session:` 行 —— 只有 Agent 的最终回复作为纯文本。

```bash
hermes -z "法国的首都是什么？"
# → 巴黎。

# 父脚本可以清晰地捕获响应：
answer=$(hermes -z "总结这个" < /path/to/file.txt)
```

每次运行的覆盖项（不修改 `~/.hermes/config.yaml`）：

| 标志 | 等效环境变量 | 用途 |
|---|---|---|
| `-m` / `--model <model>` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider <provider>` | `HERMES_INFERENCE_PROVIDER` | 覆盖本次运行的提供商 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# 或：
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的 Agent，相同的工具，相同的技能 —— 只是去掉了所有交互/装饰层。如果你也需要工具输出在记录中，请改用 `hermes chat -q`；`-z` 明确用于“我只想要最终答案”。

## `hermes model`

交互式提供商 + 模型选择器。**这是用于添加新提供商、设置 API 密钥和运行 OAuth 流程的命令。** 从你的终端运行它 —— 而不是在活跃的 Hermes 聊天会话内部。

```bash
hermes model
```

在以下情况下使用此命令：
- **添加新提供商**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录支持 OAuth 的提供商（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

:::warning hermes model 与 /model — 了解区别
**`hermes model`**（从你的终端运行，在任何 Hermes 会话之外）是**完整的提供商设置向导**。它可以添加新提供商、运行 OAuth 流程、提示输入 API 密钥以及配置端点。

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
/model custom:local:qwen-2.5        # 使用一个命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

默认情况下，`/model` 的更改**仅应用于当前会话**。添加 `--global` 以将更改持久化到 `config.yaml`：

```
/model claude-sonnet-4 --global     # 切换并保存为新的默认值
```

:::info 如果我只看到 OpenRouter 模型怎么办？
如果你只配置了 OpenRouter，`/model` 将只显示 OpenRouter 模型。要添加其他提供商（Anthropic、DeepSeek、Copilot 等），请退出你的会话并从终端运行 `hermes model`。
:::

提供商和基础 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换走时，过时的基础 URL 会被清除，以防止其泄漏到其他提供商。

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
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--all` | 在 `start` / `restart` / `stop` 上：作用于**每个配置文件的**消息网关，而不仅仅是活跃的 `HERMES_HOME`。如果你并排运行多个配置文件，并想在 `hermes update` 后重启所有配置文件，这很有用。 |

:::tip WSL 用户
使用 `hermes gateway run` 而不是 `hermes gateway start` —— WSL 的 systemd 支持不可靠。将其包装在 tmux 中以实现持久化：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/docs/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure]
```

**首次运行：** 启动首次使用向导。

**返回用户（已配置）：** 直接进入完整的重新配置向导 —— 每个提示都显示你当前的值为其默认值，按 Enter 键保留或输入新值。没有菜单。

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
| `--quick` | 在返回用户运行时：仅提示缺失或未设置的项。跳过你已配置的项。 |
| `--non-interactive` | 使用默认值/环境变量值，无需提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |
| `--reconfigure` | 向后兼容的别名 —— 在现有安装上，裸 `hermes setup` 现在默认执行此操作。 |
## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes slack`

```bash
hermes slack manifest              # 将清单打印到标准输出
hermes slack manifest --write      # 写入 ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # 仅输出 features.slash_commands 数组
```

生成一个 Slack 应用清单，将 `COMMAND_REGISTRY` 中的每个消息网关命令（`/btw`、`/stop`、`/model` 等）注册为 Slack 原生的斜杠命令，以实现与 Discord 和 Telegram 的对等功能。将输出内容粘贴到你的 Slack 应用配置中：[https://api.slack.com/apps](https://api.slack.com/apps) → 你的应用 → **Features → App Manifest → Edit**，然后 **Save**。如果权限范围或斜杠命令发生更改，Slack 会提示重新安装。

| 标志 | 默认值 | 用途 |
|------|---------|---------|
| `--write [PATH]` | stdout | 写入文件而非标准输出。单独的 `--write` 写入 `$HERMES_HOME/slack-manifest.json`。 |
| `--name NAME` | `Hermes` | Slack 中显示的 Bot 名称。 |
| `--description DESC` | 默认描述 | Slack 应用目录中显示的 Bot 描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands` 部分，以便合并到手动维护的清单中。 |

在运行 `hermes update` 后，再次运行 `hermes slack manifest --write` 以获取任何新命令。

## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭证，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth`

管理用于同提供商密钥轮换的凭证池。完整文档请参阅[凭证池](/docs/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭证
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
```

子命令：`add`、`list`、`remove`、`reset`。不带子命令调用时，启动交互式管理向导。

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可共享的脱敏格式显示所有详细信息。 |
| `--deep` | 运行可能耗时更长的深度检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已调度的任务。 |
| `create` / `add` | 根据提示词创建定时任务，可选择通过重复的 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的调度、提示词、名称、交付方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复暂停的任务并计算其下一次未来运行时间。 |
| `run` | 在下一个调度器周期触发任务。 |
| `remove` | 删除定时任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行一次到期的任务并退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动 Agent 激活的动态 Webhook 订阅。需要在配置中启用 webhook 平台——如果未配置，则打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回 URL 和 HMAC 密钥，用于在你的服务上配置。 |
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

输出整个 Hermes 设置的紧凑、纯文本摘要。设计用于在请求支持时复制粘贴到 Discord、GitHub issues 或 Telegram——没有 ANSI 颜色，没有特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏的 API 密钥前缀（前 4 位和后 4 位字符），而不仅仅是 `set`/`not set`。 |

### 包含的内容

| 部分 | 详细信息 |
|---------|---------|
| **Header** | Hermes 版本、发布日期、git 提交哈希 |
| **Environment** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **Identity** | 活动配置文件名称、HERMES_HOME 路径 |
| **Model** | 配置的默认模型和提供商 |
| **Terminal** | 后端类型（local、docker、ssh 等） |
| **API keys** | 对所有 22 个提供商/工具 API 密钥的存在性检查 |
| **Features** | 启用的工具集、MCP 服务器数量、记忆提供商 |
| **Services** | 消息网关状态、已配置的消息平台 |
| **Workload** | Cron 任务数量、已安装技能数量 |
| **Config overrides** | 任何与默认值不同的配置值 |
### 示例输出

```
--- hermes dump ---
版本:          0.8.0 (2026.4.8) [af4abd2f]
操作系统:      Linux 6.14.0-37-generic x86_64
Python:        3.11.14
OpenAI SDK:    2.24.0
配置文件:      default
Hermes 主目录: ~/.hermes
模型:          anthropic/claude-opus-4.6
提供商:        openrouter
终端:          local

API 密钥:
  openrouter           已设置
  openai               未设置
  anthropic            已设置
  nous                 未设置
  firecrawl            已设置
  ...

功能:
  工具集:          全部
  MCP 服务器:      0
  记忆提供商:      内置
  消息网关:        运行中 (systemd)
  平台:            telegram, discord
  定时任务:        3 个活跃 / 5 个总计
  技能:            42

配置覆盖:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### 使用时机

- 在 GitHub 上报告 Bug — 将 dump 内容粘贴到你的 issue 中
- 在 Discord 中寻求帮助 — 在代码块中分享它
- 将你的设置与他人进行比较
- 当某些功能不正常时进行快速完整性检查

:::tip
`hermes dump` 专为分享而设计。要进行交互式诊断，请使用 `hermes doctor`。要获取可视化概览，请使用 `hermes status`。
:::

## `hermes debug`

```bash
hermes debug share [options]
```

上传调试报告（系统信息 + 近期日志）到粘贴服务并获取可分享的 URL。对于快速支持请求非常有用 — 包含了帮助者诊断问题所需的一切信息。

| 选项 | 描述 |
|--------|-------------|
| `--lines <N>` | 每个日志文件包含的日志行数（默认：200）。 |
| `--expire <days>` | 粘贴过期天数（默认：7）。 |
| `--local` | 在本地打印报告而不是上传。 |

报告包括系统信息（操作系统、Python 版本、Hermes 版本）、近期 Agent 和消息网关日志（每个文件限制 512 KB）以及脱敏的 API 密钥状态。密钥始终会被脱敏 — 不会上传任何密钥。

粘贴服务按顺序尝试：paste.rs, dpaste.com。

### 示例

```bash
hermes debug share              # 上传调试报告，打印 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 保留粘贴 30 天
hermes debug share --local      # 在终端打印报告（不上传）
```

## `hermes backup`

```bash
hermes backup [options]
```

创建你的 Hermes 配置、技能、会话和数据的 zip 归档。备份会排除 hermes-agent 代码库本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output <path>` | zip 文件的输出路径（默认：`~/hermes-backup-<timestamp>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅包含关键状态文件（config.yaml, state.db, .env, auth, cron jobs）。比完整备份快得多。 |
| `-l`, `--label <name>` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 运行时也能正常工作（WAL 模式安全）。

**zip 文件中排除的内容：**

- `*.db-wal`, `*.db-shm`, `*.db-journal` — SQLite 的 WAL / 共享内存 / 日志附属文件。`*.db` 文件已经通过 `sqlite3.backup()` 获得了快照；将实时附属文件与它一起打包，会让恢复操作看到未完全提交的状态。
- `checkpoints/` — 每个会话的轨迹缓存。基于哈希键生成，每个会话都会重新生成；无论如何也无法干净地移植到另一个安装。
- `hermes-agent` 代码本身（这是用户数据备份，不是仓库快照）。

### 示例

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到指定路径
hermes backup --quick                   # 仅状态快速快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将先前创建的 Hermes 备份恢复到你的 Hermes 主目录。

| 选项 | 描述 |
|--------|-------------|
| `-f`, `--force` | 无需确认，直接覆盖现有文件。 |

## `hermes logs`

```bash
hermes logs [log_name] [options]
```

查看、跟踪和过滤 Hermes 日志文件。所有日志都存储在 `~/.hermes/logs/` 中（对于非默认配置文件，存储在 `<profile>/logs/` 中）。

### 日志文件

| 名称 | 文件 | 捕获内容 |
|------|------|-----------------|
| `agent` (默认) | `agent.log` | 所有 Agent 活动 — API 调用、工具分发、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 — agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息分发、webhook 事件 |

### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或使用 `list` 显示可用文件及其大小。 |
| `-n`, `--lines <N>` | 显示的行数（默认：50）。 |
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

# 从 30 分钟前开始，跟踪 errors.log
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```

### 过滤

过滤器可以组合使用。当多个过滤器处于活动状态时，日志行必须通过**所有**过滤器才能被显示：
```bash
# 过去 2 小时内包含会话 "tg-12345" 的 WARNING+ 级别日志行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 启用时，无法解析时间戳的行也会被包含（它们可能是多行日志条目的续行）。当 `--level` 启用时，无法检测级别的行也会被包含。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转——查找 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示包括轮转文件在内的所有日志文件。

## `hermes config`

```bash
hermes config <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set <键> <值>` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <平台> <代码>` | 批准一个配对码。 |
| `revoke <平台> <用户ID>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 分页浏览技能注册表。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装一个技能。 |
| `inspect` | 预览技能而不安装。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 在有可用更新时重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除一个通过 hub 安装的技能。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式启用/禁用技能配置。 |

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
hermes skills install https://example.com/SKILL.md --name my-skill        # 当 frontmatter 没有名称时覆盖名称
hermes skills check
hermes skills update
hermes skills config
```

注意：
- `--force` 可以覆盖针对第三方/社区技能的非危险策略阻止。
- `--force` 不会覆盖 `dangerous` 扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向暴露 `/.well-known/skills/index.json` 的站点。
- 传递一个 `http(s)://…/*.md` URL 会直接安装一个单文件 SKILL.md。当 frontmatter 没有 `name:` 且 URL 段不是有效标识符时，交互式终端会提示输入名称；非交互式界面（TUI 内的 `/skills install`、消息网关平台）则需要使用 `--name <x>`。

## `hermes curator`

```bash
hermes curator <子命令>
```

策展人是一个辅助模型的后台任务，定期审查 Agent 创建的技能，清理过时的技能，合并重叠的技能，并归档废弃的技能。捆绑的和通过 hub 安装的技能永远不会被触及。归档的技能可以恢复；永远不会自动删除。

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示策展人状态和技能统计信息 |
| `run` | 立即触发策展人审查 |
| `pause` | 暂停策展人直到恢复 |
| `resume` | 恢复已暂停的策展人 |
| `pin <技能>` | 固定一个技能，使策展人永远不会自动转换它 |
| `unpin <技能>` | 取消固定一个技能 |
| `restore <技能>` | 恢复一个已归档的技能 |

有关行为和配置，请参阅 [策展人](../user-guide/features/curator.md)。

## `hermes fallback`

```bash
hermes fallback <子命令>
```

管理备用提供商链。当主模型因速率限制、过载或连接错误而失败时，会按顺序尝试备用提供商。

| 子命令 | 描述 |
|------------|-------------|
| `list` (别名: `ls`) | 显示当前的备用链（无子命令时的默认行为） |
| `add` | 选择一个提供商 + 模型（与 `hermes model` 相同的选择器）并追加到链中 |
| `remove` (别名: `rm`) | 从链中选择一个条目删除 |
| `clear` | 移除所有备用条目 |

请参阅 [备用提供商](../user-guide/features/fallback-providers.md)。

## `hermes hooks`

```bash
hermes hooks <子命令>
```

检查在 `~/.hermes/config.yaml` 中声明的 shell 脚本钩子，使用合成负载测试它们，并管理位于 `~/.hermes/shell-hooks-allowlist.json` 的首次使用同意允许列表。

| 子命令 | 描述 |
|------------|-------------|
| `list` (别名: `ls`) | 列出已配置的钩子及其匹配器、超时和同意状态 |
| `test <事件>` | 针对合成负载触发每个匹配 `<事件>` 的钩子 |
| `revoke` (别名: `remove`, `rm`) | 移除命令的允许列表条目（在下次重启时生效） |
| `doctor` | 检查每个已配置的钩子：执行位、允许列表、修改时间漂移、JSON 有效性以及合成运行计时 |

有关事件签名和负载形状，请参阅 [钩子](../user-guide/features/hooks.md)。

## `hermes memory`

```bash
hermes memory <子命令>
```

设置和管理外部记忆提供商插件。可用提供商：honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory。一次只能激活一个外部提供商。内置记忆（MEMORY.md/USER.md）始终处于活动状态。
## 子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式选择并配置提供商。 |
| `status` | 显示当前记忆提供商的配置。 |
| `off` | 禁用外部提供商（仅使用内置功能）。 |

:::info 特定于提供商的子命令
当外部记忆提供商处于活动状态时，它可能会注册自己的顶级 `hermes <provider>` 命令，用于提供商特定的管理（例如，当 Honcho 处于活动状态时，使用 `hermes honcho`）。非活动状态的提供商不会暴露其子命令。运行 `hermes --help` 查看当前已连接的命令。
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

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部原理](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP（Model Context Protocol）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 —— 将会话暴露给其他 Agent。 |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个 MCP 服务器，并自动发现工具。 |
| `remove <name>` (别名：`rm`) | 从配置中移除一个 MCP 服务器。 |
| `list` (别名：`ls`) | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与 MCP 服务器的连接。 |
| `configure <name>` (别名：`config`) | 切换服务器的工具选择。 |

参见 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

统一的插件管理 —— 将通用插件、记忆提供商和上下文引擎集中在一处。不带子命令运行 `hermes plugins` 会打开一个复合交互式界面，包含两个部分：

- **通用插件** —— 多选复选框，用于启用/禁用已安装的插件
- **提供商插件** —— 用于记忆提供商和上下文引擎的单选配置。在某个类别上按 ENTER 键可打开单选选择器。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 复合交互式 UI —— 通用插件开关 + 提供商插件配置。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <name>` | 为已安装的插件拉取最新更改。 |
| `remove <name>` (别名：`rm`, `uninstall`) | 移除已安装的插件。 |
| `enable <name>` | 启用已禁用的插件。 |
| `disable <name>` | 禁用插件但不移除它。 |
| `list` (别名：`ls`) | 列出已安装的插件及其启用/禁用状态。 |

提供商插件的选择会保存到 `config.yaml`：
- `memory.provider` —— 活动的记忆提供商（空值 = 仅使用内置功能）
- `context.engine` —— 活动的上下文引擎（`"compressor"` = 内置默认值）

通用插件的禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下。

参见 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

不带 `--summary` 选项时，此命令会启动交互式的按平台工具配置 UI。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export <output> [--session-id ID]` | 将会话导出为 JSONL 格式。 |
| `delete <session-id>` | 删除一个会话。 |
| `prune` | 删除旧的会话。 |
| `stats` | 显示会话存储的统计信息。 |
| `rename <session-id> <title>` | 设置或更改会话标题。 |

## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 描述 |
|--------|-------------|
| `--days <n>` | 分析最近 `n` 天的数据（默认：30）。 |
| `--source <platform>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将您的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取，并写入到 `~/.hermes`。自动检测旧版目录名（`~/.clawdbot`、`~/.moltbot`）和配置文件（`clawdbot.json`、`moltbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，但不实际写入任何内容。 |
| `--preset <name>` | 迁移预设：`full`（所有兼容的设置）或 `user-data`（排除基础设施配置）。两种预设均不导入密钥 —— 需要显式传递 `--migrate-secrets`。 |
| `--overwrite` | 在冲突时覆盖现有的 Hermes 文件（默认：当计划存在冲突时拒绝应用）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥。即使在 `--preset full` 下也需要此选项。 |
| `--no-backup` | 跳过迁移前对 `~/.hermes/` 的 zip 快照（默认情况下，在应用迁移前会写入一个恢复点存档到 `~/.hermes/backups/pre-migration-*.zip`；可使用 `hermes import` 恢复）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作空间指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖 30 多个类别，包括人格、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么**直接导入**到 Hermes 的等效项中，要么**归档**以供手动审查。
**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4个源目录）、默认模型、自定义提供商、MCP服务器、消息平台令牌和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent默认设置（推理强度、压缩、人工延迟、时区、沙盒）、会话重置策略、审批规则、TTS配置、浏览器设置、工具设置、执行超时、命令允许列表、消息网关配置以及来自3个来源的API密钥。

**存档以供手动审查：** 定时任务、插件、钩子/webhook、记忆后端（QMD）、技能注册表配置、UI/身份、日志记录、多Agent设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API密钥解析**按优先级顺序检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段都处理纯字符串、环境变量模板（`${VAR}`）和SecretRef对象。

有关完整的配置键映射、SecretRef处理详情以及迁移后检查清单，请参阅**[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移（所有兼容设置，不含密钥）
hermes claw migrate --preset full

# 完整迁移，包括API密钥
hermes claw migrate --preset full --migrate-secrets

# 仅迁移用户数据（不含密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义OpenClaw路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动Web仪表盘——一个基于浏览器的UI，用于管理配置、API密钥和监控会话。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。完整文档请参阅[Web仪表盘](/docs/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 描述 |
|--------|---------|-------------|
| `--port` | `9119` | 运行Web服务器的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 默认——在浏览器中打开 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open
```

## `hermes profile`

```bash
hermes profile <子命令>
```

管理配置文件——多个独立的Hermes实例，每个实例都有自己的配置、会话、技能和主目录。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use <名称>` | 设置一个粘性默认配置文件。 |
| `create <名称> [--clone] [--clone-all] [--clone-from <源>] [--no-alias]` | 创建新的配置文件。`--clone` 从活动配置文件复制配置、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置文件。 |
| `delete <名称> [-y]` | 删除配置文件。 |
| `show <名称>` | 显示配置文件详情（主目录、配置等）。 |
| `alias <名称> [--remove] [--name 名称]` | 管理包装器脚本以便快速访问配置文件。 |
| `rename <旧名称> <新名称>` | 重命名配置文件。 |
| `export <名称> [-o 文件]` | 将配置文件导出到 `.tar.gz` 归档文件。 |
| `import <归档文件> [--name 名称]` | 从 `.tar.gz` 归档文件导入配置文件。 |

示例：

```bash
hermes profile list
hermes profile create work --clone
hermes profile use work
hermes profile alias work --name h-work
hermes profile export work -o work-backup.tar.gz
hermes profile import work-backup.tar.gz --name restored
hermes -p work chat -q "Hello from work profile"
```

## `hermes completion`

```bash
hermes completion [bash|zsh|fish]
```

将shell自动补全脚本打印到标准输出。在shell配置文件中加载输出，即可获得Hermes命令、子命令和配置文件名称的Tab补全功能。

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
hermes update [--check] [--backup] [--restart-gateway]
```

拉取最新的 `hermes-agent` 代码并在你的虚拟环境中重新安装依赖项，然后重新运行安装后钩子（MCP服务器、技能同步、自动补全安装）。可在运行中的安装上安全执行。

| 选项 | 描述 |
|--------|-------------|
| `--check` | 并排打印当前提交和最新的 `origin/main` 提交，如果同步则退出码为0，如果落后则退出码为1。不执行拉取、安装或重启任何操作。 |
| `--backup` | 在拉取之前，为 `HERMES_HOME`（配置、认证、会话、技能、配对数据）创建一个带标签的更新前快照。默认**关闭**——之前总是备份的行为在大型主目录上每次更新都会增加几分钟。可以通过在 `config.yaml` 中设置 `update.backup: true` 永久开启。 |
| `--restart-gateway` | 成功更新后，重启正在运行的消息网关服务。如果安装了多个配置文件，则隐含 `--all` 语义。 |

其他行为：

- **配对数据快照。** 即使 `--backup` 关闭，`hermes update` 也会在 `git pull` 之前为 `~/.hermes/pairing/` 和飞书评论规则创建一个轻量级快照。如果拉取操作重写了你正在编辑的文件，你可以使用 `hermes backup restore --state pre-update` 回滚它。
- **遗留 `hermes.service` 警告。** 如果Hermes检测到重命名前的 `hermes.service` systemd单元（而不是当前的 `hermes-gateway.service`），它会打印一次性的迁移提示，以便你避免flap-loop问题。
- **退出码。** 成功时为 `0`，拉取/安装/安装后错误时为 `1`，遇到阻止 `git pull` 的意外工作树更改时为 `2`。

## `hermes fallback`

```bash
hermes fallback           # 交互式管理器
```

管理备用提供商链（当你的主提供商遇到速率限制或返回致命错误时使用），无需手动编辑 `config.yaml`。复用 `hermes model` 中的提供商选择器——相同的提供商列表、相同的凭据提示、相同的验证。

典型会话：

1. 按 `a` 添加备用提供商 → 选择一个提供商（基于OAuth的提供商会打开浏览器；API密钥提供商会提示输入密钥），然后选择具体模型。
2. 使用 `↑`/`↓` 重新排序备用提供商（列表中的第一个会首先尝试）。
3. 按 `d` 删除一个。
所有更改都会持久化到 `config.yaml` 中 `model:` 下的 `fallback_providers:`。与[凭证池](/docs/user-guide/features/credential-pools)交互：凭证池在*同一*提供商内轮换密钥，而回退提供商会完全切换到*不同*的提供商。

有关行为详情以及与 `fallback_model`（旧版单回退键）的交互，请参阅[回退提供商](/docs/user-guide/features/fallback-providers)。

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes uninstall [--full] [--yes]` | 移除 Hermes，可选择删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)