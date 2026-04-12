---
sidebar_position: 5
title: "WhatsApp"
description: "通过内置的 Baileys 桥接器将 Hermes Agent 设置为 WhatsApp 机器人"
---

# WhatsApp 设置

Hermes 通过一个基于 **Baileys** 的内置桥接器连接到 WhatsApp。其工作原理是模拟一个 WhatsApp Web 会话——**并非**通过官方的 WhatsApp Business API。因此，不需要 Meta 开发者账户或商业验证。

:::warning 非官方 API —— 封禁风险
WhatsApp **不**正式支持 Business API 之外的第三方机器人。使用第三方桥接器存在账户受限的小风险。为最小化风险：
- **使用一个专用的手机号码**给机器人（不要用你的个人号码）
- **不要发送批量/垃圾消息**——保持使用方式为对话式
- **不要向未先发消息的人自动发送外发消息**
:::

:::warning WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能会暂时破坏与第三方桥接器的兼容性。当这种情况发生时，Hermes 会更新桥接器依赖项。如果机器人在 WhatsApp 更新后停止工作，请拉取最新的 Hermes 版本并重新配对。
:::

## 两种模式

| 模式 | 工作原理 | 最适合 |
|------|-------------|----------|
| **独立的机器人号码**（推荐） | 将一个手机号码专用于机器人。人们直接向该号码发送消息。 | 用户体验清晰，多用户，封禁风险较低 |
| **个人自聊** | 使用你自己的 WhatsApp。你给自己发消息来与 Agent 对话。 | 快速设置，单用户，测试 |

---

## 先决条件

- **Node.js v18+** 和 **npm** —— WhatsApp 桥接器作为 Node.js 进程运行
- **一部安装了 WhatsApp 的手机**（用于扫描二维码）

与旧版基于浏览器的桥接器不同，当前基于 Baileys 的桥接器**不**需要本地的 Chromium 或 Puppeteer 依赖栈。

---

## 步骤 1：运行设置向导

```bash
hermes whatsapp
```

向导将：

1. 询问您想要哪种模式（**机器人** 或 **自聊**）
2. 如果需要，安装桥接器依赖项
3. 在您的终端中显示一个 **二维码**
4. 等待您扫描它

**扫描二维码：**

1. 在手机上打开 WhatsApp
2. 进入 **设置 → 已链接的设备**
3. 点击 **链接设备**
4. 将摄像头对准终端中的二维码

配对成功后，向导会确认连接并退出。您的会话会自动保存。

:::tip
如果二维码看起来乱码，请确保您的终端至少 60 列宽并支持 Unicode。您也可以尝试使用不同的终端模拟器。
:::

---

## 步骤 2：获取第二个手机号码（机器人模式）

对于机器人模式，您需要一个尚未在 WhatsApp 注册的手机号码。有三种选择：

