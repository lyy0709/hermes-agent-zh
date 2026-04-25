---
title: "Memento Flashcards — 间隔重复闪卡系统"
sidebar_label: "Memento Flashcards"
description: "间隔重复闪卡系统"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Memento Flashcards

间隔重复闪卡系统。可从事实或文本创建卡片，通过 Agent 评分的自由文本答案与闪卡聊天，从 YouTube 字幕生成测验，使用自适应调度复习到期卡片，并以 CSV 格式导出/导入卡组。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/memento-flashcards` 安装 |
| 路径 | `optional-skills/productivity/memento-flashcards` |
| 版本 | `1.0.0` |
| 作者 | Memento AI |
| 许可证 | MIT |
| 平台 | macos, linux |
| 标签 | `Education`, `Flashcards`, `Spaced Repetition`, `Learning`, `Quiz`, `YouTube` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Memento Flashcards — 间隔重复闪卡技能

## 概述

Memento 为您提供一个基于文件的本地闪卡系统，具有间隔重复调度功能。
用户可以通过自由文本回答与闪卡聊天，并由 Agent 在安排下一次复习前对回答进行评分。
当用户想要以下操作时使用它：

- **记住一个事实** — 将任何陈述转换为问答闪卡
- **使用间隔重复学习** — 使用自适应间隔和 Agent 评分的自由文本答案复习到期卡片
- **从 YouTube 视频生成测验** — 获取字幕并生成 5 个问题的测验
- **管理卡组** — 将卡片组织到集合中，导出/导入 CSV

所有卡片数据都保存在单个 JSON 文件中。无需外部 API 密钥 — 您（Agent）直接生成闪卡内容和测验问题。

Memento Flashcards 面向用户的响应风格：
- 仅使用纯文本。在回复用户时不要使用 Markdown 格式。
- 保持复习和测验反馈简洁、中立。避免额外的表扬、鼓励或冗长的解释。

## 何时使用

当用户想要以下操作时使用此技能：
- 将事实保存为闪卡以供日后复习
- 使用间隔重复复习到期卡片
- 从 YouTube 视频字幕生成测验
- 导入、导出、检查或删除闪卡数据

不要将此技能用于一般问答、编程帮助或非记忆任务。

## 快速参考

| 用户意图 | 操作 |
|---|---|
| "记住 X" / "将此保存为闪卡" | 生成问答卡片，调用 `memento_cards.py add` |
| 发送事实但未提及闪卡 | 询问"想让我将此保存为 Memento 闪卡吗？" — 仅在确认后创建 |
| "创建一张闪卡" | 询问问题、答案、集合；调用 `memento_cards.py add` |
| "复习我的卡片" | 调用 `memento_cards.py due`，逐一呈现卡片 |
| "就 [YouTube URL] 测验我" | 调用 `youtube_quiz.py fetch VIDEO_ID`，生成 5 个问题，调用 `memento_cards.py add-quiz` |
| "导出我的卡片" | 调用 `memento_cards.py export --output PATH` |
| "从 CSV 导入卡片" | 调用 `memento_cards.py import --file PATH --collection NAME` |
| "显示我的统计信息" | 调用 `memento_cards.py stats` |
| "删除一张卡片" | 调用 `memento_cards.py delete --id ID` |
| "删除一个集合" | 调用 `memento_cards.py delete-collection --collection NAME` |

## 卡片存储

卡片存储在以下路径的 JSON 文件中：

```
~/.hermes/skills/productivity/memento-flashcards/data/cards.json
```

**切勿直接编辑此文件。** 始终使用 `memento_cards.py` 子命令。该脚本处理原子写入（写入临时文件，然后重命名）以防止损坏。

该文件在首次使用时自动创建。

## 流程

### 从事实创建卡片

### 激活规则

并非每个事实陈述都应成为闪卡。使用此三层检查：

1. **明确意图** — 用户提及 "memento"、"flashcard"、"记住这个"、"保存此卡片"、"添加卡片" 或类似明确请求闪卡的措辞 → **直接创建卡片**，无需确认。
2. **隐含意图** — 用户发送事实陈述但未提及闪卡（例如，"光速是 299,792 公里/秒"） → **先询问**："想让我将此保存为 Memento 闪卡吗？" 仅在用户确认后创建卡片。
3. **无意图** — 消息是编程任务、问题、指令、正常对话或任何明显不是要记忆的事实 → **完全不要激活此技能**。让其他技能或默认行为处理。

当激活被确认后（第 1 层直接确认，第 2 层在用户确认后），生成闪卡：

**步骤 1：** 将陈述转换为问答对。内部使用此格式：

```
将事实陈述转换为正面-背面对。
返回恰好两行：
Q: <问题文本>
A: <答案文本>

