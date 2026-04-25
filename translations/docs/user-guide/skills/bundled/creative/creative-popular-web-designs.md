---
title: "热门网页设计 — 从真实网站提取的 54 个生产级设计系统"
sidebar_label: "热门网页设计"
description: "从真实网站提取的 54 个生产级设计系统"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 热门网页设计

从真实网站提取的 54 个生产级设计系统。加载模板以生成与 Stripe、Linear、Vercel、Notion、Airbnb 等网站视觉识别相匹配的 HTML/CSS。每个模板都包含颜色、排版、组件、布局规则和可直接使用的 CSS 值。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/popular-web-designs` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium（设计系统源自 VoltAgent/awesome-design-md） |
| 许可证 | MIT |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 热门网页设计

54 个真实世界的设计系统，可在生成 HTML/CSS 时使用。每个模板都捕捉了网站的完整视觉语言：调色板、排版层次结构、组件样式、间距系统、阴影、响应式行为以及包含确切 CSS 值的实用 Agent 提示词。

## 使用方法

1.  从下面的目录中选择一个设计
2.  加载它：`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`
3.  在生成 HTML 时使用设计 Token 和组件规范
4.  与 `generative-widgets` 技能配合使用，通过 cloudflared 隧道提供结果

每个模板顶部都包含一个 **Hermes 实现说明** 块，其中包含：
- CDN 字体替代品和 Google Fonts `<link>` 标签（可直接粘贴）
- 主要字体和等宽字体的 CSS font-family 堆栈
- 使用 `write_file` 创建 HTML 和使用 `browser_vision` 进行验证的提醒

## HTML 生成模式

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <!-- 从模板的 Hermes 说明中粘贴 Google Fonts <link> -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* 将模板的调色板应用为 CSS 自定义属性 */
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
      /* ... 更多来自模板第 2 节 */
    }
    /* 应用模板第 3 节的排版 */
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
    /* 应用模板第 4 节的组件样式 */
    /* 应用模板第 5 节的布局 */
    /* 应用模板第 6 节的阴影 */
  </style>
</head>
<body>
  <!-- 使用模板中的组件规范进行构建 -->
</body>
</html>
```

使用 `write_file` 写入文件，通过 `generative-widgets` 工作流（cloudflared 隧道）提供服务，并使用 `browser_vision` 验证结果以确保视觉准确性。

## 字体替代参考

大多数网站使用无法通过 CDN 获取的专有字体。每个模板都映射到一个 Google Fonts 替代字体，以保留设计的特征。常见映射：

| 专有字体 | CDN 替代字体 | 特征 |
|---|---|---|
| Geist / Geist Sans | Geist（在 Google Fonts 上） | 几何形状，压缩字距 |
| Geist Mono | Geist Mono（在 Google Fonts 上） | 简洁等宽字体，连字 |
| sohne-var (Stripe) | Source Sans 3 | 轻量级优雅 |
| Berkeley Mono | JetBrains Mono | 技术等宽字体 |
| Airbnb Cereal VF | DM Sans | 圆润、友好的几何形状 |
| Circular (Spotify) | DM Sans | 几何形状，温暖 |
| figmaSans | Inter | 简洁的人文主义字体 |
| Pin Sans (Pinterest) | DM Sans | 友好、圆润 |
| NVIDIA-EMEA | Inter（或 Arial 系统字体） | 工业风、简洁 |
| CoinbaseDisplay/Sans | DM Sans | 几何形状，值得信赖 |
| UberMove | DM Sans | 粗体、紧凑 |
| HashiCorp Sans | Inter | 企业级、中性 |
| waldenburgNormal (Sanity) | Space Grotesk | 几何形状，略微紧缩 |
| IBM Plex Sans/Mono | IBM Plex Sans/Mono | 可在 Google Fonts 上获取 |
| Rubik (Sentry) | Rubik | 可在 Google Fonts 上获取 |

当模板的 CDN 字体与原始字体匹配时（Inter、IBM Plex、Rubik、Geist），不会发生替代损失。当使用替代字体时（DM Sans 替代 Circular，Source Sans 3 替代 sohne-var），请严格遵循模板的字重、字号和字母间距值——这些比特定的字体外观更能体现视觉识别特征。

## 设计目录

### AI 与机器学习

| 模板 | 网站 | 风格 |
|---|---|---|
| `claude.md` | Anthropic Claude | 暖色调陶土色点缀，简洁的编辑布局 |
| `cohere.md` | Cohere | 鲜艳的渐变，数据丰富的仪表板美学 |
| `elevenlabs.md` | ElevenLabs | 暗色电影感 UI，音频波形美学 |
| `minimax.md` | Minimax | 大胆的暗色界面，霓虹色点缀 |
| `mistral.ai.md` | Mistral AI | 法式工程极简主义，紫色调 |
| `ollama.md` | Ollama | 终端优先，单色简约 |
| `opencode.ai.md` | OpenCode AI | 以开发者为中心的暗色主题，全等宽字体 |
| `replicate.md` | Replicate | 简洁的白色画布，代码导向 |
| `runwayml.md` | RunwayML | 电影感暗色 UI，媒体丰富的布局 |
| `together.ai.md` | Together AI | 技术性，蓝图风格设计 |
| `voltagent.md` | VoltAgent | 虚空黑色画布，祖母绿点缀，终端原生 |
| `x.ai.md` | xAI | 鲜明的单色，未来主义极简风格，全等宽字体 |

