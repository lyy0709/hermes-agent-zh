# SimpleX Chat

[SimpleX Chat](https://simplex.chat/) 是一个私密、去中心化的消息平台，用户拥有自己的联系人和群组。与其他平台不同，SimpleX 不分配持久的用户 ID —— 每个联系人通过连接时生成的不透明内部 ID 来识别，这使其成为目前最私密的即时通讯工具之一。

> 运行 `hermes gateway setup` 并选择 **SimpleX** 以获取引导式设置。

## 先决条件

- 已安装 **simplex-chat** CLI 并作为守护进程运行
- Python 包 **websockets** (`pip install websockets`)

## 安装 simplex-chat

从 [simplex-chat GitHub releases](https://github.com/simplex-chat/simplex-chat/releases) 页面下载最新版本：

```bash
# Linux / macOS 二进制文件
curl -L https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-22_04-x86_64 -o simplex-chat
chmod +x simplex-chat
```

SimpleX Chat 项目不提供聊天客户端的预构建 Docker 镜像；要在 Docker 下运行，请从 [simplex-chat 仓库](https://github.com/simplex-chat/simplex-chat) 从源代码构建。

## 启动守护进程

```bash
simplex-chat -p 5225
```

默认情况下，守护进程在 `ws://127.0.0.1:5225` 上监听 WebSocket。

## 配置 Hermes

### 通过设置向导

```bash
hermes setup gateway
```

选择 **SimpleX Chat** 并按照提示操作。

### 通过环境变量

将这些添加到 `~/.hermes/.env`：

```
SIMPLEX_WS_URL=ws://127.0.0.1:5225
SIMPLEX_ALLOWED_USERS=<contact-id-1>,<contact-id-2>
SIMPLEX_HOME_CHANNEL=<contact-id>
```

| 变量 | 必需 | 描述 |
|---|---|---|
| `SIMPLEX_WS_URL` | 是 | simplex-chat 守护进程的 WebSocket URL |
| `SIMPLEX_ALLOWED_USERS` | 推荐 | 允许使用 Agent 的联系人 ID 列表，用逗号分隔 |
| `SIMPLEX_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 以允许所有联系人（谨慎使用） |
| `SIMPLEX_HOME_CHANNEL` | 可选 | 用于定时任务交付的默认联系人 ID |
| `SIMPLEX_HOME_CHANNEL_NAME` | 可选 | 主频道的人类可读标签 |

## 查找您的联系人 ID

启动守护进程后，打开与您的 Agent 联系人的对话。联系人 ID 将出现在会话日志中或通过 `hermes send_message action=list` 命令获取。

## 授权

默认情况下 **所有联系人都被拒绝**。您必须：

1. 将 `SIMPLEX_ALLOWED_USERS` 设置为逗号分隔的联系人 ID 列表，或者
2. 使用 **私信配对** —— 向机器人发送任何消息，它将回复一个配对码。通过 `hermes gateway pair` 输入该配对码。

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
- Hermes 与守护进程之间的连接是本地的 WebSocket (`ws://127.0.0.1:5225`) —— 数据不会离开您的机器
- 消息在到达守护进程之前已通过 SimpleX 协议进行端到端加密

## 故障排除

**“无法连接到守护进程”** —— 确保 `simplex-chat -p 5225` 正在运行，并且端口与 `SIMPLEX_WS_URL` 匹配。

**“未安装 websockets”** —— 运行 `pip install websockets`。

**未收到消息** —— 检查联系人的 ID 是否在 `SIMPLEX_ALLOWED_USERS` 中，或通过私信配对批准他们。