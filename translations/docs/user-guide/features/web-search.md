---
title: 网页搜索与提取
description: 通过多个后端提供商（包括免费自托管的 SearXNG）搜索网页、提取页面内容以及爬取网站。
sidebar_label: 网页搜索
sidebar_position: 6
---

# 网页搜索与提取

Hermes Agent 包含两个由多个后端提供商支持的、可供模型调用的网页工具：

- **`web_search`** — 搜索网页并返回排序后的结果
- **`web_extract`** — 从一个或多个 URL 获取并提取可读内容（当后端支持时，内置深度爬取功能）

两者都通过单一的后端选择进行配置。提供商通过 `hermes tools` 选择或直接在 `config.yaml` 中设置。递归爬取功能（Firecrawl/Tavily）通过 `web_extract` 暴露，而不是作为一个单独的 `web_crawl` 工具。

## 后端

| 提供商 | 环境变量 | 搜索 | 提取 | 爬取 | 免费额度 |
|----------|---------|--------|---------|-------|-----------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ | 500 积分/月 |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — | ✔ 免费 (自托管) |
| **Brave Search (免费层)** | `BRAVE_SEARCH_API_KEY` | ✔ | — | — | 2 000 次查询/月 |
| **DDGS (DuckDuckGo)** | — (无需密钥) | ✔ | — | — | ✔ 免费 |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ | 1 000 次搜索/月 |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — | 1 000 次搜索/月 |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — | 付费 |
| **xAI (Grok)** | `XAI_API_KEY` 或 `hermes auth login xai-oauth` | ✔ | — | — | 付费 (SuperGrok 或按 Token 计费) |