陈述: "{statement}"
```

规则：
- 问题应测试对关键事实的记忆
- 答案应简洁直接

**步骤 2：** 调用脚本存储卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add \
  --question "What year did World War 2 end?" \
  --answer "1945" \
  --collection "History"
```

如果用户未指定集合，则使用 `"General"` 作为默认值。

脚本输出 JSON 确认创建的卡片。

### 手动创建卡片

当用户明确要求创建闪卡时，询问他们：
1. 问题（卡片正面）
2. 答案（卡片背面）
3. 集合名称（可选 — 默认为 `"General"`）

然后如上所述调用 `memento_cards.py add`。

### 复习到期卡片

当用户想要复习时，获取所有到期卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

这将返回一个 JSON 数组，其中包含 `next_review_at <= now` 的卡片。如果需要集合过滤器：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due --collection "History"
```
**复习流程（自由文本评分）：**

以下是你必须遵循的**确切**交互模式示例。用户回答后，你进行评分，告诉他们正确答案，然后对卡片进行评级。

**示例交互：**

> **Agent:** 柏林墙是哪一年倒塌的？
>
> **User:** 1991
>
> **Agent:** 不太对。柏林墙于1989年倒塌。下次复习是明天。
> *(agent 调用：memento_cards.py rate --id ABC --rating hard --user-answer "1991")*
>
> 下一个问题：第一个在月球上行走的人是谁？

**规则：**

1. 只显示问题。等待用户回答。
2. 收到他们的答案后，与预期答案进行比较并评分：
   - **correct** → 用户答对了关键事实（即使措辞不同）
   - **partial** → 方向正确但缺少核心细节
   - **incorrect** → 错误或离题
3. **你必须告诉用户正确答案以及他们的表现。** 保持简短并使用纯文本。使用以下格式：
   - correct: "正确。答案：{answer}。7天后下次复习。"
   - partial: "接近了。答案：{answer}。{他们遗漏了什么}。3天后下次复习。"
   - incorrect: "不太对。答案：{answer}。明天下次复习。"
4. 然后调用评级命令：correct→easy, partial→good, incorrect→hard。
5. 然后显示下一个问题。

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```

**切勿跳过第3步。** 在继续之前，用户必须始终看到正确答案和反馈。

如果没有到期的卡片，告诉用户："目前没有需要复习的卡片。请稍后再来查看！"

**退休覆盖：** 在任何时候，用户都可以说"retire this card"来永久将其从复习中移除。对此使用 `--rating retire`。

### 间隔重复算法

评级决定了下次复习的间隔：

| 评级 | 间隔 | ease_streak | 状态变化 |
|---|---|---|---|
| **hard** | +1 天 | 重置为 0 | 保持学习中 |
| **good** | +3 天 | 重置为 0 | 保持学习中 |
| **easy** | +7 天 | +1 | 如果 ease_streak >= 3 → 已退休 |
| **retire** | 永久 | 重置为 0 | → 已退休 |

- **learning**: 卡片在活跃轮换中
- **retired**: 卡片不会出现在复习中（用户已掌握或手动退休）
- 连续三次"easy"评级会自动退休一张卡片

### YouTube 测验生成

当用户发送 YouTube URL 并想要测验时：

**步骤 1：** 从 URL 中提取视频 ID（例如，从 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 中提取 `dQw4w9WgXcQ`）。

