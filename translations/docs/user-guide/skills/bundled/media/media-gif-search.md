---
title: "Gif Search — 通过 curl + jq 从 Tenor 搜索/下载 GIF"
sidebar_label: "Gif Search"
description: "通过 curl + jq 从 Tenor 搜索/下载 GIF"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Gif Search

通过 curl + jq 从 Tenor 搜索/下载 GIF。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/gif-search` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GIF`, `Media`, `Search`, `Tenor`, `API` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GIF 搜索 (Tenor API)

使用 curl 通过 Tenor API 直接搜索和下载 GIF。无需额外工具。

## 使用场景

适用于查找表情包 GIF、创建视觉内容以及在聊天中发送 GIF。

## 设置

在您的环境变量中设置 Tenor API 密钥（添加到 `~/.hermes/.env`）：

```bash
TENOR_API_KEY=your_key_here
```

在 https://developers.google.com/tenor/guides/quickstart 获取免费的 API 密钥 — Google Cloud Console 的 Tenor API 密钥是免费的，并且有宽松的速率限制。

## 先决条件

- `curl` 和 `jq`（两者在 macOS/Linux 上都是标准工具）
- `TENOR_API_KEY` 环境变量

## 搜索 GIF

```bash
# 搜索并获取 GIF URL
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# 获取较小/预览版本
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## 下载 GIF

```bash
# 搜索并下载排名第一的结果
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## 获取完整元数据

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

## API 参数

| 参数 | 描述 |
|-----------|-------------|
| `q` | 搜索查询（空格用 `+` URL 编码） |
| `limit` | 最大结果数（1-50，默认 20） |
| `key` | API 密钥（来自 `$TENOR_API_KEY` 环境变量） |
| `media_filter` | 格式过滤器：`gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | 安全级别：`off`, `low`, `medium`, `high` |
| `locale` | 语言：`en_US`, `es`, `fr` 等。 |

## 可用的媒体格式

每个结果在 `.media_formats` 下都有多种格式：

| 格式 | 使用场景 |
|--------|----------|
| `gif` | 全质量 GIF |
| `tinygif` | 小型预览 GIF |
| `mp4` | 视频版本（文件更小） |
| `tinymp4` | 小型预览视频 |
| `webm` | WebM 视频 |
| `nanogif` | 微型缩略图 |

## 注意事项

- 对查询进行 URL 编码：空格用 `+`，特殊字符用 `%XX`
- 对于在聊天中发送，`tinygif` URL 更轻量
- GIF URL 可以直接在 markdown 中使用：`![alt](https://github.com/NousResearch/hermes-agent/blob/main/skills/media/gif-search/url)`