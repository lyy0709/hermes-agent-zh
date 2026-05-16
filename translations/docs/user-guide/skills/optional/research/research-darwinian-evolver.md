---
title: "达尔文进化器 — 使用 Imbue 的进化循环进化提示词/正则表达式/SQL/代码"
sidebar_label: "达尔文进化器"
description: "使用 Imbue 的进化循环进化提示词/正则表达式/SQL/代码"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 达尔文进化器

使用 Imbue 的进化循环进化提示词/正则表达式/SQL/代码。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/darwinian-evolver` 安装 |
| 路径 | `optional-skills/research/darwinian-evolver` |
| 版本 | `0.1.0` |
| 作者 | Bihruze (Asahi0x), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `evolution`, `optimization`, `prompt-engineering`, `research` |
| 相关技能 | [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv), [`jupyter-live-kernel`](/docs/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 达尔文进化器

运行 Imbue 的 [darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) — 一个由 LLM 驱动的进化搜索循环 — 以根据适应度函数优化**提示词、正则表达式、SQL 查询或小型代码片段**。

状态：上游工具的薄包装。该技能会安装它，引导 Agent 编写 `Problem` 定义（organism + evaluator + mutator），并通过上游 CLI 或一个小的自定义 Python 驱动程序来驱动循环。

**许可证：** 上游工具是 **AGPL-3.0**。该技能**仅**通过上游 CLI 或 `subprocess`/`uv run` 调用（仅为聚合）来调用它。**请勿**将上游类导入到 Hermes 本身中。

## 何时使用

- 用户说“优化这个提示词”、“为 X 进化一个正则表达式”、“自动改进这段代码/SQL”、“搜索更好的指令”。
- 你有一个评分器（精确匹配、正则表达式通过率、单元测试、LLM 评判、运行时指标）**并且**有一个起始候选（organism）。如果你没有评分器，请先停下来定义一个 — 这是困难的部分。
- 成本可以接受：一次典型运行需要 50–500 次 LLM 调用。对于 gpt-4o-mini 来说只需几美分；对于 Claude Sonnet 可能几美元。

在以下情况下**不要**使用此技能：
- 优化目标是可微分的（使用梯度下降 / DSPy）。
- 你只需要尝试 2–3 个变体 — 手动编写即可。
- 适应度信号纯粹是主观的，没有可衡量的标准。

## 先决条件

- Python ≥3.11
- `git`, `uv` (或 `pip`)
- 以下之一：`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, 或 `OPENAI_API_KEY`

该技能附带一个小的 `parrot_openrouter.py` 驱动程序，它通过 OpenAI SDK 使用 `OPENROUTER_API_KEY`，因此 OpenRouter 上的任何模型都有效。上游 CLI 本身硬编码了 Anthropic 并需要 `ANTHROPIC_API_KEY`。

## 安装（一次性）

通过 `terminal` 工具运行：

```bash
mkdir -p ~/.hermes/cache/darwinian-evolver && cd ~/.hermes/cache/darwinian-evolver
[ -d darwinian_evolver ] || git clone --depth 1 https://github.com/imbue-ai/darwinian_evolver.git
cd darwinian_evolver && uv sync
```

验证：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver \
  && uv run darwinian_evolver --help | head -5
```

## 快速开始 — 内置的 Parrot 示例

小型冒烟测试（需要 `ANTHROPIC_API_KEY`）：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver
uv run darwinian_evolver parrot \
  --num_iterations 2 \
  --num_parents_per_iteration 2 \
  --mutator_concurrency 2 --evaluator_concurrency 2 \
  --output_dir /tmp/parrot_demo
```

输出：
- `/tmp/parrot_demo/snapshots/iteration_N.pkl` — 每次迭代的序列化种群
- `/tmp/parrot_demo/<jsonl>` — 每次迭代的 JSON 日志（路径在最后打印）

在浏览器中打开 `~/.hermes/cache/darwinian-evolver/darwinian_evolver/darwinian_evolver/lineage_visualizer.html` 并加载 JSON 日志以查看进化树。

## 快速开始 — OpenRouter 驱动程序（无需 Anthropic 密钥）

该技能附带 `scripts/parrot_openrouter.py` — 相同的 parrot 问题，但 LLM 调用通过 OpenRouter 进行，因此任何提供商都有效。

```bash
# 从技能安装的位置：
SKILL_DIR=~/.hermes/skills/research/darwinian-evolver
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver

cd "$DE_DIR" && \
  EVOLVER_MODEL='openai/gpt-4o-mini' \
  uv run --with openai python "$SKILL_DIR/scripts/parrot_openrouter.py" \
    --num_iterations 3 --num_parents_per_iteration 2 \
    --output_dir /tmp/parrot_or
```

使用 `scripts/show_snapshot.py` 检查结果：

```bash
uv run --with openai python "$SKILL_DIR/scripts/show_snapshot.py" \
  /tmp/parrot_or/snapshots/iteration_3.pkl
```

预期输出：7 个进化后的提示词模板按分数排序，最佳分数大约在 0.6–0.8 之间（种子 `Say {{ phrase }}` 得分为 0.000）。

