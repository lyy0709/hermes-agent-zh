---
title: "Neuroskill Bci"
sidebar_label: "Neuroskill Bci"
description: "连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40 多种衍生 EXG 评分）整合到响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）并在本地运行 NeuroSkill 桌面应用程序。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Neuroskill Bci

连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40 多种衍生 EXG 评分）整合到响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）并在本地运行 NeuroSkill 桌面应用程序。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/health/neuroskill-bci` 安装 |
| 路径 | `optional-skills/health/neuroskill-bci` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Nous Research |
| 许可证 | MIT |
| 标签 | `BCI`, `neurofeedback`, `health`, `focus`, `EEG`, `cognitive-state`, `biometrics`, `neuroskill` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# NeuroSkill BCI 集成

将 Hermes 连接到正在运行的 [NeuroSkill](https://neuroskill.com/) 实例，以从 BCI 可穿戴设备读取实时大脑和身体指标。使用此功能提供具有认知感知的响应、建议干预措施，并跟踪随时间变化的心理表现。

> **⚠️ 仅供研究使用** — NeuroSkill 是一个开源研究工具。它**不是**医疗设备，也**未经** FDA、CE 或任何监管机构批准。切勿将这些指标用于临床诊断或治疗。

完整指标参考请参见 `references/metrics.md`，干预协议请参见 `references/protocols.md`，WebSocket/HTTP API 请参见 `references/api.md`。

---

## 先决条件

- 已安装 **Node.js 20+** (`node --version`)
- 正在运行 **NeuroSkill 桌面应用程序**，并已连接 BCI 设备
- **BCI 硬件**：Muse 2、Muse S 或 OpenBCI（通过 BLE 连接的 4 通道 EEG + PPG + IMU）
- `npx neuroskill status` 返回数据且无错误

### 验证设置
```bash
node --version                    # 必须是 20+
npx neuroskill status             # 完整的系统快照
npx neuroskill status --json      # 机器可解析的 JSON
```

如果 `npx neuroskill status` 返回错误，请告知用户：
- 确保 NeuroSkill 桌面应用程序已打开
- 确保 BCI 设备已开机并通过蓝牙连接
- 检查信号质量 — NeuroSkill 中的绿色指示灯（每个电极 ≥0.7）
- 如果显示 `command not found`，请安装 Node.js 20+

---

## CLI 参考：`npx neuroskill <command>`

所有命令都支持 `--json`（原始 JSON，管道安全）和 `--full`（人类可读摘要 + JSON）。

| 命令 | 描述 |
|---------|-------------|
| `status` | 完整的系统快照：设备、评分、频段、比率、睡眠、历史记录 |
| `session [N]` | 单个会话细分，包含前半段/后半段趋势（0=最近一次） |
| `sessions` | 列出所有日期记录的所有会话 |
| `search` | ANN 相似性搜索，查找神经学上相似的历史时刻 |
| `compare` | A/B 会话比较，包含指标差异和趋势分析 |
| `sleep [N]` | 睡眠阶段分类（清醒/N1/N2/N3/REM）及分析 |
| `label "text"` | 在当前时刻创建带时间戳的注释 |
| `search-labels "query"` | 对过去标签进行语义向量搜索 |
| `interactive "query"` | 跨模态 4 层图搜索（文本 → EXG → 标签） |
| `listen` | 实时事件流（默认 5 秒，可设置 `--seconds N`） |
| `umap` | 会话嵌入的 3D UMAP 投影 |
| `calibrate` | 打开校准窗口并开始创建配置文件 |
| `timer` | 启动专注计时器（番茄工作法/深度工作/短时专注预设） |
| `notify "title" "body"` | 通过 NeuroSkill 应用程序发送操作系统通知 |
| `raw '{json}'` | 原始 JSON 直通到服务器 |

### 全局标志
| 标志 | 描述 |
|------|-------------|
| `--json` | 原始 JSON 输出（无 ANSI，管道安全） |
| `--full` | 人类可读摘要 + 彩色 JSON |
| `--port <N>` | 覆盖服务器端口（默认：自动发现，通常为 8375） |
| `--ws` | 强制使用 WebSocket 传输 |
| `--http` | 强制使用 HTTP 传输 |
| `--k <N>` | 最近邻数量（用于 search, search-labels） |
| `--seconds <N>` | listen 命令的持续时间（默认：5） |
| `--trends` | 显示每个会话的指标趋势（用于 sessions） |
| `--dot` | Graphviz DOT 输出（用于 interactive） |

---

## 1. 检查当前状态

### 获取实时指标
```bash
npx neuroskill status --json
```

**始终使用 `--json`** 以确保可靠解析。默认输出是彩色的人类可读文本。

### 响应中的关键字段

`scores` 对象包含所有实时指标（除非另有说明，均为 0–1 范围）：

```jsonc
{
  "scores": {
    "focus": 0.70,           // β / (α + θ) — 持续注意力
    "relaxation": 0.40,      // α / (β + θ) — 平静清醒状态
    "engagement": 0.60,      // 主动心理投入
    "meditation": 0.52,      // alpha + 静止 + HRV 一致性
    "mood": 0.55,            // 来自 FAA、TAR、BAR 的复合指标
    "cognitive_load": 0.33,  // 额叶 θ / 颞叶 α · f(FAA, TBR)
    "drowsiness": 0.10,      // TAR + TBR + 下降的频谱质心
    "hr": 68.2,              // 心率，单位 bpm（来自 PPG）
    "snr": 14.3,             // 信噪比，单位 dB
    "stillness": 0.88,       // 0–1；1 = 完全静止
    "faa": 0.042,            // 额叶 Alpha 不对称性（+ = 趋近）
    "tar": 0.56,             // Theta/Alpha 比率
    "bar": 0.53,             // Beta/Alpha 比率
    "tbr": 1.06,             // Theta/Beta 比率（ADHD 代理指标）
    "apf": 10.1,             // Alpha 峰值频率，单位 Hz
    "coherence": 0.614,      // 半球间一致性
    "bands": {
      "rel_delta": 0.28, "rel_theta": 0.18,
      "rel_alpha": 0.32, "rel_beta": 0.17, "rel_gamma": 0.05
    }
  }
}
```
还包括：`device`（状态、电量、固件）、`signal_quality`（每个电极 0–1）、`session`（时长、周期）、`embeddings`、`labels`、`sleep` 摘要和 `history`。

### 解读输出

解析 JSON 并将指标翻译成自然语言。永远不要只报告原始数字——总要赋予它们意义：

**正确做法：**
> "你当前的专注度很稳固，达到 0.70——这已进入心流状态区域。心率稳定在 68 bpm，你的 FAA 为正值，这表明你有良好的趋近动机。现在是处理复杂任务的好时机。"

**错误做法：**
> "专注度: 0.70, 放松度: 0.40, 心率: 68"

关键解读阈值（完整指南请参阅 `references/metrics.md`）：
- **专注度 > 0.70** → 心流状态区域，请保持
- **专注度 < 0.40** → 建议休息或执行特定方案
- **困倦度 > 0.60** → 疲劳警告，存在微睡眠风险
- **放松度 < 0.30** → 需要进行压力干预
- **认知负荷 > 0.70 持续** → 需要清空思绪或休息
- **TBR > 1.5** → θ波主导，执行控制能力下降
- **FAA < 0** → 退缩/负面情绪——考虑进行 FAA 再平衡
- **SNR < 3 dB** → 信号不可靠，建议重新调整电极位置

---

## 2. 会话分析

### 单次会话详细分析
```bash
npx neuroskill session --json         # 最近的会话
npx neuroskill session 1 --json       # 前一次会话
npx neuroskill session 0 --json | jq '{focus: .metrics.focus, trend: .trends.focus}'
```

返回完整的指标数据，包含**前半段与后半段的趋势**（`"up"`、`"down"`、`"flat"`）。
用这个来描述会话是如何演变的：

> "你的专注度从 0.64 开始，结束时攀升至 0.76——呈现明显的上升趋势。认知负荷从 0.38 下降到 0.28，表明随着你进入状态，任务变得更加自动化。"

### 列出所有会话
```bash
npx neuroskill sessions --json
npx neuroskill sessions --trends      # 显示每个会话的指标趋势
```

---

## 3. 历史搜索

### 神经相似性搜索
```bash
npx neuroskill search --json                    # 自动：上次会话，k=5
npx neuroskill search --k 10 --json             # 10 个最近邻
npx neuroskill search --start <UTC> --end <UTC> --json
```

使用 HNSW 近似最近邻搜索算法，在 128 维 ZUNA 嵌入向量上查找历史上神经状态相似的时刻。返回距离统计、时间分布（一天中的小时）和匹配度最高的日期。

当用户询问时使用此功能：
- "我上次处于类似状态是什么时候？"
- "找出我专注度最高的会话"
- "我通常在下午什么时候状态下滑？"

### 语义标签搜索
```bash
npx neuroskill search-labels "deep focus" --k 10 --json
npx neuroskill search-labels "stress" --json | jq '[.results[].EXG_metrics.tbr]'
```

使用向量嵌入模型（Xenova/bge-small-en-v1.5）搜索标签文本。返回匹配的标签及其在标记时的相关 EXG 指标。

### 跨模态图搜索
```bash
npx neuroskill interactive "deep focus" --json
npx neuroskill interactive "deep focus" --dot | dot -Tsvg > graph.svg
```

4 层图结构：查询 → 文本标签 → EXG 数据点 → 附近的标签。使用 `--k-text`、`--k-EXG`、`--reach <minutes>` 进行调整。

---

## 4. 会话比较
```bash
npx neuroskill compare --json                   # 自动：最近 2 次会话
npx neuroskill compare --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

