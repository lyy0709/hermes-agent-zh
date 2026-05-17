# Spotify

Hermes 可以直接控制 Spotify —— 播放、队列、搜索、播放列表、已保存的曲目/专辑和收听历史 —— 使用 Spotify 官方的 Web API 和 PKCE OAuth。Token 存储在 `~/.hermes/auth.json` 中，并在收到 401 错误时自动刷新；每台机器只需登录一次。

与 Hermes 内置的 OAuth 集成（Google、GitHub Copilot、Codex）不同，Spotify 要求每个用户注册自己的轻量级开发者应用。Spotify 不允许第三方发布可供任何人使用的公共 OAuth 应用。这大约需要两分钟，`hermes auth spotify` 会引导您完成整个过程。

## 前提条件

- 一个 Spotify 账户。**免费**账户适用于搜索、播放列表、资料库和活动工具。**Premium** 账户是播放控制（播放、暂停、跳过、跳转、音量、添加队列、转移）所必需的。
- Hermes Agent 已安装并正在运行。
- 对于播放工具：需要一个**活跃的 Spotify Connect 设备** —— Spotify 应用必须在至少一个设备（手机、桌面、网页播放器、扬声器）上打开，以便 Web API 有可以控制的对象。如果没有活跃设备，您会收到带有“no active device”消息的 `403 Forbidden` 错误；在任何设备上打开 Spotify 并重试。

## 设置

### 一键完成：`hermes tools` 或首次运行设置

最快的路径。运行：

```bash
hermes tools
```

滚动到 `🎵 Spotify`，按空格键切换为开启，然后按 `s` 保存。首次运行 `hermes setup` / `hermes setup tools` 流程中也有相同的切换选项。Spotify 保持为可选功能，因此在那里启用它会运行与 `hermes tools` 相同的提供商感知配置。

Hermes 会直接将您带入 OAuth 流程 —— 如果您还没有 Spotify 应用，它会引导您在线创建一个。完成后，工具集将一次性启用并完成身份验证。

如果您希望分步操作（或者稍后重新进行身份验证），请使用下面的两步流程。

### 两步流程

#### 1. 启用工具集

```bash
hermes tools
```

切换 `🎵 Spotify` 为开启，保存，当内联向导打开时，关闭它（Ctrl+C）。工具集保持开启；只有身份验证步骤被推迟。

#### 2. 运行登录向导

```bash
hermes auth spotify
```

只有在步骤 1 之后，7 个 Spotify 工具才会出现在 Agent 的工具集中 —— 它们默认是关闭的，这样不需要这些工具的用户就不会在每个 API 调用中附带额外的工具模式。

如果没有设置 `HERMES_SPOTIFY_CLIENT_ID`，Hermes 会引导您在线完成应用注册：

1. 在浏览器中打开 `https://developer.spotify.com/dashboard`
2. 打印要粘贴到 Spotify “Create app” 表单中的确切值
3. 提示您输入返回的 Client ID
4. 将其保存到 `~/.hermes/.env`，以便后续运行跳过此步骤
5. 直接进入 OAuth 同意流程

在您批准后，Token 会被写入 `~/.hermes/auth.json` 中的 `providers.spotify` 下。活动的推理提供商**不会**改变 —— Spotify 身份验证独立于您的 LLM 提供商。

### 创建 Spotify 应用（向导会询问的内容）

当仪表板打开时，点击 **Create app** 并填写：

| 字段 | 值 |
|-------|-------|
| 应用名称 | 任意名称（例如 `hermes-agent`） |
| 应用描述 | 任意描述（例如 `personal Hermes integration`） |
| 网站 | 留空 |
| 重定向 URI | `http://127.0.0.1:43827/spotify/callback` |
| 使用哪些 API/SDK？ | 勾选 **Web API** |

同意条款并点击 **Save**。在下一页点击 **Settings** → 复制 **Client ID** 并粘贴到 Hermes 提示符中。这是 Hermes 需要的唯一值 —— PKCE 不使用客户端密钥。

### 通过 SSH / 在无头环境中运行