## 定义自定义问题

该技能附带 `templates/custom_problem_template.py` — 复制、编辑、运行。
你必须定义三件事：

1.  **`Organism`** — 一个 Pydantic `BaseModel` 子类，持有正在进化的工件（`prompt_template: str`, `regex_pattern: str`, `sql_query: str`, `code_block: str` 等）。添加一个 `run(*args)` 方法来执行它。

2.  **`Evaluator`** — `.evaluate(organism) -> EvaluationResult(score=..., trainable_failure_cases=[...], holdout_failure_cases=[...], is_viable=True)`。
    - **`score`** 在 `[0, 1]` 范围内。越高越好。
    - **`trainable_failure_cases`** — mutator 看到的内容。包含足够的上下文（输入、预期、实际）供 LLM 诊断。
    - **`holdout_failure_cases`** — 对 mutator 隐藏。使用这些来检测过拟合。
    - **`is_viable=True`** — 除非 organism 完全损坏（抛出异常、返回 None 等）。得分为 0 的可行 organism 没问题 — 它只是在父代选择中被降权。

3.  **`Mutator`** — `.mutate(organism, failure_cases, learning_log_entries) -> list[Organism]`。
    通常：构建一个 LLM 提示词，包含当前 organism + 一个失败案例 + 要求提出修复方案；解析 LLM 的响应；返回一个新的 `Organism`。解析失败时返回 `[]` — 循环会处理它。

然后编写一个驱动程序脚本，将 `Problem(initial_organism, evaluator, [mutators])` 连接到 `EvolveProblemLoop` 并迭代 `loop.run(num_iterations=N)` — 附带的 `scripts/parrot_openrouter.py` 是参考。

## 真正重要的超参数

| 标志 | 默认值 | 何时更改 |
|---|---|---|
| `--num_iterations` | 5 | 一旦信任 evaluator，增加到 10–20 |
| `--num_parents_per_iteration` | 4 | 为了廉价探索，降至 2 |
| `--mutator_concurrency` | 10 | 为避免速率限制，降至 2–4 |
| `--evaluator_concurrency` | 10 | 同上；evaluator 也会调用 LLM |
| `--batch_size` | 1 | 一旦你的 mutator 能处理多个失败，提高到 3–5 |
| `--verify_mutations` | 关闭 | 一旦 mutator 浪费严重（根据 Imbue，后期运行可节省 >10 倍成本）时开启 |
| `--midpoint_score` | `p75` | 除非分数聚集，否则保持不动 |
| `--sharpness` | 10 | 保持不动 |

## 陷阱

1.  **`初始 organism 必须是可行的`** — 即使在 0 分种子上，也要在你的 `EvaluationResult` 中设置 `is_viable=True`。循环拒绝不可行的 organism，因为它们意味着循环没有进化起点。
2.  **提供商的内容过滤器会终止运行。** Azure 支持的 OpenRouter 模型会拒绝类似“忽略先前指令”的短语，并返回 HTTP 400。将 LLM 调用包装在 `try/except` 中并返回 `f"<LLM_ERROR: {e}>"` — 进化器只会给该 organism 打 0 分并继续。
3.  **`loop.run()` 是一个生成器** — 调用它直到你迭代才会运行任何东西。使用 `for snap in loop.run(num_iterations=N):`。
4.  **快照是嵌套的 pickle。** `iteration_N.pkl` 包含一个带有 `population_snapshot`（更多 pickle 字节）的字典。要反序列化，你必须拥有 `Organism` 类，并且其导入的点路径与序列化时相同。
5.  **并发默认值很激进。** 10/10 会在大多数提供商处触发速率限制。从 2/2 开始。
6.  **CLI 硬编码为 Anthropic。** `uv run darwinian_evolver <problem>` 会寻找 `ANTHROPIC_API_KEY` 并使用 Claude Sonnet。要使用任何其他提供商，请编写像 `parrot_openrouter.py` 这样的驱动程序。
7.  **AGPL。** 切勿在 Hermes 核心中 `from darwinian_evolver import ...`。`~/.hermes/skills/...` 下的自定义驱动程序脚本是用户侧的，没问题。
8.  **没有 PyPI 包。** `pip install darwinian-evolver` 会拉取错误的东西。始终从 GitHub 仓库安装。

## 验证

安装 + 运行 parrot 示例后，以下命令退出码为 0 即表示成功：

```bash
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver
ls "$DE_DIR/darwinian_evolver/lineage_visualizer.html" >/dev/null && \
cd "$DE_DIR" && uv run darwinian_evolver --help >/dev/null && \
echo "darwinian-evolver: OK"
```

## 参考资料

- [Imbue 研究文章](https://imbue.com/research/2026-02-27-darwinian-evolver/)
- [ARC-AGI-2 结果](https://imbue.com/research/2026-02-27-arc-agi-2-evolution/)
- [imbue-ai/darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) (AGPL-3.0)
- [Darwin Gödel Machines](https://arxiv.org/abs/2505.22954)
- [PromptBreeder](https://arxiv.org/abs/2309.16797)