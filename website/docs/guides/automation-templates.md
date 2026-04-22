---
sidebar_position: 15
title: "自动化模板"
description: "开箱即用的自动化配方 —— 定时任务、GitHub 事件触发器、API Webhook 和多技能工作流"
---

# 自动化模板

常见自动化模式的复制粘贴配方。每个模板都使用 Hermes 内置的 [定时任务调度器](/docs/user-guide/features/cron) 处理基于时间的触发器，以及 [Webhook 平台](/docs/user-guide/messaging/webhooks) 处理事件驱动的触发器。

每个模板都适用于**任何模型** —— 不锁定单一提供商。

:::tip 三种触发器类型
| 触发器 | 方式 | 工具 |
|---------|-----|------|
| **定时任务** | 按节奏运行（每小时、每晚、每周） | `cronjob` 工具或 `/cron` 斜杠命令 |
| **GitHub 事件** | 在 PR 打开、推送、议题、CI 结果时触发 | Webhook 平台 (`hermes webhook subscribe`) |
| **API 调用** | 外部服务向你的端点 POST JSON | Webhook 平台 (config.yaml 路由或 `hermes webhook subscribe`) |

所有三种类型都支持投递到 Telegram、Discord、Slack、SMS、电子邮件、GitHub 评论或本地文件。
:::

---

## 开发工作流

### 夜间待办事项分类

每晚对新议题进行标记、优先级排序和总结。将摘要发送到团队频道。

**触发器：** 定时任务（每晚）

```bash
hermes cron create "0 2 * * *" \
  "你是一个项目经理，正在对 NousResearch/hermes-agent GitHub 仓库的议题进行分类。

1. 运行：gh issue list --repo NousResearch/hermes-agent --state open --json number,title,labels,author,createdAt --limit 30
2. 识别过去 24 小时内新开的议题
3. 对于每个新议题：
   - 建议一个优先级标签（P0-严重、P1-高、P2-中、P3-低）
   - 建议一个分类标签（bug、feature、docs、security）
   - 写一行分类说明
4. 总结：总开放议题数、今日新增数、按优先级细分

格式化为清晰的摘要。如果没有新议题，请用 [SILENT] 响应。" \
  --name "夜间待办事项分类" \
  --deliver telegram
```

### 自动 PR 代码审查

每次拉取请求打开时自动审查。直接在 PR 上发布审查评论。

**触发器：** GitHub webhook

**选项 A — 动态订阅 (CLI)：**

```bash
hermes webhook subscribe github-pr-review \
  --events "pull_request" \
  --prompt "审查这个拉取请求：
仓库：{repository.full_name}
PR #{pull_request.number}: {pull_request.title}
作者：{pull_request.user.login}
操作：{action}
差异 URL：{pull_request.diff_url}

使用以下命令获取差异：curl -sL {pull_request.diff_url}

审查内容：
- 安全问题（注入、认证绕过、代码中的密钥）
- 性能问题（N+1 查询、无限循环、内存泄漏）
- 代码质量（命名、重复、错误处理）
- 新行为缺少的测试

发布简洁的审查。如果 PR 是琐碎的文档/拼写更改，请简要说明。" \
  --skills "github-code-review" \
  --deliver github_comment
```

**选项 B — 静态路由 (config.yaml)：**

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "your-global-secret"
      routes:
        github-pr-review:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            审查 PR #{pull_request.number}: {pull_request.title}
            仓库：{repository.full_name}
            作者：{pull_request.user.login}
            差异 URL：{pull_request.diff_url}
            审查安全性、性能和代码质量。
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{pull_request.number}"
```

然后在 GitHub 中：**Settings → Webhooks → Add webhook** → Payload URL: `http://your-server:8644/webhooks/github-pr-review`, Content type: `application/json`, Secret: `github-webhook-secret`, Events: **Pull requests**.

### 文档漂移检测