返回约 50 个指标的差值，包括绝对变化、百分比变化和变化方向。同时包含 `insights.improved[]` 和 `insights.declined[]` 数组、两次会话的睡眠分期数据以及一个 UMAP 任务 ID。

结合上下文解读比较结果——提及趋势，而不仅仅是差值：
> "昨天你有两个强专注时段（上午 10 点和下午 2 点）。今天你从大约上午 11 点开始有一个专注时段，并且仍在持续。你今天的整体投入度更高，但压力峰值也更多——你的压力指数上升了 15%，FAA 更频繁地跌入负值。"

```bash
# 按改进百分比对指标排序
npx neuroskill compare --json | jq '.insights.deltas | to_entries | sort_by(.value.pct) | reverse'
```

---

## 5. 睡眠数据
```bash
npx neuroskill sleep --json                     # 过去 24 小时
npx neuroskill sleep 0 --json                   # 最近的睡眠会话
npx neuroskill sleep --start <UTC> --end <UTC> --json
```

返回逐周期的睡眠分期数据（5 秒窗口）及分析：
- **分期代码**：0=清醒，1=N1，2=N2，3=N3（深睡），4=REM
- **分析**：效率百分比、入睡潜伏期（分钟）、REM 潜伏期（分钟）、睡眠片段计数
- **健康目标**：N3 15–25%，REM 20–25%，效率 >85%，入睡潜伏期 <20 分钟

