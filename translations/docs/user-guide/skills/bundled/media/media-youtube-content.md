---
title: "Youtube Content — YouTube 转录文本转摘要、推文串、博客文章"
sidebar_label: "Youtube Content"
description: "YouTube 转录文本转摘要、推文串、博客文章"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Youtube Content

将 YouTube 转录文本转换为摘要、推文串、博客文章。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/youtube-content` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# YouTube 内容工具

## 使用时机

当用户分享 YouTube URL 或视频链接、要求总结视频、请求转录文本，或希望从任何 YouTube 视频中提取并重新格式化内容时使用。将转录文本转换为结构化内容（章节、摘要、推文串、博客文章）。

从 YouTube 视频中提取转录文本并将其转换为有用的格式。

## 设置

```bash
pip install youtube-transcript-api
```

## 辅助脚本

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。该脚本接受任何标准的 YouTube URL 格式、短链接 (youtu.be)、短视频、嵌入链接、直播链接或原始的 11 字符视频 ID。

```bash
# 输出包含元数据的 JSON
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 纯文本（适合管道传输进行进一步处理）
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# 带时间戳
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# 特定语言，带后备链
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## 输出格式

获取转录文本后，根据用户要求进行格式化：

- **章节**：按主题转换分组，输出带时间戳的章节列表
- **摘要**：整个视频的简洁 5-10 句概述
- **章节摘要**：每个章节附带简短段落摘要
- **推文串**：Twitter/X 推文串格式 — 编号帖子，每条不超过 280 字符
- **博客文章**：包含标题、章节和关键要点的完整文章
- **引用**：带时间戳的著名引用

### 示例 — 章节输出

```
00:00 引言 — 主持人以问题陈述开场
03:45 背景 — 先前工作及现有解决方案的不足
12:20 核心方法 — 对所提方法的逐步讲解
24:10 结果 — 基准比较和关键要点
31:55 问答 — 关于可扩展性和后续步骤的观众提问
```

## 工作流程

1.  **获取**：使用辅助脚本配合 `--text-only --timestamps` 参数获取转录文本。
2.  **验证**：确认输出非空且为预期语言。如果为空，则重试时不带 `--language` 参数以获取任何可用的转录文本。如果仍然为空，则告知用户该视频可能已禁用转录。
3.  **分块（如需要）**：如果转录文本超过约 50K 字符，则将其分割成重叠的块（约 40K 字符，重叠 2K 字符），并在合并前总结每个块。
4.  **转换**：转换为请求的输出格式。如果用户未指定格式，则默认为摘要。
5.  **验证**：在呈现前重新阅读转换后的输出，检查连贯性、时间戳正确性和完整性。

## 错误处理

- **转录功能已禁用**：告知用户；建议他们检查视频页面上是否有可用的字幕。
- **视频私密/不可用**：转达错误信息并请用户验证 URL。
- **无匹配语言**：重试时不带 `--language` 参数以获取任何可用的转录文本，然后向用户说明实际语言。
- **依赖项缺失**：运行 `pip install youtube-transcript-api` 并重试。