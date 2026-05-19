---
title: "宝玉文章插图师 — 文章插图：类型 × 风格 × 调色板一致性"
sidebar_label: "宝玉文章插图师"
description: "文章插图：类型 × 风格 × 调色板一致性"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉文章插图师

文章插图：类型 × 风格 × 调色板一致性。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-article-illustrator` |
| 版本 | `1.57.0` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `article-illustration`, `creative`, `image-generation` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 文章插图师

改编自 [baoyu-article-illustrator](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态系统。

分析文章，识别插图位置，生成具有**类型 × 风格 × 调色板**一致性的图像。

## 何时使用

当用户要求为文章配图、为文章添加图片、为内容生成插图，或使用诸如“为文章配图”、“illustrate article”或“add images”等短语时触发此技能。用户提供一篇文章（文件路径或粘贴的内容），并可选择性地指定类型、风格、调色板或密度。

## 三个维度

| 维度 | 控制内容 | 示例 |
|-----------|----------|----------|
| **类型** | 信息结构 | infographic, scene, flowchart, comparison, framework, timeline |
| **风格** | 渲染方式 | notion, warm, minimal, blueprint, watercolor, elegant |
| **调色板** | 配色方案（可选） | macaron, warm, neon — 覆盖风格的默认颜色 |

自由组合：`type=infographic, style=vector-illustration, palette=macaron`。

或使用预设：`edu-visual` → 一次性指定类型 + 风格 + 调色板。参见 [style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/style-presets.md)。

## 类型

| 类型 | 最适合 |
|------|----------|
| `infographic` | 数据、指标、技术性内容 |
| `scene` | 叙述性、情感性内容 |
| `flowchart` | 流程、工作流 |
| `comparison` | 并列对比、选项 |
| `framework` | 模型、架构 |
| `timeline` | 历史、演变 |

## 风格

参见 [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/styles.md) 了解核心风格、完整图库以及类型 × 风格兼容性。

## 输出结构

<!-- ascii-guard-ignore -->
```
{output-dir}/
├── source-{slug}.{ext}    # 仅适用于粘贴的内容
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```
<!-- ascii-guard-ignore-end -->

**默认输出目录**：

| 输入 | 输出目录 | Markdown 插入路径 |
|-------|------------------|----------------------|
| 文章文件路径 | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| 粘贴的内容 | `illustrations/{topic-slug}/` (当前工作目录) | `illustrations/{topic-slug}/NN-{type}-{slug}.png` |

如果用户要求不同的布局（例如，图片与文章并排放置，或使用 `illustrations/` 子目录），请遵循其要求。

**Slug**：2-4 个单词，kebab-case。**冲突处理**：追加 `-YYYYMMDD-HHMMSS`。

## 核心原则

- **可视化概念，而非隐喻** — 如果文章使用了隐喻（例如，“电锯切西瓜”），请图示其背后的概念，而非字面图像。
- **标签使用文章数据** — 使用文章中的实际数字、术语和引语，而非通用占位符。
- **提示词文件是可复现性记录** — 在生成任何图像之前，每个插图必须在 `prompts/` 下保存一个提示词文件。
- **移除机密信息** — 在将任何内容写入磁盘之前，扫描源内容中的 API 密钥、Token 或凭据。

## 工作流

```
- [ ] 步骤 1：检测参考图像（如果提供）
- [ ] 步骤 2：分析内容
- [ ] 步骤 3：确认设置（使用 clarify 工具，一次一个问题）
- [ ] 步骤 4：生成大纲
- [ ] 步骤 5：生成提示词
- [ ] 步骤 6：生成图像 (image_generate)
- [ ] 步骤 7：最终完成
```

### 步骤 1：检测参考图像

如果用户提供了参考图像（内联粘贴的路径、附件或 URL）：

1. 对于每个参考图像，调用 `vision_analyze`，传入路径/URL 以及询问风格、调色板、构图和主题的问题。通过 `write_file` 将返回的描述记录在 `{output-dir}/references/NN-ref-{slug}.md` 中。
2. **不要**尝试通过 `write_file` / `read_file` 复制二进制文件 — 这些工具仅处理文本。如果你想为记录保留本地副本，请使用 `terminal` (`cp "$src" "{output-dir}/references/NN-ref-{slug}.{ext}"`)。技能本身永远不需要读取二进制文件；它基于视觉描述工作。
3. 由于 `image_generate` 不接受图像输入，视觉描述是在步骤 5 中嵌入到提示词中的内容。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-1-detect-reference-images)。

### 步骤 2：分析

| 分析项 | 输出 |
|----------|--------|
| 内容类型 | 技术性 / 教程 / 方法论 / 叙述性 |
| 目的 | 信息 / 可视化 / 想象 |
| 核心论点 | 2-5 个要点 |
| 位置 | 插图能增加价值的地方 |

读取源文件（文件路径 → `read_file`，或粘贴的文本）并使用 `write_file` 将分析结果写入 `{output-dir}/analysis.md`。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-2-analyze)。

### 步骤 3：确认设置

使用 `clarify` 工具。由于 `clarify` 一次处理一个问题，请先问最重要的问题。跳过用户请求中已明确答案的任何问题。

| 顺序 | 问题 | 选项 |
|-------|----------|---------|
| Q1 | **预设或类型** | [推荐预设], [备选预设], 或手动：infographic, scene, flowchart, comparison, framework, timeline, mixed |
| Q2 | **密度** | minimal (1-2), balanced (3-5), per-section (推荐), rich (6+) |
| Q3 | **风格** *(如果在 Q1 中选择了预设则跳过)* | [推荐], minimal-flat, sci-fi, hand-drawn, editorial, scene, poster |
| Q4 | **调色板** *(可选)* | Default (风格颜色), macaron, warm, neon |
| Q5 | **语言** *(仅在文章语言不明确时询问)* | 文章语言 / 用户语言 |

不要连续问超过 2-3 个 `clarify` 问题。如果用户已在请求中指定了这些内容，则完全跳过。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-3-confirm-settings)。

### 步骤 4：生成大纲 → `outline.md`

使用 `write_file` 保存 `{output-dir}/outline.md`，包含 frontmatter（类型、密度、风格、调色板、image_count）以及每个插图的条目：

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what to show]
**Filename**: 01-infographic-concept-name.png
```

