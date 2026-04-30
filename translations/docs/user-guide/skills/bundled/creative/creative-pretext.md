---
title: "Pretext"
sidebar_label: "Pretext"
description: "在构建创意浏览器演示时使用 @chenglou/pretext —— 用于 ASCII 艺术的无 DOM 文本布局、围绕障碍物的排版流、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Pretext

在构建创意浏览器演示时使用 @chenglou/pretext —— 用于 ASCII 艺术的无 DOM 文本布局、围绕障碍物的排版流、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pretext` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `creative-coding`, `typography`, `pretext`, `ascii-art`, `canvas`, `generative`, `text-layout`, `kinetic-typography` |
| 相关技能 | [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Pretext 创意演示

## 概述

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是 Cheng Lou（React 核心、ReasonML、Midjourney）开发的一个 15KB 零依赖 TypeScript 库，用于**无 DOM 的多行文本测量和布局**。它只做一件事：给定 `(文本, 字体, 宽度)`，返回换行符、每行宽度、每个字素的位置以及总高度 —— 全部通过 Canvas 测量完成，无需回流。

这听起来像是底层工具。但它不是。因为它快速且基于几何，它是一个**创意原语**：你可以让段落以 60fps 的速度围绕移动的精灵重排，构建关卡几何由真实单词组成的游戏，让 ASCII 标志穿过散文，将文本粉碎成具有精确字素起始位置的粒子，或者打包收缩包装的多行 UI 而无需任何 `getBoundingClientRect` 抖动。

此技能的存在是为了让 Hermes 可以用它制作**很酷的演示**——那种人们在 X 上发布的演示。请访问 `pretext.cool` 和 `chenglou.me/pretext` 查看社区演示集。

## 何时使用

当用户要求以下内容时使用：
- 一个 "pretext 演示" / "很酷的 pretext 东西" / "文本即 X"
- 文本围绕移动形状流动（英雄区域、编辑布局、动画长页面）
- 使用**真实单词或散文**而非等宽栅格的 ASCII 艺术效果
- 游戏场/障碍物/砖块由文本构成的游戏（字母俄罗斯方块、散文打砖块）
- 具有逐字形物理效果的动态排版（粉碎、散射、聚集、流动）
- 排版生成艺术，特别是非拉丁文字或混合文字
- 多行 "收缩包装" UI（仍能容纳文本的最小容器宽度）
- 任何需要在渲染*之前*知道换行符的情况

不要用于：
- CSS 已解决布局的静态 SVG/HTML 页面 —— 直接使用 CSS
- 富文本编辑器、通用内联格式化引擎（pretext 有意保持功能狭窄）
- 图像 → 文本（使用 `ascii-art` / `ascii-video` 技能）
- 没有文本作用的纯 Canvas 生成艺术 —— 使用 `p5js`

## 创意标准

这是在浏览器中渲染的视觉艺术。Pretext 返回数字；**你**来绘制内容。

- **不要交付一个 "hello world" 演示。** `hello-orb-flow.html` 模板是*起点*。每个交付的演示都必须添加有意的色彩、运动、构图以及一个用户未要求但会欣赏的视觉细节。
- **深色背景，暖色核心，精心考虑的调色板。** 经典的琥珀色-黑色（CRT / 终端）可行，但冷白色-炭灰色（编辑风格）和低饱和度的柔和色彩（孔版印刷风格）也可以。选择一个并坚持使用。
- **比例字体是重点。** Pretext 的整体风格是 "非等宽" —— 充分利用这一点。使用 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或可变字体。永远不要默认使用无衬线字体。
- **真实的来源/文本，而非乱数假文。** 文本集应该有意义。简短的宣言、诗歌、真实的源代码、一段发现的文本、库自身的 README —— 永远不要使用 `lorem ipsum`。
- **首次绘制卓越。** 没有加载状态，没有空白帧。演示必须在打开的瞬间看起来就是可交付的。

## 技术栈

每个演示都是单个自包含的 HTML 文件。无需构建步骤。

| 层级 | 工具 | 用途 |
|-------|------|---------|
| 核心 | 通过 `esm.sh` CDN 的 `@chenglou/pretext` | 文本测量 + 行布局 |
| 渲染 | HTML5 Canvas 2D | 字形渲染、逐帧合成 |
| 分割 | `Intl.Segmenter`（内置） | 用于表情符号 / CJK / 组合标记的字素分割 |
| 交互 | 原始 DOM 事件 | 鼠标 / 触摸 / 滚轮 —— 无框架 |

```html
<script type="module">
import {
  prepare, layout,                   // 用例 1: 简单高度
  prepareWithSegments, layoutWithLines,  // 用例 2a: 固定宽度行
  layoutNextLineRange, materializeLineRange, // 用例 2b: 流式 / 可变宽度
  measureLineStats, walkLineRanges,  // 无需字符串分配的状态统计
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

固定版本。撰写本文时为 `@0.0.6` —— 如果演示行为异常，请检查 [npm](https://www.npmjs.com/package/@chenglou/pretext) 获取最新版本。

## 两个用例

几乎所有内容都可以归结为以下两种模式之一。学习两者。

### 用例 1 —— 测量，然后使用 CSS/DOM 渲染

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器绘制文本。Pretext 只是告诉你在给定宽度下盒子会有多高，**无需** DOM 读取。用于：
- 包含换行文本的行的虚拟化列表
- 具有精确卡片高度的瀑布流布局
- "这个标签合适吗？" 开发时检查
- 远程文本加载时防止布局偏移
**保持 `font` 和 `letterSpacing` 与 CSS 完全同步。** 画布的 `ctx.font` 格式（例如 `"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与渲染的 CSS 匹配，否则测量会出现偏差。

### 用例 2 — 自行测量*并*渲染

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```

这里是创意工作所在。你拥有绘图控制权，因此可以：
- 渲染到 canvas、SVG、WebGL 或任何坐标系
- 替换每个字形的变换（旋转、抖动、缩放、不透明度）
- 将行元数据（宽度、字位位置）用作几何图形

对于**每行可变宽度**的流式布局（围绕形状的文本、环形带中的文本、非矩形列中的文本）：

```js
let cursor = { segmentIndex: 0, graphemeIndex: 0 };
let y = 0;
while (true) {
  const lineWidth = widthAtY(y);  // 你的函数：在此 y 坐标处，通道有多宽？
  const range = layoutNextLineRange(prepared, cursor, lineWidth);
  if (!range) break;
  const line = materializeLineRange(prepared, range);
  ctx.fillText(line.text, leftEdgeAtY(y), y);
  cursor = range.end;
  y += lineHeight;
}
```

这是整个库中最重要的模式。正是它实现了“文本围绕拖动的精灵流动”——那个在 X 上疯传的演示。

### 值得了解的辅助函数

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }` — 最宽的行，即多行收缩包裹的宽度。
- `walkLineRanges(prepared, maxWidth, callback)` — 在不分配字符串的情况下迭代行。当你不需要字符时，用于统计/物理计算（基于字位）。
- `@chenglou/pretext/rich-inline` — 相同的系统，但用于混合字体/芯片/提及的段落。从子路径导入。

## 演示配方模式

社区语料库（参见 `references/patterns.md`）聚类成少数几个强大的模式。选择一个并即兴发挥——除非被要求，否则不要发明新类别。

| 模式 | 关键 API | 示例想法 |
|---|---|---|
| **围绕障碍物重排** | `layoutNextLineRange` + 每行宽度函数 | 围绕拖动的光标精灵分开的编辑段落 |
| **文本作为几何图形的游戏** | `layoutWithLines` + 每行碰撞矩形 | 每个砖块都是一个测量单词的打砖块游戏 |
| **破碎/粒子** | `walkLineRanges` → 每个字位的 (x,y) → 物理效果 | 点击时爆炸成字母的句子 |
| **ASCII 障碍物排版** | `layoutNextLineRange` + 测量的每行障碍物跨度 | 位图 ASCII 徽标、形状变形，以及可拖动的线框对象，使文本围绕其实际几何形状展开 |
| **编辑多栏布局** | 每栏的 `layoutNextLineRange` + 共享光标 | 带有引文的动画杂志版面 |
| **动态字体** | `layoutWithLines` + 每行随时间变换 | 星球大战片头滚动、波浪、弹跳、故障效果 |
| **多行收缩包裹** | `measureLineStats` | 自动调整到最紧凑容器的引用卡片 |

请参阅 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html` 以获取可用的单文件入门示例。

## 工作流程

1.  **根据用户需求，从上表中选择一个模式。**
2.  **从模板开始**：
    - `templates/hello-orb-flow.html` — 文本围绕移动的球体重排（围绕障碍物重排模式）
    - `templates/donut-orbit.html` — 高级示例：测量的 ASCII 徽标障碍物、可拖动的线框球体/立方体、变形形状场、可选择的 DOM 文本以及仅限开发者的控制项
    - 使用 `write_file` 写入 `/tmp/` 或用户工作区中的新 `.html` 文件。
3.  **将语料库替换为符合需求的有意内容。** 使用真实的散文，10-100 个句子，不要用乱数假文。
4.  **调整美学效果** — 字体、调色板、构图、交互。这是核心工作；不要跳过。
5.  **本地验证**：
    ```sh
    cd <dir-with-html> && python3 -m http.server 8765
    # 然后打开 http://localhost:8765/<file>.html
    ```
6.  **检查控制台** — 如果使用错误的字体字符串调用 `prepareWithSegments`，pretext 会抛出错误；`Intl.Segmenter` 在所有现代浏览器中都可用。
7.  **向用户展示文件路径**，而不仅仅是代码——他们想要打开它。

## 性能注意事项

- `prepare()` / `prepareWithSegments()` 是昂贵的调用。**每个文本+字体对只执行一次**。缓存句柄。
- 调整大小时，只重新运行 `layout()` / `layoutWithLines()` — 永远不要重新准备。
- 对于文本不变但几何形状变化的逐帧动画，在紧密循环中使用 `layoutNextLineRange` 足够便宜，可以在 60fps 下为正常长度的段落每帧执行。
- 当每帧渲染 ASCII 遮罩时，保留一个单元格缓冲区（`Uint8Array`/类型化数组），从单元格或投影几何图形中推导出测量的每行障碍物跨度，合并跨度，然后在绘制文本之前将这些跨度提供给 `layoutNextLineRange`。
- 保持视觉动画和布局动画耦合。如果一个球体变形为立方体，请同时补间渲染的单元格缓冲区和障碍物跨度；否则演示看起来像是画上去的，而不是物理重排。
- 对于淡入淡出，优先使用图层不透明度，而不是改变字形强度或障碍物缩放。将临时的 ASCII 精灵放在它们自己的画布上，并使用 CSS/GSAP 不透明度淡入淡出画布，这样几何形状就不会看起来在缩小。
- 设置 Canvas `ctx.font` 出奇地慢；如果字体不变化，**每帧设置一次**，而不是每次 `fillText` 调用都设置。

## 常见陷阱

1.  **CSS/画布字体字符串不一致。** `ctx.font = "16px Inter"` 被测量，但 CSS 是 `font-family: Inter, sans-serif; font-size: 16px`。*如果* Inter 加载成功，没问题。如果 Inter 404，CSS 会回退到 sans-serif，测量结果会偏差 5-20%。始终 `preload` 字体或使用 Web 安全字体族。

2.  **在动画循环内重新准备。** 只有 `layout*` 是便宜的。每帧重新调用 `prepare` 会严重损害性能。将准备好的句柄保持在模块作用域中。

3.  **忘记使用 `Intl.Segmenter` 进行字位分割。** 表情符号、组合标记、中日韩文字 — `"é".split("")` 会给你两个字符。当采样单个可见字形时，使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })`。
4. **`break: 'never'` 的原子化标签/提及不使用 `extraWidth`。** 在 `rich-inline` 中，如果你为原子化标签/提及使用 `break: 'never'`，则必须同时提供 `extraWidth` 用于标签内边距 —— 否则标签的装饰部分会溢出容器。

5. **从 `unpkg` 使用 `@chenglou/pretext` 且仅包含 TypeScript 入口。** 请使用 `esm.sh` —— 它会自动将 TS 导出编译为浏览器可用的 ESM。`unpkg` 会返回 404 或提供原始的 TS 文件。

6. **等宽字体回退会悄无声息地抹杀整个设计意图。** 用户看到等宽字体样式的输出，通常是因为 CSS `font-family` 回退到了 `monospace`。请通过开发者工具验证实际渲染的字体。

7. **在形状周围进行流式布局时，跳过行与调整宽度的选择。** 如果当前行的通道太窄而无法容纳一行文本，*请跳过该行* (`y += lineHeight; continue;`)，而不是向 `layoutNextLineRange` 传递一个极小的 maxWidth —— pretext 会返回看起来破碎的单字素行。

8. **发布一个冰冷的演示。** 默认的首屏渲染效果看起来像是教程级别的。请添加：晕影、细微的扫描线、空闲时的自动运动、一个精心选择的交互响应（拖拽、悬停、滚动、点击）。如果没有这些，"酷炫的 pretext 演示" 给人的感觉就像是 "实习生复现的 README"。

## 验证清单

- [ ] 演示是一个单一、自包含的 `.html` 文件 —— 可通过双击或 `python3 -m http.server` 打开
- [ ] `@chenglou/pretext` 通过 `esm.sh` 导入，并指定了固定版本
- [ ] 语料是真实的散文，而非乱数假文，并且与演示的概念相匹配
- [ ] 传递给 `prepare` 的字体字符串与 CSS 字体完全一致
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而不是每帧都调用
- [ ] 深色背景 + 经过考虑的调色板 —— 而非默认的白色画布
- [ ] 至少有一个交互响应（拖拽 / 悬停 / 滚动 / 点击）或空闲时的自动运动
- [ ] 使用 `python3 -m http.server` 在本地测试，并确认控制台没有错误
- [ ] 在中端笔记本电脑上达到 60fps（或已记录优雅降级方案）
- [ ] 一个用户未要求的 "额外努力" 细节

## 参考：社区演示

克隆这些项目以获取灵感/模式（均为 MIT 类许可，链接自 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker** — 带有单词砖块的打砖块游戏 — `github.com/rinesh/pretext-breaker`
- **Tetris × Pretext** — `github.com/shinichimochizuki/tetris-pretext`
- **Dragon animation** — `github.com/qtakmalay/PreTextExperiments`
- **Somnai editorial engine** — `github.com/somnai-dreams/pretext-demos`
- **Bad Apple!! ASCII** — `github.com/frmlinn/bad-apple-pretext`
- **Drag-sprite reflow** — `github.com/dokobot/pretext-demo`
- **Alarmy editorial clock** — `github.com/SmisLee/alarmy-pretext-demo`

官方游乐场：[chenglou.me/pretext](https://chenglou.me/pretext/) —— 手风琴、气泡、动态布局、编辑引擎、对齐方式比较、瀑布流、Markdown 聊天、富文本笔记。