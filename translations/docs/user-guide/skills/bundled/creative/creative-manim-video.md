---
title: "Manim 视频 — Manim CE 动画：3Blue1Brown 风格数学/算法视频"
sidebar_label: "Manim 视频"
description: "Manim CE 动画：3Blue1Brown 风格数学/算法视频"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Manim 视频

Manim CE 动画：3Blue1Brown 风格数学/算法视频。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/manim-video` |
| 版本 | `1.0.0` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Manim 视频制作流水线

## 使用时机

当用户请求以下内容时使用：动画解释、数学动画、概念可视化、算法演示、技术讲解、3Blue1Brown 风格视频，或任何包含几何/数学内容的程序化动画。使用 Manim Community Edition 创建 3Blue1Brown 风格的讲解视频、算法可视化、方程推导、架构图和数据故事。

## 创意标准

这是教育电影。每一帧都在教学。每一个动画都在揭示结构。

**在编写任何一行代码之前**，先阐明叙事弧线。这个动画纠正了什么误解？"顿悟时刻"是什么？什么样的视觉故事能将观众从困惑带到理解？用户的提示词只是一个起点——要用教学抱负去解读它。

**几何先于代数。** 先展示形状，再展示方程。视觉记忆比符号记忆编码更快。当观众先看到几何模式再看到公式时，方程会让人觉得是应得的。

**首次渲染的卓越性不容妥协。** 输出必须在视觉上清晰、美学上协调，无需修改轮次。如果某些内容看起来杂乱、时间安排不当或像"AI 生成的幻灯片"，那就是错误的。

**不透明度分层引导注意力。** 永远不要以全亮度显示所有内容。主要元素为 1.0，上下文元素为 0.4，结构元素（坐标轴、网格）为 0.15。大脑按层次处理视觉显著性。

**呼吸空间。** 每个动画之后都需要 `self.wait()`。观众需要时间来吸收刚刚出现的内容。永远不要匆忙地从一个动画跳到下一个。关键揭示后的 2 秒暂停永远不会是浪费。

**统一的视觉语言。** 所有场景共享一个调色板、一致的字体大小、匹配的动画速度。一个技术上正确但每个场景使用随机不同颜色的视频是美学上的失败。

## 先决条件

运行 `scripts/setup.sh` 以验证所有依赖项。需要：Python 3.10+、Manim Community Edition v0.20+ (`pip install manim`)、LaTeX（Linux 上为 `texlive-full`，macOS 上为 `mactex`）和 ffmpeg。参考文档针对 Manim CE v0.20.1 测试。

## 模式

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **概念讲解** | 主题/概念 | 带有几何直觉的动画解释 | `references/scene-planning.md` |
| **方程推导** | 数学表达式 | 逐步动画证明 | `references/equations.md` |
| **算法可视化** | 算法描述 | 带有数据结构的逐步执行 | `references/graphs-and-data.md` |
| **数据故事** | 数据/指标 | 动画图表、比较、计数器 | `references/graphs-and-data.md` |
| **架构图** | 系统描述 | 组件构建与连接 | `references/mobjects.md` |
| **论文讲解** | 研究论文 | 关键发现和方法的动画 | `references/scene-planning.md` |
| **3D 可视化** | 3D 概念 | 旋转曲面、参数曲线、空间几何 | `references/camera-and-3d.md` |

## 技术栈

每个项目一个 Python 脚本。无需浏览器、Node.js 或 GPU。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | Manim Community Edition | 场景渲染、动画引擎 |
| 数学 | LaTeX (texlive/MiKTeX) | 通过 `MathTex` 渲染方程 |
| 视频 I/O | ffmpeg | 场景拼接、格式转换、音频混流 |
| TTS | ElevenLabs / Qwen3-TTS (可选) | 旁白配音 |

## 流水线

```
规划 --> 编码 --> 渲染 --> 拼接 --> 音频 (可选) --> 审查
```

1.  **规划** — 编写 `plan.md`，包含叙事弧线、场景列表、视觉元素、调色板、旁白脚本
2.  **编码** — 编写 `script.py`，每个场景一个类，每个类可独立渲染
3.  **渲染** — `manim -ql script.py Scene1 Scene2 ...` 用于草稿，`-qh` 用于生产
4.  **拼接** — 使用 ffmpeg 将场景片段连接成 `final.mp4`
5.  **音频** (可选) — 通过 ffmpeg 添加旁白和/或背景音乐。参见 `references/rendering.md`
6.  **审查** — 渲染预览静帧，对照计划验证，调整

## 项目结构

```
项目名称/
  plan.md                # 叙事弧线、场景分解
  script.py              # 所有场景在一个文件中
  concat.txt             # ffmpeg 场景列表
  final.mp4              # 拼接后的输出
  media/                 # 由 Manim 自动生成
    videos/script/480p15/