```bash
npx neuroskill sleep --json | jq '.summary | {n3: .n3_epochs, rem: .rem_epochs}'
npx neuroskill sleep --json | jq '.analysis.efficiency_pct'
```

当用户提及睡眠、疲倦或恢复时使用此功能。

---

## 6. 标记时刻
```bash
npx neuroskill label "breakthrough"
npx neuroskill label "studying algorithms"
npx neuroskill label "post-meditation"
npx neuroskill label --json "focus block start"   # 返回 label_id
```

在以下情况自动标记时刻：
- 用户报告突破或顿悟
- 用户开始新类型的任务（例如，"切换到代码审查"）
- 用户完成一项重要的方案
- 用户要求你标记当前时刻
- 发生显著的状态转换（进入或离开心流）

标签存储在数据库中，并建立索引，以便后续通过 `search-labels` 和 `interactive` 命令检索。

---

## 7. 实时流式传输
```bash
npx neuroskill listen --seconds 30 --json
npx neuroskill listen --seconds 5 --json | jq '[.[] | select(.event == "scores")]'
```

在指定持续时间内流式传输实时 WebSocket 事件（EXG、PPG、IMU、分数、标签）。需要 WebSocket 连接（使用 `--http` 时不可用）。

用于持续监控场景，或在执行方案时实时观察指标变化。

---

## 8. UMAP 可视化
```bash
npx neuroskill umap --json                      # 自动：最近 2 次会话
npx neuroskill umap --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```
基于 GPU 加速的 ZUNA 嵌入 3D UMAP 投影。`separation_score` 表示两个会话在神经层面的区分度：
- **> 1.5** → 会话在神经层面是区分的（不同的脑状态）
- **&lt; 0.5** → 两个会话的脑状态相似

---

## 9. 主动状态感知

### 会话开始检查
在会话开始时，如果用户提到他们佩戴了设备或询问其状态，可选择性地运行状态检查：
```bash
npx neuroskill status --json
```

注入一个简短的状态摘要：
> "快速检查：专注度正在建立，为 0.62；放松度良好，为 0.55；你的 FAA 为正——趋近动机已激活。看起来是个不错的开始。"

### 何时主动提及状态

**仅**在以下情况下提及认知状态：
- 用户明确询问（"我状态怎么样？"、"检查我的专注度"）
- 用户报告难以集中注意力、感到压力或疲劳
- 达到关键阈值（困倦度 > 0.70，专注度持续 &lt; 0.30）
- 用户即将进行认知要求高的任务并询问准备情况

**不要**打断心流状态来报告指标。如果专注度 > 0.75，保护会话——保持沉默是正确的回应。

