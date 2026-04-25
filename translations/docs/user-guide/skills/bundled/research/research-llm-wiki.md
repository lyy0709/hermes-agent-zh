---
title: "Llm Wiki — Karpathy 的 LLM Wiki — 构建和维护一个持久、相互链接的 Markdown 知识库"
sidebar_label: "Llm Wiki"
description: "Karpathy 的 LLM Wiki — 构建和维护一个持久、相互链接的 Markdown 知识库"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Llm Wiki

Karpathy 的 LLM Wiki — 构建和维护一个持久、相互链接的 Markdown 知识库。摄取来源、查询编译后的知识，并进行一致性检查。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/llm-wiki` |
| 版本 | `2.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `wiki`, `knowledge-base`, `research`, `notes`, `markdown`, `rag-alternative` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian), [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Karpathy 的 LLM Wiki

构建和维护一个持久的、可积累的知识库，作为相互链接的 Markdown 文件。
基于 [Andrej Karpathy 的 LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

与传统 RAG（每次查询都从头重新发现知识）不同，该 Wiki 一次性编译知识并保持其最新状态。交叉引用已经存在。矛盾之处已被标记。综合反映了所有摄取的内容。

**分工：** 人类负责策划来源并指导分析。Agent 负责总结、交叉引用、归档和维护一致性。

## 此技能何时激活

当用户出现以下情况时使用此技能：
- 要求创建、构建或启动一个 Wiki 或知识库
- 要求摄取、添加或处理某个来源到他们的 Wiki 中
- 提出问题且配置路径下存在现有 Wiki
- 要求对他们的 Wiki 进行一致性检查、审计或健康检查
- 在研究上下文中提及他们的 Wiki、知识库或“笔记”

## Wiki 位置

**位置：** 通过 `WIKI_PATH` 环境变量设置（例如在 `~/.hermes/.env` 中）。

如果未设置，默认为 `~/wiki`。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

Wiki 只是一个 Markdown 文件目录 — 可以在 Obsidian、VS Code 或任何编辑器中打开。无需数据库，无需特殊工具。

## 架构：三层

```
wiki/
├── SCHEMA.md           # 约定、结构规则、领域配置
├── index.md            # 带有一行摘要的分段内容目录
├── log.md              # 按时间顺序排列的操作日志（仅追加，每年轮换）
├── raw/                # 第 1 层：不可变的原始材料
│   ├── articles/       # 网络文章、摘录
│   ├── papers/         # PDF、arxiv 论文
│   ├── transcripts/    # 会议记录、访谈
│   └── assets/         # 来源引用的图片、图表
├── entities/           # 第 2 层：实体页面（人物、组织、产品、模型）
├── concepts/           # 第 2 层：概念/主题页面
├── comparisons/        # 第 2 层：并排分析
└── queries/            # 第 2 层：值得保存的归档查询结果
```

**第 1 层 — 原始来源：** 不可变。Agent 读取但从不修改这些内容。
**第 2 层 — Wiki：** Agent 拥有的 Markdown 文件。由 Agent 创建、更新和交叉引用。
**第 3 层 — 模式：** `SCHEMA.md` 定义了结构、约定和标签分类法。

## 恢复现有 Wiki（关键 — 每次会话都执行此操作）

当用户拥有现有 Wiki 时，**在执行任何操作之前，务必先定位自己**：

① **阅读 `SCHEMA.md`** — 了解领域、约定和标签分类法。
② **阅读 `index.md`** — 了解存在哪些页面及其摘要。
③ **扫描最近的 `log.md`** — 阅读最后 20-30 条条目以了解近期活动。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# 会话开始时的定位读取
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

只有在定位之后，才能进行摄取、查询或一致性检查。这可以防止：
- 为已存在的实体创建重复页面
- 遗漏对现有内容的交叉引用
- 违反模式的约定
- 重复已记录的工作

对于大型 Wiki（100+ 页面），在创建任何新内容之前，还应针对手头的主题快速运行 `search_files`。

## 初始化新 Wiki

当用户要求创建或启动 Wiki 时：

1.  确定 Wiki 路径（从 `$WIKI_PATH` 环境变量获取，或询问用户；默认 `~/wiki`）
2.  创建上述目录结构
3.  询问用户 Wiki 涵盖的领域 — 要具体
4.  编写针对该领域定制的 `SCHEMA.md`（见下方模板）
5.  编写带有分段标题的初始 `index.md`
6.  编写带有创建条目的初始 `log.md`
7.  确认 Wiki 已准备就绪，并建议首批要摄取的来源

### SCHEMA.md 模板

根据用户的领域进行调整。模式约束 Agent 行为并确保一致性：

```markdown
# Wiki 模式

## 领域
[此 Wiki 涵盖的内容 — 例如，“AI/ML 研究”、“个人健康”、“初创公司情报”]

## 约定
- 文件名：小写，连字符，无空格（例如，`transformer-architecture.md`）
- 每个 Wiki 页面都以 YAML frontmatter 开头（见下文）
- 使用 `[[wikilinks]]` 在页面之间链接（每个页面至少 2 个出站链接）
- 更新页面时，始终更新 `updated` 日期
- 每个新页面必须添加到 `index.md` 的正确部分下
- 每个操作必须追加到 `log.md`
- **来源标记：** 在综合了 3 个以上来源的页面上，在段落末尾追加 `^[raw/articles/source-file.md]`，这些段落的声明来自特定来源。这使读者无需重新阅读整个原始文件即可追溯每个声明。对于 `sources:` frontmatter 已足够的单一来源页面，此标记是可选的。

## Frontmatter
  ```yaml
  ---
  title: 页面标题
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [来自下方的分类法]
  sources: [raw/articles/source-name.md]
  # 可选的质量信号：
  confidence: high | medium | low        # 声明得到支持的程度
  contested: true                        # 当页面存在未解决的矛盾时设置
  contradictions: [other-page-slug]      # 与此页面冲突的其他页面
  ---
  ```

`confidence` 和 `contested` 是可选的，但对于观点性强或快速变化的主题建议使用。一致性检查会显示 `contested: true` 和 `confidence: low` 的页面以供审查，这样薄弱的声明就不会悄无声息地固化为公认的 Wiki 事实。

### raw/ Frontmatter

原始来源也包含一个小的 frontmatter 块，以便重新摄取时可以检测到变化：

```yaml
---
source_url: https://example.com/article   # 原始 URL（如果适用）
ingested: YYYY-MM-DD
sha256: &lt;原始内容（frontmatter 之后）的十六进制摘要>
---
```

`sha256:` 允许未来重新摄取相同 URL 时，在内容未更改时跳过处理，并在内容更改时标记变化。仅计算正文（关闭的 `---` 之后的所有内容），而不是 frontmatter 本身。

## 标签分类法
[为领域定义 10-20 个顶级标签。在使用新标签之前，先在此处添加。]

AI/ML 示例：
- 模型：model, architecture, benchmark, training
- 人物/组织：person, company, lab, open-source
- 技术：optimization, fine-tuning, inference, alignment, data
- 元：comparison, timeline, controversy, prediction

规则：页面上的每个标签都必须出现在此分类法中。如果需要新标签，先在此处添加，然后使用。这可以防止标签泛滥。

## 页面阈值
- **创建页面**：当一个实体/概念出现在 2 个以上来源中，或是一个来源的核心内容时
- **添加到现有页面**：当一个来源提及已涵盖的内容时
- **不创建页面**：对于提及、次要细节或领域之外的内容
- **拆分页面**：当页面超过约 200 行时 — 拆分为子主题并交叉链接
- **归档页面**：当内容完全被取代时 — 移动到 `_archive/`，并从索引中移除

## 实体页面
每个重要实体一个页面。包括：
- 概述 / 它是什么
- 关键事实和日期
- 与其他实体的关系（[[wikilinks]]）
- 来源引用

## 概念页面
每个概念或主题一个页面。包括：
- 定义 / 解释
- 当前知识状态
- 开放性问题或辩论
- 相关概念（[[wikilinks]]）

## 比较页面
并排分析。包括：
- 比较的内容和原因
- 比较维度（首选表格格式）
- 结论或综合
- 来源

## 更新策略
当新信息与现有内容冲突时：
1. 检查日期 — 较新的来源通常取代较旧的来源
2. 如果确实矛盾，注明两种立场及其日期和来源
3. 在 frontmatter 中标记矛盾：`contradictions: [page-name]`
4. 在一致性检查报告中标记以供用户审查
```
### index.md 模板

索引按类型分节。每个条目占一行：wikilink + 摘要。

```markdown
# Wiki 索引

> 内容目录。每个 wiki 页面按其类型列出，并附有一行摘要。
> 首先阅读此索引，以查找任何查询的相关页面。
> 最后更新：YYYY-MM-DD | 总页数：N

## 实体
<!-- 在节内按字母顺序排列 -->

## 概念

## 对比

## 查询
```

**扩展规则：** 当任何节超过 50 个条目时，按首字母或子域将其拆分为子节。当索引总条目数超过 200 个时，创建一个 `_meta/topic-map.md`，按主题对页面进行分组，以便更快地导航。

### log.md 模板

```markdown
# Wiki 日志

> 所有 wiki 操作的时间顺序记录。仅追加。
> 格式：`## [YYYY-MM-DD] action | subject`
> 操作：ingest, update, query, lint, create, archive, delete
> 当此文件超过 500 个条目时，轮换：重命名为 log-YYYY.md，重新开始。

## [YYYY-MM-DD] create | Wiki 已初始化
- 领域：[domain]
- 使用 SCHEMA.md、index.md、log.md 创建了结构
```

## 核心操作

### 1. 摄取

当用户提供来源（URL、文件、粘贴文本）时，将其整合到 wiki 中：

① **捕获原始来源：**
   - URL → 使用 `web_extract` 获取 markdown，保存到 `raw/articles/`
   - PDF → 使用 `web_extract`（处理 PDF），保存到 `raw/papers/`
   - 粘贴的文本 → 保存到适当的 `raw/` 子目录
   - 描述性地命名文件：`raw/articles/karpathy-llm-wiki-2026.md`
   - **添加原始 frontmatter**（`source_url`、`ingested`、正文的 `sha256`）。
     当重新摄取同一 URL 时：重新计算 sha256，与存储的值进行比较 —— 如果相同则跳过，如果不同则标记漂移并更新。这在每次重新摄取时执行成本足够低，并能捕获静默的源更改。

② **与用户讨论要点** —— 什么有趣，什么对该领域重要。（在自动化/定时任务上下文中跳过此步骤 —— 直接进行。）

③ **检查已存在的内容** —— 搜索 index.md 并使用 `search_files` 查找提及的实体/概念的现有页面。这是成长型 wiki 和一堆重复内容之间的区别。

④ **编写或更新 wiki 页面：**
   - **新实体/概念：** 仅当它们满足 SCHEMA.md 中的页面阈值（2+ 个来源提及，或对一个来源至关重要）时才创建页面
   - **现有页面：** 添加新信息，更新事实，更新 `updated` 日期。
     当新信息与现有内容矛盾时，遵循更新策略。
   - **交叉引用：** 每个新的或更新的页面必须通过 `[[wikilinks]]` 链接到至少 2 个其他页面。检查现有页面是否链接回来。
   - **标签：** 仅使用 SCHEMA.md 分类法中的标签
   - **来源：** 在综合了 3+ 个来源的页面上，将 `^[raw/articles/source.md]` 标记附加到其声明可追溯到特定来源的段落。
   - **置信度：** 对于观点性强、变化快或单一来源的声明，在 frontmatter 中设置 `confidence: medium` 或 `low`。除非声明在多个来源中得到充分支持，否则不要标记为 `high`。

⑤ **更新导航：**
   - 将新页面添加到 `index.md` 的正确节下，按字母顺序排列
   - 更新索引标题中的“总页数”计数和“最后更新”日期
   - 追加到 `log.md`：`## [YYYY-MM-DD] ingest | Source Title`
   - 在日志条目中列出每个创建或更新的文件

⑥ **报告更改内容** —— 向用户列出每个创建或更新的文件。

单个来源可以触发 5-15 个 wiki 页面的更新。这是正常且期望的 —— 这是复合效应。

### 2. 查询

当用户询问有关 wiki 领域的问题时：

① **阅读 `index.md`** 以识别相关页面。
② **对于拥有 100+ 页面的 wiki**，也使用 `search_files` 在所有 `.md` 文件中搜索关键术语 —— 仅靠索引可能会遗漏相关内容。
③ **使用 `read_file` 阅读相关页面**。
④ **根据编译的知识综合答案**。引用你引用的 wiki 页面：“基于 [[page-a]] 和 [[page-b]]...”
⑤ **将有价值的答案归档** —— 如果答案是一个实质性的比较、深度探索或新颖的综合，则在 `queries/` 或 `comparisons/` 中创建一个页面。不要归档琐碎的查找 —— 只归档那些重新推导会很痛苦的答案。
⑥ **在 log.md 中更新查询**以及是否已归档。

### 3. 代码检查

当用户要求对 wiki 进行代码检查、健康检查或审计时：

① **孤立页面：** 查找没有来自其他页面的入站 `[[wikilinks]]` 的页面。
```python
# 为此使用 execute_code —— 对所有 wiki 页面进行程序化扫描
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# 扫描 entities/、concepts/、comparisons/、queries/ 中的所有 .md 文件
# 提取所有 [[wikilinks]] —— 构建入站链接映射
# 入站链接为零的页面是孤立页面
```

② **损坏的 wikilinks：** 查找指向不存在的页面的 `[[links]]`。

③ **索引完整性：** 每个 wiki 页面都应出现在 `index.md` 中。将文件系统与索引条目进行比较。

④ **Frontmatter 验证：** 每个 wiki 页面必须具有所有必填字段（title、created、updated、type、tags、sources）。标签必须在分类法中。

⑤ **陈旧内容：** 其 `updated` 日期比提及相同实体的最新来源早 >90 天的页面。

⑥ **矛盾：** 同一主题但声明冲突的页面。查找共享标签/实体但陈述不同事实的页面。将所有带有 `contested: true` 或 `contradictions:` frontmatter 的页面呈现给用户审查。

⑦ **质量信号：** 列出带有 `confidence: low` 的页面以及任何仅引用单一来源但未设置置信度字段的页面 —— 这些是需要寻找佐证或降级为 `confidence: medium` 的候选页面。

⑧ **来源漂移：** 对于 `raw/` 中每个带有 `sha256:` frontmatter 的文件，重新计算哈希值并标记不匹配。不匹配表明原始文件已被编辑（不应该发生 —— raw/ 是不可变的）或从后来已更改的 URL 摄取。这不是硬错误，但值得报告。
⑨ **页面大小：** 标记超过 200 行的页面——作为拆分的候选。

⑩ **标签审计：** 列出所有使用中的标签，标记任何不在 SCHEMA.md 分类法中的标签。

⑪ **日志轮转：** 如果 log.md 超过 500 条条目，则轮转它。

⑫ **报告发现的问题**，包含具体的文件路径和建议的操作，按严重程度分组（损坏链接 > 孤立页面 > 来源漂移 > 争议页面 > 陈旧内容 > 样式问题）。

⑬ **追加到 log.md：** `## [YYYY-MM-DD] lint | 发现 N 个问题`

## 使用 Wiki

### 搜索

```bash
# 按内容查找页面
search_files "transformer" path="$WIKI" file_glob="*.md"

# 按文件名查找页面
search_files "*.md" target="files" path="$WIKI"

# 按标签查找页面
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# 最近活动
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### 批量导入

当一次性导入多个来源时，批量处理更新：
1. 首先读取所有来源
2. 识别所有来源中的所有实体和概念
3. 为所有这些内容检查现有页面（一次搜索遍历，而非 N 次）
4. 在一次遍历中创建/更新页面（避免冗余更新）
5. 最后一次性更新 index.md
6. 写一条涵盖整个批处理的日志条目

### 归档

当内容被完全取代或领域范围发生变化时：
1. 如果 `_archive/` 目录不存在，则创建它
2. 将页面移动到 `_archive/` 并保留其原始路径（例如，`_archive/entities/old-page.md`）
3. 从 `index.md` 中移除
4. 更新任何链接到它的页面——将 wikilink 替换为纯文本 + "（已归档）"
5. 记录归档操作

### Obsidian 集成

Wiki 目录开箱即用，可作为 Obsidian 知识库：
- `[[wikilinks]]` 渲染为可点击的链接
- 图谱视图可视化知识网络
- YAML frontmatter 支持 Dataview 查询
- `raw/assets/` 文件夹存放通过 `![[image.png]]` 引用的图片

为获得最佳效果：
- 将 Obsidian 的附件文件夹设置为 `raw/assets/`
- 在 Obsidian 设置中启用 "Wikilinks"（通常默认开启）
- 安装 Dataview 插件以进行查询，例如 `TABLE tags FROM "entities" WHERE contains(tags, "company")`

如果同时使用 Obsidian 技能和此技能，请将 `OBSIDIAN_VAULT_PATH` 设置为与 wiki 路径相同的目录。

### Obsidian Headless（服务器和无头机器）

在没有显示器的机器上，使用 `obsidian-headless` 替代桌面应用。
它通过 Obsidian Sync 同步知识库，无需 GUI——非常适合在服务器上运行的 Agent，它们写入 wiki，而 Obsidian 桌面端在另一台设备上读取。

**设置：**
```bash
# 需要 Node.js 22+
npm install -g obsidian-headless

# 登录（需要具有 Sync 订阅的 Obsidian 账户）
ob login --email <email> --password '<password>'

# 为 wiki 创建一个远程知识库
ob sync-create-remote --name "LLM Wiki"

# 将 wiki 目录连接到知识库
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# 初始同步
ob sync

# 持续同步（前台运行——使用 systemd 进行后台运行）
ob sync --continuous
```

**通过 systemd 进行持续后台同步：**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# 启用 linger 以便同步在注销后继续运行：
sudo loginctl enable-linger $USER
```

这允许 Agent 在服务器上写入 `~/wiki`，而您可以在笔记本电脑/手机上的 Obsidian 中浏览同一个知识库——更改会在几秒钟内出现。

## 常见陷阱

- **切勿修改 `raw/` 中的文件**——来源是不可变的。修正应放在 wiki 页面中。
- **始终先定位**——在新会话中进行任何操作之前，先阅读 SCHEMA + index + 最近的日志。跳过此步骤会导致重复和遗漏交叉引用。
- **始终更新 index.md 和 log.md**——跳过此步骤会使 wiki 退化。这些是导航的支柱。
- **不要为偶然提及创建页面**——遵循 SCHEMA.md 中的页面阈值。一个名字在脚注中出现一次并不值得创建一个实体页面。
- **不要创建没有交叉引用的页面**——孤立的页面是不可见的。每个页面必须至少链接到其他 2 个页面。
- **Frontmatter 是必需的**——它支持搜索、过滤和过时检测。
- **标签必须来自分类法**——自由形式的标签会退化为噪音。首先将新标签添加到 SCHEMA.md，然后再使用它们。
- **保持页面可快速浏览**——一个 wiki 页面应在 30 秒内可读。拆分超过 200 行的页面。将详细分析移至专门的深度分析页面。
- **大规模更新前先询问**——如果一次导入会触及 10 个以上的现有页面，请先与用户确认范围。
- **轮转日志**——当 log.md 超过 500 条条目时，将其重命名为 `log-YYYY.md` 并重新开始。Agent 应在 lint 期间检查日志大小。
- **明确处理矛盾**——不要静默覆盖。用日期注明两种说法，在 frontmatter 中标记，并标记供用户审查。

## 相关工具

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) 是一个 Node.js CLI，它将来源编译成一个具有相同 Karpathy 灵感的概念 wiki。它与 Obsidian 兼容，因此希望使用计划任务/CLI 驱动的编译流水线的用户可以将其指向此技能维护的同一个知识库。权衡：它负责页面生成（取代了 Agent 在页面创建上的判断），并且针对小型语料库进行了调整。当您希望 Agent 参与循环策展时，请使用此技能；当您希望批量编译源目录时，请使用 llmwiki。