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

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置和配对 WhatsApp 桥接。 |
| `hermes auth` | 管理凭证 — 添加、列出、移除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** — 请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查和触发定时任务调度器。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 Webhook 订阅。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes dump` | 用于支持/调试的可复制粘贴的设置摘要。 |
| `hermes debug` | 调试工具 — 为支持上传日志和系统信息。 |
| `hermes backup` | 将 Hermes 主目录备份到 zip 文件。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes memory` | 配置外部记忆提供商。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 Token/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移助手。 |
| `hermes dashboard` | 启动 Web 仪表板以管理配置、API 密钥和会话。 |
| `hermes debug` | 调试工具 — 为支持上传日志和系统信息。 |
| `hermes backup` | 将 Hermes 主目录备份到 zip 文件。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes profile` | 管理配置文件 — 多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖项。 |
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
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`huggingface`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`kilocode`、`xiaomi`、`arcee`。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：抑制横幅/旋转器/工具预览。 |
| `--image <path>` | 将本地图像附加到单个查询。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为此运行创建隔离的 git 工作树。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传递到系统提示词中。 |
| `--source <tag>` | 用于过滤的会话来源标签（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，请使用 `tool`。 |
| `--max-turns <N>` | 每次对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "总结最新的 PR"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "仅返回 JSON"
hermes chat --worktree -q "审查此仓库并打开一个 PR"
```

## `hermes model`

交互式提供商 + 模型选择器。

```bash
hermes model
```

在以下情况下使用此命令：
- 切换默认提供商
- 在模型选择期间登录 OAuth 支持的提供商
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

### `/model` 斜杠命令（会话中）

无需离开会话即可切换模型：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```
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
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

:::tip WSL 用户
请使用 `hermes gateway run` 而不是 `hermes gateway start` — WSL 的 systemd 支持不可靠。可以将其包装在 tmux 中以实现持久化：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/docs/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset]
```

使用完整向导或跳转到某个部分：

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
| `--non-interactive` | 使用默认值/环境变量值，无需提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭证，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth`

管理用于同提供商密钥轮换的凭证池。完整文档请参阅 [凭证池](/docs/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭证
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
```

子命令：`add`、`list`、`remove`、`reset`。当不带子命令调用时，启动交互式管理向导。

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
| `create` / `add` | 根据提示词创建计划任务，可选择通过重复的 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划、提示词、名称、交付方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复暂停的任务并计算其下一次未来运行时间。 |
| `run` | 在下一个调度器周期触发任务。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行到期任务一次并退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动 Agent 激活的动态 Webhook 订阅。需要在配置中启用 webhook 平台 — 如果未配置，则打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 Webhook 路由。返回 URL 和 HMAC 密钥，以便在你的服务上配置。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。来自 config.yaml 的静态路由不受影响。 |
| `test` | 发送测试 POST 请求以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <名称> [选项]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 包含 `{dot.notation}` 负载引用的提示词模板。 |
| `--events` | 要接受的事件类型，以逗号分隔（例如 `issues,pull_request`）。空值 = 全部。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 为 Agent 运行加载的技能名称，以逗号分隔。 |
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

输出整个 Hermes 设置的紧凑、纯文本摘要。设计用于在请求支持时复制粘贴到 Discord、GitHub issues 或 Telegram — 没有 ANSI 颜色，没有特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏的 API 密钥前缀（前 4 位和后 4 位字符），而不仅仅是 `set`/`not set`。 |
### 包含内容

| 部分 | 详情 |
|---------|---------|
| **Header** | Hermes 版本、发布日期、git 提交哈希 |
| **Environment** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **Identity** | 活动配置文件名称、HERMES_HOME 路径 |
| **Model** | 配置的默认模型和提供商 |
| **Terminal** | 后端类型（本地、docker、ssh 等） |
| **API keys** | 所有 22 个提供商/工具 API 密钥的存在性检查 |
| **Features** | 启用的工具集、MCP 服务器数量、记忆提供商 |
| **Services** | 消息网关状态、配置的消息平台 |
| **Workload** | 定时任务数量、已安装技能数量 |
| **Config overrides** | 任何与默认值不同的配置值 |

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

- 在 GitHub 上报告 bug 时 — 将 dump 内容粘贴到你的 issue 中
- 在 Discord 中寻求帮助时 — 在代码块中分享它
- 将你的设置与他人的进行比较时
- 当某些功能不正常时进行快速完整性检查

