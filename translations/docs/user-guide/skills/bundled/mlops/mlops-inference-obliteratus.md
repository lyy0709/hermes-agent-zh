---
title: "Obliteratus — OBLITERATUS：消除 LLM 拒绝行为（均值差分法）"
sidebar_label: "Obliteratus"
description: "OBLITERATUS：消除 LLM 拒绝行为（均值差分法）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Obliteratus

OBLITERATUS：消除 LLM 拒绝行为（均值差分法）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/obliteratus` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 依赖项 | `obliteratus`, `torch`, `transformers`, `bitsandbytes`, `accelerate`, `safetensors` |
| 标签 | `Abliteration`, `Uncensoring`, `Refusal-Removal`, `LLM`, `Weight-Projection`, `SVD`, `Mechanistic-Interpretability`, `HuggingFace`, `Model-Surgery` |
| 相关技能 | `vllm`, `gguf`, [`huggingface-tokenizers`](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# OBLITERATUS 技能

## 包含内容

9 个 CLI 方法，28 个分析模块，涵盖 5 个计算层级的 116 个模型预设，锦标赛评估，以及遥测驱动的推荐。

无需重新训练或微调，即可从开源权重的 LLM 中移除拒绝行为（安全护栏）。使用机制可解释性技术——包括均值差分法、SVD、白化 SVD、LEACE 概念擦除、SAE 分解、贝叶斯核投影等——来识别并手术式地从模型权重中切除拒绝方向，同时保留推理能力。

**许可证警告：** OBLITERATUS 采用 AGPL-3.0 许可证。切勿将其作为 Python 库导入。始终通过 CLI（`obliteratus` 命令）或子进程调用。这可以保持 Hermes Agent 的 MIT 许可证的纯净性。

## 视频指南

Hermes Agent 使用 OBLITERATUS 消除 Gemma 安全护栏的流程演示：
https://www.youtube.com/watch?v=8fG9BrNTeHs ("OBLITERATUS: An AI Agent Removed Gemma 4's Safety Guardrails")

当用户希望在自行运行前获得端到端工作流的视觉概览时很有用。

## 何时使用此技能

当用户出现以下情况时触发：
- 想要对 LLM 进行“去审查”或“消除”
- 询问如何从模型中移除拒绝/安全护栏
- 想要创建 Llama、Qwen、Mistral 等的去审查版本
- 提及“拒绝移除”、“消除”、“权重投影”
- 想要分析模型的拒绝机制如何工作
- 提及 OBLITERATUS、消除器或拒绝方向

## 步骤 1：安装

检查是否已安装：
```bash
obliteratus --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

如果未安装，从 GitHub 克隆并安装：
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
pip install -e .
# 如需 Gradio web UI 支持：
# pip install -e ".[spaces]"
```

**重要提示：** 安装前需与用户确认。这会拉取约 5-10GB 的依赖项（PyTorch、Transformers、bitsandbytes 等）。

## 步骤 2：检查硬件

在进行任何操作之前，检查可用的 GPU：
```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('TIER: tiny (models under 1B)')
    elif vram < 8: print('TIER: small (models 1-4B)')
    elif vram < 16: print('TIER: medium (models 4-9B with 4bit quant)')
    elif vram < 32: print('TIER: large (models 8-32B with 4bit quant)')
    else: print('TIER: frontier (models 32B+)')
else:
    print('NO GPU - only tiny models (under 1B) on CPU')
