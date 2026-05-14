---
sidebar_position: 4
title: "Slack"
description: "使用 Socket Mode 将 Hermes Agent 设置为 Slack 机器人"
---

# Slack 设置

使用 Socket Mode 将 Hermes Agent 作为机器人连接到 Slack。Socket Mode 使用 WebSocket 而非公共 HTTP 端点，因此您的 Hermes 实例无需公开访问——它可以在防火墙后、您的笔记本电脑上或私有服务器上工作。

:::warning 经典 Slack 应用已弃用
经典 Slack 应用（使用 RTM API）**已于 2025 年 3 月完全弃用**。Hermes 使用支持 Socket Mode 的现代 Bolt SDK。如果您有旧的经典应用，必须按照以下步骤创建一个新的。
:::

## 概述

| 组件 | 值 |
|-----------|-------|
| **库** | Python 的 `slack-bolt` / `slack_sdk`（Socket Mode） |
| **连接** | WebSocket —— 无需公共 URL |
| **所需的认证 Token** | Bot Token (`xoxb-`) + App-Level Token (`xapp-`) |
| **用户标识** | Slack 成员 ID（例如，`U01ABC2DEF3`） |

---

## 步骤 1：创建 Slack 应用

最快的方法是粘贴 Hermes 为您生成的清单。它一次性声明了所有内置斜杠命令（`/btw`、`/stop`、`/model`……）、所有必需的 OAuth 权限范围、所有事件订阅，并启用了 Socket Mode。

### 选项 A：使用 Hermes 生成的清单（推荐）

1.  生成清单：
    ```bash
    hermes slack manifest --write
    ```
    这会将 `~/.hermes/slack-manifest.json` 写入文件并打印粘贴说明。
