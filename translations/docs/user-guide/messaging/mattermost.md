---
sidebar_position: 8
title: "Mattermost"
description: "将 Hermes Agent 设置为 Mattermost 机器人"
---

# Mattermost 设置

Hermes Agent 可作为机器人集成到 Mattermost 中，让你通过直接消息或团队频道与你的 AI 助手聊天。Mattermost 是一个自托管、开源的 Slack 替代方案——你可以在自己的基础设施上运行它，完全掌控你的数据。该机器人通过 Mattermost 的 REST API (v4) 和 WebSocket 连接以获取实时事件，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片和斜杠命令。

无需外部 Mattermost 库——适配器使用 `aiohttp`，这已经是 Hermes 的依赖项。

在设置之前，以下是大多数人想知道的部分：Hermes 进入你的 Mattermost 实例后的行为方式。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **直接消息** | Hermes 响应每条消息。无需 `@提及`。每个直接消息都有其独立的会话。 |
| **公开/私密频道** | 当你 `@提及` Hermes 时，它会响应。没有提及时，Hermes 会忽略消息。 |
| **线程** | 如果 `MATTERMOST_REPLY_MODE=thread`，Hermes 会在你的消息下方以线程形式回复。线程上下文与父频道隔离。 |
| **多用户共享频道** | 默认情况下，Hermes 在频道内为每个用户隔离会话历史记录。两个人在同一频道中交谈不会共享一个对话记录，除非你明确禁用此功能。 |

:::tip
如果你希望 Hermes 以线程对话形式回复（嵌套在你的原始消息下），请设置 `MATTERMOST_REPLY_MODE=thread`。默认值为 `off`，即在频道中发送平铺消息。
:::

### Mattermost 中的会话模型

默认情况下：

- 每个直接消息都有其独立的会话
- 每个线程都有其独立的会话命名空间
- 共享频道中的每个用户在该频道内都有其独立的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个频道共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作频道可能有用，但也意味着：

- 用户共享上下文增长和 Token 成本
- 一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
- 一个人正在进行的运行可能会在同一频道中中断另一个人的后续操作

本指南将引导你完成完整的设置过程——从在 Mattermost 上创建机器人到发送第一条消息。

## 步骤 1：启用机器人账户

在创建机器人之前，必须在你的 Mattermost 服务器上启用机器人账户。

1. 以 **系统管理员** 身份登录 Mattermost。
2. 进入 **系统控制台** → **集成** → **机器人账户**。
3. 将 **启用机器人账户创建** 设置为 **true**。
4. 点击 **保存**。

:::info
如果你没有系统管理员访问权限，请让你的 Mattermost 管理员启用机器人账户并为你创建一个。
:::

## 步骤 2：创建机器人账户

1. 在 Mattermost 中，点击 **☰** 菜单（左上角）→ **集成** → **机器人账户**。
2. 点击 **添加机器人账户**。
3. 填写详细信息：
   - **用户名**：例如，`hermes`
   - **显示名称**：例如，`Hermes Agent`
   - **描述**：可选
   - **角色**：`成员` 即可
4. 点击 **创建机器人账户**。
5. Mattermost 将显示 **机器人令牌**。**立即复制它。**

:::warning[令牌仅显示一次]
机器人令牌仅在创建机器人账户时显示一次。如果丢失，你需要从机器人账户设置中重新生成。切勿公开分享你的令牌或将其提交到 Git——任何拥有此令牌的人都可以完全控制机器人。
:::

将令牌存储在安全的地方（例如密码管理器）。你将在步骤 5 中需要它。

:::tip
你也可以使用 **个人访问令牌** 代替机器人账户。进入 **个人资料** → **安全** → **个人访问令牌** → **创建令牌**。如果你希望 Hermes 以你自己的用户身份发布消息，而不是单独的机器人用户，这很有用。
:::

## 步骤 3：将机器人添加到频道

机器人需要成为你希望它响应的任何频道的成员：

1. 打开你希望机器人所在的频道。
2. 点击频道名称 → **添加成员**。
3. 搜索你的机器人用户名（例如，`hermes`）并添加它。

对于直接消息，只需打开与机器人的直接消息——它将能够立即响应。

## 步骤 4：查找你的 Mattermost 用户 ID

Hermes Agent 使用你的 Mattermost 用户 ID 来控制谁可以与机器人交互。查找方法：

1. 点击你的 **头像**（左上角）→ **个人资料**。
2. 你的用户 ID 显示在个人资料对话框中——点击它进行复制。

你的用户 ID 是一个 26 个字符的字母数字字符串，如 `3uo8dkh1p7g1mfk49ear5fzs5c`。

:::warning
你的用户 ID **不是** 你的用户名。用户名是 `@` 后面的内容（例如，`@alice`）。用户 ID 是 Mattermost 内部使用的长字母数字标识符。
:::

