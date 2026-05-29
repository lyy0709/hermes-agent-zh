---
title: "Osint Investigation"
sidebar_label: "Osint Investigation"
description: "公开记录 OSINT 调查框架 — SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约市房产记录..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Osint Investigation

公开记录 OSINT 调查框架 — SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约市房产记录 (ACRIS)、OpenCorporates 注册信息、CourtListener 法庭记录、Wayback Machine 存档、Wikipedia + Wikidata、GDELT 新闻监控。跨来源的实体解析、交叉链接分析、时间关联、证据链构建。仅使用 Python 标准库。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/osint-investigation` 安装 |
| 路径 | `optional-skills/research/osint-investigation` |
| 版本 | `0.1.0` |
| 作者 | Hermes Agent (改编自 ShinMegamiBoson/OpenPlanter, MIT) |
| 平台 | linux, macos, windows |
| 标签 | `osint`, `investigation`, `public-records`, `sec`, `sanctions`, `corporate-registry`, `property`, `courts`, `due-diligence`, `journalism` |
| 相关技能 | [`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel), [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# OSINT Investigation — 公开记录交叉引用

用于公开记录 OSINT 的调查框架：政府合同、公司文件、游说、制裁、离岸泄露、房产记录、法庭记录、网络存档、知识库和全球新闻。在异构来源中解析实体，建立带有明确置信度的交叉链接，运行统计时间测试，并生成结构化的证据链。

**仅使用 Python 标准库。** 零安装。适用于 Linux、macOS、Windows。大多数来源无需 API 密钥即可工作（OpenCorporates 有一个可选的免费 Token，可以提高速率限制）。

改编自 MIT 许可的 ShinMegamiBoson/OpenPlanter 项目；扩展了原始项目未涵盖的身份/房产/诉讼/存档/新闻来源。

## 何时使用此技能

当用户询问以下内容时使用：

- "追踪资金流向" — 政府合同、游说 → 立法、制裁
- 公司尽职调查 — 谁控制公司 X，他们在哪里注册，谁在他们的董事会任职，他们提交了什么文件
- 制裁筛查 — 实体 X 是否在 OFAC SDN、ICIJ 离岸泄露名单上
- 利益输送调查 — 与离岸实体有联系的承包商、赢得奖项的游说客户
- 房产所有权 — 按姓名或地址查找记录的契约/抵押（纽约市；对于其他县，请将用户指向相关的记录机构）
- 诉讼历史 — 查找联邦和州法院意见以及 PACER 案件摘要
- 命名方式不同的多来源实体解析（LLC 后缀、缩写）
- 具有明确置信度级别的证据链构建
- "关于 X 说了什么" — 国际新闻 (GDELT) + Wikipedia 叙述 + Wayback Machine 恢复失效 URL

**不要**将此技能用于：

- 一般网络研究 → `web_search` / `web_extract`
- 域名/基础设施 OSINT → `domain-intel` 技能
- 学术文献 → `arxiv` 技能
- 社交媒体资料发现 → `sherlock` 技能 (可选)
- 美国**联邦**竞选财务 — 此处**故意**不涵盖 FEC（其 API 在免费的 DEMO_KEY 层级上对临时贡献者姓名查询不可靠）。对于联邦捐款，请将用户指向 https://www.fec.gov/data/。

## 工作流

Agent 通过 `terminal` 工具运行脚本。`SKILL_DIR` 是存放此 SKILL.md 的目录。

### 1. 确定适用的来源

阅读数据源维基条目以规划调查：

```
ls SKILL_DIR/references/sources/

# 联邦财务 / 监管
cat SKILL_DIR/references/sources/sec-edgar.md       # 公司文件
cat SKILL_DIR/references/sources/usaspending.md     # 联邦合同
cat SKILL_DIR/references/sources/senate-ld.md       # 游说
cat SKILL_DIR/references/sources/ofac-sdn.md        # 制裁
cat SKILL_DIR/references/sources/icij-offshore.md   # 离岸泄露

# 身份 / 房产 / 诉讼 / 存档 / 新闻
cat SKILL_DIR/references/sources/nyc-acris.md       # 纽约市房产记录
cat SKILL_DIR/references/sources/opencorporates.md  # 全球公司注册信息
cat SKILL_DIR/references/sources/courtlistener.md   # 法庭记录 (联邦 + 州)
cat SKILL_DIR/references/sources/wayback.md         # Wayback Machine 存档
cat SKILL_DIR/references/sources/wikipedia.md       # Wikipedia + Wikidata
cat SKILL_DIR/references/sources/gdelt.md           # 全球新闻监控
```

每个条目遵循 9 部分模板：摘要、访问方式、模式、覆盖范围、交叉引用键、数据质量、获取方式、法律、参考。

**交叉引用潜力**部分映射了来源之间的连接键 — 首先阅读这些以选择正确的配对。

### 2. 获取数据

每个来源在 `SKILL_DIR/scripts/` 中都有一个仅使用标准库的获取脚本：

**联邦财务 / 监管**

```bash
# SEC EDGAR 文件 (公司披露)
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --cik 0000320193 \
    --types 10-K,10-Q --out data/edgar_filings.csv

# USAspending 联邦合同
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --out data/contracts.csv

# 参议院 LD-1 / LD-2 游说披露
python3 SKILL_DIR/scripts/fetch_senate_ld.py --client "EXAMPLE CORP" \
    --year 2024 --out data/lobbying.csv

# OFAC SDN 制裁名单 (完整快照)
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --out data/ofac_sdn.csv

# ICIJ 离岸泄露 — 首次使用时下载约 70 MB 的批量 CSV，
# 然后在本地搜索。缓存 30 天，位于
# $HERMES_OSINT_CACHE/icij/ (默认: ~/.cache/hermes-osint/icij/)。
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --out data/icij.csv
```
**身份/财产/诉讼/档案/新闻**

```bash
# NYC 房产记录（契约、抵押、留置权）— 通过 Socrata 的 ACRIS
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "SMITH, JOHN" \
    --out data/acris.csv
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --address "571 HUDSON" \
    --out data/acris_addr.csv

# OpenCorporates — 130+ 司法管辖区的公司注册信息
# （需要免费 Token；设置 OPENCORPORATES_API_TOKEN 或传递 --token）
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --jurisdiction us_ny --out data/opencorporates.csv

# CourtListener — 联邦及州法院意见、PACER 案件摘要
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Smith v. Example Corp" \
    --type opinions --out data/courts.csv

# Wayback Machine — 历史网页快照
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --collapse digest --out data/wayback.csv

# Wikipedia + Wikidata — 叙述性传记 + 结构化事实
# 设置 HERMES_OSINT_UA=your-app/1.0 (your@email) 以标识自己
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Bill Gates" \
    --out data/wp.csv

# GDELT — 100+ 语言的全球新闻，约 2015 年至今
python3 SKILL_DIR/scripts/fetch_gdelt.py --query '"Example Corp"' \
    --timespan 1y --out data/gdelt.csv
```

所有输出均为带有标题行的标准化 CSV。脚本可幂等地重新运行。

当某个私人个体不会出现在某个数据源中时（例如，非上市公司人士不会出现在 SEC EDGAR 中，非联邦承包商不会出现在 USAspending 中，非游说客户不会出现在 Senate LDA 中），脚本会返回 0 行并给出明确警告，而不是静默地写入空 CSV。特别是 EDGAR，当公司名称解析器匹配到的是个人 Form 3/4/5 申报者而非公司注册者时，会进行标记。

每个数据源的维基条目中都有速率限制说明。默认的抓取器会在分页请求之间礼貌地休眠。**对于支持 API 密钥的数据源**（`SEC_USER_AGENT`、`SENATE_LDA_TOKEN`、`OPENCORPORATES_API_TOKEN`、`COURTLISTENER_TOKEN`），**API 密钥可以提高速率限制**。所有脚本都会立即向上游返回 429 响应及其配额信息，以便用户知道需要放慢速度或提供密钥。

### 3. 跨数据源解析实体

标准化名称并在两个 CSV 文件之间查找匹配项：

```bash
# 将游说客户（Senate LDA）与合同接收方（USAspending）进行匹配
python3 SKILL_DIR/scripts/entity_resolution.py \
    --left  data/lobbying.csv   --left-name-col  client_name \
    --right data/contracts.csv  --right-name-col recipient_name \
    --out data/cross_links.csv
```

三个匹配层级，带有明确的置信度：

| 层级 | 方法 | 置信度 |
|------|--------|------------|
| `exact` | 去除后缀/标点后，标准化字符串相等 | 高 |
| `fuzzy` | 排序后的词元相等（词袋匹配） | 中 |
| `token_overlap` | ≥60% 词元重叠，≥2 个共享词元，词元长度 ≥4 字符 | 低 |

输出 `cross_links.csv` 的列：`match_type, confidence, left_name, right_name, left_normalized, right_normalized, left_row, right_row`。

### 4. 统计时序相关性分析（可选）

使用置换检验来测试两个时间序列是否可疑地紧密聚集在一起——例如，游说申报时间是否接近合同授予时间：

```bash
python3 SKILL_DIR/scripts/timing_analysis.py \
    --donations data/lobbying.csv --donation-date-col filing_date \
        --donation-amount-col income --donation-donor-col client_name \
        --donation-recipient-col registrant_name \
    --contracts data/contracts.csv --contract-date-col award_date \
        --contract-vendor-col recipient_name \
    --cross-links data/cross_links.csv \
    --permutations 1000 \
    --out data/timing.json
```

脚本的列标志是故意设计成通用的——原始工具是为捐款与奖项对比而写的，但它适用于任何通过交叉链接连接的（事件，收款方）时间序列。零假设：事件时间与奖项授予日期相互独立。单尾 p 值 = 置换样本中平均最近奖项距离 ≤ 观测值的比例。每个（付款方，供应商）对至少需要 3 个事件才能运行该检验。

### 5. 构建调查结果 JSON（证据链）

```bash
python3 SKILL_DIR/scripts/build_findings.py \
    --cross-links data/cross_links.csv \
    --timing data/timing.json \
    --out data/findings.json
```

每个调查结果都包含 `id, title, severity, confidence, summary, evidence[], sources[]`。每个证据项都指向源 CSV 中的特定行。用户（或后续的 Agent）可以对照其来源验证每个声明。

## 置信度与证据规范

这是该技能的承重规则。请告知用户：

-   每个声明都必须能追溯到一条记录。没有无根据的断言。
-   置信度层级随声明一起传递。`match_type=fuzzy` 是“可能”，而不是“已确认”。
-   实体解析产生的是候选匹配，而非结论。`fuzzy` 匹配 "ACME LLC" 和 "Acme Holdings Group" 是一个线索，而不是一个事实。
-   统计显著性 ≠ 不当行为。p < 0.05 意味着该时间模式在零假设下不太可能出现。它并不能证明存在腐败。
-   这里的所有数据源都是公开记录。它们仍可能包含不准确、过时或被编辑（GDPR、密封记录）的信息。

## 添加新的数据源

使用模板：

```bash
cp SKILL_DIR/templates/source-template.md \
    SKILL_DIR/references/sources/<your-source>.md
```

填写所有 9 个部分。在 `scripts/` 目录下编写一个 `fetch_<source>.py` 脚本，该脚本仅使用标准库并写入标准化的 CSV。更新上文“何时使用”部分中的数据源列表。

## 工具及其限制

-   `entity_resolution.py` **不**使用外部模糊匹配库（没有 rapidfuzz，没有 jellyfish）。词袋匹配是这里的上限。如果需要 Levenshtein 距离、音译或语音匹配，请单独 pip 安装。
-   `timing_analysis.py` 使用 Python 的 `random` 进行置换。为了可复现性，请传递 `--seed N`。
-   `fetch_*.py` 脚本使用 `urllib.request` 并遵守 `Retry-After`。大量的批量使用仍可能违反服务条款——请先阅读每个数据源的法律条款部分。
## 法律声明

所有 Phase-1 来源均为公开记录。根据其各自的访问条款（《信息自由法》、公共记录法、ICIJ 明确发布、OFAC 公开数据），允许批量获取。但是：

-   部分来源会进行严格的速率限制。请遵守其响应头中的规定。
-   部分来源会编辑注册人信息（例如 WHOIS 中的 GDPR 规定、密封的备案文件）。
-   交叉引用公开记录以识别私人个体可能涉及伦理问题。该技能生成的是证据链，而非指控。