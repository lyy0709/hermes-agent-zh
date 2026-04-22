---
sidebar_position: 4
title: "教程：团队 Telegram 助手"
description: "逐步指南，教你设置一个整个团队都可以使用的 Telegram 机器人，用于代码帮助、研究、系统管理等"
---

# 设置团队 Telegram 助手

本教程将引导你设置一个由 Hermes Agent 驱动的 Telegram 机器人，供多名团队成员使用。最终，你的团队将拥有一个共享的 AI 助手，可以通过私信向其寻求代码、研究、系统管理等方面的帮助——并通过每用户授权确保安全。

## 我们将构建什么

一个 Telegram 机器人，它能够：

- **任何授权团队成员** 都可以通过私信寻求帮助——代码审查、研究、Shell 命令、调试
- **在你的服务器上运行**，拥有完整的工具访问权限——终端、文件编辑、网络搜索、代码执行
- **每用户会话**——每个人都有自己的对话上下文
- **默认安全**——只有经过批准的用户才能交互，提供两种授权方法
- **定时任务**——每日站会、健康检查和提醒发送到团队频道

---

## 先决条件

开始之前，请确保你拥有：

- **Hermes Agent 已安装** 在服务器或 VPS 上（不是你的笔记本电脑——机器人需要保持运行）。如果尚未安装，请遵循[安装指南](/docs/getting-started/installation)。
- **你自己的 Telegram 账户**（机器人所有者）
- **已配置的 LLM 提供商**——至少需要在 `~/.hermes/.env` 中配置 OpenAI、Anthropic 或其他受支持提供商的 API 密钥

:::tip
每月 5 美元的 VPS 足以运行消息网关。Hermes 本身是轻量级的——LLM API 调用才是花钱的地方，而这些调用是远程进行的。
:::

---

## 步骤 1：创建 Telegram 机器人

每个 Telegram 机器人都始于 **@BotFather**——Telegram 官方用于创建机器人的机器人。

