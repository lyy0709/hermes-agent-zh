---
title: "Airtable — 通过 curl 使用 Airtable REST API"
sidebar_label: "Airtable"
description: "通过 curl 使用 Airtable REST API"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Airtable

通过 curl 使用 Airtable REST API。记录的增删改查、筛选、更新或插入。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/airtable` |
| 版本 | `1.1.0` |
| 作者 | community |
| 许可证 | MIT |
| 标签 | `Airtable`, `Productivity`, `Database`, `API` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Airtable — 基础、表格与记录

通过 `terminal` 工具直接使用 `curl` 与 Airtable 的 REST API 交互。无需 MCP 服务器、OAuth 流程或 Python SDK——只需 `curl` 和个人访问令牌。

## 先决条件

1.  在 https://airtable.com/create/tokens 创建一个**个人访问令牌**（令牌以 `pat...` 开头）。
2.  授予以下（最低）权限：
    - `data.records:read` — 读取行
    - `data.records:write` — 创建 / 更新 / 删除行
    - `schema.bases:read` — 列出基础和表格
3.  **重要：** 在同一令牌界面中，将你想要访问的每个基础添加到令牌的**访问**列表中。PAT 是按基础限定范围的——在错误基础上使用有效令牌会返回 `403`。
4.  将令牌存储在 `~/.hermes/.env` 中（或通过 `hermes setup`）：
    ```
    AIRTABLE_API_KEY=pat_your_token_here
    ```

> 注意：传统的 `key...` API 密钥已于 2024 年 2 月弃用。现在仅 PAT 和 OAuth 令牌有效。

## API 基础

- **端点：** `https://api.airtable.com/v0`
- **认证头：** `Authorization: Bearer $AIRTABLE_API_KEY`
- **所有请求**都使用 JSON（任何 POST/PATCH/PUT 请求体使用 `Content-Type: application/json`）。
- **对象 ID：** 基础 `app...`、表格 `tbl...`、记录 `rec...`、字段 `fld...`。ID 永不更改；名称可以更改。在自动化中优先使用 ID。
- **速率限制：** 5 个请求/秒/基础。收到 `429` → 退避。在单个基础上突发请求将被限制。

基础 curl 模式：
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=5" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

`-s` 抑制 curl 的进度条——为保持 Hermes 的工具输出整洁，请始终设置此选项。通过 `python3 -m json.tool`（始终存在）或 `jq`（如果已安装）管道传输以获得可读的 JSON。

## 字段类型（请求体格式）

| 字段类型 | 写入格式 |
|---|---|
| 单行文本 | `"Name": "hello"` |
| 长文本 | `"Notes": "multi\nline"` |
| 数字 | `"Score": 42` |
| 复选框 | `"Done": true` |
| 单选 | `"Status": "Todo"`（名称必须已存在，除非 `typecast: true`） |
| 多选 | `"Tags": ["urgent", "bug"]` |
| 日期 | `"Due": "2026-04-01"` |
| 日期时间（UTC） | `"At": "2026-04-01T14:30:00.000Z"` |
| URL / 邮箱 / 电话 | `"Link": "https://…"` |
| 附件 | `"Files": [{"url": "https://…"}]`（Airtable 获取并重新托管） |
| 链接记录 | `"Owner": ["recXXXXXXXXXXXXXX"]`（记录 ID 数组） |
| 用户 | `"AssignedTo": {"id": "usrXXXXXXXXXXXXXX"}` |

在创建/更新请求体的顶层传递 `"typecast": true`，以允许 Airtable 自动强制转换值（例如，即时创建新的选择选项，将 `"42"` 转换为 `42`）。

## 常见查询

### 列出令牌可见的基础
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 列出基础中的表格 + 模式
```bash
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
在修改**之前**使用此命令——确认确切的字段名称和 ID，显示选择字段的 `options.choices`，并显示主字段名称。

### 列出记录（前 10 条）
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 获取单个记录
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 筛选记录（filterByFormula）
Airtable 公式必须进行 URL 编码。让 Python 标准库来处理——切勿手动编码：
```bash
FORMULA="{Status}='Todo'"
ENC=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$FORMULA")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC&maxRecords=20" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

有用的公式模式：
- 精确匹配：`{Email}='user@example.com'`
- 包含：`FIND('bug', LOWER({Title}))`
- 多条件：`AND({Status}='Todo', {Priority}='High')`
- 或：`OR({Owner}='alice', {Owner}='bob')`
- 非空：`NOT({Assignee}='')`
- 日期比较：`IS_AFTER({Due}, TODAY())`

### 排序 + 选择特定字段
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?sort%5B0%5D%5Bfield%5D=Priority&sort%5B0%5D%5Bdirection%5D=asc&fields%5B%5D=Name&fields%5B%5D=Status" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
查询参数中的方括号**必须**进行 URL 编码（`%5B` / `%5D`）。

### 使用命名视图
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?view=Grid%20view&maxRecords=50" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
视图会在服务器端应用其保存的筛选器和排序。

## 常见修改操作

### 创建记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Name":"New task","Status":"Todo","Priority":"High"}}' | python3 -m json.tool
```

### 在一次调用中创建最多 10 条记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "typecast": true,
    "records": [
      {"fields": {"Name": "Task A", "Status": "Todo"}},
      {"fields": {"Name": "Task B", "Status": "In progress"}}
    ]
  }' | python3 -m json.tool
```
批量端点限制为**每个请求 10 条记录**。对于更大的插入操作，请以 10 条为一批进行循环，并短暂休眠以遵守 5 个请求/秒/基础的速率限制。