每周扫描已合并的 PR，查找需要更新文档的 API 变更。

**触发器：** 定时任务（每周）

```bash
hermes cron create "0 9 * * 1" \
  "扫描 NousResearch/hermes-agent 仓库的文档漂移情况。

1. 运行：gh pr list --repo NousResearch/hermes-agent --state merged --json number,title,files,mergedAt --limit 30
2. 筛选过去 7 天内合并的 PR
3. 对于每个已合并的 PR，检查它是否修改了：
   - 工具模式 (tools/*.py) —— 可能需要更新 docs/reference/tools-reference.md
   - CLI 命令 (hermes_cli/commands.py, hermes_cli/main.py) —— 可能需要更新 docs/reference/cli-commands.md
   - 配置选项 (hermes_cli/config.py) —— 可能需要更新 docs/user-guide/configuration.md
   - 环境变量 —— 可能需要更新 docs/reference/environment-variables.md
4. 交叉引用：对于每个代码变更，检查相应的文档页面是否在同一 PR 中也被更新

报告任何代码变更但文档未更新的缺口。如果一切同步，请用 [SILENT] 响应。" \
  --name "文档漂移检测" \
  --deliver telegram
```

### 依赖项安全审计

每日扫描项目依赖项中的已知漏洞。

**触发器：** 定时任务（每日）

```bash
hermes cron create "0 6 * * *" \
  "对 hermes-agent 项目运行依赖项安全审计。

1. cd ~/.hermes/hermes-agent && source .venv/bin/activate
2. 运行：pip audit --format json 2>/dev/null || pip audit 2>&1
3. 运行：npm audit --json 2>/dev/null (在 website/ 目录下，如果存在)
4. 检查是否有 CVSS 分数 >= 7.0 的 CVE

如果发现漏洞：
- 列出每个漏洞，包含包名、版本、CVE ID、严重性
- 检查是否有可用的升级
- 注明是直接依赖还是传递依赖

如果没有漏洞，请用 [SILENT] 响应。" \
  --name "依赖项审计" \
  --deliver telegram
```

---

## DevOps 与监控

### 部署验证

每次部署后触发冒烟测试。当部署完成时，你的 CI/CD 流水线会向 webhook 发送 POST 请求。

**触发器：** API 调用 (webhook)

```bash
hermes webhook subscribe deploy-verify \
  --events "deployment" \
  --prompt "一个部署刚刚完成：
服务：{service}
环境：{environment}
版本：{version}
部署者：{deployer}

运行以下验证步骤：
1. 检查服务是否响应：curl -s -o /dev/null -w '%{http_code}' {health_url}
2. 在最近的日志中搜索错误：检查部署负载中是否有任何错误指示器
3. 验证版本是否匹配：curl -s {health_url}/version

报告：部署状态（健康/降级/失败）、响应时间、发现的任何错误。
如果健康，请保持简洁。如果降级或失败，请提供详细的诊断信息。" \
  --deliver telegram
```
您的 CI/CD 流水线触发它：

```bash
curl -X POST http://your-server:8644/webhooks/deploy-verify \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -d '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}'
```

### 告警分诊

将监控告警与最近的变更关联起来，以草拟响应。可与 Datadog、PagerDuty、Grafana 或任何可以 POST JSON 的告警系统配合使用。

**触发方式：** API 调用（webhook）

```bash
hermes webhook subscribe alert-triage \
  --prompt "收到监控告警：
告警：{alert.name}
严重性：{alert.severity}
服务：{alert.service}
消息：{alert.message}
时间戳：{alert.timestamp}

调查：
1. 在网络上搜索此错误模式的已知问题
2. 检查是否与任何最近的部署或配置变更相关
3. 草拟一份分诊摘要，包含：
   - 可能的根本原因
   - 建议的初步响应步骤
   - 升级建议（P1-P4）

保持简洁。此内容将发送到值班频道。" \
  --deliver slack
```

### 正常运行时间监控