如果设置了 `SSH_CLIENT` 或 `SSH_TTY`，Hermes 会在向导和 OAuth 步骤期间跳过自动打开浏览器。复制 Hermes 打印的仪表板 URL 和授权 URL，在本地机器的浏览器中打开它们，然后正常进行 —— 本地 HTTP 监听器仍在远程主机的端口 `43827` 上运行。您的笔记本电脑浏览器无法在没有 SSH 本地转发的情况下访问远程环回地址：

```bash
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

关于跳板机/堡垒机设置和其他注意事项（mosh、tmux、端口冲突），请参阅 [OAuth over SSH / Remote Hosts](../../guides/oauth-over-ssh.md)。

## 验证

```bash
hermes auth status spotify
```

显示 Token 是否存在以及访问 Token 何时过期。刷新是自动的：当任何 Spotify API 调用返回 401 时，客户端会交换刷新 Token 并重试一次。刷新 Token 在 Hermes 重启后仍然有效，因此只有在您撤销 Spotify 账户设置中的应用或运行 `hermes auth logout spotify` 时才需要重新进行身份验证。

## 使用

登录后，Agent 就可以访问 7 个 Spotify 工具。您可以自然地与 Agent 对话 —— 它会选择正确的工具和操作。为了获得最佳行为，Agent 会加载一个配套技能，该技能教授规范的使用模式（单次搜索然后播放，何时不预先执行 `get_state` 等）。

```
> 播放一些 Miles Davis
> 我正在听什么
> 把这首曲目添加到我的“深夜爵士”播放列表
> 跳到下一首歌
> 创建一个名为“Focus 2026”的新播放列表，并添加我最近播放的三首歌
> 我保存的专辑中哪些是 Radiohead 的
> 搜索 Blackbird 的原声翻唱
> 将播放转移到我的厨房扬声器
```

### 工具参考

所有改变播放状态的操作都接受一个可选的 `device_id` 参数，以定位特定设备。如果省略，Spotify 会使用当前活跃的设备。

#### `spotify_playback`
控制和检查播放状态，以及获取最近播放的历史记录。

| 操作 | 目的 | 需要 Premium？ |
|--------|---------|----------|
| `get_state` | 完整的播放状态（曲目、设备、进度、随机/重复） | 否 |
| `get_currently_playing` | 仅当前曲目（如果返回 204 则为空 —— 见下文） | 否 |
| `play` | 开始/恢复播放。可选：`context_uri`、`uris`、`offset`、`position_ms` | 是 |
| `pause` | 暂停播放 | 是 |
| `next` / `previous` | 跳过曲目 | 是 |
| `seek` | 跳转到 `position_ms` | 是 |
| `set_repeat` | `state` = `track` / `context` / `off` | 是 |
| `set_shuffle` | `state` = `true` / `false` | 是 |
| `set_volume` | `volume_percent` = 0-100 | 是 |
| `recently_played` | 最近播放的曲目。可选 `limit`、`before`、`after`（Unix 毫秒） | 否 |
#### `spotify_devices`
| 操作 | 用途 |
|--------|---------|
| `list` | 列出您账户可见的所有 Spotify Connect 设备 |
| `transfer` | 将播放转移到 `device_id`。可选的 `play: true` 参数会在转移后开始播放 |

### Home Assistant 管理的扬声器

如果 Home Assistant 管理着已经支持 Spotify Connect 的扬声器（例如 Sonos、Echo、Nest 或其他支持 Connect 的扬声器），那么只要 Spotify 能检测到它们，它们就会自动出现在 `spotify_devices list` 中。Hermes 不需要为此路径配置 Home Assistant ↔ Spotify 桥接——Spotify 会原生处理设备路由。

可以要求 Hermes 通过扬声器的显示名称来转移播放（例如，“将 Spotify 转移到厨房扬声器”），或者在编写脚本时，调用 `spotify_devices list` 并将确切的 `device_id` 传递给 `spotify_devices transfer`。如果扬声器缺失，请打开 Spotify 应用或扬声器的 Spotify 集成一次，以便 Spotify 将其注册为活跃的 Connect 目标。

#### `spotify_queue`
| 操作 | 用途 | 需要 Premium？ |
|--------|---------|----------|
| `get` | 获取当前队列中的曲目 | 否 |
| `add` | 将 `uri` 添加到队列末尾 | 是 |

#### `spotify_search`
搜索目录。`query` 是必需的。可选参数：`types`（`track` / `album` / `artist` / `playlist` / `show` / `episode` 的数组）、`limit`、`offset`、`market`。

#### `spotify_playlists`
| 操作 | 用途 | 必需参数 |
|--------|---------|---------------|
| `list` | 用户的播放列表 | — |
| `get` | 单个播放列表及其曲目 | `playlist_id` |
| `create` | 新建播放列表 | `name`（+ 可选的 `description`、`public`、`collaborative`） |
| `add_items` | 添加曲目 | `playlist_id`、`uris`（可选的 `position`） |
| `remove_items` | 移除曲目 | `playlist_id`、`uris`（+ 可选的 `snapshot_id`） |
| `update_details` | 重命名/编辑 | `playlist_id` + `name`、`description`、`public`、`collaborative` 中的任意组合 |

#### `spotify_albums`
| 操作 | 用途 | 必需参数 |
|--------|---------|---------------|
| `get` | 专辑元数据 | `album_id` |
| `tracks` | 专辑曲目列表 | `album_id` |

#### `spotify_library`
统一访问已保存的曲目和专辑。使用 `kind` 参数选择集合。

| 操作 | 用途 |
|--------|---------|
| `list` | 分页的媒体库列表 |
| `save` | 将 `ids` / `uris` 添加到媒体库 |
| `remove` | 将 `ids` / `uris` 从媒体库中移除 |

必需参数：`kind` = `tracks` 或 `albums`，以及 `action`。

### 功能矩阵：免费版 vs Premium 版

只读工具适用于免费账户。任何会改变播放或队列的操作都需要 Premium。

| 适用于免费版 | 需要 Premium 版 |
|---------------|------------------|
| `spotify_search` (全部) | `spotify_playback` — play, pause, next, previous, seek, set_repeat, set_shuffle, set_volume |
| `spotify_playback` — get_state, get_currently_playing, recently_played | `spotify_queue` — add |
| `spotify_devices` — list | `spotify_devices` — transfer |
| `spotify_queue` — get | |
| `spotify_playlists` (全部) | |
| `spotify_albums` (全部) | |
| `spotify_library` (全部) | |

## 定时任务：Spotify + cron

因为 Spotify 工具是常规的 Hermes 工具，所以在 Hermes 会话中运行的 cron 任务可以按任何时间表触发播放。无需编写新代码。

### 早晨唤醒播放列表

```bash
hermes cron add \
  --name "morning-commute" \
  "0 7 * * 1-5" \
  "Transfer playback to my kitchen speaker and start my 'Morning Commute' playlist. Volume to 40. Shuffle on."