Brave Search、DDGS 和 xAI 是**仅搜索**功能 — 当你还需要 `web_extract` 时，可以将它们中的任何一个与 Firecrawl/Tavily/Exa/Parallel 配对使用。DDGS 底层使用了 [`ddgs` Python 包](https://pypi.org/project/ddgs/)；如果尚未安装，请运行 `pip install ddgs`（或让 Hermes 在首次使用时惰性安装）。xAI 在 Responses API 上运行 Grok 的服务端 `web_search` 工具 — 结果是 LLM 生成的，而非基于索引，因此标题、描述和 URL 选择都是模型输出（请参阅下面的[信任模型注意事项](#xai-grok)）。

**按功能拆分：** 你可以独立地为搜索和提取使用不同的提供商 — 例如，使用 SearXNG（免费）进行搜索，使用 Firecrawl 进行提取。请参阅下面的[按功能配置](#per-capability-configuration)。

:::tip Nous 订阅用户
如果你拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，网页搜索和提取可通过 **[Tool Gateway](tool-gateway.md)** 通过托管的 Firecrawl 获得 — 无需 API 密钥。新安装可以通过运行 `hermes setup --portal` 登录并一次性开启所有网关工具；现有安装可以通过 `hermes tools` 仅开启网页工具。
:::

---

## `web_extract` 如何处理长页面

后端返回原始的页面 Markdown，这可能非常庞大（论坛帖子、文档网站、带有嵌入评论的新闻文章）。为了保持你的上下文窗口可用并降低成本，`web_extract` 在将返回的内容交给 Agent 之前，会先通过 **`web_extract` 辅助模型** 进行处理。行为纯粹由大小驱动：

| 页面大小 (字符数) | 处理方式 |
|------------------------|--------------|
| 小于 5 000 | 原样返回 — 无需 LLM 调用，完整的 Markdown 会传递给 Agent |
| 5 000 – 500 000 | 通过 `web_extract` 辅助模型进行单次摘要，输出限制在约 5 000 字符 |
| 500 000 – 2 000 000 | 分块处理：分成 100k 字符的块，并行摘要每个块，然后合成最终摘要（约 5 000 字符） |
| 超过 2 000 000 | 拒绝处理，并提示使用 `web_crawl` 配合聚焦提取指令或更具体的来源 |

摘要会保留引文、代码块和关键事实的原始格式 — 它是一个内容压缩器，而非释义器。如果摘要失败或超时，Hermes 会回退到原始内容的前约 5 000 个字符，而不是返回无用的错误。

### 使用哪个模型进行摘要？

`web_extract` 辅助任务。默认情况下 (`auxiliary.web_extract.provider: "auto"`)，这是你的**主聊天模型** — 与 `hermes model` 相同的提供商和模型。这对于大多数设置来说没问题，但在昂贵的推理模型（Opus、MiniMax M2.7 等）上，每次长页面提取都会增加显著成本。

要将提取摘要路由到廉价、快速的模型，而不受主模型影响：

```yaml
# ~/.hermes/config.yaml
auxiliary:
  web_extract:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 360       # 秒；如果遇到摘要超时，请提高此值
```

或者交互式选择：`hermes model` → **Configure auxiliary models** → `web_extract`。

有关完整参考和每个任务的覆盖模式，请参阅 [辅助模型](/user-guide/configuration#auxiliary-models)。

### 当摘要成为阻碍时

如果你特别需要原始的、未经摘要的页面内容 — 例如，你正在抓取一个结构化页面，而 LLM 摘要会丢弃重要字段 — 请改用 `browser_navigate` + `browser_snapshot`。浏览器工具返回实时的无障碍树，无需辅助模型重写（对于超长页面，其自身也有 8 000 字符的快照上限）。

---

## 设置

### 通过 `hermes tools` 快速设置

运行 `hermes tools`，导航到 **Web Search & Extract**，然后选择一个提供商。向导会提示输入所需的 URL 或 API 密钥，并将其写入你的配置。

```bash
hermes tools
```

---

### Firecrawl (默认)

功能齐全的搜索、提取和爬取。推荐给大多数用户。

```bash
# ~/.hermes/.env
FIRECRAWL_API_KEY=fc-your-key-here
```

在 [firecrawl.dev](https://firecrawl.dev) 获取密钥。免费层每月包含 500 积分。

**自托管 Firecrawl：** 指向你自己的实例，而不是云 API：

```bash
# ~/.hermes/.env
FIRECRAWL_API_URL=http://localhost:3002
```

当设置了 `FIRECRAWL_API_URL` 时，API 密钥是可选的（通过 `USE_DB_AUTHENTICATION=false` 禁用服务器认证）。

---

### SearXNG (免费，自托管)

SearXNG 是一个尊重隐私的开源元搜索引擎，聚合了来自 70 多个搜索引擎的结果。**无需 API 密钥** — 只需将 Hermes 指向一个正在运行的 SearXNG 实例。
SearXNG **仅支持搜索** — `web_extract`（包括其爬取模式）需要单独的提取提供商。

#### 选项 A — 使用 Docker 自托管（推荐）

这将为您提供一个没有速率限制的私有实例。

**1. 创建工作目录：**

```bash
mkdir -p ~/searxng/searxng
cd ~/searxng
```

**2. 编写 `docker-compose.yml`：**

```yaml
# ~/searxng/docker-compose.yml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8888:8080"
    volumes:
      - ./searxng:/etc/searxng:rw
    environment:
      - SEARXNG_BASE_URL=http://localhost:8888/
    restart: unless-stopped
```

**3. 启动容器：**

```bash
docker compose up -d
```

**4. 启用 JSON API 格式：**

SearXNG 默认禁用 JSON 输出。复制生成的配置并启用它：

```bash
# 从容器中复制自动生成的配置
docker cp searxng:/etc/searxng/settings.yml ~/searxng/searxng/settings.yml
```

打开 `~/searxng/searxng/settings.yml` 并找到 `formats` 块（大约在第 84 行）：

```yaml
# 之前（默认 — JSON 禁用）：
formats:
  - html

# 之后（为 Hermes 启用 JSON）：
formats:
  - html
  - json
```

**5. 重启以应用更改：**

```bash
docker cp ~/searxng/searxng/settings.yml searxng:/etc/searxng/settings.yml
docker restart searxng
```

**6. 验证是否正常工作：**

```bash
curl -s "http://localhost:8888/search?q=test&format=json" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"results\"])} results')"
```

您应该会看到类似 `10 results` 的输出。如果收到 `403 Forbidden`，说明 JSON 格式仍被禁用 — 请重新检查第 4 步。

**7. 配置 Hermes：**

```bash
# ~/.hermes/.env
SEARXNG_URL=http://localhost:8888
```

然后在 `~/.hermes/config.yaml` 中选择 SearXNG 作为搜索后端：

```yaml
web:
  search_backend: "searxng"
```

或者通过 `hermes tools` → Web Search & Extract → SearXNG 进行设置。

---

#### 选项 B — 使用公共实例

公共 SearXNG 实例列表可在 [searx.space](https://searx.space/) 找到。筛选列表中**已启用 JSON 格式**的实例（在表格中显示）。

```bash
# ~/.hermes/.env
SEARXNG_URL=https://searx.example.com
```

:::caution 公共实例
公共实例有速率限制，运行时间不稳定，并且可能随时禁用 JSON 格式。对于生产用途，强烈建议自托管。
:::

---

#### 将 SearXNG 与提取提供商配对

SearXNG 处理搜索；您需要一个单独的提供商来处理 `web_extract`（包括任何深度爬取模式）。使用按能力配置的键：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"   # 或 tavily, exa, parallel
```

通过此配置，Hermes 对所有搜索查询使用 SearXNG，对 URL 提取使用 Firecrawl — 将免费搜索与高质量提取相结合。

---

### Tavily

AI 优化的搜索、提取和爬取，提供慷慨的免费额度。

```bash
# ~/.hermes/.env
TAVILY_API_KEY=tvly-your-key-here
```

在 [app.tavily.com](https://app.tavily.com/home) 获取密钥。免费额度包括每月 1,000 次搜索。

---

### Exa

具有语义理解的神经搜索。适用于研究和查找概念上相关的内容。

```bash
# ~/.hermes/.env
EXA_API_KEY=your-exa-key-here
```

在 [exa.ai](https://exa.ai) 获取密钥。免费额度包括每月 1,000 次搜索。

---

### Parallel

具有深度研究能力的 AI 原生搜索和提取。

```bash
# ~/.hermes/.env
PARALLEL_API_KEY=your-parallel-key-here
```

在 [parallel.ai](https://parallel.ai) 获取访问权限。

---

### xAI (Grok) {#xai-grok}

通过 Grok 服务器端的 [web_search 工具](https://docs.x.ai/developers/tools/web-search) 在 Responses API 上路由 `web_search`。Grok 执行实际的搜索并将顶部结果作为结构化 JSON 返回。

适用于任一凭证路径 — 无需新的环境变量，无需新的设置向导：

```bash
# ~/.hermes/.env (环境变量路径)
XAI_API_KEY=sk-xai-your-key-here
```

或者对于 SuperGrok 订阅者：

```bash
hermes auth login xai-oauth
```

然后选择 xAI 作为搜索后端：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "xai"
```

**可选配置项：**

```yaml
web:
  backend: "xai"
  xai:
    model: grok-4.3              # web_search 所需的推理模型（默认）
    allowed_domains:             # 可选，最多 5 个 — 与 excluded_domains 互斥
      - arxiv.org
    excluded_domains:            # 可选，最多 5 个
      - example-spam.com
    timeout: 90                  # 秒（默认）
```

**仅搜索** — 如果您还需要 `web_extract`，请与 Firecrawl / Tavily / Exa / Parallel 配对使用。在 401 错误时，提供商会执行一次强制 OAuth Token 刷新并重试（涵盖主动到期检查无法解码的窗口中期吊销和不透明 Token）；环境变量凭证会跳过重试。

:::caution 信任模型
与返回逐字搜索引擎结果的基于索引的提供商（Brave、Tavily、Exa）不同，xAI 是一个 LLM，它选择要展示哪些 URL 并自行编写标题和描述。查询的*内容*会影响输出，因此恶意构造的查询（例如，通过 Agent 获取的不受信任的上游输入注入）原则上可以引导 Grok 发出攻击者选择的 URL。请像对待任何模型生成的链接一样对待返回的 URL — 在获取之前进行验证，特别是当查询来自不受信任的输入时。
:::

---

## 配置

### 单一后端

为所有网络能力设置一个提供商：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "searxng"   # firecrawl | searxng | brave-free | ddgs | tavily | exa | parallel | xai
```

### 按能力配置

为搜索和提取使用不同的提供商。这使您可以将免费搜索（SearXNG）与付费提取提供商结合使用，反之亦然：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"     # 由 web_search 使用
  extract_backend: "firecrawl"  # 由 web_extract（及其深度爬取模式）使用
```

当按能力配置的键为空时，两者都会回退到 `web.backend`。当 `web.backend` 也为空时，后端会根据存在的任何 API 密钥/URL 自动检测。
**优先级顺序（按能力划分）：**
1. `web.search_backend` / `web.extract_backend`（针对特定能力显式配置）
2. `web.backend`（共享后备配置）
3. 根据环境变量自动检测

### 自动检测

如果未显式配置后端，Hermes 会根据设置了哪些凭据来选择第一个可用的后端：

| 存在的凭据 | 自动选择的后端 |
|--------------------|-----------------------|
| `FIRECRAWL_API_KEY` 或 `FIRECRAWL_API_URL` | firecrawl |
| `PARALLEL_API_KEY` | parallel |
| `TAVILY_API_KEY` | tavily |
| `EXA_API_KEY` | exa |
| `SEARXNG_URL` | searxng |

xAI Web Search **不**在自动检测链中 —— 设置了 `XAI_API_KEY`（或通过 xAI Grok OAuth 登录）不会自动将网络流量路由到 xAI，因为这些凭据也用于推理 / TTS / 图像生成，用户可能希望为网络使用不同的后端。请使用 `web.backend: "xai"` 显式选择。

---

## 验证你的设置

运行 `hermes setup` 以查看检测到哪个网络后端：

```
✅ Web Search & Extract (searxng)
```

或者通过 CLI 检查：

```bash
# 激活 venv 并直接运行 web 工具模块
source ~/.hermes/hermes-agent/.venv/bin/activate
python -m tools.web_tools
```

这将打印活动后端及其状态：

```
✅ Web backend: searxng
   使用 SearXNG（仅搜索）：http://localhost:8888
```

---

## 故障排除

### `web_search` 返回 `{"success": false}`

- 检查 `SEARXNG_URL` 是否可达：`curl -s "http://localhost:8888/search?q=test&format=json"`
- 如果收到 HTTP 403，JSON 格式被禁用 —— 在 `settings.yml` 的 `formats` 列表中添加 `json` 并重启
- 如果收到连接错误，容器可能未运行：`docker ps | grep searxng`

### `web_extract` 显示“仅搜索后端”

SearXNG 无法提取 URL 内容。将 `web.extract_backend` 设置为支持提取的提供商：

```yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"  # 或 tavily / exa / parallel
```

### SearXNG 返回 0 个结果

某些公共实例禁用了特定的搜索引擎或类别。尝试：
- 不同的查询
- 来自 [searx.space](https://searx.space/) 的不同公共实例
- 自托管你自己的实例以获得可靠结果

### 在公共实例上被限速

切换到自托管实例（参见上面的[选项 A](#option-a--self-host-with-docker-recommended)）。使用 Docker，你自己的实例没有速率限制。

### `web_extract` 返回截断的内容并带有“summarization timed out”备注

辅助模型未在配置的超时时间内完成摘要。可以：

- 在 `config.yaml` 中提高 `auxiliary.web_extract.timeout`（新安装默认 360 秒，如果缺少该键则为 30 秒）
- 将 `web_extract` 辅助任务切换到更快的模型（例如 `google/gemini-3-flash-preview`）—— 参见 [`web_extract` 如何处理长页面](#how-web_extract-handles-long-pages)
- 对于摘要不是合适工具的情况，请改用 `browser_navigate`

---

## 可选技能：`searxng-search`

对于需要直接通过 `curl` 使用 SearXNG 的 Agent（例如，当 web 工具集不可用时作为后备），请安装 `searxng-search` 可选技能：

```bash
hermes skills install official/research/searxng-search
```

这将添加一个技能，教会 Agent 如何：
- 通过 `curl` 或 Python 调用 SearXNG JSON API
- 按类别过滤（`general`、`news`、`science` 等）
- 处理分页和错误情况
- 当 SearXNG 不可达时优雅地回退