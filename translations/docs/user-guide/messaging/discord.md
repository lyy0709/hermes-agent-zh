---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

# Discord 设置

Hermes Agent 可作为机器人集成到 Discord 中，让你通过私信或服务器频道与你的 AI 助手聊天。机器人接收你的消息，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）进行处理，并实时回复。它支持文本、语音消息、文件附件和斜杠命令。

在开始设置之前，以下是大多数人最想了解的部分：Hermes 加入你的服务器后的行为方式。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **私信** | Hermes 会回复每条消息。无需 `@提及`。每条私信都有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 仅在 `@提及` 它时才会回复。如果你在频道中发布消息但没有提及它，Hermes 会忽略该消息。 |
| **自由回复频道** | 你可以使用 `DISCORD_FREE_RESPONSE_CHANNELS` 将特定频道设为免提及，或使用 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及要求。 |
| **主题** | Hermes 在同一主题内回复。除非该主题或其父频道被配置为自由回复，否则提及规则仍然适用。主题的会话历史记录与父频道隔离。 |
| **多用户共享频道** | 默认情况下，出于安全和清晰度考虑，Hermes 会在频道内为每个用户隔离会话历史记录。两个人在同一频道中交谈，除非你明确禁用此功能，否则不会共享一个对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @提及了其他用户但**没有**提及机器人，Hermes 将保持静默。这可以防止机器人跳入针对其他人的对话。如果你希望机器人响应所有消息，无论提及了谁，请将其设置为 `false`。这仅适用于服务器频道，不适用于私信。 |

