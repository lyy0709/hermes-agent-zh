---
title: "Searxng Search — 通过 SearXNG 进行免费元搜索 — 聚合 70 多个搜索引擎的结果"
sidebar_label: "Searxng Search"
description: "通过 SearXNG 进行免费元搜索 — 聚合 70 多个搜索引擎的结果"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Searxng Search

通过 SearXNG 进行免费元搜索 — 聚合 70 多个搜索引擎的结果。可自托管或使用公共实例。无需 API 密钥。当网页搜索工具集不可用时自动回退。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/searxng-search` 安装 |
| 路径 | `optional-skills/research/searxng-search` |
| 版本 | `1.0.0` |
| 作者 | hermes-agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `search`, `searxng`, `meta-search`, `self-hosted`, `free`, `fallback` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search), [`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# SearXNG Search

使用 [SearXNG](https://searxng.org/) 进行免费元搜索 — 一个尊重隐私、可自托管的搜索聚合器，可同时查询 70 多个搜索引擎。

使用公共实例时**无需 API 密钥**。也可以自托管以获得完全控制。当主网页搜索工具集 (`FIRECRAWL_API_KEY`) 未配置时，此技能会自动作为回退选项出现。

## 配置

SearXNG 需要一个指向你的 SearXNG 实例的 `SEARXNG_URL` 环境变量：

```bash
# 公共实例（无需设置）
SEARXNG_URL=https://searxng.example.com

# 自托管的 SearXNG
SEARXNG_URL=http://localhost:8888
```

如果未配置实例，此技能将不可用，Agent 将回退到其他搜索选项。

## 检测流程

在选择方法之前，先检查实际可用的内容：

```bash
# 检查 SEARXNG_URL 是否已设置且实例可达
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

决策树：
1. 如果 `SEARXNG_URL` 已设置且实例有响应，则使用 SearXNG
2. 如果 `SEARXNG_URL` 未设置或实例不可达，则回退到其他可用的搜索工具
3. 如果用户明确想要使用 SearXNG，帮助他们设置实例或寻找公共实例

## 方法 1：通过 curl 使用 CLI（首选）

通过 `terminal` 使用 `curl` 调用 SearXNG JSON API。这避免了假设安装了任何特定的 Python 包。

```bash
# 文本搜索（JSON 输出）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=python+async+programming&format=json&engines=google,bing&limit=10"

# 关闭安全搜索
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=example&format=json&safesearch=0"

# 特定类别（常规、新闻、科学等）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=AI+news&format=json&categories=news"
```

### 常用 CLI 标志

| 标志 | 描述 | 示例 |
|------|-------------|---------|
| `q` | 查询字符串（URL 编码） | `q=python+async` |
| `format` | 输出格式：`json`, `csv`, `rss` | `format=json` |
| `engines` | 逗号分隔的引擎名称 | `engines=google,bing,ddg` |
| `limit` | 每个引擎的最大结果数（默认 10） | `limit=5` |
| `categories` | 按类别过滤 | `categories=news,science` |
| `safesearch` | 0=无，1=中等，2=严格 | `safesearch=0` |
| `time_range` | 过滤：`day`, `week`, `month`, `year` | `time_range=week` |

### 解析 JSON 结果

```bash
# 从 JSON 中提取标题和 URL
curl -s --max-time 10 "${SEARXNG_URL}/search?q=fastapi&format=json&limit=5" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(r.get('title',''))
    print(r.get('url',''))
    print(r.get('content','')[:200])
    print()
"
```

每个结果返回：`title`, `url`, `content`（摘要）, `engine`, `parsed_url`, `img_src`, `thumbnail`, `author`, `published_date`

## 方法 2：通过 `requests` 使用 Python API

使用 `requests` 库直接从 Python 调用 SearXNG REST API：

```python
import os, requests, urllib.parse

base_url = os.environ.get("SEARXNG_URL", "")
if not base_url:
    raise RuntimeError("SEARXNG_URL is not set")

query = "fastapi deployment guide"
params = {
    "q": query,
    "format": "json",
    "limit": 5,
    "engines": "google,bing",
}

resp = requests.get(f"{base_url}/search", params=params, timeout=10)
resp.raise_for_status()
data = resp.json()

for r in data.get("results", []):
    print(r["title"])
    print(r["url"])
    print(r.get("content", "")[:200])
    print()
```

## 方法 3：searxng-data Python 包

为了更结构化的访问，安装 `searxng-data` 包：

```bash
pip install searxng-data
```

```python
from searxng_data import engines

# 列出可用引擎
print(engines.list_engines())
```

注意：此包仅提供引擎元数据，而非搜索 API 本身。

## 自托管 SearXNG

要运行你自己的 SearXNG 实例：

```bash
# 使用 Docker
docker run -d -p 8888:8080 \
  -v $(pwd)/searxng:/etc/searxng \
  searxng/searxng:latest

# 然后设置
SEARXNG_URL=http://localhost:8888
```

或者通过 pip 安装：
```bash
pip install searxng
# 编辑 /etc/searxng/settings.yml
searxng-run
```

可用的公共 SearXNG 实例：
- `https://searxng.example.com`（替换为任何公共实例）

## 工作流：先搜索后提取

SearXNG 返回标题、URL 和摘要 — 而非完整的页面内容。要获取完整的页面内容，请先搜索，然后使用 `web_extract`、浏览器工具或 `curl` 提取最相关的 URL。

```bash
# 搜索相关页面
curl -s "${SEARXNG_URL}/search?q=fastapi+deployment&format=json&limit=3"
# 输出：包含标题和 URL 的结果列表

# 然后使用 web_extract 提取最佳 URL
```

## 限制

- **实例可用性**：如果 SearXNG 实例宕机或不可达，搜索将失败。始终检查 `SEARXNG_URL` 是否已设置且实例可达。
- **无内容提取**：SearXNG 返回摘要，而非完整的页面内容。使用 `web_extract`、浏览器工具或 `curl` 获取完整文章。
- **速率限制**：某些公共实例会限制请求。自托管可避免此问题。
- **引擎覆盖范围**：可用引擎取决于 SearXNG 实例的配置。某些引擎可能被禁用。
- **结果新鲜度**：元搜索聚合外部引擎 — 结果的新鲜度取决于这些引擎。

## 故障排除

| 问题 | 可能原因 | 操作建议 |
|---------|--------------|------------|
| `SEARXNG_URL` 未设置 | 未配置实例 | 使用公共 SearXNG 实例或设置你自己的实例 |
| 连接被拒绝 | 实例未运行或 URL 错误 | 检查 URL 是否正确以及实例是否正在运行 |
| 结果为空 | 实例阻止了查询 | 尝试不同的实例或自托管 |
| 响应缓慢 | 公共实例负载过高 | 自托管或使用负载较轻的公共实例 |
| 不支持 `json` 格式 | SearXNG 版本过旧 | 尝试 `format=rss` 或升级 SearXNG |

## 常见陷阱

- **始终设置 `SEARXNG_URL`**：没有它，技能无法工作。
- **URL 编码查询**：在 curl 中，空格和特殊字符必须进行 URL 编码，或者在 Python 中使用 `urllib.parse.quote()`。
- **使用 `format=json`**：默认格式可能不是机器可读的。始终明确请求 JSON。
- **设置超时**：始终使用 `--max-time` 或 `timeout=` 以避免在不可达的实例上挂起。
- **自托管最佳**：公共实例可能宕机、限速或阻止。自托管实例更可靠。

## 实例发现

如果 `SEARXNG_URL` 未设置且用户询问 SearXNG，帮助他们：
1. 寻找公共 SearXNG 实例（搜索 "public searxng instance"）
2. 使用 Docker 或 pip 设置他们自己的实例

公共实例列表位于：https://searxng.org/