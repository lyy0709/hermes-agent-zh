---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 集成了 Matrix，这是一个开放、联邦式的消息协议。Matrix 允许您运行自己的家庭服务器或使用像 matrix.org 这样的公共服务器——无论哪种方式，您都能保持对通信的控制。该机器人通过 `mautrix` Python SDK 连接，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图像、音频、视频以及可选的端到端加密（E2EE）。

Hermes 可与任何 Matrix 家庭服务器配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在设置之前，以下是大多数人想知道的部分：Hermes 连接后的行为方式。

## Hermes 的行为方式

| 上下文 | 行为 |
|---------|----------|
| **私信** | Hermes 响应每条消息。无需 `@提及`。每个私信都有其独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可在私信中 `@提及` 机器人时启动一个线程。 |
| **群聊** | 默认情况下，Hermes 需要 `@提及` 才会响应。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 以创建自由响应房间。房间邀请会自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果您在线程中回复，Hermes 会保持线程上下文与主房间时间线隔离。机器人已参与的线程不需要提及。 |
| **自动线程化** | 默认情况下，Hermes 会为它在房间中响应的每条消息自动创建一个线程。这可以保持对话隔离。设置 `MATRIX_AUTO_THREAD=false` 来禁用。设置 `MATRIX_DM_AUTO_THREAD=true`（默认为 false）也可为私信消息自动创建线程——这与 `MATRIX_DM_MENTION_THREADS` 不同，后者仅在私信中 `@提及` 机器人时启动线程。 |
| **命令** | 当您的 Matrix 客户端发送普通 `/commands` 时，Hermes 会接受它们。如果您的客户端将 `/` 保留用于本地命令，请改用 `!commands`；Hermes 会将已知的 `!command` 别名规范化为 `/command`。 |
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
- 一个人冗长且工具密集的任务可能会使其他人的上下文膨胀
- 一个人正在进行的运行可能会中断另一个人在同一房间中的后续操作

### 提及和线程化配置

您可以通过环境变量或 `config.yaml` 配置提及和自动线程化行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @提及（默认：true）
  free_response_rooms:            # 免除提及要求的房间
    - "!abc123:matrix.org"
  auto_thread: true               # 为响应自动创建线程（默认：true）
  dm_mention_threads: false       # 在私信中 @提及时创建线程（默认：false）
```

或通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
MATRIX_REACTIONS=true          # 默认：true — 处理过程中的表情符号反应
```

:::tip 禁用反应
`MATRIX_REACTIONS=false` 会关闭机器人在接收消息时发布的生命周期表情符号反应（👀/✅/❌）。对于反应事件嘈杂或并非所有参与客户端都支持的房间很有用。
:::

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

2. 选择一个用户名，如 `hermes`——完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共家庭服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为您的机器人选择一个用户名（例如，`hermes-bot`）。

### 选项 C：使用您自己的账户

您也可以将 Hermes 作为您自己的用户运行。这意味着机器人以您的身份发布消息——对于个人助理很有用。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来向家庭服务器进行身份验证。您有两个选项：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 转到 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级**——访问令牌显示在那里。
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
响应中包含一个 `access_token` 字段 —— 请复制它。

:::warning[妥善保管你的访问令牌]
该访问令牌授予对机器人 Matrix 账户的完全访问权限。切勿公开分享或将其提交到 Git。如果令牌泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

除了提供访问令牌，你也可以给 Hermes 机器人的用户 ID 和密码。Hermes 将在启动时自动登录。这种方式更简单，但意味着密码会存储在你的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 步骤 3：找到你的 Matrix 用户 ID

Hermes Agent 使用你的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 遵循 `@用户名:服务器` 的格式。

要找到你的用户 ID：