| 选项 | 成本 | 备注 |
|--------|------|-------|
| **Google Voice** | 免费 | 仅限美国。在 [voice.google.com](https://voice.google.com) 获取一个号码。通过 Google Voice 应用使用短信验证 WhatsApp。 |
| **预付费 SIM 卡** | 一次性 $5–15 | 任何运营商。激活，验证 WhatsApp，然后 SIM 卡可以放在抽屉里。号码必须保持活跃（每 90 天打一次电话）。 |
| **VoIP 服务** | 免费–$5/月 | TextNow、TextFree 或类似服务。一些 VoIP 号码被 WhatsApp 屏蔽——如果第一个不行，可以多试几个。 |

获取号码后：

1. 在手机上安装 WhatsApp（或使用支持双卡双待的 WhatsApp Business 应用）
2. 用新号码注册 WhatsApp
3. 运行 `hermes whatsapp` 并从该 WhatsApp 账户扫描二维码

---

## 步骤 3：配置 Hermes

将以下内容添加到您的 `~/.hermes/.env` 文件中：

```bash
# 必需
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" 或 "self-chat"

# 访问控制 —— 选择以下选项之一：
WHATSAPP_ALLOWED_USERS=15551234567         # 逗号分隔的电话号码（带国家代码，不带 +）
# WHATSAPP_ALLOWED_USERS=*                 # 或者使用 * 允许所有人
# WHATSAPP_ALLOW_ALL_USERS=true            # 或者设置此标志（效果与 * 相同）
```

:::tip 允许所有人的简写
设置 `WHATSAPP_ALLOWED_USERS=*` 允许**所有**发送者（等同于 `WHATSAPP_ALLOW_ALL_USERS=true`）。
这与 [Signal 群组白名单](/docs/reference/environment-variables) 保持一致。
要使用配对流程，请移除这两个变量并依赖 [DM 配对系统](/docs/user-guide/security#dm-pairing-system)。
:::

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` 是全局默认值。未知的 DM 发送者会收到一个配对码。
- `whatsapp.unauthorized_dm_behavior: ignore` 使 WhatsApp 对未经授权的 DM 保持静默，这对于私人号码通常是更好的选择。

然后启动消息网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：启动时系统服务
```

消息网关会使用保存的会话自动启动 WhatsApp 桥接器。

---

## 会话持久化

Baileys 桥接器将其会话保存在 `~/.hermes/platforms/whatsapp/session` 下。这意味着：

- **会话在重启后保留**——您不需要每次都重新扫描二维码
- 会话数据包括加密密钥和设备凭证
- **请勿共享或提交此会话目录**——它授予对 WhatsApp 账户的完全访问权限

---

## 重新配对

如果会话中断（手机重置、WhatsApp 更新、手动取消链接），您将在消息网关日志中看到连接错误。要修复它：

```bash
hermes whatsapp
```

这将生成一个新的二维码。再次扫描它，会话就会重新建立。消息网关通过重连逻辑自动处理**临时**断开连接（网络波动、手机短暂离线）。

---

## 语音消息

Hermes 支持 WhatsApp 上的语音：

- **接收：** 语音消息（`.ogg` opus 格式）会使用配置的 STT 提供商自动转录：本地的 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 响应作为 MP3 音频文件附件发送
- Agent 的响应默认以 "⚕ **Hermes Agent**" 为前缀。您可以在 `config.yaml` 中自定义或禁用此功能：

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # 空字符串禁用标题
  # reply_prefix: "🤖 *我的机器人*\n──────\n"  # 自定义前缀（支持 \n 换行）
```

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端足够宽（60+ 列）。尝试不同的终端。确保您是从正确的 WhatsApp 账户（机器人号码，而非个人号码）扫描。 |
| **二维码过期** | 二维码每约 20 秒刷新一次。如果超时，请重启 `hermes whatsapp`。 |
| **会话未持久化** | 检查 `~/.hermes/platforms/whatsapp/session` 是否存在且可写。如果是容器化环境，请将其挂载为持久化卷。 |
| **意外退出登录** | WhatsApp 在长时间不活动后会取消链接设备。保持手机开机并连接到网络，如果需要，使用 `hermes whatsapp` 重新配对。 |
| **桥接器崩溃或重连循环** | 重启消息网关，更新 Hermes，如果会话因 WhatsApp 协议更改而失效，则重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获取最新的桥接器版本，然后重新配对。 |
| **macOS: "Node.js 未安装" 但终端中 node 命令有效** | launchd 服务不继承您的 shell PATH。运行 `hermes gateway install` 将您当前的 PATH 重新快照到 plist 中，然后运行 `hermes gateway start`。详情请参阅 [消息网关服务文档](./index.md#macos-launchd)。 |
| **未收到消息** | 验证 `WHATSAPP_ALLOWED_USERS` 是否包含发送者的号码（带国家代码，不带 `+` 或空格），或者将其设置为 `*` 以允许所有人。在 `.env` 中设置 `WHATSAPP_DEBUG=true` 并重启消息网关，以在 `bridge.log` 中查看原始消息事件。 |
| **机器人向陌生人回复配对码** | 如果您希望未经授权的 DM 被静默忽略，请在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |

---

## 安全

:::warning
**在正式上线前配置访问控制**。使用特定的电话号码（包括国家代码，不带 `+`）设置 `WHATSAPP_ALLOWED_USERS`，使用 `*` 允许所有人，或者设置 `WHATSAPP_ALLOW_ALL_USERS=true`。如果没有任何这些设置，消息网关会**拒绝所有传入消息**作为安全措施。
:::

默认情况下，未经授权的 DM 仍会收到配对码回复。如果您希望私人 WhatsApp 号码对陌生人完全保持静默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录包含完整的会话凭证——请像保护密码一样保护它
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`
- 为机器人使用**专用手机号码**，以隔离您个人账户的风险
- 如果您怀疑账户被盗用，请在 WhatsApp → 设置 → 已链接的设备中取消链接该设备
- 日志中的电话号码会被部分隐藏，但请审查您的日志保留策略