---
sidebar_position: 10
title: "钉钉"
description: "将 Hermes Agent 设置为钉钉聊天机器人"
---

# 钉钉设置

Hermes Agent 可与钉钉集成作为聊天机器人，让您通过私聊或群聊与您的 AI 助手对话。该机器人通过钉钉的 Stream 模式连接——这是一种长连接的 WebSocket 连接，无需公共 URL 或 Webhook 服务器——并通过钉钉的会话 Webhook API 使用 Markdown 格式的消息进行回复。

在开始设置之前，以下是大多数人想了解的部分：Hermes 在您的钉钉工作空间中如何运行。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **私聊 (1:1 聊天)** | Hermes 回复每条消息。无需 `@提及`。每个私聊都有其独立的会话。 |
| **群聊** | 当您 `@提及` Hermes 时，它才会回复。没有提及，Hermes 会忽略消息。 |
| **多用户共享的群组** | 默认情况下，Hermes 在群组内为每个用户隔离会话历史。两个人在同一个群组中交谈不会共享一个对话记录，除非您明确禁用此功能。 |

### 钉钉中的会话模型

默认情况下：
- 每个私聊拥有独立的会话
- 共享群聊中的每个用户在该群组内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅在您明确希望整个群组共享一个对话时，将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

本指南将引导您完成完整的设置过程——从创建钉钉机器人到发送第一条消息。

## 先决条件

安装所需的 Python 包：

```bash
pip install "hermes-agent[dingtalk]"
```

或单独安装：

```bash
pip install dingtalk-stream httpx alibabacloud-dingtalk
```

- `dingtalk-stream` — 钉钉官方的 Stream 模式 SDK（基于 WebSocket 的实时消息传递）
- `httpx` — 用于通过会话 Webhook 发送回复的异步 HTTP 客户端
- `alibabacloud-dingtalk` — 钉钉 OpenAPI SDK，用于 AI 卡片、表情反应和媒体下载

## 步骤 1：创建钉钉应用

