---
sidebar_position: 7
title: "邮件"
description: "通过 IMAP/SMTP 将 Hermes Agent 设置为邮件助手"
---

# 邮件设置

Hermes 可以使用标准的 IMAP 和 SMTP 协议接收和回复邮件。向 Agent 的地址发送邮件，它会在同一邮件线程中回复——无需特殊的客户端或机器人 API。适用于 Gmail、Outlook、Yahoo、Fastmail 或任何支持 IMAP/SMTP 的提供商。

:::info 无外部依赖
邮件适配器使用 Python 内置的 `imaplib`、`smtplib` 和 `email` 模块。无需额外的包或外部服务。
:::

---

## 前提条件

- 为你的 Hermes Agent 准备一个**专用的电子邮件账户**（不要使用你的个人邮箱）
- 在电子邮件账户上**启用 IMAP**
- 如果使用 Gmail 或其他启用了双重认证的提供商，需要**一个应用专用密码**

### Gmail 设置

1.  在你的 Google 账户上启用双重认证
2.  前往[应用专用密码](https://myaccount.google.com/apppasswords)
3.  创建一个新的应用专用密码（选择“邮件”或“其他”）
4.  复制 16 位字符的密码——你将使用此密码代替常规密码

### Outlook / Microsoft 365

1.  前往[安全设置](https://account.microsoft.com/security)
2.  如果尚未启用，请启用双重认证
3.  在“其他安全选项”下创建应用专用密码
4.  IMAP 主机：`outlook.office365.com`，SMTP 主机：`smtp.office365.com`

### 其他提供商

大多数电子邮件提供商都支持 IMAP/SMTP。请查阅你的提供商文档以获取：
- IMAP 主机和端口（通常为端口 993，使用 SSL）
- SMTP 主机和端口（通常为端口 587，使用 STARTTLS）
- 是否需要应用专用密码

---

## 步骤 1：配置 Hermes

最简单的方式：

```bash
hermes gateway setup
```

从平台菜单中选择 **Email**。向导会提示你输入电子邮件地址、密码、IMAP/SMTP 主机以及允许的发件人。

### 手动配置

添加到 `~/.hermes/.env`：

```bash
# 必需
EMAIL_ADDRESS=hermes@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop    # 应用专用密码（非你的常规密码）
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com

# 安全（推荐）
EMAIL_ALLOWED_USERS=your@email.com,colleague@work.com

# 可选
EMAIL_IMAP_PORT=993                    # 默认：993 (IMAP SSL)
EMAIL_SMTP_PORT=587                    # 默认：587 (SMTP STARTTLS)
EMAIL_POLL_INTERVAL=15                 # 收件箱检查间隔秒数（默认：15）
EMAIL_HOME_ADDRESS=your@email.com      # 定时任务的默认投递目标
```

---

## 步骤 2：启动消息网关

```bash
hermes gateway              # 在前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：作为开机启动的系统服务
```

启动时，适配器会：
1.  测试 IMAP 和 SMTP 连接
2.  将所有现有的收件箱邮件标记为“已读”（仅处理新邮件）
3.  开始轮询新消息

---

## 工作原理

### 接收消息

适配器以可配置的间隔（默认：15 秒）轮询 IMAP 收件箱中的 UNSEEN（未读）消息。对于每封新邮件：

- **主题行**作为上下文包含（例如，`[Subject: Deploy to production]`）
- **回复邮件**（主题以 `Re:` 开头）会跳过主题前缀——邮件线程上下文已建立
- **附件**在本地缓存：
  - 图像（JPEG、PNG、GIF、WebP）→ 可供视觉工具使用
  - 文档（PDF、ZIP 等）→ 可供文件访问使用
- **纯 HTML 邮件**会去除标签以提取纯文本
- **自己发送给自己的消息**会被过滤掉，以防止回复循环
- **自动/无回复发件人**会被静默忽略——包括 `noreply@`、`mailer-daemon@`、`bounce@`、`no-reply@`，以及带有 `Auto-Submitted`、`Precedence: bulk` 或 `List-Unsubscribe` 邮件头的邮件

### 发送回复

回复通过 SMTP 发送，并保持正确的邮件线程：

- **In-Reply-To** 和 **References** 邮件头用于维护线程
- **主题行** 保留并添加 `Re:` 前缀（不会出现 `Re: Re:` 这样的重复前缀）
- **Message-ID** 使用 Agent 的域名生成
- 回复以纯文本（UTF-8）形式发送

### 文件附件

Agent 可以在回复中发送文件附件。在回复中包含 `MEDIA:/path/to/file`，该文件就会附加到外发邮件中。

### 跳过附件

要忽略所有传入的附件（用于恶意软件防护或节省带宽），请添加到你的 `config.yaml`：

```yaml
platforms:
  email:
    skip_attachments: true
```

启用后，附件和内联部分会在有效负载解码前被跳过。邮件正文文本仍会正常处理。

---

## 访问控制

邮件访问遵循与所有其他 Hermes 平台相同的模式：

1.  **设置了 `EMAIL_ALLOWED_USERS`** → 仅处理来自这些地址的邮件
2.  **未设置允许列表** → 未知发件人会收到一个配对码
3.  **`EMAIL_ALLOW_ALL_USERS=true`** → 接受任何发件人（谨慎使用）

:::warning
**务必配置 `EMAIL_ALLOWED_USERS`。** 如果不配置，任何知道 Agent 邮件地址的人都可以发送命令。默认情况下，Agent 拥有终端访问权限。
:::

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 启动时出现 **"IMAP connection failed"** | 验证 `EMAIL_IMAP_HOST` 和 `EMAIL_IMAP_PORT`。确保账户已启用 IMAP。对于 Gmail，请在设置 → 转发和 POP/IMAP 中启用。 |
| 启动时出现 **"SMTP connection failed"** | 验证 `EMAIL_SMTP_HOST` 和 `EMAIL_SMTP_PORT`。检查密码是否正确（对于 Gmail 使用应用专用密码）。 |
| **未收到消息** | 检查 `EMAIL_ALLOWED_USERS` 是否包含发件人的电子邮件。检查垃圾邮件文件夹——某些提供商会标记自动回复。 |
| **"Authentication failed"** | 对于 Gmail，必须使用应用专用密码，而不是常规密码。确保已首先启用双重认证。 |
| **重复回复** | 确保只有一个消息网关实例在运行。检查 `hermes gateway status`。 |
| **响应缓慢** | 默认轮询间隔为 15 秒。使用 `EMAIL_POLL_INTERVAL=5` 可减少间隔以获得更快的响应（但会增加 IMAP 连接数）。 |
| **回复未形成线程** | 适配器使用 In-Reply-To 邮件头。某些电子邮件客户端（尤其是基于网页的）可能无法正确与自动消息形成线程。 |

---

## 安全

:::warning
**使用专用的电子邮件账户。** 不要使用你的个人邮箱——Agent 会将密码存储在 `.env` 中，并通过 IMAP 拥有完整的收件箱访问权限。
:::

- 使用**应用专用密码**代替你的主密码（对于启用了双重认证的 Gmail 是必需的）
- 设置 `EMAIL_ALLOWED_USERS` 以限制可以与 Agent 交互的人员
- 密码存储在 `~/.hermes/.env` 中——请保护此文件（`chmod 600`）
- IMAP 默认使用 SSL（端口 993），SMTP 默认使用 STARTTLS（端口 587）——连接是加密的

---

## 环境变量参考

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `EMAIL_ADDRESS` | 是 | — | Agent 的电子邮件地址 |
| `EMAIL_PASSWORD` | 是 | — | 电子邮件密码或应用专用密码 |
| `EMAIL_IMAP_HOST` | 是 | — | IMAP 服务器主机（例如，`imap.gmail.com`） |
| `EMAIL_SMTP_HOST` | 是 | — | SMTP 服务器主机（例如，`smtp.gmail.com`） |
| `EMAIL_IMAP_PORT` | 否 | `993` | IMAP 服务器端口 |
| `EMAIL_SMTP_PORT` | 否 | `587` | SMTP 服务器端口 |
| `EMAIL_POLL_INTERVAL` | 否 | `15` | 收件箱检查间隔秒数 |
| `EMAIL_ALLOWED_USERS` | 否 | — | 逗号分隔的允许发件人地址 |
| `EMAIL_HOME_ADDRESS` | 否 | — | 定时任务的默认投递目标 |
| `EMAIL_ALLOW_ALL_USERS` | 否 | `false` | 允许所有发件人（不推荐） |