---
title: "Notion — Notion API + ntn CLI：页面、数据库、Markdown、Workers"
sidebar_label: "Notion"
description: "Notion API + ntn CLI：页面、数据库、Markdown、Workers"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Notion

Notion API + ntn CLI：页面、数据库、Markdown、Workers。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/notion` |
| 版本 | `2.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Notion`, `Productivity`, `Notes`, `Database`, `API`, `CLI`, `Workers` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Notion

与 Notion 交互的两种方式。同一个集成 Token 对两者都有效——根据可用性选择。

◆ **`ntn` CLI** — Notion 官方 CLI。语法更简洁，支持单行文件上传，Workers 必需。截至 2026 年 5 月，仅支持 macOS + Linux（Windows 支持“即将推出”）。**安装后默认使用此方式。**
◆ **HTTP + curl** — 适用于所有平台，包括 Windows。当 `ntn` 未安装时的**默认回退方案**。

## 设置

### 1. 获取集成 Token（两种方式都需要）

1. 在 https://notion.so/my-integrations 创建集成
2. 复制 API 密钥（以 `ntn_` 或 `secret_` 开头）
3. 存储到 `~/.hermes/.env`：
   ```
   NOTION_API_KEY=ntn_your_key_here
   ```
4. **在 Notion 中将目标页面/数据库分享给该集成**：页面菜单 `...` → `Connect to` → 你的集成名称。不执行此操作，即使页面存在，API 也会对该页面返回 404。

### 2. 安装 `ntn`（macOS / Linux 上的首选方式）

```bash
# 推荐方式
curl -fsSL https://ntn.dev | bash

# 或通过 npm（需要 Node 22+, npm 10+）
npm install --global ntn

ntn --version    # 验证安装
```

**跳过 `ntn login` — 直接使用集成 Token。** 这可以在无头环境下工作，无需浏览器：
```bash
export NOTION_API_TOKEN=$NOTION_API_KEY      # ntn 读取 NOTION_API_TOKEN
export NOTION_KEYRING=0                       # 不要尝试使用操作系统密钥环
```

将这些导出命令添加到你的 shell 配置文件（或 `~/.hermes/.env`）中，以便每个会话都能继承它们。

### 3. 在运行时选择方式

```bash
if command -v ntn >/dev/null 2>&1; then
  # 使用 ntn
else
  # 回退到 curl
fi
```

Windows 用户：在原生 `ntn` 发布前，完全跳过步骤 2——方式 B 工作正常。如果你现在就想使用 CLI 的便利性，请在 WSL2 中安装 `ntn`。

## API 基础

所有 HTTP 请求都需要 `Notion-Version: 2025-09-03` 头。`ntn` 会为你处理。在此版本中，用户所称的“数据库”在 API 中被称为**数据源**。

## 方式 A — `ntn` CLI（首选，macOS / Linux）

### 原始 API 调用（curl 的简写形式）
```bash
ntn api v1/users                                  # GET
ntn api v1/pages parent[page_id]=abc123 \         # POST 并内联请求体
  properties[title][0][text][content]="Notes"
ntn api v1/pages/abc123 -X PATCH archived:=true   # PATCH；:= 表示非字符串类型（布尔值/数字/null）
```

语法说明：
- `key=value` — 字符串字段
- `key[nested]=value` — 嵌套对象字段
- `key:=value` — 类型化赋值（布尔值、数字、null、数组）

### 搜索
```bash
ntn api v1/search query="page title"
```

### 读取页面元数据
```bash
ntn api v1/pages/{page_id}
```

### 以 Markdown 格式读取页面（对 Agent 友好）
```bash
ntn api v1/pages/{page_id}/markdown
```

### 以块的形式读取页面内容
```bash
ntn api v1/blocks/{page_id}/children
```

### 从 Markdown 创建页面
```bash
ntn api v1/pages \
  parent[page_id]=xxx \
  properties[title][0][text][content]="Notes from meeting" \
  markdown="# Agenda

- Q3 roadmap
- Hiring"
```

### 使用 Markdown 更新页面
```bash
ntn api v1/pages/{page_id}/markdown -X PATCH \
  markdown="## Update

Shipped the prototype."
```

### 查询数据库（数据源）
```bash
ntn api v1/data_sources/{data_source_id}/query -X POST \
  filter[property]=Status filter[select][equals]=Active
