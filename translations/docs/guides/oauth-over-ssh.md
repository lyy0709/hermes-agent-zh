---
sidebar_position: 17
title: "通过 SSH / 远程主机进行 OAuth"
description: "当 Hermes 运行在远程机器、容器或跳板机后面时，如何完成基于浏览器的 OAuth（xAI、Spotify、MCP 服务器）"
---

# 通过 SSH / 远程主机进行 OAuth

一些 Hermes 提供商——**xAI Grok OAuth**、**Spotify** 和**远程 MCP 服务器**（Linear、Sentry、Atlassian、Asana、Figma 等）——使用*环回重定向* OAuth 流程。授权服务器将你的浏览器重定向到 `http://127.0.0.1:<端口>/callback`，以便 Hermes 启动的一个小型 HTTP 监听器可以获取授权码。

当 Hermes 和你的浏览器在同一台机器上时，这工作得很好。一旦它们不在同一台机器上，就会出问题：你笔记本电脑的浏览器试图访问**你笔记本电脑**上的 `127.0.0.1`，但监听器绑定在**远程服务器**上的 `127.0.0.1`。

解决方法是使用一行 SSH 本地端口转发——**或者**，当你没有真正的 SSH 客户端时（例如 GCP Cloud Shell、GitHub Codespaces、EC2 Instance Connect、Gitpod、基于浏览器的 Web IDE），可以使用 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923) 中引入的新 `--manual-paste` 标志。

## 摘要

```bash
# 在你的本地机器（笔记本电脑）上，打开一个单独的终端：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 在远程机器上你现有的 SSH 会话中：
hermes auth add xai-oauth --no-browser
# → Hermes 打印一个授权 URL。在你的笔记本电脑浏览器中打开它。
# → 你的浏览器重定向到 127.0.0.1:56121/callback，隧道将请求转发到远程监听器，登录完成。
```

端口 `56121` 是 xAI OAuth 使用的端口。对于 Spotify，将其替换为 `43827`。Hermes 会在 `Waiting for callback on ...` 这一行打印它绑定的确切端口——从那里复制它。

## 仅限浏览器的远程环境（Cloud Shell / Codespaces / EC2 Instance Connect）

如果你没有常规的 SSH 客户端——例如，因为你在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台内运行 Hermes——那么上述 SSH 隧道不可用。请改用 `--manual-paste`：

```bash
hermes auth add xai-oauth --manual-paste
# → Hermes 打印一个授权 URL。在你的笔记本电脑浏览器中打开它。
# → 在浏览器中批准。重定向到 127.0.0.1:56121/callback 的页面加载失败——这是预期的。
# → 从失败页面的地址栏复制完整的 URL。
# → 在终端中 "Callback URL:" 提示符处将其粘贴回去。
```

同样的标志也适用于 `hermes model --manual-paste` 用于集成模型选择器。Hermes 可以互换地接受三种回调粘贴形式：完整 URL、裸的 `?code=...&state=...` 查询片段，或者——当上游同意页面在页面内呈现授权码而不是重定向时（xAI 当前在基于浏览器的控制台上的行为）——单独的裸授权码值。

Hermes 对两种路径使用**相同的 PKCE 验证器、状态和随机数**，因此上游 OAuth 流程在字节级别是相同的——`--manual-paste` 纯粹是回调跳转的传输方式改变，并非安全性降级。

## 哪些提供商需要此操作

| 提供商 | 环回端口 | 需要隧道？ |
|----------|---------------|----------------|
| `xai-oauth` (Grok SuperGrok) | `56121` | 是，当 Hermes 在远程时 |
| Spotify | `43827` | 是，当 Hermes 在远程时 |
| MCP 服务器 (`auth: oauth`) | 每个服务器自动选择 | 是，当 Hermes 在远程时 |
| `anthropic` (Claude Pro/Max) | 不适用 | 否——粘贴代码流程 |
| `openai-codex` (ChatGPT Plus/Pro) | 不适用 | 否——设备代码流程 |
| `minimax`, `nous-portal` | 不适用 | 否——设备代码流程 |

如果你的提供商不在表中，则不需要隧道。

## MCP 服务器

远程 MCP 服务器（Linear、Sentry、Atlassian、Asana、Figma 等）使用相同的环回重定向流程。Hermes 为每个服务器自动选择一个空闲端口，并在 OAuth 流程启动时打印授权 URL——要么在启动时（当 `mcp_servers:` 中出现新服务器时），要么在你运行 `hermes mcp login <server>` 时。

你有两种方法从远程主机完成它：

**选项 1 —— 粘贴重定向 URL 回来（无需设置，随处可用）。** 在交互式终端上，Hermes 会提示你粘贴重定向 URL，同时运行本地监听器。在浏览器中批准后，重定向到 `http://127.0.0.1:<端口>/callback` 将显示连接错误——这是预期的。从**浏览器的地址栏复制完整的 URL** 并将其粘贴到 Hermes 提示符处：

```
  MCP OAuth: authorization required.
  Open this URL in your browser:

    https://mcp.linear.app/authorize?response_type=code&...

  Or paste the redirect URL here (or the ?code=...&state=... portion) and press Enter:
> https://mcp.linear.app/callback?code=abc123&state=xyz
  Got authorization code from paste — completing flow.
```

裸的 `?code=...&state=...` 查询字符串也被接受。这适用于任何带有 `auth: oauth` 的 MCP 服务器，并且不需要更改 SSH 配置。

**选项 2 —— SSH 端口转发（与 xAI / Spotify 相同）。** Hermes 在 SSH 会话提示中打印它绑定的确切端口。在你的笔记本电脑上打开一个单独的终端：