"
```

### VRAM 要求（使用 4 位量化）

| VRAM     | 最大模型尺寸  | 示例模型                              |
|:---------|:----------------|:--------------------------------------------|
| 仅 CPU | ~10 亿参数      | GPT-2, TinyLlama, SmolLM                    |
| 4-8 GB   | ~40 亿参数      | Qwen2.5-1.5B, Phi-3.5 mini, Llama 3.2 3B   |
| 8-16 GB  | ~90 亿参数      | Llama 3.1 8B, Mistral 7B, Gemma 2 9B       |
| 24 GB    | ~320 亿参数     | Qwen3-32B, Llama 3.1 70B (tight), Command-R |
| 48 GB+   | ~720 亿+ 参数    | Qwen2.5-72B, DeepSeek-R1                    |
| 多 GPU| 2000 亿+ 参数    | Llama 3.1 405B, DeepSeek-V3 (685B MoE)      |

## 步骤 3：浏览可用模型并获取推荐

```bash
# 按计算层级浏览模型
obliteratus models --tier medium

# 获取特定模型的架构信息
obliteratus info <model_name>

# 获取遥测驱动的最佳方法和参数推荐
obliteratus recommend <model_name>
obliteratus recommend <model_name> --insights  # 全局跨架构排名
```

## 步骤 4：选择方法

### 方法选择指南
**默认/大多数情况推荐：`advanced`。** 它使用多方向 SVD 并保持范数投影，经过充分测试。

| 情况                         | 推荐方法 | 原因                                      |
|:----------------------------------|:-------------------|:-----------------------------------------|
| 默认 / 大多数模型             | `advanced`         | 多方向 SVD，保持范数，可靠 |
| 快速测试 / 原型设计          | `basic`            | 快速，简单，足以进行评估    |
| 密集模型 (Llama, Mistral)      | `advanced`         | 多方向，保持范数         |
| MoE 模型 (DeepSeek, Mixtral)     | `nuclear`          | 专家粒度，处理 MoE 复杂性  |
| 推理模型 (R1 蒸馏)     | `surgical`         | 感知 CoT，保留思维链    |
| 顽固拒绝持续存在         | `aggressive`       | 白化 SVD + 头部手术 + 越狱   |
| 希望可逆更改           | 使用转向向量（参见分析部分） |
| 追求最高质量，时间不限   | `optimized`        | 贝叶斯搜索最佳参数      |
| 实验性自动检测       | `informed`         | 自动检测对齐类型——实验性，可能不总是优于 advanced |
### 9 种 CLI 方法
- **basic** — 通过均值差异进行单拒绝方向消除。速度快（8B 模型约 5-10 分钟）。
- **advanced** （默认，推荐）— 多 SVD 方向、保范投影、2 次精炼。中等速度（约 10-20 分钟）。
- **aggressive** — 白化 SVD + 越狱对比 + 注意力头手术。连贯性受损风险更高。
- **spectral_cascade** — DCT 频域分解。研究/新颖方法。
- **informed** — 在消除过程中运行分析以自动配置。实验性 — 比 advanced 方法更慢且更不可预测。
- **surgical** — SAE 特征 + 神经元掩码 + 头手术 + 逐专家处理。非常慢（约 1-2 小时）。最适合推理模型。
- **optimized** — 贝叶斯超参数搜索（Optuna TPE）。运行时间最长，但能找到最优参数。
- **inverted** — 翻转拒绝方向。模型变得主动愿意。
- **nuclear** — 针对顽固 MoE 模型的最大力度组合。专家粒度。

### 方向提取方法（--direction-method 标志）
- **diff_means** （默认）— 拒绝/遵从激活之间的简单均值差异。稳健。
- **svd** — 多方向 SVD 提取。更适合复杂对齐。
- **leace** — LEACE（通过闭式估计进行线性擦除）。最优线性擦除。

### 4 种仅限 Python API 的方法
（不通过 CLI 提供 — 需要 Python 导入，这违反了 AGPL 边界。仅在用户明确希望在自己的 AGPL 项目中将 OBLITERATUS 作为库使用时提及。）
- failspy, gabliteration, heretic, rdo

## 步骤 5：运行消除

### 标准用法
```bash
# 默认方法（advanced）— 推荐用于大多数模型
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models

# 使用 4 位量化（节省 VRAM）
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models

# 大型模型（70B+）— 保守默认值
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

