---
sidebar_position: 6
title: "Teams 会议"
description: "使用 Microsoft Graph Webhook 设置 Microsoft Teams 会议摘要流水线"
---

# Microsoft Teams 会议

当您希望 Hermes 摄取 Microsoft Graph 会议事件、优先获取转录文本、在需要时回退到录音加语音转文字（STT），并将结构化摘要发送到下游接收器时，请使用 Teams 会议流水线。

本页重点介绍设置和启用：
- Graph 凭据
- Webhook 监听器配置
- Teams 交付模式
- 流水线配置结构

关于上线后运维、上线检查清单和操作员工作表，请使用专用指南：[运维 Teams 会议流水线](/docs/guides/operate-teams-meeting-pipeline)。

## 功能概述

该流水线：
1.  接收 Microsoft Graph Webhook 事件
2.  解析会议，并优先使用转录文件
3.  当没有可用的转录时，回退到下载录音并进行 STT
4.  在本地存储持久的作业状态和接收器记录
5.  可以将摘要写入 Notion、Linear 和 Microsoft Teams

操作员操作在 CLI 中进行（`teams-pipeline` 子命令由 `teams_pipeline` 插件注册——通过 `hermes plugins enable teams_pipeline` 启用，或在 `config.yaml` 中设置 `plugins.enabled: [teams_pipeline]`）：

```bash
hermes teams-pipeline validate
hermes teams-pipeline list
hermes teams-pipeline maintain-subscriptions
```

## 先决条件

在启用会议流水线之前，请确保您已具备：

-   一个正常运行的 Hermes 安装
-   如果您希望进行 Teams 出站交付，则需要现有的 [Microsoft Teams 机器人设置](/docs/user-guide/messaging/teams)
-   具有计划订阅的会议资源所需权限的 Microsoft Graph 应用程序凭据
-   一个 Microsoft Graph 可以调用以交付 Webhook 的公共 HTTPS URL
-   如果您希望使用录音加 STT 回退功能，则需要安装 `ffmpeg`

## 步骤 1：添加 Microsoft Graph 凭据

将 Graph 仅应用凭据添加到 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<tenant-id>
MSGRAPH_CLIENT_ID=<client-id>
MSGRAPH_CLIENT_SECRET=<client-secret>
```

这些凭据用于：
-   Graph 客户端基础
-   订阅维护命令
-   会议解析和文件获取
-   当您未提供专用的 Teams 访问令牌时，基于 Graph 的 Teams 出站交付

## 步骤 2：启用 Graph Webhook 监听器

Webhook 监听器是一个名为 `msgraph_webhook` 的消息网关平台。至少需要启用它并设置一个客户端状态值：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<random-shared-secret>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

监听器暴露：
-   `/msgraph/webhook` 用于接收 Graph 通知
-   `/health` 用于简单的健康检查

您需要将您的公共 HTTPS 端点路由到该监听器。例如，如果您的公共域是 `https://ops.example.com`，您的 Graph 通知 URL 通常为：

```text
https://ops.example.com/msgraph/webhook
```

## 步骤 3：配置 Teams 交付和流水线行为

会议流水线从现有的 `teams` 平台条目读取其运行时配置。流水线特定的配置项位于 `teams.extra.meeting_pipeline` 下。Teams 出站交付配置则保留在正常的 Teams 平台配置表面。

示例 `~/.hermes/config.yaml`：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      port: 8646
      client_state: "replace-me"
      accepted_resources:
        - "communications/onlineMeetings"

  teams:
    enabled: true
    extra:
      client_id: "your-teams-client-id"
      client_secret: "your-teams-client-secret"
      tenant_id: "your-teams-tenant-id"

      # 出站摘要交付
      delivery_mode: "graph" # 或 incoming_webhook
      team_id: "team-id"
      channel_id: "channel-id"
      # incoming_webhook_url: "https://..."

      meeting_pipeline:
        transcript_min_chars: 80
        transcript_required: false
        transcription_fallback: true
        ffmpeg_extract_audio: true
        notion:
          enabled: false
        linear:
          enabled: false
```

## Teams 交付模式

流水线在现有的 Teams 插件内支持两种 Teams 摘要交付模式。

### `incoming_webhook`

当您希望通过简单的 Webhook 将摘要发布到 Teams，而不通过 Graph 创建频道消息时，请使用此模式。

所需配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "incoming_webhook"
      incoming_webhook_url: "https://..."
```

### `graph`

当您希望 Hermes 通过 Microsoft Graph 将摘要发布到 Teams 聊天或频道时，请使用此模式。

支持的目标：
-   `chat_id`
-   `team_id` + `channel_id`
-   `team_id` + `home_channel`（作为现有 Teams 平台的回退）

示例：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "graph"
      team_id: "team-id"
      channel_id: "channel-id"
```

## 步骤 4：启动消息网关

更新配置后正常启动 Hermes：

```bash
hermes gateway run
```

或者，如果您在 Docker 中运行 Hermes，请按照您部署的现有方式启动消息网关。

检查监听器：

```bash
curl http://localhost:8646/health
```

## 步骤 5：创建 Graph 订阅

使用插件 CLI 创建和检查订阅。

示例：

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllRecordings \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"
```

:::warning Graph 订阅在 72 小时后过期

Microsoft Graph 将 Webhook 订阅限制在 72 小时内，并且不会自动续订。您**必须**在上线前安排 `hermes teams-pipeline maintain-subscriptions`，否则在任何手动订阅创建三天后，通知将静默停止。请参阅操作员手册中的[自动化订阅续订](/docs/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production)——提供了三种选项（Hermes 定时任务、systemd 定时器、普通 crontab）。

:::

关于订阅维护和上线后操作员流程，请继续阅读指南：[运维 Teams 会议流水线](/docs/guides/operate-teams-meeting-pipeline)。

## 验证

运行内置的验证快照：

```bash
hermes teams-pipeline validate
```

有用的配套检查：

```bash
hermes teams-pipeline token-health
hermes teams-pipeline subscriptions
```

## 故障排除

| 问题 | 检查内容 |
|---------|---------------|
| Graph Webhook 验证失败 | 确认公共 URL 正确且可访问，并且 Graph 正在调用确切的 `/msgraph/webhook` 路径 |
| 作业未出现在 `hermes teams-pipeline list` 中 | 确认 `msgraph_webhook` 已启用，并且订阅指向正确的通知 URL |
| 优先转录从未成功 | 检查 Graph 对转录资源的权限，以及该会议的转录文件是否存在 |
| 录音回退失败 | 确认 `ffmpeg` 已安装，并且 Graph 应用可以访问录音文件 |
| Teams 摘要交付失败 | 重新检查 `delivery_mode`、目标 ID 和 Teams 身份验证配置 |

## 相关文档

-   [Microsoft Teams 机器人设置](/docs/user-guide/messaging/teams)
-   [运维 Teams 会议流水线](/docs/guides/operate-teams-meeting-pipeline)