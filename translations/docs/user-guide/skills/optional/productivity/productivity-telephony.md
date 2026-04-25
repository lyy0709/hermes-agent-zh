---
title: "Telephony — 在不更改核心工具的情况下为 Hermes 提供电话功能"
sidebar_label: "Telephony"
description: "在不更改核心工具的情况下为 Hermes 提供电话功能"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Telephony

在不更改核心工具的情况下为 Hermes 提供电话功能。配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，进行直接通话，并通过 Bland.ai 或 Vapi 发起 AI 驱动的外呼。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/telephony` 安装 |
| 路径 | `optional-skills/productivity/telephony` |
| 版本 | `1.0.0` |
| 作者 | Nous Research |
| 许可证 | MIT |
| 标签 | `telephony`, `phone`, `sms`, `mms`, `voice`, `twilio`, `bland.ai`, `vapi`, `calling`, `texting` |
| 相关技能 | [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps), [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace), [`agentmail`](/docs/user-guide/skills/optional/email/email-agentmail) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Telephony — 无需更改核心工具即可实现号码、通话和短信功能

此可选技能为 Hermes 提供实用的电话功能，同时将电话功能排除在核心工具列表之外。

它附带一个辅助脚本 `scripts/telephony.py`，可以：
- 将提供商凭据保存到 `~/.hermes/.env`
- 搜索并购买一个 Twilio 电话号码
- 记住该已拥有的号码以供后续会话使用
- 从已拥有的号码发送 SMS / MMS
- 轮询该号码的入站短信，无需 Webhook 服务器
- 使用 TwiML `<Say>` 或 `<Play>` 进行直接的 Twilio 通话
- 将已拥有的 Twilio 号码导入 Vapi
- 通过 Bland.ai 或 Vapi 发起外呼 AI 通话

## 解决的问题

此技能旨在覆盖用户实际需要的实用电话任务：
- 外呼
- 发短信
- 拥有一个可重复使用的 Agent 号码
- 稍后检查发送到该号码的消息
- 在会话之间保留该号码及相关 ID
- 为入站短信轮询和其他自动化提供面向未来的电话身份

它**不会**将 Hermes 变成实时入站电话网关。入站短信通过轮询 Twilio REST API 处理。这对于许多工作流（包括通知和一些一次性代码检索）来说已经足够，无需添加核心 Webhook 基础设施。

## 安全规则 — 强制性

1.  在拨打电话或发送短信前，务必进行确认。
2.  切勿拨打紧急号码。
3.  切勿将电话功能用于骚扰、垃圾信息、冒充或任何非法活动。
4.  将第三方电话号码视为敏感的操作数据：
    - 不要将其保存到 Hermes 记忆
    - 除非用户明确要求，否则不要将其包含在技能文档、摘要或后续笔记中
5.  可以持久化**Agent 拥有的 Twilio 号码**，因为这是用户配置的一部分。
6.  VoIP 号码**不能保证**适用于所有第三方 2FA 流程。请谨慎使用并明确设定用户期望。

## 决策树 — 使用哪个服务？

使用此逻辑，而非硬编码的提供商路由：

### 1) "我希望 Hermes 拥有一个真实的电话号码"
使用 **Twilio**。

原因：
- 购买和保留号码的最简单途径
- 最佳的 SMS / MMS 支持
- 最简单的入站短信轮询方案
- 未来通向入站 Webhook 或通话处理的最清晰路径

使用场景：
- 稍后接收短信
- 发送部署警报 / 定时任务通知
- 为 Agent 维护一个可重复使用的电话身份
- 稍后试验基于电话的认证流程

### 2) "我现在只需要最简单的外呼 AI 电话"
使用 **Bland.ai**。

原因：
- 设置最快
- 一个 API 密钥
- 无需先自行购买/导入号码

权衡：
- 灵活性较差
- 语音质量尚可，但不是最佳

### 3) "我想要最好的对话式 AI 语音质量"
使用 **Twilio + Vapi**。

原因：
- Twilio 提供您拥有的号码
- Vapi 提供更好的对话式 AI 通话质量和更多的语音/模型灵活性

推荐流程：
1.  购买/保存一个 Twilio 号码
2.  将其导入 Vapi
3.  保存返回的 `VAPI_PHONE_NUMBER_ID`
4.  使用 `ai-call --provider vapi`

### 4) "我想使用自定义的预录音频消息进行通话"
使用 **Twilio 直接通话** 并提供一个公开的音频 URL。

原因：
- 播放自定义 MP3 的最简单方式
- 与 Hermes `text_to_speech` 加上公共文件托管或隧道配合良好

## 文件和持久化状态

该技能在两个位置持久化电话状态：

### `~/.hermes/.env`
用于长期存在的提供商凭据和已拥有号码的 ID，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER` (AI 通话提供商：bland 或 vapi)

