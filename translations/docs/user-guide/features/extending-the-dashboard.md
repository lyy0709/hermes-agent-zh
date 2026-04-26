---
sidebar_position: 17
title: "扩展仪表盘"
description: "为 Hermes 网页仪表盘构建主题和插件 —— 调色板、排版、布局、自定义标签页、外壳插槽、页面作用域插槽以及后端 API 路由"
---

# 扩展仪表盘

Hermes 网页仪表盘 (`hermes dashboard`) 的设计允许在不分叉代码库的情况下重新换肤和扩展。它暴露了三个层面：

1.  **主题** —— YAML 文件，用于重新绘制仪表盘的调色板、排版、布局以及每个组件的装饰。将文件放入 `~/.hermes/dashboard-themes/` 目录；它就会出现在主题切换器中。
2.  **UI 插件** —— 一个包含 `manifest.json` 和 JavaScript 包的目录，用于注册标签页、替换内置页面、通过页面作用域插槽增强页面，或将组件注入到命名的外壳插槽中。
3.  **后端插件** —— 插件目录内的一个 Python 文件，用于暴露一个 FastAPI `router`；路由挂载在 `/api/plugins/<name>/` 下，并从插件的 UI 调用。

这三者都是**运行时即插即用**的：无需克隆仓库、无需 `npm run build`、无需修改仪表盘源代码。本页面是这三者的权威参考。

如果你只想使用仪表盘，请参阅 [网页仪表盘](./web-dashboard)。如果你想为终端 CLI（而非网页仪表盘）重新换肤，请参阅 [皮肤与主题](./skins) —— CLI 皮肤系统与仪表盘主题无关。