1.  打开 [Element](https://app.element.io)（或你首选的 Matrix 客户端）。
2.  点击你的头像 → **设置**。
3.  你的用户 ID 会显示在个人资料顶部（例如，`@alice:matrix.org`）。

:::tip
Matrix 用户 ID 总是以 `@` 开头，并包含一个 `:` 后跟服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

当提示时，选择 **Matrix**，然后按要求提供你的 homeserver URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

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

- `group_sessions_per_user: true` 在共享房间内保持每个参与者的上下文隔离

### 启动消息网关

配置完成后，启动 Matrix 消息网关：

```bash
hermes gateway
```

机器人应该连接到你的 homeserver 并在几秒钟内开始同步。给它发送一条消息 —— 可以是私聊消息，也可以是它已加入的房间里的消息 —— 来进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 端到端加密 (E2EE)

Hermes 支持 Matrix 端到端加密，因此你可以在加密房间中与你的机器人聊天。

### 要求

E2EE 需要带有加密额外功能的 `mautrix` 库和 C 库 `libolm`：

```bash
# 安装支持 E2EE 的 mautrix
pip install 'mautrix[encryption]'

# 或者使用 hermes 额外功能安装
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

启用 E2EE 后，Hermes：

-   将加密密钥存储在 `~/.hermes/platforms/matrix/store/`（旧版本安装：`~/.hermes/matrix/store/`）
-   在首次连接时上传设备密钥
-   自动解密传入消息并加密传出消息
-   在被邀请时自动加入加密房间

### 交叉签名验证（推荐）

如果你的 Matrix 账户启用了交叉签名（Element 中的默认设置），请设置恢复密钥，以便机器人可以在启动时自行签名其设备。如果没有这个，其他 Matrix 客户端在设备密钥轮换后可能会拒绝与机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥在这里
```

**在哪里找到它：** 在 Element 中，转到 **设置** → **安全与隐私** → **加密** → 你的恢复密钥（也称为“安全密钥”）。这是你首次设置交叉签名时被要求保存的密钥。

每次启动时，如果设置了 `MATRIX_RECOVERY_KEY`，Hermes 会从 homeserver 的安全秘密存储中导入交叉签名密钥，并对当前设备进行签名。这是幂等的，可以安全地永久启用。

:::warning[删除加密存储]
如果你删除 `~/.hermes/platforms/matrix/store/crypto.db`，机器人将丢失其加密身份。仅使用相同的设备 ID 重新启动**无法**完全恢复 —— homeserver 仍然持有用旧身份密钥签名的一次性密钥，对等方无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况并拒绝启用 E2EE，记录：`设备 XXXX 在服务器上有用先前身份密钥签名的陈旧一次性密钥`。

**最简单的恢复方法：生成一个新的访问令牌**（这将获得一个没有陈旧密钥历史的新设备 ID）。请参阅下面的“从先前版本升级并启用 E2EE”部分。这是最可靠的路径，并且避免了接触 homeserver 数据库。

**手动恢复**（高级 —— 保持相同的设备 ID）：

1.  停止 Synapse 并从其数据库中删除旧设备：
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
    或者通过 Synapse 管理 API（注意 URL 编码的用户 ID）：
    ```bash
    curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
      'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
    ```
    注意：通过管理 API 删除设备也可能使相关的访问令牌失效。之后你可能需要生成一个新的令牌。
:::
2. 删除本地加密存储并重启 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # 重启 hermes
   ```

其他 Matrix 客户端（Element、matrix-commander）可能会缓存旧的设备密钥。恢复后，在 Element 中输入 `/discardsession` 以强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人会自动回退到普通（未加密）客户端。您将在日志中看到警告。
:::

## 主房间

您可以指定一个“主房间”，机器人会在此发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在机器人所在的任何 Matrix 房间中输入 `/sethome`。该房间将成为主房间。
如果您的 Matrix 客户端拦截斜杠命令，请改用 `!sethome`。

### 手动配置

将此添加到您的 `~/.hermes/.env`：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

## 房间允许列表 (`allowed_rooms`)

将机器人限制在一组固定的 Matrix 房间中。设置后，机器人**仅**在 ID 出现在列表中的房间内响应——来自任何其他房间的消息都会被静默忽略，即使机器人被提及。

**私聊（直接聊天房间）不受此过滤器限制**，因此授权用户始终可以与机器人进行一对一交流。

```yaml
matrix:
  allowed_rooms:
    - "!abc123def456:matrix.example.org"
    - "!opsroom789:matrix.example.org"
```

或通过环境变量（逗号分隔）：

```bash
MATRIX_ALLOWED_ROOMS="!abc123def456:matrix.example.org,!opsroom789:matrix.example.org"
```

行为：

- 空/未设置 → 无限制（默认）。
- 非空 → 房间 ID 必须在列表中。此检查在**任何**其他门控（提及要求、发送者允许列表等）**之前**运行。
- 使用房间的**内部 ID** (`!abc...:server`)，而不是其别名 (`#room:server`)。您可以在 Element 中通过房间 → 设置 → 高级找到房间的内部 ID。

另请参阅：[管理员/用户斜杠命令拆分](../../reference/slash-commands.md#permissions-and-adminuser-split)。

:::tip
要查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → **内部房间 ID** 显示在那里（以 `!` 开头）。
:::

## Matrix 中的命令

Hermes 在 Matrix 中支持与其他消息平台相同的消息网关命令，包括 `/commands`、`/model`、`/stop`、`/queue`、`/steer`、`/goal`、`/subgoal`、`/background`、`/bg`、`/btw`、`/tasks` 和 `/yolo`。

一些 Matrix 客户端保留前导 `/` 用于本地客户端命令，可能不会将未知的斜杠命令发送到房间。在这种情况下，请使用 `!` 作为 Matrix 安全的别名：

```text
!commands
!model
!model gpt-5.5 --provider openrouter
!queue continue with the next task
!stop
```

Hermes 仅在命令为消息网关已知、已注册的插件命令或已安装的技能命令时，才会将 `!command` 标准化。普通的感叹句（如 `!important`）仍被视为普通聊天消息。

## 故障排除

### 机器人不响应消息

**原因**：机器人尚未加入房间，或者 `MATRIX_ALLOWED_USERS` 未包含您的用户 ID。

**修复**：邀请机器人加入房间——它会在收到邀请时自动加入。验证您的用户 ID 是否在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式）。重启消息网关。

### 机器人加入房间但静默丢弃每条消息（时钟偏差）

**原因**：主机的系统时钟设置得比实际时间快。Matrix 适配器应用了一个 5 秒的启动宽限过滤器 (`event_ts < startup_ts - 5`) 来忽略从初始同步重放的事件。当挂钟时间超前时，每个传入事件看起来都“比启动时间旧”，并在到达消息处理程序之前被丢弃——机器人看起来已连接但从不回复。参见 [#12614](https://github.com/NousResearch/hermes-agent/issues/12614)。

**症状**：消息网关日志显示 `Matrix: dropped N live events as 'too old' more than 30s after startup`。

**修复**：使用 NTP 同步主机时钟并重启机器人：

```bash
# Debian/Ubuntu
sudo timedatectl set-ntp true
timedatectl status   # 确认 "System clock synchronized: yes"

# macOS
sudo sntp -sS time.apple.com
```

### 启动时出现“Failed to authenticate” / “whoami failed”

**原因**：访问令牌或家庭服务器 URL 不正确。

**修复**：验证 `MATRIX_HOMESERVER` 指向您的家庭服务器（包含 `https://`，无尾部斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效——使用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回您的用户信息，则令牌有效。如果返回错误，请生成新令牌。

### “mautrix not installed” 错误

**原因**：未安装 `mautrix` Python 包。

**修复**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或使用 Hermes 扩展：

```bash
pip install 'hermes-agent[matrix]'
```

### 加密错误 / “could not decrypt event”

**原因**：缺少加密密钥、未安装 `libolm` 或机器人的设备不受信任。

**修复**：
1. 验证系统上已安装 `libolm`（参见上面的 E2EE 部分）。
2. 确保在 `.env` 中设置了 `MATRIX_ENCRYPTION=true`。
3. 在您的 Matrix 客户端（Element）中，转到机器人的个人资料 -> 会话 -> 验证/信任机器人的设备。
4. 如果机器人刚加入加密房间，它只能解密在它加入*之后*发送的消息。较早的消息无法访问。

### 从带有 E2EE 的先前版本升级

:::tip
如果您还手动删除了 `crypto.db`，请参阅上面 E2EE 部分中的“删除加密存储”警告——需要额外的步骤来清除家庭服务器中过时的一次性密钥。
:::

如果您之前使用带有 `MATRIX_ENCRYPTION=true` 的 Hermes，并升级到使用新的基于 SQLite 的加密存储的版本，机器人的加密身份已更改。您的 Matrix 客户端（Element）可能会缓存旧的设备密钥，并拒绝与机器人共享加密会话。

**症状**：机器人连接并在日志中显示“E2EE enabled”，但所有消息都显示“could not decrypt event”且机器人从不响应。
**问题原因**：旧的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。机器人创建了新的加密身份，但你的 Matrix 客户端仍然缓存着旧的密钥，并且不会与密钥已更改的设备共享房间的加密会话。这是 Matrix 的一项安全功能——客户端会将同一设备更改身份密钥的行为视为可疑。

**修复方法**（一次性迁移）：

1.  **生成新的访问令牌**以获取新的设备 ID。最简单的方法：

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

2.  **删除旧的加密状态**：

    ```bash
    rm -f ~/.hermes/platforms/matrix/store/crypto.db
    rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
    ```

3.  **设置你的恢复密钥**（如果你使用交叉签名——大多数 Element 用户都使用）。添加到 `~/.hermes/.env`：

    ```bash
    MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥放在这里
    ```

    这允许机器人在启动时使用交叉签名密钥进行自签名，因此 Element 会立即信任新设备。如果没有这个，Element 可能会将新设备视为未验证，并拒绝共享加密会话。在 Element 的 **设置** → **安全与隐私** → **加密** 下找到你的恢复密钥。

4.  **强制你的 Matrix 客户端轮换加密会话**。在 Element 中，打开与机器人的私聊房间并输入 `/discardsession`。这会强制 Element 创建新的加密会话并与机器人的新设备共享。

5.  **重启消息网关**：

    ```bash
    hermes gateway run
    ```

    如果设置了 `MATRIX_RECOVERY_KEY`，你应该在日志中看到 `Matrix: cross-signing verified via recovery key`。

6.  **发送新消息**。机器人应该能正常解密和回复。

:::note
迁移后，*升级前*发送的消息将无法解密——旧的加密密钥已丢失。这只影响过渡期；新消息正常工作。
:::

:::tip
**新安装不受影响。** 此迁移仅在你之前使用 Hermes 旧版本建立了正常工作的 E2EE 设置并正在升级时才需要。

**为什么需要新的访问令牌？** 每个 Matrix 访问令牌都绑定到特定的设备 ID。使用新的加密密钥重用相同的设备 ID 会导致其他 Matrix 客户端不信任该设备（它们将更改的身份密钥视为潜在的安全漏洞）。新的访问令牌会获得一个没有陈旧密钥历史的新设备 ID，因此其他客户端会立即信任它。
:::

## 代理模式（macOS 上的 E2EE）

Matrix E2EE 需要 `libolm`，而该库无法在 macOS ARM64（Apple Silicon）上编译。`hermes-agent[matrix]` 额外依赖项仅限 Linux。如果你在 macOS 上，代理模式允许你在 Linux 虚拟机上的 Docker 容器中运行 E2EE，而实际的 Agent 则在 macOS 上原生运行，可以完全访问你的本地文件、记忆和技能。

### 工作原理

```
macOS (主机):
  └─ hermes gateway
       ├─ api_server 适配器 ← 监听 0.0.0.0:8642
       ├─ AIAgent ← 单一事实来源
       ├─ 会话、记忆、技能
       └─ 本地文件访问 (Obsidian、项目等)

Linux VM (Docker):
  └─ hermes gateway (代理模式)
       ├─ Matrix 适配器 ← E2EE 解密/加密
       └─ HTTP 转发 → macOS:8642/v1/chat/completions
           (无 LLM API 密钥，无 Agent，无推理)
```

Docker 容器仅处理 Matrix 协议 + E2EE。当消息到达时，它解密消息并通过标准 HTTP 请求将文本转发给主机。主机运行 Agent，调用工具，生成响应，并将其流式传输回来。容器加密响应并将其发送到 Matrix。所有会话都是统一的——CLI、Matrix、Telegram 和任何其他平台共享相同的记忆和对话历史。

### 步骤 1：配置主机（macOS）

启用 API 服务器，以便主机接受来自 Docker 容器的传入请求。

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```

-   `API_SERVER_HOST=0.0.0.0` 绑定到所有接口，以便 Docker 容器可以访问它。
-   `API_SERVER_KEY` 对于非环回绑定是必需的。选择一个强随机字符串。
-   API 服务器默认在端口 8642 上运行（如果需要，可以使用 `API_SERVER_PORT` 更改）。

启动消息网关：

```bash
hermes gateway
```

你应该会看到 API 服务器与你配置的任何其他平台一起启动。验证它可以从虚拟机访问：

```bash
# 从 Linux VM
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

      # 代理模式 — 转发到主机 Agent
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

这就是整个容器。没有 OpenRouter、Anthropic 或任何推理提供商的 API 密钥。

### 步骤 3：启动两者

1.  首先启动主机消息网关：
    ```bash
    hermes gateway
    ```
2.  启动 Docker 容器：
    ```bash
    docker compose up -d
    ```
3. 在加密的 Matrix 房间中发送消息。容器会解密消息，将其转发给主机，并流式传回响应。

### 配置参考

代理模式在**容器端**（瘦网关）进行配置：

| 设置项 | 描述 |
|---------|-------------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如，`http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于身份验证的 Bearer token（必须与主机上的 `API_SERVER_KEY` 匹配） |
| `gateway.proxy_url` | 与 `GATEWAY_PROXY_URL` 相同，但在 `config.yaml` 中配置 |

主机端需要：

| 设置项 | 描述 |
|---------|-------------|
| `API_SERVER_ENABLED` | 设置为 `true` |
| `API_SERVER_KEY` | Bearer token（与容器共享） |
| `API_SERVER_HOST` | 设置为 `0.0.0.0` 以允许网络访问 |
| `API_SERVER_PORT` | 端口号（默认：`8642`） |

### 适用于任何平台

代理模式不仅限于 Matrix。任何平台适配器都可以使用它——在任何网关实例上设置 `GATEWAY_PROXY_URL`，它就会将请求转发到远程 Agent，而不是在本地运行一个。这对于任何需要平台适配器在与 Agent 不同的环境中运行（网络隔离、E2EE 要求、资源限制）的部署都很有用。

:::tip
会话连续性通过 `X-Hermes-Session-Id` 请求头来维护。主机的 API 服务器通过此 ID 跟踪会话，因此对话在消息之间持续存在，就像使用本地 Agent 一样。
:::

:::note
**限制（v1）：** 来自远程 Agent 的工具进度消息不会被中继回来——用户只能看到流式传输的最终响应，而不是单个的工具调用。危险命令的批准提示在主机端处理，不会中继给 Matrix 用户。这些问题可以在未来的更新中解决。
:::

### 同步问题 / Bot 响应滞后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者 homeserver 速度较慢。

**修复**：同步循环在出错时会自动每 5 秒重试一次。请检查 Hermes 日志中与同步相关的警告。如果 Bot 持续滞后，请确保您的 homeserver 拥有足够的资源。

### Bot 离线

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：错误的 homeserver URL、过期的访问令牌、homeserver 无法访问。

### "用户不被允许" / Bot 忽略您

**原因**：您的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**修复**：将您的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATRIX_ALLOWED_USERS` 并重启网关。请使用完整的 `@user:server` 格式。

## 安全

:::warning
务必设置 `MATRIX_ALLOWED_USERS` 以限制可以与 Bot 交互的人员。如果不设置，作为安全措施，网关默认会拒绝所有用户。只添加您信任的用户 ID——授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

- **任何 homeserver**：适用于 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix homeserver。无需特定的 homeserver 软件。
- **联邦**：如果您在联邦 homeserver 上，Bot 可以与其他服务器的用户通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 中。
- **自动加入**：Bot 会自动接受房间邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图像、音频、视频和文件附件。媒体使用 Matrix 内容存储库 API 上传到您的 homeserver。
- **原生语音消息（MSC3245）**：Matrix 适配器会自动为发出的语音消息打上 `org.matrix.msc3245.voice` 标签。这意味着 TTS 响应和语音音频在 Element 和其他支持 MSC3245 的客户端中会呈现为**原生语音气泡**，而不是作为通用的音频文件附件。带有 MSC3245 标签的传入语音消息也能被正确识别并路由到语音转文字转录。无需配置——此功能自动生效。