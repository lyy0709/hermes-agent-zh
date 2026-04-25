---
title: "Agentmail — 通过 AgentMail 为 Agent 提供专属邮箱"
sidebar_label: "Agentmail"
description: "通过 AgentMail 为 Agent 提供专属邮箱"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Agentmail

通过 AgentMail 为 Agent 提供专属邮箱。使用 Agent 拥有的邮箱地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/email/agentmail` 安装 |
| 路径 | `optional-skills/email/agentmail` |
| 版本 | `1.0.0` |
| 标签 | `email`, `communication`, `agentmail`, `mcp` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# AgentMail — Agent 拥有的邮箱

## 要求

- **AgentMail API 密钥**（必需） — 在 https://console.agentmail.to 注册（免费套餐：3 个邮箱，每月 3,000 封邮件；付费计划起价 20 美元/月）
- Node.js 18+（用于 MCP 服务器）

## 使用场景
在以下情况下使用此技能：
- 为 Agent 提供专属邮箱地址
- 代表 Agent 自主发送电子邮件
- 接收和阅读收到的电子邮件
- 管理邮件线程和对话
- 通过电子邮件注册服务或进行身份验证
- 通过电子邮件与其他 Agent 或人类通信

此技能**不**用于读取用户的个人电子邮件（请使用 himalaya 或 Gmail 技能）。
AgentMail 为 Agent 提供其自身的身份和收件箱。

## 设置

### 1. 获取 API 密钥
- 访问 https://console.agentmail.to
- 创建账户并生成 API 密钥（以 `am_` 开头）

### 2. 配置 MCP 服务器
添加到 `~/.hermes/config.yaml`（粘贴您的实际密钥 — MCP 环境变量不会从 .env 文件扩展）：
```yaml
mcp_servers:
  agentmail:
    command: "npx"
    args: ["-y", "agentmail-mcp"]
    env:
      AGENTMAIL_API_KEY: "am_your_key_here"
```

### 3. 重启 Hermes
```bash
hermes
```
现在所有 11 个 AgentMail 工具都会自动可用。

## 可用工具（通过 MCP）

| 工具 | 描述 |
|------|-------------|
| `list_inboxes` | 列出所有 Agent 邮箱 |
| `get_inbox` | 获取特定邮箱的详细信息 |
| `create_inbox` | 创建新邮箱（获得真实邮箱地址） |
| `delete_inbox` | 删除邮箱 |
| `list_threads` | 列出邮箱中的邮件线程 |
| `get_thread` | 获取特定的邮件线程 |
| `send_message` | 发送新邮件 |
| `reply_to_message` | 回复现有邮件 |
| `forward_message` | 转发邮件 |
| `update_message` | 更新邮件标签/状态 |
| `get_attachment` | 下载邮件附件 |

## 操作流程

### 创建邮箱并发送邮件
1. 创建专属邮箱：
   - 使用 `create_inbox` 并指定用户名（例如 `hermes-agent`）
   - Agent 将获得地址：`hermes-agent@agentmail.to`
2. 发送邮件：
   - 使用 `send_message`，指定 `inbox_id`、`to`、`subject`、`text`
3. 检查回复：
   - 使用 `list_threads` 查看收到的对话
   - 使用 `get_thread` 阅读特定线程

### 检查收到的邮件
1. 使用 `list_inboxes` 查找您的邮箱 ID
2. 使用 `list_threads` 并指定邮箱 ID 来查看对话
3. 使用 `get_thread` 阅读线程及其消息

### 回复邮件
1. 使用 `get_thread` 获取线程
2. 使用 `reply_to_message` 并指定消息 ID 和您的回复文本

## 示例工作流

**注册服务：**
```
1. create_inbox (用户名: "signup-bot")
2. 使用该邮箱地址在服务上注册
3. list_threads 检查验证邮件
4. get_thread 读取验证码
```

**Agent 对外联系：**
```
1. create_inbox (用户名: "hermes-outreach")
2. send_message (收件人: user@example.com, 主题: "Hello", 正文: "...")
3. list_threads 检查回复
```

## 注意事项
- 免费套餐限制为 3 个邮箱和每月 3,000 封邮件
- 免费套餐的邮件来自 `@agentmail.to` 域名（付费计划支持自定义域名）
- MCP 服务器需要 Node.js (18+) (`npx -y agentmail-mcp`)
- 必须安装 `mcp` Python 包：`pip install mcp`
- 实时接收邮件（Webhook）需要公共服务器 — 对于个人使用，请改用通过定时任务轮询 `list_threads`

## 验证
设置完成后，使用以下命令测试：
```
hermes --toolsets mcp -q "创建一个名为 test-agent 的 AgentMail 邮箱并告诉我它的邮箱地址"
```
您应该能看到返回的新邮箱地址。

## 参考
- AgentMail 文档：https://docs.agentmail.to/
- AgentMail 控制台：https://console.agentmail.to
- AgentMail MCP 仓库：https://github.com/agentmail-to/agentmail-mcp
- 定价：https://www.agentmail.to/pricing