---
title: "Sketch — 一次性 HTML 原型：用于比较的 2-3 个设计变体"
sidebar_label: "Sketch"
description: "一次性 HTML 原型：用于比较的 2-3 个设计变体"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Sketch

一次性 HTML 原型：用于比较的 2-3 个设计变体。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/sketch` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (改编自 gsd-build/get-shit-done) |
| 许可证 | MIT |
| 标签 | `sketch`, `mockup`, `design`, `ui`, `prototype`, `html`, `variants`, `exploration`, `wireframe`, `comparison` |
| 相关技能 | [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Sketch

当用户希望在**确定一个方向之前先看看设计方向**时使用此技能——将 UI/UX 想法作为一次性 HTML 原型进行探索。重点是生成 2-3 个交互式变体，以便用户可以并排比较视觉方向，而不是生成可交付的代码。

当用户说类似以下内容时加载此技能："sketch this screen"、"show me what X could look like"、"compare layout A vs B"、"give me 2-3 takes on this UI"、"let me see some variants"、"mockup this before I build"。

## 何时不应使用此技能

- 用户想要一个生产级组件——使用 `claude-design` 或正确构建它
- 用户想要一个精美的一次性 HTML 产物（落地页、演示文稿）——使用 `claude-design`
- 用户想要一个图表——使用 `excalidraw`、`architecture-diagram`
- 设计已经确定——直接构建即可

## 如果用户安装了完整的 GSD 系统

如果 `gsd-sketch` 显示为同级技能（通过 `npx get-shit-done-cc --hermes` 安装），则优先使用 **`gsd-sketch`** 以获得完整工作流：持久的 `.planning/sketches/` 目录（包含 MANIFEST）、前沿模式分析、跨历史原型的一致性审计，以及与 GSD 其余部分的集成。本技能是轻量级独立版本——无需状态机制的一次性原型设计。

## 核心方法

```
需求输入 → 生成变体 → 对比分析 → 选择优胜者（或迭代）
```

### 1. 需求输入（如果用户已提供足够信息，可跳过）

在生成变体之前，获取三样东西——一次一个问题，不要一次性问完：

1.  **感觉。** "这应该给人什么感觉？形容词、情绪、氛围。"——"calm, editorial, like Linear" 比 "minimal" 告诉你更多信息。
2.  **参考。** "哪些应用、网站或产品捕捉到了你想象中的感觉？"——实际的参考胜过抽象的描述。
3.  **核心操作。** "用户在这个屏幕上做的最重要的一件事是什么？"——所有变体都应该很好地服务于这一点；如果没有，它们就只是装饰。

在问下一个问题之前，简要复述每个答案。如果用户已经提前给出了所有三个信息，则直接跳到变体生成。

### 2. 变体（2-3 个，绝不要 1 个，很少需要 4 个以上）

一次性生成 **2-3 个变体**。每个变体都是一个完整、独立的 HTML 文件。不要描述变体——直接构建它们。重点在于比较。

每个变体应该采取**不同的设计立场**，而不仅仅是不同的像素值。三个好的变体维度：

-   **密度：** 紧凑型 / 宽松型 / 超密集型（选择两个对比鲜明的极端）
-   **重点：** 内容优先 / 操作优先 / 工具优先
-   **美学：** 编辑风格 / 实用风格 / 趣味风格
-   **布局：** 单栏 / 侧边栏 / 分栏
-   **基础样式：** 卡片式 / 纯内容式 / 文档式

选择一个维度并从中拉开差距。两个仅在强调色上不同的变体是浪费精力——用户无法区分它们。

**变体命名：** 描述立场，而不是编号。

<!-- ascii-guard-ignore -->
```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```
<!-- ascii-guard-ignore-end -->

### 3. 制作真实的 HTML

每个变体都是一个**单一的自包含 HTML 文件**：

-   内联 `<style>`——无需构建步骤，无需外部 CSS
-   系统字体或通过 `<link>` 引入的一个 Google Font
-   通过 CDN 使用 Tailwind (`<script src="https://cdn.tailwindcss.com"></script>`) 是可以的
-   逼真的模拟内容——实际的句子、实际的名称，而不是 "Lorem ipsum"
-   **交互性：** 链接可点击，悬停效果真实，至少有一个状态转换（打开/关闭、筛选、切换）。一个冻结的静态图像比一个粗糙的动画原型更糟糕。

在浏览器中打开它。如果看起来有问题，在展示给用户之前修复它。

**视觉验证变体——使用 Hermes 的浏览器工具。** 不要只写 HTML 并希望它能正确渲染；加载每个变体并查看它：

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="这个布局看起来是否干净易读？有任何可见的 bug 吗（文字重叠、未样式化的元素、损坏的图像）？")
```

