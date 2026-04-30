---
sidebar_position: 6
title: "Signal"
description: "通过 signal-cli 守护进程将 Hermes Agent 设置为 Signal 消息机器人"
---

# Signal 设置

Hermes 通过运行在 HTTP 模式下的 [signal-cli](https://github.com/AsamK/signal-cli) 守护进程连接到 Signal。适配器通过 SSE（服务器发送事件）实时流式传输消息，并通过 JSON-RPC 发送响应。

Signal 是最注重隐私的主流消息应用——默认端到端加密，开源协议，元数据收集最少。这使其成为安全敏感型 Agent 工作流的理想选择。

:::info 无需新的 Python 依赖
Signal 适配器使用 `httpx`（已是 Hermes 核心依赖）进行所有通信。无需额外的 Python 包。您只需要在外部安装 signal-cli。
:::

---

## 先决条件

- **signal-cli** — 基于 Java 的 Signal 客户端 ([GitHub](https://github.com/AsamK/signal-cli))
- **Java 17+** 运行时 — signal-cli 所需
- **一个安装了 Signal 的电话号码**（用于作为辅助设备链接）

### 安装 signal-cli

```bash
# macOS
brew install signal-cli

# Linux (下载最新版本)
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} \
  https://github.com/AsamK/signal-cli/releases/latest | sed 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
sudo tar xf "signal-cli-${VERSION}.tar.gz" -C /opt
sudo ln -sf "/opt/signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/
```

:::caution
signal-cli **不在** apt 或 snap 软件仓库中。上面的 Linux 安装直接从 [GitHub 发布页面](https://github.com/AsamK/signal-cli/releases)下载。
:::

---

## 步骤 1：链接您的 Signal 账户

Signal-cli 作为**链接设备**工作——类似于 WhatsApp Web，但用于 Signal。您的手机保持为主要设备。

```bash
# 生成链接 URI（显示二维码或链接）
signal-cli link -n "HermesAgent"
```

1. 在手机上打开 **Signal**
2. 进入 **设置 → 已链接的设备**
3. 点击 **链接新设备**
4. 扫描二维码或输入 URI

---

## 步骤 2：启动 signal-cli 守护进程

```bash
# 将 +1234567890 替换为您的 Signal 电话号码（E.164 格式）
signal-cli --account +1234567890 daemon --http 127.0.0.1:8080
```

:::tip
保持此进程在后台运行。您可以使用 `systemd`、`tmux`、`screen` 或将其作为服务运行。
:::

验证其是否正在运行：

```bash
curl http://127.0.0.1:8080/api/v1/check
# 应返回：{"versions":{"signal-cli":...}}
```

---

## 步骤 3：配置 Hermes

最简单的方式：

```bash
hermes gateway setup
```

从平台菜单中选择 **Signal**。向导将：

1. 检查 signal-cli 是否已安装
2. 提示输入 HTTP URL（默认：`http://127.0.0.1:8080`）
3. 测试与守护进程的连接性
4. 询问您的账户电话号码
5. 配置允许的用户和访问策略

### 手动配置

添加到 `~/.hermes/.env`：

```bash
# 必需
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1234567890

# 安全（推荐）
SIGNAL_ALLOWED_USERS=+1234567890,+0987654321    # 逗号分隔的 E.164 号码或 UUID

# 可选
SIGNAL_GROUP_ALLOWED_USERS=groupId1,groupId2     # 启用群组（省略以禁用，* 表示全部）
SIGNAL_HOME_CHANNEL=+1234567890                  # 定时任务的默认发送目标
```

然后启动消息网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机启动的系统服务
```

---

## 访问控制

### 私信访问

私信访问遵循与所有其他 Hermes 平台相同的模式：

1. **设置了 `SIGNAL_ALLOWED_USERS`** → 只有这些用户可以发送消息
2. **未设置允许列表** → 未知用户会收到私信配对码（通过 `hermes pairing approve signal CODE` 批准）
3. **`SIGNAL_ALLOW_ALL_USERS=true`** → 任何人都可以发送消息（谨慎使用）

### 群组访问

群组访问由 `SIGNAL_GROUP_ALLOWED_USERS` 环境变量控制：

| 配置 | 行为 |
|---------------|----------|
| 未设置（默认） | 忽略所有群组消息。机器人仅响应私信。 |
| 设置群组 ID | 仅监控列出的群组（例如，`groupId1,groupId2`）。 |
| 设置为 `*` | 机器人响应其所在的任何群组。 |

---

## 功能

### 附件

适配器支持双向发送和接收媒体文件。

**传入**（用户 → Agent）：

- **图片** — PNG、JPEG、GIF、WebP（通过魔数字节自动检测）
- **音频** — MP3、OGG、WAV、M4A（如果配置了 Whisper，语音消息会被转录）
- **文档** — PDF、ZIP 和其他文件类型

**传出**（Agent → 用户）：

Agent 可以通过响应中的 `MEDIA:` 标签发送媒体文件。支持以下发送方式：

- **图片** — `send_image_file` 将 PNG、JPEG、GIF、WebP 作为原生 Signal 附件发送
- **语音** — `send_voice` 将音频文件（OGG、MP3、WAV、M4A、AAC）作为附件发送
- **视频** — `send_video` 发送 MP4 视频文件
- **文档** — `send_document` 发送任何文件类型（PDF、ZIP 等）

所有传出的媒体都通过 Signal 的标准附件 API。与某些平台不同，Signal 在协议层面不区分语音消息和文件附件。

附件大小限制：**100 MB**（双向）。

### 原生格式化、回复引用和反应

Signal 消息以**原生格式化**呈现，而不是字面上的 Markdown 字符。适配器将 Markdown（`**粗体**`、`*斜体*`、`` `代码` ``、`~~删除线~~`、`||剧透||`、标题）转换为 Signal 的 `bodyRanges`，以便文本在接收方客户端显示为真实的样式，而不是可见的 `**` / `` ` `` 字符。

**回复引用。** 当 Hermes 回复特定消息时，它现在会发布一个引用原始消息的原生回复——与 Signal 用户自己使用“回复”时看到的 UI 效果相同。这对于响应入站消息生成的回复是自动的。

**反应。** Agent 可以通过标准的反应 API 对消息做出反应；反应在 Signal 中显示为被引用消息上的表情符号反应，而不是额外的文本。

所有这些都不需要额外的配置——在最近的 signal-cli 版本中默认启用。如果您的 `signal-cli` 版本太旧，Hermes 将回退到纯文本发送并记录一次性警告。

### 输入指示器

机器人在处理消息时会发送输入指示器，每 8 秒刷新一次。

### 电话号码脱敏

所有电话号码在日志中都会自动脱敏：
- `+15551234567` → `+155****4567`
- 这适用于 Hermes 消息网关日志和全局脱敏系统

### 给自己发消息（单号码设置）

如果您在自己的电话号码（而不是单独的机器人号码）上将 signal-cli 作为**链接的辅助设备**运行，则可以通过 Signal 的“给自己发消息”功能与 Hermes 交互。

只需从您的手机给自己发送一条消息——signal-cli 会接收到它，Hermes 会在同一会话中回复。

**工作原理：**
- “给自己发消息”以 `syncMessage.sentMessage` 信封形式到达
- 适配器检测到这些消息是发送给机器人自己的账户时，会将其作为常规入站消息处理
- 防回显保护（发送时间戳跟踪）可防止无限循环——机器人自己的回复会被自动过滤掉

**无需额外配置。** 只要 `SIGNAL_ACCOUNT` 与您的电话号码匹配，这就会自动生效。

### 健康监控

适配器监控 SSE 连接，并在以下情况下自动重新连接：
- 连接断开（采用指数退避：2s → 60s）
- 120 秒内未检测到活动（ping signal-cli 以验证）

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 设置期间 **“无法连接到 signal-cli”** | 确保 signal-cli 守护进程正在运行：`signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080` |
| **未收到消息** | 检查 `SIGNAL_ALLOWED_USERS` 是否包含发送者的 E.164 格式号码（带 `+` 前缀） |
| **“在 PATH 中找不到 signal-cli”** | 安装 signal-cli 并确保其在您的 PATH 中，或使用 Docker |
| **连接不断断开** | 检查 signal-cli 日志中的错误。确保已安装 Java 17+。 |
| **群组消息被忽略** | 配置 `SIGNAL_GROUP_ALLOWED_USERS` 为特定的群组 ID，或使用 `*` 允许所有群组。 |
| **机器人不响应任何人** | 配置 `SIGNAL_ALLOWED_USERS`，使用私信配对，或者如果您希望更广泛的访问，通过消息网关策略明确允许所有用户。 |
| **重复消息** | 确保只有一个 signal-cli 实例在监听您的电话号码 |

---

## 安全

:::warning
**始终配置访问控制。** 机器人默认具有终端访问权限。如果没有 `SIGNAL_ALLOWED_USERS` 或私信配对，消息网关会拒绝所有入站消息作为安全措施。
:::

- 电话号码在所有日志输出中都会被脱敏
- 使用私信配对或明确的允许列表来安全地接纳新用户
- 除非您特别需要群组支持，否则保持群组禁用，或者仅允许您信任的群组
- Signal 的端到端加密保护传输中的消息内容
- `~/.local/share/signal-cli/` 中的 signal-cli 会话数据包含账户凭据——请像保护密码一样保护它

---

## 环境变量参考

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `SIGNAL_HTTP_URL` | 是 | — | signal-cli HTTP 端点 |
| `SIGNAL_ACCOUNT` | 是 | — | 机器人电话号码（E.164） |
| `SIGNAL_ALLOWED_USERS` | 否 | — | 逗号分隔的电话号码/UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 否 | — | 要监控的群组 ID，或 `*` 表示全部（省略以禁用群组） |
| `SIGNAL_ALLOW_ALL_USERS` | 否 | `false` | 允许任何用户交互（跳过允许列表） |
| `SIGNAL_HOME_CHANNEL` | 否 | — | 定时任务的默认发送目标 |