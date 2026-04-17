---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 与 Matrix（开放的联邦式消息协议）集成。Matrix 允许您运行自己的家庭服务器或使用公共服务器（如 matrix.org）——无论哪种方式，您都能控制自己的通信。机器人通过 `mautrix` Python SDK 连接，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图像、音频、视频以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix 家庭服务器配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在设置之前，以下是大多数人想知道的部分：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| **私信** | Hermes 响应每条消息。无需 `@提及`。每个私信都有其独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可在私信中 `@提及` 机器人时启动一个线程。 |
| **群聊** | 默认情况下，Hermes 需要 `@提及` 才会响应。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 以启用自由响应房间。房间邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果您在线程中回复，Hermes 会保持线程上下文与主房间时间线隔离。机器人已参与的线程不需要提及。 |
| **自动线程化** | 默认情况下，Hermes 会为它在房间中响应的每条消息自动创建一个线程。这可以保持对话隔离。设置 `MATRIX_AUTO_THREAD=false` 来禁用此功能。 |
| **多用户共享房间** | 默认情况下，Hermes 在房间内为每个用户隔离会话历史记录。两个人在同一个房间中交谈不会共享一个对话记录，除非您明确禁用该功能。 |

:::tip
机器人被邀请时会自动加入房间。只需将机器人的 Matrix 用户邀请到任何房间，它就会加入并开始响应。
:::

### Matrix 中的会话模型

默认情况下：

- 每个私信都有其独立的会话
- 每个线程都有其独立的会话命名空间
- 共享房间中的每个用户在该房间内都有其独立的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅在您明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

- 用户共享上下文增长和 Token 成本
- 一个人的长时间、工具密集型的任务可能会使其他人的上下文膨胀
- 一个人正在运行的任务可能会中断另一个人在同一房间中的后续操作

### 提及和线程化配置

您可以通过环境变量或 `config.yaml` 配置提及和自动线程化行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @提及（默认：true）
  free_response_rooms:            # 免除提及要求的房间
    - "!abc123:matrix.org"
  auto_thread: true               # 为响应自动创建线程（默认：true）
  dm_mention_threads: false       # 在私信中 @提及 时创建线程（默认：false）
```

或通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
```

:::note
如果您是从没有 `MATRIX_REQUIRE_MENTION` 的版本升级，机器人之前会响应房间中的所有消息。要保留该行为，请设置 `MATRIX_REQUIRE_MENTION=false`。
:::

本指南将引导您完成完整的设置过程——从创建机器人账户到发送第一条消息。

## 步骤 1：创建机器人账户

您需要一个 Matrix 用户账户作为机器人。有几种方法可以做到这一点：

### 选项 A：在您的家庭服务器上注册（推荐）

如果您运行自己的家庭服务器（Synapse、Conduit、Dendrite）：

1. 使用管理员 API 或注册工具创建新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，如 `hermes` —— 完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共家庭服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为您的机器人选择一个用户名（例如，`hermes-bot`）。

### 选项 C：使用您自己的账户

您也可以将 Hermes 作为您自己的用户运行。这意味着机器人将以您的身份发布消息——对于个人助手很有用。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来向家庭服务器进行身份验证。您有两个选项：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 转到 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级** —— 访问令牌显示在那里。
4. **立即复制它。**

**通过 API：**

```bash
curl -X POST https://your-server/_matrix/client/v3/login \
  -H "Content-Type: application/json" \
  -d '{
    "type": "m.login.password",
    "user": "@hermes:your-server.org",
    "password": "your-password"
  }'
```

响应中包含一个 `access_token` 字段 —— 复制它。

:::warning[妥善保管您的访问令牌]
访问令牌授予对机器人 Matrix 账户的完全访问权限。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

您可以为 Hermes 提供机器人的用户 ID 和密码，而不是提供访问令牌。Hermes 将在启动时自动登录。这更简单，但意味着密码存储在您的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 步骤 3：找到您的 Matrix 用户 ID

Hermes Agent 使用您的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 遵循格式 `@username:server`。
要找到你的用户 ID：