2.  访问 [https://api.slack.com/apps](https://api.slack.com/apps) → **创建新应用** → **从应用清单创建**
3.  选择您的工作区，粘贴 JSON 内容，检查后点击 **下一步** → **创建**
4.  直接跳到 **步骤 6：将应用安装到工作区**。清单已为您处理了权限范围、事件和斜杠命令。

### 选项 B：从头开始（手动）

1.  访问 [https://api.slack.com/apps](https://api.slack.com/apps)
2.  点击 **创建新应用**
3.  选择 **从头开始**
4.  输入应用名称（例如，"Hermes Agent"）并选择您的工作区
5.  点击 **创建应用**

您将进入应用的 **基本信息** 页面。继续下面的步骤 2-6。

---

## 步骤 2：配置 Bot Token 权限范围

在侧边栏中导航到 **功能 → OAuth & 权限**。滚动到 **权限范围 → Bot Token 权限范围** 并添加以下内容：

| 权限范围 | 用途 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测在频道中被 @提及 |
| `channels:history` | 读取机器人所在公共频道中的消息 |
| `channels:read` | 列出和获取公共频道信息 |
| `groups:history` | 读取机器人被邀请加入的私密频道中的消息 |
| `im:history` | 读取直接消息历史 |
| `im:read` | 查看基本的 DM 信息 |
| `im:write` | 打开和管理 DM |
| `users:read` | 查找用户信息 |
| `files:read` | 读取和下载附件，包括语音笔记/音频 |
| `files:write` | 上传文件（图像、音频、文档） |

:::caution 缺少权限范围 = 缺少功能
没有 `channels:history` 和 `groups:history`，机器人**将无法接收频道中的消息**——它只能在 DM 中工作。没有 `files:read`，Hermes 可以聊天但**无法可靠读取用户上传的附件**。这些是最常被遗漏的权限范围。
:::

**可选权限范围：**

| 权限范围 | 用途 |
|-------|---------|
| `groups:read` | 列出和获取私密频道信息 |

---

## 步骤 3：启用 Socket Mode

Socket Mode 允许机器人通过 WebSocket 连接，而无需公共 URL。

1.  在侧边栏中，转到 **设置 → Socket Mode**
2.  将 **启用 Socket Mode** 切换为 ON
3.  系统会提示您创建 **App-Level Token**：
    - 为其命名，例如 `hermes-socket`（名称无关紧要）
    - 添加 **`connections:write`** 权限范围
    - 点击 **生成**
4.  **复制 Token** —— 它以 `xapp-` 开头。这是您的 `SLACK_APP_TOKEN`

:::tip
您始终可以在 **设置 → 基本信息 → App-Level Tokens** 下找到或重新生成 App-Level Token。
:::

---

## 步骤 4：订阅事件

此步骤至关重要——它控制机器人可以看到哪些消息。

1.  在侧边栏中，转到 **功能 → 事件订阅**
2.  将 **启用事件** 切换为 ON
3.  展开 **订阅机器人事件** 并添加：

| 事件 | 必需？ | 用途 |
|-------|-----------|---------|
| `message.im` | **是** | 机器人接收直接消息 |
| `message.channels` | **是** | 机器人接收其加入的**公共**频道中的消息 |
| `message.groups` | **推荐** | 机器人接收其被邀请加入的**私密**频道中的消息 |
| `app_mention` | **是** | 防止机器人被 @提及时 Bolt SDK 出错 |

4.  点击页面底部的 **保存更改**

:::danger 缺少事件订阅是头号设置问题
如果机器人在 DM 中工作但**在频道中不工作**，您几乎肯定忘记了添加 `message.channels`（用于公共频道）和/或 `message.groups`（用于私密频道）。没有这些事件，Slack 根本不会将频道消息传递给机器人。
:::

---

## 步骤 5：启用消息选项卡

此步骤启用与机器人的直接消息。没有它，用户尝试与机器人 DM 时会看到 **"向此应用发送消息的功能已关闭"**。

1.  在侧边栏中，转到 **功能 → 应用主页**
2.  滚动到 **显示选项卡**
3.  将 **消息选项卡** 切换为 ON
4.  勾选 **"允许用户从消息选项卡发送斜杠命令和消息"**

:::danger 没有此步骤，DM 将被完全阻止
即使拥有所有正确的权限范围和事件订阅，除非启用了消息选项卡，否则 Slack 将不允许用户向机器人发送直接消息。这是 Slack 平台的要求，而不是 Hermes 配置问题。
:::

---

## 步骤 6：将应用安装到工作区

1.  在侧边栏中，转到 **设置 → 安装应用**
2.  点击 **安装到工作区**
3.  检查权限并点击 **允许**
4.  授权后，您将看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5.  **复制此 Token** —— 这是您的 `SLACK_BOT_TOKEN`
:::tip
如果你之后更改了权限范围或事件订阅，**必须重新安装应用**才能使更改生效。安装应用页面会显示横幅提示你这样做。
:::

---

## 步骤 7：查找允许列表的用户 ID

Hermes 使用 Slack 的**成员 ID**（而非用户名或显示名称）来管理允许列表。

要查找成员 ID：

1.  在 Slack 中，点击用户的姓名或头像
2.  点击**查看完整个人资料**
3.  点击 **⋮**（更多）按钮
4.  选择**复制成员 ID**

成员 ID 的格式类似 `U01ABC2DEF3`。你至少需要你自己的成员 ID。

---

## 步骤 8：配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 逗号分隔的成员 ID

# 可选
SLACK_HOME_CHANNEL=C01234567890              # 定时任务/计划消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 主频道的人类可读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 提示时选择 Slack
```

然后启动消息网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机启动的系统服务
```

---

## 步骤 9：邀请 Bot 加入频道

启动消息网关后，你需要**邀请 Bot** 到你希望它响应的任何频道：

```
/invite @Hermes Agent
```

Bot **不会**自动加入频道。你必须单独邀请它加入每个频道。

---

## 斜杠命令

每个 Hermes 命令（`/btw`、`/stop`、`/new`、`/model`、`/help`……）都是原生的 Slack 斜杠命令——其工作方式与 Telegram 和 Discord 上完全相同。在 Slack 中输入 `/`，自动完成选择器会列出每个 Hermes 命令及其描述。

底层原理：Hermes 附带一个生成的 Slack 应用清单（见步骤 1，选项 A），该清单将 [`COMMAND_REGISTRY`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/commands.py) 中的每个命令都声明为斜杠命令。在 Socket 模式下，无论清单的 `url` 字段如何，Slack 都会通过 WebSocket 路由命令事件。

### 更新后刷新斜杠命令

当 Hermes 添加新命令时（例如在 `hermes update` 之后），重新生成清单并更新你的 Slack 应用：

```bash
hermes slack manifest --write
```

然后在 Slack 中：
1.  打开 [https://api.slack.com/apps](https://api.slack.com/apps) → 你的 Hermes 应用
2.  **Features → App Manifest → Edit**
3.  粘贴 `~/.hermes/slack-manifest.json` 的新内容
4.  **Save**。如果权限范围或斜杠命令发生更改，Slack 会提示重新安装应用。

### 旧版 `/hermes <子命令>` 仍然有效

为了向后兼容旧版清单，你仍然可以输入 `/hermes btw run the tests`——Hermes 会以与 `/btw run the tests` 相同的方式路由它。自由格式的问题也有效：`/hermes what's the weather?` 会被视为常规消息。

### 在话题内使用命令（`!cmd` 前缀）

Slack 本身会阻止在话题回复中使用原生斜杠命令——尝试在话题中输入 `/queue`，Slack 会回复 *"/queue is not supported in threads. Sorry!"*。没有应用端设置可以重新启用它们；Slack 永远不会将它们传递给 Hermes。

作为一种变通方法，Hermes 将前导的 `!` 识别为可在话题（以及任何其他地方）使用的替代命令前缀。在常规话题回复中输入 `!queue`、`!stop`、`!model gpt-5.4` 等——Hermes 会将其视为与斜杠形式相同，并在同一话题中回复。

只有第一个 Token 会与已知命令列表进行核对，因此像 `!nice work` 这样的随意消息会原封不动地传递给 Agent。

### 高级：仅输出斜杠命令数组

如果你手动维护 Slack 清单，并且只想要斜杠命令列表：

```bash
hermes slack manifest --slashes-only > /tmp/slashes.json
```

将该数组粘贴到现有清单的 `features.slash_commands` 键中。

---

## Bot 如何响应

了解 Hermes 在不同上下文中的行为：

| 上下文 | 行为 |
|---------|----------|
| **私信** | Bot 响应每条消息——无需 @提及 |
| **频道** | Bot **仅在 @提及时响应**（例如，`@Hermes Agent what time is it?`）。在频道中，Hermes 会在附加到该消息的话题中回复。 |
| **话题** | 如果你在现有话题内 @提及 Hermes，它会在同一话题中回复。一旦 Bot 在某个话题中拥有活动会话，**该话题中的后续回复无需 @提及**——Bot 会自然地跟随对话。 |

:::tip
在频道中，始终 @提及 Bot 以开始对话。一旦 Bot 在某个话题中处于活动状态，你可以在该话题中回复而无需提及它。在话题之外，未 @提及的消息会被忽略，以防止在繁忙的频道中产生噪音。
:::

---

## 配置选项

除了步骤 8 中必需的环境变量外，你还可以通过 `~/.hermes/config.yaml` 自定义 Slack Bot 的行为。

### 话题与回复行为

```yaml
platforms:
  slack:
    # 控制多部分响应如何创建话题
    # "off"   — 从不将回复创建为原消息的话题
    # "first" — 第一个分块创建为原消息的话题（默认）
    # "all"   — 所有分块都创建为原消息的话题
    reply_to_mode: "first"

    extra:
      # 是否在话题中回复（默认：true）。
      # 当为 false 时，频道消息会直接在频道中回复，而不是创建话题。现有话题内的消息仍然在话题内回复。
      reply_in_thread: true

      # 同时将话题回复发布到主频道
      # （Slack 的"Also send to channel"功能）。
      # 仅广播第一个回复的第一个分块。
      reply_broadcast: false
```

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多部分消息的话题模式：`"off"`、`"first"` 或 `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | 当为 `false` 时，频道消息会直接回复，而不是创建话题。现有话题内的消息仍然在话题内回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 当为 `true` 时，话题回复也会发布到主频道。仅广播第一个分块。 |
### 会话隔离

```yaml
# 全局设置 — 适用于 Slack 和所有其他平台
group_sessions_per_user: true
```

当设置为 `true`（默认值）时，共享频道中的每个用户都将拥有自己独立的对话会话。两个人在 `#general` 频道中与 Hermes 交谈将拥有各自独立的历史记录和上下文。

如果希望整个频道共享一个对话会话的协作模式，请设置为 `false`。请注意，这意味着用户将共享上下文增长和 Token 成本，并且一个用户的 `/reset` 命令会为所有人清除会话。

### 提及与触发行为

```yaml
slack:
  # 在频道中要求 @提及（这是默认行为；
  # Slack 适配器无论如何都会在频道中强制执行 @提及门控，
  # 但你可以显式设置此选项以与其他平台保持一致）
  require_mention: true

  # 防止线程自动参与：仅回复包含显式 @提及的频道消息。
  # 当此选项为 OFF（默认）时，Slack 可以“自动参与”——记住线程中过去的提及并跟进机器人消息回复，
  # 并在没有新提及的情况下恢复活动会话。
  # 当 strict_mention 为 ON 时，Hermes 在回复之前，每条新的频道消息都必须 @提及机器人。
  strict_mention: false

  # 触发机器人的自定义提及模式
  # （除了默认的 @提及检测之外）
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # 附加到每条外发消息前的文本
  reply_prefix: ""
```

:::tip 何时使用 `strict_mention`
在繁忙的工作区中，当 Slack 默认的“机器人记住此线程”行为让用户感到意外时，请将此设置为 `true`——例如，在一个很长的技术支持线程中，机器人在开始时提供了帮助，而你更希望它保持静默，除非被再次明确提及。私信和活动的交互式会话不受影响。
:::

:::info
Slack 支持两种模式：默认情况下需要 `@提及` 来开始对话，但你可以通过 `SLACK_FREE_RESPONSE_CHANNELS`（逗号分隔的频道 ID）或 `config.yaml` 中的 `slack.free_response_channels` 选择特定的频道退出此限制。一旦机器人在线程中拥有活动会话，后续的线程回复就不需要提及。在私信中，机器人总是无需提及即可回复。
:::

### 未授权用户处理

```yaml
slack:
  # 当未授权用户（不在 SLACK_ALLOWED_USERS 中）向机器人发送私信时会发生什么
  # "pair"   — 提示他们输入配对码（默认）
  # "ignore" — 静默丢弃消息
  unauthorized_dm_behavior: "pair"
```

你也可以为所有平台全局设置此选项：

```yaml
unauthorized_dm_behavior: "pair"
```

`slack:` 下的平台特定设置优先于全局设置。

### 语音转录

```yaml
# 全局设置 — 启用/禁用传入语音消息的自动转录
stt_enabled: true
```

当设置为 `true`（默认值）时，传入的音频消息在被 Agent 处理之前，会使用配置的 STT 提供商自动转录。

### 完整示例

```yaml
# 全局消息网关设置
group_sessions_per_user: true
unauthorized_dm_behavior: "pair"
stt_enabled: true

# Slack 特定设置
slack:
  require_mention: true
  unauthorized_dm_behavior: "pair"

# 平台配置
platforms:
  slack:
    reply_to_mode: "first"
    extra:
      reply_in_thread: true
      reply_broadcast: false
```

---

## 主频道

将 `SLACK_HOME_CHANNEL` 设置为一个频道 ID，Hermes 将向该频道发送定时消息、定时任务结果和其他主动通知。要查找频道 ID：

1. 在 Slack 中右键点击频道名称
2. 点击 **查看频道详情**
3. 滚动到底部 — 频道 ID 显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

确保机器人**已被邀请到该频道**（`/invite @Hermes Agent`）。

---

## 多工作区支持

Hermes 可以使用单个消息网关实例同时连接到**多个 Slack 工作区**。每个工作区都使用其自己的机器人用户 ID 独立进行身份验证。

### 配置

在 `SLACK_BOT_TOKEN` 中以**逗号分隔的列表**形式提供多个机器人令牌：

```bash
# 多个机器人令牌 — 每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# 单个应用级令牌仍用于 Socket 模式
SLACK_APP_TOKEN=xapp-your-app-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth 令牌文件

除了环境变量或配置文件中的令牌外，Hermes 还会从以下位置的 **OAuth 令牌文件** 加载令牌：

```
~/.hermes/slack_tokens.json
```

该文件是一个 JSON 对象，将团队 ID 映射到令牌条目：

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

此文件中的令牌将与通过 `SLACK_BOT_TOKEN` 指定的任何令牌合并。重复的令牌会自动去重。

### 工作原理

- 列表中的**第一个令牌**是主令牌，用于 Socket 模式连接（AsyncApp）。
- 每个令牌在启动时通过 `auth.test` 进行身份验证。消息网关将每个 `team_id` 映射到其自己的 `WebClient` 和 `bot_user_id`。
- 当消息到达时，Hermes 使用特定于工作区的正确客户端进行响应。
- 主 `bot_user_id`（来自第一个令牌）用于与期望单一机器人身份的功能保持向后兼容。

---

## 语音消息

Hermes 支持 Slack 上的语音功能：

- **传入：** 语音/音频消息使用配置的 STT 提供商自动转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **传出：** TTS 响应作为音频文件附件发送

---

## 按频道提示词

为特定的 Slack 频道分配临时的系统提示词。该提示词在每次交互时于运行时注入——永远不会持久化到对话历史记录中——因此更改会立即生效。

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      你是一名研究助理。专注于学术来源、引用和简洁的综述。
    "C02ENGINEERING": |
      代码审查模式。请精确关注边界情况和性能影响。
```
键是 Slack 频道 ID（可通过频道详情 → "关于" → 滚动到底部找到）。匹配频道中的所有消息都会收到该提示词，作为一条临时的系统指令注入。

## 按频道技能绑定

每当在特定频道或私信中开始新会话时，自动加载一个技能。与按频道提示词（在每次对话轮次中注入）不同，技能绑定在**会话开始时**将技能内容作为用户消息注入——它成为对话历史的一部分，无需在后续轮次中重新加载。

这非常适合用于有特定目的的私信或频道（例如抽认卡、特定领域问答机器人、支持分流频道等），在这些场景中，您不希望模型自身的技能选择器来决定是否在每次简短回复时加载。

```yaml
slack:
  channel_skill_bindings:
    # 私信频道 — 始终以 "german-flashcards" 模式运行
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # 研究频道 — 按顺序预加载多个技能
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # 简写形式：单个技能作为字符串
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

注意事项：
- 绑定通过频道 ID 匹配。对于绑定频道中的线程消息，线程会继承父频道的绑定。
- 技能仅在会话开始时加载（新会话或自动重置后）。如果您更改了绑定，请运行 `/new` 或等待会话自动重置以使更改生效。
- 可与 `channel_prompts` 结合使用，在技能指令之上添加按频道的语气/约束。

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人不回复私信 | 验证 `message.im` 是否在您的事件订阅中，并且应用已重新安装 |
| 机器人在私信中工作，但在频道中不工作 | **最常见问题。** 将 `message.channels` 和 `message.groups` 添加到事件订阅，重新安装应用，并使用 `/invite @Hermes Agent` 邀请机器人加入频道 |
| 机器人在频道中不响应 @提及 | 1) 检查 `message.channels` 事件是否已订阅。2) 必须邀请机器人加入频道。3) 确保添加了 `channels:history` 权限范围。4) 在更改权限范围/事件后重新安装应用 |
| 机器人忽略私密频道中的消息 | 同时添加 `message.groups` 事件订阅和 `groups:history` 权限范围，然后重新安装应用并 `/invite` 机器人 |
| 在私信中显示"向此应用发送消息已关闭" | 在应用主页设置中启用**消息选项卡**（参见步骤 5） |
| "not_authed" 或 "invalid_auth" 错误 | 重新生成您的 Bot Token 和 App Token，更新 `.env` 文件 |
| 机器人有响应但无法在频道中发帖 | 使用 `/invite @Hermes Agent` 邀请机器人加入频道 |
| 机器人可以聊天但无法读取上传的图片/文件 | 添加 `files:read` 权限，然后**重新安装**应用。当 Slack 返回权限范围/认证/权限失败时，Hermes 现在会在聊天中显示附件访问诊断信息。 |
| `missing_scope` 错误 | 在 OAuth & Permissions 中添加所需权限范围，然后**重新安装**应用 |
| Socket 频繁断开连接 | 检查您的网络；Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了权限范围/事件但没有任何变化 | 在更改任何权限范围或事件订阅后，您**必须重新安装**应用到您的工作区 |

### 快速检查清单

如果机器人在频道中无法工作，请验证**所有**以下项目：

1. ✅ `message.channels` 事件已订阅（针对公开频道）
2. ✅ `message.groups` 事件已订阅（针对私密频道）
3. ✅ `app_mention` 事件已订阅
4. ✅ `channels:history` 权限范围已添加（针对公开频道）
5. ✅ `groups:history` 权限范围已添加（针对私密频道）
6. ✅ 在添加权限范围/事件后，应用已**重新安装**
7. ✅ 机器人已**被邀请**加入频道 (`/invite @Hermes Agent`)
8. ✅ 您在消息中**@提及**了机器人

---

## 安全

:::warning
**务必设置 `SLACK_ALLOWED_USERS`**，包含授权用户的 Member ID。如果没有此设置，
作为安全措施，消息网关将默认**拒绝所有消息**。切勿分享您的 bot token ——
像对待密码一样对待它们。
:::

- Token 应存储在 `~/.hermes/.env` 中（文件权限设置为 `600`）
- 定期通过 Slack 应用设置轮换 token
- 审计谁有权访问您的 Hermes 配置目录
- Socket 模式意味着没有公开的端点暴露 —— 减少了一个攻击面