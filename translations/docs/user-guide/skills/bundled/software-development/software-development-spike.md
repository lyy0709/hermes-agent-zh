---
title: "Spike — 构建前用于验证想法的临时实验"
sidebar_label: "Spike"
description: "构建前用于验证想法的临时实验"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Spike

构建前用于验证想法的临时实验。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/spike` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `spike`, `prototype`, `experiment`, `feasibility`, `throwaway`, `exploration`, `research`, `planning`, `mvp`, `proof-of-concept` |
| 相关技能 | [`sketch`](/docs/user-guide/skills/bundled/creative/creative-sketch), [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Spike

当用户希望在投入实际构建之前**试探一个想法**时使用此技能——用于验证可行性、比较不同方法，或揭示任何研究都无法回答的未知问题。Spike 在设计上就是一次性的。一旦它们完成了使命，就将其丢弃。

当用户说类似“让我试试这个”、“我想看看 X 是否可行”、“把这个 spike 出来”、“在我投入 Y 之前”、“Z 的快速原型”、“这甚至可能吗？”或“比较 A 和 B”时，加载此技能。

## 何时不应使用此技能

- 答案可以通过文档或阅读代码获知——只需进行研究，无需构建
- 工作是生产路径的一部分——改用 `writing-plans` / `plan`
- 想法已经过验证——直接开始实施

## 如果用户安装了完整的 GSD 系统

如果 `gsd-spike` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），当用户想要完整的 GSD 工作流时，**优先使用 `gsd-spike`**：持久的 `.planning/spikes/` 状态、跨会话的 MANIFEST 跟踪、Given/When/Then 裁决格式，以及与 GSD 其余部分集成的提交模式。此技能是轻量级独立版本，适用于没有（或不想要）完整系统的用户。

## 核心方法

无论规模大小，每个 spike 都遵循以下循环：

```
分解 → 研究 → 构建 → 裁决
   ↑__________________________________________↓
                 基于发现进行迭代
```

### 1. 分解

将用户的想法分解为 **2-5 个独立的可行性问题**。每个问题就是一个 spike。使用 Given/When/Then 框架将它们呈现为一个表格：

| # | Spike | 验证内容 (Given/When/Then) | 风险 |
|---|-------|----------------------------|------|
| 001 | websocket-streaming | Given a WS connection, when LLM streams tokens, then client receives chunks &lt; 100ms | 高 |
| 002a | pdf-parse-pdfjs | Given a multi-page PDF, when parsed with pdfjs, then structured text is extractable | 中 |
| 002b | pdf-parse-camelot | Given a multi-page PDF, when parsed with camelot, then structured text is extractable | 中 |

**Spike 类型：**
- **标准** —— 一种方法回答一个问题
- **比较** —— 相同问题，不同方法（共享编号，字母后缀 `a`/`b`/`c`）

**好的 spike 问题：** 具体的可行性，具有可观察的输出。
**坏的 spike 问题：** 过于宽泛，没有可观察的输出，或者只是“阅读关于 X 的文档”。

**按风险排序。** 最有可能扼杀该想法的 spike 首先运行。如果困难部分无法工作，就没有必要对简单部分进行原型设计。

**跳过分解**，仅当用户已经确切知道他们想要 spike 什么并明确说明时。然后将他们的想法视为单个 spike。

### 2. 对齐（针对多 spike 想法）

呈现 spike 表格。询问：“按此顺序全部构建，还是调整？” 在编写任何代码之前，让用户删除、重新排序或重新构建。

### 3. 研究（每个 spike，在构建之前）

Spike 并非无需研究——你需要研究足够的信息来选择正确的方法，然后进行构建。针对每个 spike：

1.  **简要说明。** 2-3 句话：这个 spike 是什么，为什么重要，关键风险。
2.  **如果存在真正的选择，列出竞争方法：**

   | 方法 | 工具/库 | 优点 | 缺点 | 状态 |
   |----------|-------------|------|------|--------|
   | ... | ... | ... | ... | maintained / abandoned / beta |

3.  **选择一个。** 说明原因。如果有 2 种以上方法可信，在 spike 内构建快速变体。
4.  **对于没有外部依赖的纯逻辑，跳过研究。**

在研究步骤中使用 Hermes 工具：

- `web_search("python websocket streaming libraries 2025")` —— 寻找候选方案
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` —— 阅读实际文档（返回 markdown）
- `terminal("pip show websockets | grep Version")` —— 检查项目虚拟环境中安装的内容

