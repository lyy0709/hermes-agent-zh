# ntfy

[ntfy](https://ntfy.sh/) 是一个基于 HTTP 的简单发布-订阅通知服务。它可以使用免费的公共服务器 `ntfy.sh` 或任何自托管实例，并支持任何可以发出 HTTP 请求的客户端——手机、浏览器、脚本、手表。

ntfy 是 Hermes 一个很好的轻量级推送通道：从 [ntfy 手机应用](https://ntfy.sh/docs/subscribe/phone/)订阅一个主题，向该主题发送消息来与 Agent 对话，在你的手机上接收回复。

> 运行 `hermes gateway setup` 并选择 **ntfy** 以获取引导式设置。

## 前提条件

- 一个主题名称（任何唯一的字符串——`hermes-myname-2026` 就可以）
- 安装 [ntfy 手机应用](https://ntfy.sh/docs/subscribe/phone/) 并订阅该主题
- 可选：一个自托管的 ntfy 服务器，或一个用于私有/保留主题的 `ntfy.sh` 账户 Token

就这样。不需要 SDK，不需要守护进程，不需要 Node.js。适配器使用 `httpx`，它已经是 Hermes 的依赖项。

## 配置 Hermes

### 通过设置向导

```bash
hermes setup gateway
```

选择 **ntfy** 并按照提示操作。

### 通过环境变量

将这些添加到 `~/.hermes/.env`：

```
NTFY_TOPIC=hermes-myname-2026
NTFY_ALLOWED_USERS=hermes-myname-2026
NTFY_HOME_CHANNEL=hermes-myname-2026
```

| 变量 | 必需 | 描述 |
|---|---|---|
| `NTFY_TOPIC` | 是 | 要订阅的主题（传入消息） |
| `NTFY_SERVER_URL` | 可选 | 服务器 URL（默认：`https://ntfy.sh`）——指向自托管的 ntfy 以保护隐私 |
| `NTFY_TOKEN` | 可选 | Bearer Token（例如 `tk_xyz`）或用于基本认证的 `user:pass` |
| `NTFY_PUBLISH_TOPIC` | 可选 | 用于发送回复的不同主题（默认为 `NTFY_TOPIC`） |
| `NTFY_MARKDOWN` | 可选 | 设置为 `true` 以发送带有 `X-Markdown: true` 头的回复 |
| `NTFY_ALLOWED_USERS` | 推荐 | 允许的逗号分隔的主题名称（视为用户 ID；见下文） |
| `NTFY_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 以允许所有发布者——仅对带有读取 Token 的私有主题安全 |
| `NTFY_HOME_CHANNEL` | 可选 | 用于定时任务 / 通知传递的默认主题 |
| `NTFY_HOME_CHANNEL_NAME` | 可选 | 主通道的人工标签 |

## 身份模型——部署前请阅读

ntfy 没有原生的认证用户身份。已发布消息上的 `title` 字段是**发布者控制的**，可以是发送者想要的任何内容。Hermes 适配器**不**使用 `title` 进行授权——这将允许任何知道主题的发布者冒充允许的用户。

相反，**主题名称本身就是身份**。发布到该主题的每条消息都被视为来自同一个逻辑用户（即该主题）。因此，`NTFY_ALLOWED_USERS` 通常只是主题名称本身——一个单条目允许列表，用于控制整个通道的访问。

这意味着**任何知道该主题的人都可以与 Agent 对话**。要使其成为真正的信任边界：

- **自托管 ntfy** 并使用[访问控制](https://docs.ntfy.sh/config/#access-control)锁定主题。只有拥有读写 Token 的授权客户端才能发布。
- 或者**在 ntfy.sh 上使用私有主题**（[保留主题](https://docs.ntfy.sh/publish/#reserved-topics)需要账户）并使用 `NTFY_TOKEN` 保护它。
- 或者**选择一个长的、难以猜测的主题名称**（`hermes-7d4f9c8b-2026`）并将其视为共享密钥。这是最轻量的设置，但主题名称可能会通过任何日志或截图泄露。

在所有情况下，除非底层主题有访问控制，否则不要通过 ntfy 传递敏感数据。

## 快速开始——从手机与你的 Agent 对话

1.  选择一个主题名称：`hermes-myname-2026`
2.  在你的手机上：安装 [ntfy 应用](https://ntfy.sh/docs/subscribe/phone/)，点击 **+**，输入 `hermes-myname-2026`
3.  在主机上：
    ```bash
    echo 'NTFY_TOPIC=hermes-myname-2026' >> ~/.hermes/.env
    echo 'NTFY_ALLOWED_USERS=hermes-myname-2026' >> ~/.hermes/.env
    hermes gateway restart
    ```
4.  从 ntfy 应用，向该主题发送一条消息。Agent 的回复会作为推送通知送达。

## 将 ntfy 与定时任务一起使用

一旦设置了 `NTFY_HOME_CHANNEL`，定时任务就可以向 ntfy 传递消息：

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="ntfy",          # 使用 NTFY_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或者显式指定一个特定主题：

```python
send_message(target="ntfy:alerts-channel", message="Done!")
```

即使定时任务在消息网关之外独立运行时，这也能工作——插件注册了一个 `standalone_sender_fn`，它会打开自己的 HTTP 连接。

## 自托管 ntfy

如果你想要完全控制：

```bash
# Docker
docker run -p 80:80 -it binwiederhier/ntfy serve

# 原生
go install heckel.io/ntfy/v2@latest
ntfy serve
```

然后将 Hermes 指向它：

```
NTFY_SERVER_URL=https://ntfy.mydomain.com
NTFY_TOPIC=hermes
NTFY_TOKEN=tk_abc123  # 如果你设置了访问控制
```

自托管为你提供主题访问控制、消息持久化策略、附件和表情符号标签。请参阅 [ntfy 服务器文档](https://docs.ntfy.sh/install/)。

## Markdown 格式化

当发布者设置 `X-Markdown: true` 头时，ntfy 客户端会渲染 markdown。要为传出的 Hermes 回复启用此功能：

```
NTFY_MARKDOWN=true
```

或者在 `config.yaml` 中：

```yaml
platforms:
  ntfy:
    extra:
      markdown: true
```

手机应用支持 CommonMark 的一个子集——粗体、斜体、列表、链接、围栏代码块。确切的集合请参阅 [ntfy 的 markdown 文档](https://docs.ntfy.sh/publish/#markdown-formatting)。

## 仅发送设置（无入站的通知）

如果你只希望 Hermes *推送* 通知到 ntfy（定时任务摘要、警报）而从不接受返回的消息，请将 `NTFY_TOPIC` 和 `NTFY_PUBLISH_TOPIC` 都设置为相同的值，并完全跳过 `NTFY_ALLOWED_USERS`。没有允许列表，Agent 永远不会响应入站消息——你的手机会收到推送，但对话是单向的。

## 限制

- **消息大小**：ntfy 将消息正文限制在 4096 个字符。当超过此限制时，Hermes 会发出警告并截断。
- **无输入指示器**：协议不提供此功能；`send_typing` 是无操作。
- **无线程或附件**：ntfy 是纯推送通知。长回复保留在消息正文中，没有线程展开。
- **无原生用户身份**：请参阅上面的身份模型部分。

## 故障排除

**认证失败 / 401** —— `NTFY_TOKEN` 错误，或者该 Token 在此主题上没有发布/订阅权限。适配器在遇到 401 时会停止其重连循环，消息网关运行时状态将显示 `fatal: ntfy_unauthorized`。修复 Token 并重启消息网关。

**主题未找到 / 404** —— `NTFY_TOPIC` 在配置的服务器上不存在。对于 ntfy.sh，主题在首次发布时自动创建，所以出现 404 意味着你指向了一个没有预置该主题的自托管服务器。适配器会停止其重连循环并显示 `fatal: ntfy_topic_not_found`。

**已连接但无消息** —— 检查 `NTFY_ALLOWED_USERS` 是否包含主题名称本身。根据 ntfy 的身份模型，主题就是用户；允许列表为空会拒绝所有消息。

**每 60 秒重连一次** —— 流保活默认是 55 秒；ntfy 可能存在间歇性网络问题。适配器应用指数退避（2 → 5 → 10 → 30 → 60 秒），一旦流保持活动状态 ≥60 秒，就会重置为 0。