### 开发者工具与平台

| 模板 | 网站 | 风格 |
|---|---|---|
| `cursor.md` | Cursor | 时尚的暗色界面，渐变点缀 |
| `expo.md` | Expo | 暗色主题，紧凑的字距，以代码为中心 |
| `linear.app.md` | Linear | 极致简约的暗色模式，精确，紫色点缀 |
| `lovable.md` | Lovable | 活泼的渐变，友好的开发者美学 |
| `mintlify.md` | Mintlify | 简洁，绿色点缀，阅读优化 |
| `posthog.md` | PostHog | 活泼的品牌形象，开发者友好的暗色 UI |
| `raycast.md` | Raycast | 时尚的暗色铬合金风格，鲜艳的渐变点缀 |
| `resend.md` | Resend | 简约的暗色主题，等宽字体点缀 |
| `sentry.md` | Sentry | 暗色仪表板，数据密集，粉紫色点缀 |
| `supabase.md` | Supabase | 暗祖母绿主题，代码优先的开发者工具 |
| `superhuman.md` | Superhuman | 高级暗色 UI，键盘优先，紫色辉光 |
| `vercel.md` | Vercel | 黑白精确，Geist 字体系统 |
| `warp.md` | Warp | 暗色 IDE 风格界面，基于块的命令 UI |
| `zapier.md` | Zapier | 温暖的橙色，友好的插图驱动 |

### 基础设施与云

| 模板 | 网站 | 风格 |
|---|---|---|
| `clickhouse.md` | ClickHouse | 黄色点缀，技术文档风格 |
| `composio.md` | Composio | 现代暗色风格，多彩的集成图标 |
| `hashicorp.md` | HashiCorp | 企业级简洁，黑白配色 |
| `mongodb.md` | MongoDB | 绿色叶子品牌形象，以开发者文档为中心 |
| `sanity.md` | Sanity | 红色点缀，内容优先的编辑布局 |
| `stripe.md` | Stripe | 标志性的紫色渐变，字重 300 的优雅 |

### 设计与生产力

| 模板 | 网站 | 风格 |
|---|---|---|
| `airtable.md` | Airtable | 多彩、友好、结构化数据美学 |
| `cal.md` | Cal.com | 简洁的中性 UI，面向开发者的简约 |
| `clay.md` | Clay | 有机形状，柔和渐变，艺术指导的布局 |
| `figma.md` | Figma | 鲜艳的多彩色，活泼而专业 |
| `framer.md` | Framer | 大胆的黑蓝配色，动效优先，设计导向 |
| `intercom.md` | Intercom | 友好的蓝色调色板，对话式 UI 模式 |
| `miro.md` | Miro | 明亮的黄色点缀，无限画布美学 |
| `notion.md` | Notion | 温暖的极简主义，衬线标题，柔和表面 |
| `pinterest.md` | Pinterest | 红色点缀，瀑布流网格，图片优先布局 |
| `webflow.md` | Webflow | 蓝色点缀，精致的营销网站美学 |

### 金融科技与加密货币

| 模板 | 网站 | 风格 |
|---|---|---|
| `coinbase.md` | Coinbase | 简洁的蓝色标识，注重信任，机构感 |
| `kraken.md` | Kraken | 紫色点缀的暗色 UI，数据密集的仪表板 |
| `revolut.md` | Revolut | 时尚的暗色界面，渐变卡片，金融科技精度 |
| `wise.md` | Wise | 明亮的绿色点缀，友好且清晰 |

### 企业与消费级

| 模板 | 网站 | 风格 |
|---|---|---|
| `airbnb.md` | Airbnb | 温暖的珊瑚色点缀，摄影驱动，圆润 UI |
| `apple.md` | Apple | 高级留白，SF Pro 字体，电影感图像 |
| `bmw.md` | BMW | 暗色高级表面，精确的工程美学 |
| `ibm.md` | IBM | Carbon 设计系统，结构化的蓝色调色板 |
| `nvidia.md` | NVIDIA | 绿黑色能量，技术力量美学 |
| `spacex.md` | SpaceX | 鲜明的黑白配色，全出血图像，未来感 |
| `spotify.md` | Spotify | 暗色背景上的鲜艳绿色，粗体字体，专辑封面驱动 |
| `uber.md` | Uber | 大胆的黑白配色，紧凑字体，都市能量 |

## 选择设计

根据内容匹配设计：

-   **开发者工具 / 仪表板：** Linear、Vercel、Supabase、Raycast、Sentry
-   **文档 / 内容网站：** Mintlify、Notion、Sanity、MongoDB
-   **营销 / 落地页：** Stripe、Framer、Apple、SpaceX
-   **暗色模式 UI：** Linear、Cursor、ElevenLabs、Warp、Superhuman
-   **浅色 / 简洁 UI：** Vercel、Stripe、Notion、Cal.com、Replicate
-   **活泼 / 友好：** PostHog、Figma、Lovable、Zapier、Miro
-   **高级 / 奢华：** Apple、BMW、Stripe、Superhuman、Revolut
-   **数据密集 / 仪表板：** Sentry、Kraken、Cohere、ClickHouse
-   **等宽字体 / 终端美学：** Ollama、OpenCode、x.ai、VoltAgent