---

## 10. 建议协议

当指标显示有需要时，从 `references/protocols.md` 中建议一个协议。在开始前总是先询问——永远不要打断心流状态：

> "过去 15 分钟你的专注度一直在下降，TBR 已攀升超过 1.5——这是 θ 波主导和精神疲劳的迹象。想让我带你做一个 θ-β 神经反馈锚定练习吗？这是一个 90 秒的练习，使用有节奏的计数和呼吸来抑制 θ 波并提升 β 波。"

关键触发点：
- **专注度 &lt; 0.40，TBR > 1.5** → θ-β 神经反馈锚定或箱式呼吸法
- **放松度 &lt; 0.30，压力指数高** → 心脏一致性或 4-7-8 呼吸法
- **认知负荷持续 > 0.70** → 认知负荷卸载（思维倾倒）
- **困倦度 > 0.60** → 超昼夜节律重置或唤醒重置
- **FAA &lt; 0（负值）** → FAA 再平衡
- **心流状态（专注度 > 0.75，投入度 > 0.70）** → **不要**打断
- **高静止度 + 头痛指数** → 颈部放松序列
- **低 RMSSD（&lt; 25ms）** → 迷走神经调谐

---

## 11. 附加工具

### 专注计时器
```bash
npx neuroskill timer --json
```
启动专注计时器窗口，提供番茄工作法（25/5）、深度工作（50/10）或短时专注（15/5）预设。

### 校准
```bash
npx neuroskill calibrate
npx neuroskill calibrate --profile "Eyes Open"
```
打开校准窗口。在信号质量差或用户希望建立个性化基线时很有用。

### 操作系统通知
```bash
npx neuroskill notify "Break Time" "Your focus has been declining for 20 minutes"
```

### 原始 JSON 透传
```bash
npx neuroskill raw '{"command":"status"}' --json
```
用于任何尚未映射到 CLI 子命令的服务器命令。

---

## 错误处理

| 错误 | 可能原因 | 修复方法 |
|-------|-------------|-----|
| `npx neuroskill status` 挂起 | NeuroSkill 应用未运行 | 打开 NeuroSkill 桌面应用 |
| `device.state: "disconnected"` | BCI 设备未连接 | 检查蓝牙、设备电量 |
| 所有分数返回 0 | 电极接触不良 | 重新定位头带，湿润电极 |
| `signal_quality` 值 &lt; 0.7 | 电极松动 | 调整贴合度，清洁电极触点 |
| SNR &lt; 3 dB | 信号噪声大 | 减少头部运动，检查环境 |
| `command not found: npx` | Node.js 未安装 | 安装 Node.js 20+ |

---

## 交互示例

**"我现在状态怎么样？"**
```bash
npx neuroskill status --json
```
→ 自然地解释分数，提及专注度、放松度、情绪以及任何显著的比率（FAA, TBR）。仅在指标显示有需要时才建议行动。

**"我无法集中注意力"**
```bash
npx neuroskill status --json
```
→ 检查指标是否确认此情况（高 θ 波，低 β 波，TBR 上升，高困倦度）。
→ 如果确认，从 `references/protocols.md` 建议合适的协议。
→ 如果指标看起来正常，问题可能是动机性的而非神经性的。

**"比较我今天和昨天的专注度"**
```bash
npx neuroskill compare --json
```
→ 解释趋势，而不仅仅是数字。提及哪些方面改善了，哪些方面下降了，以及可能的原因。

**"我上次处于心流状态是什么时候？"**
```bash
npx neuroskill search-labels "flow" --json
npx neuroskill search --json
```
→ 报告时间戳、相关指标以及用户当时在做什么（来自标签）。

**"我睡得怎么样？"**
```bash
npx neuroskill sleep --json
```
→ 报告睡眠结构（N3%、REM%、效率），与健康目标比较，并注意任何问题（高清醒时段，低 REM）。

**"标记这个时刻——我刚刚有了突破"**
```bash
npx neuroskill label "breakthrough"
```
→ 确认标签已保存。可选择性地记录当前指标以记住该状态。

---

## 参考资料

- [NeuroSkill 论文 — arXiv:2603.03212](https://arxiv.org/abs/2603.03212) (Kosmyna & Hauptmann, MIT Media Lab)
- [NeuroSkill 桌面应用](https://github.com/NeuroSkill-com/skill) (GPLv3)
- [NeuroLoop CLI 伴侣工具](https://github.com/NeuroSkill-com/neuroloop) (GPLv3)
- [MIT Media Lab 项目](https://www.media.mit.edu/projects/neuroskill/overview/)