**替代方法**：你也可以通过 API 获取你的用户 ID：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-mattermost-server/api/v4/users/me | jq .id
```

:::tip
要获取 **频道 ID**：点击频道名称 → **查看信息**。频道 ID 显示在信息面板中。如果你想手动设置主频道，将需要这个。
:::

## 步骤 5：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

出现提示时选择 **Mattermost**，然后在询问时粘贴你的服务器 URL、机器人令牌和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
MATTERMOST_URL=https://mm.example.com
MATTERMOST_TOKEN=***
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c

# 多个允许的用户（逗号分隔）
# MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c,8fk2jd9s0a7bncm1xqw4tp6r3e

# 可选：回复模式（thread 或 off，默认：off）
# MATTERMOST_REPLY_MODE=thread

# 可选：无需 @提及 即可响应（默认：true = 需要提及）
# MATTERMOST_REQUIRE_MENTION=false

# 可选：机器人无需 @提及 即可响应的频道（逗号分隔的频道 ID）
# MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享频道和线程中保持每个参与者的上下文隔离

### 启动消息网关

配置完成后，启动 Mattermost 消息网关：

```bash
hermes gateway
```

机器人应在几秒钟内连接到你的 Mattermost 服务器。发送一条消息进行测试——可以是直接消息，也可以是在已添加机器人的频道中。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 主频道

你可以指定一个“主频道”，机器人可以在其中发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在任何机器人所在的 Mattermost 频道中键入 `/sethome`。该频道将成为主频道。

### 手动配置

将此添加到你的 `~/.hermes/.env`：

```bash
MATTERMOST_HOME_CHANNEL=abc123def456ghi789jkl012mn
```

将 ID 替换为实际的频道 ID（点击频道名称 → 查看信息 → 复制 ID）。

## 回复模式

`MATTERMOST_REPLY_MODE` 设置控制 Hermes 发布响应的方式：

| 模式 | 行为 |
|------|----------|
| `off`（默认） | Hermes 在频道中发布平铺消息，就像普通用户一样。 |
| `thread` | Hermes 在你的原始消息下方以线程形式回复。当有大量来回对话时，保持频道整洁。 |

在你的 `~/.hermes/.env` 中设置：

```bash
MATTERMOST_REPLY_MODE=thread
```

## 提及行为

默认情况下，机器人仅在频道中被 `@提及` 时响应。你可以更改此行为：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | 设置为 `false` 以响应频道中的所有消息（直接消息始终有效）。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | _(无)_ | 逗号分隔的频道 ID，即使 require_mention 为 true，机器人也无需 `@提及` 即可响应。 |

在 Mattermost 中查找频道 ID：打开频道，点击频道名称标题，在 URL 或频道详细信息中查找 ID。

当机器人被 `@提及` 时，在处理消息之前会自动去除提及。

## 故障排除

### 机器人不响应消息

**原因**：机器人不是频道的成员，或者 `MATTERMOST_ALLOWED_USERS` 不包含你的用户 ID。

**解决方法**：将机器人添加到频道（频道名称 → 添加成员 → 搜索机器人）。验证你的用户 ID 是否在 `MATTERMOST_ALLOWED_USERS` 中。重启消息网关。

### 403 禁止错误

**原因**：机器人令牌无效，或者机器人没有在频道中发布的权限。

**解决方法**：检查 `.env` 文件中的 `MATTERMOST_TOKEN` 是否正确。确保机器人账户未被停用。验证机器人是否已添加到频道。如果使用个人访问令牌，请确保你的账户具有所需权限。

### WebSocket 断开连接 / 重连循环

**原因**：网络不稳定、Mattermost 服务器重启或防火墙/代理对 WebSocket 连接有问题。

**解决方法**：适配器会自动以指数退避（2秒 → 60秒）重新连接。检查服务器的 WebSocket 配置——反向代理（nginx、Apache）需要配置 WebSocket 升级头。验证防火墙是否阻止了 Mattermost 服务器上的 WebSocket 连接。

对于 nginx，确保你的配置包含：

```nginx
location /api/v4/websocket {
    proxy_pass http://mattermost-backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

### 启动时“身份验证失败”

**原因**：令牌或服务器 URL 不正确。

**解决方法**：验证 `MATTERMOST_URL` 是否指向你的 Mattermost 服务器（包含 `https://`，无尾部斜杠）。检查 `MATTERMOST_TOKEN` 是否有效——使用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/api/v4/users/me
```

如果返回你的机器人用户信息，则令牌有效。如果返回错误，请重新生成令牌。

### 机器人离线

**原因**：Hermes 消息网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误消息。常见问题：错误的 URL、过期的令牌、Mattermost 服务器无法访问。

### “用户不允许” / 机器人忽略你

**原因**：你的用户 ID 不在 `MATTERMOST_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `MATTERMOST_ALLOWED_USERS` 并重启消息网关。记住：用户 ID 是一个 26 个字符的字母数字字符串，不是你的 `@用户名`。

## 安全

:::warning
始终设置 `MATTERMOST_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，消息网关默认拒绝所有用户作为安全措施。只添加你信任的用户 ID——授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

- **自托管友好**：适用于任何自托管的 Mattermost 实例。无需 Mattermost Cloud 账户或订阅。
- **无额外依赖**：适配器使用 `aiohttp` 处理 HTTP 和 WebSocket，这已包含在 Hermes Agent 中。
- **团队版兼容**：适用于 Mattermost 团队版（免费）和企业版。