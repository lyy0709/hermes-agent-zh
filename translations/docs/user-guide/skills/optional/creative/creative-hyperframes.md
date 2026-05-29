---
title: "Hyperframes"
sidebar_label: "Hyperframes"
description: "使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交叠加层、带字幕的谈话头视频、音频响应式视觉效果以及着色器过渡..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hyperframes

使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交叠加层、带字幕的谈话头视频、音频响应式视觉效果以及着色器过渡。HTML 是视频的单一事实来源。当用户希望从 HTML 合成渲染出 MP4/WebM 视频、希望在媒体上为文本/徽标/图表添加动画、需要字幕与音频同步、需要 TTS 旁白，或者希望将网站转换为视频时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/hyperframes` 安装 |
| 路径 | `optional-skills/creative/hyperframes` |
| 版本 | `1.0.0` |
| 作者 | heygen-com |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `video`, `animation`, `html`, `gsap`, `motion-graphics` |
| 相关技能 | [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# HyperFrames

HTML 是视频的单一事实来源。一个合成是一个 HTML 文件，其中包含用于定时的 `data-*` 属性、用于动画的 GSAP 时间线以及用于外观的 CSS。HyperFrames 引擎逐帧捕获页面，并使用 FFmpeg 编码为 MP4/WebM。

**对 `manim-video` 的补充：** 使用 `manim-video` 处理数学/几何解释（方程、3B1B 风格）。使用 `hyperframes` 处理动态图形、带字幕的谈话头、产品导览、社交叠加层、着色器过渡以及任何由真实视频/音频媒体驱动的内容。

## 何时使用

- 用户要求从文本、脚本或网站渲染视频
- 动画标题卡、下三分之一图形或排版开场
- 带字幕的旁白视频（TTS + 字幕与波形同步）
- 音频响应式视觉效果（节拍同步、频谱条、脉动辉光）
- 场景到场景的过渡（交叉淡入淡出、擦除、着色器扭曲、白色闪切）
- 社交叠加层（Instagram/TikTok/YouTube 风格）
- 网站到视频流水线（捕获 URL，生成宣传视频）
- 任何必须确定性地渲染为视频文件的 HTML/CSS/JS 动画

**不要**将此技能用于：
- 纯数学/方程动画（→ `manim-video`）
- 图像生成或表情包（→ `meme-generation`、图像模型）
- 实时视频会议或流媒体

## 快速参考

```bash
npx hyperframes init my-video               # 搭建项目脚手架
cd my-video
npx hyperframes lint                        # 在预览/渲染前验证
npx hyperframes preview                     # 实时重载浏览器预览（端口 3002）
npx hyperframes render --output final.mp4   # 渲染为 MP4
npx hyperframes doctor                      # 诊断环境问题
```

渲染标志：`--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker`（可重现）· `--strict`。

完整 CLI 参考：[references/cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md)。

## 设置（一次性）

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

该脚本：
1. 验证 Node.js >= 22 和 FFmpeg 是否已安装（如果未安装则打印修复说明）。
2. 全局安装 `hyperframes` CLI（`npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell` — 这是通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获路径实现最佳质量渲染所**必需**的。
4. 运行 `npx hyperframes doctor` 并报告结果。

如果设置失败，请参阅 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。

## 流程

### 1. 在编写 HTML 前进行规划

在接触代码之前，先在高层次上阐明：
- **内容** — 叙事弧线、关键时刻、情感节拍
- **结构** — 合成、轨道（视频/音频/叠加层）、持续时间
- **视觉识别** — 颜色、字体、动效特征（爆炸性 / 电影感 / 流畅 / 技术性）
- **关键帧** — 对于每个场景，当最多元素同时可见的时刻。这是你首先要构建的静态布局。

**视觉识别门控（硬性门控）。** 在编写**任何**合成 HTML 之前，必须定义视觉识别。**不要**使用默认或通用颜色（`#333`、`#3b82f6`、`Roboto` 是跳过此步骤的迹象）编写合成。按顺序检查：

1. **项目根目录有 `DESIGN.md` 吗？** → 使用其确切的颜色、字体、动效规则和“不应做什么”约束。
2. **用户指定了样式吗**（例如“Swiss Pulse”、“dark and techy”、“luxury brand”）？ → 生成一个包含 `## Style Prompt`、`## Colors`（3-5 个十六进制颜色及其角色）、`## Typography`（1-2 种字体族）、`## What NOT to Do`（3-5 个反模式）的最小化 `DESIGN.md`。
3. **以上都没有？** → 在编写任何 HTML 之前询问 3 个问题：
   - 氛围？（爆炸性 / 电影感 / 流畅 / 技术性 / 混乱 / 温暖）
   - 浅色还是深色画布？
   - 有任何品牌颜色、字体或视觉参考吗？

   然后根据答案生成一个 `DESIGN.md`。每个合成都必须将其调色板和字体追溯到 `DESIGN.md` 或明确的用户指示。