### `~/.hermes/telephony_state.json`
用于应在会话间保留的仅限技能使用的状态，例如：
- 记住的默认 Twilio 号码 / SID
- 记住的 Vapi 电话号码 ID
- 用于收件箱轮询检查点的最后一条入站消息 SID/日期

这意味着：
- 下次加载技能时，`diagnose` 可以告诉您已配置的号码
- `twilio-inbox --since-last --mark-seen` 可以从上一个检查点继续

## 定位辅助脚本

安装此技能后，按如下方式定位脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 为空，则表示技能尚未安装。

## 安装

这是一个官方的可选技能，因此可以从 Skills Hub 安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

## 提供商设置

### Twilio — 拥有号码、SMS/MMS、直接通话、入站短信轮询

注册地址：
- https://www.twilio.com/try-twilio
然后将凭据保存到 Hermes：

```bash
python3 "$SCRIPT" save-twilio ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_auth_token_here
```

搜索可用号码：

```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 5
```

购买并记住一个号码：

```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

列出已拥有的号码：

```bash
python3 "$SCRIPT" twilio-owned
```

稍后将其中的一个设置为默认号码：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# 或者
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

### Bland.ai — 最简单的外呼 AI 通话

在此注册：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

### Vapi — 更好的对话语音质量

在此注册：
- https://dashboard.vapi.ai

首先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将你拥有的 Twilio 号码导入 Vapi 并持久化返回的电话号码 ID：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果你已经知道 Vapi 电话号码 ID，直接保存它：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

## 诊断当前状态

随时可以检查该技能已经知道的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，请首先使用此命令。

## 常见工作流

### A. 购买一个 Agent 号码并后续持续使用

1. 保存 Twilio 凭据：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索一个号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买它并保存到 `~/.hermes/.env` 和状态中：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 下次会话时，运行：
```bash
python3 "$SCRIPT" diagnose
```
这将显示已记住的默认号码和收件箱检查点状态。

### B. 从 Agent 号码发送短信

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Your deployment completed successfully."
```

附带媒体：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Here is the chart." --media-url "https://example.com/chart.png"
```

### C. 稍后在没有 Webhook 服务器的情况下检查收到的短信

轮询默认 Twilio 号码的收件箱：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示自上次检查点之后到达的消息，并在你阅读完后推进检查点：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这是回答“下次加载技能时，如何访问该号码收到的消息？”的主要方法。

### D. 使用内置 TTS 直接拨打 Twilio 电话

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "Hello! This is Hermes calling with your status update." --voice Polly.Joanna
```

### E. 使用预录制/自定义语音消息进行呼叫

这是复用 Hermes 现有 `text_to_speech` 支持的主要途径。

在以下情况使用：
- 你希望通话使用 Hermes 配置的 TTS 语音，而不是 Twilio 的 `<Say>`
- 你希望进行单向语音传递（简报、警报、笑话、提醒、状态更新）
- 你**不需要**实时对话式电话通话