**步骤 2：** 获取字幕：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/youtube_quiz.py fetch VIDEO_ID
```

这将返回 `{"title": "...", "transcript": "..."}` 或一个错误。

如果脚本报告 `missing_dependency`，告诉用户安装它：
```bash
pip install youtube-transcript-api
```

**步骤 3：** 根据字幕生成 5 个测验问题。使用以下规则：

```
你正在为一期播客节目创建一个 5 个问题的测验。
只返回一个恰好包含 5 个对象的 JSON 数组。
每个对象必须包含 'question' 和 'answer' 键。

选择标准：
- 优先考虑重要的、令人惊讶的或基础性的事实。
- 跳过填充内容、明显细节和需要大量上下文的事实。
- 永远不要返回是/否问题。
- 永远不要只问日期。

问题规则：
- 每个问题必须测试一个离散的事实。
- 使用清晰、明确的措辞。
- 优先使用 What, Who, How many, Which。
- 避免开放式的 Describe 或 Explain 提示。

答案规则：
- 每个答案必须少于 240 个字符。
- 以答案本身开头，而不是前言。
- 仅在需要时添加最少的澄清细节。
```

使用字幕的前 15,000 个字符作为上下文。自己生成问题（你是 LLM）。

**步骤 4：** 验证输出是有效的 JSON，恰好包含 5 个项目，每个项目都有非空的 `question` 和 `answer` 字符串。如果验证失败，重试一次。

**步骤 5：** 存储测验卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add-quiz \
  --video-id "VIDEO_ID" \
  --questions '[{"question":"...","answer":"..."},...]' \
  --collection "Quiz - Episode Title"
```

脚本通过 `video_id` 去重——如果该视频的卡片已存在，则跳过创建并报告现有卡片。

**步骤 6：** 使用相同的自由文本评分流程逐个呈现问题：
1. 显示"问题 1/5: ..."并等待用户的答案。**永远不要**包含答案或任何关于揭示答案的提示。
2. 等待用户用自己的话回答
3. 使用评分提示对用户的答案进行评分（参见"复习到期卡片"部分）
4. **重要：在**做任何其他事情之前，**你必须**回复用户并提供反馈。显示评分、正确答案以及卡片下次到期时间。**不要**默默地跳到下一个问题。保持简短并使用纯文本。示例："不太对。答案：{answer}。明天下次复习。"
5. **显示反馈后**，调用评级命令，然后在同一条消息中显示下一个问题：
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```
6. 重复。每个答案在下一个问题之前**必须**收到可见的反馈。

### 导出/导入 CSV

**导出：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py export \
  --output ~/flashcards.csv
```

生成一个 3 列的 CSV：`question,answer,collection`（无标题行）。

**导入：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py import \
  --file ~/flashcards.csv \
  --collection "Imported"
```

读取包含以下列的 CSV：question, answer，以及可选的 collection（第 3 列）。如果缺少 collection 列，则使用 `--collection` 参数。

### 统计信息

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
```
返回包含以下字段的 JSON：
- `total`：卡片总数
- `learning`：处于活跃轮换中的卡片数
- `retired`：已掌握的卡片数
- `due_now`：当前需要复习的卡片数
- `collections`：按集合名称细分的统计

## 注意事项

- **切勿直接编辑 `cards.json`** — 始终使用脚本子命令以避免文件损坏
- **转录失败** — 部分 YouTube 视频没有英文字幕或字幕功能被禁用；请告知用户并建议更换视频
- **可选依赖** — `youtube_quiz.py` 需要 `youtube-transcript-api`；如果缺失，请告知用户运行 `pip install youtube-transcript-api`
- **大型导入** — 包含数千行的 CSV 导入可以正常工作，但 JSON 输出可能较为冗长；请为用户总结结果
- **视频 ID 提取** — 支持 `youtube.com/watch?v=ID` 和 `youtu.be/ID` 两种 URL 格式

## 验证

直接验证辅助脚本：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add --question "Capital of France?" --answer "Paris" --collection "General"
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

如果从仓库检出目录进行测试，请运行：

```bash
pytest tests/skills/test_memento_cards.py tests/skills/test_youtube_quiz.py -q
```

Agent 级别验证：
- 开始一次复习，确认反馈是纯文本、简洁的，并且在展示下一张卡片前总是包含正确答案
- 运行一次 YouTube 问答流程，确认每个答案在下一个问题出现前都收到了可见的反馈