---
title: "Blackbox — 将编码任务委派给 Blackbox AI CLI Agent"
sidebar_label: "Blackbox"
description: "将编码任务委派给 Blackbox AI CLI Agent"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blackbox

将编码任务委派给 Blackbox AI CLI Agent。这是一个内置评判机制的多模型 Agent，通过多个 LLM 运行任务并选取最佳结果。需要安装 blackbox CLI 并拥有 Blackbox AI API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/blackbox` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/blackbox` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 标签 | `Coding-Agent`, `Blackbox`, `Multi-Agent`, `Judge`, `Multi-Model` |
| 相关技能 | [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Blackbox CLI

通过 Hermes 终端将编码任务委派给 [Blackbox AI](https://www.blackbox.ai/)。Blackbox 是一个多模型编码 Agent CLI，它将任务分派给多个 LLM（Claude、Codex、Gemini、Blackbox Pro）并使用评判机制来选择最佳实现。

该 CLI 是[开源](https://github.com/blackboxaicode/cli)的（GPL-3.0，TypeScript，从 Gemini CLI 分叉而来），支持交互式会话、非交互式单次执行、检查点、MCP 和视觉模型切换。

## 先决条件

- 已安装 Node.js 20+
- 已安装 Blackbox CLI：`npm install -g @blackboxai/cli`
- 或从源码安装：
  ```
  git clone https://github.com/blackboxaicode/cli.git
  cd cli && npm install && npm install -g .
  ```
- 从 [app.blackbox.ai/dashboard](https://app.blackbox.ai/dashboard) 获取 API 密钥
- 已配置：运行 `blackbox configure` 并输入你的 API 密钥
- 在终端调用中使用 `pty=true` — Blackbox CLI 是一个交互式终端应用程序

## 单次执行任务

```
terminal(command="blackbox --prompt '为 Express API 添加 JWT 认证和刷新令牌'", workdir="/path/to/project", pty=true)
```

对于快速草稿工作：
```
terminal(command="cd $(mktemp -d) && git init && blackbox --prompt '为待办事项构建一个使用 SQLite 的 REST API'", pty=true)
```

## 后台模式（长任务）

对于需要数分钟的任务，使用后台模式以便监控进度：

```
# 在后台启动并使用 PTY
terminal(command="blackbox --prompt '重构认证模块以使用 OAuth 2.0'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Blackbox 提问，发送输入
process(action="submit", session_id="<id>", data="yes")

# 必要时终止
process(action="kill", session_id="<id>")
```

## 检查点与恢复

Blackbox CLI 内置了用于暂停和恢复任务的检查点支持：

```
# 任务完成后，Blackbox 会显示一个检查点标签
# 使用后续任务恢复：
terminal(command="blackbox --resume-checkpoint 'task-abc123-2026-03-06' --prompt '现在为端点添加速率限制'", workdir="~/project", pty=true)
```

## 会话命令

在交互式会话期间，使用以下命令：

| 命令 | 效果 |
|---------|--------|
| `/compress` | 压缩对话历史以节省 Token |
| `/clear` | 清除历史并重新开始 |
| `/stats` | 查看当前 Token 使用情况 |
| `Ctrl+C` | 取消当前操作 |

## PR 审查

克隆到临时目录以避免修改工作树：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && blackbox --prompt '对照 main 分支审查此 PR。检查错误、安全问题和代码质量。'", pty=true)
```

## 并行工作

为独立任务生成多个 Blackbox 实例：

```
terminal(command="blackbox --prompt '修复登录错误'", workdir="/tmp/issue-1", background=true, pty=true)
terminal(command="blackbox --prompt '为认证添加单元测试'", workdir="/tmp/issue-2", background=true, pty=true)

# 监控所有实例
process(action="list")
```

## 多模型模式

Blackbox 的独特功能是通过多个模型运行同一任务并评判结果。通过 `blackbox configure` 配置要使用的模型 — 选择多个提供商以启用 Chairman/评判工作流，其中 CLI 评估来自不同模型的输出并选择最佳的一个。

## 关键标志

| 标志 | 效果 |
|------|--------|
| `--prompt "task"` | 非交互式单次执行 |
| `--resume-checkpoint "tag"` | 从保存的检查点恢复 |
| `--yolo` | 自动批准所有操作和模型切换 |
| `blackbox session` | 启动交互式聊天会话 |
| `blackbox configure` | 更改设置、提供商、模型 |
| `blackbox info` | 显示系统信息 |

## 视觉支持

Blackbox 自动检测输入中的图像，并可切换到多模态分析。VLM 模式：
- `"once"` — 仅针对当前查询切换模型
- `"session"` — 为整个会话切换模型
- `"persist"` — 保持当前模型（不切换）

## Token 限制

通过 `.blackboxcli/settings.json` 控制 Token 使用：
```json
{
  "sessionTokenLimit": 32000
}
```

## 规则

1. **始终使用 `pty=true`** — Blackbox CLI 是一个交互式终端应用程序，没有 PTY 会挂起
2. **使用 `workdir`** — 让 Agent 专注于正确的目录
3. **长任务使用后台模式** — 使用 `background=true` 并通过 `process` 工具监控
4. **不要干扰** — 使用 `poll`/`log` 监控，不要因为会话慢而终止它们
5. **报告结果** — 完成后，检查更改内容并为用户总结
6. **积分需要花钱** — Blackbox 使用基于积分的系统；多模型模式消耗积分更快
7. **检查先决条件** — 在尝试委派之前，验证 `blackbox` CLI 是否已安装