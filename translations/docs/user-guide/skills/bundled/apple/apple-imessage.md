---
title: "Imessage — 通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS"
sidebar_label: "Imessage"
description: "通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Imessage

通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/imessage` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `iMessage`, `SMS`, `messaging`, `macOS`, `Apple` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# iMessage

使用 `imsg` 通过 macOS 的 Messages.app 读取和发送 iMessage/SMS。

## 先决条件

- 已登录 Messages.app 的 **macOS** 系统
- 安装：`brew install steipete/tap/imsg`
- 授予终端完全磁盘访问权限（系统设置 → 隐私与安全性 → 完全磁盘访问）
- 在提示时授予 Messages.app 自动化权限

## 使用时机

- 用户要求发送 iMessage 或短信
- 读取 iMessage 对话历史记录
- 检查最近的 Messages.app 聊天
- 发送消息到电话号码或 Apple ID

## 避免使用时机

- Telegram/Discord/Slack/WhatsApp 消息 → 使用相应的消息网关通道
- 群聊管理（添加/移除成员）→ 不支持
- 批量/群发消息 → 务必先与用户确认

## 快速参考

### 列出聊天

```bash
imsg chats --limit 10 --json
```

### 查看历史记录

```bash
# 通过聊天 ID
imsg history --chat-id 1 --limit 20 --json

# 包含附件信息
imsg history --chat-id 1 --limit 20 --attachments --json
```

### 发送消息

```bash
# 仅文本
imsg send --to "+14155551212" --text "Hello!"

# 带附件
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# 强制使用 iMessage 或 SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### 监听新消息

```bash
imsg watch --chat-id 1 --attachments
```

## 服务选项

- `--service imessage` — 强制使用 iMessage（要求收件人启用了 iMessage）
- `--service sms` — 强制使用 SMS（绿色气泡）
- `--service auto` — 让 Messages.app 决定（默认）

## 规则

1. **发送前务必确认收件人和消息内容**
2. **未经用户明确批准，切勿向未知号码发送消息**
3. **附加文件前，验证文件路径**是否存在
4. **不要滥发** — 自行限制发送频率

## 示例工作流

用户："给妈妈发短信说我可能会迟到"

```bash
# 1. 找到妈妈的聊天
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. 与用户确认："在 +1555123456 找到了妈妈。通过 iMessage 发送‘我可能会迟到’吗？"

# 3. 确认后发送
imsg send --to "+1555123456" --text "I'll be late"
```