### 微调参数
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # 选择加入社区研究的遥测数据
```

### 关键标志
| 标志 | 描述 | 默认值 |
|:-----|:------------|:--------|
| `--method` | 消除方法 | advanced |
| `--direction-method` | 方向提取方法 | diff_means |
| `--n-directions` | 拒绝方向数量（1-32） | 取决于方法 |
| `--refinement-passes` | 迭代精炼次数（1-5） | 2 |
| `--regularization` | 正则化强度（0.0-1.0） | 0.1 |
| `--quantization` | 以 4 位或 8 位加载 | 无（全精度） |
| `--large-model` | 针对 120B+ 模型的保守默认值 | false |
| `--output-dir` | 保存消除后模型的位置 | ./obliterated_model |
| `--contribute` | 为研究共享匿名化结果 | false |
| `--verify-sample-size` | 用于拒绝检查的测试提示词数量 | 20 |
| `--dtype` | 模型数据类型（float16, bfloat16） | auto |

### 其他执行模式
```bash
# 交互式引导模式（硬件 → 模型 → 预设）
obliteratus interactive

# Web UI（Gradio）
obliteratus ui --port 7860

# 从 YAML 配置运行完整消融研究
obliteratus run config.yaml --preset quick

# 锦标赛：所有方法相互比拼
obliteratus tourney <model_name>
```

## 步骤 6：验证结果

消除后，检查输出指标：

| 指标 | 良好值 | 警告 |
|:-------|:-----------|:--------|
| 拒绝率 | &lt; 5%（理想情况 ~0%） | > 10% 表示拒绝持续存在 |
| 困惑度变化 | &lt; 10% 增加 | > 15% 表示连贯性受损 |
| KL 散度 | &lt; 0.1 | > 0.5 表示分布显著偏移 |
| 连贯性 | 高 / 通过定性检查 | 响应质量下降、重复 |

### 如果拒绝持续存在（> 10%）
1. 尝试 `aggressive` 方法
2. 增加 `--n-directions`（例如 8 或 16）
3. 添加 `--refinement-passes 3`
4. 尝试 `--direction-method svd` 而不是 diff_means

### 如果连贯性受损（困惑度增加 > 15%）
1. 减少 `--n-directions`（尝试 2）
2. 增加 `--regularization`（尝试 0.3）
3. 将 `--refinement-passes` 减少到 1
4. 尝试 `basic` 方法（更温和）

## 步骤 7：使用消除后的模型

输出是一个标准的 HuggingFace 模型目录。

```bash
# 使用 transformers 本地测试
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('How do I pick a lock?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# 上传到 HuggingFace Hub
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# 使用 vLLM 提供服务
vllm serve ./abliterated-models/<model>
```

## CLI 命令参考

| 命令 | 描述 |
|:--------|:------------|
| `obliteratus obliterate` | 主消除命令 |
| `obliteratus info <model>` | 打印模型架构详情 |
| `obliteratus models --tier <tier>` | 按计算层级浏览精选模型 |
| `obliteratus recommend <model>` | 基于遥测的方法/参数建议 |
| `obliteratus interactive` | 引导式设置向导 |
| `obliteratus tourney <model>` | 锦标赛：所有方法正面交锋 |
| `obliteratus run <config.yaml>` | 从 YAML 执行消融研究 |
| `obliteratus strategies` | 列出所有已注册的消除策略 |
| `obliteratus report <results.json>` | 重新生成可视化报告 |
| `obliteratus ui` | 启动 Gradio Web 界面 |
| `obliteratus aggregate` | 汇总社区遥测数据 |

## 分析模块

OBLITERATUS 包含 28 个用于机械可解释性的分析模块。
完整参考请参见 `skill_view(name="obliteratus", file_path="references/analysis-modules.md")`。
### 快速分析命令
```bash
# 运行特定分析模块
obliteratus run analysis-config.yaml --preset quick

# 首先运行的关键模块：
# - alignment_imprint: 指纹 DPO/RLHF/CAI/SFT 对齐方法
# - concept_geometry: 单方向 vs 多面体锥
# - logit_lens: 哪一层决定拒绝
# - anti_ouroboros: 自修复风险评分
# - causal_tracing: 因果必要的组件
```

### 转向向量（可逆替代方案）
作为永久权重修改的替代，使用推理时转向：
```python
# 仅限 Python API — 用于用户自己的项目
from obliteratus.analysis.steering_vectors import SteeringVectorFactory, SteeringHookManager
```

## 消融策略

除了基于方向的消融，OBLITERATUS 还包括结构性消融策略：
- **嵌入消融** — 目标嵌入层组件
- **FFN 消融** — 前馈网络块移除
- **注意力头剪枝** — 注意力头剪枝
- **层移除** — 完整层移除

列出所有可用策略：`obliteratus strategies`

## 评估

OBLITERATUS 包含内置评估工具：
- 拒绝率基准测试
- 困惑度比较（消融前/后）
- 集成 LM Eval Harness 用于学术基准测试
- 与竞争对手的正面比较
- 基线性能跟踪

## 平台支持

- **CUDA** — 完全支持（NVIDIA GPU）
- **Apple Silicon (MLX)** — 通过 MLX 后端支持
- **CPU** — 支持小模型（&lt; 10 亿参数）

## YAML 配置模板

通过 `skill_view` 加载模板以实现可复现的运行：
- `templates/abliteration-config.yaml` — 标准单模型配置
- `templates/analysis-study.yaml` — 消融前分析研究
- `templates/batch-abliteration.yaml` — 多模型批量处理

## 遥测

OBLITERATUS 可以选择性地将匿名运行数据贡献给全球研究数据集。
使用 `--contribute` 标志启用。不收集个人数据 — 仅收集模型名称、方法、指标。

## 常见陷阱

1. **不要默认使用 `informed`** — 它是实验性的且速度较慢。使用 `advanced` 以获得可靠结果。
2. **约 10 亿参数以下的模型对消融反应不佳** — 它们的拒绝行为是浅层且碎片化的，使得提取清晰的方向变得困难。预期部分结果（20-40% 的拒绝率残留）。30 亿参数以上的模型具有更清晰的拒绝方向，反应要好得多（使用 `advanced` 通常能达到 0% 拒绝率）。
3. **`aggressive` 可能使情况更糟** — 在小模型上，它可能损害连贯性并实际上增加拒绝率。仅当 `advanced` 在 30 亿参数以上的模型上留下 > 10% 的拒绝率时才使用它。
4. **始终检查困惑度** — 如果它激增 > 15%，则模型已受损。降低激进程度。
5. **MoE 模型需要特殊处理** — 对 Mixtral、DeepSeek-MoE 等模型使用 `nuclear` 方法。
6. **量化模型无法重新量化** — 消融全精度模型，然后量化输出。
7. **VRAM 估计是近似的** — 4 位量化有帮助，但在提取过程中峰值使用量可能激增。
8. **推理模型很敏感** — 对 R1 蒸馏模型使用 `surgical` 以保留思维链。
9. **检查 `obliteratus recommend`** — 遥测数据可能提供比默认值更好的参数。
10. **AGPL 许可证** — 切勿在 MIT/Apache 项目中 `import obliteratus`。仅限 CLI 调用。
11. **大模型（700 亿参数以上）** — 始终使用 `--large-model` 标志以获得保守的默认值。
12. **光谱认证 RED 很常见** — 光谱检查经常标记为“不完整”，即使实际拒绝率为 0%。检查实际拒绝率，而不是仅仅依赖光谱认证。

## 互补技能

- **vllm** — 以高吞吐量服务消融后的模型
- **gguf** — 将消融后的模型转换为 GGUF 格式以供 llama.cpp 使用
- **huggingface-tokenizers** — 处理模型分词器