```

每个工作日上午 7 点会发生什么：
1. Cron 启动一个无头 Hermes 会话。
2. Agent 读取提示词，调用 `spotify_devices list` 按名称查找“kitchen speaker”，然后依次调用 `spotify_devices transfer` → `spotify_playback set_volume` → `spotify_playback set_shuffle` → `spotify_search` + `spotify_playback play`。
3. 音乐在目标扬声器上开始播放。总成本：一个会话，几次工具调用，无需人工输入。

### 夜间放松

```bash
hermes cron add \
  --name "wind-down" \
  "30 22 * * *" \
  "Pause Spotify. Then set volume to 20 so it's quiet when I start it again tomorrow."
```

### 注意事项

- **cron 触发时必须存在活跃设备。** 如果没有 Spotify 客户端在运行（手机/桌面/Connect 扬声器），播放操作将返回 `403 no active device`。对于早晨播放列表，技巧是定位一个始终在线的设备（Sonos、Echo、智能扬声器），而不是您的手机。
- **任何改变播放的操作都需要 Premium** —— play, pause, skip, volume, transfer。只读的 cron 任务（例如定时“通过邮件发送我最近播放的曲目”）在免费账户上可以正常工作。
- **cron agent 会继承您活跃的工具集。** 必须在 `hermes tools` 中启用 Spotify，cron 会话才能看到 Spotify 工具。
- **Cron 任务以 `skip_memory=True` 运行**，因此它们不会写入您的记忆存储。

完整的 cron 参考：[Cron Jobs](./cron)。

## 退出登录

```bash
hermes auth logout spotify
```

从 `~/.hermes/auth.json` 中移除 Token。要同时清除应用配置，请从 `~/.hermes/.env` 中删除 `HERMES_SPOTIFY_CLIENT_ID`（以及如果您设置了的话，`HERMES_SPOTIFY_REDIRECT_URI`），或者重新运行向导。

要在 Spotify 端撤销应用，请访问 [Apps connected to your account](https://www.spotify.com/account/apps/) 并点击 **REMOVE ACCESS**。

## 故障排除

**`403 Forbidden — Player command failed: No active device found`** —— 您至少需要在一个设备上运行 Spotify。在您的手机、桌面或网页播放器上打开 Spotify 应用，播放任意曲目几秒钟以注册设备，然后重试。`spotify_devices list` 会显示当前可见的设备。

**`403 Forbidden — Premium required`** —— 您使用的是免费账户，但尝试执行改变播放的操作。请参阅上面的功能矩阵。

**`get_currently_playing` 返回 `204 No Content`** —— 当前没有任何设备在播放。这是 Spotify 的正常响应，不是错误；Hermes 会将其显示为解释性的空结果（`is_playing: false`）。

**`INVALID_CLIENT: Invalid redirect URI`** —— 您在 Spotify 应用设置中的重定向 URI 与 Hermes 使用的不匹配。默认是 `http://127.0.0.1:43827/spotify/callback`。请将此 URI 添加到您应用的允许重定向 URI 列表中，或者在 `~/.hermes/.env` 中将 `HERMES_SPOTIFY_REDIRECT_URI` 设置为您注册的 URI。
**`429 Too Many Requests`** — Spotify 的速率限制。Hermes 会返回友好的错误信息；等待一分钟然后重试。如果问题持续出现，你可能在脚本中运行了紧密循环 — Spotify 的配额大约每 30 秒重置一次。