对于没有文档页面的库，通过 `read_file` 克隆并阅读其 `README.md` / `examples/`。Context7 MCP（如果用户已配置）也是一个很好的来源——使用 `mcp_*_resolve-library-id` 然后 `mcp_*_query-docs`。

### 4. 构建

每个 spike 一个目录。保持其独立性。

<!-- ascii-guard-ignore -->
```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```
<!-- ascii-guard-ignore-end -->

**倾向于构建用户可以交互的东西。** 当唯一输出是显示“它工作”的日志行时，Spike 就失败了。用户希望*感受* spike 在工作。默认选择，按偏好顺序：

1.  一个可运行的 CLI，接收输入并打印可观察的输出
2.  一个演示该行为的最小化 HTML 页面
3.  一个具有单个端点的小型 Web 服务器
4.  一个使用可识别断言来验证问题的单元测试

**深度优于速度。** 永远不要在运行一次成功路径后就宣布“它工作”。测试边缘情况。追踪令人惊讶的发现。只有当调查是诚实的，裁决才是可信的。

**避免**，除非 spike 特别需要：复杂的包管理、构建工具/打包器、Docker、环境文件、配置系统。硬编码所有内容——这是一个 spike。

**构建一个 spike** —— 典型的工具序列：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# 观察输出，迭代。
```

**并行比较 spike (002a / 002b) —— 委派。** 当两种方法可以并行运行并且都需要真正的工程（不是 10 行的原型）时，使用 `delegate_task` 进行分发：

```
delegate_task(tasks=[
    {"goal": "Build 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "Build 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子 Agent 返回自己的裁决；你来撰写对比分析。

### 5. 裁决

每个 spike 的 `README.md` 以以下内容结尾：

```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
- ...

### What didn't
- ...

### Surprises
- ...

### Recommendation for the real build
- ...
```

**VALIDATED** = 核心问题得到肯定回答，并有证据。
**PARTIAL** = 在约束条件 X, Y, Z 下工作——记录它们。
**INVALIDATED** = 不工作，原因如下。这是一个成功的 spike。

## 比较 Spike

当两种方法回答同一个问题时 (002a / 002b)，**连续构建**它们，然后在最后进行对比分析：

```markdown
## Head-to-head: pdfjs vs camelot

| Dimension | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| Extraction quality | 9/10 structured | 7/10 table-only |
| Setup complexity | npm install, 1 line | pip + ghostscript |
| Perf on 100-page PDF | 3s | 18s |
| Handles rotated text | no | yes |

**Winner:** pdfjs for our use case. Camelot if we need table-first extraction later.
```

## 前沿模式（选择下一个要 spike 的内容）

如果 spike 已经存在，并且用户说“我接下来应该 spike 什么？”，请遍历现有目录并寻找：

-   **集成风险** —— 两个已验证的 spike 接触相同的资源，但独立测试
-   **数据传递** —— 假设 spike A 的输出与 spike B 的输入兼容；但从未证明
-   **愿景中的空白** —— 假设但未证明的能力
-   **替代方法** —— 针对 PARTIAL 或 INVALIDATED spike 的不同角度

提出 2-4 个候选方案作为 Given/When/Then。让用户选择。

## 输出

-   在仓库根目录创建 `spikes/`（如果用户使用 GSD 约定，则为 `.planning/spikes/`）
-   每个 spike 一个目录：`NNN-descriptive-name/`
-   每个 spike 的 `README.md` 记录问题、方法、结果、裁决
-   保持代码的一次性——一个需要 2 天来“清理以用于生产”的 spike 是一个糟糕的 spike

## 归属

改编自 GSD (Get Shit Done) 项目的 `/gsd-spike` 工作流 —— MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统提供持久的 spike 状态、MANIFEST 跟踪以及与更广泛的规范驱动开发流水线的集成；使用 `npx get-shit-done-cc --hermes --global` 安装。