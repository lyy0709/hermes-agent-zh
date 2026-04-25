---
title: "研究论文撰写"
sidebar_label: "研究论文撰写"
description: "撰写 ML/AI 研究论文的端到端流水线——从实验设计到分析、起草、修订和提交"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 研究论文撰写

撰写 ML/AI 研究论文的端到端流水线——从实验设计到分析、起草、修订和提交。涵盖 NeurIPS、ICML、ICLR、ACL、AAAI、COLM。集成了自动化实验监控、统计分析、迭代写作和引文验证。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/research-paper-writing` |
| 版本 | `1.1.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `semanticscholar`, `arxiv`, `habanero`, `requests`, `scipy`, `numpy`, `matplotlib`, `SciencePlots` |
| 平台 | linux, macos |
| 标签 | `Research`, `Paper Writing`, `Experiments`, `ML`, `AI`, `NeurIPS`, `ICML`, `ICLR`, `ACL`, `AAAI`, `COLM`, `LaTeX`, `Citations`, `Statistical Analysis` |
| 相关技能 | [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv), `ml-paper-writing`, [`subagent-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 研究论文撰写流水线

用于产出面向 **NeurIPS、ICML、ICLR、ACL、AAAI 和 COLM** 的可发表 ML/AI 研究论文的端到端流水线。此技能涵盖完整的研究生命周期：实验设计、执行、监控、分析、论文写作、审阅、修订和提交。

这**不是线性流水线**——它是一个迭代循环。结果会触发新的实验。审阅会触发新的分析。Agent 必须处理这些反馈循环。

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────────┐
│                    研究论文撰写流水线                       │
│                                                             │
│  阶段 0: 项目设置 ──► 阶段 1: 文献综述                      │
│       │                          │                          │
│       ▼                          ▼                          │
│  阶段 2: 实验          阶段 5: 论文起草 ◄──┐                │
│      设计                       │          │                │
│       │                          ▼          │                │
│       ▼                   阶段 6: 自我审阅   │                │
│  阶段 3: 执行与              与修订 ────────┘                │
│      监控                       │                          │
│       │                          ▼                          │
│       ▼                   阶段 7: 提交                      │
│  阶段 4: 分析 ─────► (反馈至阶段 2 或 5)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

---

## 何时使用此技能

在以下情况使用此技能：
- **开始撰写一篇新的研究论文**，基于现有代码库或想法
- **设计和运行实验**以支持论文主张
- **撰写或修订**研究论文的任何部分
- **准备向特定会议或研讨会提交**
- **通过额外实验或修订来回应审稿意见**
- **在会议格式之间转换**论文
- **撰写非实证性论文**——理论、综述、基准测试或立场论文（参见[实证性 ML 之外的论文类型](#paper-types-beyond-empirical-ml)）
- **为 NLP、HCI 或对齐研究设计人工评估**
- **准备录用后的交付物**——海报、演讲、代码发布

## 核心理念

1.  **积极主动。** 交付完整草稿，而非问题。科学家很忙——产出具体内容供其反馈，然后迭代。
2.  **绝不捏造引文。** AI 生成的引文错误率约为 40%。务必通过编程方式获取。将无法验证的引文标记为 `[CITATION NEEDED]`。
3.  **论文是故事，而非实验集合。** 每篇论文都需要一个用一句话清晰陈述的明确贡献。如果做不到这一点，论文就尚未准备好。
4.  **实验服务于主张。** 每个实验必须明确说明其支持哪个主张。绝不运行与论文叙述无关的实验。
5.  **尽早提交，频繁提交。** 每完成一批实验、每次论文草稿更新——都使用描述性信息提交。Git 日志就是实验历史。

### 主动性与协作

**默认：积极主动。先起草，带着草稿提问。**

| 置信度水平 | 行动 |
|-----------------|--------|
| **高**（代码库清晰，贡献明确） | 撰写完整草稿，交付，根据反馈迭代 |
| **中**（存在一些模糊性） | 撰写草稿并标记不确定性，继续推进 |
| **低**（存在重大未知） | 通过 `clarify` 提出 1-2 个有针对性的问题，然后起草 |

| 章节 | 是否自主起草？ | 随草稿标记 |
|---------|-------------------|-----------------|
| 摘要 | 是 | "将贡献表述为 X——如需调整请告知" |
| 引言 | 是 | "强调了问题 Y——如有错误请纠正" |
| 方法 | 是 | "包含了细节 A, B, C——请补充缺失部分" |
| 实验 | 是 | "突出了结果 1, 2, 3——如需重新排序请告知" |
| 相关工作 | 是 | "引用了论文 X, Y, Z——请补充我遗漏的任何论文" |

**仅在以下情况阻塞等待输入**：目标会议不明确、存在多个矛盾的框架、结果似乎不完整、明确要求先审阅。

---

## 阶段 0：项目设置

**目标**：建立工作空间，理解现有工作，明确贡献。
### 步骤 0.1：探索代码库

```bash
# 了解项目结构
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

寻找：
- `README.md` — 项目概述和声明
- `results/`、`outputs/`、`experiments/` — 现有发现
- `configs/` — 实验设置
- `.bib` 文件 — 现有引用
- 草稿文档或笔记

### 步骤 0.2：组织工作空间

建立一个一致的工作空间结构：

```
workspace/
  paper/               # LaTeX 源码、图表、编译后的 PDF
  experiments/         # 实验运行脚本
  code/                # 核心方法实现
  results/             # 原始实验结果（自动生成）
  tasks/               # 任务/基准定义
  human_eval/          # 人工评估材料（如果需要）
```

### 步骤 0.3：设置版本控制

```bash
git init  # 如果尚未初始化
git remote add origin <repo-url>
git checkout -b paper-draft  # 或 main
```

**Git 纪律**：每完成一批实验就提交，并附上描述性信息。示例：
```
添加蒙特卡洛约束结果（5 次运行，Sonnet 4.6，政策备忘录任务）
添加 Haiku 基线比较：廉价模型层级的自推理与优化基线对比
```

### 步骤 0.4：明确贡献

在撰写任何内容之前，阐明：
- **是什么**：这篇论文贡献了什么？
- **为什么**：有什么证据支持？
- **那又如何**：读者为什么应该关心？

> 向科学家提议："根据我的理解，主要贡献是：[一句话]。关键结果显示 [Y]。这是您想要的框架吗？"

### 步骤 0.5：创建待办事项列表

使用 `todo` 工具创建结构化的项目计划：

```
研究论文待办事项：
- [ ] 定义一句话贡献
- [ ] 文献综述（相关工作 + 基线）
- [ ] 设计核心实验
- [ ] 运行实验
- [ ] 分析结果
- [ ] 撰写初稿
- [ ] 自我审阅（模拟审稿人）
- [ ] 根据审阅意见修订
- [ ] 提交准备
```

在整个项目过程中更新此列表。它作为跨会话的持久状态。

### 步骤 0.6：估算计算预算

在运行实验之前，估算总成本和时间：

```
计算预算清单：
- [ ] API 成本：（每个 Token 的模型价格）×（每次运行估计的 Token 数）×（运行次数）
- [ ] GPU 小时数：（每次实验时间）×（实验数量）×（种子数）
- [ ] 人工评估成本：（标注员）×（小时数）×（小时费率）
- [ ] 总预算上限和应急费用（为重新运行增加 30-50%）
```

在实验运行时跟踪实际支出：
```python
# 简单的成本跟踪模式
import json, os
from datetime import datetime

COST_LOG = "results/cost_log.jsonl"

def log_cost(experiment: str, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "experiment": experiment,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }
    with open(COST_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**预算紧张时**：在投入全面实验之前，先运行试点实验（1-2 个种子，任务子集）。使用更便宜的模型调试流水线，然后为目标模型进行最终运行。

### 步骤 0.7：多作者协作

大多数论文有 3-10 位作者。尽早建立工作流程：

| 工作流程 | 工具 | 使用时机 |
|----------|------|-------------|
| **Overleaf** | 基于浏览器 | 多位作者同时编辑，无 git 经验 |
| **Git + LaTeX** | 使用 `.gitignore` 排除辅助文件的 `git` | 技术团队，需要基于分支的审阅 |
| **Overleaf + Git 同步** | Overleaf 高级版 | 两者兼顾 — 实时协作与版本历史 |

**章节所有权**：将每个章节分配给一位主要作者。其他人评论但不直接编辑。防止合并冲突和风格不一致。

```
作者协作清单：
- [ ] 商定章节所有权（谁写什么）
- [ ] 设置共享工作空间（Overleaf 或 git 仓库）
- [ ] 建立符号约定（在任何撰写之前）
- [ ] 安排内部审阅轮次（不仅仅在最后）
- [ ] 指定一人负责最终格式调整
- [ ] 在创建图表前商定图表样式（颜色、字体、大小）
```

**尽早商定的 LaTeX 约定**：
- 使用 `\method{}` 宏确保方法命名一致
- 引用样式：`\citet{}` 与 `\citep{}` 的用法
- 数学符号：小写粗体表示向量，大写粗体表示矩阵等
- 英式与美式拼写

---

## 阶段 1：文献综述

**目标**：查找相关工作，确定基线，收集引用。

### 步骤 1.1：确定种子论文

从代码库中已引用的论文开始：

```bash
# 通过终端：
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

### 步骤 1.2：搜索相关工作

**加载 `arxiv` 技能**以进行结构化论文发现：`skill_view("arxiv")`。它提供 arXiv REST API 搜索、Semantic Scholar 引用图、作者资料和 BibTeX 生成。

使用 `web_search` 进行广泛发现，使用 `web_extract` 获取特定论文：

```
# 通过 web_search：
web_search("[主要技术] + [应用领域] site:arxiv.org")
web_search("[基线方法] 比较 ICML NeurIPS 2024")

# 通过 web_extract（针对特定论文）：
web_extract("https://arxiv.org/abs/2303.17651")
```

可以尝试的其他搜索查询：

```
搜索查询：
- "[主要技术] + [应用领域]"
- "[基线方法] 比较"
- "[问题名称] 最新技术"
- 现有引用中的作者姓名
```

**推荐**：安装 **Exa MCP** 以进行实时学术搜索：
```bash
claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"
```

### 步骤 1.2b：深化搜索（先广度，后深度）

扁平搜索（一轮查询）通常会遗漏重要的相关工作。使用迭代的**先广度后深度**模式，灵感来自深度研究流水线：
```
迭代式文献检索：

第一轮（广度）：4-6个并行查询，覆盖不同角度
  - "[方法] + [领域]"
  - "[问题名称] state-of-the-art 2024 2025"
  - "[基线方法] comparison"
  - "[替代方法] vs [你的方法]"
  → 收集论文，提取关键概念和术语

第二轮（深度）：根据第一轮的学习成果生成后续查询
  - 在第一轮论文中发现的新术语
  - 被最相关的第一轮结果引用的论文
  - 需要调查的矛盾发现
  → 收集论文，识别剩余空白

第三轮（针对性）：填补特定空白
  - 在第一、二轮中识别出的缺失基线
  - 同期工作（过去6个月，相同问题）
  - 关键的负面结果或失败方法
  → 当新查询返回的论文大部分已见过时停止

**何时停止**：如果一轮检索返回的论文中超过80%已在你的收藏中，则检索已饱和。通常2-3轮足够。对于综述论文，预计需要4-5轮。

**对于基于 Agent 的工作流**：通过 `delegate_task` 并行委派每轮的查询。收集结果，去重，然后根据综合学习成果生成下一轮的查询。

### 步骤 1.3：验证每条引用

**切勿凭记忆生成 BibTeX。务必通过编程方式获取。**

对于每条引用，遵循强制性的5步流程：

```
引用验证（每条引用必须执行）：
1. 搜索 → 使用特定关键词查询 Semantic Scholar 或 Exa MCP
2. 验证 → 在2个以上来源（Semantic Scholar + arXiv/CrossRef）确认论文存在
3. 获取 → 通过 DOI 内容协商获取 BibTeX（编程方式，非凭记忆）
4. 验证 → 确认你引用的主张确实出现在论文中
5. 添加 → 将已验证的 BibTeX 添加到参考文献
如果任何步骤失败 → 标记为 [CITATION NEEDED]，并通知科学家
```

```python
# 通过 DOI 获取 BibTeX
import requests

def doi_to_bibtex(doi: str) -> str:
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text
```

如果无法验证引用：

```latex
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: 验证此引用是否存在
```

**务必告知科学家**："我已将 [X] 条引用标记为需要验证的占位符。"

完整的 API 文档和完整的 `CitationManager` 类，请参阅 [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md)。

### 步骤 1.4：组织相关工作

按方法论而非逐篇论文进行分组：

**好的**："一系列工作使用了 X 的假设 [引用]，而我们使用 Y 的假设，因为..."
**差的**："Smith 等人引入了 X。Jones 等人引入了 Y。我们结合了两者。"

---

## 阶段 2：实验设计

**目标**：设计直接支持论文主张的实验。每个实验必须回答一个具体问题。

### 步骤 2.1：将主张映射到实验

创建明确的映射：

| 主张 | 实验 | 预期证据 |
|-------|-----------|-------------------|
| "我们的方法优于基线" | 主要比较（表 1） | 胜率，统计显著性 |
| "对于较弱模型效果更明显" | 模型缩放研究 | 单调改进曲线 |
| "收敛需要范围约束" | 约束与非约束对比 | 收敛率比较 |

**规则**：如果一个实验不映射到任何主张，就不要运行它。

### 步骤 2.2：设计基线

强大的基线是区分被接受论文和被拒稿论文的关键。审稿人会问："他们与 X 比较了吗？"

标准基线类别：
- **朴素基线**：最简单可能的方法
- **强基线**：已知的最佳现有方法
- **消融基线**：你的方法减去一个组件
- **计算匹配基线**：相同的计算预算，不同的分配方式

### 步骤 2.3：定义评估协议

在运行任何实验之前，明确指定：
- **指标**：你测量的内容，方向符号（越高/越低越好）
- **聚合**：如何跨运行/任务组合结果
- **统计检验**：将使用什么检验来确定显著性
- **样本量**：运行次数/问题数/任务数

### 步骤 2.4：编写实验脚本

遵循成功研究流水线的这些模式：

**增量保存** — 为便于崩溃恢复，在每个步骤后保存结果：
```python
# 在每个问题/任务后保存
result_path = f"results/{task}/{strategy}/result.json"
if os.path.exists(result_path):
    continue  # 跳过已完成的工作
# ... 运行实验 ...
with open(result_path, 'w') as f:
    json.dump(result, f, indent=2)
```

**工件保存** — 保存所有中间输出：
```
results/<experiment>/
  <task>/
    <strategy>/
      final_output.md          # 最终结果
      history.json             # 完整轨迹
      pass_01/                 # 每次迭代的工件
        version_a.md
        version_b.md
        critic.md
```

**关注点分离** — 保持生成、评估和可视化分离：
```
run_experiment.py              # 核心实验运行器
run_baselines.py               # 基线比较
run_comparison_judge.py        # 盲评估
analyze_results.py             # 统计分析
make_charts.py                 # 可视化
```

完整的设计模式、定时任务监控和错误恢复，请参阅 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md)。

### 步骤 2.5：设计人工评估（如适用）

许多 NLP、HCI 和对齐论文需要人工评估作为主要或补充证据。在运行自动化实验之前设计好这一点——人工评估通常有更长的准备时间（IRB 批准、标注员招募）。

**需要人工评估的情况：**
- 自动化指标无法捕捉你关心的方面（流畅度、帮助性、安全性）
- 你的贡献是关于面向人类的品质（可读性、偏好、信任）
- NLP 会议（ACL、EMNLP）的审稿人期望生成任务包含人工评估
**关键设计决策：**

| 决策 | 选项 | 指导原则 |
|----------|---------|----------|
| **标注者类型** | 专家、众包工作者、终端用户 | 根据你的主张要求进行匹配 |
| **量表类型** | 李克特量表（1-5分）、成对比较、排序 | 对于 LLM 输出，成对比较比李克特量表更可靠 |
| **样本量** | 每位标注者及总项目数 | 功效分析或至少 100 个项目，3 名以上标注者 |
| **一致性指标** | Cohen's kappa、Krippendorff's alpha、ICC | 标注者 >2 人时使用 Krippendorff's alpha；同时报告原始一致性 |
| **平台** | Prolific、MTurk、内部团队 | 质量选 Prolific；规模选 MTurk；领域专业知识选内部团队 |

**标注指南清单：**
```
- [ ] 清晰的任务描述，包含示例（好的和坏的）
- [ ] 模糊情况的决策标准
- [ ] 每个类别至少 2 个完整示例
- [ ] 注意力检查 / 黄金标准项目（占总数的 10-15%）
- [ ] 资格任务或筛选轮次
- [ ] 预估每项任务耗时及公平报酬（>= 当地最低工资）
- [ ] 若机构要求，进行 IRB/伦理审查
```

**报告要求**（审稿人会检查所有这些）：
- 标注者数量及其资质
- 标注者间一致性，包含具体指标和数值
- 报酬详情（金额、预估时薪）
- 标注界面描述或截图（附录）
- 总标注时间

完整指南请参阅 [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)，包括人工评估数据的统计检验、众包质量控制模式以及 IRB 指导。

---

## 阶段 3：实验执行与监控

**目标**：可靠地运行实验，监控进度，从故障中恢复。

### 步骤 3.1：启动实验

对于长时间运行的实验，使用 `nohup`：

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!  # 记录 PID
```

**并行执行**：可以同时运行独立的实验，但要注意 API 速率限制。在同一 API 上并发运行 4 个以上实验会相互拖慢速度。

### 步骤 3.2：设置监控（Cron 模式）

对于长时间运行的实验，设置定期状态检查。cron 提示词应遵循此模板：

```
监控提示词模板：
1. 检查进程是否仍在运行：ps aux | grep <pattern>
2. 读取日志最后 30 行：tail -30 <logfile>
3. 检查完成的结果：ls <result_dir>
4. 如果结果存在，读取并报告：cat <result_file>
5. 如果全部完成，提交：git add -A && git commit -m "<descriptive message>" && git push
6. 以结构化格式报告（包含关键指标的表格）
7. 回答本次实验的关键分析问题
```

**静默模式**：如果自上次检查以来没有任何变化，则用 `[SILENT]` 响应，以抑制向用户发送通知。仅在出现新情况时报告。

### 步骤 3.3：处理故障

常见故障模式及恢复方法：

| 故障 | 检测 | 恢复 |
|---------|-----------|----------|
| API 速率限制 / 额度耗尽 | 日志中出现 402/429 错误 | 等待，然后重新运行（脚本会跳过已完成的工作） |
| 进程崩溃 | PID 消失，结果不完整 | 从最后一个检查点重新运行 |
| 难题超时 | 进程卡住，日志无进展 | 终止并跳过，在结果中注明 |
| 错误的模型 ID | 引用模型名称的错误 | 修复 ID 并重新运行 |

**关键**：脚本应始终检查现有结果并跳过已完成的工作。这使得重新运行安全且高效。

### 步骤 3.4：提交完成的结果

每批实验完成后：

```bash
git add -A
git commit -m "Add <experiment name>: <key finding in 1 line>"
git push
```

### 步骤 3.5：维护实验日志

Git 提交记录了发生了什么，但没有记录**探索树**——即基于所学知识决定下一步尝试的决策过程。维护一个结构化的实验日志来捕获这棵树：

```json
// experiment_journal.jsonl — 每次实验尝试追加一条记录
{
  "id": "exp_003",
  "parent": "exp_001",
  "timestamp": "2025-05-10T14:30:00Z",
  "hypothesis": "添加范围约束将修复 exp_001 中的收敛失败",
  "plan": "使用 max_tokens=2000 和固定结构模板重新运行 autoreason",
  "config": {"model": "haiku", "strategy": "autoreason", "max_tokens": 2000},
  "status": "completed",
  "result_path": "results/exp_003/",
  "key_metrics": {"win_rate": 0.85, "convergence_rounds": 3},
  "analysis": "范围约束修复了收敛问题。胜率从 0.42 跃升至 0.85。",
  "next_steps": ["在 Sonnet 上尝试相同约束", "测试不使用结构模板"],
  "figures": ["figures/exp003_convergence.pdf"]
}
```

**为什么用日志而不仅仅是 Git？** Git 跟踪文件变化。日志跟踪推理过程：你为什么尝试 X，你学到了什么，这对下一个实验意味着什么。在撰写论文时，这棵树对于方法部分（"我们观察到 X，这促使我们进行 Y"）和诚实地报告失败至关重要。

**选择最佳路径**：当日志显示一个分支树（exp_001 → exp_002a, exp_002b, exp_003）时，确定最能支持论文主张的路径。将死胡同分支记录在附录中，作为消融研究或负面结果。

**为每次实验快照代码**：每次运行后复制实验脚本：
```bash
cp experiment.py results/exp_003/experiment_snapshot.py
```
这样即使在后续代码更改后也能精确复现。

---

## 阶段 4：结果分析

**目标**：提取发现，计算统计数据，确定故事线。

### 步骤 4.1：汇总结果

编写分析脚本，用于：
1. 加载一批中的所有结果文件
2. 计算每项任务和汇总指标
3. 生成汇总表格

```python
# 标准分析模式
import json, os
from pathlib import Path

results = {}
for result_file in Path("results/").rglob("result.json"):
    data = json.loads(result_file.read_text())
    strategy = result_file.parent.name
    task = result_file.parent.parent.name
    results.setdefault(strategy, {})[task] = data

# 计算汇总指标
for strategy, tasks in results.items():
    scores = [t["score"] for t in tasks.values()]
    print(f"{strategy}: mean={np.mean(scores):.1f}, std={np.std(scores):.1f}")
```
### 步骤 4.2：统计显著性

始终计算：
- **误差线**：标准差或标准误，请注明是哪种
- **置信区间**：关键结果的 95% 置信区间
- **配对检验**：用于比较两种方法的 McNemar 检验
- **效应量**：用于衡量实际显著性的 Cohen's d 或 h

有关 McNemar 检验、自助法置信区间和 Cohen's h 的完整实现，请参阅 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md)。

### 步骤 4.3：确定故事线

分析后，请明确回答：
1.  **主要发现是什么？** 用一句话陈述。
2.  **什么让你感到意外？** 意外的结果往往能成就最好的论文。
3.  **什么失败了？** 失败的实验可能最有启发性。诚实地报告失败能增强论文的说服力。
4.  **需要哪些后续实验？** 结果往往会引出新的问题。

#### 处理阴性或无效结果

当你的假设错误或结果不确定时，你有三种选择：

| 情况 | 行动 | 适合的发表渠道 |
|-----------|--------|-----------|
| 假设错误，但**原因**具有启发性 | 围绕原因分析来构建论文 | NeurIPS, ICML（如果分析严谨） |
| 方法未超越基线，但**揭示了新东西** | 将贡献重新定义为理解/分析 | ICLR（重视理解）、研讨会论文 |
| 针对流行主张的明确阴性结果 | 写出来——领域需要知道 | NeurIPS Datasets & Benchmarks, TMLR, 研讨会 |
| 结果不确定，没有清晰的故事线 | 转向——运行不同的实验或重新构建 | 不要强行写一篇不存在的论文 |

**如何撰写阴性结果论文：**
- 开头说明社区普遍相信什么，以及为什么测试它很重要
- 描述你严谨的方法论（必须无懈可击——审稿人会更加仔细地审查）
- 清晰地呈现无效结果并提供统计证据
- 分析**为什么**预期结果没有出现
- 讨论对领域的影响

**明确欢迎阴性结果的发表渠道**：NeurIPS（Datasets & Benchmarks 赛道）、TMLR、ML Reproducibility Challenge、主要会议的研讨会。有些研讨会专门征集阴性结果。

### 步骤 4.4：创建图表

**图表**：
- 所有绘图使用矢量图形（PDF）：`plt.savefig('fig.pdf')`
- 使用色盲友好调色板（Okabe-Ito 或 Paul Tol）
- 图注应自成一体——读者无需阅读正文即可理解
- 图表内不要有标题——图注即起到标题作用

**表格**：
- 使用 `booktabs` LaTeX 包
- 每个指标的最佳值加粗
- 包含方向符号（↑ 表示越高越好，↓ 表示越低越好）
- 保持小数位数一致

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

### 步骤 4.5：决定：继续实验还是开始写作？

| 情况 | 行动 |
|-----------|--------|
| 核心主张得到支持，结果显著 | 进入阶段 5（写作） |
| 结果不确定，需要更多数据 | 回到阶段 2（设计） |
| 意外发现提示了新方向 | 回到阶段 2（设计） |
| 缺少一个审稿人可能会问的消融实验 | 运行它，然后进入阶段 5 |
| 所有实验已完成，但部分失败 | 记录失败，进入阶段 5 |

### 步骤 4.6：撰写实验日志（连接写作的桥梁）

在开始论文写作之前，创建一个结构化的实验日志，作为连接结果与文本的桥梁。这是连接实验与论文草稿最重要的纽带——没有它，写作 Agent 将不得不从原始结果文件中重新推导故事线。

**创建 `experiment_log.md`**，结构如下：

```markdown
# 实验日志

## 贡献（一句话）
[论文的主要主张]

## 已运行的实验

### 实验 1：[名称]
- **测试的主张**：[这支持了论文的哪个主张]
- **设置**：[模型、数据集、配置、运行次数]
- **关键结果**：[包含数字的一句话]
- **结果文件**：results/exp1/final_info.json
- **生成的图表**：figures/exp1_comparison.pdf
- **意外发现**：[任何意外情况]

### 实验 2：[名称]
...

## 图表
| 文件名 | 描述 | 所属章节 |
|----------|-------------|---------------------------|
| figures/main_comparison.pdf | 在基准 X 上比较所有方法的条形图 | 结果，图 2 |
| figures/ablation.pdf | 移除组件 A、B、C 的消融实验 | 结果，图 3 |
...

## 失败的实验（为诚实而记录）
- [尝试了什么，为什么失败，它告诉了我们什么]

## 开放性问题
- [结果引发的、论文应解决的任何问题]
```

**为什么这很重要**：在起草时，Agent（或委派的子 Agent）可以加载 `experiment_log.md` 和 LaTeX 模板，并基于实际结果生成初稿。没有这个桥梁，写作 Agent 必须解析原始的 JSON/CSV 文件并推断故事线——这是导致数字被捏造或误报的常见原因。

**Git 规范**：将此日志与其描述的结果一起提交。

---

## 迭代优化：策略选择

此流水线中的任何输出——论文草稿、实验脚本、分析——都可以迭代优化。自推理研究为每种优化策略何时有效、何时失败提供了经验证据。使用本节内容来选择正确的方法。

### 快速决策表

| 你的情况 | 策略 | 原因 |
|---------------|----------|-----|
| 中端模型 + 约束性任务 | **自推理** | 最佳点。生成与评估之间的差距最大。基线方法会主动破坏弱模型的输出。 |
| 中端模型 + 开放性任务 | **添加范围约束的自推理** | 添加固定事实、结构或交付物来限定改进空间。 |
| 前沿模型 + 约束性任务 | **自推理** | 即使在最前沿，也能在 2/3 的约束性任务中胜出。 |
| 前沿模型 + 无约束任务 | **批判与修订** 或 **单次通过** | 自推理排在最后。模型的自我评估已经足够好。 |
| 具体技术任务（系统设计） | **批判与修订** | 直接的查找-修复循环更高效。 |
| 模板填充任务（一种正确结构） | **单次通过** 或 **保守策略** | 决策空间最小。迭代不增加价值。 |
| 带有测试用例的代码 | **自推理（代码变体）** | 在修复前，对*为什么*失败进行结构化分析。恢复率为 62% 对 43%。 |
| 非常弱的模型（Llama 8B 级别） | **单次通过** | 模型太弱，无法生成多样化的候选方案。应投资于生成质量。 |
### 生成-评估差距

**核心洞察**：Autoreason 的价值取决于模型的生成能力与其自我评估能力之间的差距。

```
模型层级        │ 生成能力 │ 自我评估 │ 差距    │ Autoreason 价值
──────────────────┼────────────┼───────────┼────────┼─────────────────
弱 (Llama 8B)     │ 差        │ 差        │ 小     │ 无 — 无法生成多样化的候选方案
中 (Haiku 3.5)    │ 尚可      │ 差        │ 大     │ 最大 — 42/42 完美 Borda 计数
中 (Gemini Flash) │ 尚可      │ 中等      │ 大     │ 高 — 赢得 2/3
强 (Sonnet 4)     │ 好        │ 尚可      │ 中等   │ 中等 — 赢得 3/5
前沿 (S4.6)       │ 优秀      │ 好        │ 小     │ 仅在有限制条件下有效
```

这种差距是结构性的，而非暂时的。随着成本下降，今天的前沿模型会成为明天的中端模型。最佳应用点会移动，但永远不会消失。

### Autoreason 循环（摘要）

每一轮都会由全新的、独立的 Agent 生成三个候选方案：

1.  **批评者** → 找出当前方案 A 的问题（不提供修复）
2.  **作者 B** → 基于批评意见修订 A
3.  **合成器** → 合并 A 和 B（随机化标签）
4.  **评审团** → 3 位盲审的 CoT 评审员通过 Borda 计数法对 A、B、AB 进行排序
5.  **收敛** → A 连续赢得 k=2 轮 → 完成

**关键参数：**
-   k=2 收敛（k=1 过早，k=3 成本过高，无质量增益）
-   始终使用 CoT 评审员（收敛速度快 3 倍）
-   作者温度 0.8，评审员温度 0.3
-   保守的平局处理：当前方案在平局时获胜
-   每个角色都是没有共享上下文的全新 Agent

### 应用于论文草稿

通过 Autoreason 精炼论文本身时：
-   **为批评者提供事实依据**：实际的实验数据、结果 JSON、统计输出。没有这些，模型会编造虚假的消融研究和置信区间。
-   **至少使用 3 位有效的评审员**：一个损坏的评审员解析器不会增加噪音——它会完全阻止达到平衡。
-   **限定修订范围**：“解决这些具体弱点”，而不是“改进论文”。

### 失败模式

| 失败模式 | 检测方法 | 修复方法 |
|---------|-----------|-----|
| 不收敛（A 从未获胜） | 超过 20 轮后 A 获胜率 <15% | 为任务添加范围限制 |
| 合成漂移 | 字数无限制增长 | 限制结构和交付物 |
| 低于单轮质量 | 基线得分高于迭代输出 | 切换到单轮；模型可能太弱 |
| 过拟合（代码） | 公开测试通过率高，私有测试通过率低 | 使用结构化分析，而不仅仅是测试反馈 |
| 评审员损坏 | 解析失败导致评审团少于 3 人 | 在继续之前修复解析器 |

完整提示词、Borda 计分细节、模型选择指南、范围限制设计模式和计算预算参考，请参见 [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md)。

---

## 阶段 5：论文起草

**目标**：撰写一篇完整、可发表的论文。

### 大型项目的上下文管理

一个包含 50 多个实验文件、多个结果目录和大量文献笔记的论文项目很容易超出 Agent 的上下文窗口。需要主动管理：

**每个起草任务应加载到上下文中的内容：**

| 起草任务 | 加载到上下文中 | 不加载 |
|---------------|------------------|-------------|
| 撰写引言 | `experiment_log.md`、贡献声明、5-10 篇最相关的论文摘要 | 原始结果 JSON、完整的实验脚本、所有文献笔记 |
| 撰写方法 | 实验配置、伪代码、架构描述 | 原始日志、其他实验的结果 |
| 撰写结果 | `experiment_log.md`、结果汇总表、图表列表 | 完整的分析脚本、中间数据 |
| 撰写相关工作 | 整理好的引用笔记（步骤 1.4 输出）、.bib 文件 | 实验文件、原始 PDF |
| 修订轮次 | 完整的论文草稿、具体的审稿人意见 | 其他所有内容 |

**原则：**
-   **`experiment_log.md` 是主要的上下文桥梁** — 它总结了写作所需的一切，而无需加载原始数据文件（见步骤 4.6）
-   **委派时，一次只加载一个部分的上下文**。负责起草方法的子 Agent 不需要文献综述笔记。
-   **总结，不要包含原始文件。** 对于一个 200 行的结果 JSON，加载一个 10 行的汇总表。对于一篇 50 页的相关论文，加载 5 句话的摘要 + 你关于其相关性的 2 行笔记。
-   **对于非常大的项目**：创建一个包含预压缩摘要的 `context/` 目录：
    ```
    context/
      contribution.md          # 1 句话
      experiment_summary.md    # 关键结果表（来自 experiment_log.md）
      literature_map.md        # 整理好的引用笔记
      figure_inventory.md      # 图表列表及描述
    ```

### 叙事原则

**最关键的一个洞察**：你的论文不是一系列实验的集合——它是一个有明确贡献、并由证据支撑的故事。

每一篇成功的机器学习论文都围绕 Neel Nanda 所说的“叙事”展开：一个简短、严谨、基于证据的技术故事，其结论是读者所关心的。

**三大支柱（必须在引言结束时清晰阐明）：**

| 支柱 | 描述 | 检验标准 |
|--------|-------------|------|
| **是什么** | 1-3 个具体的新颖主张 | 你能用一句话概括它们吗？ |
| **为什么** | 严谨的经验证据 | 实验能否将你的假设与替代方案区分开？ |
| **那又如何** | 读者为何应该关心 | 这是否与公认的社区问题相关联？ |

**如果你不能用一句话说出你的贡献，那么你还没有一篇论文。**

### 本指南背后的来源

本技能综合了在顶级会议上发表过大量论文的研究人员的写作哲学。写作哲学层最初由 [Orchestra Research](https://github.com/orchestra-research) 作为 `ml-paper-writing` 技能整理。

| 来源 | 关键贡献 | 链接 |
|--------|-----------------|------|
| **Neel Nanda** (Google DeepMind) | 叙事原则，是什么/为什么/那又如何框架 | [如何撰写 ML 论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) |
| **Sebastian Farquhar** (DeepMind) | 5 句话摘要公式 | [如何撰写 ML 论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| **Gopen & Swan** | 读者期望的 7 条原则 | [科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| **Zachary Lipton** | 措辞选择，消除模糊表述 | [科学写作启发式](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| **Jacob Steinhardt** (UC Berkeley) | 精确性，一致的术语 | [写作技巧](https://bounded-regret.ghost.io/) |
| **Ethan Perez** (Anthropic) | 微观层面的清晰度技巧 | [简单的论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/) |
| **Andrej Karpathy** | 单一贡献焦点 | 各种讲座 |
**如需深入了解以下任何内容，请参阅：**
- [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) — 包含示例的完整说明
- [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) — 完整的参考文献列表

### 时间分配

将时间大致**平均分配**给以下各部分：
1. 摘要
2. 引言
3. 图表
4. 其余所有部分的总和

**为什么？** 大多数审稿人在读到你的方法部分之前就已经形成了判断。读者阅读论文的顺序是：标题 → 摘要 → 引言 → 图表 → 可能阅读其余部分。

### 写作工作流

```
论文写作清单：
- [ ] 步骤 1：定义一句话贡献
- [ ] 步骤 2：起草图 1（核心思想或最引人注目的结果）
- [ ] 步骤 3：起草摘要（5 句话公式）
- [ ] 步骤 4：起草引言（最多 1-1.5 页）
- [ ] 步骤 5：起草方法
- [ ] 步骤 6：起草实验与结果
- [ ] 步骤 7：起草相关工作
- [ ] 步骤 8：起草结论与讨论
- [ ] 步骤 9：起草局限性（所有会议/期刊都要求）
- [ ] 步骤 10：规划附录（证明、额外实验、细节）
- [ ] 步骤 11：完成论文清单
- [ ] 步骤 12：最终审阅
```

### 两轮精炼模式

使用 AI Agent 起草时，采用**两轮**方法（在 SakanaAI 的 AI-Scientist 流水线中证明有效）：

**第一轮 — 按节写作 + 立即精炼：**
对于每一节，先完成完整草稿，然后在同一上下文中立即进行精炼。这能在该节内容新鲜时捕捉局部问题（清晰度、流畅度、完整性）。

**第二轮 — 基于全文上下文的全局精炼：**
所有节起草完成后，带着对整篇论文的认知重新审视每一节。这能捕捉跨节问题：冗余、术语不一致、叙事流，以及一节承诺了但另一节未兑现的空白。

```
第二轮精炼提示词（针对每一节）：
"在完整论文的上下文中审阅 [SECTION]。
- 它是否与论文其余部分契合？是否与其他节存在冗余？
- 术语是否与引言和方法部分保持一致？
- 是否有任何内容可以删减而不削弱核心信息？
- 叙事是否从前一节流畅过渡到下一节？
进行最小化、有针对性的编辑。不要从头重写。"
```

### LaTeX 错误清单

将此清单附加到每个精炼提示词后。这是 LLM 编写 LaTeX 时最常见的错误：

```
LaTeX 质量清单（每次编辑后验证）：
- [ ] 没有未闭合的数学符号（$ 符号成对出现）
- [ ] 只引用存在的图表（\ref 与 \label 匹配）
- [ ] 没有捏造的引用（\cite 与 .bib 文件中的条目匹配）
- [ ] 每个 \begin{env} 都有匹配的 \end{env}（尤其是 figure, table, algorithm）
- [ ] 没有 HTML 污染（例如使用 </end{figure}> 而不是 \end{figure}）
- [ ] 数学模式外没有未转义的下划线（在文本中使用 \_）
- [ ] 没有重复的 \label 定义
- [ ] 没有重复的章节标题
- [ ] 文本中的数字与实际实验结果匹配
- [ ] 所有图表都有标题和标签
- [ ] 没有过长的行导致 overfull hbox 警告
```

### 步骤 5.0：标题

标题是论文中被阅读次数最多的单一元素。它决定了是否有人会点击阅读摘要。

**好的标题**：
- 陈述贡献或发现："Autoreason: When Iterative LLM Refinement Works and Why It Fails"
- 突出令人惊讶的结果："Scaling Data-Constrained Language Models"（暗示你做到了）
- 命名方法 + 其作用："DPO: Direct Preference Optimization of Language Models"

**差的标题**：
- 过于笼统："An Approach to Improving Language Model Outputs"
- 过长：超过约 15 个单词
- 全是术语："Asymptotic Convergence of Iterative Stochastic Policy Refinement"（这是给谁看的？）

**规则**：
- 如果你有方法名称，请包含它（便于引用）
- 包含 1-2 个审稿人会搜索的关键词
- 避免使用冒号，除非冒号两边都有意义
- 测试：审稿人能否仅从标题就知道领域和贡献？

### 步骤 5.1：摘要（5 句话公式）

来自 Sebastian Farquhar (DeepMind)：

```
1. 你取得了什么成就："我们引入了...", "我们证明了...", "我们展示了..."
2. 为什么这很难且很重要
3. 你如何做到（使用专业关键词以提高可发现性）
4. 你有什么证据
5. 你最显著的数字/结果
```

**删除** 像 "Large language models have achieved remarkable success..." 这样的通用开头。

### 步骤 5.2：图 1

图 1 是大多数读者看的第二样东西（在摘要之后）。在写引言之前先起草它——这会迫使你理清核心思想。

| 图 1 类型 | 何时使用 | 示例 |
|---------------|-------------|---------|
| **方法示意图** | 新架构或流水线 | 展示你系统的 TikZ 流程图 |
| **结果预告图** | 一个引人注目的结果能讲述整个故事 | 条形图："我们的方法 vs 基线"，有清晰的差距 |
| **问题示意图** | 问题不直观 | 展示你修复的故障模式的前后对比 |
| **概念图** | 抽象贡献需要视觉基础 | 方法属性的 2x2 矩阵 |

**规则**：图 1 必须在不阅读任何文字的情况下即可理解。仅凭标题就应该能传达核心思想。有目的地使用颜色——不要仅仅为了装饰。

### 步骤 5.3：引言（最多 1-1.5 页）

必须包含：
- 清晰的问题陈述
- 简要的方法概述
- 2-4 个要点的贡献列表（双栏格式下，每点最多 1-2 行）
- 方法部分应在第 2-3 页开始

### 步骤 5.4：方法

确保可复现：
- 概念性概述或伪代码
- 列出所有超参数
- 提供足以复现的架构细节
- 呈现最终设计决策；消融实验放在实验部分

### 步骤 5.5：实验与结果

对于每个实验，明确说明：
- **它支持什么主张**
- 它如何与主要贡献相关联
- 观察什么："蓝线显示了 X，这证明了 Y"
### 步骤 5.6：相关工作

按方法论组织，而非逐篇罗列论文。慷慨引用——审稿人很可能就是相关论文的作者。

### 步骤 5.7：局限性（必需）

所有主流会议都要求此部分。诚实有益：
- 审稿人被指示不会因诚实地承认局限性而扣分
- 通过首先指出弱点来预先应对批评
- 解释为何这些局限性不会削弱核心主张

### 步骤 5.8：结论与讨论

**结论**（必需，0.5-1页）：
- 用一句话重述贡献（措辞与摘要不同）
- 总结关键发现（2-3句话，非列表形式）
- 意义：这对该领域意味着什么？
- 未来工作：2-3个具体的后续步骤（避免模糊的“我们将X留给未来工作”）

**讨论**（可选，有时与结论合并）：
- 超出直接结果的更广泛意义
- 与其他子领域的联系
- 对方法何时有效、何时无效的诚实评估
- 实际部署的考量

**切勿**在结论中引入新的结果或主张。

### 步骤 5.9：附录策略

所有主流会议对附录页数没有限制，附录对于可复现性至关重要。结构如下：

| 附录章节 | 内容 |
|-----------------|---------------|
| **证明与推导** | 正文中篇幅过长的完整证明。正文可以陈述定理并注明“证明见附录A”。 |
| **补充实验** | 消融实验、缩放曲线、各数据集细分结果、超参数敏感性分析 |
| **实现细节** | 完整的超参数表、训练细节、硬件规格、随机种子 |
| **数据集文档** | 数据收集过程、标注指南、许可协议、预处理步骤 |
| **提示词与模板** | 使用的确切提示词（针对基于LLM的方法）、评估模板 |
| **人工评估** | 标注界面截图、给标注者的说明、IRB详情 |
| **补充图表** | 各任务细分结果、轨迹可视化、失败案例示例 |

**规则**：
- 正文必须自成一体——审稿人没有义务阅读附录
- 切勿将关键证据仅放在附录中
- 交叉引用：使用“完整结果见表5（附录B）”，而非仅仅“见附录”
- 使用 `\appendix` 命令，然后使用 `\section{A: 证明}` 等

### 页面预算管理

当超出页数限制时：

| 削减策略 | 节省页数 | 风险 |
|-------------|-------|------|
| 将证明移至附录 | 0.5-2页 | 低——标准做法 |
| 压缩相关工作 | 0.5-1页 | 中——可能遗漏关键引用 |
| 将表格与子图合并 | 0.25-0.5页 | 低——通常能提高可读性 |
| 谨慎使用 `\vspace{-Xpt}` | 0.1-0.3页 | 如果使用巧妙则风险低，如果明显则风险高 |
| 移除定性示例 | 0.5-1页 | 中——审稿人喜欢示例 |
| 缩小图表尺寸 | 0.25-0.5页 | 高——图表必须保持可读性 |

**切勿**：减小字体大小、更改页边距、删除必需章节（局限性、更广泛影响），或在正文中使用 `\small`/`\footnotesize`。

### 步骤 5.10：伦理与更广泛影响声明

现在大多数会议都要求或强烈建议提供伦理/更广泛影响声明。这不是模板套话——审稿人会阅读，并且可以标记伦理问题，导致直接拒稿。

**应包含的内容：**

| 组成部分 | 内容 | 要求方 |
|-----------|---------|-------------|
| **积极的社会影响** | 您的工作如何造福社会 | NeurIPS, ICML |
| **潜在的负面影响** | 滥用风险、双重用途问题、失败模式 | NeurIPS, ICML |
| **公平性与偏见** | 您的方法/数据是否存在已知偏见？ | 所有会议（隐含要求） |
| **环境影响** | 大规模训练的计算碳足迹 | ICML, NeurIPS 日益要求 |
| **隐私** | 您的工作是否使用或支持处理个人数据？ | ACL, NeurIPS |
| **LLM 使用披露** | 是否使用 AI 进行写作或实验？ | ICLR（强制）, ACL |

**撰写声明：**

```latex
\section*{更广泛影响声明}
% NeurIPS/ICML：位于结论之后，不计入页数限制

% 1. 积极应用（1-2句话）
这项工作实现了[具体应用]，可能使[特定群体]受益。

% 2. 风险与缓解措施（1-3句话，具体说明）
[方法/模型]可能被滥用于[具体风险]。我们通过[具体缓解措施，例如，仅发布大于X尺寸的模型权重、包含安全过滤器、记录失败模式]来缓解此风险。

% 3. 影响声明的局限性（1句话）
我们的评估仅限于[特定领域]；更广泛的部署需要[具体的额外工作]。
```

**常见错误：**
- 写“我们预见没有负面影响”（几乎从不正确——审稿人不信任此说法）
- 含糊其辞：“这可能被滥用”，但没有具体说明如何滥用
- 忽略大规模工作的计算成本
- 在要求披露的会议上忘记披露 LLM 使用情况

**计算碳足迹**（针对训练密集型论文）：
```python
# 使用 ML CO2 Impact 工具方法估算
gpu_hours = 1000  # 总 GPU 小时数
gpu_tdp_watts = 400  # 例如，A100 = 400W
pue = 1.1  # 电力使用效率（数据中心开销）
carbon_intensity = 0.429  # kg CO2/kWh（美国平均值；因地区而异）

energy_kwh = (gpu_hours * gpu_tdp_watts * pue) / 1000
carbon_kg = energy_kwh * carbon_intensity
print(f"Energy: {energy_kwh:.0f} kWh, Carbon: {carbon_kg:.0f} kg CO2eq")
```

### 步骤 5.11：数据表与模型卡（如适用）

如果您的论文引入了**新数据集**或**发布了模型**，请包含结构化文档。审稿人对此的期望越来越高，NeurIPS 数据集与基准赛道也要求提供。

**数据集数据表**（Gebru 等人，2021）——包含在附录中：

```
数据集文档（附录）：
- 动机：为何创建此数据集？它支持什么任务？
- 构成：数据实例是什么？有多少？数据类型是什么？
- 收集：数据如何收集？来源是什么？
- 预处理：应用了哪些清洗/过滤？
- 分发：数据集如何分发？采用何种许可协议？
- 维护：谁维护它？如何报告问题？
- 伦理考量：包含个人数据吗？是否获得同意？潜在的危害？已知的偏见？
```
**模型卡片**（Mitchell 等人，2019）— 模型发布时包含在附录中：

```
模型卡片（附录）：
- 模型详情：架构、训练数据、训练过程
- 预期用途：主要用例、超出范围的用途
- 指标：评估指标和基准测试结果
- 伦理考量：已知偏见、公平性评估
- 局限性：已知的失败模式、模型表现不佳的领域
```

### 写作风格

**句子层面的清晰度（Gopen & Swan 的 7 条原则）：**

| 原则 | 规则 |
|-----------|------|
| 主语-动词邻近性 | 保持主语和动词靠近 |
| 强调位置 | 将重点放在句子末尾 |
| 主题位置 | 将上下文放在前面，新信息放在后面 |
| 旧信息先于新信息 | 熟悉的信息 → 不熟悉的信息 |
| 一个单元，一个功能 | 每个段落阐述一个要点 |
| 动作在动词中 | 使用动词，而非名词化 |
| 上下文先于新信息 | 在呈现前设置好舞台 |

**措辞选择（Lipton, Steinhardt）：**
- 具体化：使用“准确率”而非“性能”
- 消除模糊措辞：除非确实不确定，否则去掉“可能”
- 术语贯穿全文保持一致
- 避免增量词汇：使用“开发”，而非“结合”

**完整的写作指南及示例**：参见 [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md)

### 使用 LaTeX 模板

**始终先复制整个模板目录，然后在其中进行写作。**

```
模板设置检查清单：
- [ ] 步骤 1：将整个模板目录复制到新项目
- [ ] 步骤 2：验证模板原样编译（在进行任何更改之前）
- [ ] 步骤 3：阅读模板的示例内容以理解结构
- [ ] 步骤 4：逐节替换示例内容
- [ ] 步骤 5：使用模板宏（检查导言区中的 \newcommand 定义）
- [ ] 步骤 6：仅在最后清理模板残留内容
```

**步骤 1：复制完整模板**

```bash
cp -r templates/neurips2025/ ~/papers/my-paper/
cd ~/papers/my-paper/
ls -la  # 应该看到：main.tex, neurips.sty, Makefile 等
```

复制**整个**目录，而不仅仅是 .tex 文件。模板包含样式文件 (.sty)、参考文献样式 (.bst)、示例内容和 Makefile。

**步骤 2：首先验证模板编译**

在进行**任何**更改之前：
```bash
latexmk -pdf main.tex
# 或者手动：pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

如果未修改的模板无法编译，请先修复此问题（通常是缺少 TeX 包 — 通过 `tlmgr install <package>` 安装）。

**步骤 3：保留模板内容作为参考**

不要立即删除示例内容。将其注释掉并用作格式参考：
```latex
% 模板示例（保留作为参考）：
% \begin{figure}[t]
%   \centering
%   \includegraphics[width=0.8\linewidth]{example-image}
%   \caption{模板展示了标题样式}
% \end{figure}

% 你的实际图表：
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{your-figure.pdf}
  \caption{你的标题遵循相同的样式。}
\end{figure}
```

**步骤 4：逐节替换内容**

系统地进行：标题/作者 → 摘要 → 引言 → 方法 → 实验 → 相关工作 → 结论 → 参考文献 → 附录。每完成一节后编译。

**步骤 5：使用模板宏**

```latex
\newcommand{\method}{YourMethodName}  % 一致的方法命名
\newcommand{\eg}{e.g.,\xspace}        % 正确的缩写
\newcommand{\ie}{i.e.,\xspace}
```

### 模板常见陷阱

| 陷阱 | 问题 | 解决方案 |
|---------|---------|----------|
| 仅复制 `.tex` 文件 | 缺少 `.sty`，无法编译 | 复制整个目录 |
| 修改 `.sty` 文件 | 破坏会议格式要求 | 切勿编辑样式文件 |
| 随意添加包 | 冲突，破坏模板 | 仅在必要时添加 |
| 过早删除模板内容 | 失去格式参考 | 在完成前保留为注释 |
| 不频繁编译 | 错误累积 | 每节完成后编译 |
| 图表使用栅格 PNG | 论文中模糊 | 始终通过 `savefig('fig.pdf')` 使用矢量 PDF |

### 快速模板参考

| 会议 | 主文件 | 样式文件 | 页数限制 |
|------------|-----------|------------|------------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 9 页 |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 8 页 |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 9 页 |
| ACL 2025 | `acl_latex.tex` | `acl.sty` | 8 页（长文） |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 7 页 |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 9 页 |

**通用规则**：双盲评审，参考文献不计入页数，附录无限制，必须使用 LaTeX。

模板位于 `templates/` 目录。参见 [templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md) 了解编译设置（VS Code, CLI, Overleaf, 其他 IDE）。

### 表格和图表

**表格** — 使用 `booktabs` 进行专业格式化：

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
方法 & 准确率 $\uparrow$ & 延迟 $\downarrow$ \\
\midrule
基线 & 85.2 & 45ms \\
\textbf{我们的方法} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

规则：
- 每个指标的最佳值加粗
- 包含方向符号（$\uparrow$ 越高越好，$\downarrow$ 越低越好）
- 数值列右对齐
- 小数精度保持一致

**图表**：
- **矢量图形**（PDF, EPS）用于所有绘图和图表 — `plt.savefig('fig.pdf')`
- **栅格图形**（PNG 600 DPI）仅用于照片
- **色盲安全调色板**（Okabe-Ito 或 Paul Tol）
- 验证**灰度可读性**（8% 的男性有色觉缺陷）
- **图表内无标题** — 图注即为此功能服务
- **自包含的图注** — 读者无需阅读正文即可理解

### 会议重新投稿

关于在不同会议间转换，请参见第 7 阶段（提交准备）— 其中涵盖了完整的转换工作流、页数变更表和拒稿后指导。
### 专业的 LaTeX 导言区

将这些包添加到任何论文中，以获得专业质量。它们与所有主流会议样式文件兼容：

```latex
% --- 专业包（在会议样式文件之后添加） ---

% 排版
\usepackage{microtype}              % 微排版改进（突出、扩展）
                                     % 使文本明显更精致 — 务必包含

% 表格
\usepackage{booktabs}               % 专业的表格线条（\toprule, \midrule, \bottomrule）
\usepackage{siunitx}                % 一致的数字格式、小数点对齐
                                     % 用法：\num{12345} → 12,345；\SI{3.5}{GHz} → 3.5 GHz
                                     % 表格对齐：S 列类型用于小数点对齐的数字

% 图形
\usepackage{graphicx}               % 包含图形（\includegraphics）
\usepackage{subcaption}             % 带有 (a)、(b)、(c) 标签的子图
                                     % 用法：\begin{subfigure}{0.48\textwidth} ... \end{subfigure}

% 图表和算法
\usepackage{tikz}                   % 可编程矢量图
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc, fit, backgrounds}
\usepackage[ruled,vlined]{algorithm2e}  % 专业的伪代码
                                     % 替代方案：如果模板捆绑了它，则使用 \usepackage{algorithmicx}

% 交叉引用
\usepackage{cleveref}               % 智能引用：\cref{fig:x} → "图 1"
                                     % 必须在 hyperref 之后加载
                                     % 处理：图形、表格、章节、方程、算法

% 数学（通常由会议 .sty 包含，但请验证）
\usepackage{amsmath,amssymb}        % AMS 数学环境和符号
\usepackage{mathtools}              % 扩展 amsmath（dcases、coloneqq 等）

% 颜色（用于图形和图表）
\usepackage{xcolor}                 % 颜色管理
% Okabe-Ito 色盲安全调色板：
\definecolor{okblue}{HTML}{0072B2}
\definecolor{okorange}{HTML}{E69F00}
\definecolor{okgreen}{HTML}{009E73}
\definecolor{okred}{HTML}{D55E00}
\definecolor{okpurple}{HTML}{CC79A7}
\definecolor{okcyan}{HTML}{56B4E9}
\definecolor{okyellow}{HTML}{F0E442}
```

**注意：**
- `microtype` 是对视觉质量影响最大的单个包。它在亚像素级别调整字符间距。务必包含它。
- `siunitx` 通过 `S` 列类型处理表格中的小数点对齐 — 消除了手动间距。
- `cleveref` 必须在 `hyperref` **之后** 加载。大多数会议 .sty 文件会加载 hyperref，因此将 cleveref 放在最后。
- 检查会议模板是否已经加载了这些包中的任何一个（尤其是 `algorithm`、`amsmath`、`graphicx`）。不要重复加载。

### siunitx 表格对齐

`siunitx` 使包含大量数字的表格可读性显著提高：

```latex
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1] S[table-format=2.1]}
\toprule
Method & {Accuracy $\uparrow$} & {F1 $\uparrow$} & {Latency (ms) $\downarrow$} \\
\midrule
Baseline         & 85.2  & 83.7  & 45.3 \\
Ablation (no X)  & 87.1  & 85.4  & 42.1 \\
\textbf{Ours}    & \textbf{92.1} & \textbf{90.8} & \textbf{38.7} \\
\bottomrule
\end{tabular}
```

`S` 列类型自动按小数点对齐。`{}` 中的标题会避开对齐。

### 子图

并排图形的标准模式：

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_a.pdf}
    \caption{Results on Dataset A.}
    \label{fig:results-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_b.pdf}
    \caption{Results on Dataset B.}
    \label{fig:results-b}
  \end{subfigure}
  \caption{Comparison of our method across two datasets. (a) shows the scaling
  behavior and (b) shows the ablation results. Both use 5 random seeds.}
  \label{fig:results}
\end{figure}
```

使用 `\cref{fig:results}` → "图 1"，`\cref{fig:results-a}` → "图 1a"。

### 使用 algorithm2e 的伪代码

```latex
\begin{algorithm}[t]
\caption{Iterative Refinement with Judge Panel}
\label{alg:method}
\KwIn{Task $T$, model $M$, judges $J_1 \ldots J_n$, convergence threshold $k$}
\KwOut{Final output $A^*$}
$A \gets M(T)$ \tcp*{Initial generation}
$\text{streak} \gets 0$\;
\While{$\text{streak} < k$}{
  $C \gets \text{Critic}(A, T)$ \tcp*{Identify weaknesses}
  $B \gets M(T, C)$ \tcp*{Revised version addressing critique}
  $AB \gets \text{Synthesize}(A, B)$ \tcp*{Merge best elements}
  \ForEach{judge $J_i$}{
    $\text{rank}_i \gets J_i(\text{shuffle}(A, B, AB))$ \tcp*{Blind ranking}
  }
  $\text{winner} \gets \text{BordaCount}(\text{ranks})$\;
  \eIf{$\text{winner} = A$}{
    $\text{streak} \gets \text{streak} + 1$\;
  }{
    $A \gets \text{winner}$; $\text{streak} \gets 0$\;
  }
}
\Return{$A$}\;
\end{algorithm}
```

### TikZ 图表模式

TikZ 是 ML 论文中方法图的标准。常见模式：

**流水线/流程图**（ML 论文中最常见）：

```latex
\begin{figure}[t]
\centering
\begin{tikzpicture}[
  node distance=1.8cm,
  box/.style={rectangle, draw, rounded corners, minimum height=1cm, 
              minimum width=2cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
]
  \node[box, fill=okcyan!20] (input) {Input\\$x$};
  \node[box, fill=okblue!20, right of=input] (encoder) {Encoder\\$f_\theta$};
  \node[box, fill=okgreen!20, right of=encoder] (latent) {Latent\\$z$};
  \node[box, fill=okorange!20, right of=latent] (decoder) {Decoder\\$g_\phi$};
  \node[box, fill=okred!20, right of=decoder] (output) {Output\\$\hat{x}$};
  
  \draw[arrow] (input) -- (encoder);
  \draw[arrow] (encoder) -- (latent);
  \draw[arrow] (latent) -- (decoder);
  \draw[arrow] (decoder) -- (output);
\end{tikzpicture}
\caption{Architecture overview. The encoder maps input $x$ to latent 
representation $z$, which the decoder reconstructs.}
\label{fig:architecture}
\end{figure}
```
**对比/矩阵图**（用于展示方法变体）：

```latex
\begin{tikzpicture}[
  cell/.style={rectangle, draw, minimum width=2.5cm, minimum height=1cm, 
               align=center, font=\small},
  header/.style={cell, fill=gray!20, font=\small\bfseries},
]
  % Headers
  \node[header] at (0, 0) {Method};
  \node[header] at (3, 0) {Converges?};
  \node[header] at (6, 0) {Quality?};
  % Rows
  \node[cell] at (0, -1) {Single Pass};
  \node[cell, fill=okgreen!15] at (3, -1) {N/A};
  \node[cell, fill=okorange!15] at (6, -1) {Baseline};
  \node[cell] at (0, -2) {Critique+Revise};
  \node[cell, fill=okred!15] at (3, -2) {No};
  \node[cell, fill=okred!15] at (6, -2) {Degrades};
  \node[cell] at (0, -3) {Ours};
  \node[cell, fill=okgreen!15] at (3, -3) {Yes ($k$=2)};
  \node[cell, fill=okgreen!15] at (6, -3) {Improves};
\end{tikzpicture}
```

**迭代循环图**（用于带有反馈的方法）：

```latex
\begin{tikzpicture}[
  node distance=2cm,
  box/.style={rectangle, draw, rounded corners, minimum height=0.8cm, 
              minimum width=1.8cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
  label/.style={font=\scriptsize, midway, above},
]
  \node[box, fill=okblue!20] (gen) {Generator};
  \node[box, fill=okred!20, right=2.5cm of gen] (critic) {Critic};
  \node[box, fill=okgreen!20, below=1.5cm of $(gen)!0.5!(critic)$] (judge) {Judge Panel};
  
  \draw[arrow] (gen) -- node[label] {output $A$} (critic);
  \draw[arrow] (critic) -- node[label, right] {critique $C$} (judge);
  \draw[arrow] (judge) -| node[label, left, pos=0.3] {winner} (gen);
\end{tikzpicture}
```

### 用于修订跟踪的 latexdiff

对于反驳至关重要 —— 生成一个标记了版本间更改的 PDF：

```bash
# 安装
# macOS: brew install latexdiff (或随 TeX Live 附带)
# Linux: sudo apt install latexdiff

# 生成差异
latexdiff paper_v1.tex paper_v2.tex > paper_diff.tex
pdflatex paper_diff.tex

# 对于多文件项目（使用 \input{} 或 \include{}）
latexdiff --flatten paper_v1.tex paper_v2.tex > paper_diff.tex
```

这会生成一个 PDF，其中删除内容以红色删除线显示，添加内容以蓝色显示 —— 这是反驳补充材料的标准格式。

### 用于 matplotlib 的 SciencePlots

安装并使用以生成符合出版质量的图表：

```bash
pip install SciencePlots
```

```python
import matplotlib.pyplot as plt
import scienceplots  # 注册样式

# 使用科学风格（类似 IEEE，简洁）
with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # 单栏宽度
    ax.plot(x, y, label='Ours', color='#0072B2')
    ax.plot(x, y2, label='Baseline', color='#D55E00', linestyle='--')
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Accuracy')
    ax.legend()
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')

# 可用样式：'science', 'ieee', 'nature', 'science+ieee'
# 如果生成图表的机器上没有安装 LaTeX，请添加 'no-latex'
```

**标准图形尺寸**（双栏格式）：
- 单栏：`figsize=(3.5, 2.5)` —— 适合一栏
- 双栏：`figsize=(7.0, 3.0)` —— 横跨两栏
- 方形：`figsize=(3.5, 3.5)` —— 用于热图、混淆矩阵

---

## 阶段 6：自我审阅与修订

**目标**：在提交前模拟审阅过程。及早发现弱点。

### 步骤 6.1：模拟审阅（集成模式）

从多个角度生成审阅意见。自动化研究流水线（尤其是 SakanaAI 的 AI-Scientist）的关键见解是：**带有元审阅者的集成审阅比单次审阅能产生校准度更高的反馈。**

**步骤 1：生成 N 个独立的审阅意见** (N=3-5)

使用不同的模型或温度设置。每个审阅者只看到论文，看不到其他审阅意见。**默认采用负面偏见** —— LLM 在评估中存在众所周知的积极性偏见。

```
You are an expert reviewer for [VENUE]. You are critical and thorough.
If a paper has weaknesses or you are unsure about a claim, flag it clearly
and reflect that in your scores. Do not give the benefit of the doubt.

Review this paper according to the official reviewer guidelines. Evaluate:

1. Soundness (are claims well-supported? are baselines fair and strong?)
2. Clarity (is the paper well-written? could an expert reproduce it?)
3. Significance (does this matter to the community?)
4. Originality (new insights, not just incremental combination?)

Provide your review as structured JSON:
{
  "summary": "2-3 sentence summary",
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1 (most critical)", "weakness 2", ...],
  "questions": ["question for authors 1", ...],
  "missing_references": ["paper that should be cited", ...],
  "soundness": 1-4,
  "presentation": 1-4,
  "contribution": 1-4,
  "overall": 1-10,
  "confidence": 1-5
}
```

**步骤 2：元审阅（领域主席汇总）**

将所有 N 份审阅意见输入给一个元审阅者：

```
You are an Area Chair at [VENUE]. You have received [N] independent reviews
of a paper. Your job is to:

1. Identify consensus strengths and weaknesses across reviewers
2. Resolve disagreements by examining the paper directly
3. Produce a meta-review that represents the aggregate judgment
4. Use AVERAGED numerical scores across all reviews

Be conservative: if reviewers disagree on whether a weakness is serious,
treat it as serious until the authors address it.

Reviews:
[review_1]
[review_2]
...
```

**步骤 3：反思循环**（可选，2-3 轮）

每个审阅者在看到元审阅意见后可以完善自己的审阅意见。使用提前终止哨兵：如果审阅者回应“I am done”（无更改），则停止迭代。

**用于审阅的模型选择**：审阅最好使用可用的最强模型完成，即使你使用更便宜的模型撰写论文。审阅模型的选择应独立于写作模型。

**少样本校准**：如果可能，包含 1-2 份来自目标会议的真实已发表审阅意见作为示例。这能显著提高分数校准度。请参阅 [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) 获取示例审阅意见。
### 步骤 6.1b：视觉审查环节（VLM）

纯文本审查会遗漏一整类问题：图表质量、布局问题、视觉一致性。如果你能访问具备视觉能力的模型，请对编译后的 PDF 进行单独的**视觉审查**：

```
你正在审查这份研究论文 PDF 的视觉呈现。
检查以下内容：
1.  图表质量：图表可读吗？标签清晰吗？颜色可区分吗？
2.  图表-标题对齐：每个标题是否准确描述了其对应的图表？
3.  布局问题：孤立的章节标题、尴尬的分页符、图表远离其引用位置
4.  表格格式：列对齐、小数精度一致、最佳结果加粗
5.  视觉一致性：所有图表使用相同的配色方案、字体大小一致
6.  灰度可读性：如果以黑白打印，图表还能理解吗？

对于每个问题，请指定页码和确切位置。
```

这能捕捉到基于文本的审查无法发现的问题：坐标轴标签不清晰的图表、距离首次引用位置 3 页远的图表、图 2 和图 5 之间不一致的调色板，或者明显超出列宽的表格。

### 步骤 6.1c：声明验证环节

模拟审查后，运行一个单独的验证环节。这能捕捉到审稿人可能遗漏的事实性错误：

```
声明验证协议：
1.  从论文中提取每一个事实性声明（数字、比较、趋势）
2.  对于每个声明，追溯其支持它的具体实验/结果
3.  验证论文中的数字与实际结果文件是否匹配
4.  将任何没有可追溯来源的声明标记为 [VERIFY]
```

对于基于 Agent 的工作流：将验证任务委派给一个**全新的子 Agent**，它只接收论文文本和原始结果文件。全新的上下文可以防止确认偏差——验证者不会“记得”结果应该是什么。

### 步骤 6.2：优先级排序反馈

收集审查意见后，进行分类：

| 优先级 | 行动 |
|----------|--------|
| **关键**（技术缺陷、缺少基线） | 必须修复。可能需要新的实验 → 回到阶段 2 |
| **高**（清晰度问题、缺少消融实验） | 应在此次修订中修复 |
| **中**（次要的写作问题、额外的实验） | 如果时间允许则修复 |
| **低**（风格偏好、无关紧要的建议） | 记录供未来工作参考 |

### 步骤 6.3：修订周期

对于每个关键/高级别问题：
1.  确定受影响的具体章节
2.  起草修复方案
3.  验证修复不会破坏其他声明
4.  更新论文
5.  对照审稿人的意见重新检查

### 步骤 6.4：撰写反驳意见

在回应实际审稿意见（提交后）时，反驳意见的撰写技巧与修订不同：

**格式**：逐点回应。针对每位审稿人的意见：
```
> R1-W1: "论文缺少与方法 X 的比较。"

我们感谢审稿人的建议。我们已在表 3（修订版）中添加了与方法 X 的比较。
我们的方法在 [指标] 上优于 X 3.2 个百分点（p<0.05）。我们注意到 X 需要 2 倍于我们的计算预算。
```

**规则**：
-   回应每一个问题——如果你跳过某个问题，审稿人会注意到
-   用最强的回应开头
-   简洁直接——审稿人要阅读数十份反驳意见
-   如果在反驳期内进行了实验，请包含新结果
-   即使面对薄弱的批评，也绝不要表现出防御性或轻蔑态度
-   使用 `latexdiff` 生成显示更改的标记 PDF（参见专业 LaTeX 工具部分）
-   感谢审稿人提出具体、可操作的反馈（而非泛泛的赞扬）

**不要做的事**：没有证据的“我们尊重地不同意”。没有解释的“这超出了范围”。只回应优点而忽略弱点。

### 步骤 6.5：论文演进跟踪

在关键节点保存快照：
```
paper/
  paper.tex                    # 当前工作版本
  paper_v1_first_draft.tex     # 第一个完整草稿
  paper_v2_post_review.tex     # 模拟审查后
  paper_v3_pre_submission.tex  # 提交前的最终版
  paper_v4_camera_ready.tex    # 录用后的最终版
```

---

## 阶段 7：提交准备

**目标**：最终检查、格式化和提交。

### 步骤 7.1：会议清单

每个会议都有强制性的清单。请仔细完成——清单不完整可能导致直接拒稿。

请参阅 [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) 获取：
-   NeurIPS 16 项论文清单
-   ICML 更广泛影响 + 可复现性
-   ICLR LLM 披露政策
-   ACL 强制限制部分
-   通用提交前清单

### 步骤 7.2：匿名化清单

双盲评审意味着审稿人不能知道论文作者是谁。请检查以下所有项目：

```
匿名化清单：
- [ ] PDF 中任何地方都没有作者姓名或单位信息
- [ ] 没有致谢部分（录用后添加）
- [ ] 自引用使用第三人称："Smith 等人 [1] 表明..." 而不是 "我们之前表明 [1]..."
- [ ] 没有指向个人仓库的 GitHub/GitLab URL
- [ ] 代码链接使用匿名 GitHub (https://anonymous.4open.science/)
- [ ] 图表中没有机构标识或徽标
- [ ] 文件元数据中没有包含作者姓名（检查 PDF 属性）
- [ ] 没有 "我们之前的工作" 或 "在我们早期的论文中" 这类措辞
- [ ] 数据集名称不透露机构信息（如有需要则重命名）
- [ ] 补充材料不包含识别信息
```

**常见错误**：补充代码中可见的 Git 提交信息、来自机构工具的水印图表、前一稿中遗留的致谢、在匿名期之前发布的 arXiv 预印本。

### 步骤 7.3：格式验证

```
提交前格式检查：
- [ ] 遵守页数限制（参考文献和附录除外）
- [ ] 所有图表均为矢量（PDF）或高分辨率栅格（600 DPI PNG）
- [ ] 所有图表在灰度模式下可读
- [ ] 所有表格使用 booktabs
- [ ] 参考文献编译正确（引用中没有 "?"）
- [ ] 关键区域没有 overfull hboxes
- [ ] 附录标签清晰且分隔明确
- [ ] 所需章节齐全（限制、更广泛影响等）
```
### 步骤 7.4：预编译验证

在尝试运行 `pdflatex` **之前**，先运行这些自动化检查。在此处捕获错误比调试编译器输出更快。

```bash
# 1. 使用 chktex 进行代码检查（捕获常见的 LaTeX 错误）
# 抑制嘈杂的警告：-n2（句子结尾），-n24（括号），-n13（句间），-n1（命令终止）
chktex main.tex -q -n2 -n24 -n13 -n1

# 2. 验证所有引用在 .bib 文件中都存在
# 从 .tex 文件中提取 \cite{...}，并针对 .bib 文件检查每个引用
python3 -c "
import re
tex = open('main.tex').read()
bib = open('references.bib').read()
cites = set(re.findall(r'\\\\cite[tp]?{([^}]+)}', tex))
for cite_group in cites:
    for cite in cite_group.split(','):
        cite = cite.strip()
        if cite and cite not in bib:
            print(f'WARNING: \\\\cite{{{cite}}} not found in references.bib')
"

# 3. 验证所有引用的图片文件都存在于磁盘上
python3 -c "
import re, os
tex = open('main.tex').read()
figs = re.findall(r'\\\\includegraphics(?:\[.*?\])?{([^}]+)}', tex)
for fig in figs:
    if not os.path.exists(fig):
        print(f'WARNING: Figure file not found: {fig}')
"

# 4. 检查重复的 \label 定义
python3 -c "
import re
from collections import Counter
tex = open('main.tex').read()
labels = re.findall(r'\\\\label{([^}]+)}', tex)
dupes = {k: v for k, v in Counter(labels).items() if v > 1}
for label, count in dupes.items():
    print(f'WARNING: Duplicate label: {label} (appears {count} times)')
"
```

在继续之前修复所有警告。对于基于 Agent 的工作流：将 chktex 的输出反馈给 Agent，并指示其进行最小化的修复。

### 步骤 7.5：最终编译

```bash
# 清理构建
rm -f *.aux *.bbl *.blg *.log *.out *.pdf
latexmk -pdf main.tex

# 或者手动编译（三次 pdflatex + bibtex 用于交叉引用）
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# 验证输出文件存在且有内容
ls -la main.pdf
```

**如果编译失败**：解析 `.log` 文件中的第一个错误。常见修复方法：
- "Undefined control sequence" → 缺少包或命令名拼写错误
- "Missing $ inserted" → 数学符号在数学模式外使用
- "File not found" → 图片路径错误或缺少 .sty 文件
- "Citation undefined" → .bib 条目缺失或未运行 bibtex

### 步骤 7.6：会议特定要求

| 会议 | 特殊要求 |
|-------|---------------------|
| **NeurIPS** | 附录中包含论文检查清单，如果被接受则需要通俗摘要 |
| **ICML** | 更广泛影响声明（在结论之后，不计入页数限制） |
| **ICLR** | 需要 LLM 披露声明，互惠评审协议 |
| **ACL** | 强制性局限性章节，负责任 NLP 检查清单 |
| **AAAI** | 严格的样式文件 — 不允许任何修改 |
| **COLM** | 为语言模型社区阐述贡献 |

### 步骤 7.7：会议重新提交与格式转换

在不同会议之间转换格式时，**切勿在模板之间复制 LaTeX 导言区**：

```bash
# 1. 使用目标模板重新开始
cp -r templates/icml2026/ new_submission/

# 2. 仅复制内容章节（而非导言区）
#    - 摘要文本、章节内容、图片、表格、参考文献条目

# 3. 根据页数限制进行调整
# 4. 添加会议特定的必需章节
# 5. 更新参考文献
```

| 从 → 到 | 页数变化 | 关键调整 |
|-----------|-------------|-----------------|
| NeurIPS → ICML | 9 → 8 | 删减 1 页，添加更广泛影响声明 |
| ICML → ICLR | 8 → 9 | 扩展实验，添加 LLM 披露声明 |
| NeurIPS → ACL | 9 → 8 | 为 NLP 惯例重构，添加局限性章节 |
| ICLR → AAAI | 9 → 7 | 大幅删减，严格遵守样式要求 |
| 任意 → COLM | 可变 → 9 | 为语言模型焦点重新阐述 |

删减页数时：将证明移至附录，压缩相关工作，合并表格，使用子图。
扩展时：添加消融实验，扩展局限性，包含额外的基线，添加定性示例。

**被拒稿后**：在新版本中解决审稿人的关切，但不要包含"修改说明"章节或引用之前的提交（盲审）。

### 步骤 7.8：最终版准备（录用后）

录用后，准备最终版：

```
最终版检查清单：
- [ ] 去匿名化：添加作者姓名、单位、邮箱地址
- [ ] 添加致谢章节（资金、计算资源资助、有帮助的审稿人）
- [ ] 添加公开代码/数据 URL（真实的 GitHub，而非匿名链接）
- [ ] 处理元审稿人要求的任何强制性修改
- [ ] 将模板切换到最终版模式（如果适用 — 例如，AAAI 的 \anon → \camera）
- [ ] 添加版权声明（如果会议要求）
- [ ] 更新文本中任何"匿名"占位符
- [ ] 验证最终 PDF 编译无误
- [ ] 检查最终版的页数限制（有时与提交版不同）
- [ ] 将补充材料（代码、数据、附录）上传至会议门户
```

### 步骤 7.9：arXiv 与预印本策略

在 ML 领域，发布到 arXiv 是标准做法，但涉及重要的时机和匿名性考量。

**时机决策树：**

| 情况 | 建议 |
|-----------|---------------|
| 提交到双盲会议（NeurIPS、ICML、ACL） | 在提交截止日期**之后**发布到 arXiv，而不是之前。提前发布可能在技术上违反匿名政策，尽管执行力度不一。 |
| 提交到 ICLR | ICLR 明确允许在提交前发布到 arXiv。但不要在提交的论文中写上作者姓名。 |
| 论文已在 arXiv 上，提交到新会议 | 大多数会议都接受。在评审期间，**不要**更新 arXiv 版本以包含引用评审意见的修改。 |
| 研讨会论文 | 随时发布到 arXiv 都可以 — 研讨会通常不是双盲的。 |
| 希望确立优先权 | 如果担心被抢先发表，立即发布 — 但要接受匿名性的权衡。 |

**arXiv 类别选择**（ML/AI 论文）：

| 类别 | 代码 | 最适合 |
|----------|------|----------|
| 机器学习 | `cs.LG` | 通用 ML 方法 |
| 计算与语言 | `cs.CL` | NLP，语言模型 |
| 人工智能 | `cs.AI` | 推理，规划，Agent |
| 计算机视觉 | `cs.CV` | 视觉模型 |
| 信息检索 | `cs.IR` | 搜索，推荐 |
**列出主要类别 + 1-2 个交叉列出的类别。** 类别越多，可见度越高，但仅在真正相关时才进行交叉列出。

**版本控制策略：**
- **v1**：初始提交（与会议提交内容一致）
- **v2**：接收后带有最终稿修正的版本（在摘要中添加"accepted at [会议名称]"）
- 在评审期间，不要发布明显回应审稿人反馈的 v2 版本

```bash
# 检查你的论文标题是否已在 arXiv 上被使用
# （在选择标题之前）
pip install arxiv
python -c "
import arxiv
results = list(arxiv.Search(query='ti:\"Your Exact Title\"', max_results=5).results())
print(f'Found {len(results)} matches')
for r in results: print(f'  {r.title} ({r.published.year})')
"
```

### 步骤 7.10：研究代码打包

发布干净、可运行的代码能显著增加引用次数和审稿人的信任度。将代码与最终稿一起打包提交。

**代码仓库结构：**

```
your-method/
  README.md              # 设置、使用、复现说明
  requirements.txt       # 或者用于 conda 的 environment.yml
  setup.py               # 用于可通过 pip 安装的包
  LICENSE                # 研究推荐使用 MIT 或 Apache 2.0 许可证
  configs/               # 实验配置
  src/                   # 核心方法实现
  scripts/               # 训练、评估、分析脚本
    train.py
    evaluate.py
    reproduce_table1.sh  # 每个主要结果对应一个脚本
  data/                  # 小数据或下载脚本
    download_data.sh
  results/               # 用于验证的预期输出
```

**研究代码的 README 模板：**

```markdown
# [论文标题]

"[论文标题]"（会议名称 年份）的官方实现。

## 设置
[设置环境的确切命令]

## 复现
要复现表 1：`bash scripts/reproduce_table1.sh`
要复现图 2：`python scripts/make_figure2.py`

## 引用
[BibTeX 条目]
```

**预发布清单：**
```
- [ ] 代码可以从干净的克隆仓库运行（在新机器或 Docker 上测试）
- [ ] 所有依赖项都固定到特定版本
- [ ] 没有硬编码的绝对路径
- [ ] 仓库中没有 API 密钥、凭证或个人数据
- [ ] README 涵盖设置、复现和引用
- [ ] 包含 LICENSE 文件（为最大程度重用，推荐 MIT 或 Apache 2.0）
- [ ] 结果在预期方差内可复现
- [ ] .gitignore 排除了数据文件、检查点、日志
```

**用于提交的匿名代码**（接收前）：
```bash
# 为双盲评审使用 Anonymous GitHub
# https://anonymous.4open.science/
# 上传你的仓库 → 获取匿名 URL → 放入论文中
```

---

## 阶段 8：接收后的交付成果

**目标**：通过演示材料和社区参与，最大化你被接收论文的影响力。

### 步骤 8.1：会议海报

大多数会议都要求海报展示。海报设计原则：

| 元素 | 指导原则 |
|---------|-----------|
| **尺寸** | 检查会议场地要求（通常是 24"x36" 或 A0 纵向/横向） |
| **内容** | 标题、作者、一句话贡献、方法图、2-3 个关键结果、结论 |
| **布局** | 左上到右下（Z 型）或分栏式 |
| **文字** | 标题在 3 米外可读，正文在 1 米外可读。不要完整段落——只用要点。 |
| **图表** | 以更高分辨率重用论文图表。放大关键结果。 |

**工具**：LaTeX（`beamerposter` 包）、PowerPoint/Keynote、Figma、Canva。

**制作**：在会议前 2 周以上预订。织物海报更轻便，便于旅行。许多会议现在也支持虚拟/数字海报。

### 步骤 8.2：会议演讲 / 亮点报告

如果获得口头或亮点报告机会：

| 演讲类型 | 时长 | 内容 |
|-----------|----------|---------|
| **亮点报告** | 5 分钟 | 问题、方法、一个关键结果。排练到恰好 5 分钟。 |
| **口头报告** | 15-20 分钟 | 完整故事：问题、方法、关键结果、消融实验、局限性。 |
| **研讨会报告** | 10-15 分钟 | 根据研讨会听众调整——可能需要更多背景介绍。 |

**幻灯片设计规则：**
- 每张幻灯片一个核心观点
- 最小化文字——细节用说的，不要都投影出来
- 对关键图表使用动画，逐步构建理解
- 最后包含一张"要点"幻灯片（一句话贡献）
- 为预期的问题准备备用幻灯片

### 步骤 8.3：博客文章 / 社交媒体

一篇易于理解的总结能显著增加影响力：

- **Twitter/X 线程**：5-8 条推文。以结果开头，而不是方法。包含图 1 和关键结果图。
- **博客文章**：800-1500 词。为 ML 从业者撰写，而不是审稿人。跳过形式化描述，强调直觉和实际意义。
- **项目页面**：包含摘要、图表、演示、代码链接、BibTeX 的 HTML 页面。使用 GitHub Pages。

**时机**：在论文出现在会议论文集或 arXiv 最终稿后的 1-2 天内发布。

---

## 研讨会与短文

研讨会论文和短文（例如，ACL 短文、Findings 论文）遵循相同的流程，但有不同的限制和期望。

### 研讨会论文

| 属性 | 研讨会 | 主会议 |
|----------|----------|-----------------|
| **页数限制** | 4-6 页（通常） | 7-9 页 |
| **评审标准** | 对完整性的要求较低 | 必须完整、详尽 |
| **评审流程** | 通常是单盲或轻量级评审 | 双盲、严格 |
| **看重什么** | 有趣的想法、初步结果、立场性文章 | 具有强基线的完整实证故事 |
| **arXiv** | 随时发布 | 时机很重要（参见 arXiv 策略） |
| **贡献门槛** | 新颖的方向、有趣的负面结果、进行中的工作 | 具有强有力证据的显著进展 |

**何时以研讨会为目标：**
- 希望在完整论文之前获得反馈的早期想法
- 不足以支撑 8 页以上的负面结果
- 关于及时话题的立场性文章或观点
- 复制研究或可复现性报告

### ACL 短文与 Findings

ACL 会议有不同的投稿类型：
| 类型 | 页数 | 预期内容 |
|------|-------|-----------------|
| **长论文** | 8 | 完整的研究、强基线、消融实验 |
| **短论文** | 4 | 聚焦的贡献：一个明确的观点及其证据 |
| **研究结果** | 8 | 扎实的工作，仅以微弱差距未入选主会议 |

**短论文策略**：选择一个主张并充分支持它。不要试图将一篇长论文压缩到 4 页——写一篇不同的、更聚焦的论文。

---

## 经验性机器学习之外的论文类型

上述主要流程针对经验性机器学习论文。其他类型的论文需要不同的结构和证据标准。关于每种类型的详细指导，请参阅 [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。

### 理论论文

**结构**：引言 → 预备知识（定义、符号） → 主要结果（定理） → 证明概要 → 讨论 → 完整证明（附录）

**与经验性论文的主要区别**：
- 贡献是一个定理、界限或不可能性结果——而非实验数据
- “方法”部分被“预备知识”和“主要结果”取代
- 证明是证据，而非实验（尽管对理论进行经验验证是受欢迎的）
- 正文中包含证明概要、附录中包含完整证明是标准做法
- 实验部分是可选的，但如果能验证理论预测，则会增强论文的说服力

**证明写作原则**：
- 正式陈述定理，所有假设明确
- 在正式证明前提供直觉解释（“关键见解是...”）
- 证明概要应在 0.5-1 页内传达主要思想
- 使用 `\begin{proof}...\end{proof}` 环境
- 对假设进行编号并在定理中引用：“在假设 1-3 下，...”

### 综述 / 教程论文

**结构**：引言 → 分类 / 组织 → 详细覆盖 → 开放问题 → 结论

**主要区别**：
- 贡献在于组织、综合和识别开放问题——而非新方法
- 必须在范围内全面（审稿人会检查是否有遗漏的参考文献）
- 需要清晰的分类或组织框架
- 价值在于建立各工作之间的联系，这是单篇论文无法做到的
- 最佳投稿渠道：TMLR（综述方向）、JMLR、Foundations and Trends in ML、ACM Computing Surveys

### 基准测试论文

**结构**：引言 → 任务定义 → 数据集构建 → 基线评估 → 分析 → 预期用途与局限性

**主要区别**：
- 贡献是基准本身——它必须填补真正的评估空白
- 数据集文档是强制性的，而非可选的（参见 Datasheets，步骤 5.11）
- 必须证明基准具有挑战性（基线无法饱和其性能）
- 必须证明基准能测量你所声称的内容（结构效度）
- 最佳投稿渠道：NeurIPS 数据集与基准测试方向、ACL（资源论文）、LREC-COLING

### 观点论文

**结构**：引言 → 背景 → 论点 / 论证 → 支持证据 → 反驳论点 → 影响

**主要区别**：
- 贡献是一个论点，而非一个结果
- 必须认真对待反驳论点
- 证据可以是经验性的、理论性的或逻辑分析
- 最佳投稿渠道：ICML（观点方向）、研讨会、TMLR

---

## Hermes Agent 集成

此技能专为 Hermes Agent 设计。它利用 Hermes 的工具、委派、调度和记忆功能来完成整个研究生命周期。

### 相关技能

将此技能与其他 Hermes 技能结合使用，以应对特定阶段：

| 技能 | 使用时机 | 如何加载 |
|-------|-------------|-------------|
| **arxiv** | 阶段 1（文献综述）：搜索 arXiv、生成 BibTeX、通过 Semantic Scholar 查找相关论文 | `skill_view("arxiv")` |
| **subagent-driven-development** | 阶段 5（起草）：通过两阶段评审（规范符合性然后质量）进行并行章节撰写 | `skill_view("subagent-driven-development")` |
| **plan** | 阶段 0（设置）：在执行前创建结构化计划。写入 `.hermes/plans/` | `skill_view("plan")` |
| **qmd** | 阶段 1（文献）：通过混合 BM25+向量搜索搜索本地知识库（笔记、转录稿、文档） | 安装：`skill_manage("install", "qmd")` |
| **diagramming** | 阶段 4-5：创建基于 Excalidraw 的图表和架构图 | `skill_view("diagramming")` |
| **data-science** | 阶段 4（分析）：用于交互式分析和可视化的 Jupyter 实时内核 | `skill_view("data-science")` |

**此技能取代了 `ml-paper-writing`** —— 它包含了 ml-paper-writing 的所有内容，以及完整的实验/分析流程和自动推理方法。

### Hermes 工具参考

| 工具 | 在此流程中的用途 |
|------|----------------------|
| **`terminal`** | LaTeX 编译（`latexmk -pdf`）、git 操作、启动实验（`nohup python run.py &`）、进程检查 |
| **`process`** | 后台实验管理：`process("start", ...)`、`process("poll", pid)`、`process("log", pid)`、`process("kill", pid)` |
| **`execute_code`** | 运行 Python 进行引用验证、统计分析、数据聚合。通过 RPC 拥有工具访问权限。 |
| **`read_file`** / **`write_file`** / **`patch`** | 论文编辑、实验脚本、结果文件。使用 `patch` 对大型 .tex 文件进行针对性编辑。 |
| **`web_search`** | 文献发现：`web_search("transformer attention mechanism 2024")` |
| **`web_extract`** | 获取论文内容，验证引用：`web_extract("https://arxiv.org/abs/2303.17651")` |
| **`delegate_task`** | **并行章节起草** —— 为每个章节生成独立的子 Agent。也用于并发引用验证。 |
| **`todo`** | 跨会话的主要状态跟踪器。每次阶段转换后更新。 |
| **`memory`** | 跨会话持久化关键决策：贡献框架、投稿渠道选择、审稿人反馈。 |
| **`cronjob`** | 安排实验监控、截止日期倒计时、自动 arXiv 检查。 |
| **`clarify`** | 在遇到阻碍时向用户提出有针对性的问题（投稿渠道选择、贡献框架）。 |
| **`send_message`** | 在实验完成或草稿就绪时通知用户，即使用户不在聊天中。 |
### 工具使用模式

**实验监控**（最常见）：
```
terminal("ps aux | grep <pattern>")
→ terminal("tail -30 <logfile>")
→ terminal("ls results/")
→ execute_code("analyze results JSON, compute metrics")
→ terminal("git add -A && git commit -m '<descriptive message>' && git push")
→ send_message("Experiment complete: <summary>")
```

**并行章节草稿撰写**（使用委派）：
```
delegate_task("根据这些实验脚本和配置起草方法部分。
  包括：伪代码、所有超参数、足以复现的架构细节。
  使用 LaTeX 按照 neurips2025 模板规范撰写。")

delegate_task("起草相关工作部分。使用 web_search 和 web_extract 查找论文。
  通过 Semantic Scholar 验证每篇引用。按方法论分组。")

delegate_task("起草实验部分。读取 results/ 中的所有结果文件。
  说明每个实验支持哪个主张。包括误差条和显著性。")
```

每个委派任务都作为一个**全新的子 Agent** 运行，没有共享的上下文——请在提示词中提供所有必要信息。收集输出并进行整合。

**引用验证**（使用 execute_code）：
```python
# 在 execute_code 中：
from semanticscholar import SemanticScholar
import requests

sch = SemanticScholar()
results = sch.search_paper("attention mechanism transformers", limit=5)
for paper in results:
    doi = paper.externalIds.get('DOI', 'N/A')
    if doi != 'N/A':
        bibtex = requests.get(f"https://doi.org/{doi}", 
                              headers={"Accept": "application/x-bibtex"}).text
        print(bibtex)
```

### 使用 `memory` 和 `todo` 进行状态管理

**`memory` 工具** — 持久化关键决策（有界：MEMORY.md 约 2200 字符）：

```
memory("add", "论文：autoreason。会议：NeurIPS 2025（9页）。
  贡献：当生成-评估差距较大时，结构化精炼有效。
  关键结果：Haiku 42/42，Sonnet 3/5，S4.6 约束 2/3。
  状态：第 5 阶段 — 起草方法部分。")
```

在做出重大决策或阶段转换后更新记忆。这会在会话间持久化。

**`todo` 工具** — 跟踪细粒度进度：

```
todo("add", "为 Sonnet 4.6 设计约束任务实验")
todo("add", "运行 Haiku 基线比较")
todo("add", "起草方法部分")
todo("update", id=3, status="in_progress")
todo("update", id=1, status="completed")
```

**会话启动协议：**
```
1. todo("list")                           # 检查当前任务列表
2. memory("read")                         # 回忆关键决策
3. terminal("git log --oneline -10")      # 检查最近提交
4. terminal("ps aux | grep python")       # 检查正在运行的实验
5. terminal("ls results/ | tail -20")     # 检查新结果
6. 向用户报告状态，询问方向
```

### 使用 `cronjob` 进行定时任务监控

使用 `cronjob` 工具安排定期实验检查：

```
cronjob("create", {
  "schedule": "*/30 * * * *",  # 每 30 分钟
  "prompt": "检查实验状态：
    1. ps aux | grep run_experiment
    2. tail -30 logs/experiment_haiku.log
    3. ls results/haiku_baselines/
    4. 如果完成：读取结果，计算 Borda 分数，
       git add -A && git commit -m 'Add Haiku results' && git push
    5. 报告：结果表格、关键发现、下一步
    6. 如果无变化：用 [SILENT] 响应"
})
```

**[SILENT] 协议**：如果自上次检查以来没有任何变化，则用 `[SILENT]` 精确响应。这会抑制向用户发送通知。仅在有值得了解的真正变化时才报告。

**截止日期跟踪**：
```
cronjob("create", {
  "schedule": "0 9 * * *",  # 每天上午 9 点
  "prompt": "NeurIPS 2025 截止日期：5月22日。今天是 {date}。
    剩余天数：{compute}。
    检查 todo 列表 — 我们是否按计划进行？
    如果 <7 天：警告用户剩余任务。"
})
```

### 通信模式

**何时通知用户**（通过 `send_message` 或直接响应）：
- 实验批次完成（附结果表格）
- 需要决策的意外发现或失败
- 草稿章节可供审阅
- 截止日期临近且任务未完成

**何时不通知：**
- 实验仍在运行，无新结果 → `[SILENT]`
- 例行监控无变化 → `[SILENT]`
- 不需要关注的中间步骤

**报告格式** — 始终包含结构化数据：
```
## 实验：<名称>
状态：完成 / 运行中 / 失败

| 任务 | 方法 A | 方法 B | 方法 C |
|------|---------|---------|---------|
| 任务 1 | 85.2 | 82.1 | **89.4** |

关键发现：<一句话>
下一步：<接下来做什么>
```

### 需要人工输入的决策点

当真正受阻时，使用 `clarify` 提出有针对性的问题：

| 决策 | 何时询问 |
|----------|-------------|
| 目标会议 | 开始撰写论文之前（影响页数限制、框架） |
| 贡献框架 | 存在多个有效框架时 |
| 实验优先级 | 当 TODO 列表中的实验数量超过时间允许时 |
| 提交准备情况 | 最终提交之前 |

**不要询问**（积极主动，做出选择，标记出来）：
- 措辞选择、章节顺序
- 具体突出哪些结果
- 引用完整性（用找到的内容起草，注明差距）

---

## 审稿人评估标准

了解审稿人关注什么有助于集中精力：

| 标准 | 他们检查什么 |
|-----------|----------------|
| **质量** | 技术正确性、有充分支持的论点、公平的基线 |
| **清晰度** | 清晰的写作、专家可复现、一致的符号 |
| **重要性** | 对社区的影响、增进理解 |
| **原创性** | 新的见解（不需要新方法） |

**评分（NeurIPS 6 分制）：**
- 6: 强烈接受 — 开创性、无懈可击
- 5: 接受 — 技术扎实、高影响力
- 4: 临界接受 — 扎实、评估有限
- 3: 临界拒绝 — 弱点超过优点
- 2: 拒绝 — 技术缺陷
- 1: 强烈拒绝 — 已知结果或伦理问题
请参阅 [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) 了解详细的指南、常见问题以及反驳策略。

---

## 常见问题与解决方案

| 问题 | 解决方案 |
|-------|----------|
| 摘要过于笼统 | 如果第一句话可以放在任何机器学习论文的开头，请删除它。从你的具体贡献开始。 |
| 引言超过 1.5 页 | 将背景部分拆分到相关工作部分。将贡献要点前置。 |
| 实验缺乏明确的声明 | 在每个实验前添加："本实验旨在验证 [具体声明]..."。 |
| 审稿人认为论文难以理解 | 添加路标，使用一致的术语，使图注自成一体。 |
| 缺乏统计显著性 | 添加误差线、运行次数、统计检验、置信区间。 |
| 实验范围蔓延 | 每个实验都必须对应一个具体的声明。删除无关的实验。 |
| 论文被拒，需要重新提交 | 参见第 7 阶段的会议重投。在不提及审稿意见的情况下解决审稿人的关切。 |
| 缺少更广泛影响声明 | 参见步骤 5.10。大多数会议都要求此声明。"没有负面影响"几乎不可信。 |
| 人工评估被批评为薄弱 | 参见步骤 2.5 和 [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)。报告一致性指标、标注者详情、报酬。 |
| 审稿人质疑可复现性 | 发布代码（步骤 7.9），记录所有超参数，包含随机种子和计算细节。 |
| 理论论文缺乏直观解释 | 在正式证明之前，添加带有通俗语言解释的证明概要。参见 [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。 |
| 结果为阴性/无效 | 参见第 4.3 阶段关于处理阴性结果的部分。考虑研讨会、TMLR 或重新定义为分析性论文。 |

---

## 参考文档

| 文档 | 内容 |
|----------|----------|
| [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) | Gopen & Swan 7 原则，Perez 微技巧，Lipton 选词，Steinhardt 精确性，图表设计 |
| [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md) | 引用 API，Python 代码，CitationManager 类，BibTeX 管理 |
| [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) | NeurIPS 16 项清单，ICML，ICLR，ACL 要求，通用提交前清单 |
| [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) | 评估标准，评分，常见问题，反驳模板 |
| [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) | 所有写作指南、会议指南、API 的完整参考文献 |
| [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md) | 实验设计模式，评估协议，监控，错误恢复 |
| [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md) | 自动推理循环，策略选择，模型指南，提示词，范围约束，Borda 评分 |
| [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md) | 人工评估设计，标注指南，一致性指标，众包质量控制，IRB 指导 |
| [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md) | 理论论文（证明写作，定理结构），综述论文，基准论文，立场论文 |

### LaTeX 模板

`templates/` 目录中的模板适用于：**NeurIPS 2025**，**ICML 2026**，**ICLR 2026**，**ACL**，**AAAI 2026**，**COLM 2025**。

编译说明请参见 [templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md)。

### 关键外部资源

**写作理念：**
- [Neel Nanda: 如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar: 如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen & Swan: 科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton: 科技写作启发法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez: 简易论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/)

**API：** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**会议：** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)