:::tip
`hermes dump` 是专门为分享而设计的。要进行交互式诊断，请使用 `hermes doctor`。要获取可视化概览，请使用 `hermes status`。
:::

## `hermes debug`

```bash
hermes debug share [options]
```

将调试报告（系统信息 + 最近的日志）上传到粘贴服务并获取可分享的 URL。适用于快速支持请求 — 包含帮助者诊断问题所需的一切信息。

| 选项 | 描述 |
|--------|-------------|
| `--lines <N>` | 每个日志文件包含的日志行数（默认：200）。 |
| `--expire <days>` | 粘贴过期天数（默认：7）。 |
| `--local` | 在本地打印报告而不是上传。 |

报告包括系统信息（操作系统、Python 版本、Hermes 版本）、最近的 Agent 和消息网关日志（每个文件限制 512 KB）以及脱敏的 API 密钥状态。密钥始终会被脱敏 — 不会上传任何秘密信息。

粘贴服务按顺序尝试：paste.rs, dpaste.com。

### 示例

```bash
hermes debug share              # 上传调试报告，打印 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 将粘贴保留 30 天
hermes debug share --local      # 将报告打印到终端（不上传）
```

## `hermes backup`

```bash
hermes backup [options]
```

创建你的 Hermes 配置、技能、会话和数据的 zip 归档。备份不包括 hermes-agent 代码库本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output <path>` | zip 文件的输出路径（默认：`~/hermes-backup-<timestamp>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅包含关键状态文件（config.yaml, state.db, .env, auth, cron jobs）。比完整备份快得多。 |
| `-l`, `--label <name>` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 运行时也能正常工作（WAL 模式安全）。

### 示例

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到指定路径
hermes backup --quick                   # 仅状态的快速快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将先前创建的 Hermes 备份恢复到你的 Hermes 主目录。

| 选项 | 描述 |
|--------|-------------|
| `-f`, `--force` | 无需确认即覆盖现有文件。 |

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
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息调度、webhook 事件 |

### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看哪个日志：`agent`（默认）、`errors`、`gateway`，或使用 `list` 显示可用文件及其大小。 |
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

过滤器可以组合使用。当多个过滤器同时生效时，日志行必须通过**所有**过滤器才会显示：

```bash
# 显示过去 2 小时内包含会话 "tg-12345" 的 WARNING 及以上级别的日志行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 生效时，无法解析时间戳的日志行也会被包含（它们可能是多行日志条目的续行）。当 `--level` 生效时，无法检测到级别的日志行也会被包含。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转 —— 请查找 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示包括已轮转文件在内的所有日志文件。

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
| `check` | 检查已安装的 Hub 技能是否有上游更新。 |
| `update` | 在有可用更新时重新安装 Hub 技能。 |
| `audit` | 重新扫描已安装的 Hub 技能。 |
| `uninstall` | 移除一个通过 Hub 安装的技能。 |
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
hermes skills check
hermes skills update
hermes skills config
```

注意：
- `--force` 可以覆盖第三方/社区技能的非危险策略阻止。
- `--force` 不会覆盖 `dangerous` 扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向暴露 `/.well-known/skills/index.json` 的站点。

## `hermes honcho`

```bash
hermes honcho [--target-profile 名称] <子命令>
```

管理 Honcho 跨会话记忆集成。此命令由 Honcho 记忆提供商插件提供，仅在配置中将 `memory.provider` 设置为 `honcho` 时可用。

`--target-profile` 标志允许你管理另一个配置文件的 Honcho 配置，而无需切换到该配置文件。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 重定向到 `hermes memory setup`（统一设置路径）。 |
| `status [--all]` | 显示当前 Honcho 配置和连接状态。`--all` 显示跨配置文件概览。 |
| `peers` | 显示所有配置文件中的对等身份。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map [名称]` | 将当前目录映射到 Honcho 会话名称。省略 `名称` 以列出当前映射。 |
| `peer` | 显示或更新对等名称和辩证推理级别。选项：`--user 名称`、`--ai 名称`、`--reasoning 级别`。 |
| `mode [模式]` | 显示或设置回忆模式：`hybrid`、`context` 或 `tools`。省略以显示当前模式。 |
| `tokens` | 显示或设置上下文和辩证的 Token 预算。选项：`--context N`、`--dialectic N`。 |
| `identity [文件] [--show]` | 初始化或显示 AI 对等身份表示。 |
| `enable` | 为活动配置文件启用 Honcho。 |
| `disable` | 为活动配置文件禁用 Honcho。 |
| `sync` | 将 Honcho 配置同步到所有现有配置文件（创建缺失的主机块）。 |
| `migrate` | 从 openclaw-honcho 迁移到 Hermes Honcho 的逐步指南。 |

## `hermes memory`

```bash
hermes memory <子命令>
```

设置和管理外部记忆提供商插件。可用提供商：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。一次只能激活一个外部提供商。内置记忆（MEMORY.md/USER.md）始终处于活动状态。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供商选择和配置。 |
| `status` | 显示当前记忆提供商配置。 |
| `off` | 禁用外部提供商（仅使用内置记忆）。 |

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
hermes mcp <子命令>
```