每 30 分钟检查端点。仅在出现故障时通知。

**触发方式：** 定时任务（每 30 分钟）

```python title="~/.hermes/scripts/check-uptime.py"
import urllib.request, json, time

ENDPOINTS = [
    {"name": "API", "url": "https://api.example.com/health"},
    {"name": "Web", "url": "https://www.example.com"},
    {"name": "Docs", "url": "https://docs.example.com"},
]

results = []
for ep in ENDPOINTS:
    try:
        start = time.time()
        req = urllib.request.Request(ep["url"], headers={"User-Agent": "Hermes-Monitor/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        results.append({"name": ep["name"], "status": resp.getcode(), "ms": elapsed})
    except Exception as e:
        results.append({"name": ep["name"], "status": "DOWN", "error": str(e)})

down = [r for r in results if r.get("status") == "DOWN" or (isinstance(r.get("status"), int) and r["status"] >= 500)]
if down:
    print("OUTAGE DETECTED")
    for r in down:
        print(f"  {r['name']}: {r.get('error', f'HTTP {r[\"status\"]}')} ")
    print(f"\nAll results: {json.dumps(results, indent=2)}")
else:
    print("NO_ISSUES")
```

```bash
hermes cron create "every 30m" \
  "如果脚本报告 OUTAGE DETECTED，总结哪些服务已宕机并建议可能的原因。如果报告 NO_ISSUES，则用 [SILENT] 响应。" \
  --script ~/.hermes/scripts/check-uptime.py \
  --name "Uptime monitor" \
  --deliver telegram
```

---

## 研究与情报

### 竞争对手仓库侦察

监控竞争对手的仓库，关注有趣的 PR、新功能和架构决策。

**触发方式：** 定时任务（每日）

```bash
hermes cron create "0 8 * * *" \
  "侦察以下 AI Agent 仓库在过去 24 小时内的显著活动：

需要检查的仓库：
- anthropics/claude-code
- openai/codex
- All-Hands-AI/OpenHands
- Aider-AI/aider

对每个仓库：
1. gh pr list --repo <repo> --state all --json number,title,author,createdAt,mergedAt --limit 15
2. gh issue list --repo <repo> --state open --json number,title,labels,createdAt --limit 10

重点关注：
- 正在开发的新功能
- 架构变更
- 我们可以借鉴的集成模式
- 可能也会影响我们的安全修复

跳过常规的依赖项更新和 CI 修复。如果没有显著发现，用 [SILENT] 响应。
如果有发现，按仓库组织，并对每个项目进行简要分析。" \
  --skills "competitive-pr-scout" \
  --name "Competitor scout" \
  --deliver telegram
```

### AI 新闻摘要

每周汇总 AI/ML 发展动态。

**触发方式：** 定时任务（每周）

```bash
hermes cron create "0 9 * * 1" \
  "生成过去 7 天的每周 AI 新闻摘要：

1. 在网络上搜索主要的 AI 公告、模型发布和研究突破
2. 搜索 GitHub 上热门的 ML 仓库
3. 在 arXiv 上查看关于语言模型和 Agent 的高引用论文

结构：
## 头条新闻（3-5 个主要故事）
## 值得关注的论文（2-3 篇论文，附一句话摘要）
## 开源动态（有趣的新仓库或主要发布）
## 行业动向（融资、收购、发布）

每个项目保持 1-2 句话。包含链接。总字数不超过 600 字。" \
  --name "Weekly AI digest" \
  --deliver telegram
```

### 带笔记的论文摘要

每日 arXiv 扫描，将摘要保存到您的笔记系统。

**触发方式：** 定时任务（每日）

```bash
hermes cron create "0 8 * * *" \
  "在 arXiv 上搜索过去一天关于 'language model reasoning' 或 'tool-use agents' 的 3 篇最有趣的论文。对于每篇论文，在 Obsidian 中创建一个笔记，包含标题、作者、摘要总结、关键贡献以及对 Hermes Agent 开发的潜在相关性。" \
  --skills "arxiv,obsidian" \
  --name "Paper digest" \
  --deliver local
```

