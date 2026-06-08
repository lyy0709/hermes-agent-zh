---
sidebar_position: 17
title: "LINE"
description: "将 Hermes Agent 设置为 LINE Messaging API 机器人"
---

# LINE 设置

通过官方的 LINE Messaging API 将 Hermes Agent 作为 [LINE](https://line.me/) 机器人运行。该适配器作为一个捆绑的平台插件位于 `plugins/platforms/line/` 下——无需修改核心代码，像启用其他平台一样启用它即可。

LINE 是日本、台湾和泰国占主导地位的即时通讯应用。如果你的用户在那里，这是他们联系你的方式。

> 运行 `hermes gateway setup` 并选择 **LINE** 以获取引导式设置。

## 机器人如何响应

| 上下文 | 行为 |
|---------|----------|
| **1对1聊天** (`U` ID) | 响应每条消息 |
| **群聊** (`C` ID) | 当群组在允许列表中时响应 |
| **多人房间** (`R` ID) | 当房间在允许列表中时响应 |

传入的文本、图片、音频、视频、文件、贴纸和位置信息都会被处理。发出的文本会**优先使用免费的回复 Token**（一次性使用，约 60 秒窗口），当 Token 过期后，会回退到计费的 Push API。

---

## 步骤 1：创建 LINE Messaging API 频道

1.  前往 [LINE Developers Console](https://developers.line.biz/console/)。
2.  创建一个 Provider，然后在其下创建一个 **Messaging API** 频道。
3.  从频道的 **Basic settings** 选项卡中，复制 **Channel secret**。
4.  在 **Messaging API** 选项卡中，滚动到 **Channel access token (long-lived)** 并点击 **Issue**。复制该 Token。
5.  在 **Messaging API** 选项卡中，同时禁用 **Auto-reply messages** 和 **Greeting messages**，以免它们干扰你的机器人回复。

---

## 步骤 2：暴露 Webhook 端口

LINE 通过公共 HTTPS 发送 Webhook。默认端口是 `8646`——如果需要，可以用 `LINE_PORT` 覆盖。

```bash
# Cloudflare Tunnel (生产环境推荐——固定主机名)
cloudflared tunnel --url http://localhost:8646

# ngrok (适合开发)
ngrok http 8646

# devtunnel
devtunnel create hermes-line --allow-anonymous
devtunnel port create hermes-line -p 8646 --protocol https
devtunnel host hermes-line
```

复制 `https://...` URL——你将在下面将其设置为 Webhook URL。**在测试时保持隧道运行**。对于生产环境，请设置一个固定的 Cloudflare 命名隧道，这样 Webhook URL 在重启时就不会改变。

---

## 步骤 3：配置 Hermes

添加到 `~/.hermes/.env`：

```env
LINE_CHANNEL_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN
LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET

# 允许列表——至少设置其中一个（或为开发设置 LINE_ALLOW_ALL_USERS=true）
LINE_ALLOWED_USERS=U1234567890abcdef...           # 逗号分隔的 U 前缀 ID
LINE_ALLOWED_GROUPS=C1234567890abcdef...          # 可选的群组 ID
LINE_ALLOWED_ROOMS=R1234567890abcdef...           # 可选的房间 ID

# 发送图片/音频/视频所必需——公共 HTTPS 基础 URL
# 隧道解析到的地址。没有它，send_image/voice/video 将拒绝执行。
LINE_PUBLIC_URL=https://my-tunnel.example.com
```

然后在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  platforms:
    line:
      enabled: true
```

这就足够了——`gateway/config.py` 中的捆绑插件扫描会自动拾取 `plugins/platforms/line/`。无需编辑 `Platform.LINE` 枚举，也无需 `_create_adapter` 注册。

---

## 步骤 4：设置 Webhook URL

回到 LINE 控制台：

1.  打开你的频道 → **Messaging API** 选项卡。
2.  在 **Webhook settings** → **Webhook URL** 下，粘贴 `https://<your-tunnel>/line/webhook`（注意 `/line/webhook` 路径——适配器监听该路径）。
3.  点击 **Verify**。LINE 会 ping 该 URL；你应该看到 200 状态码。
4.  将 **Use webhook** 切换为 **On**。

---

## 步骤 5：运行消息网关

```bash
hermes gateway
```

Agent 日志会显示：

```
LINE: webhook listening on 0.0.0.0:8646/line/webhook (public: https://my-tunnel.example.com)
```

从 LINE 应用中将机器人添加为好友（扫描频道 **Messaging API** 选项卡中的二维码）并向它发送一条消息。

---

## 慢速 LLM 响应

LINE 的回复 Token 是一次性的，大约在传入事件后 60 秒过期。慢速 LLM 无法及时回复，这通常会导致强制使用付费的 Push API 调用。

当 LLM 运行时间超过 `LINE_SLOW_RESPONSE_THRESHOLD` 秒（默认 `45`）时，适配器会消耗原始的回复 Token 来发送一个 **Template Buttons** 气泡：

> 🤔 仍在思考。请在准备好后点击下方获取答案。
>
> [ 获取答案 ]

用户在方便时点击 **获取答案**——该回传会提供一个*新的*回复 Token，适配器用它来发送缓存的答案（仍然是免费的）。

状态机：`PENDING → READY → DELIVERED`，加上 `ERROR` 用于已取消的运行（在 `/stop` 后，孤立的 PENDING 状态会解析为 "Run was interrupted before completion."，这样持久的按钮就不会循环）。

要禁用回传按钮并始终回退到 Push API：

```env
LINE_SLOW_RESPONSE_THRESHOLD=0
```

为了使回传流程可靠触发，请抑制在阈值之前会消耗回复 Token 的聊天信息：

```yaml
# ~/.hermes/config.yaml
display:
  interim_assistant_messages: false
  platforms:
    line:
      tool_progress: off
```

---

## 定时任务 / 通知发送

```env
LINE_HOME_CHANNEL=Uxxxxxxxxxxxxxxxxxxxx     # 默认发送目标
```

带有 `deliver: line` 的定时任务会路由到 `LINE_HOME_CHANNEL`。适配器附带一个独立的仅 Push 发送器，因此即使定时任务在与消息网关分离的进程中运行，定时任务也能正常工作。

---

## 环境变量参考

| 变量 | 必需 | 默认值 | 描述 |
|---|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | 是 | — | 长期频道访问 Token |
| `LINE_CHANNEL_SECRET` | 是 | — | 频道密钥（用于 HMAC-SHA256 Webhook 验证） |
| `LINE_HOST` | 否 | `0.0.0.0` | Webhook 绑定主机 |
| `LINE_PORT` | 否 | `8646` | Webhook 绑定端口 |
| `LINE_PUBLIC_URL` | 用于媒体 | — | 公共 HTTPS 基础 URL；发送图片/语音/视频所必需 |
| `LINE_ALLOWED_USERS` | 至少一个 | — | 逗号分隔的用户 ID（U 前缀） |
| `LINE_ALLOWED_GROUPS` | 至少一个 | — | 逗号分隔的群组 ID（C 前缀） |
| `LINE_ALLOWED_ROOMS` | 至少一个 | — | 逗号分隔的房间 ID（R 前缀） |
| `LINE_ALLOW_ALL_USERS` | 仅开发 | `false` | 完全跳过允许列表 |
| `LINE_HOME_CHANNEL` | 否 | — | 默认定时任务 / 通知发送目标 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 否 | `45` | 触发回传按钮前的秒数（`0` = 禁用） |
| `LINE_PENDING_TEXT` | 否 | "🤔 Still thinking…" | 与回传按钮一起显示的气泡文本 |
| `LINE_BUTTON_LABEL` | 否 | "Get answer" | 按钮标签 |
| `LINE_DELIVERED_TEXT` | 否 | "Already replied ✅" | 当再次点击已发送的按钮时的回复 |
| `LINE_INTERRUPTED_TEXT` | 否 | "Run was interrupted before completion." | 当点击 `/stop` 孤立按钮时的回复 |

---

## 故障排除

**Webhook 验证时出现 "invalid signature"。** `Channel secret` 复制错误，或者你的隧道重写了请求体。先用 `curl -i https://<tunnel>/line/webhook/health` 验证——应该返回 `{"status":"ok","platform":"line"}`。

**机器人在群组中收不到任何消息。** 检查 `LINE_ALLOWED_GROUPS` 是否包含 `C...` 群组 ID。要查找群组 ID，发送一条测试消息并在 `~/.hermes/logs/gateway.log` 中 grep `LINE: rejecting unauthorized source`——被拒绝的源字典中包含 ID。

**`send_image` 失败并提示 "LINE_PUBLIC_URL must be set"。** LINE 的 Messaging API 不接受二进制上传——图片、音频和视频必须是可访问的 HTTPS URL。将 `LINE_PUBLIC_URL` 设置为隧道的公共主机名，适配器将自动从 `/line/media/<token>/<filename>` 提供文件。

**回传按钮从未出现。** 要么 LLM 响应速度快于 `LINE_SLOW_RESPONSE_THRESHOLD`，要么另一个气泡（工具进度、流式响应）先消耗了回复 Token。请参阅“慢速 LLM 响应”下的抑制块。

**"already in use by another profile"。** 相同的频道访问 Token 已绑定到另一个正在运行的 Hermes 配置文件。停止另一个消息网关或使用单独的频道。

---

## 限制

*   **气泡和长度限制。** 每个 LINE 文本气泡限制为 5000 个字符。更长的响应会被智能分块，每个 Reply/Push 调用最多 5 个气泡，每个约 4500 个字符，尽可能在自然边界处分割。
*   **没有原生消息编辑。** LINE 没有编辑消息的 API——流式响应总是发送新的气泡，从不编辑之前的。
*   **没有 Markdown 渲染。** 粗体 (`**`)、斜体 (`*`)、代码块和标题渲染为字面字符。适配器在发送前会剥离它们；URL 会被保留（`[label](url)` 变为 `label (url)`）。
*   **加载指示器仅限私聊。** LINE 拒绝在群组和房间中使用聊天/加载 API，因此输入指示器仅显示在 1 对 1 聊天中。