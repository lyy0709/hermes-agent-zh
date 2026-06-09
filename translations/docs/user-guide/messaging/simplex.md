# SimpleX Chat

[SimpleX Chat](https://simplex.chat/) 是一个私密、去中心化的消息平台，用户拥有自己的联系人和群组。与其他平台不同，SimpleX 不分配持久的用户 ID —— 每个联系人通过连接时生成的不透明内部 ID 来识别，这使其成为目前最私密的即时通讯工具之一。

> 运行 `hermes gateway setup` 并选择 **SimpleX** 以获取引导式配置。

## 前提条件

- 已安装 **simplex-chat** CLI 并作为守护进程运行
- Python 包 **websockets** (`pip install websockets`)

## 安装 simplex-chat

从 [simplex-chat GitHub releases](https://github.com/simplex-chat/simplex-chat/releases) 页面下载最新版本：

```bash
# Linux / macOS 二进制文件
curl -L https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-22_04-x86_64 -o simplex-chat
chmod +x simplex-chat
```

SimpleX Chat 项目没有为聊天客户端发布预构建的 Docker 镜像；要在 Docker 下运行，请从 [simplex-chat 仓库](https://github.com/simplex-chat/simplex-chat) 从源代码构建。

## 启动守护进程

```bash
simplex-chat -p 5225
```

默认情况下，守护进程在 `ws://127.0.0.1:5225` 上监听 WebSocket。

## 配置 Hermes

### 通过设置向导

```bash
hermes gateway setup
```

选择 **SimpleX Chat** 并按照提示操作。

### 通过环境变量

将这些添加到 `~/.hermes/.env`：

```
SIMPLEX_WS_URL=ws://127.0.0.1:5225
SIMPLEX_ALLOWED_USERS=<contact-id-1>,<contact-id-2>
SIMPLEX_HOME_CHANNEL=<contact-id>
```

| 变量 | 是否必需 | 描述 |
|---|---|---|
| `SIMPLEX_WS_URL` | 是 | simplex-chat 守护进程的 WebSocket URL |
| `SIMPLEX_ALLOWED_USERS` | 推荐 | 逗号分隔的允许列表。每个条目可以是数字 `contactId` **或** 显示名称 —— 两种形式都有效。 |
| `SIMPLEX_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 以允许所有联系人（谨慎使用） |
| `SIMPLEX_AUTO_ACCEPT` | 可选 | 自动接受传入的联系人请求（默认：`true`） |
| `SIMPLEX_GROUP_ALLOWED` | 可选 | 逗号分隔的机器人参与的群组 ID，或 `*` 表示任何群组。省略则完全忽略群组消息 |
| `SIMPLEX_HOME_CHANNEL` | 可选 | 定时任务交付的默认联系人/群组 ID |
| `SIMPLEX_HOME_CHANNEL_NAME` | 可选 | 主通道的人类可读标签 |
| `HERMES_SIMPLEX_TEXT_BATCH_DELAY` | 可选 | 静默期秒数（默认：`0.8`），用于将快速连续的入站文本消息连接成一个事件 |

## 查找您的联系人 ID 或显示名称

启动守护进程后，打开与您的 Agent 联系人的对话。数字 `contactId` 会出现在会话日志中或通过 `hermes send_message action=list` 获取。如果您更愿意使用 SimpleX UI 中显示的显示名称，那也有效 —— `SIMPLEX_ALLOWED_USERS` 接受两种形式。

## 授权

默认情况下 **所有联系人都被拒绝**。您必须：

1. 将 `SIMPLEX_ALLOWED_USERS` 设置为逗号分隔的 `contactId` 和/或显示名称列表（例如 `SIMPLEX_ALLOWED_USERS=4,alice` 匹配 contactId 4 或显示名称为 "alice" 的联系人），或者
2. 使用 **私信配对** —— 向机器人发送任何消息，它将回复一个配对码。通过 `hermes pairing approve simplex <CODE>` 输入该代码。

## 群聊

默认情况下，适配器会忽略群组消息 —— 否则群组中的机器人会处理每个成员的流量。需要显式选择加入：

```
SIMPLEX_GROUP_ALLOWED=12,34          # 特定的群组 ID
# 或
SIMPLEX_GROUP_ALLOWED=*              # 机器人所在的任何群组
```

通过在聊天 ID 前加上 `group:` 前缀来寻址群组，例如在 `send_message` 中或作为定时任务 `deliver=` 目标时使用 `simplex:group:12`。

## 附件

适配器支持双向的原生 SimpleX 附件：

- **入站** —— 传入的图片、语音消息和文件通过守护进程的 XFTP 流程接受（`rcvFileDescrReady` → `/freceive` → 等待 `rcvFileComplete`），并作为 `MessageEvent.media_urls` 呈现，带有适当的 `MessageType`（`PHOTO`、`VOICE`、`TEXT` + 文档）。
- **出站** —— `send_image_file`、`send_voice`、`send_document` 和 `send_video` 都使用带有 `filePath` 的结构化 `/_send` 表单，因此接收的 SimpleX 客户端会内联渲染图片并内联播放语音消息，而不是将它们作为下载提供。

Agent 回复也可以在纯文本中嵌入 `MEDIA:/path/to/file` 标签 —— 适配器会从正文中剥离该标签，并将文件作为语音消息（音频扩展名）或文档发送。

## 将 SimpleX 与定时任务一起使用

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="simplex",          # 使用 SIMPLEX_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或者指定特定联系人：

```python
send_message(target="simplex:<contact-id>", message="Done!")
```

## 隐私说明

- SimpleX 从不透露电话号码或电子邮件地址 —— 联系人使用不透明的 ID
- Hermes 和守护进程之间的连接是本地的 WebSocket（`ws://127.0.0.1:5225`）—— 数据不会离开您的机器
- 消息在到达守护进程之前已通过 SimpleX 协议进行端到端加密

## 故障排除

**"无法连接到守护进程"** —— 确保 `simplex-chat -p 5225` 正在运行，并且端口与 `SIMPLEX_WS_URL` 匹配。

**"websockets 未安装"** —— 运行 `pip install websockets`。

**"未收到消息"** —— 检查联系人的 ID 是否在 `SIMPLEX_ALLOWED_USERS` 中，或通过私信配对批准他们。