1. **打开 Telegram** 并搜索 `@BotFather`，或访问 [t.me/BotFather](https://t.me/BotFather)

2. **发送 `/newbot`** —— BotFather 会询问你两件事：
   - **显示名称** —— 用户看到的名称（例如，`Team Hermes Assistant`）
   - **用户名** —— 必须以 `bot` 结尾（例如，`myteam_hermes_bot`）

3. **复制机器人令牌** —— BotFather 会回复类似这样的内容：
   ```
   Use this token to access the HTTP API:
   7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...
   ```
   保存此令牌——下一步会用到它。

4. **设置描述**（可选但推荐）：
   ```
   /setdescription
   ```
   选择你的机器人，然后输入类似这样的内容：
   ```
   Team AI assistant powered by Hermes Agent. DM me for help with code, research, debugging, and more.
   ```

5. **设置机器人命令**（可选——为用户提供命令菜单）：
   ```
   /setcommands
   ```
   选择你的机器人，然后粘贴：
   ```
   new - Start a fresh conversation
   model - Show or change the AI model
   status - Show session info
   help - Show available commands
   stop - Stop the current task
   ```

:::warning
请妥善保管你的机器人令牌。任何拥有该令牌的人都可以控制机器人。如果令牌泄露，请在 BotFather 中使用 `/revoke` 生成新令牌。
:::

---

## 步骤 2：配置消息网关

你有两个选择：交互式设置向导（推荐）或手动配置。

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

这将通过箭头键选择引导你完成所有步骤。选择 **Telegram**，粘贴你的机器人令牌，并在提示时输入你的用户 ID。

### 选项 B：手动配置

将以下行添加到 `~/.hermes/.env`：

```bash
# 来自 BotFather 的 Telegram 机器人令牌
TELEGRAM_BOT_TOKEN=7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...

# 你的 Telegram 用户 ID（数字）
TELEGRAM_ALLOWED_USERS=123456789
```

### 查找你的用户 ID

你的 Telegram 用户 ID 是一个数字值（不是你的用户名）。要找到它：

1. 在 Telegram 上向 [@userinfobot](https://t.me/userinfobot) 发送消息
2. 它会立即回复你的数字用户 ID
3. 将该数字复制到 `TELEGRAM_ALLOWED_USERS` 中

:::info
Telegram 用户 ID 是像 `123456789` 这样的永久数字。它们与你的 `@username` 不同，后者可以更改。在允许列表中始终使用数字 ID。
:::

---

## 步骤 3：启动消息网关

### 快速测试

首先在前台运行消息网关以确保一切正常：

```bash
hermes gateway
```

你应该会看到类似这样的输出：

```
[Gateway] Starting Hermes Gateway...
[Gateway] Telegram adapter connected
[Gateway] Cron scheduler started (tick every 60s)
```

打开 Telegram，找到你的机器人，并向它发送一条消息。如果它回复了，那就成功了。按 `Ctrl+C` 停止。

### 生产环境：安装为服务

为了部署一个持久化、能经受重启的版本：

```bash
hermes gateway install
sudo hermes gateway install --system   # 仅限 Linux：启动时系统服务
```

这将创建一个后台服务：在 Linux 上默认是用户级别的 **systemd** 服务，在 macOS 上是 **launchd** 服务，如果传递 `--system` 参数，则是在 Linux 上的启动时系统服务。

```bash
# Linux — 管理默认的用户服务
hermes gateway start
hermes gateway stop
hermes gateway status

# 查看实时日志
journalctl --user -u hermes-gateway -f

# 在 SSH 注销后保持运行
sudo loginctl enable-linger $USER

# Linux 服务器 — 明确的系统服务命令
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

```bash
# macOS — 管理服务
hermes gateway start
hermes gateway stop
tail -f ~/.hermes/logs/gateway.log
```

:::tip macOS PATH
launchd plist 在安装时捕获你的 shell PATH，以便消息网关子进程可以找到 Node.js 和 ffmpeg 等工具。如果你之后安装了新工具，请重新运行 `hermes gateway install` 以更新 plist。
:::

### 验证它正在运行

```bash
hermes gateway status
```

然后在 Telegram 上向你的机器人发送一条测试消息。你应该在几秒钟内收到回复。

---

## 步骤 4：设置团队访问权限

现在让我们给你的团队成员授予访问权限。有两种方法。

### 方法 A：静态允许列表

收集每个团队成员的 Telegram 用户 ID（让他们向 [@userinfobot](https://t.me/userinfobot) 发送消息），并将其添加为逗号分隔的列表：
```bash
# 在 ~/.hermes/.env 中
TELEGRAM_ALLOWED_USERS=123456789,987654321,555555555
```

更改后重启消息网关：

```bash
hermes gateway stop && hermes gateway start
```

### 方法 B：私聊配对（团队推荐）

私聊配对更加灵活——你不需要预先收集用户 ID。其工作原理如下：

1.  **队友私聊机器人**——由于他们不在允许列表中，机器人会回复一个一次性配对码：
    ```
    🔐 配对码：XKGH5N7P
    将此代码发送给机器人所有者进行批准。
    ```

2.  **队友将代码发送给你**（通过任何渠道——Slack、电子邮件、当面）

3.  **你在服务器上批准它**：
    ```bash
    hermes pairing approve telegram XKGH5N7P
    ```

4.  **他们加入成功**——机器人立即开始响应他们的消息

**管理已配对用户：**

```bash
# 查看所有待处理和已批准的用户
hermes pairing list

# 撤销某人的访问权限
hermes pairing revoke telegram 987654321

# 清除过期的待处理代码
hermes pairing clear-pending
```

:::tip
私聊配对非常适合团队，因为添加新用户时你不需要重启消息网关。批准会立即生效。
:::

### 安全注意事项

- **切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`** ——任何发现你机器人都可以在你的服务器上运行命令
- 配对码在 **1 小时** 后过期，并使用加密随机数生成
- 速率限制防止暴力攻击：每个用户每 10 分钟 1 次请求，每个平台最多 3 个待处理代码
- 5 次批准尝试失败后，平台将进入 1 小时锁定状态
- 所有配对数据都以 `chmod 0600` 权限存储

---

## 步骤 5：配置机器人

### 设置主频道

**主频道** 是机器人发送定时任务结果和主动消息的地方。如果没有主频道，计划任务将无处发送输出。

**选项 1：** 在机器人所在的任何 Telegram 群组或聊天中使用 `/sethome` 命令。

**选项 2：** 在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="团队更新"
```

要查找频道 ID，请将 [@userinfobot](https://t.me/userinfobot) 添加到群组中——它会报告群组的聊天 ID。

### 配置工具进度显示

控制机器人使用工具时显示的详细程度。在 `~/.hermes/config.yaml` 中：

```yaml
display:
  tool_progress: new    # off | new | all | verbose
```

| 模式 | 你将看到的内容 |
|------|-------------|
| `off` | 仅显示干净的响应——不显示工具活动 |
| `new` | 每个新工具调用的简要状态（推荐用于消息传递） |
| `all` | 每个工具调用及其详细信息 |
| `verbose` | 完整的工具输出，包括命令结果 |

用户也可以在聊天中通过 `/verbose` 命令按会话更改此设置。

### 使用 SOUL.md 设置人格

通过编辑 `~/.hermes/SOUL.md` 来自定义机器人的沟通方式：

完整指南请参阅 [在 Hermes 中使用 SOUL.md](/docs/guides/use-soul-with-hermes)。

```markdown
# 灵魂
你是一个乐于助人的团队助手。保持简洁和技术性。
对于任何代码，请使用代码块。省略客套话——团队
重视直接性。调试时，在猜测解决方案之前，
总是先询问错误日志。
```

### 添加项目上下文

如果你的团队从事特定项目，请创建上下文文件，以便机器人了解你的技术栈：

```markdown
<!-- ~/.hermes/AGENTS.md -->
# 团队上下文
- 我们使用 Python 3.12 搭配 FastAPI 和 SQLAlchemy
- 前端是 React 搭配 TypeScript
- CI/CD 在 GitHub Actions 上运行
- 生产环境部署到 AWS ECS
- 对于新代码，总是建议编写测试
```

:::info
上下文文件会被注入到每个会话的系统提示词中。保持简洁——每个字符都会计入你的 Token 预算。
:::

---

## 步骤 6：设置计划任务

在消息网关运行的情况下，你可以安排定期任务，将结果发送到你的团队频道。

### 每日站会摘要

在 Telegram 上向机器人发送消息：

```
每个工作日上午 9 点，检查位于
github.com/myorg/myproject 的 GitHub 仓库：
1. 过去 24 小时内打开/合并的拉取请求
2. 创建或关闭的问题
3. 主分支上的任何 CI/CD 失败
格式化为简短的站会风格摘要。
```

Agent 会自动创建一个定时任务，并将结果发送到你提问的聊天（或主频道）。

### 服务器健康检查

```
每 6 小时，使用 'df -h' 检查磁盘使用情况，使用 'free -h' 检查内存，
并使用 'docker ps' 检查 Docker 容器状态。报告任何异常情况——
分区使用率超过 80%、已重启的容器或高内存使用率。
```

### 管理计划任务

```bash
# 从 CLI
hermes cron list          # 查看所有计划任务
hermes cron status        # 检查调度程序是否正在运行

# 从 Telegram 聊天
/cron list                # 查看任务
/cron remove <job_id>     # 删除任务
```

:::warning
定时任务提示词在全新的会话中运行，没有先前对话的记忆。确保每个提示词包含 Agent 所需的 **所有** 上下文——文件路径、URL、服务器地址和清晰的指令。
:::

---

## 生产环境提示

### 使用 Docker 确保安全

在共享的团队机器人上，使用 Docker 作为终端后端，以便 Agent 命令在容器中运行，而不是在你的主机上：

```bash
# 在 ~/.hermes/.env 中
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=nikolaik/python-nodejs:python3.11-nodejs20
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
terminal:
  backend: docker
  container_cpu: 1
  container_memory: 5120
  container_persistent: true
```

这样，即使有人要求机器人运行破坏性命令，你的主机系统也会受到保护。

### 监控消息网关

```bash
# 检查消息网关是否正在运行
hermes gateway status

# 查看实时日志 (Linux)
journalctl --user -u hermes-gateway -f

# 查看实时日志 (macOS)
tail -f ~/.hermes/logs/gateway.log
```

### 保持 Hermes 更新

在 Telegram 上，向机器人发送 `/update`——它将拉取最新版本并重启。或者在服务器上：

```bash
hermes update
hermes gateway stop && hermes gateway start
```

### 日志位置
| 内容 | 位置 |
|------|----------|
| 消息网关日志 | `journalctl --user -u hermes-gateway` (Linux) 或 `~/.hermes/logs/gateway.log` (macOS) |
| 定时任务输出 | `~/.hermes/cron/output/{job_id}/{timestamp}.md` |
| 定时任务定义 | `~/.hermes/cron/jobs.json` |
| 配对数据 | `~/.hermes/pairing/` |
| 会话历史 | `~/.hermes/sessions/` |

---

## 深入探索

你已经拥有了一个可工作的团队 Telegram 助手。以下是一些后续步骤：

- **[安全指南](/docs/user-guide/security)** — 深入了解授权、容器隔离和命令审批
- **[消息网关](/docs/user-guide/messaging)** — 消息网关架构、会话管理和聊天命令的完整参考
- **[Telegram 设置](/docs/user-guide/messaging/telegram)** — 平台特定细节，包括语音消息和 TTS
- **[定时任务](/docs/user-guide/features/cron)** — 具有交付选项和 cron 表达式的高级定时任务调度
- **[上下文文件](/docs/user-guide/features/context-files)** — 用于项目知识的 AGENTS.md、SOUL.md 和 .cursorrules
- **[人格](/docs/user-guide/features/personality)** — 内置人格预设和自定义角色定义
- **添加更多平台** — 同一个消息网关可以同时运行 [Discord](/docs/user-guide/messaging/discord)、[Slack](/docs/user-guide/messaging/slack) 和 [WhatsApp](/docs/user-guide/messaging/whatsapp)

---

*有问题或遇到问题？请在 GitHub 上提交 issue — 欢迎贡献。*