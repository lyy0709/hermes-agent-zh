---
title: "操作 Teams 会议流水线"
description: "Microsoft Teams 会议流水线的操作手册、上线检查清单和操作员工作表"
---

# 操作 Teams 会议流水线

本指南适用于已通过 [Teams 会议](/docs/user-guide/messaging/teams-meetings) 启用该功能后。

本页内容涵盖：
- 操作员 CLI 流程
- 常规订阅维护
- 故障排查
- 上线检查
- 部署工作表

## 核心操作员命令

### 验证配置快照

```bash
hermes teams-pipeline validate
```

任何配置更改后，请首先使用此命令。

### 检查 Token 健康状态

```bash
hermes teams-pipeline token-health
hermes teams-pipeline token-health --force-refresh
```

当怀疑身份验证状态过时时，使用 `--force-refresh`。

### 检查订阅

```bash
hermes teams-pipeline subscriptions
```

### 续订即将过期的订阅

```bash
hermes teams-pipeline maintain-subscriptions
hermes teams-pipeline maintain-subscriptions --dry-run
```

### 自动化订阅续订（生产环境必需）

**Microsoft Graph 订阅最多在 72 小时后过期。** 如果没有东西续订它们，会议通知将在 3 天后静默停止，流水线看起来就像“坏了”。这是任何基于 Graph 的集成的首要操作故障模式。

您必须按计划运行 `maintain-subscriptions`。从以下三个选项中选择一个：

#### 选项 1：Hermes cron（如果已运行 Hermes 消息网关，推荐使用）

Hermes 内置了一个 cron 调度器。`--no-agent` 模式将脚本作为作业运行（而不是使用 LLM），`--script` 必须指向 `~/.hermes/scripts/` 下的文件。首先创建脚本：

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/maintain-teams-subscriptions.sh <<'EOF'
#!/usr/bin/env bash
exec hermes teams-pipeline maintain-subscriptions
EOF
chmod +x ~/.hermes/scripts/maintain-teams-subscriptions.sh
```

然后注册一个仅脚本的 cron 作业，每 12 小时运行一次（相对于 72 小时的过期窗口，提供 6 倍的安全余量）：

```bash
hermes cron create "0 */12 * * *" \
  --name "teams-pipeline-maintain-subscriptions" \
  --no-agent \
  --script maintain-teams-subscriptions.sh \
  --deliver local
```

验证是否已注册并检查下次运行时间：

```bash
hermes cron list
hermes cron status        # 调度器状态
```

#### 选项 2：systemd 定时器（推荐用于 Linux 生产部署）

创建 `/etc/systemd/system/hermes-teams-pipeline-maintain.service`：

```ini
[Unit]
Description=Hermes Teams pipeline subscription maintenance
After=network-online.target

[Service]
Type=oneshot
User=hermes
EnvironmentFile=/etc/hermes/env
ExecStart=/usr/local/bin/hermes teams-pipeline maintain-subscriptions
```

以及 `/etc/systemd/system/hermes-teams-pipeline-maintain.timer`：

```ini
[Unit]
Description=Run Hermes Teams pipeline subscription maintenance every 12 hours

