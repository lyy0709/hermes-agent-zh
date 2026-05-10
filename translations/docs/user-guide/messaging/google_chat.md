---
sidebar_position: 12
title: "Google Chat"
description: "使用 Cloud Pub/Sub 将 Hermes Agent 设置为 Google Chat 机器人"
---

# Google Chat 设置

将 Hermes Agent 作为机器人连接到 Google Chat。该集成使用 Cloud Pub/Sub 拉取订阅来处理入站事件，并使用 Chat REST API 处理出站消息。其易用性与 Slack Socket Mode 或 Telegram 长轮询相当：你的 Hermes 进程不需要公共 URL、隧道或 TLS 证书。它连接、认证并监听一个订阅——就像 Telegram 机器人监听 Token 一样。

:::note Workspace 版本
Google Chat 是 Google Workspace 的一部分。你可以将此集成用于个人 Workspace（通过 Google 注册的 `@yourdomain.com`）或你拥有发布应用管理员权限的工作 Workspace。仅限 Gmail 的账户无法托管 Chat 应用。
:::

## 概述

| 组件 | 值 |
|-----------|-------|
| **库** | `google-cloud-pubsub`, `google-api-python-client`, `google-auth` |
| **入站传输** | Cloud Pub/Sub 拉取订阅（无公共端点） |
| **出站传输** | Chat REST API (`chat.googleapis.com`) |
| **认证** | 在订阅上具有 `roles/pubsub.subscriber` 角色的服务账户 JSON |
| **用户标识** | Chat 资源名称 (`users/{id}`) + 电子邮件 |

---

## 步骤 1：创建或选择一个 GCP 项目