### 2. 搭建脚手架

```bash
npx hyperframes init my-video --non-interactive
```

模板：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。传递 `--example <name>` 以选择一个模板，传递 `--video clip.mp4` 或 `--audio track.mp3` 以使用媒体作为种子。
### 3. 动画前的布局

首先为**英雄帧编写静态 HTML+CSS** —— 先不使用 GSAP。`.scene-content` 容器必须填满场景（`width:100%; height:100%; padding:Npx`），并使用 `display:flex` + `gap`。使用内边距将内容向内推 —— 切勿在内容容器上使用 `position: absolute; top: Npx`（当内容高度超过剩余空间时会溢出）。

只有在英雄帧看起来正确之后，才添加 `gsap.from()` 入场动画（动画**到** CSS 位置）和 `gsap.to()` 退场动画（动画**从**该位置开始）。

完整的数据属性模式和构图规则请参阅 [references/composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md)。

### 4. 使用 GSAP 制作动画

每个构图必须：
- 注册其时间轴：`window.__timelines["<composition-id>"] = tl`
- 以暂停状态开始：`gsap.timeline({ paused: true })` —— 播放器控制播放
- 使用有限的 `repeat` 值（不要用 `repeat: -1` —— 这会破坏捕获引擎）。计算公式：`repeat: Math.ceil(duration / cycleDuration) - 1`。
- 是确定性的 —— 不要使用 `Math.random()`、`Date.now()` 或实时时钟逻辑。如果需要伪随机性，请使用种子 PRNG。
- 同步构建 —— 不要在时间轴构建周围使用 `async`/`await`、`setTimeout` 或 Promise。

核心 GSAP API（补间动画、缓动、错开、时间轴）请参阅 [references/gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md)。

### 5. 场景间的过渡

多场景构图需要过渡。规则：
1. **场景之间始终使用过渡** —— 不要使用跳切。
2. **每个场景元素始终使用入场动画**（`gsap.from(...)`）。
3. **除了最终场景外，切勿使用退场动画** —— 过渡本身就是退场。
4. 最终场景可以淡出。

使用 `npx hyperframes add <transition-name>` 来安装着色器过渡（`flash-through-white`、`liquid-wipe` 等）。完整列表：`npx hyperframes add --list`。

### 6. 音频、字幕、TTS、音频响应、高亮

- **音频：** 始终是单独的 `<audio>` 元素（视频是 `muted playsinline`）。
- **TTS：** `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav`。使用 `--list` 列出语音。语音 ID 的第一个字母编码语言（`a`/`b`=英语，`e`=西班牙语，`f`=法语，`j`=日语，`z`=普通话等）—— CLI 会自动推断音素化器区域设置；仅在需要覆盖时传递 `--lang`。非英语音素化需要系统全局安装 `espeak-ng`。
- **字幕：** `npx hyperframes transcribe narration.wav` → 单词级转录。根据转录的语调选择风格（宣传 / 企业 / 教程 / 故事讲述 / 社交 —— 参见 `references/features.md` 中的表格）。**语言规则：** 除非音频确认是英语，否则切勿使用 `.en` 的 Whisper 模型 —— `.en` 模型会翻译非英语音频而不是转录它。每个字幕组在其退场补间动画之后**必须**有一个强制的 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 来清除它 —— 否则字幕组会泄漏并显示在后面的场景中。
- **音频响应式视觉效果：** 预提取音频频段（低音 / 中音 / 高音），并在时间轴内使用 `for` 循环 `tl.call(draw, [], f / fps)` 进行逐帧采样 —— 单个长补间动画**不会**对音频做出反应。映射低音 → `scale`（脉动），高音 → `textShadow`/`boxShadow`（发光），整体振幅 → `opacity`/`y`/`backgroundColor`。避免均衡器条这种陈词滥调 —— 让内容引导视觉，让音频驱动其行为。
- **标记式高亮：** 用于文本强调的高亮、圆圈、爆发、涂鸦、草图效果是确定性的 CSS+GSAP —— 参见 `references/features.md#marker-highlighting`。完全可搜索，没有动画 SVG 滤镜。
- **场景过渡：** 每个多场景构图**必须**使用过渡（无跳切）。从 CSS 原语（推动幻灯片、模糊交叉淡入淡出、缩放穿过、错开块）或通过 `npx hyperframes add` 安装的着色器过渡（`flash-through-white`、`liquid-wipe`、`cross-warp-morph`、`chromatic-split` 等）中选择。情绪和能量表位于 `references/features.md#transitions`。不要在同一个构图中混合使用 CSS 和着色器过渡。

### 7. 代码检查、验证、检查、预览、渲染