管理 MCP（Model Context Protocol）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 —— 将会话暴露给其他 Agent。 |
| `add <名称> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个 MCP 服务器并自动发现工具。 |
| `remove <名称>` (别名：`rm`) | 从配置中移除一个 MCP 服务器。 |
| `list` (别名：`ls`) | 列出已配置的 MCP 服务器。 |
| `test <名称>` | 测试与 MCP 服务器的连接。 |
| `configure <名称>` (别名：`config`) | 切换服务器的工具选择。 |
请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

统一的插件管理——将通用插件、记忆提供商和上下文引擎集中在一处。不带子命令运行 `hermes plugins` 会打开一个复合交互式界面，包含两个部分：

- **通用插件** —— 多选复选框，用于启用/禁用已安装的插件
- **提供商插件** —— 用于记忆提供商和上下文引擎的单选配置。按 ENTER 键打开某个类别的单选选择器。

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
- `memory.provider` —— 活跃的记忆提供商（空 = 仅使用内置）
- `context.engine` —— 活跃的上下文引擎（`"compressor"` = 内置默认值）

通用插件的禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下。

请参阅 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前启用的工具摘要并退出。 |

不带 `--summary` 选项时，此命令会启动交互式的按平台工具配置 UI。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 带有搜索和恢复功能的交互式会话选择器。 |
| `export <output> [--session-id ID]` | 将会话导出为 JSONL 格式。 |
| `delete <session-id>` | 删除一个会话。 |
| `prune` | 删除旧的会话。 |
| `stats` | 显示会话存储统计信息。 |
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

将你的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取并写入 `~/.hermes`。自动检测旧版目录名（`~/.clawdbot`、`~/.moltbot`）和配置文件名（`clawdbot.json`、`moltbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，不实际写入任何内容。 |
| `--preset <name>` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（排除 API 密钥）。 |
| `--overwrite` | 冲突时覆盖现有的 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥（使用 `--preset full` 时默认启用）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作空间指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖 30 多个类别，包括人格、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么**直接导入**到 Hermes 的等效项中，要么**存档**以供手动审查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台 Token 和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认值（推理强度、压缩、人工延迟、时区、沙盒）、会话重置策略、审批规则、TTS 配置、浏览器设置、工具设置、执行超时、命令允许列表、消息网关配置，以及来自 3 个来源的 API 密钥。

**存档以供手动审查：** 定时任务、插件、钩子/webhook、记忆后端（QMD）、技能注册表配置、UI/身份、日志记录、多 Agent 设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析** 按优先级顺序检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有 Token 字段都处理纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理细节和迁移后检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full

# 仅迁移用户数据（无密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动 Web 仪表板 —— 一个基于浏览器的 UI，用于管理配置、API 密钥和监控会话。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。完整文档请参阅 [Web 仪表板](/docs/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 描述 |
|--------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
```bash
# 默认 — 在浏览器中打开 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open
```

## `hermes profile`

```bash
hermes profile <子命令>
```

管理配置文件 — 多个独立的 Hermes 实例，每个实例都有自己的配置、会话、技能和主目录。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use <名称>` | 设置一个粘性默认配置文件。 |
| `create <名称> [--clone] [--clone-all] [--clone-from <源>] [--no-alias]` | 创建一个新的配置文件。`--clone` 从活动配置文件复制配置、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置文件。 |
| `delete <名称> [-y]` | 删除一个配置文件。 |
| `show <名称>` | 显示配置文件详细信息（主目录、配置等）。 |
| `alias <名称> [--remove] [--name 名称]` | 管理用于快速访问配置文件的包装脚本。 |
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
hermes completion [bash|zsh]
```

将 shell 自动补全脚本打印到标准输出。在您的 shell 配置文件中加载输出，以获得 Hermes 命令、子命令和配置文件名称的 Tab 键自动补全功能。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc
```

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选择删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 界面](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)