1. 前往 [钉钉开发者后台](https://open-dev.dingtalk.com/)。
2. 使用您的钉钉管理员账号登录。
3. 点击 **应用开发** → **企业内部开发** → **H5微应用**（或 **机器人**，具体取决于您的控制台版本）→ **创建应用**。
4. 填写：
   - **应用名称**：例如，`Hermes Agent`
   - **应用描述**：可选
5. 创建后，导航至 **凭证与基础信息** 以找到您的 **Client ID** (AppKey) 和 **Client Secret** (AppSecret)。复制两者。

:::warning[凭证仅显示一次]
Client Secret 仅在创建应用时显示一次。如果丢失，您需要重新生成。切勿公开共享这些凭证或将其提交到 Git。
:::

## 步骤 2：启用机器人能力

1. 在您的应用设置页面，前往 **添加能力** → **机器人**。
2. 启用机器人能力。
3. 在 **消息接收模式** 下，选择 **Stream 模式**（推荐——无需公共 URL）。

:::tip
Stream 模式是推荐的设置。它使用从您的机器发起的长期 WebSocket 连接，因此您不需要公共 IP、域名或 Webhook 端点。这可以在 NAT、防火墙后以及本地机器上工作。
:::

## 步骤 3：查找您的钉钉用户 ID

Hermes Agent 使用您的钉钉用户 ID 来控制谁可以与机器人交互。钉钉用户 ID 是由您组织的管理员设置的字母数字字符串。

查找您的方法：
1. 询问您的钉钉组织管理员——用户 ID 在钉钉管理后台的 **通讯录** → **成员** 下配置。
2. 或者，机器人会记录每条传入消息的 `sender_id`。启动消息网关，向机器人发送一条消息，然后在日志中检查您的 ID。

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

出现提示时选择 **DingTalk**。设置向导可以通过以下两种路径之一进行授权：

- **二维码设备流（推荐）。** 使用钉钉移动应用扫描终端中打印的二维码——您的 Client ID 和 Client Secret 会自动返回并写入 `~/.hermes/.env`。无需访问开发者后台。
- **手动粘贴。** 如果您已有凭证（或扫描二维码不方便），请在提示时粘贴您的 Client ID、Client Secret 和允许的用户 ID。

:::note openClaw 品牌披露说明
由于钉钉的 `verification_uri_complete` 在 API 层硬编码为 openClaw 身份，二维码当前在 `openClaw` 源字符串下授权，直到阿里巴巴/钉钉-Real-AI 在服务器端注册 Hermes 特定的模板。这纯粹是钉钉呈现同意屏幕的方式——您创建的机器人完全属于您，并且对您的租户是私有的。
:::

### 选项 B：手动配置

将以下内容添加到您的 `~/.hermes/.env` 文件中：

```bash
# 必需
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret

# 安全性：限制谁可以与机器人交互
DINGTALK_ALLOWED_USERS=user-id-1

# 多个允许的用户（逗号分隔）
# DINGTALK_ALLOWED_USERS=user-id-1,user-id-2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享群聊中保持每个参与者的上下文隔离

### 启动消息网关

配置完成后，启动钉钉消息网关：

```bash
hermes gateway
```

机器人应在几秒钟内连接到钉钉的 Stream 模式。发送一条消息进行测试——可以是私聊，也可以是在已添加机器人的群组中。

:::tip
您可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。有关详细信息，请参阅部署文档。
:::

## 功能

### AI 卡片

Hermes 可以使用钉钉 AI 卡片进行回复，而不是纯 Markdown 消息。卡片提供了更丰富、结构化的显示，并支持在 Agent 生成响应时进行流式更新。

要启用 AI 卡片，请在 `config.yaml` 中配置卡片模板 ID：

```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      card_template_id: "your-card-template-id"
```

您可以在钉钉开发者后台中您应用的 AI 卡片设置下找到您的卡片模板 ID。启用 AI 卡片后，所有回复都将作为带有流式文本更新的卡片发送。

### 表情反应

Hermes 会自动在您的消息上添加表情反应以显示处理状态：
- 🤔思考中 — 当机器人开始处理您的消息时添加
- 🥳完成 — 当响应完成时添加（替换思考中反应）

这些反应在私聊和群聊中都有效。

### 显示设置

您可以独立于其他平台自定义钉钉的显示行为：

```yaml
display:
  platforms:
    dingtalk:
      show_reasoning: false   # 在回复中显示模型推理/思考过程
      streaming: true         # 启用流式响应（与 AI 卡片配合使用）
      tool_progress: all      # 显示工具执行进度（全部/新/关闭）
      interim_assistant_messages: true  # 显示中间评论消息
```

要禁用工具进度和中间消息以获得更简洁的体验：

```yaml
display:
  platforms:
    dingtalk:
      tool_progress: off
      interim_assistant_messages: false
```

## 故障排除

### 机器人不响应消息

**原因**：机器人能力未启用，或者 `DINGTALK_ALLOWED_USERS` 未包含您的用户 ID。

**解决方法**：验证在您的应用设置中机器人能力已启用，并且选择了 Stream 模式。检查您的用户 ID 是否在 `DINGTALK_ALLOWED_USERS` 中。重启消息网关。

### "dingtalk-stream not installed" 错误

**原因**：未安装 `dingtalk-stream` Python 包。

**解决方法**：安装它：

```bash
pip install dingtalk-stream httpx
```

### "DINGTALK_CLIENT_ID and DINGTALK_CLIENT_SECRET required"

**原因**：凭证未在您的环境或 `.env` 文件中设置。

**解决方法**：验证 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET` 在 `~/.hermes/.env` 中正确设置。Client ID 是您的 AppKey，Client Secret 是来自钉钉开发者后台的 AppSecret。

### 流连接断开 / 重连循环

**原因**：网络不稳定、钉钉平台维护或凭证问题。

**解决方法**：适配器会自动以指数退避（2s → 5s → 10s → 30s → 60s）重新连接。检查您的凭证是否有效，以及您的应用是否未被停用。验证您的网络是否允许出站 WebSocket 连接。

### 机器人离线

**原因**：Hermes 消息网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误消息。常见问题：错误的凭证、应用被停用、未安装 `dingtalk-stream` 或 `httpx`。

### "No session_webhook available"

**原因**：机器人尝试回复但没有会话 Webhook URL。这通常发生在 Webhook 过期或机器人在接收消息和发送回复之间重启的情况下。

**解决方法**：向机器人发送一条新消息——每条传入消息都会为回复提供一个全新的会话 Webhook。这是钉钉的正常限制；机器人只能回复它最近收到的消息。

## 安全性

:::warning
始终设置 `DINGTALK_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，消息网关默认会拒绝所有用户作为安全措施。仅添加您信任的用户 ID——授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。

## 注意事项

- **Stream 模式**：无需公共 URL、域名或 Webhook 服务器。连接通过 WebSocket 从您的机器发起，因此可以在 NAT 和防火墙后工作。
- **AI 卡片**：可选择使用丰富的 AI 卡片进行回复，而不是纯 Markdown。通过 `card_template_id` 配置。
- **表情反应**：自动的 🤔思考中/🥳完成 反应，用于显示处理状态。
- **Markdown 响应**：回复采用钉钉的 Markdown 格式，用于富文本显示。
- **媒体支持**：传入消息中的图像和文件会自动解析，并可由视觉工具处理。
- **消息去重**：适配器使用 5 分钟窗口对消息进行去重，以防止重复处理同一条消息。
- **自动重连**：如果流连接断开，适配器会自动以指数退避重新连接。
- **消息长度限制**：每条消息的响应限制为 20,000 个字符。更长的响应将被截断。