```

## 创意指导

### 调色板

| 调色板 | 背景 | 主色 | 辅色 | 强调色 | 使用场景 |
|---------|-----------|---------|-----------|--------|----------|
| **经典 3B1B** | `#1C1C1C` | `#58C4DD` (蓝色) | `#83C167` (绿色) | `#FFFF00` (黄色) | 通用数学/计算机科学 |
| **温暖学术** | `#2D2B55` | `#FF6B6B` | `#FFD93D` | `#6BCB77` | 平易近人 |
| **霓虹科技** | `#0A0A0A` | `#00F5FF` | `#FF00FF` | `#39FF14` | 系统、架构 |
| **单色** | `#1A1A2E` | `#EAEAEA` | `#888888` | `#FFFFFF` | 极简主义 |

### 动画速度

| 上下文 | run_time | 之后 self.wait() |
|---------|----------|-------------------|
| 标题/介绍出现 | 1.5秒 | 1.0秒 |
| 关键方程揭示 | 2.0秒 | 2.0秒 |
| 变换/变形 | 1.5秒 | 1.5秒 |
| 辅助标签 | 0.8秒 | 0.5秒 |
| 淡出清理 | 0.5秒 | 0.3秒 |
| "顿悟时刻"揭示 | 2.5秒 | 3.0秒 |
### 排版比例

| 角色 | 字体大小 | 用途 |
|------|-----------|-------|
| 标题 | 48 | 场景标题、开场文字 |
| 标题 | 36 | 场景内的章节标题 |
| 正文 | 30 | 说明性文字 |
| 标签 | 24 | 注释、坐标轴标签 |
| 说明文字 | 20 | 副标题、小字 |

### 字体

**所有文本使用等宽字体。** Manim 的 Pango 渲染器在所有尺寸下使用比例字体都会产生错误的字距调整。完整建议请参阅 `references/visual-design.md`。

```python
MONO = "Menlo"  # 在文件顶部定义一次

Text("Fourier Series", font_size=48, font=MONO, weight=BOLD)  # 标题
Text("n=1: sin(x)", font_size=20, font=MONO)                  # 标签
MathTex(r"\nabla L")                                            # 数学公式（使用 LaTeX）
```

为保证可读性，最小 `font_size=18`。

### 按场景变化

切勿对所有场景使用相同的配置。对于每个场景：
- **使用调色板中不同的主色调**
- **不同的布局** — 不要总是将所有内容居中
- **不同的动画入场方式** — 在 Write、FadeIn、GrowFromCenter、Create 之间变化
- **不同的视觉权重** — 有些场景密集，有些稀疏

## 工作流

### 步骤 1：规划 (plan.md)

在编写任何代码之前，先写 `plan.md`。完整的模板请参阅 `references/scene-planning.md`。

### 步骤 2：编码 (script.py)

每个场景一个类。每个场景都是独立可渲染的。

```python
from manim import *

BG = "#1C1C1C"
PRIMARY = "#58C4DD"
SECONDARY = "#83C167"
ACCENT = "#FFFF00"
MONO = "Menlo"

class Scene1_Introduction(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Why Does This Work?", font_size=48, color=PRIMARY, weight=BOLD, font=MONO)
        self.add_subcaption("Why does this work?", duration=2)
        self.play(Write(title), run_time=1.5)
        self.wait(1.0)
        self.play(FadeOut(title), run_time=0.5)
```

关键模式：
- **每个动画都添加字幕**：`self.add_subcaption("text", duration=N)` 或在 `self.play()` 中使用 `subcaption="text"`
- **在文件顶部定义共享的颜色常量**，以保证跨场景一致性
- **在每个场景中设置 `self.camera.background_color`**
- **干净地退出** — 在场景结束时淡出所有 mobject：`self.play(FadeOut(Group(*self.mobjects)))`

### 步骤 3：渲染

