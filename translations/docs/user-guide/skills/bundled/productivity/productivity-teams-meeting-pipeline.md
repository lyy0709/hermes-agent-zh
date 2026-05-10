---
title: "Teams 会议流水线"
sidebar_label: "Teams 会议流水线"
description: "通过 Hermes CLI 操作 Teams 会议摘要流水线 — 总结会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Teams 会议流水线

通过 Hermes CLI 操作 Teams 会议摘要流水线 — 总结会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/teams-meeting-pipeline` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `Teams`, `Microsoft Graph`, `Meetings`, `Productivity`, `Operations` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Teams 会议流水线

每当用户询问有关 Microsoft Teams 会议摘要、转录、录制、行动项、Graph 订阅或任何关于 Teams 会议流水线的操作性问题时，请使用此技能。适用于任何语言 — 下面的触发器是示例，并非详尽列表。

所有面向操作员的功能都是通过终端工具运行的 `hermes teams-pipeline` 子命令。此流水线没有新的模型工具 — CLI 是操作界面。

## 何时使用此技能

用户要求：
- 总结 Teams 会议 / 提取行动项 / 拉取会议笔记
- 检查流水线状态、检查存储的会议任务或查看最近的会议
- 重放 / 重新运行一个存储的失败任务或需要重新生成摘要的任务
- 更改环境或配置后验证 Microsoft Graph 设置
- 排查“会议摘要未送达”或“没有新会议被摄取”的问题
- 管理 Graph Webhook 订阅（创建、续订、删除、检查）
- 设置自动订阅续订（参见下面的陷阱）

多语言触发器示例（非详尽）：
- 英语："summarize the Teams meeting", "pipeline status", "replay job X"
- 土耳其语："Teams meeting özetle", "action item çıkar", "toplantı notu", "pipeline durumu", "replay job"

## 先决条件

在使用流水线之前，请验证以下内容已在 `~/.hermes/.env` 中设置：

```bash
MSGRAPH_TENANT_ID=...
MSGRAPH_CLIENT_ID=...
MSGRAPH_CLIENT_SECRET=...
```

如果缺少任何一项，请引导用户访问 `/docs/guides/microsoft-graph-app-registration` 的 Azure 应用注册指南 — 在流水线工作之前，他们需要一个具有管理员同意的 Graph 应用程序权限的 Azure AD 应用注册。

## 命令参考

### 状态和检查（从此处开始）

```bash
hermes teams-pipeline validate              # 配置快照 — 任何更改后首先运行
hermes teams-pipeline token-health          # Graph Token 状态
hermes teams-pipeline token-health --force-refresh   # 强制获取新的 Token
hermes teams-pipeline list                  # 最近的会议任务
hermes teams-pipeline list --status failed  # 仅失败的任务
hermes teams-pipeline show <job-id>         # 单个任务的完整详情
hermes teams-pipeline subscriptions         # 当前的 Graph Webhook 订阅
```

### 重新运行 / 调试

```bash
hermes teams-pipeline run <job-id>          # 重放一个存储的任务（重新总结、重新交付）
hermes teams-pipeline fetch --meeting-id <id>   # 试运行：解析会议和转录但不持久化
hermes teams-pipeline fetch --join-web-url "<url>"   # 通过加入 URL 进行试运行
```

### 订阅管理

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://<your-public-host>/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline renew-subscription <sub-id> --expiration <iso-8601>
hermes teams-pipeline delete-subscription <sub-id>
hermes teams-pipeline maintain-subscriptions            # 续订即将到期的订阅
hermes teams-pipeline maintain-subscriptions --dry-run  # 显示将要续订的内容
```

## 常见请求的决策树

- 用户问“为什么我没有收到今天会议的摘要？” → 从 `list --status failed` 开始，然后在相关行上使用 `show <job-id>`。如果任务根本不存在，请检查 `subscriptions` — Webhook 可能已过期（参见下面的陷阱）。
- 用户问“设置工作正常吗？” → `validate`，然后 `token-health`，然后 `subscriptions`。如果三者都通过，请求一个测试会议并检查 `list` 是否有新行。
- 用户问“为会议 X 重新运行摘要” → `list` 查找任务 ID，`run <job-id>` 重放。如果再次失败，`show <job-id>` 检查错误，`fetch --meeting-id` 试运行工件解析。
- 用户问“将会议 X 添加到流水线” → 通常不需要 — 流水线是订阅驱动的，而不是按会议驱动的。如果他们想总结特定的过去会议，请使用 `fetch` 拉取转录，然后在任务创建后使用 `run`。

## 关键陷阱：Graph 订阅在 72 小时后过期

Microsoft Graph 将 Webhook 订阅限制在 72 小时，并且**不会自动续订**。如果未安排 `maintain-subscriptions`，则在任何手动订阅创建 3 天后，会议通知将静默停止到达。

当用户报告“流水线昨天工作正常，但今天没有任何消息到达”时：
1. 运行 `hermes teams-pipeline subscriptions` — 如果为空或所有条目的 `expirationDateTime` 显示为过去时间，那就是原因。
2. 使用上面的 `subscribe` 重新创建。
3. **立即通过 `hermes cron add`、systemd 定时器或普通 crontab 设置自动续订**。操作员运行手册 `/docs/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production` 提供了所有三种选项。12 小时间隔是安全的（相对于 72 小时限制有 6 倍余量）。

## 其他陷阱

- **转录尚未可用。** Teams 在会议结束后需要一些时间来生成转录工件。对刚结束的会议使用 `fetch --meeting-id` 可能返回空。等待 2-5 分钟重试，或让 Graph Webhook 自然驱动摄取。
- **交付模式不匹配。** 如果摘要已生成（`list` 显示成功）但未到达 Teams，请检查 `platforms.teams.extra.delivery_mode` 和匹配的目标配置（`incoming_webhook_url` 或 `chat_id` 或 `team_id`+`channel_id`）。写入器从 config.yaml 或 `TEAMS_*` 环境变量中读取这些配置。
- **Graph 应用权限。** Token 获取成功（`token-health` 通过）但 Graph API 调用返回 401/403，这是因为添加了权限但未重新授予管理员同意。让用户重新访问 Azure 门户中的应用注册，再次点击“授予管理员同意”。

## 相关文档

当用户需要比此技能涵盖的更深入信息时，请引导他们查看以下内容：
- Azure 应用注册分步指南：`/docs/guides/microsoft-graph-app-registration`
- 完整流水线设置：`/docs/user-guide/messaging/teams-meetings`
- 操作员运行手册（续订自动化、故障排除、上线清单）：`/docs/guides/operate-teams-meeting-pipeline`
- Webhook 监听器设置：`/docs/user-guide/messaging/msgraph-webhook`