```

对于包含 `sorts`、多个过滤子句或复合逻辑的复杂查询，可以通过管道传入 JSON：
```bash
echo '{"filter": {"property": "Status", "select": {"equals": "Active"}}, "sorts": [{"property": "Date", "direction": "descending"}]}' | \
  ntn api v1/data_sources/{data_source_id}/query -X POST --json -
```

### 文件上传（单行命令 — CLI 的最大优势）
```bash
ntn files create < photo.png
ntn files create --external-url https://example.com/photo.png
ntn files list
```

与三步 HTTP 流程（创建上传 → PUT 字节 → 引用）相比。

### 有用的环境变量
| 变量 | 作用 |
|---|---|
| `NOTION_API_TOKEN` | 认证 Token（覆盖密钥环）— 将其设置为你的集成 Token |
| `NOTION_KEYRING=0` | 使用 `~/.config/notion/auth.json` 的文件凭证，而非操作系统密钥环 |
| `NOTION_WORKSPACE_ID` | 跳过工作区选择提示 |

## 方式 B — HTTP + curl（跨平台，Windows 上默认）

所有请求都遵循此模式：

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

在 Windows 上，Windows 10+ 自带的 `curl` 可以直接使用。PowerShell 用户也可以使用 `Invoke-RestMethod`。

### 搜索
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

### 读取页面元数据
```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 以 Markdown 格式读取页面（对 Agent 友好）

比块 JSON 更容易输入给模型。

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```
### 以块的形式读取页面内容（当你需要结构时）
```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 从 Markdown 创建页面

`POST /v1/pages` 接受一个 `markdown` 正文参数。

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "properties": {"title": [{"text": {"content": "Notes from meeting"}}]},
    "markdown": "# Agenda\n\n- Q3 roadmap\n- Hiring\n\n## Decisions\n- Ship MVP Friday"
  }'
```

### 使用 Markdown 更新页面
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Update\n\nShipped the prototype."}'
```

### 在数据库中创建页面（带类型属性）
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

### 查询数据库（数据源）
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

### 创建数据库
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

### 更新页面属性
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### 向页面追加块
```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
    ]
  }'
```

### 文件上传（三步流程）
```bash
# 1. 创建上传
curl -s -X POST "https://api.notion.com/v1/file_uploads" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filename": "photo.png", "content_type": "image/png"}'

# 2. 将字节数据 PUT 到上面返回的 upload_url
curl -s -X PUT "{upload_url}" --data-binary @photo.png

# 3. 在页面/块的有效载荷中引用 {file_upload_id}
```

## 属性类型

数据库项目的常见属性格式：

- **标题：** `{"title": [{"text": {"content": "..."}}]}`
- **富文本：** `{"rich_text": [{"text": {"content": "..."}}]}`
- **选择：** `{"select": {"name": "Option"}}`
- **多选：** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **日期：** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **复选框：** `{"checkbox": true}`
- **数字：** `{"number": 42}`
- **URL：** `{"url": "https://..."}`
- **电子邮件：** `{"email": "user@example.com"}`
- **关联：** `{"relation": [{"id": "page_id"}]}`

## API 版本 2025-09-03 — 数据库与数据源

- **数据库变为数据源。** 使用 `/data_sources/` 端点进行查询和检索。
- **每个数据库有两个 ID：** `database_id` 和 `data_source_id`。
  - 创建页面时使用 `database_id`：`parent: {"database_id": "..."}`
  - 查询时使用 `data_source_id`：`POST /v1/data_sources/{id}/query`
- 搜索返回的数据库对象为 `"object": "data_source"`，并带有 `data_source_id` 字段。

## Notion Workers（高级功能，需要 `ntn`）

Workers 是 Notion 为你托管的 TypeScript 程序。一个 Worker 可以公开以下任意组合：
- **同步** — 按计划（默认 30 分钟）从外部 API 拉取数据到 Notion 数据库。
- **工具** — 作为可调用工具出现在 Notion 的 Custom Agents 中。
- **Webhooks** — 接收来自外部服务（GitHub、Stripe 等）的 HTTP 事件并在 Notion 中执行操作。

**计划/平台限制：**
- CLI 在所有计划中都可用。**部署 Workers 需要 Business 或 Enterprise 计划。**
- 截至 2026 年 5 月，`ntn` 仅支持 macOS/Linux。Windows 用户需要使用 WSL2 或等待原生支持。
- 在 2026 年 8 月 11 日之前免费；之后按 Notion 积分计费。