1. 打开 [Element](https://app.element.io)（或你偏好的 Matrix 客户端）。
2. 点击你的头像 → **设置**。
3. 你的用户 ID 会显示在个人资料顶部（例如：`@alice:matrix.org`）。

:::tip
Matrix 用户 ID 总是以 `@` 开头，并包含一个 `:` 后跟服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

当提示时选择 **Matrix**，然后按要求提供你的 homeserver URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略，将从令牌自动检测）
# MATRIX_USER_ID=@hermes:matrix.example.org

# 安全：限制谁可以与机器人交互
MATRIX_ALLOWED_USERS=@alice:matrix.example.org

# 多个允许的用户（逗号分隔）
# MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
```

**使用密码登录：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_USER_ID=@hermes:matrix.example.org
MATRIX_PASSWORD=***

# 安全
MATRIX_ALLOWED_USERS=@alice:matrix.example.org
```

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享房间内隔离每个参与者的上下文

### 启动消息网关

配置完成后，启动 Matrix 消息网关：

```bash
hermes gateway
```

机器人应该连接到你的 homeserver 并在几秒钟内开始同步。发送一条消息给它——可以是私聊或在它已加入的房间中——进行测试。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 端到端加密 (E2EE)

Hermes 支持 Matrix 端到端加密，因此你可以在加密房间中与你的机器人聊天。

### 要求

E2EE 需要带有加密额外功能的 `mautrix` 库和 `libolm` C 库：

```bash
# 安装支持 E2EE 的 mautrix
pip install 'mautrix[encryption]'

# 或安装带有 hermes 额外功能的版本
pip install 'hermes-agent[matrix]'
```

你还需要在系统上安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用 E2EE

添加到你的 `~/.hermes/.env`：

```bash
MATRIX_ENCRYPTION=true
```

当 E2EE 启用时，Hermes：

- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/`（旧版安装：`~/.hermes/matrix/store/`）
- 在首次连接时上传设备密钥
- 自动解密传入消息并加密传出消息
- 在被邀请时自动加入加密房间

### 交叉签名验证（推荐）

如果你的 Matrix 账户启用了交叉签名（Element 中的默认设置），请设置恢复密钥，以便机器人可以在启动时自签名其设备。如果没有这个，其他 Matrix 客户端在设备密钥轮换后可能会拒绝与机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥在这里
```

**在哪里找到它：** 在 Element 中，转到 **设置** → **安全与隐私** → **加密** → 你的恢复密钥（也称为“安全密钥”）。这是你首次设置交叉签名时被要求保存的密钥。

每次启动时，如果设置了 `MATRIX_RECOVERY_KEY`，Hermes 会从 homeserver 的安全秘密存储中导入交叉签名密钥并签名当前设备。这是幂等的，可以安全地永久启用。

:::warning[删除加密存储]
如果你删除 `~/.hermes/platforms/matrix/store/crypto.db`，机器人将丢失其加密身份。仅使用相同的设备 ID 重启**不会**完全恢复——homeserver 仍然持有用旧身份密钥签名的一次性密钥，对等方无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况并拒绝启用 E2EE，记录：`device XXXX has stale one-time keys on the server signed with a previous identity key`。

**最简单的恢复方法：生成一个新的访问令牌**（这会获得一个没有陈旧密钥历史的新设备 ID）。请参阅下面的“从带有 E2EE 的先前版本升级”部分。这是最可靠的路径，避免触及 homeserver 数据库。

**手动恢复**（高级——保持相同的设备 ID）：

1. 停止 Synapse 并从其数据库中删除旧设备：
   ```bash
   sudo systemctl stop matrix-synapse
   sudo sqlite3 /var/lib/matrix-synapse/homeserver.db "
     DELETE FROM e2e_device_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_one_time_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_fallback_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM devices WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
   "
   sudo systemctl start matrix-synapse
   ```
   或通过 Synapse 管理 API（注意 URL 编码的用户 ID）：
   ```bash
   curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
     'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
   ```
   注意：通过管理 API 删除设备也可能使相关的访问令牌失效。之后你可能需要生成一个新的令牌。

2. 删除本地加密存储并重启 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # 重启 hermes
   ```

其他 Matrix 客户端（Element、matrix-commander）可能会缓存旧的设备密钥。恢复后，在 Element 中输入 `/discardsession` 以强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人会自动回退到普通（未加密）客户端。你会在日志中看到警告。
:::
## 主房间

你可以指定一个"主房间"，让机器人主动发送消息（例如定时任务输出、提醒和通知）。有两种设置方式：

### 使用斜杠命令

在机器人所在的任何 Matrix 房间中，输入 `/sethome`。该房间将成为主房间。

### 手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

:::tip
要查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → **内部房间 ID** 显示在那里（以 `!` 开头）。
:::

## 故障排除

### 机器人不响应消息

**原因**：机器人尚未加入房间，或者 `MATRIX_ALLOWED_USERS` 未包含你的用户 ID。

**解决方法**：邀请机器人加入房间 — 收到邀请后它会自动加入。确认你的用户 ID 在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重启消息网关。

### 启动时出现"Failed to authenticate" / "whoami failed"错误

**原因**：访问令牌或家庭服务器 URL 不正确。

**解决方法**：验证 `MATRIX_HOMESERVER` 指向你的家庭服务器（包含 `https://`，末尾没有斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效 — 使用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回你的用户信息，则令牌有效。如果返回错误，请生成新令牌。

### "mautrix not installed"错误

**原因**：未安装 `mautrix` Python 包。

**解决方法**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或者使用 Hermes 扩展包：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误 / "could not decrypt event"

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备未被信任。

**解决方法**：
1. 验证系统上已安装 `libolm`（参见上面的 E2EE 部分）。
2. 确保在 `.env` 中设置了 `MATRIX_ENCRYPTION=true`。
3. 在你的 Matrix 客户端（Element）中，进入机器人资料 -> 会话 -> 验证/信任机器人的设备。
4. 如果机器人刚加入加密房间，它只能解密*加入后*发送的消息。旧消息无法访问。

### 从使用 E2EE 的旧版本升级

:::tip
如果你还手动删除了 `crypto.db`，请参阅上面 E2EE 部分中的"Deleting the crypto store"警告 — 需要额外步骤来清除家庭服务器上过时的一次性密钥。
:::

如果你之前使用 Hermes 时设置了 `MATRIX_ENCRYPTION=true`，并且正在升级到使用新的基于 SQLite 的加密存储的版本，机器人的加密身份已更改。你的 Matrix 客户端（Element）可能会缓存旧的设备密钥，并拒绝与机器人共享加密会话。

**症状**：机器人连接并在日志中显示"E2EE enabled"，但所有消息都显示"could not decrypt event"，且机器人从不响应。

**原因**：旧的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。机器人创建了新的加密身份，但你的 Matrix 客户端仍然缓存了旧密钥，并且不会与密钥已更改的设备共享房间的加密会话。这是 Matrix 的安全特性 — 客户端将同一设备更改的身份密钥视为可疑。

**解决方法**（一次性迁移）：

1. **生成新的访问令牌**以获取新的设备 ID。最简单的方法：

   ```bash
   curl -X POST https://your-server/_matrix/client/v3/login \
     -H "Content-Type: application/json" \
     -d '{
       "type": "m.login.password",
       "identifier": {"type": "m.id.user", "user": "@hermes:your-server.org"},
       "password": "***",
       "initial_device_display_name": "Hermes Agent"
     }'
   ```

   复制新的 `access_token` 并更新 `~/.hermes/.env` 中的 `MATRIX_ACCESS_TOKEN`。

2. **删除旧的加密状态**：

   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db
   rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
   ```

3. **设置你的恢复密钥**（如果你使用交叉签名 — 大多数 Element 用户使用）。添加到 `~/.hermes/.env`：

   ```bash
   MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥在这里
   ```

   这允许机器人在启动时使用交叉签名密钥进行自签名，因此 Element 会立即信任新设备。如果没有这个，Element 可能会将新设备视为未验证，并拒绝共享加密会话。在 Element 的**设置** → **安全与隐私** → **加密**下找到你的恢复密钥。

4. **强制你的 Matrix 客户端轮换加密会话**。在 Element 中，打开与机器人的私聊房间并输入 `/discardsession`。这会强制 Element 创建新的加密会话并与机器人的新设备共享。

5. **重启消息网关**：

   ```bash
   hermes gateway run
   ```

   如果设置了 `MATRIX_RECOVERY_KEY`，你应该在日志中看到 `Matrix: cross-signing verified via recovery key`。

6. **发送新消息**。机器人应该能正常解密和响应。

:::note
迁移后，*升级前*发送的消息无法解密 — 旧的加密密钥已丢失。这仅影响过渡期；新消息正常工作。
:::

:::tip
**新安装不受影响。** 此迁移仅在你之前使用 Hermes 的旧版本设置了有效的 E2EE 并正在升级时才需要。

**为什么需要新的访问令牌？** 每个 Matrix 访问令牌都绑定到特定的设备 ID。使用新的加密密钥重用相同的设备 ID 会导致其他 Matrix 客户端不信任该设备（它们将更改的身份密钥视为潜在的安全漏洞）。新的访问令牌会获得一个没有陈旧密钥历史的新设备 ID，因此其他客户端会立即信任它。
:::

## 代理模式（macOS 上的 E2EE）

Matrix E2EE 需要 `libolm`，而它在 macOS ARM64（Apple Silicon）上无法编译。`hermes-agent[matrix]` 扩展包仅限 Linux。如果你在 macOS 上，代理模式允许你在 Linux VM 的 Docker 容器中运行 E2EE，而实际的 Agent 在 macOS 上原生运行，完全访问你的本地文件、记忆和技能。
### 工作原理

```
macOS（宿主机）：
  └─ hermes 消息网关
       ├─ api_server 适配器 ← 监听 0.0.0.0:8642
       ├─ AIAgent ← 单一事实来源
       ├─ 会话、记忆、技能
       └─ 本地文件访问（Obsidian、项目等）

Linux VM（Docker）：
  └─ hermes 消息网关（代理模式）
       ├─ Matrix 适配器 ← E2EE 解密/加密
       └─ HTTP 转发 → macOS:8642/v1/chat/completions
           （无 LLM API 密钥，无 Agent，无推理）
```

Docker 容器仅处理 Matrix 协议和端到端加密。当消息到达时，它解密消息并通过标准 HTTP 请求将文本转发给宿主机。宿主机运行 Agent、调用工具、生成响应并流式传输回来。容器对响应进行加密并发送到 Matrix。所有会话都是统一的——CLI、Matrix、Telegram 以及任何其他平台共享相同的记忆和对话历史。

### 步骤 1：配置宿主机（macOS）

启用 API 服务器，以便宿主机接受来自 Docker 容器的传入请求。

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```

- `API_SERVER_HOST=0.0.0.0` 绑定到所有接口，以便 Docker 容器可以访问它。
- `API_SERVER_KEY` 对于非环回绑定是必需的。选择一个强随机字符串。
- API 服务器默认在端口 8642 上运行（如果需要，可以使用 `API_SERVER_PORT` 更改）。

启动消息网关：

```bash
hermes gateway
```

您应该会看到 API 服务器与您配置的任何其他平台一起启动。验证它可以从虚拟机访问：

```bash
# 从 Linux 虚拟机
curl http://<mac-ip>:8642/health
```

### 步骤 2：配置 Docker 容器（Linux VM）

容器需要 Matrix 凭据和代理 URL。它**不需要** LLM API 密钥。

**`docker-compose.yml`：**

```yaml
services:
  hermes-matrix:
    build: .
    environment:
      # Matrix 凭据
      MATRIX_HOMESERVER: "https://matrix.example.org"
      MATRIX_ACCESS_TOKEN: "syt_..."
      MATRIX_ALLOWED_USERS: "@you:matrix.example.org"
      MATRIX_ENCRYPTION: "true"
      MATRIX_DEVICE_ID: "HERMES_BOT"

      # 代理模式 — 转发到宿主机 Agent
      GATEWAY_PROXY_URL: "http://192.168.1.100:8642"
      GATEWAY_PROXY_KEY: "your-secret-key-here"
    volumes:
      - ./matrix-store:/root/.hermes/platforms/matrix/store
```

**`Dockerfile`：**

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libolm-dev && rm -rf /var/lib/apt/lists/*
RUN pip install 'hermes-agent[matrix]'

CMD ["hermes", "gateway"]
```

这就是整个容器。没有用于 OpenRouter、Anthropic 或任何推理提供商的 API 密钥。

### 步骤 3：启动两者

1. 首先启动宿主机消息网关：
   ```bash
   hermes gateway
   ```

2. 启动 Docker 容器：
   ```bash
   docker compose up -d
   ```

3. 在加密的 Matrix 房间中发送消息。容器解密消息，将其转发给宿主机，并流式传输回响应。

### 配置参考

代理模式在**容器端**（精简的消息网关）配置：

| 设置 | 描述 |
|---------|-------------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如，`http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于身份验证的 Bearer Token（必须与宿主机上的 `API_SERVER_KEY` 匹配） |
| `gateway.proxy_url` | 与 `GATEWAY_PROXY_URL` 相同，但在 `config.yaml` 中 |

宿主机端需要：

| 设置 | 描述 |
|---------|-------------|
| `API_SERVER_ENABLED` | 设置为 `true` |
| `API_SERVER_KEY` | Bearer Token（与容器共享） |
| `API_SERVER_HOST` | 设置为 `0.0.0.0` 以进行网络访问 |
| `API_SERVER_PORT` | 端口号（默认：`8642`） |

### 适用于任何平台

代理模式不仅限于 Matrix。任何平台适配器都可以使用它——在任何消息网关实例上设置 `GATEWAY_PROXY_URL`，它将转发到远程 Agent，而不是在本地运行一个。这对于平台适配器需要在与 Agent 不同的环境中运行的任何部署（网络隔离、E2EE 要求、资源限制）都很有用。

:::tip
会话连续性通过 `X-Hermes-Session-Id` 标头维护。宿主机的 API 服务器通过此 ID 跟踪会话，因此对话在消息之间持续存在，就像使用本地 Agent 一样。
:::

:::note
**限制（v1）：** 来自远程 Agent 的工具进度消息不会被中继回来——用户只能看到流式传输的最终响应，而不是单个工具调用。危险的命令批准提示在宿主机端处理，不会中继给 Matrix 用户。这些问题可以在未来的更新中解决。
:::

### 同步问题 / 机器人掉队

**原因**：长时间运行的工具执行可能会延迟同步循环，或者主服务器速度慢。

**修复**：同步循环在出错时每 5 秒自动重试。检查 Hermes 日志中与同步相关的警告。如果机器人持续掉队，请确保您的主服务器有足够的资源。

### 机器人离线

**原因**：Hermes 消息网关未运行，或者连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误消息。常见问题：错误的主服务器 URL、过期的访问令牌、主服务器无法访问。

### "用户不允许" / 机器人忽略您

**原因**：您的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**修复**：将您的用户 ID 添加到 `~/.hermes/.env` 中的 `MATRIX_ALLOWED_USERS` 并重新启动消息网关。使用完整的 `@user:server` 格式。

## 安全性

:::warning
始终设置 `MATRIX_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，作为安全措施，消息网关默认拒绝所有用户。只添加您信任的人的用户 ID——授权用户拥有对 Agent 功能的完全访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

- **任何主服务器**：适用于 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix 主服务器。不需要特定的主服务器软件。
- **联邦**：如果您在联邦主服务器上，机器人可以与来自其他服务器的用户通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS`。
- **自动加入**：机器人自动接受房间邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图像、音频、视频和文件附件。媒体使用 Matrix 内容存储库 API 上传到您的主服务器。
- **原生语音消息（MSC3245）**：Matrix 适配器自动将传出的语音消息标记为 `org.matrix.msc3245.voice` 标志。这意味着 TTS 响应和语音音频在 Element 和其他支持 MSC3245 的客户端中呈现为**原生语音气泡**，而不是作为通用音频文件附件。带有 MSC3245 标志的传入语音消息也能被正确识别并路由到语音转文本转录。无需配置——这自动生效。