```bash
manim -ql script.py Scene1_Introduction Scene2_CoreConcept  # 草稿
manim -qh script.py Scene1_Introduction Scene2_CoreConcept  # 成品
```

### 步骤 4：拼接

```bash
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1_Introduction.mp4'
file 'media/videos/script/480p15/Scene2_CoreConcept.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

### 步骤 5：审阅

```bash
manim -ql --format=png -s script.py Scene2_CoreConcept  # 预览静态图
```

## 关键实现注意事项

### LaTeX 使用原始字符串
```python
# 错误：MathTex("\frac{1}{2}")
# 正确：
MathTex(r"\frac{1}{2}")
```

### 边缘文本的 buff >= 0.5
```python
label.to_edge(DOWN, buff=0.5)  # 永远不要 < 0.5
```

### 替换文本前先淡出
```python
self.play(ReplacementTransform(note1, note2))  # 不要在顶部 Write(note2)
```

### 切勿动画化未添加的 Mobject
```python
self.play(Create(circle))  # 必须先添加
self.play(circle.animate.set_color(RED))  # 然后动画化
```

## 性能目标

| 质量 | 分辨率 | 帧率 | 速度 |
|---------|-----------|-----|-------|
| `-ql` (草稿) | 854x480 | 15 | 5-15秒/场景 |
| `-qm` (中等) | 1280x720 | 30 | 15-60秒/场景 |
| `-qh` (成品) | 1920x1080 | 60 | 30-120秒/场景 |

始终在 `-ql` 下迭代。仅在最终输出时渲染 `-qh`。

## 参考资料

| 文件 | 内容 |
|------|----------|
| `references/animations.md` | 核心动画、速率函数、组合、`.animate` 语法、时序模式 |
| `references/mobjects.md` | 文本、形状、VGroup/Group、定位、样式、自定义 mobject |
| `references/visual-design.md` | 12 条设计原则、不透明度分层、布局模板、调色板 |
| `references/equations.md` | Manim 中的 LaTeX、TransformMatchingTex、推导模式 |
| `references/graphs-and-data.md` | 坐标轴、绘图、BarChart、动画数据、算法可视化 |
| `references/camera-and-3d.md` | MovingCameraScene、ThreeDScene、3D 曲面、相机控制 |
| `references/scene-planning.md` | 叙事弧线、布局模板、场景过渡、规划模板 |
| `references/rendering.md` | CLI 参考、质量预设、ffmpeg、画外音工作流、GIF 导出 |
| `references/troubleshooting.md` | LaTeX 错误、动画错误、常见错误、调试 |
| `references/animation-design-thinking.md` | 何时动画化 vs 静态展示、分解、节奏、与旁白同步 |
| `references/updaters-and-trackers.md` | ValueTracker、add_updater、always_redraw、基于时间的更新器、模式 |
| `references/paper-explainer.md` | 将研究论文转化为动画 — 工作流、模板、领域模式 |
| `references/decorations.md` | SurroundingRectangle、Brace、箭头、DashedLine、Angle、注释生命周期 |
| `references/production-quality.md` | 编码前、渲染前、渲染后检查清单、空间布局、颜色、节奏 |

---

## 创意发散（仅在用户请求实验性/创意性/独特输出时使用）

如果用户要求创意性、实验性或非传统的解释方法，请在选择策略并在设计动画之前进行推理。

- **SCAMPER** — 当用户希望对标准解释有新的看法时
- **假设反转** — 当用户想要挑战通常的教学方式时

### SCAMPER 转换
取一个标准的数学/技术可视化并进行转换：
- **替代**：替换标准的视觉隐喻（数轴 → 蜿蜒路径，矩阵 → 城市网格）
- **组合**：合并两种解释方法（代数 + 几何同时进行）
- **反转**：反向推导 — 从结果开始，解构到公理
- **修改**：夸大一个参数以显示其重要性（学习率 10 倍，样本量 1000 倍）
- **消除**：移除所有符号 — 纯粹通过动画和空间关系来解释
### 假设反转
1. 列出关于该主题可视化方式的“标准”做法（从左到右、二维、离散步骤、形式化符号）
2. 选取最根本的假设
3. 将其反转（从右到左推导、二维概念的 3D 嵌入、连续变形而非离散步骤、零符号化）
4. 探索反转所揭示的、标准方法所隐藏的内容