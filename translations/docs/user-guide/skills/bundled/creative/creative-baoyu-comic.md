---
title: "宝玉漫画 — 知识漫画：教育、传记、教程"
sidebar_label: "宝玉漫画"
description: "知识漫画：教育、传记、教程"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉漫画

知识漫画：教育、传记、教程。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-comic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 标签 | `comic`, `knowledge-comic`, `creative`, `image-generation` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 知识漫画创作器

改编自 [baoyu-comic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态系统。

创建原创知识漫画，支持灵活的艺术风格 × 氛围组合。

## 使用时机

当用户要求创建知识/教育漫画、传记漫画、教程漫画，或使用诸如“知识漫画”、“教育漫画”或“Logicomix风格”等术语时触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可选择指定艺术风格、氛围、布局、宽高比或语言。

## 参考图像

Hermes 的 `image_generate` 工具是**仅提示词**的——它接受文本提示词和宽高比，并返回图像 URL。它**不**接受参考图像。当用户提供参考图像时，用它来**提取文本特征**，并嵌入到每一页的提示词中：

**输入**：当用户提供文件路径时接受（或在对话中粘贴图像）。
- 文件路径 → 复制到 `refs/NN-ref-{slug}.{ext}`，与漫画输出放在一起以便溯源
- 粘贴的图像没有路径 → 通过 `clarify` 向用户询问路径，或作为文本后备方案口头提取风格特征
- 无参考图像 → 跳过此部分

**使用模式**（每个参考图像）：

| 用途 | 效果 |
|-------|--------|
| `style` | 提取风格特征（线条处理、纹理、情绪）并附加到每一页的提示词正文中 |
| `palette` | 提取十六进制颜色并附加到每一页的提示词正文中 |
| `scene` | 提取场景构图或主题说明并附加到相关页面 |

**当存在参考图像时，记录在每个页面的提示词 frontmatter 中**：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: style
    traits: "muted earth tones, soft-edged ink wash, low-contrast backgrounds"
```

角色一致性由 `characters/characters.md`（在第 3 步中编写）中的**文本描述**驱动，这些描述被内联嵌入到每个页面提示词中（第 5 步）。第 7.1 步中生成的可选 PNG 角色表是面向人工的审查产物，不是 `image_generate` 的输入。

## 选项

### 视觉维度

| 选项 | 值 | 描述 |
|--------|--------|-------------|
| 艺术风格 | ligne-claire (默认), manga, realistic, ink-brush, chalk, minimalist | 艺术风格 / 渲染技术 |
| 氛围 | neutral (默认), warm, dramatic, romantic, energetic, vintage, action | 情绪 / 氛围 |
| 布局 | standard (默认), cinematic, dense, splash, mixed, webtoon, four-panel | 分格排列 |
| 宽高比 | 3:4 (默认, 纵向), 4:3 (横向), 16:9 (宽屏) | 页面宽高比 |
| 语言 | auto (默认), zh, en, ja, 等 | 输出语言 |
| 参考图像 | 文件路径 | 用于风格/调色板特征提取的参考图像（不传递给图像模型）。参见上文的[参考图像](#参考图像)。 |

### 部分工作流选项

| 选项 | 描述 |
|--------|-------------|
| 仅分镜 | 仅生成分镜，跳过提示词和图像 |
| 仅提示词 | 生成分镜 + 提示词，跳过图像 |
| 仅图像 | 从现有的提示词目录生成图像 |
| 重新生成 N | 仅重新生成特定页面（例如 `3` 或 `2,5,8`） |

详情：[references/partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md)

### 艺术风格、氛围与预设目录

- **艺术风格** (6): `ligne-claire`, `manga`, `realistic`, `ink-brush`, `chalk`, `minimalist`。完整定义见 `references/art-styles/<style>.md`。
- **氛围** (7): `neutral`, `warm`, `dramatic`, `romantic`, `energetic`, `vintage`, `action`。完整定义见 `references/tones/<tone>.md`。
- **预设** (5) 具有超越简单艺术风格+氛围的特殊规则：

  | 预设 | 等效组合 | 特点 |
  |--------|-----------|------|
  | `ohmsha` | manga + neutral | 视觉隐喻，无大头照，小工具揭示 |
  | `wuxia` | ink-brush + action | 气功效果，战斗视觉，氛围感 |
  | `shoujo` | manga + romantic | 装饰元素，眼部细节，浪漫桥段 |
  | `concept-story` | manga + warm | 视觉符号系统，成长弧线，对话与动作平衡 |
  | `four-panel` | minimalist + neutral + four-panel layout | 起承转合结构，黑白 + 点缀色，简笔画角色 |

  完整规则见 `references/presets/<preset>.md` —— 选择预设时加载该文件。

- **兼容性矩阵**和**内容信号 → 预设**表位于 [references/auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md)。在第 2 步推荐组合之前请阅读它。

## 文件结构

输出目录：`comic/{topic-slug}/`
- Slug：来自主题的 2-4 个单词 kebab-case（例如 `alan-turing-bio`）
- 冲突：附加时间戳（例如 `turing-story-20260118-143052`）

**内容**：
| 文件 | 描述 |
|------|-------------|
| `source-{slug}.md` | 保存的源内容（kebab-case slug 与输出目录匹配） |
| `analysis.md` | 内容分析 |
| `storyboard.md` | 带有分格分解的分镜 |
| `characters/characters.md` | 角色定义 |
| `characters/characters.png` | 角色参考表（从 `image_generate` 下载） |
| `prompts/NN-{cover\|page}-[slug].md` | 生成提示词 |
| `NN-{cover\|page}-[slug].png` | 生成的图像（从 `image_generate` 下载） |
| `refs/NN-ref-{slug}.{ext}` | 用户提供的参考图像（可选，用于溯源） |
## 语言处理

**检测优先级**：
1. 用户指定的语言（显式选项）
2. 用户对话语言
3. 源内容语言

**规则**：所有交互均使用用户的输入语言：
- 故事板大纲和场景描述
- 图像生成提示词
- 用户选择选项和确认信息
- 进度更新、问题、错误、摘要

技术术语保持英文。

## 工作流

### 进度清单

```
漫画进度：
- [ ] 步骤 1：设置与分析
  - [ ] 1.1 分析内容
  - [ ] 1.2 检查现有目录
- [ ] 步骤 2：确认 - 风格与选项 ⚠️ 必需
- [ ] 步骤 3：生成故事板 + 角色
- [ ] 步骤 4：审阅大纲（条件性）
- [ ] 步骤 5：生成提示词
- [ ] 步骤 6：审阅提示词（条件性）
- [ ] 步骤 7：生成图像
  - [ ] 7.1 生成角色设定图（如果需要）→ `characters/characters.png`
  - [ ] 7.2 生成页面（提示词中嵌入角色描述）
- [ ] 步骤 8：完成报告
```

### 流程

```
输入 → 分析 → [检查现有？] → [确认：风格 + 审阅] → 故事板 → [审阅？] → 提示词 → [审阅？] → 图像 → 完成
```

### 步骤摘要

| 步骤 | 操作 | 关键输出 |
|------|--------|------------|
| 1.1 | 分析内容 | `analysis.md`, `source-{slug}.md` |
| 1.2 | 检查现有目录 | 处理冲突 |
| 2 | 确认风格、焦点、受众、审阅 | 用户偏好 |
| 3 | 生成故事板 + 角色 | `storyboard.md`, `characters/` |
| 4 | 审阅大纲（如果请求） | 用户批准 |
| 5 | 生成提示词 | `prompts/*.md` |
| 6 | 审阅提示词（如果请求） | 用户批准 |
| 7.1 | 生成角色设定图（如果需要） | `characters/characters.png` |
| 7.2 | 生成页面 | `*.png` 文件 |
| 8 | 完成报告 | 摘要 |

### 用户问题

使用 `clarify` 工具来确认选项。由于 `clarify` 一次处理一个问题，请先问最重要的问题，然后按顺序进行。完整的步骤 2 问题集请参见 [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。

**超时处理（关键）**：`clarify` 可能返回 `"The user did not provide a response within the time limit. Use your best judgement to make the choice and proceed."` —— 这**不是**用户同意所有默认设置的许可。

- 将其视为**仅针对该单个问题**的默认选择。继续按顺序询问剩余的步骤 2 问题；每个问题都是一个独立的确认点。
- **在您的下一条消息中向用户明确显示默认选择**，以便他们有机会纠正：例如，`"风格：已默认设置为 ohmsha 预设（clarify 超时）。请说一个词来切换。"` —— 未报告的默认选择与从未询问过是无法区分的。
- 在一个超时后，**不要**将步骤 2 折叠成一个单一的“使用所有默认值”的流程。如果用户确实不在，那么对于所有五个问题他们都会同样不在 —— 但当他们返回时，他们可以纠正可见的默认值，而无法纠正不可见的默认值。

### 步骤 7：图像生成

所有图像渲染都使用 Hermes 内置的 `image_generate` 工具。其模式只接受 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）；它**返回一个 URL**，而不是本地文件。因此，每个生成的页面或角色设定图都必须下载到输出目录。

**提示词文件要求（硬性规定）**：在调用 `image_generate` **之前**，将每个图像的完整、最终提示词写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。提示词文件是可重复性的记录。

**宽高比映射** —— 故事板中的 `aspect_ratio` 字段映射到 `image_generate` 的格式如下：

| 故事板比例 | `image_generate` 格式 |
|------------------|-------------------------|
| `3:4`, `9:16`, `2:3` | `portrait` |
| `4:3`, `16:9`, `3:2` | `landscape` |
| `1:1` | `square` |

**下载步骤** —— 每次 `image_generate` 调用后：
1. 从工具结果中读取 URL
2. 使用**绝对**输出路径获取图像字节，例如：
   `curl -fsSL "<url>" -o /abs/path/to/comic/<slug>/NN-page-<slug>.png`
3. 在继续处理下一页之前，验证该确切路径下的文件存在且非空

**切勿依赖 shell 的当前工作目录（CWD）持久性来指定 `-o` 路径。** 终端工具的持久 shell 的 CWD 可能在批次之间发生变化（会话过期、`TERMINAL_LIFETIME_SECONDS`、失败的 `cd` 导致您处于错误的目录）。`curl -o relative/path.png` 是一个无声的隐患：如果 CWD 已经漂移，文件会悄无声息地保存在其他地方。**始终向 `-o` 传递一个完全限定的绝对路径**，或者向终端工具传递 `workdir=<abs path>`。2026 年 4 月事件：一个 10 页漫画的第 06-09 页被保存到了仓库根目录，而不是 `comic/<slug>/`，因为批次 3 继承了批次 2 的陈旧 CWD，而 `curl -o 06-page-skills.png` 写入了错误的目录。然后 Agent 花费了几轮时间声称文件存在于它们不存在的地方。

**7.1 角色设定图** —— 当漫画是多页且角色重复出现时，生成它（到 `characters/characters.png`，宽高比 `landscape`）。对于简单的预设（例如，四格极简主义）或单页漫画，则跳过。在调用 `image_generate` 之前，`characters/characters.md` 处的提示词文件必须存在。渲染的 PNG 是一个**面向人类的审阅工件**（以便用户可以直观地验证角色设计），也是后续重新生成或手动编辑提示词的参考 —— 它**不**驱动步骤 7.2。页面提示词在步骤 5 中已经根据 `characters/characters.md` 中的**文本描述**编写完成；`image_generate` 无法接受图像作为视觉输入。

**7.2 页面** —— 每个页面的提示词在调用 `image_generate` **之前**必须已经存在于 `prompts/NN-{cover|page}-[slug].md`。因为 `image_generate` 仅接受提示词，角色一致性是通过**在步骤 5 期间，将角色描述（源自 `characters/characters.md`）内联嵌入到每个页面提示词中**来强制执行的。无论是否在 7.1 中生成 PNG 设定图，都会统一进行这种嵌入；PNG 仅作为审阅/重新生成的辅助工具。
**备份规则**：现有的 `prompts/…md` 和 `…png` 文件 → 在重新生成前，使用 `-backup-YYYYMMDD-HHMMSS` 后缀重命名。

完整的逐步工作流（分析、故事板、审查节点、重新生成变体）：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。

## 参考资料

**核心模板**：
- [analysis-framework.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/analysis-framework.md) - 深度内容分析
- [character-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/character-template.md) - 角色定义格式
- [storyboard-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/storyboard-template.md) - 故事板结构
- [ohmsha-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/ohmsha-guide.md) - Ohmsha 漫画规范

**风格定义**：
- `references/art-styles/` - 艺术风格（清晰线条、漫画、写实、水墨、粉笔、极简）
- `references/tones/` - 色调（中性、温暖、戏剧性、浪漫、活力、复古、动作）
- `references/presets/` - 包含特殊规则的预设（ohmsha、武侠、少女、概念故事、四格）
- `references/layouts/` - 布局（标准、电影感、密集、跨页、混合、条漫、四格）

**工作流**：
- [workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md) - 完整工作流详情
- [auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md) - 内容信号分析
- [partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md) - 部分工作流选项

## 页面修改

| 操作 | 步骤 |
|--------|-------|
| **编辑** | **首先更新提示词文件** → 重新生成图像 → 下载新的 PNG |
| **添加** | 在指定位置创建提示词 → 嵌入角色描述后生成 → 重新编号后续文件 → 更新故事板 |
| **删除** | 删除文件 → 重新编号后续文件 → 更新故事板 |

**重要提示**：更新页面时，**务必先**更新提示词文件 (`prompts/NN-{cover|page}-[slug].md`)，然后再重新生成。这确保了更改被记录且可复现。

## 常见陷阱

- 图像生成：每页 10-30 秒；失败时自动重试一次
- **务必下载** `image_generate` 返回的 URL 到本地 PNG 文件 —— 下游工具（以及用户的审查）期望在输出目录中找到文件，而不是临时的 URL
- **为 `curl -o` 使用绝对路径** —— 切勿依赖跨批次持久 shell 的当前工作目录。一个无声的陷阱：文件会保存在错误的目录，随后在预期路径执行 `ls` 会显示为空。请参见步骤 7 的“下载步骤”。
- 对敏感的公众人物使用风格化的替代方案
- **步骤 2 需要确认** - 不要跳过
- **步骤 4/6 是条件性的** - 仅当用户在步骤 2 中要求时才执行
- **步骤 7.1 角色设定表** - 推荐用于多页漫画，对于简单预设是可选的。PNG 文件是用于审查/重新生成的辅助工具；页面提示词（在步骤 5 中编写）使用的是 `characters/characters.md` 中的文本描述，而不是 PNG 图像。`image_generate` 不接受图像作为视觉输入
- **清除机密信息** — 在写入任何输出文件之前，扫描源内容中的 API 密钥、Token 或凭据