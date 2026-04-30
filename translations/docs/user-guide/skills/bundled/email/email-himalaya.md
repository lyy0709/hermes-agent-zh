---
title: "Himalaya — Himalaya CLI：在终端中使用 IMAP/SMTP 处理邮件"
sidebar_label: "Himalaya"
description: "Himalaya CLI：在终端中使用 IMAP/SMTP 处理邮件"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Himalaya

Himalaya CLI：在终端中使用 IMAP/SMTP 处理邮件。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/email/himalaya` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 标签 | `Email`, `IMAP`, `SMTP`, `CLI`, `Communication` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Himalaya 邮件 CLI

Himalaya 是一个 CLI 邮件客户端，允许你使用 IMAP、SMTP、Notmuch 或 Sendmail 后端在终端中管理邮件。

## 参考资料

- `references/configuration.md`（配置文件设置 + IMAP/SMTP 认证）
- `references/message-composition.md`（用于撰写邮件的 MML 语法）

## 先决条件

1.  已安装 Himalaya CLI（运行 `himalaya --version` 验证）
2.  在 `~/.config/himalaya/config.toml` 处存在配置文件
3.  已配置 IMAP/SMTP 凭据（密码安全存储）

### 安装

```bash
# 预编译二进制文件（Linux/macOS — 推荐）
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# macOS 通过 Homebrew
brew install himalaya

# 或通过 cargo（任何支持 Rust 的平台）
cargo install himalaya --locked
```

## 配置设置

运行交互式向导来设置账户：

```bash
himalaya account configure
```

或者手动创建 `~/.config/himalaya/config.toml`：

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"  # 或使用密钥环

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"
```

## Hermes 集成说明

-   **读取、列出、搜索、移动、删除** 邮件都可以直接通过终端工具完成
-   **撰写/回复/转发** — 建议使用管道输入（`cat << EOF | himalaya template send`）以获得更好的可靠性。交互式 `$EDITOR` 模式可以与 `pty=true` + 后台 + 进程工具配合使用，但需要了解编辑器及其命令
-   使用 `--output json` 获取结构化输出，便于程序解析
-   `himalaya account configure` 向导需要交互式输入 — 使用 PTY 模式：`terminal(command="himalaya account configure", pty=true)`

## 常见操作

### 列出文件夹

```bash
himalaya folder list
```

### 列出邮件

列出 INBOX 中的邮件（默认）：

```bash
himalaya envelope list
```

列出特定文件夹中的邮件：

```bash
himalaya envelope list --folder "Sent"
```

带分页列出：

```bash
himalaya envelope list --page 1 --page-size 20
```

### 搜索邮件

```bash
himalaya envelope list from john@example.com subject meeting
```

### 读取邮件

按 ID 读取邮件（显示纯文本）：

```bash
himalaya message read 42
```

导出原始 MIME：

```bash
himalaya message export 42 --full
```

### 回复邮件

要从 Hermes 非交互式回复，请读取原始消息，撰写回复，并通过管道发送：

```bash
# 获取回复模板，编辑并发送
himalaya template reply 42 | sed 's/^$/\nYour reply text here\n/' | himalaya template send
```

或者手动构建回复：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: Original Subject
In-Reply-To: <original-message-id>

Your reply here.
EOF
```

回复所有人（交互式 — 需要 $EDITOR，建议使用上述模板方法）：

```bash
himalaya message reply 42 --all
```

### 转发邮件

```bash
# 获取转发模板并通过管道修改后发送
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

### 撰写新邮件

**非交互式（从 Hermes 使用此方法）** — 通过 stdin 管道传递消息：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF
```

或者使用 headers 标志：

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "Message body here"
```

注意：不带管道输入的 `himalaya message write` 会打开 `$EDITOR`。这可以与 `pty=true` + 后台模式配合使用，但使用管道更简单、更可靠。

### 移动/复制邮件

移动到文件夹：

```bash
himalaya message move 42 "Archive"
```

复制到文件夹：

```bash
himalaya message copy 42 "Important"
```

### 删除邮件

```bash
himalaya message delete 42
```

### 管理标志

添加标志：

```bash
himalaya flag add 42 --flag seen
```

移除标志：

```bash
himalaya flag remove 42 --flag seen
```

## 多账户

列出账户：

```bash
himalaya account list
```

使用特定账户：

```bash
himalaya --account work envelope list
```

## 附件

从消息中保存附件：

```bash
himalaya attachment download 42
```

保存到特定目录：

```bash
himalaya attachment download 42 --dir ~/Downloads
```

## 输出格式

大多数命令支持 `--output` 以获取结构化输出：

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

## 调试

启用调试日志：

```bash
RUST_LOG=debug himalaya envelope list
```

完整跟踪（含回溯）：

```bash
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## 提示

-   使用 `himalaya --help` 或 `himalaya <command> --help` 获取详细用法。
-   邮件 ID 相对于当前文件夹；更改文件夹后请重新列出。
-   要撰写带附件的富文本邮件，请使用 MML 语法（参见 `references/message-composition.md`）。
-   使用 `pass`、系统密钥环或输出密码的命令安全地存储密码。