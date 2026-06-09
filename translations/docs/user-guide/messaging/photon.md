---
sidebar_position: 18
---

# Photon iMessage

通过 [Photon][photon] 将 Hermes 连接到 **iMessage**。Photon 是一项托管服务，负责处理 Apple 线路分配和防滥用层，因此您无需运行自己的 Mac 中继。

免费套餐使用 Photon 的共享 iMessage 线路池——不同的收件人可能会看到不同的发送号码，但每个会话保持稳定。付费的商业套餐为每个用户提供相同的专用号码；插件支持两者，免费套餐是推荐的起点。

:::info 免费开始
Photon 的共享线路池是免费的。从 Hermes 发送第一条 iMessage 无需订阅——只需一个我们可以绑定到您帐户的电话号码。
:::

## 架构

Photon 是一个**持久连接**通道，类似于 Discord 或 Slack——**无需管理 Webhook、公共 URL 或签名密钥。**

`spectrum-ts` SDK 通过一个长期存在的 **gRPC 流** 与 Photon 进行双向通信。由于 SDK 仅支持 TypeScript，Hermes 在一个受监管的小型 **Node 边车** 中运行它，并通过环回地址与之通信：

- **入站** —— 边车消费 SDK 的 `app.messages` gRPC 流，并通过环回 `GET /inbound` (NDJSON) 将每条消息转发到 Python 适配器。适配器进行去重并将其分派给 Agent，如果流中断则自动重新连接。
- **出站** —— 回复通过环回 POST 发送到边车，边车在 SDK 上调用 `space.send(...)`。

Python 插件会自动启动、监管和关闭边车。

## 先决条件

- 一个 Photon 帐户 —— 在 [app.photon.codes][app] 注册
- PATH 上有 **Node.js 18.17 或更新版本** (`node --version`)
- 一个可以接收 iMessage 的电话号码（用于绑定您的帐户）

就这样 —— 无需设置公共 URL 或隧道。

## 首次设置

可以运行统一的消息网关向导并选择 **Photon iMessage**：

```bash
hermes gateway setup
```

…或者直接运行 Photon 设置（向导调用相同的流程）：

```bash
# 设备码登录 + 项目 + 用户 + 边车依赖，全部一步完成
hermes photon setup --phone +15551234567
```

设置步骤，按顺序：

1.  **设备登录** (`client_id=photon-cli`) —— 打开 `https://app.photon.codes/` 进行授权并存储承载令牌。
2.  **查找或创建** 您帐户上的 `Hermes Agent` 项目。
3.  **启用 Spectrum**，读取项目的 Spectrum id，并轮换项目密钥。
4.  **将您的电话号码注册** 为 Spectrum 用户 —— 如果已存在使用该号码的用户，则跳过此步，因此重新运行是安全的。
5.  **打印分配给您的 iMessage 线路** —— 您发送短信以联系您的 Agent 的号码。
6.  **在插件的边车目录内运行 `npm install`**。

运行时凭据写入 `~/.hermes/.env` (`PHOTON_PROJECT_ID` = Spectrum 项目 id, `PHOTON_PROJECT_SECRET`)，与其他通道存储其令牌的位置相同。管理元数据（设备令牌、仪表板项目 id）位于 `~/.hermes/auth.json` 的 `credential_pool.photon` / `credential_pool.photon_project` 下。

## 授权用户

Photon 使用与所有其他 Hermes 通道相同的授权模型。选择一种方法：

**私信配对（默认）。** 当未知号码向您的 Photon 线路发送消息时，Hermes 会回复一个配对码。使用以下命令批准：

```bash
hermes pairing approve photon <CODE>
```

使用 `hermes pairing list` 查看待处理的配对码和已批准的用户。

**预授权特定号码**（在 `~/.hermes/.env` 中）：

```bash
PHOTON_ALLOWED_USERS=+15551234567,+15559876543
```

**开放访问**（仅限开发，在 `~/.hermes/.env` 中）：

```bash
PHOTON_ALLOW_ALL_USERS=true
```

当设置了 `PHOTON_ALLOWED_USERS` 时，未知发件人会被静默忽略，而不是提供配对码（允许列表表明您有意限制了访问权限）。

### 在群聊中要求提及

默认情况下，Hermes 会响应每条已授权的私信和群组消息。要使群聊选择加入，请启用提及门控（私信仍然始终有效）：

```yaml
gateway:
  platforms:
    photon:
      enabled: true
      require_mention: true
```

