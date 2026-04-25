---
title: "架构图"
sidebar_label: "架构图"
description: "生成深色主题的软件系统和云基础设施 SVG 图，作为带有内联 SVG 图形的独立 HTML 文件"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 架构图

生成深色主题的软件系统和云基础设施 SVG 图，作为带有内联 SVG 图形的独立 HTML 文件。语义化组件颜色（青色=前端，翠绿色=后端，紫色=数据库，琥珀色=云/AWS，玫瑰色=安全，橙色=消息总线），JetBrains Mono 字体，网格背景。最适合软件架构、云/VPC 拓扑、微服务地图、服务网格图、数据库 + API 层图、安全组、消息总线——任何适合深色美学技术基础设施演示文稿的内容。如果存在针对该主题的更专业的绘图技能（科学、教育、手绘、动画等），请优先使用该技能——否则此技能也可作为通用的 SVG 图备用方案。基于 Cocoon AI 的 architecture-diagram-generator (MIT)。

## 技能元数据

| | |
|---|---|
| 来源 | 捆绑（默认安装） |
| 路径 | `skills/creative/architecture-diagram` |
| 版本 | `1.0.0` |
| 作者 | Cocoon AI (hello@cocoon-ai.com)，由 Hermes Agent 移植 |
| 许可证 | MIT |
| 标签 | `architecture`, `diagrams`, `SVG`, `HTML`, `visualization`, `infrastructure`, `cloud` |
| 相关技能 | [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 架构图技能

生成专业的深色主题技术架构图，作为带有内联 SVG 图形的独立 HTML 文件。无需外部工具、API 密钥或渲染库——只需编写 HTML 文件并在浏览器中打开。

## 范围

**最适合用于：**
- 软件系统架构（前端 / 后端 / 数据库层）
- 云基础设施（VPC、区域、子网、托管服务）
- 微服务 / 服务网格拓扑
- 数据库 + API 映射、部署图
- 任何适合深色、网格背景美学的技术基础设施主题

**以下情况请优先考虑其他技能：**
- 物理、化学、数学、生物学或其他科学主题
- 物理对象（车辆、硬件、解剖、横截面）
- 平面图、叙述性旅程、教育 / 教科书式视觉内容
- 手绘白板草图（考虑 `excalidraw`）
- 动画解说（考虑动画技能）

如果存在针对该主题的更专业的技能，请优先使用。如果没有合适的，此技能也可作为通用的 SVG 图备用方案——输出将仅遵循下述的深色技术美学。

基于 [Cocoon AI 的 architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT)。

## 工作流

1.  用户描述其系统架构（组件、连接、技术）
2.  按照以下设计系统生成 HTML 文件
3.  使用 `write_file` 保存到 `.html` 文件（例如 `~/architecture-diagram.html`）
4.  用户在任意浏览器中打开——可离线工作，无依赖

### 输出位置

将图表保存到用户指定的路径，或默认为当前工作目录：
```
./[项目名称]-architecture.html
```

### 预览

保存后，建议用户打开它：
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

## 设计系统与视觉语言

### 调色板（语义映射）

使用特定的 `rgba` 填充色和十六进制描边色对组件进行分类：

| 组件类型 | 填充色 (rgba) | 描边色 (Hex) |
| :--- | :--- | :--- |
| **前端** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| **后端** | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| **数据库** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| **AWS/云** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| **安全** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| **消息总线** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| **外部** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

### 排版与背景
- **字体：** JetBrains Mono（等宽字体），从 Google Fonts 加载
- **大小：** 12px（名称），9px（子标签），8px（注释），7px（微小标签）
- **背景：** Slate-950 (`#020617`) 带有微妙的 40px 网格图案

```svg
<!-- 背景网格图案 -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## 技术实现细节

### 组件渲染
组件是圆角矩形 (`rx="6"`)，带有 1.5px 描边。为防止箭头透过半透明填充色显示，请使用**双矩形遮罩技术**：
1.  绘制一个不透明的背景矩形 (`#0f172a`)
2.  在其上方绘制半透明样式矩形

### 连接规则
- **Z 轴顺序：** 在 SVG 中*尽早*绘制箭头（在网格之后），使其渲染在组件框后面
- **箭头头部：** 通过 SVG 标记定义
- **安全流：** 使用玫瑰色 (`#fb7185`) 虚线
- **边界：**
  - *安全组：* 虚线 (`4,4`)，玫瑰色
  - *区域：* 大虚线 (`8,4`)，琥珀色，`rx="12"`

### 间距与布局逻辑
- **标准高度：** 60px（服务）；80-120px（大型组件）
- **垂直间距：** 组件之间最小 40px
- **消息总线：** 必须放置*在*服务之间的间隙中，不能重叠
- **图例放置：** **至关重要。** 必须放置在所有边界框之外。计算所有边界的最低 Y 坐标，并将图例放置在其下方至少 20px 处。

## 文档结构

生成的 HTML 文件遵循四部分布局：
1.  **页眉：** 带有脉动圆点指示器和副标题的标题
2.  **主 SVG：** 包含在圆角边框卡片内的图表
3.  **摘要卡片：** 图表下方用于显示高级详细信息的三张卡片网格
4.  **页脚：** 最少的元数据

### 信息卡片模式
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## 输出要求
- **单文件：** 一个自包含的 `.html` 文件
- **无外部依赖：** 所有 CSS 和 SVG 必须内联（Google Fonts 除外）
- **无 JavaScript：** 使用纯 CSS 实现任何动画（如脉动圆点）
- **兼容性：** 必须在任何现代网络浏览器中正确渲染

## 模板参考

加载完整的 HTML 模板以获取确切的结构、CSS 和 SVG 组件示例：

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

该模板包含每种组件类型（前端、后端、数据库、云、安全）、箭头样式（标准、虚线、曲线）、安全组、区域边界和图例的工作示例——在生成图表时将其用作您的结构参考。