你需要一个 Google Cloud 项目来托管 Pub/Sub 主题。如果没有，请在 [console.cloud.google.com](https://console.cloud.google.com) 创建一个——个人账户享有免费层级，足以轻松覆盖机器人流量。

记下项目 ID（例如 `my-chat-bot-123`）。你将在后续每个步骤中使用它。

---

## 步骤 2：启用两个 API

在控制台中，转到 **APIs & Services → Library** 并启用：

- **Google Chat API**
- **Cloud Pub/Sub API**

对于个人机器人产生的流量，两者都是免费的。

---

## 步骤 3：创建服务账户

**IAM & Admin → Service Accounts → Create Service Account。**

- 名称：`hermes-chat-bot`
- 跳过“Grant this service account access to project”步骤。你只需要特定订阅上的 IAM 权限——**不要**授予项目级别的 Pub/Sub 角色。

创建后，打开该服务账户，转到 **Keys → Add Key → Create new key → JSON** 并下载文件。将其保存在只有 Hermes 可以读取的位置（例如 `~/.hermes/google-chat-sa.json`，`chmod 600`）。

:::caution 不存在“Chat Bot Caller”角色
一个常见的错误是搜索特定于 Chat 的 IAM 角色并在项目级别授予它。该角色不存在。Chat 机器人的权限来自安装在空间中，而不是来自 IAM。你的服务账户只需要在下一步创建的订阅上拥有 Pub/Sub 订阅者权限。
:::

---

## 步骤 4：创建 Pub/Sub 主题和订阅

**Pub/Sub → Topics → Create topic。**

- 主题 ID：`hermes-chat-events`
- 其他所有设置保持默认。

创建后，主题的详细信息页面有一个 **Subscriptions** 选项卡。创建一个：

- 订阅 ID：`hermes-chat-events-sub`
- 传递类型：**Pull**
- 消息保留期：**7 天**（这样在 Hermes 重启后积压的消息可以保留）
- 其余设置保持默认。

---

## 步骤 5：在主题上绑定 IAM（关键）

在**主题**（不是订阅）上，添加一个 IAM 主体：

- 主体：`chat-api-push@system.gserviceaccount.com`
- 角色：`Pub/Sub Publisher`

没有这个，Google Chat 就无法将事件发布到你的主题，你的机器人将永远收不到任何消息。

---

## 步骤 6：在订阅上绑定 IAM

在**订阅**上，添加你自己的服务账户作为主体：

- 主体：`hermes-chat-bot@<your-project>.iam.gserviceaccount.com`
- 角色：`Pub/Sub Subscriber`

同时授予同一订阅的 `Pub/Sub Viewer` 权限——Hermes 在启动时会调用 `subscription.get()` 作为可达性检查。

---

## 步骤 7：配置 Chat 应用

转到 **APIs & Services → Google Chat API → Configuration**。

- **应用名称**：你希望用户看到的任何名称（“Hermes”是合理的）。
- **头像 URL**：任何公共 PNG（Google 有一些默认选项）。
- **描述**：在应用目录中显示的简短句子。
- **功能**：启用 **Receive 1:1 messages** 和 **Join spaces and group conversations**。
- **连接设置**：选择 **Cloud Pub/Sub**，输入主题名称 `projects/<your-project>/topics/hermes-chat-events`。
- **可见性**：限制在你的工作空间（或特定用户）——在测试时不要发布给所有人。

保存。

---

## 步骤 8：在测试空间中安装机器人

在浏览器中打开 Google Chat。通过在 **+ New Chat** 菜单中搜索其名称，与你的应用开始一个私聊。当你第一次给它发消息时，Google 会发送一个 `ADDED_TO_SPACE` 事件，Hermes 使用该事件来缓存机器人自身的 `users/{id}` 以进行自我消息过滤。

---

## 步骤 9：配置 Hermes

将 Google Chat 部分添加到 `~/.hermes/.env`：

```bash
# 必需
GOOGLE_CHAT_PROJECT_ID=my-chat-bot-123
GOOGLE_CHAT_SUBSCRIPTION_NAME=projects/my-chat-bot-123/subscriptions/hermes-chat-events-sub
GOOGLE_CHAT_SERVICE_ACCOUNT_JSON=/home/you/.hermes/google-chat-sa.json

# 授权——粘贴允许与机器人对话的人员的电子邮件
GOOGLE_CHAT_ALLOWED_USERS=you@yourdomain.com,coworker@yourdomain.com

# 可选
GOOGLE_CHAT_HOME_CHANNEL=spaces/AAAA...         # 定时任务的默认发送目的地
GOOGLE_CHAT_MAX_MESSAGES=1                      # Pub/Sub 流控制；每个会话序列化命令
GOOGLE_CHAT_MAX_BYTES=16777216                  # 16 MiB——飞行中消息字节数的上限
```

项目 ID 也会回退到 `GOOGLE_CLOUD_PROJECT`，服务账户路径也会回退到 `GOOGLE_APPLICATION_CREDENTIALS`——使用你喜欢的任何约定。

安装 Google Chat 适配器所需的依赖项（目前没有发布 Hermes 额外包——直接安装它们）：

```bash
pip install google-cloud-pubsub google-api-python-client google-auth google-auth-oauthlib
```

启动消息网关：

```bash
hermes gateway
```

你应该会看到类似这样的日志行：

```
[GoogleChat] Connected; project=my-chat-bot-123, subscription=<redacted>,
             bot_user_id=users/XXXX, flow_control(msgs=1, bytes=16777216)
```
在测试私聊中发送“hola”。机器人会发布一个“Hermes 正在思考…”标记，然后原地编辑同一条消息以显示真实回复——没有“消息已删除”的墓碑。

---

## 格式和功能

Google Chat 渲染一个有限的 Markdown 子集：

| 支持 | 不支持 |
|-----------|---------------|
| `*粗体*`、`_斜体_`、`~删除线~`、`` `代码` `` | 标题、列表 |
| 通过 URL 的内联图片 | 交互式 Card v2 按钮（此消息网关的 v1 版本） |
| 原生文件附件（在 `/setup-files` 之后——参见步骤 10） | 原生语音笔记 / 圆形视频笔记 |

Agent 的系统提示词包含一个特定于 Google Chat 的提示，以便它了解这些限制并避免使用无法渲染的格式。

消息大小限制：每条消息 4000 个字符。较长的 Agent 回复会自动拆分为多条消息。

线程支持：当用户在某个线程内回复时，Hermes 会检测到 `thread.name` 并将其回复发布在同一线程中，因此每个线程都有一个独立的 Hermes 会话。

---

## 步骤 10：原生附件传递（可选）

开箱即用，机器人可以发布文本、通过 URL 的内联图片以及音频/视频/文档的下载卡片。要传递**原生** Chat 附件——即人类用户拖放文件时获得的相同文件小部件——每个用户需要通过针对每个用户的 OAuth 流程对机器人进行一次授权。

### 为什么需要单独的流程

Google Chat 的 `media.upload` 端点硬性拒绝服务账号认证：

> 此方法不支持使用服务账号进行应用身份验证。请使用用户账号进行身份验证。

没有 IAM 角色或范围可以解决此问题。该端点只接受用户凭据。因此，每当机器人上传文件时，它都必须*以用户身份*进行操作——具体来说，是以请求文件的用户身份。

### 一次性主机设置

1. 在同一个 GCP 项目中，转到 **APIs & Services → Credentials**。
2. **Create credentials → OAuth client ID → Desktop app**。
3. 下载 JSON 文件。将其移动到运行 Hermes 的主机上。
4. 在主机上，向 Hermes 注册客户端：

```bash
python -m gateway.platforms.google_chat_user_oauth \
    --client-secret /path/to/client_secret.json
```

这将写入 `~/.hermes/google_chat_user_client_secret.json`。这是共享的基础设施——它标识的是 OAuth *应用*，而不是任何单个用户。无论以后有多少用户授权，每台主机一个文件就足够了。

### 每个用户的授权（在聊天中）

每个用户在自己的机器人私聊中运行一次此流程：

1. 他们向机器人发送 `/setup-files`。机器人会回复状态和下一步。
2. 他们发送 `/setup-files start`。机器人回复一个 OAuth URL。
3. 他们打开该 URL，点击 **Allow**，然后观察浏览器无法加载 `http://localhost:1/?...&code=...`。这个失败是预期的——授权码就在 URL 栏中。
4. 他们复制失败的 URL（或仅复制 `code=...` 值）并将其粘贴回聊天中，格式为 `/setup-files <PASTED_URL>`。机器人将其交换为刷新令牌。

令牌保存在 `~/.hermes/google_chat_user_tokens/<sanitized_email>.json`。后续在该用户私聊中的文件请求将使用*他们的*令牌，因此机器人以他们的身份上传，消息会出现在他们的空间中。

稍后撤销：`/setup-files revoke` 仅删除该用户的令牌。其他用户的令牌不受影响。

### 范围

该流程仅请求一个范围：`chat.messages.create`。这涵盖了 `media.upload` 和引用已上传 `attachmentDataRef` 的 `messages.create`。没有 Drive，没有更广泛的 Chat 范围——这是有意为之的最小权限。

### 多用户行为

当请求者还没有每个用户的令牌时，机器人会回退到 `~/.hermes/google_chat_user_token.json` 处的旧版单用户令牌（如果来自多用户安装前的设置）。当两者都不可用时，机器人会发布清晰的文本通知，告诉请求者运行 `/setup-files`。

用户撤销仅清除他们自己的槽位。来自某个用户令牌的 401/403 错误仅驱逐该用户的缓存。用户之间不会互相干扰。

---

## 故障排除

**发送“hola”后机器人保持沉默。**

1. 在控制台中检查 Pub/Sub 订阅是否有未传递的消息。
   如果有，说明 Hermes 未通过身份验证——请验证 `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` 以及该服务账号是否在订阅上被列为 `Pub/Sub Subscriber`。
2. 如果订阅的消息数为零，说明 Google Chat 没有发布。
   请仔细检查**主题**上的 IAM 绑定：
   `chat-api-push@system.gserviceaccount.com` 必须具有 `Pub/Sub Publisher` 权限。
3. 检查 `hermes gateway` 日志中是否有 `[GoogleChat] Connected`。如果看到 `[GoogleChat] Config validation failed`，错误消息会告诉你需要修复哪个环境变量。

**机器人回复了，但显示的是错误消息而不是 Agent 的答案。**

检查日志中是否有 `[GoogleChat] Pub/Sub stream died`——如果这些重复出现，你的服务账号凭据可能已被轮换或订阅已被删除。经过 10 次尝试后，适配器会将自己标记为致命错误。

**每条出站消息都出现“403 Forbidden”。**

机器人已从空间中移除，或者你在 Chat API 控制台中撤销了它。在空间中重新安装它（下一个 `ADDED_TO_SPACE` 事件将自动重新启用消息传递）。

**出现太多“Rate limit hit”警告。**

Chat API 的默认配额允许每个空间每分钟 60 条消息。如果你的 Agent 生成长流式响应并超过此限制，适配器会使用指数退避进行重试——但你仍然会看到用户可见的延迟。请考虑使用简洁的响应或在 GCP 控制台中提高配额。

**机器人不断发布“/setup-files”通知而不是文件。**

请求者没有每个用户的 OAuth 令牌，并且没有旧版回退。在他们的私聊中运行 `/setup-files` 并遵循步骤 10。交换完成后，下一个文件请求将原生上传，无需重启消息网关。

**`/setup-files start` 显示“主机上未存储客户端凭据。”**

未完成一次性主机设置。在运行 Hermes 的主机的终端中执行：

```bash
python -m gateway.platforms.google_chat_user_oauth \
    --client-secret /path/to/client_secret.json
```
然后再次发送 `/setup-files start`。

**`/setup-files <PASTED_URL>` 提示 "Token exchange failed."**

授权码是一次性且有效期很短（通常几分钟）。发送 `/setup-files start` 以获取新的 URL 并重试。

---

## 安全注意事项

- **服务账号权限范围**：适配器请求 `chat.bot` 和 `pubsub` 权限范围。IAM 应该是实际的执行机制——授予你的服务账号最小权限（订阅上的 `roles/pubsub.subscriber` + `roles/pubsub.viewer`），而不是项目级或组织级的 Pub/Sub 角色。
- **附件下载保护**：Hermes 只会将服务账号的持有者令牌附加到主机与 Google 自有域名的简短允许列表（`googleapis.com`、`drive.google.com`、`lh[3-6].googleusercontent.com` 等）匹配的 URL。任何其他主机都会在 HTTP 请求发出前被拒绝，以防止精心构造的事件将持有者令牌重定向到 GCE 元数据服务这种 SSRF 场景。
- **信息脱敏**：服务账号邮箱、订阅路径和主题路径会通过 `agent/redact.py` 从日志输出中剥离。调试信封转储（`GOOGLE_CHAT_DEBUG_RAW=1`）会经过相同的脱敏过滤器，并在 DEBUG 级别记录日志。
- **合规性**：如果你计划将此机器人连接到受监管的工作区（任何有数据驻留或 AI 治理政策的环境），请在首次安装前获得批准。
- **用户 OAuth 权限范围**：每个用户的附件流程*仅*请求 `chat.messages.create`——这是覆盖 `media.upload` 加上后续 `messages.create` 所需的最小权限。令牌以纯 JSON 格式持久化存储在 `~/.hermes/google_chat_user_tokens/<sanitized_email>.json`（文件系统权限是保护机制——与服务账号密钥文件模型相同）。每个令牌仅属于一个用户；撤销操作也仅限于该用户。