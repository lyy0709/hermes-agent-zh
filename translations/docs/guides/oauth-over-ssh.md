---
sidebar_position: 17
title: "通过 SSH / 远程主机进行 OAuth 认证"
description: "当 Hermes 运行在远程机器、容器或跳板机后时，如何完成基于浏览器的 OAuth 认证（xAI、Spotify）"
---

# 通过 SSH / 远程主机进行 OAuth 认证

一些 Hermes 提供商——目前是 **xAI Grok OAuth** 和 **Spotify**——使用*环回重定向* OAuth 流程。认证服务器（xAI、Spotify）会将你的浏览器重定向到 `http://127.0.0.1:<端口>/callback`，以便 `hermes auth ...` 命令启动的一个小型 HTTP 监听器可以获取授权码。

当 Hermes 和你的浏览器在同一台机器上时，这工作得很好。一旦它们不在同一台机器上，流程就会中断：你笔记本电脑的浏览器试图访问**你笔记本电脑**上的 `127.0.0.1`，但监听器绑定在**远程服务器**的 `127.0.0.1` 上。

解决方法是使用一行 SSH 本地端口转发——**或者**，当你没有真正的 SSH 客户端时（例如在 GCP Cloud Shell、GitHub Codespaces、EC2 Instance Connect、Gitpod、基于浏览器的 Web IDE 中），可以使用 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923) 中引入的新标志 `--manual-paste`。

## 快速指南

```bash
# 在你的本地机器（笔记本电脑）上，打开一个单独的终端：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 在远程机器上你现有的 SSH 会话中：
hermes auth add xai-oauth --no-browser
# → Hermes 会打印一个授权 URL。在你的笔记本电脑浏览器中打开它。
# → 你的浏览器重定向到 127.0.0.1:56121/callback，隧道将请求转发到远程监听器，登录完成。
```

端口 `56121` 是 xAI OAuth 使用的。对于 Spotify，请将其替换为 `43827`。Hermes 会在 `Waiting for callback on ...` 这一行打印它绑定的确切端口——从那里复制端口号。

## 仅限浏览器的远程环境（Cloud Shell / Codespaces / EC2 Instance Connect）

如果你没有常规的 SSH 客户端——例如，因为你在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台中运行 Hermes——那么上述 SSH 隧道不可用。请改用 `--manual-paste`：

```bash
hermes auth add xai-oauth --manual-paste
# → Hermes 会打印一个授权 URL。在你的笔记本电脑浏览器中打开它。
# → 在浏览器中批准授权。重定向到 127.0.0.1:56121/callback 的页面会加载失败——这是预期的。
# → 从失败页面的地址栏复制完整的 URL。
# → 在终端提示 "Callback URL:" 时将其粘贴回去。
```

同样的标志也适用于 `hermes model --manual-paste` 用于集成的模型选择器。如果你不想粘贴整个 URL，也可以接受仅包含 `?code=...&state=...` 查询片段的 URL。

Hermes 对两种路径使用**相同的 PKCE 验证器、状态和随机数**，因此上游 OAuth 流程在字节级别是相同的——`--manual-paste` 纯粹是回调跳转的传输方式改变，并非安全性降级。

## 哪些提供商需要此操作

| 提供商 | 环回端口 | 需要隧道？ |
|----------|---------------|----------------|
| `xai-oauth` (Grok SuperGrok) | `56121` | 是，当 Hermes 在远程时 |
| Spotify | `43827` | 是，当 Hermes 在远程时 |
| `anthropic` (Claude Pro/Max) | 不适用 | 否——使用粘贴代码流程 |
| `openai-codex` (ChatGPT Plus/Pro) | 不适用 | 否——使用设备代码流程 |
| `minimax`, `nous-portal` | 不适用 | 否——使用设备代码流程 |

如果你的提供商不在表中，则不需要隧道。

## 为什么监听器不能直接绑定到 0.0.0.0

xAI 和 Spotify 都会根据允许列表验证 `redirect_uri` 参数。两者都要求环回形式（`http://127.0.0.1:<精确端口>/callback`）。将监听器绑定到 `0.0.0.0` 或不同的端口会导致认证服务器因 redirect_uri 不匹配而拒绝请求。SSH 隧道保持了环回 URI 的端到端完整性。