### 最小化 Worker

```bash
ntn workers new my-worker      # 脚手架
cd my-worker
# 编辑 src/index.ts
ntn workers deploy --name my-worker
```

`src/index.ts`：
```typescript
import { Worker } from "@notionhq/workers";

const worker = new Worker();
export default worker;

worker.tool("greet", {
  title: "Greet a User",
  description: "Returns a friendly greeting",
  inputSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] },
  execute: async ({ name }) => `Hello, ${name}!`,
});
```

### Webhook 功能

```typescript
worker.webhook("onGithubPush", {
  title: "GitHub Push Handler",
  execute: async (events, { notion }) => {
    for (const event of events) {
      // event.body, event.rawBody (用于签名验证), event.headers
      console.log("got delivery", event.deliveryId);
    }
  },
});
```
部署后：`ntn workers webhooks list` 会显示 Notion 生成的 URL。请将该 URL 视为机密——除非你添加签名验证，否则任何拥有该 URL 的人都可以 POST 事件。

### Worker 生命周期命令

```bash
ntn workers deploy
ntn workers list
ntn workers exec <capability-key> -d '{"name": "world"}'
ntn workers sync trigger <key>            # 立即运行同步
ntn workers sync pause <key>
ntn workers env set GITHUB_WEBHOOK_SECRET=...
ntn workers runs list                     # 最近的调用
ntn workers runs logs <run-id>
ntn workers webhooks list
```

当需要构建一个 Worker 时，使用 `ntn workers new` 搭建脚手架，在 `src/index.ts` 中编写代码，使用 `ntn workers env set` 设置任何密钥，然后部署。Notion 的文档位于 https://developers.notion.com/workers，涵盖了完整的 API 接口。

## Notion 风格 Markdown（由 `/markdown` 端点使用）

标准 CommonMark 加上用于 Notion 特定块的类 XML 标签。使用 **制表符** 进行缩进。

**超出 CommonMark 的块：**
```
<callout icon="🎯" color="blue_bg">
	Ship the MVP by **Friday**.
</callout>

<details color="gray">
<summary>Toggle title</summary>
	Children indented one tab
</details>

<columns>
	<column>Left side</column>
	<column>Right side</column>
</columns>

<table_of_contents color="gray"/>
```

**行内元素：**
- 提及：`<mention-user url="..."/>`, `<mention-page url="...">Title</mention-page>`, `<mention-date start="2026-05-15"/>`
- 下划线：`<span underline="true">text</span>`
- 颜色：`<span color="blue">text</span>` 或块级 `{color="blue"}` 放在第一行
- 数学公式：行内 `$x^2$`，块级 `$$ ... $$`
- 引用：`[^https://example.com]`

**颜色：** `gray brown orange yellow green blue purple pink red`，以及用于背景的 `*_bg` 变体。

标题 5/6 会折叠为 H4。多个 `>` 行会渲染为单独的引用块——在单个 `>` 内使用 `<br>` 来实现多行引用。

## 选择正确的路径

| 任务 | mac / Linux | Windows |
|---|---|---|
| 读写页面、搜索、查询数据库 | `ntn api ...` | curl |
| 读取页面供 Agent 总结 | `ntn api v1/pages/{id}/markdown` | curl `/markdown` 端点 |
| 上传文件 | `ntn files create < file` | 3 步 HTTP 流程 |
| 一次性 API 探索 | `ntn api ...` | curl |
| 构建由 Notion 托管的同步 / webhook / Agent 工具 | `ntn workers ...` | WSL2 + `ntn workers ...` |

## 注意事项

- 页面/数据库 ID 是 UUID（带或不带短横线——两者都接受）。
- 速率限制：平均约每秒 3 个请求。CLI 不会绕过此限制。
- API 无法设置数据库**视图**过滤器——这仅限于 UI。
- 创建数据源时使用 `"is_inline": true` 以将其嵌入页面。
- 使用 curl 时始终传递 `-s` 以抑制进度条（使 Agent 输出更清晰）。
- 读取时通过 `jq` 管道传输 JSON：`... | jq '.results[0].properties'`。
- Notion 现在还提供了一个 MCP 服务器（`Notion MCP`，在数据库操作上比前一版本节省约 91% 的 Token）——如果你希望在会话内部获得流式 Notion 访问，可以通过 Hermes 的 MCP 支持连接它，但上述路径对于大多数一次性任务来说已经足够。