完整模板：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-4-generate-outline)。

### 步骤 5：生成提示词

**阻塞性要求**：在生成任何图像之前，每个插图必须有一个保存的提示词文件 — 提示词文件是可复现性记录。

对于每个插图：

1. 根据 [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/prompt-construction.md) 创建提示词文件。
2. 使用 `write_file` 保存到 `{output-dir}/prompts/NN-{type}-{slug}.md`，包含 YAML frontmatter。
3. 提示词**必须**使用特定于类型的模板，包含结构化部分（ZONES / LABELS / COLORS / STYLE / ASPECT）。
4. LABELS **必须**包含文章特定的数据：实际数字、术语、指标、引语。
5. 根据提示词 frontmatter 处理参考图像（`direct`/`style`/`palette`）— 对于 `direct` 用法，在提示词中嵌入参考图像的文本描述（因为 `image_generate` 不接受参考图像输入）。

### 步骤 6：生成图像

对于每个提示词文件：

1. 调用 `image_generate(prompt=..., aspect_ratio=...)`。`image_generate` 返回一个包含图像 URL 的 JSON 结果；它**不会**写入磁盘，也**不接受**输出路径。
2. 将提示词的 `ASPECT` 映射到 `image_generate` 的枚举值：`16:9` → `landscape`, `9:16` → `portrait`, `1:1` → `square`。自定义比例 → 最接近的命名宽高比。
3. 通过 `terminal` 将返回的 URL 下载到 `{output-dir}/NN-{type}-{slug}.png`（例如 `curl -sSL -o "{output-dir}/NN-{type}-{slug}.png" "{url}"`）。
4. 生成失败时，自动重试一次。

注意：底层的图像生成后端是用户配置的（默认：FAL FLUX 2 Klein 9B），Agent **无法**通过 `image_generate` 选择。不要在提示词中写入模型名称并期望它能路由。

### 步骤 7：最终完成

在对应段落后插入 `![description](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/{relative-path}/NN-{type}-{slug}.png)`。替代文本：使用文章语言的简洁描述。

报告：

```
文章插图完成！
文章：[路径] | 类型：[类型] | 密度：[级别] | 风格：[风格] | 调色板：[调色板或默认]
图像：已生成 X/N 张
```

## 修改

| 操作 | 步骤 |
|--------|-------|
| 编辑 | 更新提示词 → 重新生成 → 更新引用 |
| 添加 | 位置 → 提示词 → 生成 → 更新大纲 → 插入 |
| 删除 | 删除文件 → 移除引用 → 更新大纲 |

## 参考资料

| 文件 | 内容 |
|------|---------|
| [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md) | 详细流程 |
| [references/usage.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/usage.md) | 调用示例 |
| [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/styles.md) | 风格图库 + 调色板图库 |
| [references/style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/style-presets.md) | 预设快捷方式（类型 + 风格 + 调色板） |
| [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/prompt-construction.md) | 提示词模板 |

## 常见陷阱

1. **数据完整性至关重要** — 永远不要总结、转述或更改源数据统计信息。“73% increase” 保持为 “73% increase”。
2. **移除机密信息** — 在将任何内容包含到输出文件之前，扫描源内容中的 API 密钥、Token 或凭据。
3. **不要字面化地图示隐喻** — 可视化其背后的概念。
4. **提示词文件是强制性的** — 没有保存的提示词文件，就不能生成图像。该文件让你以后可以重新生成或切换后端。
5. **`image_generate` 宽高比** — 该工具支持 `landscape`、`portrait` 和 `square`。自定义比例映射到最接近的选项。
6. **`image_generate` 返回 URL，而非本地文件** — 在将本地图像路径插入文章之前，始终通过 `terminal` (`curl`) 下载。
7. **Agent 无法选择后端** — `image_generate` 使用用户配置的任何模型（默认：FAL FLUX 2 Klein 9B）。不要在提示词中写入 `"use <model> to generate this"` 并期望它能路由。