## 逐步指南：单次 SSH 跳转

### 1. 从你的本地机器启动隧道

```bash
# xAI Grok OAuth (端口 56121)
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 或者对于 Spotify (端口 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 表示“不打开远程 shell，只保持隧道打开”。在登录期间保持此终端运行。

### 2. 在另一个 SSH 会话中，运行认证命令

```bash
ssh user@remote-host
hermes auth add xai-oauth --no-browser
# 或者对于 Spotify：
# hermes auth add spotify --no-browser
```

Hermes 检测到 SSH 会话，跳过浏览器自动打开，并打印授权 URL 以及一行 `Waiting for callback on http://127.0.0.1:<端口>/callback`。

### 3. 在你的本地浏览器中打开 URL

从远程终端复制授权 URL 并粘贴到你笔记本电脑的浏览器中。批准同意屏幕。认证服务器重定向到 `http://127.0.0.1:<端口>/callback`。你的浏览器通过隧道，请求被转发到远程监听器，然后 Hermes 打印 `Login successful!`。

一旦你看到成功行，就可以拆除隧道（在第一个终端中按 Ctrl+C）。

## 逐步指南：通过跳板机

如果你通过堡垒机 / 跳板主机访问 Hermes，请使用 SSH 内置的 `-J` (ProxyJump)：

```bash
ssh -N -L 56121:127.0.0.1:56121 -J jump-user@jump-host user@final-host
```

这通过跳板主机链式建立 SSH 连接，而无需将环回端口放在跳板机本身上。你笔记本电脑上的本地 `127.0.0.1:56121` 直接隧道连接到最终远程主机上的 `127.0.0.1:56121`。

对于不支持 `-J` 的旧版 OpenSSH，长格式为：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 56121:127.0.0.1:56121 \
    user@final-host
```

## Mosh, tmux, ssh ControlMaster

隧道是底层 SSH 连接的一个属性。如果你在 mosh 会话中通过 `tmux` 运行 Hermes，mosh 的漫游不会携带 `-L` 转发。为 `-L` 隧道打开一个*单独的*普通 SSH 会话——这是必须在认证流程期间保持存活的连接。你的交互式 mosh/tmux 会话可以继续正常运行 Hermes。

如果你使用 `ssh -o ControlMaster=auto`，多路复用连接上的端口转发共享主连接的生存期。如果隧道没有建立，请重启主连接：

```bash
ssh -O exit user@remote-host
ssh -N -L 56121:127.0.0.1:56121 user@remote-host
```

## 故障排除

### `bind [127.0.0.1]:56121: Address already in use`

你笔记本电脑上的某个程序已经使用了该端口。可能是之前的隧道没有干净地关闭，或者本地 Hermes 也在监听该端口。找到并终止占用者：

```bash
# macOS / Linux
lsof -iTCP:56121 -sTCP:LISTEN
kill <PID>
```

然后重试 `ssh -L` 命令。

### "Could not establish connection. We couldn't reach your app." (xAI)

当 xAI 的重定向到 `127.0.0.1:<端口>/callback` 无法到达监听器时，xAI 的授权页面会显示此信息。可能是隧道没有运行、端口错误，或者你使用了 Hermes 在之前运行中打印的端口（如果首选端口繁忙，端口可能会自动调整——请始终读取最新的 `Waiting for callback on ...` 行）。

### `xAI authorization timed out waiting for the local callback`

与上述相同的根本原因——重定向从未返回。检查隧道是否仍然存活（`ssh -N` 不显示输出，所以查看你启动它的终端），如果需要则重启它，并重新运行 `hermes auth add xai-oauth --no-browser`。

### Token 写入错误的 `~/.hermes`

Token 写入运行 `hermes auth add ...` 的 Linux 用户目录下。如果你的消息网关 / systemd 服务以不同的用户身份运行（例如 `root` 或专用的 `hermes` 用户），请以**该**用户身份进行认证，以便 Token 写入他们的 `~/.hermes/auth.json`。使用 `sudo -u hermes -i` 或等效命令。

## 另请参阅

- [xAI Grok OAuth](./xai-grok-oauth.md)
- [Spotify (`在 SSH 上运行`)](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [SSH `-J` / ProxyJump (man 页面)](https://man.openbsd.org/ssh#J)