[Timer]
OnBootSec=5min
OnUnitActiveSec=12h
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-teams-pipeline-maintain.timer
systemctl list-timers hermes-teams-pipeline-maintain.timer
```

#### 选项 3：普通 crontab

```cron
0 */12 * * * /usr/local/bin/hermes teams-pipeline maintain-subscriptions >> /var/log/hermes/teams-pipeline-maintain.log 2>&1
```

确保 cron 环境具有 `MSGRAPH_*` 凭据。最简单的解决方法：在 crontab 调用的包装脚本顶部 source `~/.hermes/.env`。

#### 验证续订是否正常工作

设置好计划后，在第一次计划运行后检查续订活动：

```bash
hermes teams-pipeline subscriptions   # 应显示 expirationDateTime 已提前
hermes teams-pipeline maintain-subscriptions --dry-run   # 大多数时候应显示 "0 expiring soon"
```

如果您发现 Graph webhook 在恰好约 72 小时后神秘地“停止工作”，这是首先要检查的事情：续订作业是否真的运行了？

### 检查最近的作业

```bash
hermes teams-pipeline list
hermes teams-pipeline list --status failed
hermes teams-pipeline show <job-id>
```

### 重放已存储的作业

```bash
hermes teams-pipeline run <job-id>
```

### 会议工件获取的试运行

```bash
hermes teams-pipeline fetch --meeting-id <meeting-id>
hermes teams-pipeline fetch --join-web-url "<join-url>"
```

## 常规操作手册

### 首次设置后

按顺序运行这些命令：

```bash
hermes teams-pipeline validate
hermes teams-pipeline token-health --force-refresh
hermes teams-pipeline subscriptions
```

然后触发或等待一个真实的会议事件并确认：

```bash
hermes teams-pipeline list
hermes teams-pipeline show <job-id>
```

### 每日或定期检查

- 运行 `hermes teams-pipeline maintain-subscriptions --dry-run`
- 检查 `hermes teams-pipeline list --status failed`
- 验证 Teams 投递目标仍然是正确的聊天或频道

### 更改 Webhook URL 或投递目标前

- 更新公共通知 URL 或 Teams 目标配置
- 运行 `hermes teams-pipeline validate`
- 续订或重新创建受影响的订阅
- 确认新事件到达预期的接收端

## 故障排查

### 没有创建作业

检查：
- `msgraph_webhook` 已启用
- 公共通知 URL 指向 `/msgraph/webhook`
- 订阅中的客户端状态与 `MSGRAPH_WEBHOOK_CLIENT_STATE` 匹配
- 订阅在远程仍然存在且未过期

### 作业停留在重试状态或在摘要生成前失败

检查：
- 转录权限和可用性
- 录制权限和工件可用性
- 如果启用了录制回退，检查 `ffmpeg` 可用性
- Graph Token 健康状态

### 摘要已生成但未投递到 Teams

检查：
- `platforms.teams.enabled: true`
- `delivery_mode`
- webhook 模式的 `incoming_webhook_url`
- Graph 模式的 `chat_id` 或 `team_id` 加 `channel_id`
- 如果使用 Graph 发布，检查 Teams 身份验证配置

### 重复或意外的重放

检查：
- 是否使用 `hermes teams-pipeline run` 手动重放了作业
- 该会议的接收端记录是否已存在
- 是否在本地配置中故意启用了重新发送路径

## 上线检查清单

- [ ] Graph 凭据存在且正确
- [ ] `msgraph_webhook` 已启用且可从公共互联网访问
- [ ] `MSGRAPH_WEBHOOK_CLIENT_STATE` 已设置且与订阅匹配
- [ ] 转录订阅已创建
- [ ] 如果需要 STT 回退，录制订阅已创建
- [ ] 如果启用了录制回退，`ffmpeg` 已安装
- [ ] Teams 出站投递目标已配置并验证
- [ ] Notion 和 Linear 接收端仅在确实需要时才配置
- [ ] `hermes teams-pipeline validate` 返回 OK 快照
- [ ] `hermes teams-pipeline token-health --force-refresh` 成功
- [ ] **`maintain-subscriptions` 已安排计划**（Hermes cron、systemd 定时器或 crontab — 参见[自动化订阅续订](#automating-subscription-renewal-required-for-production)）。没有这个，Graph 订阅将在 72 小时内静默过期。
- [ ] 一个真实的端到端会议事件已产生一个存储的作业
- [ ] 至少有一个摘要已到达预期的投递接收端

## 投递模式决策指南

| 模式 | 适用场景 | 权衡 |
|------|----------|----------|
| `incoming_webhook` | 您只需要简单地向 Teams 发布 | 设置最简单，控制较少 |
| `graph` | 您需要通过 Graph 向频道或聊天发布 | 控制更多，需要更多身份验证和目标配置 |

## 操作员工作表

部署前填写此表：

| 项目 | 值 |
|------|-------|
| 公共通知 URL | |
| Graph 租户 ID | |
| Graph 客户端 ID | |
| Webhook 客户端状态 | |
| 转录资源订阅 | |
| 录制资源订阅 | |
| Teams 投递模式 | |
| Teams 聊天 ID 或团队/频道 | |
| Notion 数据库 ID | |
| Linear 团队 ID | |
| 存储路径覆盖（如有） | |
| 每日检查负责人 | |

## 变更审查工作表

更改部署前使用此表：

| 问题 | 答案 |
|----------|--------|
| 我们是否在更改公共 webhook URL？ | |
| 我们是否在轮换 Graph 凭据？ | |
| 我们是否在更改 Teams 投递模式？ | |
| 我们是否要迁移到新的 Teams 聊天或频道？ | |
| 订阅是否需要重新创建或续订？ | |
| 我们是否需要一次全新的端到端验证运行？ | |

## 相关文档

- [Teams 会议设置](/docs/user-guide/messaging/teams-meetings)
- [Microsoft Teams 机器人设置](/docs/user-guide/messaging/teams)