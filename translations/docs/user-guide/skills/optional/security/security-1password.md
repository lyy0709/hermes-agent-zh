---
title: "1Password — 设置和使用 1Password CLI (op)"
sidebar_label: "1Password"
description: "设置和使用 1Password CLI (op)"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

# 1Password

设置和使用 1Password CLI (op)。在安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/1password` 安装 |
| 路径 | `optional-skills/security/1password` |
| 版本 | `1.0.0` |
| 作者 | arceus77-7，由 Hermes Agent 增强 |
| 许可证 | MIT |
| 标签 | `security`, `secrets`, `1password`, `op`, `cli` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 1Password CLI

当用户希望通过 1Password 管理密钥，而不是使用明文环境变量或文件时，使用此技能。

## 要求

- 1Password 账户
- 已安装 1Password CLI (`op`)
- 以下之一：桌面应用集成、服务账户令牌 (`OP_SERVICE_ACCOUNT_TOKEN`) 或 Connect 服务器
- 在 Hermes 终端调用期间，`tmux` 可用于稳定的认证会话（仅限桌面应用流程）

## 使用时机

- 安装或配置 1Password CLI
- 使用 `op signin` 登录
- 读取密钥引用，如 `op://Vault/Item/field`
- 使用 `op inject` 将密钥注入配置/模板
- 通过 `op run` 运行带有密钥环境变量的命令

## 认证方法

### 服务账户（推荐用于 Hermes）

在 `~/.hermes/.env` 中设置 `OP_SERVICE_ACCOUNT_TOKEN`（技能首次加载时会提示输入此项）。
无需桌面应用。支持 `op read`、`op inject`、`op run`。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
op whoami  # 验证 — 应显示 Type: SERVICE_ACCOUNT
```

### 桌面应用集成（交互式）

1. 在 1Password 桌面应用中启用：设置 → 开发者 → 与 1Password CLI 集成
2. 确保应用已解锁
3. 运行 `op signin` 并批准生物识别提示

### Connect 服务器（自托管）

```bash
export OP_CONNECT_HOST="http://localhost:8080"
export OP_CONNECT_TOKEN="your-connect-token"
```

## 设置

1. 安装 CLI：

```bash
# macOS
brew install 1password-cli

# Linux (官方包/安装文档)
# 查看 references/get-started.md 获取特定发行版的链接。

# Windows (winget)
winget install AgileBits.1Password.CLI
```

2. 验证：

```bash
op --version
```

3. 选择上述一种认证方法并进行配置。

## Hermes 执行模式（桌面应用流程）

Hermes 终端命令默认是非交互式的，并且可能在调用之间丢失认证上下文。
为了在使用桌面应用集成时可靠地使用 `op`，请在专用的 tmux 会话中运行登录和密钥操作。

注意：使用 `OP_SERVICE_ACCOUNT_TOKEN` 时**不需要**这样做 — 令牌会自动在终端调用之间持久化。

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# 登录（提示时在桌面应用中批准）
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# 验证认证
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# 示例读取
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# 需要时捕获输出
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# 清理
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## 常见操作

### 读取密钥

```bash
op read "op://app-prod/db/password"
```

### 获取 OTP

```bash
op read "op://app-prod/npm/one-time password?attribute=otp"
```

### 注入到模板

```bash
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

### 使用密钥环境变量运行命令

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

## 防护措施

- 除非用户明确请求值，否则切勿将原始密钥打印回给用户。
- 优先使用 `op run` / `op inject`，而不是将密钥写入文件。
- 如果命令因“account is not signed in”而失败，请在同一个 tmux 会话中再次运行 `op signin`。
- 如果桌面应用集成不可用（无头/CI 环境），请使用服务账户令牌流程。

## CI / 无头环境说明

对于非交互式使用，请使用 `OP_SERVICE_ACCOUNT_TOKEN` 进行认证，并避免交互式的 `op signin`。
服务账户需要 CLI v2.18.0+。

## 参考

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/