---

## GitHub 事件自动化

### Issue 自动标记

自动标记新 Issue 并回复。

**触发方式：** GitHub webhook

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "收到新的 GitHub Issue：
仓库：{repository.full_name}
Issue #{issue.number}: {issue.title}
作者：{issue.user.login}
操作：{action}
正文：{issue.body}
标签：{issue.labels}

如果这是一个新 Issue（action=opened）：
1. 仔细阅读 Issue 标题和正文
2. 建议合适的标签（bug, feature, docs, security, question）
3. 如果是 Bug 报告，检查是否能从描述中识别受影响的组件
4. 发布一个有帮助的初始回复，确认收到 Issue

如果是标签或分配变更，用 [SILENT] 响应。" \
  --deliver github_comment
```

### CI 故障分析

分析 CI 故障并在 PR 上发布诊断信息。

**触发方式：** GitHub webhook

```yaml
# config.yaml 路由
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        ci-failure:
          events: ["check_run"]
          secret: "ci-secret"
          prompt: |
            CI 检查失败：
            仓库：{repository.full_name}
            检查：{check_run.name}
            状态：{check_run.conclusion}
            PR：#{check_run.pull_requests.0.number}
            详情 URL：{check_run.details_url}

            如果结论是 "failure"：
            1. 如果可访问，从详情 URL 获取日志
            2. 识别失败的可能原因
            3. 建议修复方法
            如果结论是 "success"，用 [SILENT] 响应。
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{check_run.pull_requests.0.number}"
```
### 跨仓库自动同步代码变更

当一个仓库的 PR 合并时，自动将等效的变更同步到另一个仓库。

**触发条件：** GitHub Webhook

```bash
hermes webhook subscribe auto-port \
  --events "pull_request" \
  --prompt "源仓库的 PR 已合并：
仓库：{repository.full_name}
PR #{pull_request.number}: {pull_request.title}
作者：{pull_request.user.login}
操作：{action}
合并提交：{pull_request.merge_commit_sha}

如果操作是 'closed' 且 pull_request.merged 为 true：
1. 获取差异：curl -sL {pull_request.diff_url}
2. 分析变更内容
3. 判断此变更是否需要同步到 Go SDK 等效仓库
4. 如果需要，创建一个分支，应用等效变更，并在目标仓库开启一个 PR
5. 在新 PR 的描述中引用原始 PR

如果操作不是 'closed' 或未合并，则回复 [SILENT]。" \
  --skills "github-pr-workflow" \
  --deliver log
```

---

## 业务运营

### Stripe 支付监控

追踪支付事件并获取失败摘要。

**触发条件：** API 调用 (Webhook)

```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed,charge.dispute.created" \
  --prompt "收到 Stripe 事件：
事件类型：{type}
金额：{data.object.amount} 分 ({data.object.currency})
客户：{data.object.customer}
状态：{data.object.status}

对于 payment_intent.payment_failed：
- 从 {data.object.last_payment_error} 中识别失败原因
- 建议这是暂时性问题（重试）还是永久性问题（联系客户）

对于 charge.dispute.created：
- 标记为紧急
- 总结争议详情

对于 payment_intent.succeeded：
- 仅简要确认

为运营频道保持回复简洁。" \
  --deliver slack
```

### 每日营收摘要

每天早上汇总关键业务指标。

**触发条件：** 定时任务 (每日)

```bash
hermes cron create "0 8 * * *" \
  "生成早间业务指标摘要。

搜索网络获取：
1. 当前比特币和以太坊价格
2. 标普 500 指数状态（盘前或前收盘价）
3. 过去 12 小时内任何重大的科技/AI 行业新闻

