---
title: X (Twitter) 搜索
description: 在 Agent 内部使用 xAI 内置的 x_search Responses 工具搜索 X (Twitter) 帖子和线程 — 支持 SuperGrok OAuth 登录或 XAI_API_KEY。
sidebar_label: X (Twitter) 搜索
sidebar_position: 7
---

# X (Twitter) 搜索

`x_search` 工具允许 Agent 直接搜索 X (Twitter) 帖子、个人资料和线程。它由 xAI 在 `https://api.x.ai/v1/responses` 的 Responses API 上内置的 `x_search` 工具支持 — Grok 本身在服务器端运行搜索，并返回带有原始帖子引用的综合结果。

当你**特别需要 X 上的**当前讨论、反应或声明时，**请使用此工具代替 `web_search`**。对于一般的网页，请继续使用 `web_search` / `web_extract`。

## 认证

当**任一** xAI 凭证路径可用时，`x_search` 会注册：

| 凭证 | 来源 | 设置 |
|------------|--------|-------|
| **SuperGrok OAuth** (首选) | 在 `accounts.x.ai` 进行浏览器登录，自动刷新 | `hermes auth add xai-oauth` — 参见 [xAI Grok OAuth (SuperGrok 订阅)](../../guides/xai-grok-oauth.md) |
| **`XAI_API_KEY`** | 付费的 xAI API 密钥 | 在 `~/.hermes/.env` 中设置 |

两者都使用相同的端点和相同的负载 — 唯一的区别是承载令牌。**当两者都配置时，SuperGrok OAuth 优先**，因此 x_search 将使用你的订阅配额运行，而不是消耗付费 API 额度。

该工具的 `check_fn` 每次重建模型的工具列表时都会运行 xAI 凭证解析器。返回 `True` 意味着承载令牌可获取、非空且（如果已过期）已成功刷新。刷新失败导致令牌被撤销时，该工具将从模式中隐藏；模型根本看不到它。

## 启用工具

默认关闭。在 `hermes tools` 中启用：

```bash
hermes tools
# → 🐦 X (Twitter) Search   (按空格键切换启用)
```

选择器提供两种凭证选择：

1.  **xAI Grok OAuth (SuperGrok 订阅)** — 如果你尚未登录，将打开浏览器访问 `accounts.x.ai`
2.  **xAI API 密钥** — 提示输入 `XAI_API_KEY`

任一选择都满足启用条件。你可以选择你已有的任何凭证；该工具对两者都同样有效。如果最终两者都配置了，在调用时 OAuth 是首选。

## 配置

```yaml
# ~/.hermes/config.yaml
x_search:
  # 用于 Responses 调用的 xAI 模型。
  # grok-4.20-reasoning 是推荐的默认值；任何具有 x_search 工具访问权限的 Grok 模型都适用。
  model: grok-4.20-reasoning

  # 请求超时时间（秒）。x_search 对于复杂查询可能需要 60–120 秒 — 默认值较为宽松。最小值：30。
  timeout_seconds: 180

  # 在 5xx / ReadTimeout / ConnectionError 时的自动重试次数。
  # 每次重试都会退避（尝试秒数的 1.5 倍，上限为 5 秒）。
  retries: 2
```

## 工具参数

Agent 使用以下参数调用 `x_search`：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `query` | 字符串 (必需) | 在 X 上查找的内容。 |
| `allowed_x_handles` | 字符串数组 | 可选的要**专门**包含的句柄列表（最多 10 个）。开头的 `@` 会被去除。 |
| `excluded_x_handles` | 字符串数组 | 可选的要排除的句柄列表（最多 10 个）。与 `allowed_x_handles` 互斥。 |
| `from_date` | 字符串 | 可选的 `YYYY-MM-DD` 开始日期。 |
| `to_date` | 字符串 | 可选的 `YYYY-MM-DD` 结束日期。 |
| `enable_image_understanding` | 布尔值 | 要求 xAI 分析匹配帖子附带的图片。 |
| `enable_video_understanding` | 布尔值 | 要求 xAI 分析匹配帖子附带的视频。 |

该工具返回包含以下内容的 JSON：

- `answer` — 来自 Grok 的综合文本响应
- `citations` — Responses API 顶级字段返回的引用
- `inline_citations` — 从消息体中提取的 `url_citation` 注释（每个包含 `url`、`title`、`start_index`、`end_index`）
- `credential_source` — 如果 OAuth 解析成功则为 `"xai-oauth"`，如果 API 密钥解析成功则为 `"xai"`
- `model`、`query`、`provider`、`tool`、`success`

## 示例

与 Agent 对话：

> X 上的人们对新的 Grok 图像功能有什么看法？重点关注来自 @xai 的回复。

Agent 将：

1.  使用 `query="reactions to new Grok image features"`、`allowed_x_handles=["xai"]` 调用 `x_search`
2.  获取一个综合答案以及链接到特定帖子的引用列表
3.  用答案和引用进行回复

## 故障排除

### "没有可用的 xAI 凭证"

当两种认证路径都失败时，该工具会显示此信息。请在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，或者运行 `hermes auth add xai-oauth` 并完成浏览器登录。然后重新启动你的会话，以便 Agent 重新读取工具注册表。

### "`x_search` 未为此模型启用"

配置的 `x_search.model` 无法访问服务器端的 `x_search` 工具。切换到 `grok-4.20-reasoning`（默认值）或支持该工具的其他 Grok 模型。请查阅 [xAI 文档](https://docs.x.ai/) 获取当前支持的模型列表。

### 工具未出现在模式中

两种可能的原因：

1.  **工具集未启用。** 运行 `hermes tools` 并确认 `🐦 X (Twitter) Search` 已勾选。
2.  **没有 xAI 凭证。** check_fn 返回 False，因此模式保持隐藏。运行 `hermes auth status` 以确认 xai-oauth 登录状态，并检查 `XAI_API_KEY` 是否已设置（如果你使用的是 API 密钥路径）。

## 另请参阅

-   [xAI Grok OAuth (SuperGrok 订阅)](../../guides/xai-grok-oauth.md) — OAuth 设置指南
-   [网页搜索与提取](web-search.md) — 用于一般（非 X）网页搜索
-   [工具参考](../../reference/tools-reference.md) — 完整的工具目录