---
title: "Meme Generation — 通过选择模板并使用 Pillow 叠加文本生成真实的梗图"
sidebar_label: "Meme Generation"
description: "通过选择模板并使用 Pillow 叠加文本生成真实的梗图"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Meme Generation

通过选择模板并使用 Pillow 叠加文本来生成真实的梗图。生成实际的 .png 梗图文件。

## 技能元数据

| | |
|---|---|
| 来源 | Optional — 使用 `hermes skills install official/creative/meme-generation` 安装 |
| 路径 | `optional-skills/creative/meme-generation` |
| 版本 | `2.0.0` |
| 作者 | adanaleycio |
| 许可证 | MIT |
| 标签 | `creative`, `memes`, `humor`, `images` |
| 相关技能 | [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art), `generative-widgets` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Meme Generation

根据主题生成实际的梗图。选择模板、编写标题，并使用文本叠加渲染出真实的 .png 文件。

## 使用时机

- 用户要求你制作或生成梗图
- 用户想要关于特定主题、情境或烦恼的梗图
- 用户说“meme this”或类似的话

## 可用模板

该脚本支持 **imgflip 上约 100 个流行模板中的任何一个**（通过名称或 ID），外加 10 个经过手动调整文本位置的精选模板。

### 精选模板（自定义文本位置）

| ID | 名称 | 字段 | 最适合 |
|----|------|--------|----------|
| `this-is-fine` | This is Fine | top, bottom | 混乱、否认 |
| `drake` | Drake Hotline Bling | reject, approve | 拒绝/偏好 |
| `distracted-boyfriend` | Distracted Boyfriend | distraction, current, person | 诱惑、优先级转移 |
| `two-buttons` | Two Buttons | left, right, person | 艰难选择 |
| `expanding-brain` | Expanding Brain | 4 levels | 递进式讽刺 |
| `change-my-mind` | Change My Mind | statement | 热门观点 |
| `woman-yelling-at-cat` | Woman Yelling at Cat | woman, cat | 争论 |
| `one-does-not-simply` | One Does Not Simply | top, bottom | 看似简单实则困难的事情 |
| `grus-plan` | Gru's Plan | step1-3, realization | 适得其反的计划 |
| `batman-slapping-robin` | Batman Slapping Robin | robin, batman | 否定糟糕的想法 |

### 动态模板（来自 imgflip API）

任何不在精选列表中的模板都可以通过名称或 imgflip ID 使用。这些模板会获得智能的默认文本定位（2个字段用顶部/底部，3个及以上字段则均匀分布）。使用以下命令搜索：
```bash
python "$SKILL_DIR/scripts/generate_meme.py" --search "disaster"
```

## 流程

### 模式 1：经典模板（默认）

1.  阅读用户主题并识别核心动态（混乱、困境、偏好、讽刺等）
2.  选择最匹配的模板。使用“最适合”列，或使用 `--search` 搜索。
3.  为每个字段编写简短的标题（每个字段最多 8-12 个词，越短越好）。
4.  找到技能的脚本目录：
    ```
    SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
    ```
5.  运行生成器：
    ```bash
    python "$SKILL_DIR/scripts/generate_meme.py" <template_id> /tmp/meme.png "caption 1" "caption 2" ...
    ```
6.  使用 `MEDIA:/tmp/meme.png` 返回图像

### 模式 2：自定义 AI 图像（当 `image_generate` 可用时）

当没有经典模板合适，或者用户想要原创内容时使用此模式。

1.  首先编写标题。
2.  使用 `image_generate` 创建与梗图概念匹配的场景。**不要**在图像提示词中包含任何文本——文本将由脚本添加。仅描述视觉场景。
3.  从 `image_generate` 结果的 URL 中找到生成的图像路径。如果需要，将其下载到本地路径。
4.  使用 `--image` 运行脚本以叠加文本，选择一种模式：
    - **叠加**（文本直接覆盖在图像上，白色带黑色描边）：
      ```bash
      python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png /tmp/meme.png "top text" "bottom text"
      ```
    - **条带**（图像上方/下方添加黑色条带，显示白色文本——更清晰，始终可读）：
      ```bash
      python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png --bars /tmp/meme.png "top text" "bottom text"
      ```
    当图像内容繁杂/细节丰富，直接叠加文本难以阅读时，使用 `--bars`。
5.  **使用视觉模型验证**（如果 `vision_analyze` 可用）：检查结果是否良好：
    ```
    vision_analyze(image_url="/tmp/meme.png", question="Is the text legible and well-positioned? Does the meme work visually?")
    ```
    如果视觉模型标记出问题（文本难以阅读、位置不佳等），尝试另一种模式（在叠加和条带之间切换）或重新生成场景。
6.  使用 `MEDIA:/tmp/meme.png` 返回图像

## 示例

**"凌晨两点调试生产环境"：**
```bash
python generate_meme.py this-is-fine /tmp/meme.png "SERVERS ARE ON FIRE" "This is fine"
```

**"在睡觉和再看一集之间选择"：**
```bash
python generate_meme.py drake /tmp/meme.png "Getting 8 hours of sleep" "One more episode at 3 AM"
```

**"周一早晨的各个阶段"：**
```bash
python generate_meme.py expanding-brain /tmp/meme.png "Setting an alarm" "Setting 5 alarms" "Sleeping through all alarms" "Working from bed"
```

## 列出模板

要查看所有可用模板：
```bash
python generate_meme.py --list
```

## 注意事项

-   保持标题**简短**。带有长文本的梗图看起来很糟糕。
-   确保文本参数的数量与模板的字段数量匹配。
-   选择符合笑话结构的模板，而不仅仅是主题。
-   不要生成仇恨、辱骂或针对个人的内容。
-   脚本在首次下载后会将模板图像缓存到 `scripts/.cache/` 目录。

## 验证

输出正确的条件是：
-   在输出路径创建了 .png 文件
-   文本在模板上清晰可读（白色带黑色描边）
-   笑话成立——标题符合模板的预期结构
-   文件可以通过 MEDIA: 路径传递