当 `require_mention: true` 时，除非群聊消息匹配唤醒词模式，否则将被忽略。默认模式匹配 `Hermes` 和 `@Hermes agent` 的变体。对于自定义 Agent 名称，设置正则表达式模式：

```yaml
gateway:
  platforms:
    photon:
      require_mention: true
      mention_patterns:
        - '(?<![\w@])@?amos\b[,:\-]?'
```

这两个键也接受环境变量 (`PHOTON_REQUIRE_MENTION`, `PHOTON_MENTION_PATTERNS`)。这与 BlueBubbles iMessage 通道使用的提及门控模型相同。

## 启动消息网关

```bash
hermes gateway start --platform photon
```

您将看到类似内容：

```
[photon] connected — sidecar on 127.0.0.1:8789, streaming inbound over gRPC
```

向分配给您的号码发送一条 iMessage，Hermes 将会回复。

## 状态与故障排除

```bash
hermes photon status
```

打印保存的凭据、边车健康状况、您注册的号码以及 Hermes 使用的已分配 iMessage 线路。当 Photon 令牌和仪表板项目可用时，`status` 会从仪表板刷新缺失的号码行，而无需配置新线路。

```
Photon iMessage 状态
──────────────────────
  device token        : ✓ 已存储
  dashboard project   : 3c90c3cc-0d44-4b50-...
  spectrum project id : sp-...
  project secret      : ✓ 已存储
  my number           : +15551234567
  assigned number     : +16282679185
  node binary         : /usr/bin/node
  sidecar deps        : ✓ 已安装
```

常见问题：

- **`sidecar deps : ✗ run hermes photon install-sidecar`** —— Node 已安装但 `spectrum-ts` 未安装。运行建议的命令。
- **`device token : ✗ missing`** —— 运行 `hermes photon setup` 登录。
- **`No iMessage line assigned yet`** —— Spectrum 已启用但尚未分配线路；重新运行 `hermes photon setup` 或检查 [仪表板][app]。
- **边车无法启动** —— 确认 `node --version` 是 18.17+ 并且 `hermes photon install-sidecar` 完成无误。

## 当前限制

- **入站附件仅为元数据。** 入站事件携带文件名 + MIME 类型；Agent 可以看到标记但尚无法读取字节。SDK 通过 `content.read()` 公开附件字节，因此这是边车后续要跟进的功能。
- **支持出站附件。** Hermes 通过边车的 `/send-attachment` 端点，使用 spectrum-ts 的 `attachment()` / `voice()` 内容构建器发送图像、语音备忘录、视频和文档。标题在媒体之后作为单独的 iMessage 气泡到达。
- **Photon 的免费配额：** 每台服务器每天 5,000 条消息，每个共享线路每天 50 次新会话发起。可申请增加 —— 发送邮件至 `help@photon.codes`。

## 环境变量

| 变量                      | 默认值               | 说明                                      |
|---------------------------|----------------------|-------------------------------------------|
| `PHOTON_PROJECT_ID`       | 来自 `.env`          | Spectrum 项目 id (SDK 的 `projectId`)；由设置设置 |
| `PHOTON_PROJECT_SECRET`   | 来自 `.env`          | 项目密钥；由设置设置                        |
| `PHOTON_SIDECAR_PORT`     | `8789`               | 边车控制 + 入站通道的环回端口                |
| `PHOTON_SIDECAR_AUTOSTART`| `true`               | 适配器是否生成边车                          |
| `PHOTON_NODE_BIN`         | `which node`         | 覆盖 Node 二进制文件路径                    |
| `PHOTON_HOME_CHANNEL`     | (未设置)             | 定时任务 / 通知的默认空间 id                |
| `PHOTON_HOME_CHANNEL_NAME`| (未设置)             | 主通道的人类可读标签                        |
| `PHOTON_ALLOWED_USERS`    | (未设置)             | 逗号分隔的 E.164 允许列表                   |
| `PHOTON_ALLOW_ALL_USERS`  | `false`              | 仅开发 —— 接受任何发件人                    |
| `PHOTON_REQUIRE_MENTION`  | `false`              | 在群组中响应前需要唤醒词                    |
| `PHOTON_MENTION_PATTERNS` | Hermes 唤醒词        | 用于群组提及的 JSON 列表 / 逗号 / 换行正则表达式模式 |
| `PHOTON_DASHBOARD_HOST`   | `app.photon.codes`   | 覆盖仪表板 / 设备登录主机                   |
| `PHOTON_SPECTRUM_HOST`    | `spectrum.photon.codes` | 覆盖 Spectrum API 主机                     |

[photon]: https://photon.codes/
[app]: https://app.photon.codes/