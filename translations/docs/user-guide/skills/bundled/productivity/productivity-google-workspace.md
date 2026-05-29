---
title: "Google Workspace — 通过 gws CLI 或 Python 使用 Gmail、日历、Drive、Docs、Sheets"
sidebar_label: "Google Workspace"
description: "通过 gws CLI 或 Python 使用 Gmail、日历、Drive、Docs、Sheets"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Google Workspace

通过 gws CLI 或 Python 使用 Gmail、日历、Drive、Docs、Sheets。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/google-workspace` |
| 版本 | `1.1.0` |
| 作者 | Nous Research |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Google`, `Gmail`, `Calendar`, `Drive`, `Sheets`, `Docs`, `Contacts`, `Email`, `OAuth` |
| 相关技能 | [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Google Workspace

Gmail、日历、Drive、联系人、Sheets 和 Docs —— 通过 Hermes 管理的 OAuth 和一个轻量级 CLI 包装器。当 `gws` 已安装时，该技能将其用作执行后端以获得更广泛的 Google Workspace 覆盖；否则回退到内置的 Python 客户端实现。

## 参考

- `references/gmail-search-syntax.md` — Gmail 搜索运算符（is:unread, from:, newer_than: 等）

## 脚本

- `scripts/setup.py` — OAuth2 设置（运行一次以授权）
- `scripts/google_api.py` — 兼容性包装器 CLI。它在可用时优先使用 `gws` 进行操作，同时保持 Hermes 现有的 JSON 输出约定。

## 首次设置

设置完全是非交互式的 —— 您可以逐步驱动它，使其在 CLI、Telegram、Discord 或任何平台上工作。

首先定义一个简写：

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
```

### 步骤 0：检查是否已设置

```bash
$GSETUP --check
```

如果打印 `AUTHENTICATED`，请跳至“使用”部分 —— 设置已完成。

### 步骤 1：分流 —— 询问用户需要什么

在开始 OAuth 设置之前，询问用户两个问题：

**问题 1：“您需要哪些 Google 服务？仅电子邮件，还是也需要日历/Drive/Sheets/Docs？”**

- **仅电子邮件** → 他们完全不需要此技能。请改用 `himalaya` 技能 —— 它使用 Gmail 应用密码（设置 → 安全 → 应用密码）工作，只需 2 分钟即可设置。无需 Google Cloud 项目。加载 himalaya 技能并遵循其设置说明。

- **电子邮件 + 日历** → 继续使用此技能，但在授权期间使用 `--services email,calendar`，以便同意屏幕仅请求他们实际需要的范围。

- **仅日历/Drive/Sheets/Docs** → 继续使用此技能，并使用更窄的 `--services` 集合，如 `calendar,drive,sheets,docs`。

- **完整的 Workspace 访问权限** → 继续使用此技能，并使用默认的 `all` 服务集。

**问题 2：“您的 Google 帐户是否使用高级保护（需要硬件安全密钥才能登录）？如果不确定，您可能没有 —— 这是您需要明确注册的功能。”**

- **否 / 不确定** → 正常设置。继续下面的步骤。
- **是** → 他们的 Workspace 管理员必须在步骤 4 生效之前，将 OAuth 客户端 ID 添加到组织的允许应用列表中。请提前告知他们。

### 步骤 2：创建 OAuth 凭据（一次性，约 5 分钟）

告诉用户：

> 您需要一个 Google Cloud OAuth 客户端。这是一次性设置：
>
> 1.  创建或选择一个项目：
>     https://console.cloud.google.com/projectselector2/home/dashboard
> 2.  从 API 库启用所需的 API：
>     https://console.cloud.google.com/apis/library
>     启用：Gmail API、Google Calendar API、Google Drive API、Google Sheets API、Google Docs API、People API
> 3.  在此处创建 OAuth 客户端：
>     https://console.cloud.google.com/apis/credentials
>     凭据 → 创建凭据 → OAuth 2.0 客户端 ID
> 4.  应用程序类型：“桌面应用” → 创建
> 5.  如果应用仍处于测试阶段，请在此处将用户的 Google 帐户添加为测试用户：
>     https://console.cloud.google.com/auth/audience
>     受众群体 → 测试用户 → 添加用户
> 6.  下载 JSON 文件并告诉我文件路径
>
> 重要的 Hermes CLI 注意事项：如果文件路径以 `/` 开头，请勿在 CLI 中仅将裸路径作为单独的消息发送，因为它可能被误认为是斜杠命令。请将其放在一个句子中发送，例如：
> `JSON 文件路径是：/home/user/Downloads/client_secret_....json`

一旦他们提供路径：

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

如果他们粘贴的是原始的客户端 ID / 客户端密钥值，而不是文件路径，请自行为他们编写一个有效的桌面 OAuth JSON 文件，将其保存在某个明确的位置（例如 `~/Downloads/hermes-google-client-secret.json`），然后对该文件运行 `--client-secret`。

### 步骤 3：获取授权 URL

使用步骤 1 中选择的服务集。示例：

```bash
$GSETUP --auth-url --services email,calendar --format json
$GSETUP --auth-url --services calendar,drive,sheets,docs --format json
$GSETUP --auth-url --services all --format json
```

这将返回一个包含 `auth_url` 字段的 JSON，并将确切的 URL 保存到 `~/.hermes/google_oauth_last_url.txt`。

此步骤的 Agent 规则：
- 提取 `auth_url` 字段，并将该确切 URL 作为单行发送给用户。
- 告诉用户，批准后浏览器很可能会在 `http://localhost:1` 上失败，这是预期情况。
- 告诉他们从浏览器地址栏复制**整个**重定向后的 URL。
- 如果用户遇到 `Error 403: access_denied`，请直接引导他们访问 `https://console.cloud.google.com/auth/audience` 将自己添加为测试用户。

### 步骤 4：交换代码

用户将粘贴回一个类似 `http://localhost:1/?code=4/0A...&scope=...` 的 URL 或仅仅是代码字符串。两者都可以。`--auth-url` 步骤会在本地存储一个临时的待处理 OAuth 会话，以便 `--auth-code` 稍后可以完成 PKCE 交换，即使在无头系统上也是如此：
```bash
$GSETUP --auth-code "用户粘贴的URL或代码" --format json
```

如果 `--auth-code` 因代码过期、已被使用或来自旧浏览器标签页而失败，现在会返回一个新的 `fresh_auth_url`。在这种情况下，请立即将新 URL 发送给用户，并让他们仅使用最新的浏览器重定向重试。

### 步骤 5：验证

```bash
$GSETUP --check
```

应打印 `AUTHENTICATED`。至此设置完成——从现在开始 Token 将自动刷新。

### 注意事项

- Token 存储在 `~/.hermes/google_token.json` 并会自动刷新。
- 待处理的 OAuth 会话状态/验证器会临时存储在 `~/.hermes/google_oauth_pending.json` 中，直到交换完成。
- 如果安装了 `gws`，`google_api.py` 会指向同一个 `~/.hermes/google_token.json` 凭证文件。用户无需运行单独的 `gws auth login` 流程。
- 撤销授权：`$GSETUP --revoke`

## 使用方法

所有命令都通过 API 脚本执行。设置 `GAPI` 作为简写：

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

### Gmail

```bash
# 搜索（返回包含 id、from、subject、date、snippet 的 JSON 数组）
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# 读取完整邮件（返回包含正文文本的 JSON）
$GAPI gmail get MESSAGE_ID

# 发送
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "Message text"

# 回复（自动处理线程并设置 In-Reply-To）
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail reply MESSAGE_ID --from '"Support Bot" <user@example.com>' --body "Thanks"

# 标签
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# 列出事件（默认为未来 7 天）
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# 创建事件（需要带时区的 ISO 8601 格式）
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# 删除事件
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
# 搜索现有文件
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# 获取单个文件的元数据
$GAPI drive get FILE_ID

# 上传本地文件（自动检测 MIME 类型）
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# 下载（二进制文件按原样下载；Google 原生文件导出为合理的默认格式——Docs→pdf、Sheets→csv、Slides→pdf、Drawings→png）
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# 创建文件夹
$GAPI drive create-folder "Reports"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# 共享
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # 任何拥有链接的人
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# 删除——默认移至回收站（可恢复）。使用 --permanent 跳过回收站。
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# 创建新的电子表格
$GAPI sheets create --title "Q4 Budget"
$GAPI sheets create --title "Inventory" --sheet-name "Stock"

# 读取
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# 写入
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# 追加行
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

### Docs

```bash
# 读取
$GAPI docs get DOC_ID

# 创建新的文档（可选择包含初始正文文本）
$GAPI docs create --title "Meeting Notes"
$GAPI docs create --title "Draft" --body "First paragraph..."

# 在现有文档末尾追加文本
$GAPI docs append DOC_ID --text "Additional content to append"
```

## 输出格式

所有命令都返回 JSON。使用 `jq` 解析或直接读取。关键字段：

- **Gmail 搜索**：`[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail 获取**：`{id, threadId, from, to, subject, date, labels, body}`
- **Gmail 发送/回复**：`{status: "sent", id, threadId}`
- **Calendar 列表**：`[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar 创建**：`{status: "created", id, summary, htmlLink}`
- **Drive 搜索**：`[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive 获取**：`{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive 上传**：`{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive 下载**：`{status: "downloaded", id, name, path, mimeType}`
- **Drive 创建文件夹**：`{status: "created", id, name, webViewLink}`
- **Drive 共享**：`{status: "shared", permissionId, fileId, role, type}`
- **Drive 删除**：`{status: "trashed" | "deleted", fileId, permanent}`
- **Contacts 列表**：`[{name, emails: [...], phones: [...]}]`
- **Sheets 获取**：`[[cell, cell, ...], ...]`
- **Sheets 创建**：`{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs 创建**：`{status: "created", documentId, title, url}`
- **Docs 追加**：`{status: "appended", documentId, inserted_at, characters}`
## 规则

1. **未经用户确认，切勿发送邮件、创建/删除日历事件、删除 Drive 文件、共享文件或修改 Docs/Sheets。** 展示将要执行的操作（收件人、文件 ID、内容、共享角色）并请求批准。对于 `drive delete`，优先选择默认的回收站（可恢复）而非 `--permanent`。
2. **首次使用前检查授权** — 运行 `setup.py --check`。如果失败，引导用户完成设置。
3. **对于复杂查询，使用 Gmail 搜索语法参考** — 使用 `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")` 加载它。
4. **日历时间必须包含时区** — 始终使用带偏移量的 ISO 8601 格式（例如 `2026-03-01T10:00:00-06:00`）或 UTC（`Z`）。
5. **遵守速率限制** — 避免快速连续调用 API。尽可能批量读取。

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `NOT_AUTHENTICATED` | 运行上述设置步骤 2-5 |
| `REFRESH_FAILED` | Token 已撤销或过期 — 重新执行步骤 3-5 |
| `HttpError 403: Insufficient Permission` | 缺少 API 权限范围 — 执行 `$GSETUP --revoke` 然后重新执行步骤 3-5 |
| `AUTHENTICATED (partial)` 或 "Token missing scopes" | 新的写入能力（Drive 写入/删除、Docs 创建/编辑）需要重新授权。执行 `$GSETUP --revoke` 然后重新执行步骤 3-5 以授予升级后的权限范围。 |
| `HttpError 403: Access Not Configured` | API 未启用 — 用户需要在 Google Cloud Console 中启用它 |
| `ModuleNotFoundError` | 运行 `$GSETUP --install-deps` |
| 高级保护阻止授权 | Workspace 管理员必须将 OAuth 客户端 ID 加入允许列表 |

## 撤销访问权限

```bash
$GSETUP --revoke
```