```bash
npx hyperframes lint              # 捕获缺失的 data-composition-id、重叠的轨道、未注册的时间轴
npx hyperframes validate          # 在 5 个时间戳进行 WCAG 对比度审计
npx hyperframes inspect           # 视觉布局审计 —— 溢出、超出帧的元素、被遮挡的文本
npx hyperframes preview           # 实时浏览器预览
npx hyperframes render --quality draft --output draft.mp4    # 快速迭代
npx hyperframes render --quality high --output final.mp4     # 最终交付
```

`hyperframes validate` 会采样每个文本元素后面的背景像素，并在对比度低于 4.5:1（或大文本低于 3:1）时发出警告。`hyperframes inspect` 是布局方面的伴侣 —— 在多个时间戳运行页面，并标记静态代码检查无法看到的问题（仅在 4.5 秒时换行超出安全区域的字幕、当标题是最长变体时溢出的卡片、最终位于过渡着色器后面的元素）。特别是在包含对话气泡、卡片、字幕或紧凑排版的构图上运行 `inspect`。

### 8. 网站转视频（如果用户提供了 URL）

使用 [references/website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) 中的 7 步捕获到视频工作流：捕获 → DESIGN.md → SCRIPT.md → 故事板 → 构图 → 渲染 → 交付。

## 常见陷阱

- **`HeadlessExperimental.beginFrame' wasn't found`** —— Chromium 147+ 移除了此协议。确保你使用的是 `hyperframes@>=0.4.2`（自动检测并回退到截图模式）。应急方案：`export PRODUCER_FORCE_SCREENSHOT=true`。参见 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 和 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。
- **系统 Chrome（非 `chrome-headless-shell`）** —— 渲染会挂起 120 秒然后超时。运行 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 会执行此操作）。`hyperframes doctor` 报告将使用哪个二进制文件。
- **任何地方使用 `repeat: -1`** —— 破坏捕获引擎。始终计算一个有限的重复次数。
- **对稍后进入的剪辑元素使用 `gsap.set()`** —— 该元素在页面加载时不存在。改为在时间轴内部使用 `tl.set(selector, vars, timePosition)`，在剪辑的 `data-start` 处或之后。
- **内容文本中使用 `<br>`** —— 强制换行不知道渲染的字体宽度，因此自然换行 + `<br>` 会导致双重换行。使用 `max-width` 让文本换行。例外情况：简短的显示标题，其中每个单词都特意放在单独一行。
- **动画化 `visibility` 或 `display`** —— GSAP 无法对这些属性进行补间动画。使用 `autoAlpha`（同时处理可见性和不透明度）。
- **调用 `video.play()` 或 `audio.play()`** —— 框架拥有播放控制权。切勿自行调用这些方法。
- **异步构建时间轴** —— 捕获引擎在页面加载后同步读取 `window.__timelines`。切勿将时间轴构建包装在 `async`、`setTimeout` 或 Promise 中。
- **独立的 `index.html` 包裹在 `<template>` 中** —— 将所有内容对浏览器隐藏。只有通过 `data-composition-src` 加载的**子构图**才使用 `<template>`。
- **使用视频承载音频** —— 始终使用静音的 `<video>` + 单独的 `<audio>`。
## 验证

渲染前后：

1. **Lint + validate + inspect 通过：** `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（lint 捕获结构问题，validate 捕获对比度问题，inspect 捕获视觉布局/溢出问题 — 如果出现警告，请参阅 troubleshooting.md）。
2. **动画编排** — 对于新的合成或重大的动画更改，运行动画映射。`npx hyperframes init` 会将技能脚本复制到项目中，因此路径是项目本地的：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
   输出一个包含每个补间摘要、ASCII 甘特图时间线、交错检测、死区（>1 秒无动画）、元素生命周期和标记（`offscreen`、`collision`、`invisible`、`paced-fast` <0.2s、`paced-slow` >2s）的单一 `animation-map.json` 文件。扫描摘要和标记 — 修复或说明每个问题。小修改可跳过此步骤。
3. **文件存在且非零：** `ls -lh final.mp4`。
4. **时长与 `data-duration` 匹配：** `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取合成中间的一帧：`ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **音频存在（如果预期有）：** `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 失败，请运行 `npx hyperframes doctor` 并在报告时附上其输出。

## 参考

- [composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md) — 数据属性、时间线约定、不可协商的规则、排版/资源规则
- [cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md) — 每个 CLI 命令（init、capture、lint、validate、inspect、preview、render、transcribe、tts、doctor、browser、info、upgrade、benchmark）
- [gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md) — HyperFrames 的 GSAP 核心 API（补间、缓动、交错、时间线、matchMedia）
- [features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/features.md) — 字幕、TTS、音频响应、标记高亮、过渡（按需加载）
- [website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) — 7 步从捕获到视频的工作流
- [troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md) — OpenClaw 修复、环境变量、常见渲染错误