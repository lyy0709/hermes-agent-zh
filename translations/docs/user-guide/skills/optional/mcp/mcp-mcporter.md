---
title: "Mcporter"
sidebar_label: "Mcporter"
description: "使用 mcporter CLI 直接列出、配置、授权和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Mcporter

使用 mcporter CLI 直接列出、配置、授权和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mcp/mcporter` 安装 |
| 路径 | `optional-skills/mcp/mcporter` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 标签 | `MCP`, `Tools`, `API`, `Integrations`, `Interop` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# mcporter

使用 `mcporter` 直接在终端中探索、调用和管理 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 服务器和工具。

## 先决条件

需要 Node.js：
```bash
# 无需安装（通过 npx 运行）
npx mcporter list

# 或全局安装
npm install -g mcporter
```

## 快速开始

```bash
# 列出此机器上已配置的 MCP 服务器
mcporter list

# 列出特定服务器的工具及其模式详情
mcporter list <server> --schema

# 调用一个工具
mcporter call <server.tool> key=value
```

## 发现 MCP 服务器

mcporter 会自动发现机器上由其他 MCP 客户端（Claude Desktop、Cursor 等）配置的服务器。要查找新的服务器使用，可以浏览像 [mcpfinder.dev](https://mcpfinder.dev) 或 [mcp.so](https://mcp.so) 这样的注册表，然后临时连接：

```bash
# 通过 URL 连接到任何 MCP 服务器（无需配置）
mcporter list --http-url https://some-mcp-server.com --name my_server

# 或即时运行一个 stdio 服务器
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem" --name fs
```

## 调用工具

```bash
# Key=value 语法
mcporter call linear.list_issues team=ENG limit:5

# 函数语法
mcporter call "linear.create_issue(title: \"Bug fix needed\")"

# 临时 HTTP 服务器（无需配置）
mcporter call https://api.example.com/mcp.fetch url=https://example.com

# 临时 stdio 服务器
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com

# JSON 负载
mcporter call <server.tool> --args '{"limit": 5}'

# 机器可读输出（推荐用于 Hermes）
mcporter call <server.tool> key=value --output json
```

## 授权和配置

```bash
# 为服务器进行 OAuth 登录
mcporter auth <server | url> [--reset]

# 管理配置
mcporter config list
mcporter config get <key>
mcporter config add <server>
mcporter config remove <server>
mcporter config import <path>
```

配置文件位置：`./config/mcporter.json`（可使用 `--config` 覆盖）。

## 守护进程

用于持久化服务器连接：
```bash
mcporter daemon start
mcporter daemon status
mcporter daemon stop
mcporter daemon restart
```

## 代码生成

```bash
# 为 MCP 服务器生成 CLI 包装器
mcporter generate-cli --server <name>
mcporter generate-cli --command <url>

# 检查生成的 CLI
mcporter inspect-cli <path> [--json]

# 生成 TypeScript 类型/客户端
mcporter emit-ts <server> --mode client
mcporter emit-ts <server> --mode types
```

## 注意事项

- 使用 `--output json` 获取更易于解析的结构化输出
- 临时服务器（HTTP URL 或 `--stdio` 命令）无需任何配置即可工作 — 适用于一次性调用
- OAuth 授权可能需要交互式浏览器流程 — 如果需要，请使用 `terminal(command="mcporter auth <server>", pty=true)`