`browser_vision` 返回一个关于页面上实际内容的 AI 描述以及一个截图路径——可以捕捉到纯源代码检查会遗漏的布局 bug（例如，一个静默失败的字体导入，一个折叠的 flex 容器）。修复并重新导航，直到每个变体看起来都正确。

**默认 CSS 重置 + 系统字体栈** 以便快速开始：

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

### 4. 变体 README

每个变体的 `README.md` 回答：

```markdown
## 变体：{立场名称}

### 设计立场
一句话说明驱动此变体的原则。

### 关键选择
- 布局：...
- 排版：...
- 颜色：...
- 交互：...

### 权衡
- 擅长：...
- 不擅长：...

### 最适合
- 此变体实际服务的用户类型或使用场景
```

### 5. 对比分析

在所有变体构建完成后，将它们作为比较呈现。不要只是列出——**提出观点**：

```markdown
## 首页屏幕的三种方案

| 维度 | 冷静编辑风格 | 实用密集风格 | 趣味分栏风格 |
|-----------|----------------|-------------------|---------------|
| 密度   | 低            | 高              | 中等        |
| 主要操作可见性 | 低 | 高 | 中等 |
| 可扫描性 | 高 | 中等 | 低 |
| 感觉 | 冷静、可信 | 锐利、工具感 | 吸引人、有活力 |

**我的看法：** 实用密集风格适合高级用户，冷静编辑风格适合内容导向的受众。趣味分栏风格最弱——试图兼顾两者，但都没有做好。
```

让用户选择一个优胜者，或者将两个组合成一个混合体，或者要求进行另一轮设计。

## 主题化（当项目有视觉识别时）

如果用户有现有的主题（颜色、字体、Token），将共享的 Token 放在 `sketches/themes/tokens.css` 中，并在每个变体中 `@import` 它们。保持 Token 最小化：

```css
/* sketches/themes/tokens.css */
:root {
  --color-bg: #fafafa;
  --color-fg: #1a1a1a;
  --color-accent: #0066ff;
  --color-muted: #666;
  --radius: 8px;
  --font-display: "Inter", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

不要对一个一次性原型过度 Token 化——通常三种颜色和一种字体就足够了。

## 交互性标准

当一个原型具备以下条件时，其交互性就足够了：

1.  **点击一个主要操作**，会发生一些可见的事情（状态改变、模态框、提示、导航假动作）
2.  **看到一个有意义的状态转换**（筛选列表、切换模式、打开/关闭面板）
3.  **悬停识别可操作元素**（按钮、行、标签页）

超过这个标准就是对一个一次性原型过度设计。低于这个标准就是一张截图。

## 前沿模式（选择接下来要设计什么）

如果已经存在原型，并且用户说 "what should I sketch next?"：

-   **一致性差距**——来自不同原型的两个优胜变体做出了尚未组合在一起的独立选择
-   **未设计的屏幕**——被提及但从未探索过
-   **状态覆盖**——设计了理想路径，但没有设计空状态 / 加载状态 / 错误状态 / 1000 项状态
-   **响应式差距**——在一个视口下已验证；在移动端 / 超宽屏下是否成立？
-   **交互模式**——存在静态布局；但过渡、拖拽、滚动行为不存在

提出 2-4 个命名的候选方案。让用户选择。

## 输出

-   在仓库根目录创建 `sketches/`（如果用户使用 GSD 约定，则为 `.planning/sketches/`）
-   每个变体一个子目录：`NNN-stance-name/index.html` + `README.md`
-   告诉用户如何打开它们：在 macOS 上使用 `open sketches/001-calm-editorial/index.html`，在 Linux 上使用 `xdg-open`，在 Windows 上使用 `start`
-   保持变体的可丢弃性——一个你觉得需要保留的原型应该被提升为真正的项目代码，而不是作为资产来维护

**一个变体的典型工具序列：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="How does this look? Any obvious layout issues?")
```

对每个变体重复此过程，然后呈现比较表格。

## 归属

改编自 GSD (Get Shit Done) 项目的 `/gsd-sketch` 工作流——MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统包含持久的原型状态、主题/变体模式参考以及一致性审计工作流；通过 `npx get-shit-done-cc --hermes --global` 安装。