```bash
ssh -N -L <端口>:127.0.0.1:<端口> user@remote-host
```

然后像往常一样在浏览器中打开授权 URL；重定向通过隧道传输，监听器会接收到它。当你需要流程在无人值守的情况下完成时使用此方法（例如，无法交互式粘贴的脚本化重新认证）。

**陷阱 —— 30 秒配置重新加载竞争。** 如果你从正在运行的 Hermes 会话内部编辑 `~/.hermes/config.yaml` 以添加 OAuth MCP 服务器，CLI 会在 30 秒超时后自动重新加载 MCP 连接。这没有足够的时间来完成交互式 OAuth 流程，重新加载将会放弃。请改用新终端中的 `hermes mcp login <server>`——它没有这样的限制，并会等待完整的 5 分钟让你粘贴回来。

## 为什么监听器不能直接绑定 0.0.0.0

xAI 和 Spotify 都根据允许列表验证 `redirect_uri` 参数。两者都需要环回形式 (`http://127.0.0.1:<确切端口>/callback`)。将监听器绑定到 `0.0.0.0` 或不同的端口将导致授权服务器因 redirect_uri 不匹配而拒绝请求。SSH 隧道保持环回 URI 端到端完整。

## 逐步指南：单次 SSH 跳转

### 1. 从你的本地机器启动隧道

```bash
# xAI Grok OAuth (端口 56121)
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 或者对于 Spotify (端口 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 表示“不打开远程 shell，只保持隧道打开。”在整个登录期间保持此终端运行。

### 2. 在单独的 SSH 会话中，运行认证命令

```bash
ssh user@remote-host
hermes auth add xai-oauth --no-browser
# 或者对于 Spotify：
# hermes auth add spotify --no-browser
```

Hermes 检测到 SSH 会话，跳过浏览器自动打开，并打印授权 URL 以及一行 `Waiting for callback on http://127.0.0.1:<端口>/callback`。

### 3. 在你的本地浏览器中打开 URL

从远程终端复制授权 URL 并粘贴到你笔记本电脑的浏览器中。批准同意屏幕。授权服务器重定向到 `http://127.0.0.1:<端口>/callback`。你的浏览器访问隧道，请求被转发到远程监听器，Hermes 打印 `Login successful!`。

一旦你看到成功行，就可以拆除隧道（在第一个终端中按 Ctrl+C）。

## 逐步指南：通过跳板机

如果你通过堡垒机 / 跳板主机访问 Hermes，请使用 SSH 内置的 `-J` (ProxyJump)：

```bash
ssh -N -L 56121:127.0.0.1:56121 -J jump-user@jump-host user@final-host
```

这通过跳板主机链式连接 SSH 连接，而不会将环回端口放在跳板机本身上。你笔记本电脑上的本地 `127.0.0.1:56121` 直接隧道传输到最终远程主机上的 `127.0.0.1:56121`。

对于不支持 `-J` 的旧版 OpenSSH，长格式是：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 56121:127.0.0.1:56121 \
    user@final-host
```

## Mosh、tmux、ssh ControlMaster

隧道是底层 SSH 连接的一个属性。如果你在 mosh 会话中通过 `tmux` 运行 Hermes，mosh 漫游不会携带 `-L` 转发。为 `-L` 隧道打开一个*单独的*普通 SSH 会话——这是必须在认证流程期间保持存活的连接。你的交互式 mosh/tmux 会话可以继续正常运行 Hermes。

如果你使用 `ssh -o ControlMaster=auto`，多路复用连接上的端口转发共享主连接的生存期。如果隧道没有建立，请重启主连接：

```bash
ssh -O exit user@remote-host
ssh -N -L 56121:127.0.0.1:56121 user@remote-host
```

## 故障排除

### `bind [127.0.0.1]:56121: Address already in use`

你笔记本电脑上的某个程序已经使用了该端口。要么是之前的隧道没有干净地关闭，要么是本地 Hermes 也在监听它。找到并终止占用者：

```bash
# macOS / Linux
lsof -iTCP:56121 -sTCP:LISTEN
kill <PID>
```

然后重试 `ssh -L` 命令。

### "Could not establish connection. We couldn't reach your app." (xAI)

当 xAI 的重定向到 `127.0.0.1:<端口>/callback` 无法到达监听器时，xAI 的授权页面会显示此信息。要么隧道没有运行，端口错误，要么你使用了 Hermes 在之前运行中打印的端口（如果首选端口繁忙，端口可能会自动调整——始终读取最新的 `Waiting for callback on ...` 行）。

### `xAI authorization timed out waiting for the local callback`

与上述相同根本原因——重定向从未返回。检查隧道是否仍然存活（`ssh -N` 不显示输出，所以查看你启动它的终端），如果需要则重启它，并重新运行 `hermes auth add xai-oauth --no-browser`。

### Token 存储到错误的 `~/.hermes`

Token 写入运行 `hermes auth add ...` 的 Linux 用户下。如果你的消息网关 / systemd 服务以不同用户身份运行（例如 `root` 或专用的 `hermes` 用户），请以**该**用户身份进行认证，以便 Token 存储到他们的 `~/.hermes/auth.json` 中。使用 `sudo -u hermes -i` 或等效命令。

## 另请参阅

- [xAI Grok OAuth](./xai-grok-oauth.md)
- [Spotify (`Running over SSH`)](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [原生 MCP 客户端 (OAuth 部分)](../user-guide/features/mcp.md#oauth-authenticated-http-servers)
- [SSH `-J` / ProxyJump (man 手册页)](https://man.openbsd.org/ssh#J)