:::note 各部分如何组合
主题和插件是独立但协同工作的。一个主题可以独立存在（仅一个 YAML 文件）。一个插件可以独立存在（仅一个标签页）。它们共同让你能够构建一个带有自定义 HUD 的完整视觉换肤 —— 捆绑的 `strike-freedom-cockpit` 演示正是这样做的。请参阅 [主题 + 插件组合演示](#combined-theme--plugin-demo)。
:::

---

## 目录

- [主题](#themes)
  - [快速开始 —— 你的第一个主题](#quick-start--your-first-theme)
  - [调色板、排版、布局](#palette-typography-layout)
  - [布局变体](#layout-variants)
  - [主题资源（图像作为 CSS 变量）](#theme-assets-images-as-css-vars)
  - [组件装饰覆盖](#component-chrome-overrides)
  - [颜色覆盖](#color-overrides)
  - [原始 `customCSS`](#raw-customcss)
  - [内置主题](#built-in-themes)
  - [完整主题 YAML 参考](#full-theme-yaml-reference)
- [插件](#plugins)
  - [快速开始 —— 你的第一个插件](#quick-start--your-first-plugin)
  - [目录结构](#directory-layout)
  - [清单参考](#manifest-reference)
  - [插件 SDK](#the-plugin-sdk)
  - [外壳插槽](#shell-slots)
  - [替换内置页面 (`tab.override`)](#replacing-built-in-pages-taboverride)
  - [增强内置页面（页面作用域插槽）](#augmenting-built-in-pages-page-scoped-slots)
  - [仅插槽插件 (`tab.hidden`)](#slot-only-plugins-tabhidden)
  - [后端 API 路由](#backend-api-routes)
  - [每个插件的自定义 CSS](#custom-css-per-plugin)
  - [插件发现与重载](#plugin-discovery--reload)
- [主题 + 插件组合演示](#combined-theme--plugin-demo)
- [API 参考](#api-reference)
- [故障排除](#troubleshooting)

---

## 主题

主题是存储在 `~/.hermes/dashboard-themes/` 目录下的 YAML 文件。文件名无关紧要（系统使用主题的 `name:` 字段），但惯例是 `<name>.yaml`。每个字段都是可选的 —— 缺失的键会回退到内置的 `default` 主题，因此一个主题可以小到只有一种颜色。

### 快速开始 —— 你的第一个主题

```bash
mkdir -p ~/.hermes/dashboard-themes
```

```yaml
# ~/.hermes/dashboard-themes/neon.yaml
name: neon
label: Neon
description: 黑色背景上的纯品红色

palette:
  background: "#000000"
  midground: "#ff00ff"
```

刷新仪表盘。点击标题栏中的调色板图标并选择 **Neon**。背景变为黑色，文本和强调色变为品红色，并且每个派生颜色（卡片、边框、柔和色、环状等）都通过 CSS 中的 `color-mix()` 从这个 2 色三元组重新计算得出。

这就是完整的入门指南：一个文件，两种颜色。下面的所有内容都是可选的细化。

### 调色板、排版、布局

这三个模块是主题的核心。每个都是独立的 —— 覆盖一个，保留其他。

#### 调色板（3 层）

调色板是一个三层颜色层，外加一个暖光晕晕影颜色和一个噪点颗粒乘数。仪表盘的设计系统级联通过 CSS `color-mix()` 从这个三元组派生出每个与 shadcn 兼容的 Token（卡片、弹出框、柔和色、边框、主色、破坏色、环状等）。覆盖三种颜色会级联影响整个 UI。

| 键 | 描述 |
|-----|-------------|
| `palette.background` | 最深的画布颜色 —— 通常接近黑色。决定页面背景和卡片填充。 |
| `palette.midground` | 主要文本和强调色。大多数 UI 装饰使用此颜色（前景文本、按钮轮廓、焦点环）。 |
| `palette.foreground` | 顶层高亮。默认主题将其设置为 alpha 为 0 的白色（不可见）；想要在顶部有明亮强调色的主题可以提高其 alpha 值。 |
| `palette.warmGlow` | 被 `<Backdrop />` 用作晕影颜色的 `rgba(...)` 字符串。 |
| `palette.noiseOpacity` | 0–1.2 的颗粒叠加层乘数。值越低越柔和，值越高越粗糙。 |

每一层接受 `{hex: "#RRGGBB", alpha: 0.0–1.0}` 或一个纯十六进制字符串（alpha 默认为 1.0）。

```yaml
palette:
  background:
    hex: "#05091a"
    alpha: 1.0
  midground: "#d8f0ff"          # 纯十六进制，alpha = 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0                    # 不可见的顶层
  warmGlow: "rgba(255, 199, 55, 0.24)"
  noiseOpacity: 0.7
```

#### 排版

| 键 | 类型 | 描述 |
|-----|------|-------------|
| `fontSans` | 字符串 | 用于正文的 CSS font-family 堆栈（应用于 `html`, `body`）。 |
| `fontMono` | 字符串 | 用于代码块、`<code>`、`.font-mono` 工具的 CSS font-family 堆栈。 |
| `fontDisplay` | 字符串 | 可选的标题/显示堆栈。回退到 `fontSans`。 |
| `fontUrl` | 字符串 | 可选的外部样式表 URL。在主题切换时作为 `<link rel="stylesheet">` 注入到 `<head>` 中。相同的 URL 不会被注入两次。适用于 Google Fonts、Bunny Fonts、自托管的 `@font-face` 样式表 —— 任何可链接的内容。 |
| `baseSize` | 字符串 | 根字体大小 —— 控制 rem 比例。例如 `"14px"`, `"16px"`。 |
| `lineHeight` | 字符串 | 默认行高。例如 `"1.5"`, `"1.65"`。 |
| `letterSpacing` | 字符串 | 默认字母间距。例如 `"0"`, `"0.01em"`, `"-0.01em"`。 |
```yaml
typography:
  fontSans: '"Orbitron", "Eurostile", "Impact", sans-serif'
  fontMono: '"Share Tech Mono", ui-monospace, monospace'
  fontDisplay: '"Orbitron", "Eurostile", sans-serif'
  fontUrl: "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Share+Tech+Mono&display=swap"
  baseSize: "14px"
  lineHeight: "1.5"
  letterSpacing: "0.04em"
```

#### 布局

| 键 | 值 | 描述 |
|-----|--------|-------------|
| `radius` | 任意 CSS 长度 (`"0"`, `"0.25rem"`, `"0.5rem"`, `"1rem"`, ...) | 圆角 Token。映射到 `--radius` 并级联到 `--radius-sm/md/lg/xl` — 所有圆角元素会一起变化。 |
| `density` | `compact` \| `comfortable` \| `spacious` | 应用于 `--spacing-mul` CSS 变量的间距乘数。`compact = 0.85×`, `comfortable = 1.0×` (默认), `spacious = 1.2×`。缩放 Tailwind 的基础间距，因此 padding、gap 和 space-between 工具类都会按比例变化。 |

```yaml
layout:
  radius: "0"
  density: compact
```

### 布局变体

`layoutVariant` 选择整体的外壳布局。缺失时默认为 `"standard"`。

| 变体 | 行为 |
|---------|-----------|
| `standard` | 单列，最大宽度 1600px (默认)。 |
| `cockpit` | 左侧边栏轨道 (260px) + 主要内容。由插件通过 `sidebar` 插槽填充 — 参见 [外壳插槽](#shell-slots)。没有插件时，轨道显示占位符。 |
| `tiled` | 移除最大宽度限制，使页面可以使用完整的视口宽度。 |

```yaml
layoutVariant: cockpit
```

当前变体通过 `document.documentElement.dataset.layoutVariant` 暴露，因此 `customCSS` 中的原始 CSS 可以通过 `:root[data-layout-variant="cockpit"] ...` 来定位它。

### 主题资源 (图片作为 CSS 变量)

随主题附带艺术作品的 URL。每个命名的插槽都会变成一个 CSS 变量 (`--theme-asset-<name>`)，内置外壳和任何插件都可以读取。`bg` 插槽会自动连接到背景；其他插槽面向插件。

```yaml
assets:
  bg: "https://example.com/hero-bg.jpg"           # 自动连接到 <Backdrop />
  hero: "/my-images/strike-freedom.png"           # 用于插件侧边栏
  crest: "/my-images/crest.svg"                   # 用于 header-left 插件
  logo: "/my-images/logo.png"
  sidebar: "/my-images/rail.png"
  header: "/my-images/header-art.png"
  custom:
    scanLines: "/my-images/scanlines.png"         # → --theme-asset-custom-scanLines
```

值接受：

- 裸 URL — 会自动包装在 `url(...)` 中。
- 预包装的 `url(...)`、`linear-gradient(...)`、`radial-gradient(...)` 表达式 — 按原样使用。
- `"none"` — 显式选择退出。

每个资源也会作为 `--theme-asset-<name>-raw` (未包装的 URL) 发出，以防插件需要将其传递给 `<img src>` 而不是 `background-image`。

插件可以通过纯 CSS 或 JS 读取这些：

```javascript
// 在插件插槽中
const hero = getComputedStyle(document.documentElement)
  .getPropertyValue("--theme-asset-hero").trim();
```

### 组件外观覆盖

`componentStyles` 无需编写 CSS 选择器即可重新设置单个外壳组件的样式。每个桶的条目会变成 CSS 变量 (`--component-<bucket>-<kebab-property>`)，由外壳的共享组件读取。因此 `card:` 覆盖应用于每个 `<Card>`，`header:` 应用于应用栏，等等。

```yaml
componentStyles:
  card:
    clipPath: "polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px)"
    background: "linear-gradient(180deg, rgba(10, 22, 52, 0.85), rgba(5, 9, 26, 0.92))"
    boxShadow: "inset 0 0 0 1px rgba(64, 200, 255, 0.28)"
  header:
    background: "linear-gradient(180deg, rgba(16, 32, 72, 0.95), rgba(5, 9, 26, 0.9))"
  tab:
    clipPath: "polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)"
  sidebar: {}
  backdrop: {}
  footer: {}
  progress: {}
  badge: {}
  page: {}
```

支持的桶：`card`, `header`, `footer`, `sidebar`, `tab`, `progress`, `badge`, `backdrop`, `page`。

属性名使用驼峰命名法 (`clipPath`) 并以短横线命名法 (`clip-path`) 发出。值是纯 CSS 字符串 — CSS 接受的任何内容 (`clip-path`, `border-image`, `background`, `box-shadow`, `animation`, ...)。

### 颜色覆盖

大多数主题不需要这个 — 三层调色板派生出所有 shadcn Token。当您需要一个派生无法产生的特定强调色时（例如柔和主题中更柔和的破坏性红色，或品牌特定的成功绿色），请使用 `colorOverrides`。

```yaml
colorOverrides:
  primary: "#ffce3a"
  primaryForeground: "#05091a"
  accent: "#3fd3ff"
  ring: "#3fd3ff"
  destructive: "#ff3a5e"
  border: "rgba(64, 200, 255, 0.28)"
```

支持的键：`card`, `cardForeground`, `popover`, `popoverForeground`, `primary`, `primaryForeground`, `secondary`, `secondaryForeground`, `muted`, `mutedForeground`, `accent`, `accentForeground`, `destructive`, `destructiveForeground`, `success`, `warning`, `border`, `input`, `ring`。

每个键都 1:1 映射到 `--color-<kebab>` CSS 变量 (例如 `primaryForeground` → `--color-primary-foreground`)。此处设置的任何键都会覆盖仅对活动主题的调色板级联 — 切换到另一个主题会清除覆盖。

### 原始 `customCSS`

对于 `componentStyles` 无法表达的选择器级外观 — 伪元素、动画、媒体查询、主题作用域覆盖 — 将原始 CSS 放入 `customCSS`：

```yaml
customCSS: |
  /* 扫描线叠加层 — 仅在 cockpit 变体激活时可见。 */
  :root[data-layout-variant="cockpit"] body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 100;
    background: repeating-linear-gradient(to bottom,
      transparent 0px, transparent 2px,
      rgba(64, 200, 255, 0.035) 3px, rgba(64, 200, 255, 0.035) 4px);
    mix-blend-mode: screen;
  }
```

CSS 在应用主题时作为单个作用域的 `<style data-hermes-theme-css>` 标签注入，并在切换主题时清理。**每个主题限制为 32 KiB。**

### 内置主题

每个内置主题都附带自己的调色板、排版和布局 — 切换会产生超越颜色之外的可见变化。
| 主题 | 调色板 | 字体 | 布局 |
|-------|---------|------------|--------|
| **Hermes 青绿色** (`default`) | 深青色 + 奶油色 | 系统字体栈，15px | 0.5rem 圆角，舒适 |
| **午夜** (`midnight`) | 深蓝紫色 | Inter + JetBrains Mono，14px | 0.75rem 圆角，舒适 |
| **余烬** (`ember`) | 暖绯红色 + 青铜色 | Spectral (衬线体) + IBM Plex Mono，15px | 0.25rem 圆角，舒适 |
| **单色** (`mono`) | 灰度 | IBM Plex Sans + IBM Plex Mono，13px | 无圆角，紧凑 |
| **赛博朋克** (`cyberpunk`) | 黑色背景霓虹绿 | 全部使用 Share Tech Mono，14px | 无圆角，紧凑 |
| **玫瑰** (`rose`) | 粉色 + 象牙色 | Fraunces (衬线体) + DM Mono，16px | 1rem 圆角，宽松 |

引用 Google Fonts 的主题（除 Hermes 青绿色外）按需加载样式表——首次切换到这些主题时，会向 `<head>` 中注入一个 `<link>` 标签。

### 完整主题 YAML 参考

所有配置项都在一个文件中——复制并删除你不需要的部分：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: Ocean Deep
description: Deep sea blues with coral accents

# 3层调色板（接受 {hex, alpha} 或纯 hex 值）
palette:
  background:
    hex: "#0a1628"
    alpha: 1.0
  midground:
    hex: "#a8d0ff"
    alpha: 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0.0
  warmGlow: "rgba(255, 107, 107, 0.35)"
  noiseOpacity: 0.7

typography:
  fontSans: "Poppins, system-ui, sans-serif"
  fontMono: "Fira Code, ui-monospace, monospace"
  fontDisplay: "Poppins, system-ui, sans-serif"   # 可选
  fontUrl: "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap"
  baseSize: "15px"
  lineHeight: "1.6"
  letterSpacing: "-0.003em"

layout:
  radius: "0.75rem"
  density: comfortable

layoutVariant: standard        # standard | cockpit | tiled

assets:
  bg: "https://example.com/ocean-bg.jpg"
  hero: "/my-images/kraken.png"
  crest: "/my-images/anchor.svg"
  logo: "/my-images/logo.png"
  custom:
    pattern: "/my-images/waves.svg"

componentStyles:
  card:
    boxShadow: "inset 0 0 0 1px rgba(168, 208, 255, 0.18)"
  header:
    background: "linear-gradient(180deg, rgba(10, 22, 40, 0.95), rgba(5, 9, 26, 0.9))"

colorOverrides:
  destructive: "#ff6b6b"
  ring: "#ff6b6b"

customCSS: |
  /* 任何额外的选择器级别调整 */
```

创建文件后刷新仪表板。从标题栏实时切换主题——点击调色板图标。选择会持久化到 `config.yaml` 中的 `dashboard.theme` 下，并在重新加载时恢复。

---

## 插件

仪表板插件是一个包含 `manifest.json`、预构建 JS 包以及可选 CSS 文件和带有 FastAPI 路由的 Python 文件的目录。插件与其他 Hermes 插件一起位于 `~/.hermes/plugins/<name>/` 中——仪表板扩展是该插件目录内的一个 `dashboard/` 子文件夹，因此一个插件可以通过一次安装同时扩展 CLI/消息网关和仪表板。

插件不捆绑 React 或 UI 组件。它们使用在 `window.__HERMES_PLUGIN_SDK__` 上公开的 **插件 SDK**。这使得插件包非常小（通常几 KB）并避免了版本冲突。

### 快速开始——你的第一个插件

创建目录结构：

```bash
mkdir -p ~/.hermes/plugins/my-plugin/dashboard/dist
```

编写清单：

```json
// ~/.hermes/plugins/my-plugin/dashboard/manifest.json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills"
  },
  "entry": "dist/index.js"
}
```

编写 JS 包（一个普通的 IIFE——无需构建步骤）：

```javascript
// ~/.hermes/plugins/my-plugin/dashboard/dist/index.js
(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardHeader, CardTitle, CardContent } = SDK.components;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin"),
      ),
      React.createElement(CardContent, null,
        React.createElement("p", { className: "text-sm text-muted-foreground" },
          "Hello from my custom dashboard tab.",
        ),
      ),
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

刷新仪表板——你的标签页出现在导航栏中，位于 **技能** 之后。

:::tip 跳过 React.createElement
如果你更喜欢 JSX，可以使用任何打包工具（esbuild、Vite、rollup），将 React 作为外部依赖并输出 IIFE。唯一硬性要求是最终文件是一个可通过 `<script>` 加载的单个 JS 文件。React 从不捆绑；它来自 `SDK.React`。
:::

### 目录布局

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml              # 可选——现有的 CLI/消息网关插件清单
├── __init__.py              # 可选——现有的 CLI/消息网关钩子
└── dashboard/               # 仪表板扩展
    ├── manifest.json        # 必需——标签页配置、图标、入口点
    ├── dist/
    │   ├── index.js         # 必需——预构建的 JS 包 (IIFE)
    │   └── style.css        # 可选——自定义 CSS
    └── plugin_api.py        # 可选——后端 API 路由 (FastAPI)
```

一个插件目录可以承载三个正交的扩展：

- `plugin.yaml` + `__init__.py` —— CLI/消息网关插件（[参见插件页面](./plugins)）。
- `dashboard/manifest.json` + `dashboard/dist/index.js` —— 仪表板 UI 插件。
- `dashboard/plugin_api.py` —— 仪表板后端路由。

它们都不是必需的；只包含你需要的层。

### 清单参考

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "description": "What this plugin does",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills",
    "override": "/",
    "hidden": false
  },
  "slots": ["sidebar", "header-left"],
  "entry": "dist/index.js",
  "css": "dist/style.css",
  "api": "plugin_api.py"
}
```

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 唯一的插件标识符。小写，允许连字符。用于 URL 和注册。 |
| `label` | 是 | 在导航标签页中显示的展示名称。 |
| `description` | 否 | 简短描述（显示在仪表板管理界面中）。 |
| `icon` | 否 | Lucide 图标名称。默认为 `Puzzle`。未知名称回退到 `Puzzle`。 |
| `version` | 否 | Semver 字符串。默认为 `0.0.0`。 |
| `tab.path` | 是 | 标签页的 URL 路径（例如 `/my-plugin`）。 |
| `tab.position` | 否 | 在何处插入标签页。`"end"`（默认）、`"after:<path>"` 或 `"before:<path>"`——冒号后的值是目标标签页的**路径段**（无前导斜杠）。例如：`"after:skills"`、`"before:config"`。 |
| `tab.override` | 否 | 设置为内置路由路径（`"/"`、`"/sessions"`、`"/config"`、...）以**替换**该页面，而不是添加新标签页。参见[替换内置页面](#replacing-built-in-pages-taboverride)。 |
| `tab.hidden` | 否 | 为 true 时，注册组件和任何插槽，但不向导航栏添加标签页。用于仅插槽插件。参见[仅插槽插件](#slot-only-plugins-tabhidden)。 |
| `slots` | 否 | 此插件填充的命名外壳插槽。**仅用于文档辅助**——实际的注册通过 JS 包中的 `registerSlot()` 进行。在此处列出插槽可以使发现界面信息更丰富。 |
| `entry` | 是 | JS 包相对于 `dashboard/` 的路径。默认为 `dist/index.js`。 |
| `css` | 否 | 要作为 `<link>` 标签注入的 CSS 文件路径。 |
| `api` | 否 | 包含 FastAPI 路由的 Python 文件路径。挂载在 `/api/plugins/<name>/`。 |
#### 可用图标

插件使用 Lucide 图标名称。仪表板按名称映射这些图标——未知名称会静默回退到 `Puzzle`。

当前已映射的图标：`Activity`, `BarChart3`, `Clock`, `Code`, `Database`, `Eye`, `FileText`, `Globe`, `Heart`, `KeyRound`, `MessageSquare`, `Package`, `Puzzle`, `Settings`, `Shield`, `Sparkles`, `Star`, `Terminal`, `Wrench`, `Zap`。

需要其他图标？请向 `web/src/App.tsx` 中的 `ICON_MAP` 提交 PR——这是一个纯增量的更改。

### 插件 SDK

插件所需的一切都在 `window.__HERMES_PLUGIN_SDK__` 上。插件永远不应直接导入 React。

```javascript
const SDK = window.__HERMES_PLUGIN_SDK__;

// React + hooks
SDK.React                    // React 实例
SDK.hooks.useState
SDK.hooks.useEffect
SDK.hooks.useCallback
SDK.hooks.useMemo
SDK.hooks.useRef
SDK.hooks.useContext
SDK.hooks.createContext

// UI 组件 (shadcn/ui 基础组件)
SDK.components.Card
SDK.components.CardHeader
SDK.components.CardTitle
SDK.components.CardContent
SDK.components.Badge
SDK.components.Button
SDK.components.Input
SDK.components.Label
SDK.components.Select
SDK.components.SelectOption
SDK.components.Separator
SDK.components.Tabs
SDK.components.TabsList
SDK.components.TabsTrigger
SDK.components.PluginSlot    // 渲染一个命名插槽（对嵌套插件 UI 有用）

// Hermes API 客户端 + 原始 fetcher
SDK.api                      // 类型化客户端 — getStatus, getSessions, getConfig, ...
SDK.fetchJSON                // 用于自定义端点（插件注册的路由）的原始 fetch

// 工具函数
SDK.utils.cn                 // Tailwind 类合并器 (clsx + twMerge)
SDK.utils.timeAgo            // 从 Unix 时间戳生成 "5分钟前"
SDK.utils.isoTimeAgo         // 从 ISO 字符串生成 "5分钟前"

// Hooks
SDK.useI18n                  // 用于多语言插件的 i18n hook
```

#### 调用插件的后端

```javascript
SDK.fetchJSON("/api/plugins/my-plugin/data")
  .then((data) => console.log(data))
  .catch((err) => console.error("API call failed:", err));
```

`fetchJSON` 会自动注入会话认证令牌，将错误作为异常抛出，并自动解析 JSON。

#### 调用内置的 Hermes 端点

```javascript
// Agent 状态
SDK.api.getStatus().then((s) => console.log("Version:", s.version));

// 最近会话
SDK.api.getSessions(10).then((resp) => console.log(resp.sessions.length));
```

完整列表请参见 [Web 仪表板 → REST API](./web-dashboard#rest-api)。

### Shell 插槽

插槽允许插件将组件注入到应用外壳的指定位置——驾驶舱侧边栏、页眉、页脚、覆盖层——而无需占用整个标签页。多个插件可以填充同一个插槽；它们会按照注册顺序堆叠渲染。

在插件包内注册：

```javascript
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sidebar", MySidebar);
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "header-left", MyCrest);
```

#### 插槽目录

**Shell 全局插槽**（在应用外壳的任何位置渲染）：

| 插槽 | 位置 |
|------|----------|
| `backdrop` | 在 `<Backdrop />` 层栈内部，位于噪点层之上。 |
| `header-left` | 顶部栏中 Hermes 品牌标识之前。 |
| `header-right` | 顶部栏中主题/语言切换器之前。 |
| `header-banner` | 导航栏下方的全宽条带。 |
| `sidebar` | 驾驶舱侧边栏轨道——**仅在 `layoutVariant === "cockpit"` 时渲染**。 |
| `pre-main` | 路由出口上方（在 `<main>` 内部）。 |
| `post-main` | 路由出口下方（在 `<main>` 内部）。 |
| `footer-left` | 页脚单元格内容（替换默认内容）。 |
| `footer-right` | 页脚单元格内容（替换默认内容）。 |
| `overlay` | 位于所有内容之上的固定定位层。对于 `customCSS` 无法单独实现的视觉效果（扫描线、晕影）很有用。 |

**页面作用域插槽**（仅在指定的内置页面上渲染——使用这些插槽可以在不覆盖整个路由的情况下，将小部件、卡片或工具栏注入到现有页面中）：

| 插槽 | 渲染位置 |
|------|------------------|
| `sessions:top` / `sessions:bottom` | `/sessions` 页面的顶部 / 底部。 |
| `analytics:top` / `analytics:bottom` | `/analytics` 页面的顶部 / 底部。 |
| `logs:top` / `logs:bottom` | `/logs` 页面的顶部（过滤器工具栏上方）/ 底部（日志查看器下方）。 |
| `cron:top` / `cron:bottom` | `/cron` 页面的顶部 / 底部。 |
| `skills:top` / `skills:bottom` | `/skills` 页面的顶部 / 底部。 |
| `config:top` / `config:bottom` | `/config` 页面的顶部 / 底部。 |
| `env:top` / `env:bottom` | `/env`（密钥）页面的顶部 / 底部。 |
| `docs:top` / `docs:bottom` | `/docs` 页面的顶部（iframe 上方）/ 底部。 |
| `chat:top` / `chat:bottom` | `/chat` 页面的顶部 / 底部（仅在启用嵌入式聊天时有效）。 |

示例——在 Sessions 页面顶部添加一个横幅卡片：

```javascript
function PinnedSessionsBanner() {
  return React.createElement(Card, null,
    React.createElement(CardContent, { className: "py-2 text-xs" },
      "Pinned note injected by my-plugin"),
  );
}

window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sessions:top", PinnedSessionsBanner);
```

如果你的插件仅增强现有页面而不需要自己的侧边栏标签页，可以将页面作用域插槽与 `tab.hidden: true` 结合使用。

Shell 仅针对上述插槽渲染 `<PluginSlot name="..." />`。注册表接受其他名称用于嵌套插件 UI——插件可以通过 `SDK.components.PluginSlot` 暴露自己的插槽。

#### 重新注册和 HMR

如果同一个 `(plugin, slot)` 对注册了两次，后一次调用会替换前一次——这与 React HMR 期望插件重新挂载的行为方式一致。

### 替换内置页面 (`tab.override`)

将 `tab.override` 设置为内置路由路径，会使插件的组件替换该页面，而不是添加新标签页。当主题想要自定义主页 (`/`) 但又想保持仪表板其余部分完整时很有用。

```json
{
  "name": "my-home",
  "label": "Home",
  "tab": {
    "path": "/my-home",
    "override": "/",
    "position": "end"
  },
  "entry": "dist/index.js"
}
```
设置 `override` 时：

- 路由器中 `/` 路径的原始页面组件将被移除。
- 你的插件将在 `/` 路径渲染。
- 不会为 `tab.path` 添加导航标签（覆盖本身就是目的）。

一个给定的路径只能被一个插件覆盖。如果两个插件声明覆盖同一路径，第一个生效，第二个将被忽略并在开发模式下发出警告。

如果你只需要向现有页面添加卡片或工具栏，而不是完全接管它，请使用[页面作用域插槽](#增强内置页面页面作用域插槽)。

### 增强内置页面（页面作用域插槽）

通过 `tab.override` 进行完全替换是重量级的——你的插件现在拥有整个页面，包括我们未来对该页面的任何更新。大多数时候，你只是想向现有页面添加横幅、卡片或工具栏。这就是**页面作用域插槽**的用途。

每个内置页面都暴露 `<page>:top` 和 `<page>:bottom` 插槽，分别在其内容区域的顶部和底部渲染。你的插件通过调用 `registerSlot()` 来填充一个插槽——内置页面继续正常工作，你的组件与它一起渲染。

可用插槽：`sessions:*`、`analytics:*`、`logs:*`、`cron:*`、`skills:*`、`config:*`、`env:*`、`docs:*`、`chat:*`（每个都有 `:top` 和 `:bottom`）。完整目录请参见 [Shell 插槽 → 插槽目录](#slot-catalogue)。

最小示例——在 Sessions 页面顶部固定一个横幅：

```json
// ~/.hermes/plugins/session-notes/dashboard/manifest.json
{
  "name": "session-notes",
  "label": "Session Notes",
  "tab": { "path": "/session-notes", "hidden": true },
  "slots": ["sessions:top"],
  "entry": "dist/index.js"
}
```

```javascript
// ~/.hermes/plugins/session-notes/dashboard/dist/index.js
(function () {
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardContent } = SDK.components;

  function Banner() {
    return React.createElement(Card, null,
      React.createElement(CardContent, { className: "py-2 text-xs" },
        "Remember to label important sessions before archiving."),
    );
  }

  // 隐藏标签页的占位符。
  window.__HERMES_PLUGINS__.register("session-notes", function () { return null; });

  // 实际工作。
  window.__HERMES_PLUGINS__.registerSlot("session-notes", "sessions:top", Banner);
})();
```

关键点：

- `tab.hidden: true` 使插件不出现在侧边栏中——它没有独立的页面。
- `slots` 清单字段仅用于文档说明。实际的绑定通过 JS 包中的 `registerSlot()` 进行。
- 多个插件可以声明同一个页面作用域插槽。它们按照注册顺序堆叠渲染。
- 当没有插件注册时，零占用：内置页面完全按原样渲染。

捆绑的 `example-dashboard` 插件提供了一个实时演示，向 `sessions:top` 注入一个横幅——安装它以端到端地查看此模式。

### 仅插槽插件 (`tab.hidden`)

当 `tab.hidden: true` 时，插件会注册其组件（用于直接 URL 访问）和任何插槽，但永远不会向导航添加标签页。用于那些仅为了注入插槽而存在的插件——例如页头徽章、侧边栏 HUD、覆盖层。

```json
{
  "name": "header-crest",
  "label": "Header Crest",
  "tab": {
    "path": "/header-crest",
    "position": "end",
    "hidden": true
  },
  "slots": ["header-left"],
  "entry": "dist/index.js"
}
```

JS 包仍然会调用 `register()` 并传入一个占位符组件（以防有人直接访问该 URL，这是良好实践），然后调用 `registerSlot()` 来完成实际工作。

### 后端 API 路由

插件可以通过在清单中设置 `api` 来注册 FastAPI 路由。创建文件并导出一个 `router`：

```python
# ~/.hermes/plugins/my-plugin/dashboard/plugin_api.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/data")
async def get_data():
    return {"items": ["one", "two", "three"]}

@router.post("/action")
async def do_action(body: dict):
    return {"ok": True, "received": body}
```

路由挂载在 `/api/plugins/<name>/` 下，因此上述代码变为：

- `GET  /api/plugins/my-plugin/data`
- `POST /api/plugins/my-plugin/action`

插件 API 路由绕过会话令牌认证，因为仪表板服务器默认绑定到 localhost。**如果你运行不受信任的插件，请不要使用 `--host 0.0.0.0` 将仪表板暴露在公共接口上**——它们的路由也会变得可访问。

#### 访问 Hermes 内部

后端路由在仪表板进程内运行，因此它们可以直接从 hermes-agent 代码库导入：

```python
from fastapi import APIRouter
from hermes_state import SessionDB
from hermes_cli.config import load_config

router = APIRouter()

@router.get("/session-count")
async def session_count():
    db = SessionDB()
    try:
        count = len(db.list_sessions(limit=9999))
        return {"count": count}
    finally:
        db.close()

@router.get("/config-snapshot")
async def config_snapshot():
    cfg = load_config()
    return {"model": cfg.get("model", {})}
```

### 每个插件的自定义 CSS

如果你的插件需要超出 Tailwind 类和内联 `style=` 的样式，请添加一个 CSS 文件并在清单中引用它：

```json
{
  "css": "dist/style.css"
}
```

该文件在插件加载时作为 `<link>` 标签注入。使用特定的类名以避免与仪表板样式冲突，并引用仪表板的 CSS 变量以保持主题感知：

```css
/* dist/style.css */
.my-plugin-chart {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-card-foreground);
  padding: 1rem;
}
.my-plugin-chart:hover {
  border-color: var(--color-ring);
}
```

仪表板将每个 shadcn token 暴露为 `--color-*`，外加主题额外变量（`--theme-asset-*`、`--component-<bucket>-*`、`--radius`、`--spacing-mul`）。引用这些变量，你的插件将自动根据活动主题重新换肤。

### 插件发现与重载

仪表板扫描三个目录以查找 `dashboard/manifest.json`：

| 优先级 | 目录 | 来源标签 |
|----------|-----------|--------------|
| 1 (冲突时胜出) | `~/.hermes/plugins/<name>/dashboard/` | `user` |
| 2 | `<repo>/plugins/memory/<name>/dashboard/` | `bundled` |
| 2 | `<repo>/plugins/<name>/dashboard/` | `bundled` |
| 3 | `./.hermes/plugins/<name>/dashboard/` | `project` —— 仅在设置 `HERMES_ENABLE_PROJECT_PLUGINS` 时启用 |
发现结果按每个仪表板进程缓存。添加新插件后，需要：

```bash
# 强制重新扫描而不重启
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

…或者重启 `hermes dashboard`。

#### 插件加载生命周期

1.  仪表板加载。`main.tsx` 将 SDK 暴露在 `window.__HERMES_PLUGIN_SDK__` 上，将注册表暴露在 `window.__HERMES_PLUGINS__` 上。
2.  `App.tsx` 调用 `usePlugins()` → 获取 `GET /api/dashboard/plugins`。
3.  对于每个清单：注入 CSS `<link>`（如果已声明），然后通过 `<script>` 标签加载 JS 包。
4.  插件的 IIFE 运行并调用 `window.__HERMES_PLUGINS__.register(name, Component)` —— 并且可选地为每个插槽调用 `.registerSlot(name, slot, Component)`。
5.  仪表板根据清单解析已注册的组件，将标签页添加到导航（除非是 `hidden`），并将组件作为路由挂载。

插件在其脚本加载后最多有 **2 秒** 的时间来调用 `register()`。之后，仪表板将停止等待并完成初始渲染。如果插件稍后注册，它仍然会出现——导航是响应式的。

如果插件的脚本加载失败（404、语法错误、IIFE 期间异常），仪表板会向浏览器控制台记录警告并继续运行，不加载该插件。

---

## 主题 + 插件组合演示

仓库附带了 `plugins/strike-freedom-cockpit/` 作为一个完整的重新设计演示。它将一个主题 YAML 与一个仅包含插槽的插件配对，无需分叉仪表板即可生成驾驶舱风格的 HUD。

**它演示了：**

*   一个完整的主题，使用了调色板、排版、`fontUrl`、`layoutVariant: cockpit`、`assets`、`componentStyles`（带缺口的卡片角、渐变背景）、`colorOverrides` 和 `customCSS`（扫描线覆盖层）。
*   一个仅包含插槽的插件（`tab.hidden: true`），它注册到三个插槽：
    *   `sidebar` —— 一个 MS-STATUS 面板，带有由 `SDK.api.getStatus()` 驱动的实时遥测条。
    *   `header-left` —— 一个派系徽章，从活动主题读取 `--theme-asset-crest`。
    *   `footer-right` —— 一个自定义标语，替换默认的组织行。
*   该插件通过 CSS 变量读取主题提供的艺术作品，因此切换主题会更改英雄/徽章，而无需更改插件代码。

**安装：**

```bash
# 主题
cp plugins/strike-freedom-cockpit/theme/strike-freedom.yaml \
   ~/.hermes/dashboard-themes/

# 插件
cp -r plugins/strike-freedom-cockpit ~/.hermes/plugins/
```

打开仪表板，从主题切换器中选择 **Strike Freedom**。驾驶舱侧边栏出现，徽章显示在标题中，标语替换了页脚。切换回 **Hermes Teal**，插件保持安装但不可见（`sidebar` 插槽仅在 `cockpit` 布局变体下渲染）。

阅读插件源代码（`plugins/strike-freedom-cockpit/dashboard/dist/index.js`）以了解它如何读取 CSS 变量、防范不支持插槽的旧版仪表板，以及从一个包中注册三个插槽。

---

## API 参考

### 主题端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题 + 活动主题名称。内置主题返回 `{name, label, description}`；用户主题还包括一个 `definition` 字段，包含完整的规范化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置活动主题。请求体：`{"name": "midnight"}`。持久化到 `config.yaml` 中的 `dashboard.theme` 下。 |

### 插件端点

| 端点 | Method | 描述 |
|----------|--------|-------------|
| `/api/dashboard/plugins` | GET | 列出发现的插件（包含清单，不包括内部字段）。 |
| `/api/dashboard/plugins/rescan` | GET | 强制重新扫描插件目录而不重启。 |
| `/dashboard-plugins/<name>/<path>` | GET | 从插件的 `dashboard/` 目录提供静态资源。路径遍历被阻止。 |
| `/api/plugins/<name>/*` | * | 插件注册的后端路由。 |

### `window` 上的 SDK

| 全局变量 | 类型 | 提供者 |
|--------|------|----------|
| `window.__HERMES_PLUGIN_SDK__` | object | `registry.ts` —— React、hooks、UI 组件、API 客户端、工具函数。 |
| `window.__HERMES_PLUGINS__.register(name, Component)` | function | 注册插件的主组件。 |
| `window.__HERMES_PLUGINS__.registerSlot(name, slot, Component)` | function | 注册到指定的外壳插槽。 |

---

## 故障排除

**我的主题没有出现在选择器中。**
检查文件是否在 `~/.hermes/dashboard-themes/` 中，并且以 `.yaml` 或 `.yml` 结尾。刷新页面。运行 `curl http://127.0.0.1:9119/api/dashboard/themes` —— 你的主题应该出现在响应中。如果 YAML 有解析错误，仪表板会记录到 `~/.hermes/logs/` 下的 `errors.log`。

**我的插件标签页没有显示。**
1.  检查清单是否在 `~/.hermes/plugins/<name>/dashboard/manifest.json`（注意 `dashboard/` 子目录）。
2.  `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan` 强制重新发现。
3.  打开浏览器开发者工具 → 网络 —— 确认 `manifest.json`、`index.js` 和任何 CSS 已加载且没有 404 错误。
4.  打开浏览器开发者工具 → 控制台 —— 查找 IIFE 期间或 `window.__HERMES_PLUGINS__ is undefined` 的错误（表明 SDK 未初始化，通常是之前 React 渲染崩溃）。
5.  验证你的包调用 `window.__HERMES_PLUGINS__.register(...)` 时使用的 **名称** 与 `manifest.json:name` 相同。

**注册到插槽的组件没有渲染。**
`sidebar` 插槽仅在活动主题具有 `layoutVariant: cockpit` 时渲染。其他插槽始终渲染。如果你注册到一个没有匹配项的插槽，请在 `registerSlot` 内部添加 `console.log` 以确认插件包确实运行了。

**插件后端路由返回 404。**
1.  确认清单中的 `"api": "plugin_api.py"` 指向 `dashboard/` 内的现有文件。
2.  重启 `hermes dashboard` —— 插件 API 路由在启动时挂载一次，**不会**在重新扫描时挂载。
3.  检查 `plugin_api.py` 是否导出了一个模块级别的 `router = APIRouter()`。其他导出名称不会被识别。
4.  跟踪 `~/.hermes/logs/errors.log` 中的 `Failed to load plugin <name> API routes` —— 导入错误会记录在那里。
**主题切换会丢失我的颜色覆盖设置。**
`colorOverrides` 的作用域仅限于当前激活的主题，并在切换主题时被清除——这是设计如此。如果你希望覆盖设置持久化，请将它们放在主题的 YAML 文件中，而不是在实时切换器中。

**主题的 customCSS 被截断。**
每个主题的 `customCSS` 块大小上限为 32 KiB。请将大型样式表拆分到多个主题中，或者改用通过其 `css` 字段注入完整样式表的插件（无大小限制）。

**我想在 PyPI 上发布一个插件。**
Dashboard 插件是通过目录结构安装的，而不是通过 pip 入口点。目前最简洁的分发方式是让用户将 git 仓库克隆到 `~/.hermes/plugins/` 目录下。目前还没有为 dashboard 插件配置基于 pip 的安装程序。