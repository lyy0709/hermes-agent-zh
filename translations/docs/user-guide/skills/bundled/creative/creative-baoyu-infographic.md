---
title: "宝玉信息图 — 信息图：21 种布局 × 21 种风格 (信息图, 可视化)"
sidebar_label: "宝玉信息图"
description: "信息图：21 种布局 × 21 种风格 (信息图, 可视化)"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉信息图

信息图：21 种布局 × 21 种风格 (信息图, 可视化).

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-infographic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 标签 | `infographic`, `visual-summary`, `creative`, `image-generation` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 信息图生成器

改编自 [baoyu-infographic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态系统。

两个维度：**布局**（信息结构） × **风格**（视觉美学）。可自由组合任意布局与任意风格。

## 使用时机

当用户要求创建信息图、视觉摘要、信息图表，或使用诸如“信息图”、“可视化”或“高密度信息大图”等术语时触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可选择指定布局、风格、宽高比或语言。

## 选项

| 选项 | 值 |
|--------|--------|
| 布局 | 21 种选项（见布局图库），默认：bento-grid |
| 风格 | 21 种选项（见风格图库），默认：craft-handmade |
| 宽高比 | 预设：landscape (16:9), portrait (9:16), square (1:1)。自定义：任意 W:H 比例（例如 3:4, 4:3, 2.35:1） |
| 语言 | en, zh, ja 等 |

## 布局图库

| 布局 | 最适合 |
|--------|----------|
| `linear-progression` | 时间线、流程、教程 |
| `binary-comparison` | A 对 B、前后对比、利弊分析 |
| `comparison-matrix` | 多因素比较 |
| `hierarchical-layers` | 金字塔、优先级层次 |
| `tree-branching` | 分类、分类法 |
| `hub-spoke` | 中心概念与相关项 |
| `structural-breakdown` | 分解视图、剖面图 |
| `bento-grid` | 多主题、概览（默认） |
| `iceberg` | 表面与隐藏方面 |
| `bridge` | 问题-解决方案 |
| `funnel` | 转化、筛选 |
| `isometric-map` | 空间关系 |
| `dashboard` | 指标、关键绩效指标 |
| `periodic-table` | 分类集合 |
| `comic-strip` | 叙事、序列 |
| `story-mountain` | 情节结构、张力弧线 |
| `jigsaw` | 相互关联的部分 |
| `venn-diagram` | 重叠概念 |
| `winding-roadmap` | 旅程、里程碑 |
| `circular-flow` | 循环、重复过程 |
| `dense-modules` | 高密度模块、数据丰富的指南 |

完整定义：`references/layouts/<layout>.md`

## 风格图库

| 风格 | 描述 |
|-------|-------------|
| `craft-handmade` | 手绘、纸艺（默认） |
| `claymation` | 3D 粘土人偶、定格动画 |
| `kawaii` | 日式可爱、柔和色彩 |
| `storybook-watercolor` | 柔和绘画、奇幻风格 |
| `chalkboard` | 黑板粉笔画 |
| `cyberpunk-neon` | 霓虹发光、未来感 |
| `bold-graphic` | 漫画风格、半色调 |
| `aged-academia` | 复古科学、深褐色调 |
| `corporate-memphis` | 扁平矢量、鲜艳色彩 |
| `technical-schematic` | 蓝图、工程图 |
| `origami` | 折纸、几何形状 |
| `pixel-art` | 复古 8 位像素 |
| `ui-wireframe` | 灰度界面线框图 |
| `subway-map` | 交通路线图 |
| `ikea-manual` | 极简线条艺术 |
| `knolling` | 有序平铺 |
| `lego-brick` | 乐高积木搭建 |
| `pop-laboratory` | 蓝图网格、坐标标记、实验室精度 |
| `morandi-journal` | 手绘涂鸦、温暖的莫兰迪色调 |
| `retro-pop-grid` | 1970 年代复古波普艺术、瑞士网格、粗轮廓线 |
| `hand-drawn-edu` | 马卡龙柔和色、手绘抖动线条、简笔画人物 |

完整定义：`references/styles/<style>.md`

## 推荐组合

| 内容类型 | 布局 + 风格 |
|--------------|----------------|
| 时间线/历史 | `linear-progression` + `craft-handmade` |
| 分步指南 | `linear-progression` + `ikea-manual` |
| A 对 B | `binary-comparison` + `corporate-memphis` |
| 层级结构 | `hierarchical-layers` + `craft-handmade` |
| 重叠概念 | `venn-diagram` + `craft-handmade` |
| 转化漏斗 | `funnel` + `corporate-memphis` |
| 循环过程 | `circular-flow` + `craft-handmade` |
| 技术说明 | `structural-breakdown` + `technical-schematic` |
| 指标仪表盘 | `dashboard` + `corporate-memphis` |
| 教育图表 | `bento-grid` + `chalkboard` |
| 旅程路线 | `winding-roadmap` + `storybook-watercolor` |
| 分类集合 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 潮流指南 | `dense-modules` + `retro-pop-grid` |
| 教育图表 | `hub-spoke` + `hand-drawn-edu` |
| 流程教程 | `linear-progression` + `hand-drawn-edu` |

默认：`bento-grid` + `craft-handmade`

## 关键词快捷方式

当用户输入包含以下关键词时，**自动选择**关联的布局，并在步骤 3 中将关联风格作为首要推荐。跳过基于内容的布局推断。

如果快捷方式有 **提示词备注**，则将其作为附加的风格指令追加到生成的提示词（步骤 5）中。

| 用户关键词 | 布局 | 推荐风格 | 默认宽高比 | 提示词备注 |
|--------------|--------|--------------------|----------------|--------------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid` | portrait | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | landscape | 极简主义：干净的画布、充足的留白、无复杂背景纹理。仅使用简单的卡通元素和图标。 |

## 输出结构

<!-- ascii-guard-ignore -->
```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```
<!-- ascii-guard-ignore-end -->

Slug：由主题生成的 2-4 个单词的 kebab-case。冲突时追加 `-YYYYMMDD-HHMMSS`。

## 核心原则

- 忠实保留源数据 — 不进行摘要或改写（但在包含到输出中之前，**务必去除任何凭据、API 密钥、Token 或秘密信息**）
- 在构建内容结构前定义学习目标
- 为视觉传达构建结构（标题、标签、视觉元素）

## 工作流

### 步骤 1：分析内容

**加载参考**：从本技能读取 `references/analysis-framework.md`。

1.  保存源内容（文件路径或粘贴 → 使用 `write_file` 写入 `source.md`）
    -   **备份规则**：如果 `source.md` 已存在，则重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2.  分析：主题、数据类型、复杂度、语气、受众
3.  检测源语言和用户语言
4.  从用户输入中提取设计指令
5.  将分析保存到 `analysis.md`
    -   **备份规则**：如果 `analysis.md` 已存在，则重命名为 `analysis-backup-YYYYMMDD-HHMMSS.md`

详细格式请参见 `references/analysis-framework.md`。

### 步骤 2：生成结构化内容 → `structured-content.md`

将内容转换为信息图结构：
1.  标题和学习目标
2.  包含以下内容的章节：关键概念、内容（逐字）、视觉元素、文本标签
3.  数据点（所有统计数据/引文完全复制）
4.  来自用户的设计指令

**规则**：仅使用 Markdown。不添加新信息。忠实保留数据。从输出中去除任何凭据或秘密信息。

详细格式请参见 `references/structured-content-template.md`。

### 步骤 3：推荐组合

**3.1 首先检查关键词快捷方式**：如果用户输入匹配**关键词快捷方式**表中的关键词，则自动选择关联的布局，并优先将关联风格作为首要推荐。跳过基于内容的布局推断。

**3.2 否则**，基于以下因素推荐 3-5 个布局×风格组合：
- 数据结构 → 匹配布局
- 内容语气 → 匹配风格
- 受众期望
- 用户设计指令

### 步骤 4：确认选项

使用 `clarify` 工具与用户确认选项。由于 `clarify` 一次处理一个问题，请先问最重要的问题：

**Q1 — 组合**：展示 3 个以上的布局×风格组合及其理由。请用户选择一个。

**Q2 — 宽高比**：询问宽高比偏好（landscape/portrait/square 或自定义 W:H）。

**Q3 — 语言**（仅当源语言 ≠ 用户语言时）：询问文本内容应使用哪种语言。

### 步骤 5：生成提示词 → `prompts/infographic.md`

**备份规则**：如果 `prompts/infographic.md` 已存在，则重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

**加载参考**：从 `references/layouts/<layout>.md` 读取选定的布局定义，从 `references/styles/<style>.md` 读取选定的风格定义。

组合：
1.  来自 `references/layouts/<layout>.md` 的布局定义
2.  来自 `references/styles/<style>.md` 的风格定义
3.  来自 `references/base-prompt.md` 的基础模板
4.  来自步骤 2 的结构化内容
5.  所有文本使用确认的语言

**宽高比解析**，用于 `{{ASPECT_RATIO}}`：
-   命名预设 → 比例字符串：landscape→`16:9`, portrait→`9:16`, square→`1:1`
-   自定义 W:H 比例 → 按原样使用（例如 `3:4`, `4:3`, `2.35:1`）

使用 `write_file` 将组装的提示词保存到 `prompts/infographic.md`。

### 步骤 6：生成图像

使用 `image_generate` 工具和步骤 5 中组装的提示词。

-   将宽高比映射到 image_generate 的格式：`16:9` → `landscape`, `9:16` → `portrait`, `1:1` → `square`
-   对于自定义比例，选择最接近的命名宽高比
-   失败时自动重试一次
-   将生成的图像 URL/路径保存到输出目录

### 步骤 7：输出摘要

报告：主题、布局、风格、宽高比、语言、输出路径、创建的文件。

## 参考文件

-   `references/analysis-framework.md` — 分析方法论
-   `references/structured-content-template.md` — 内容格式
-   `references/base-prompt.md` — 提示词模板
-   `references/layouts/<layout>.md` — 21 种布局定义
-   `references/styles/<style>.md` — 21 种风格定义

## 常见陷阱

1.  **数据完整性至关重要** — 切勿对源统计数据进行摘要、转述或更改。“增长 73%”必须保持为“增长 73%”，而不是“显著增长”。
2.  **去除秘密信息** — 在将任何源内容包含到输出文件之前，务必扫描其中的 API 密钥、Token 或凭据。
3.  **每个章节一个信息** — 信息图的每个章节应传达一个清晰的概念。章节过载会降低可读性。
4.  **风格一致性** — 必须将参考文件中的风格定义一致地应用于整个信息图。不要混合风格。
5.  **image_generate 宽高比** — 该工具仅支持 `landscape`、`portrait` 和 `square`。自定义比例如 `3:4` 应映射到最接近的选项（例如 portrait）。