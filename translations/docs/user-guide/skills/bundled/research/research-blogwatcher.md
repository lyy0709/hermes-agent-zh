---
title: "Blogwatcher — 通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
sidebar_label: "Blogwatcher"
description: "通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blogwatcher

通过 `blogwatcher-cli` 工具监控博客和 RSS/Atom 订阅源。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/blogwatcher` |
| 版本 | `2.0.0` |
| 作者 | JulienTant (fork of Hyaxia/blogwatcher) |
| 许可证 | MIT |
| 标签 | `RSS`, `Blogs`, `Feed-Reader`, `Monitoring` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Blogwatcher

使用 `blogwatcher-cli` 工具跟踪博客和 RSS/Atom 订阅源的更新。支持自动发现订阅源、HTML 抓取回退、OPML 导入以及已读/未读文章管理。

## 安装

选择一种方法：

- **Go:** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker:** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **二进制文件 (Linux amd64):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件 (Linux arm64):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件 (macOS Apple Silicon):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件 (macOS Intel):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

所有版本：https://github.com/JulienTant/blogwatcher-cli/releases

### 使用持久化存储的 Docker

默认情况下，数据库位于 `~/.blogwatcher-cli/blogwatcher-cli.db`。在 Docker 中，容器重启后此数据会丢失。使用 `BLOGWATCHER_DB` 或卷挂载来持久化数据：

```bash
# 命名卷（最简单）
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# 主机绑定挂载
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

### 从原始 blogwatcher 迁移

如果从 `Hyaxia/blogwatcher` 升级，请移动您的数据库：

```bash
mv ~/.blogwatcher/blogwatcher.db ~/.blogwatcher-cli/blogwatcher-cli.db
```

二进制文件名已从 `blogwatcher` 更改为 `blogwatcher-cli`。

## 常用命令

### 管理博客

- 添加博客：`blogwatcher-cli add "My Blog" https://example.com`
- 添加并指定订阅源：`blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- 添加并使用 HTML 抓取：`blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- 列出跟踪的博客：`blogwatcher-cli blogs`
- 移除博客：`blogwatcher-cli remove "My Blog" --yes`
- 从 OPML 导入：`blogwatcher-cli import subscriptions.opml`

### 扫描和阅读

- 扫描所有博客：`blogwatcher-cli scan`
- 扫描单个博客：`blogwatcher-cli scan "My Blog"`
- 列出未读文章：`blogwatcher-cli articles`
- 列出所有文章：`blogwatcher-cli articles --all`
- 按博客筛选：`blogwatcher-cli articles --blog "My Blog"`
- 按类别筛选：`blogwatcher-cli articles --category "Engineering"`
- 标记文章为已读：`blogwatcher-cli read 1`
- 标记文章为未读：`blogwatcher-cli unread 1`
- 标记所有文章为已读：`blogwatcher-cli read-all`
- 标记某个博客的所有文章为已读：`blogwatcher-cli read-all --blog "My Blog" --yes`

## 环境变量

所有标志都可以通过带有 `BLOGWATCHER_` 前缀的环境变量设置：

| 变量 | 描述 |
|---|---|
| `BLOGWATCHER_DB` | SQLite 数据库文件路径 |
| `BLOGWATCHER_WORKERS` | 并发扫描工作线程数（默认：8） |
| `BLOGWATCHER_SILENT` | 扫描时仅输出 "scan done" |
| `BLOGWATCHER_YES` | 跳过确认提示 |
| `BLOGWATCHER_CATEGORY` | 按类别筛选文章的默认过滤器 |

## 示例输出

```
$ blogwatcher-cli blogs
跟踪的博客 (1):

  xkcd
    URL: https://xkcd.com
    Feed: https://xkcd.com/atom.xml
    最后扫描时间: 2026-04-03 10:30
```

```
$ blogwatcher-cli scan
正在扫描 1 个博客...

  xkcd
    来源: RSS | 找到: 4 | 新文章: 4

总共找到 4 篇新文章！
```

```
$ blogwatcher-cli articles
未读文章 (2):

  [1] [new] Barrel - Part 13
       博客: xkcd
       URL: https://xkcd.com/3095/
       发布日期: 2026-04-02
       类别: Comics, Science

  [2] [new] Volcano Fact
       博客: xkcd
       URL: https://xkcd.com/3094/
       发布日期: 2026-04-01
       类别: Comics
```

## 说明

- 当未提供 `--feed-url` 时，会自动从博客主页发现 RSS/Atom 订阅源。
- 如果 RSS 失败且配置了 `--scrape-selector`，则回退到 HTML 抓取。
- 来自 RSS/Atom 订阅源的类别会被存储，并可用于筛选文章。
- 从 Feedly、Inoreader、NewsBlur 等导出的 OPML 文件批量导入博客。
- 数据库默认存储在 `~/.blogwatcher-cli/blogwatcher-cli.db`（可通过 `--db` 或 `BLOGWATCHER_DB` 覆盖）。
- 使用 `blogwatcher-cli <command> --help` 来发现所有标志和选项。