:::tip
如果你想要一个普通的机器人帮助频道，让人们无需每次都标记 Hermes 即可与之交谈，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS`。
:::

### Discord 消息网关模型

Discord 上的 Hermes 不是一个无状态回复的 Webhook。它通过完整的消息网关运行，这意味着每条传入消息都会经过：

1.  授权 (`DISCORD_ALLOWED_USERS`)
2.  提及 / 自由回复检查
3.  会话查找
4.  会话记录加载
5.  正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6.  将响应发送回 Discord

这很重要，因为在繁忙服务器中的行为取决于 Discord 的路由和 Hermes 的会话策略。

### Discord 中的会话模型

默认情况下：

*   每条私信都有独立的会话
*   每个服务器主题都有独立的会话命名空间
*   共享频道中的每个用户在该频道内都有自己独立的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道与 Hermes 交谈，默认情况下 Hermes 会将其视为独立的对话，即使他们使用的是同一个可见的 Discord 频道。

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

*   用户共享上下文增长和 Token 成本
*   一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
*   一个人正在运行的任务可能会中断另一个人在同一房间的后续操作

### 中断和并发

Hermes 通过会话键跟踪正在运行的 Agent。

使用默认的 `group_sessions_per_user: true`：

*   Alice 中断她自己正在运行的请求只会影响她在该频道中的会话
*   Bob 可以在同一频道继续交谈，而不会继承 Alice 的历史记录或中断 Alice 的运行

使用 `group_sessions_per_user: false`：

*   整个房间共享该频道/主题的一个正在运行的 Agent 槽位
*   来自不同用户的后续消息可能会相互中断或排队

本指南将引导你完成完整的设置过程——从在 Discord 开发者门户创建机器人到发送第一条消息。

## 步骤 1：创建 Discord 应用

1.  前往 [Discord 开发者门户](https://discord.com/developers/applications)，使用你的 Discord 账户登录。
2.  点击右上角的 **New Application**。
3.  为你的应用输入一个名称（例如 "Hermes Agent"）并接受开发者服务条款。
4.  点击 **Create**。

你将进入 **General Information** 页面。记下 **Application ID** —— 稍后构建邀请链接时需要用到它。

## 步骤 2：创建机器人

1.  在左侧边栏中，点击 **Bot**。
2.  Discord 会自动为你的应用创建一个机器人用户。你将看到机器人的用户名，你可以自定义它。
3.  在 **Authorization Flow** 下：
    *   将 **Public Bot** 设置为 **ON** —— 这是使用 Discord 提供的邀请链接（推荐）所必需的。这允许 Installation 选项卡生成默认的授权 URL。
    *   将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
你可以在此页面为你的机器人设置自定义头像和横幅。这将是用户在 Discord 中看到的内容。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），你**必须**在步骤 5 中使用 **Manual URL** 方法，而不是 Installation 选项卡。Discord 提供的链接要求启用 Public Bot。
:::

## 步骤 3：启用特权网关意图

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人将连接到 Discord，但**无法读取消息内容**。

在 **Bot** 页面上，向下滚动到 **Privileged Gateway Intents**。你会看到三个开关：

| 意图 | 用途 | 是否必需？ |
|--------|---------|-----------|
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |
**启用服务器成员意图和消息内容意图**，将它们切换为**开启**状态。

- 如果没有**消息内容意图**，你的机器人会收到消息事件，但消息文本是空的——机器人实际上看不到你输入的内容。
- 如果没有**服务器成员意图**，机器人无法解析允许用户列表中的用户名，可能无法识别谁在给它发消息。

:::warning[这是 Discord 机器人无法工作的首要原因]
如果你的机器人显示在线但从不回复消息，**消息内容意图**几乎肯定是禁用的。返回 [开发者门户](https://discord.com/developers/applications)，选择你的应用 → Bot → Privileged Gateway Intents，确保**消息内容意图**已切换为 ON。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果你的机器人在**少于 100 个服务器**中，你可以自由地开启和关闭意图。
- 如果你的机器人在**100 个或更多服务器**中，Discord 要求你提交验证申请才能使用特权意图。对于个人使用，这通常不是问题。

点击页面底部的 **Save Changes**。

## 步骤 4：获取机器人 Token

机器人 Token 是 Hermes Agent 用来以你的机器人身份登录的凭证。仍在 **Bot** 页面：

1. 在 **Token** 部分下，点击 **Reset Token**。
2. 如果你的 Discord 账户启用了双因素认证，请输入你的 2FA 代码。
3. Discord 将显示你的新 Token。**立即复制它。**

:::warning[Token 仅显示一次]
Token 只显示一次。如果你丢失了它，你需要重置并生成一个新的。切勿公开分享你的 Token 或将其提交到 Git——任何拥有此 Token 的人都可以完全控制你的机器人。
:::

将 Token 安全地存储在某处（例如密码管理器）。你将在步骤 8 中需要它。

## 步骤 5：生成邀请 URL

你需要一个 OAuth2 URL 来邀请机器人加入你的服务器。有两种方法可以做到这一点：

### 选项 A：使用 Installation 标签页（推荐）

:::note[需要公开机器人]
此方法要求**在步骤 2 中将 Public Bot 设置为 ON**。如果你将 Public Bot 设置为 OFF，请改用下面的手动 URL 方法。
:::

1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 Guild Install 的 **Default Install Settings** 下：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

### 选项 B：手动 URL

你可以直接使用以下格式构建邀请 URL：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为步骤 1 中的 Application ID。

### 所需权限

这些是你的机器人需要的最低权限：

- **查看频道** — 查看它有权限访问的频道
- **发送消息** — 回复你的消息
- **嵌入链接** — 格式化富文本响应
- **附加文件** — 发送图片、音频和文件输出
- **读取消息历史** — 维护会话上下文

### 推荐的额外权限

- **在线程中发送消息** — 在线程对话中回复
- **添加反应** — 对消息做出反应以确认

### 权限整数值

| 级别 | 权限整数值 | 包含内容 |
|-------|-------------------|-----------------|
| 最低 | `117760` | 查看频道、发送消息、读取消息历史、附加文件 |
| 推荐 | `274878286912` | 以上所有权限，外加嵌入链接、在线程中发送消息、添加反应 |

## 步骤 6：邀请到你的服务器

1. 在浏览器中打开邀请 URL（来自 Installation 标签页或你构建的手动 URL）。
2. 在 **Add to Server** 下拉菜单中，选择你的服务器。
3. 点击 **Continue**，然后点击 **Authorize**。
4. 如果出现提示，请完成 CAPTCHA。

:::info
你需要在 Discord 服务器上拥有 **Manage Server** 权限才能邀请机器人。如果在下拉菜单中看不到你的服务器，请让服务器管理员使用邀请链接。
:::

授权后，机器人将出现在你服务器的成员列表中（在启动 Hermes 消息网关之前，它将显示为离线状态）。

## 步骤 7：查找你的 Discord 用户 ID

Hermes Agent 使用你的 Discord 用户 ID 来控制谁可以与机器人交互。查找方法如下：

1. 打开 Discord（桌面版或网页版）。
2. 进入 **Settings** → **Advanced** → 将 **Developer Mode** 切换为 **ON**。
3. 关闭设置。
4. 右键单击你自己的用户名（在消息、成员列表或你的个人资料中）→ **Copy User ID**。

你的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式也允许你以同样的方式复制**频道 ID** 和**服务器 ID**——右键单击频道或服务器名称并选择 Copy ID。如果你想手动设置一个主频道，你将需要一个频道 ID。
:::

## 步骤 8：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

出现提示时选择 **Discord**，然后在被要求时粘贴你的机器人 Token 和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许的用户（逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动消息网关：

```bash
hermes gateway
```

机器人应该在几秒钟内在 Discord 中上线。给它发送一条消息——可以是私信，也可以是它能看到的频道——进行测试。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 配置参考

Discord 行为通过两个文件控制：**`~/.hermes/.env`** 用于凭证和环境级别的开关，以及 **`~/.hermes/config.yaml`** 用于结构化设置。当两者都设置时，环境变量始终优先于 config.yaml 中的值。

### 环境变量（`.env`）
| 变量 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord 开发者门户](https://discord.com/developers/applications) 的 Bot Token。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与 Bot 交互的 Discord 用户 ID，以逗号分隔。如果未设置此项 **或** `DISCORD_ALLOWED_ROLES`，消息网关将拒绝所有用户。 |
| `DISCORD_ALLOWED_ROLES` | 否 | — | 以逗号分隔的 Discord 角色 ID。拥有这些角色之一的成员即被授权 —— 与 `DISCORD_ALLOWED_USERS` 是 OR（或）逻辑。连接时自动启用 **Server Members Intent**。在管理团队变动时很有用：新管理员一旦被授予角色即可获得访问权限，无需推送配置。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | Bot 发送主动消息（定时任务输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 在日志和状态输出中显示的主频道名称。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 当为 `true` 时，Bot 仅在服务器频道中被 `@提及` 时才响应。设置为 `false` 可在所有频道中响应所有消息。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，在这些频道中，即使 `DISCORD_REQUIRE_MENTION` 为 `true`，Bot 也无需 `@提及` 即可响应。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 当为 `true` 时，如果一条消息 `@提及` 了其他用户但**没有**提及 Bot，Bot 将保持静默。防止 Bot 跳入针对其他人的对话。仅适用于服务器频道，不适用于私信。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 当为 `true` 时，在文本频道中为每次 `@提及` 自动创建一个新线程，以便每个对话都是隔离的（类似于 Slack 的行为）。已在线程内或私信中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制 Bot 如何处理来自其他 Discord Bot 的消息。`"none"` —— 忽略所有其他 Bot。`"mentions"` —— 仅接受 `@提及` Hermes 的 Bot 消息。`"all"` —— 接受所有 Bot 消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 当为 `true` 时，Bot 在处理过程中为消息添加表情符号反应（开始时 👀，成功时 ✅，错误时 ❌）。设置为 `false` 可完全禁用反应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，Bot 在这些频道中**永不**响应，即使被 `@提及`。优先级高于所有其他频道设置。 |
| `DISCORD_ALLOWED_CHANNELS` | 否 | — | 以逗号分隔的频道 ID。设置后，Bot**仅**在这些频道中响应（如果允许，还包括私信）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。可与 `DISCORD_IGNORED_CHANNELS` 结合使用以表达允许/拒绝规则。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，在这些频道中，Bot 直接在频道中响应，而不是创建线程。仅当 `DISCORD_AUTO_THREAD` 为 `true` 时相关。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` —— 从不回复原始消息，`"first"` —— 仅在第一条消息块上回复引用（默认），`"all"` —— 在每个消息块上都回复引用。 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 否 | `false` | 当为 `false`（默认）时，即使 Bot 的响应包含这些 Token，也无法提及 `@everyone` 或 `@here`。设置为 `true` 以重新启用。请参阅下面的 [提及控制](#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 否 | `false` | 当为 `false`（默认）时，Bot 无法提及 `@角色`。设置为 `true` 以允许。 |
| `DISCORD_ALLOW_MENTION_USERS` | 否 | `true` | 当为 `true`（默认）时，Bot 可以通过 ID 提及单个用户。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 否 | `true` | 当为 `true`（默认）时，回复消息会提及原始作者。 |
| `DISCORD_PROXY` | 否 | — | 用于 Discord 连接的代理 URL（HTTP、WebSocket、REST）。覆盖 `HTTPS_PROXY`/`ALL_PROXY`。支持 `http://`、`https://` 和 `socks5://` 协议。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 否 | `0.6` | 适配器在刷新排队的文本块之前等待的宽限窗口。用于平滑流式输出。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 否 | `0.1` | 当单条消息超过 Discord 长度限制时，分割块之间的延迟。 |

### 配置文件 (`config.yaml`)

`~/.hermes/config.yaml` 中的 `discord` 部分与上述环境变量对应。`config.yaml` 中的设置作为默认值应用 —— 如果已设置等效的环境变量，则环境变量优先。

```yaml
# Discord 特定设置
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  free_response_channels: ""      # 以逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # 在 @提及 时自动创建线程
  reactions: true                 # 处理过程中添加表情符号反应
  ignored_channels: []            # Bot 永不响应的频道 ID
  no_thread_channels: []          # Bot 响应时不创建线程的频道 ID
  channel_prompts: {}             # 每个频道的临时系统提示词
  allow_mentions:                 # Bot 允许提及的内容（安全默认值）
    everyone: false               # @everyone / @here 提及（默认：false）
    roles: false                  # @角色 提及（默认：false）
    users: true                   # @用户 提及（默认：true）
    replied_user: true            # 回复引用会提及作者（默认：true）

# 会话隔离（适用于所有消息网关平台，不仅仅是 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

#### `discord.require_mention`

**类型：** 布尔值 — **默认值：** `true`

启用后，Bot 仅在服务器频道中被直接 `@提及` 时才响应。无论此设置如何，私信始终会得到响应。

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

Bot 无需 `@提及` 即可响应所有消息的频道 ID。接受逗号分隔的字符串或 YAML 列表：
```yaml
# 字符串格式
discord:
  free_response_channels: "1234567890,9876543210"

# 列表格式
discord:
  free_response_channels:
    - 1234567890
    - 9876543210
```

如果一个线程的父频道在此列表中，该线程也将变为免提及。

#### `discord.auto_thread`

**类型:** boolean — **默认值:** `true`

启用后，常规文本频道中的每次 `@提及` 都会自动为该对话创建一个新线程。这可以保持主频道整洁，并为每次对话提供独立的会话历史记录。线程创建后，在该线程中发送的后续消息不再需要 `@提及` —— 机器人知道它已经在参与其中。

在现有线程或私信中发送的消息不受此设置影响。

#### `discord.reactions`

**类型:** boolean — **默认值:** `true`

控制机器人是否在消息上添加表情符号作为视觉反馈：
- 👀 当机器人开始处理你的消息时添加
- ✅ 当响应成功发送时添加
- ❌ 如果在处理过程中发生错误时添加

如果你觉得这些反应分散注意力，或者机器人的角色没有**添加反应**权限，请禁用此功能。

#### `discord.ignored_channels`

**类型:** string 或 list — **默认值:** `[]`

机器人**绝不**响应的频道 ID，即使被直接 `@提及`。此设置具有最高优先级 —— 如果一个频道在此列表中，机器人将静默忽略该处的所有消息，无论 `require_mention`、`free_response_channels` 或任何其他设置如何。

```yaml
# 字符串格式
discord:
  ignored_channels: "1234567890,9876543210"

# 列表格式
discord:
  ignored_channels:
    - 1234567890
    - 9876543210
```

如果一个线程的父频道在此列表中，该线程中的消息也会被忽略。

#### `discord.no_thread_channels`

**类型:** string 或 list — **默认值:** `[]`

机器人直接在频道中响应而不是自动创建线程的频道 ID。这仅在 `auto_thread` 为 `true`（默认值）时有效。在这些频道中，机器人像普通消息一样内联响应，而不是生成新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # 机器人在这里内联响应
```

适用于专门用于机器人交互的频道，在这些频道中创建线程会增加不必要的噪音。

#### `discord.channel_prompts`

**类型:** mapping — **默认值:** `{}`

每个频道的临时系统提示词，在匹配的 Discord 频道或线程中的每一轮对话中注入，但不会持久化到对话历史记录中。

```yaml
discord:
  channel_prompts:
    "1234567890": |
      此频道用于研究任务。请优先进行深度比较、引用和简洁的综合分析。
    "9876543210": |
      此论坛用于治疗式支持。请保持温暖、接地气且不带评判。
```

行为：
- 精确的线程/频道 ID 匹配优先。
- 如果消息到达线程或论坛帖子内部，并且该线程没有明确的条目，Hermes 将回退到父频道/论坛 ID。
- 提示词在运行时临时应用，因此更改它们会立即影响未来的轮次，而无需重写过去的会话历史记录。

#### `group_sessions_per_user`

**类型:** boolean — **默认值:** `true`

这是一个全局消息网关设置（非 Discord 专用），用于控制同一频道中的用户是否拥有独立的会话历史记录。

当为 `true` 时：在 `#research` 中交谈的 Alice 和 Bob 各自与 Hermes 拥有独立的对话。当为 `false` 时：整个频道共享一个对话记录和一个运行中的 Agent 槽位。

```yaml
group_sessions_per_user: true
```

有关每种模式的完整含义，请参阅上面的[会话模型](#session-model-in-discord)部分。

#### `display.tool_progress`

**类型:** string — **默认值:** `"all"` — **可选值:** `off`, `new`, `all`, `verbose`

控制机器人在处理过程中是否在聊天中发送进度消息（例如，“正在读取文件...”、“正在运行终端命令...”）。这是一个全局消息网关设置，适用于所有平台。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度消息
- `new` — 仅显示每轮的第一个工具调用
- `all` — 显示所有工具调用（在网关消息中截断为 40 个字符）
- `verbose` — 显示完整的工具调用详情（可能产生长消息）

#### `display.tool_progress_command`

**类型:** boolean — **默认值:** `false`

启用后，在消息网关中提供 `/verbose` 斜杠命令，让你无需编辑 config.yaml 即可循环切换工具进度模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 命令，以打开基于下拉菜单的模型选择器：

1.  **提供商选择** — 一个显示可用提供商（最多 25 个）的 Select 下拉菜单。
2.  **模型选择** — 第二个下拉菜单，显示所选提供商的模型（最多 25 个）。

选择器在 120 秒后超时。只有授权用户（在 `DISCORD_ALLOWED_USERS` 中的用户）可以与之交互。如果你知道模型名称，可以直接输入 `/model <名称>`。

## 技能的原生斜杠命令

Hermes 会自动将已安装的技能注册为**原生 Discord 应用命令**。这意味着技能会出现在 Discord 的自动补全 `/` 菜单中，与内置命令并列。

- 每个技能都成为一个 Discord 斜杠命令（例如，`/code-review`、`/ascii-art`）
- 技能接受一个可选的 `args` 字符串参数
- Discord 限制每个机器人最多 100 个应用命令 —— 如果你的技能数量超过可用槽位，额外的技能将被跳过，并在日志中发出警告
- 技能在机器人启动时与内置命令（如 `/model`、`/reset` 和 `/background`）一起注册

无需额外配置 —— 任何通过 `hermes skills install` 安装的技能都会在下次网关重启时自动注册为 Discord 斜杠命令。

## 主频道

你可以指定一个“主频道”，机器人将在此发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：
### 使用斜杠命令

在机器人所在的任意 Discord 频道中，输入 `/sethome`。该频道将成为主频道。

### 手动配置

将这些内容添加到你的 `~/.hermes/.env` 文件中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（右键点击 → 在开发者模式下复制频道 ID）。

## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **传入的语音消息** 会自动使用配置的 STT 提供商进行转录：本地的 `faster-whisper`（无需密钥）、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）。
- **文本转语音**：使用 `/voice tts` 让机器人在发送文本回复的同时发送语音音频回复。
- **Discord 语音频道**：Hermes 也可以加入语音频道，听取用户发言，并在频道内进行回复。

完整的设置和操作指南，请参阅：
- [语音模式](/docs/user-guide/features/voice-mode)
- [与 Hermes 一起使用语音模式](/docs/guides/use-voice-mode-with-hermes)

## 论坛频道

Discord 论坛频道（类型 15）不接受直接消息——论坛中的每个帖子都必须是一个主题。Hermes 会自动检测论坛频道，并在需要向该频道发送消息时创建一个新的主题帖子，因此 `send_message`、TTS、图片、语音消息和文件附件都可以正常工作，无需 Agent 进行特殊处理。

- **主题名称** 源自消息的第一行（去除 Markdown 标题前缀，最多 100 个字符）。当消息仅包含附件时，将使用文件名作为备选主题名称。
- **附件** 随新主题的起始消息一起发送——无需单独的上传步骤，不会出现部分发送。
- **一次调用，一个主题**：每次向论坛发送消息都会创建一个新主题。因此，连续向同一论坛发送消息将产生不同的主题。
- **检测分为三层**：首先是频道目录缓存，其次是进程本地探测缓存，最后是实时的 `GET /channels/{id}` 探测（其结果将在进程生命周期内被记忆）。

刷新目录（在暴露此功能的平台上使用 `/channels refresh`，或重启消息网关）会将机器人启动后创建的任何论坛频道填充到缓存中。

## 故障排除

### 机器人已上线但不响应消息

**原因**：消息内容意图被禁用。

**解决方法**：前往 [开发者门户](https://discord.com/developers/applications) → 你的应用 → Bot → Privileged Gateway Intents → 启用 **Message Content Intent** → 保存更改。重启消息网关。

### 启动时出现 "Disallowed Intents" 错误

**原因**：你的代码请求了在开发者门户中未启用的意图。

**解决方法**：在 Bot 设置中启用所有三个 Privileged Gateway Intents（Presence, Server Members, Message Content），然后重启。

### 机器人在特定频道中看不到消息

**原因**：机器人的角色没有查看该频道的权限。

**解决方法**：在 Discord 中，进入频道设置 → 权限 → 添加机器人的角色，并启用 **查看频道** 和 **读取消息历史** 权限。

### 403 Forbidden 错误

**原因**：机器人缺少所需的权限。

**解决方法**：使用第 5 步中的 URL 重新邀请机器人并授予正确的权限，或在服务器设置 → 角色中手动调整机器人的角色权限。

### 机器人离线

**原因**：Hermes 消息网关未运行，或者 Token 不正确。

**解决方法**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果你最近重置了 Token，请更新它。

### "User not allowed" / 机器人忽略你

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 文件中的 `DISCORD_ALLOWED_USERS`，然后重启消息网关。

### 同一频道中的人意外地共享上下文

**原因**：`group_sessions_per_user` 被禁用，或者平台无法为该上下文中的消息提供用户 ID。

**解决方法**：在 `~/.hermes/config.yaml` 中设置此项并重启消息网关：

```yaml
group_sessions_per_user: true
```

如果你有意进行共享房间对话，请保持关闭——只需预期会共享对话历史和共享中断行为。

## 安全

:::warning
始终设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）以限制谁可以与机器人交互。如果两者都未设置，作为安全措施，消息网关默认会拒绝所有用户。只授权你信任的人——被授权的用户拥有对 Agent 功能的完全访问权限，包括工具使用和系统访问。
:::

### 基于角色的访问控制

对于通过角色而非个人用户列表管理访问权限的服务器（例如，版主团队、支持人员、内部工具），请使用 `DISCORD_ALLOWED_ROLES`——一个逗号分隔的角色 ID 列表。拥有其中任何一个角色的成员都将被授权。

```bash
# ~/.hermes/.env — 可与 DISCORD_ALLOWED_USERS 一起使用或替代它
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义：

- **与用户白名单是 OR 关系**。如果用户的 ID 在 `DISCORD_ALLOWED_USERS` 中 **或者** 他们拥有 `DISCORD_ALLOWED_ROLES` 中的任何角色，则该用户被授权。
- **自动启用 Server Members Intent**。当设置 `DISCORD_ALLOWED_ROLES` 时，机器人会在连接时启用 Members 意图——这是 Discord 发送包含角色信息的成员记录所必需的。
- **使用角色 ID，而非名称**。从 Discord 获取：**用户设置 → 高级 → 开发者模式 ON**，然后右键点击任意角色 → **复制角色 ID**。
- **私信回退**。在私信中，角色检查会扫描共同加入的服务器；在任何共享服务器中拥有允许角色的用户在私信中也会被授权。

当版主团队人员变动时，这是首选模式——新成员在获得角色的那一刻就获得了访问权限，无需编辑 `.env` 文件或重启消息网关。

### 提及控制

默认情况下，Hermes 会阻止机器人提及 `@everyone`、`@here` 和角色提及，即使其回复中包含这些标记。这可以防止措辞不当的提示词或回显的用户内容向整个服务器发送垃圾信息。单独的 `@user` 提及和回复引用提及（小的"正在回复…"标签）保持启用，以便正常对话仍可进行。
你可以通过环境变量或 `config.yaml` 来放宽这些默认设置：

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # 允许机器人提及 @everyone / @here
    roles: false         # 允许机器人提及 @角色
    users: true          # 允许机器人提及单个 @用户
    replied_user: true   # 回复消息时提及原消息作者
```

```bash
# ~/.hermes/.env — 环境变量的优先级高于 config.yaml
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::tip
除非你确切知道为什么需要，否则请将 `everyone` 和 `roles` 保持为 `false`。LLM 很容易在看似正常的回复中生成 `@everyone` 字符串；如果没有此保护，这将通知你服务器中的每个成员。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。