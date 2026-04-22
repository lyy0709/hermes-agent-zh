---
sidebar_position: 2
sidebar_label: "Google Workspace"
title: "Google Workspace — Gmail、日历、云端硬盘、表格和文档"
description: "发送电子邮件、管理日历事件、搜索云端硬盘、读写表格以及访问文档 — 全部通过 OAuth2 认证的 Google API 实现"
---

# Google Workspace 技能

为 Hermes 提供 Gmail、日历、云端硬盘、联系人、表格和文档的集成。使用 OAuth2 并支持自动 Token 刷新。优先使用 [Google Workspace CLI (`gws`)](https://github.com/nicholasgasior/gws) 以获得更广泛的功能覆盖，否则回退到 Google 的 Python 客户端库。

**技能路径：** `skills/productivity/google-workspace/`

## 设置

设置过程完全由 Agent 驱动 — 只需让 Hermes 设置 Google Workspace，它会引导您完成每个步骤。流程如下：

1.  **创建 Google Cloud 项目**并启用所需的 API（Gmail、日历、云端硬盘、表格、文档、联系人）
2.  **创建 OAuth 2.0 凭据**（桌面应用类型）并下载客户端密钥 JSON 文件
3.  **授权** — Hermes 生成授权 URL，您在浏览器中批准，然后粘贴回重定向 URL
4.  **完成** — 从此时起 Token 会自动刷新

:::tip 仅需电子邮件的用户
如果您只需要电子邮件功能（不需要日历/云端硬盘/表格），请改用 **himalaya** 技能 — 它使用 Gmail 应用密码，只需 2 分钟即可完成。无需 Google Cloud 项目。
:::

## Gmail

### 搜索

```bash
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"
```

返回包含每条消息的 `id`、`from`、`subject`、`date`、`snippet` 和 `labels` 的 JSON。

### 读取

```bash
$GAPI gmail get MESSAGE_ID
```

以文本形式返回完整的邮件正文（优先使用纯文本，回退到 HTML）。

### 发送

```bash
# 基本发送
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"

# HTML 邮件
$GAPI gmail send --to user@example.com --subject "Report" \
  --body "<h1>Q4 Results</h1><p>Details here</p>" --html

# 自定义发件人标头（显示名称 + 电子邮件）
$GAPI gmail send --to user@example.com --subject "Hello" \
  --from '"Research Agent" <user@example.com>' --body "Message text"

# 带抄送
$GAPI gmail send --to user@example.com --cc "team@example.com" \
  --subject "Update" --body "FYI"
```

### 自定义发件人标头

`--from` 标志允许您自定义外发电子邮件的发件人显示名称。当多个 Agent 共享同一个 Gmail 账户，但您希望收件人看到不同的名称时，这非常有用：

```bash
# Agent 1
$GAPI gmail send --to client@co.com --subject "Research Summary" \
  --from '"Research Agent" <shared@company.com>' --body "..."

# Agent 2  
$GAPI gmail send --to client@co.com --subject "Code Review" \
  --from '"Code Assistant" <shared@company.com>' --body "..."
```

**工作原理：** `--from` 的值被设置为 MIME 消息上的 RFC 5322 `From` 标头。Gmail 允许在您自己经过身份验证的电子邮件地址上自定义显示名称，无需任何额外配置。收件人将看到自定义的显示名称（例如 "Research Agent"），而电子邮件地址保持不变。

**重要提示：** 如果您在 `--from` 中使用*不同的电子邮件地址*（不是经过身份验证的账户），Gmail 要求该地址必须在 Gmail 设置 → 账户 → 以...身份发送邮件中配置为 [Send As 别名](https://support.google.com/mail/answer/22370)。

`--from` 标志在 `send` 和 `reply` 命令上都有效：

```bash
$GAPI gmail reply MESSAGE_ID \
  --from '"Support Bot" <shared@company.com>' --body "We're on it"
```

### 回复

```bash
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
```

自动将回复加入对话线程（设置 `In-Reply-To` 和 `References` 标头），并使用原始消息的线程 ID。

### 标签

```bash
# 列出所有标签
$GAPI gmail labels

# 添加/移除标签
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

## 日历

```bash
# 列出事件（默认为未来 7 天）
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# 创建事件（需要时区）
$GAPI calendar create --summary "Team Standup" \
  --start 2026-03-01T10:00:00-07:00 --end 2026-03-01T10:30:00-07:00

# 带地点和参与者
$GAPI calendar create --summary "Lunch" \
  --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z \
  --location "Cafe" --attendees "alice@co.com,bob@co.com"

# 删除事件
$GAPI calendar delete EVENT_ID
```

:::warning
日历时间**必须**包含时区偏移量（例如 `-07:00`）或使用 UTC（`Z`）。像 `2026-03-01T10:00:00` 这样的裸日期时间是不明确的，将被视为 UTC。
:::

## 云端硬盘

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

## 表格

```bash
# 读取一个范围
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# 写入一个范围
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# 追加行
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

## 文档

```bash
$GAPI docs get DOC_ID
```

返回文档标题和完整的文本内容。

## 联系人

```bash
$GAPI contacts list --max 20
```

## 输出格式

所有命令都返回 JSON。各服务的关键字段：

| 命令 | 字段 |
|---------|--------|
| `gmail search` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `snippet`, `labels` |
| `gmail get` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `labels`, `body` |
| `gmail send/reply` | `status`, `id`, `threadId` |
| `calendar list` | `id`, `summary`, `start`, `end`, `location`, `description`, `htmlLink` |
| `calendar create` | `status`, `id`, `summary`, `htmlLink` |
| `drive search` | `id`, `name`, `mimeType`, `modifiedTime`, `webViewLink` |
| `contacts list` | `name`, `emails`, `phones` |
| `sheets get` | 单元格值的二维数组 |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `NOT_AUTHENTICATED` | 运行设置（让 Hermes 设置 Google Workspace） |
| `REFRESH_FAILED` | Token 已撤销 — 重新运行授权步骤 |
| `HttpError 403: Insufficient Permission` | 缺少权限范围 — 撤销并重新授权正确的服务 |
| `HttpError 403: Access Not Configured` | Google Cloud Console 中未启用 API |
| `ModuleNotFoundError` | 使用 `--install-deps` 运行设置脚本 |