单独生成或托管音频，然后：

```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS -> Twilio Play 工作流：

1. 使用 Hermes `text_to_speech` 生成音频。
2. 使生成的 MP3 文件可公开访问。
3. 使用 `--audio-url` 拨打 Twilio 电话。

示例 Agent 流程：
- 要求 Hermes 使用 `text_to_speech` 创建消息音频
- 如果需要，通过临时静态主机/隧道/对象存储 URL 公开文件
- 使用 `twilio-call --audio-url ...` 通过电话传递

MP3 文件的良好托管选项：
- 临时的公共对象/存储 URL
- 指向本地静态文件服务器的短期隧道
- 电话提供商可以直接获取的任何现有 HTTPS URL

重要说明：
- Hermes TTS 非常适合预录制的外呼消息
- Bland/Vapi 更适合**实时对话式 AI 通话**，因为它们自己处理实时电话音频栈
- 此处并未将 Hermes STT/TTS 单独用作全双工电话对话引擎；这需要比本技能试图引入的更重的流式传输/Webhook 集成

### F. 使用 Twilio 直接呼叫导航电话树 / IVR

如果你需要在电话接通后按数字键，请使用 `--send-digits`。
Twilio 将 `w` 解释为短暂等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "Connecting to billing now." --send-digits "ww1w2w3"
```

这在转接给人工客服或传递简短状态消息之前，到达特定菜单分支时很有用。

### G. 使用 Bland.ai 进行外呼 AI 电话

```bash
python3 "$SCRIPT" ai-call "+15551230000" "Call the dental office, ask for a cleaning appointment on Tuesday afternoon, and if they do not have Tuesday availability, ask for Wednesday or Thursday instead." --provider bland --voice mason --max-duration 3
```

检查状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

完成后询问 Bland 分析问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "Was the appointment confirmed?,What date and time?,Any special instructions?"
```

### H. 使用 Vapi 在你拥有的号码上进行外呼 AI 电话

1. 将你的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2. 拨打电话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "You are calling to make a dinner reservation for two at 7:30 PM. If that is unavailable, ask for the nearest time between 6:30 and 8:30 PM." --provider vapi --max-duration 4
```

3. 检查结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

## 建议的 Agent 流程

当用户要求打电话或发短信时：
1. 根据决策树确定适合请求的路径。
2. 如果配置状态不明确，运行 `diagnose`。
3. 收集完整的任务详情。
4. 在拨打电话或发送短信前与用户确认。
5. 使用正确的命令。
6. 如果需要，轮询结果。
7. 总结结果，不将第三方号码持久化到 Hermes 记忆。

## 此技能目前仍无法做到

- 实时接听来电
- 基于 Webhook 将实时短信推送到 Agent 循环中
- 保证支持任意的第三方 2FA 提供商

这些功能需要比一个纯粹的可选技能更复杂的基础设施。

## 注意事项

- Twilio 试用账户和地区规则可能会限制您可以呼叫/发送短信的对象。
- 某些服务会拒绝 VoIP 号码用于 2FA。
- `twilio-inbox` 轮询 REST API；它不是即时推送交付。
- Vapi 外呼仍然依赖于拥有一个有效的已导入号码。
- Bland 最容易使用，但音质不一定总是最好。
- 不要将任意第三方电话号码存储在 Hermes 记忆。

## 验证清单

设置完成后，您应该能够仅使用此技能完成以下所有操作：

1. `diagnose` 显示提供商准备状态和已记忆的状态
2. 搜索并购买一个 Twilio 号码
3. 将该号码持久化到 `~/.hermes/.env`
4. 从拥有的号码发送一条短信
5. 稍后轮询该拥有号码的接收短信
6. 直接拨打一个 Twilio 电话
7. 通过 Bland 或 Vapi 拨打一个 AI 电话

## 参考

- Twilio 电话号码：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai：https://app.bland.ai/