格式化为简短的早间简报，最多 3-4 个要点。
以清晰、易于浏览的消息形式发送。" \
  --name "Morning briefing" \
  --deliver telegram
```

---

## 多技能工作流

### 安全审计流水线

结合多种技能进行全面的每周安全审查。

**触发条件：** 定时任务 (每周)

```bash
hermes cron create "0 3 * * 0" \
  "对 hermes-agent 代码库进行全面的安全审计。

1. 检查依赖项漏洞 (pip audit, npm audit)
2. 在代码库中搜索常见的安全反模式：
   - 硬编码的密钥或 API 密钥
   - SQL 注入风险点（查询中的字符串格式化）
   - 路径遍历风险（用户输入未经验证地用于文件路径）
   - 不安全的反序列化 (pickle.loads, 未使用 SafeLoader 的 yaml.load)
3. 审查最近（过去 7 天）的提交中与安全相关的变更
4. 检查是否有任何新的环境变量在未记录的情况下被添加

撰写一份安全报告，按严重程度（严重、高、中、低）对发现的问题进行分类。
如果未发现任何问题，则报告一切正常。" \
  --skills "codebase-security-audit" \
  --name "Weekly security audit" \
  --deliver telegram
```

### 内容流水线

按计划研究、起草和准备内容。

**触发条件：** 定时任务 (每周)

```bash
hermes cron create "0 10 * * 3" \
  "研究并起草一份关于本周 AI Agent 热门话题的技术博客文章大纲。

1. 搜索网络，查找本周讨论最多的 AI Agent 话题
2. 挑选一个最有趣且与开源 AI Agent 相关的话题
3. 创建一个包含以下内容的大纲：
   - 吸引人的切入点/引言角度
   - 3-4 个关键部分
   - 适合开发者的技术深度
   - 带有可操作建议的结论
4. 将大纲保存到 ~/drafts/blog-$(date +%Y%m%d).md

将大纲控制在约 300 词。这是一个起点，不是完整的文章。" \
  --name "Blog outline" \
  --deliver local
```

---

## 快速参考

### Cron 定时任务语法

| 表达式 | 含义 |
|-----------|---------|
| `every 30m` | 每 30 分钟 |
| `every 2h` | 每 2 小时 |
| `0 2 * * *` | 每天凌晨 2:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `0 9 * * 1-5` | 工作日上午 9:00 |
| `0 3 * * 0` | 每周日凌晨 3:00 |
| `0 */6 * * *` | 每 6 小时 |

### 交付目标

| 目标 | 标志 | 说明 |
|--------|------|-------|
| 同一聊天 | `--deliver origin` | 默认 — 交付到任务创建的地方 |
| 本地文件 | `--deliver local` | 保存输出，无通知 |
| Telegram | `--deliver telegram` | 主频道，或使用 `telegram:CHAT_ID` 指定特定聊天 |
| Discord | `--deliver discord` | 主频道，或使用 `discord:CHANNEL_ID` |
| Slack | `--deliver slack` | 主频道 |
| 短信 | `--deliver sms:+15551234567` | 直接发送到手机号 |
| 特定主题 | `--deliver telegram:-100123:456` | Telegram 论坛主题 |

### Webhook 模板变量

| 变量 | 描述 |
|----------|-------------|
| `{pull_request.title}` | PR 标题 |
| `{issue.number}` | Issue 编号 |
| `{repository.full_name}` | `所有者/仓库` |
| `{action}` | 事件操作 (opened, closed 等) |
| `{__raw__}` | 完整的 JSON 负载（截断至 4000 字符） |
| `{sender.login}` | 触发事件的 GitHub 用户 |

### [SILENT] 模式

当定时任务的响应包含 `[SILENT]` 时，将抑制交付。使用此模式避免在安静运行时产生通知垃圾信息：

```
如果没有值得注意的事情发生，请回复 [SILENT]。
```

这意味着只有当 Agent 有内容需要报告时，你才会收到通知。