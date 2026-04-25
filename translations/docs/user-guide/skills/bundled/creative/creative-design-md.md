---
title: "Design Md — 编写、验证、差异对比和导出 DESIGN"
sidebar_label: "Design Md"
description: "编写、验证、差异对比和导出 DESIGN"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Design Md

编写、验证、差异对比和导出 DESIGN.md 文件——这是 Google 的开源格式规范，为编码 Agent 提供对设计系统（Token 和设计原理合并在一个文件中）的持久化、结构化理解。适用于构建设计系统、在项目间移植样式规则、生成具有一致品牌风格的 UI，或审计无障碍/对比度。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/design-md` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `design`, `design-system`, `tokens`, `ui`, `accessibility`, `wcag`, `tailwind`, `dtcg`, `google` |
| 相关技能 | [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# DESIGN.md 技能

DESIGN.md 是 Google 用于向编码 Agent 描述视觉识别的开放规范（Apache-2.0，`google-labs-code/design.md`）。一个文件结合了：

- **YAML front matter** — 机器可读的设计 Token（规范值）
- **Markdown 正文** — 人类可读的设计原理，按规范章节组织

Token 提供精确值。正文告诉 Agent 这些值*为什么*存在以及如何应用它们。CLI（`npx @google/design.md`）可以检查结构 + WCAG 对比度、对比版本以发现退化，并导出到 Tailwind 或 W3C DTCG JSON。

## 何时使用此技能

- 用户要求一个 DESIGN.md 文件、设计 Token 或设计系统规范
- 用户希望在多个项目或工具间保持一致的 UI/品牌风格
- 用户粘贴了一个现有的 DESIGN.md 并要求检查、差异对比、导出或扩展它
- 用户要求将样式指南移植成 Agent 可以使用的格式
- 用户希望对他们的调色板进行对比度 / WCAG 无障碍验证

对于纯粹的视觉灵感或布局示例，请改用 `popular-web-designs`。此技能针对的是*规范文件本身*。

## 文件结构

```md
---
version: alpha
name: Heritage
description: Architectural minimalism meets journalistic gravitas.
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
---

## 概述

建筑极简主义遇见新闻庄重感...

## 颜色

- **主色 (#1A1C1E):** 用于标题和核心文本的深墨色。
- **第三色 (#B8422E):** "波士顿粘土色" — 交互的唯一驱动色。

## 排版

除小型全大写标签外，所有内容均使用 Public Sans...

## 组件

`button-primary` 是页面上唯一的高强调度操作...
```

## Token 类型

| 类型 | 格式 | 示例 |
|------|--------|---------|
| 颜色 | `#` + 十六进制 (sRGB) | `"#1A1C1E"` |
| 尺寸 | 数字 + 单位 (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token 引用 | `{path.to.token}` | `{colors.primary}` |
| 排版 | 包含 `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` 的对象 | 见上文 |

组件属性白名单：`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`。变体（hover, active, pressed）是**单独的组件条目**，具有相关的键名（`button-primary-hover`），而非嵌套。

## 规范章节顺序

章节是可选的，但存在的章节必须按此顺序出现。重复的标题会导致文件被拒绝。

1. 概述 (别名：品牌与风格)
2. 颜色
3. 排版
4. 布局 (别名：布局与间距)
5. 层级与深度 (别名：层级)
6. 形状
7. 组件
8. 注意事项

未知章节会被保留，不会报错。如果值类型有效，未知的 Token 名称会被接受。未知的组件属性会产生警告。

## 工作流：编写新的 DESIGN.md

1.  **询问用户**（或推断）品牌调性、强调色和排版方向。如果他们提供了网站、图片或氛围描述，将其转换为上述 Token 结构。
2.  使用 `write_file` 在项目根目录下**编写 `DESIGN.md`**。始终包含 `name:` 和 `colors:`；其他部分可选但鼓励添加。
3.  在 `components:` 部分**使用 Token 引用**（`{colors.primary}`），而不是重新输入十六进制值。保持调色板单一来源。
4.  **检查它**（见下文）。在返回之前修复任何损坏的引用或 WCAG 失败。
5.  **如果用户有现有项目**，同时将 Tailwind 或 DTCG 导出文件写入文件旁边（`tailwind.theme.json`, `tokens.json`）。

## 工作流：检查 / 差异对比 / 导出

CLI 是 `@google/design.md` (Node)。使用 `npx` — 无需全局安装。

```bash
# 验证结构 + Token 引用 + WCAG 对比度
npx -y @google/design.md lint DESIGN.md

# 比较两个版本，在退化时失败 (退出码 1 = 退化)
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# 导出到 Tailwind 主题 JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# 导出到 W3C DTCG (设计 Token 格式模块) JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# 打印规范本身 — 在注入到 Agent 提示词时很有用
npx -y @google/design.md spec --rules-only --format json
```

所有命令都接受 `-` 作为标准输入。`lint` 在遇到错误时返回退出码 1。如果需要结构化地报告发现的问题，请使用 `--format json` 标志并解析输出。

### 检查规则参考（7条规则捕获的内容）

- `broken-ref` (错误) — `{colors.missing}` 指向不存在的 Token
- `duplicate-section` (错误) — 相同的 `## 标题` 出现两次
- `invalid-color`, `invalid-dimension`, `invalid-typography` (错误)
- `wcag-contrast` (警告/信息) — 组件 `textColor` 与 `backgroundColor` 相对于 WCAG AA (4.5:1) 和 AAA (7:1) 标准的对比度比率
- `unknown-component-property` (警告) — 超出上述白名单

当用户关心无障碍性时，请在总结中明确指出这一点 — WCAG 发现是使用 CLI 最重要的原因。

## 常见陷阱

-   **不要嵌套组件变体。** `button-primary.hover` 是错误的；作为兄弟键的 `button-primary-hover` 是正确的。
-   **十六进制颜色必须是带引号的字符串。** 否则 YAML 会因 `#` 而解析失败，或错误地截断像 `#1A1C1E` 这样的值。
-   **负值尺寸也需要引号。** `letterSpacing: -0.02em` 会被解析为 YAML 流 — 应写作 `letterSpacing: "-0.02em"`。
-   **章节顺序是强制性的。** 如果用户以随机顺序提供了正文，请在保存前将其重新排序以匹配规范列表。
-   **`version: alpha` 是当前的规范版本**（截至 2026 年 4 月）。该规范标记为 alpha — 注意破坏性变更。
-   **Token 引用通过点分隔路径解析。** `{colors.primary}` 有效；`{primary}` 无效。

## 规范的真实来源

-   仓库：https://github.com/google-labs-code/design.md (Apache-2.0)
-   CLI：npm 上的 `@google/design.md`
-   生成的 DESIGN.md 文件的许可证：用户项目使用的任何许可证；规范本身是 Apache-2.0。