### 更新记录（PATCH — 合并，保留未更改的字段）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Status":"Done"}}' | python3 -m json.tool
```

### 通过合并字段进行更新或插入（无需 ID）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "performUpsert": {"fieldsToMergeOn": ["Email"]},
    "records": [
      {"fields": {"Email": "user@example.com", "Status": "Active"}}
    ]
  }' | python3 -m json.tool
```
`performUpsert` 会创建合并字段值新的记录，并修补合并字段值已存在的记录。非常适合幂等同步。

### 删除记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 在一次调用中删除最多 10 条记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE?records%5B%5D=rec1&records%5B%5D=rec2" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

## 分页

列表端点每页最多返回 **100 条记录**。如果响应包含 `"offset": "..."`，则在下次调用时将其传回。循环直到该字段消失：

```bash
OFFSET=""
while :; do
  URL="https://api.airtable.com/v0/$BASE_ID/$TABLE?pageSize=100"
  [ -n "$OFFSET" ] && URL="$URL&offset=$OFFSET"
  RESP=$(curl -s "$URL" -H "Authorization: Bearer $AIRTABLE_API_KEY")
  echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(r["id"], r["fields"].get("Name","")) for r in d["records"]]'
  OFFSET=$(echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("offset",""))')
  [ -z "$OFFSET" ] && break
done
```

## 典型的 Hermes 工作流

1.  **确认认证。** `curl -s -o /dev/null -w "%{http_code}\n" https://api.airtable.com/v0/meta/bases -H "Authorization: Bearer $AIRTABLE_API_KEY"` — 期望 `200`。
2.  **找到基础。** 列出基础（上述步骤）**或**如果令牌缺少 `schema.bases:read` 权限，则直接向用户询问 `app...` ID。
3.  **检查模式。** `GET /v0/meta/bases/$BASE_ID/tables` — 在修改任何内容之前，在会话中本地缓存确切的字段名称和主字段名称。
4.  **先读后写。** 对于“更新满足 Y 条件的 X”，先使用 `filterByFormula` 解析出 `rec...` ID，然后使用 `PATCH /v0/$BASE_ID/$TABLE/$RECORD_ID`。切勿猜测记录 ID。
5.  **批量写入。** 将相关的创建操作合并到一个包含 10 条记录的 POST 请求中，以保持在 5 个请求/秒的预算内。
6.  **破坏性操作。** 删除操作无法通过 API 撤销。如果用户说“删除所有 X”，请在执行前回显筛选条件和记录数量并确认。

## 常见陷阱

- **`filterByFormula` 必须进行 URL 编码。** 包含空格或非 ASCII 字符的字段名也需要编码（`{My Field}` → `%7BMy%20Field%7D`）。使用 Python 标准库（上述模式）——切勿手动转义。
- **响应中会省略空字段。** 缺少 `"Assignee"` 键并不意味着该字段不存在——它意味着此记录的值是空的。在断定字段缺失之前，请检查模式（步骤 3）。
- **PATCH 与 PUT。** `PATCH` 将提供的字段合并到记录中。`PUT` 完全替换记录并清除你未包含的任何字段。默认使用 `PATCH`。
- **单选选项必须存在。** 当 `Shipping` 不在字段的选项列表中时，写入 `"Status": "Shipping"` 会导致 `INVALID_MULTIPLE_CHOICE_OPTIONS` 错误，除非你传递 `"typecast": true`（这会自动创建该选项）。
- **按基础令牌范围限定。** 一个基础返回 `403` 而另一个基础正常，意味着令牌的访问列表未包含该基础——不是权限或认证问题。引导用户访问 https://airtable.com/create/tokens 授予权限。
- **速率限制是按基础，而不是按令牌。** 在 `baseA` 上 5 个请求/秒和在 `baseB` 上 5 个请求/秒是没问题的；仅在 `baseA` 上 6 个请求/秒将被限制。监控 `429` 响应中的 `Retry-After` 头。

## 给 Hermes 的重要说明

- **始终使用带有 `curl` 的 `terminal` 工具。** 不要使用 `web_extract`（它无法发送认证头）或 `browser_navigate`（需要 UI 认证且速度慢）。
- **当此技能加载时，`AIRTABLE_API_KEY` 会自动从 `~/.hermes/.env` 流入子进程**——无需在每次 `curl` 调用前重新导出。
- **在公式中小心转义花括号。** 在 heredoc 请求体中，`{Status}` 是字面量。在 shell 参数中，`{Status}` 在 `{...}` 大括号扩展上下文之外是安全的——但在将动态字符串拼接到 URL 之前，请通过 `python3 urllib.parse.quote` 传递。
- **使用 `python3 -m json.tool`（始终存在）进行美化输出**，而不是 `jq`（可选）。仅在需要筛选/投影时才使用 `jq`。
- **分页是按页的，不是全局的。** Airtable 的 100 条记录上限是硬性限制；无法提高。使用 `offset` 循环直到该字段消失。
- **读取非 2xx 响应中的 `errors` 数组**——Airtable 返回结构化的错误代码，如 `AUTHENTICATION_REQUIRED`、`INVALID_PERMISSIONS`、`MODEL_ID_NOT_FOUND`、`INVALID_MULTIPLE_CHOICE_OPTIONS`，这些代码会准确告诉你问题所在。