**`401 Unauthorized` 反复出现** — 你的刷新令牌已被撤销（通常是因为你从账户中移除了应用，或者应用被删除）。重新运行 `hermes auth spotify`。

**Wizard 没有打开浏览器** — 如果你通过 SSH 连接或在没有显示器的容器中，Hermes 会检测到并跳过自动打开。复制它打印的仪表板 URL 并手动打开。

## 高级：自定义权限范围

默认情况下，Hermes 会请求所有已提供工具所需的权限范围。如果你想限制访问，可以覆盖此设置：

```bash
hermes auth spotify --scope "user-read-playback-state user-modify-playback-state playlist-read-private"
```

权限范围参考：[Spotify Web API 权限范围](https://developer.spotify.com/documentation/web-api/concepts/scopes)。如果你请求的权限范围少于某个工具所需，该工具的调用将失败并返回 403。

## 高级：自定义客户端 ID / 重定向 URI

```bash
hermes auth spotify --client-id <id> --redirect-uri http://localhost:3000/callback
```

或者将它们永久设置在 `~/.hermes/.env` 中：

```
HERMES_SPOTIFY_CLIENT_ID=<your_id>
HERMES_SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

重定向 URI 必须在你的 Spotify 应用设置中被允许。默认设置对几乎所有人都有效 — 仅在端口 43827 被占用时才需要更改。

## 文件位置

| 文件 | 内容 |
|------|----------|
| `~/.hermes/auth.json` → `providers.spotify` | 访问令牌、刷新令牌、过期时间、权限范围、重定向 URI |
| `~/.hermes/.env` | `HERMES_SPOTIFY_CLIENT_ID`，可选的 `HERMES_SPOTIFY_REDIRECT_URI` |
| Spotify 应用 | 由你在 [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) 拥有；包含客户端 ID 和重定向 URI 允许列表 |