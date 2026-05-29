---
title: "看板视频编排器 — 基于 Hermes 看板规划、设置和监控多 Agent 视频制作流水线"
sidebar_label: "看板视频编排器"
description: "基于 Hermes 看板规划、设置和监控多 Agent 视频制作流水线"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 看板视频编排器

基于 Hermes 看板规划、设置和监控多 Agent 视频制作流水线。当用户想要制作**任何**视频时使用——叙事电影、产品/营销视频、音乐视频、解说视频、ASCII/终端艺术、抽象/生成循环、漫画、3D、实时/装置艺术——并且该工作值得分解为由看板协调的专门角色（编剧、设计师、动画师、渲染师、配音、剪辑等）。执行适应性探索以确定需求范围，根据请求的风格设计合适的团队，生成创建 Hermes 角色和初始看板任务的设置脚本，然后帮助监控执行并在任务停滞或失败时进行干预。将场景路由到适合每个节拍的 Hermes 渲染/音频/设计技能（`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`pixel-art`、`baoyu-comic`、`claude-design`、`excalidraw`、`songsee`、`heartmula`……），并根据需要调用外部 API 进行 TTS、图像生成和图像转视频。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/kanban-video-orchestrator` 安装 |
| 路径 | `optional-skills/creative/kanban-video-orchestrator` |
| 版本 | `1.0.0` |
| 作者 | ['SHL0MS', 'alt-glitch'] |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `video`, `kanban`, `multi-agent`, `orchestration`, `production-pipeline` |
| 相关技能 | [`kanban-orchestrator`](/docs/user-guide/skills/bundled/devops/devops-kanban-orchestrator), [`kanban-worker`](/docs/user-guide/skills/bundled/devops/devops-kanban-worker), [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js), [`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui), [`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp), [`blender-mcp`](/docs/user-guide/skills/optional/creative/creative-blender-mcp), [`pixel-art`](/docs/user-guide/skills/bundled/creative/creative-pixel-art), [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art), [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music), [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula), [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee), [`spotify`](/docs/user-guide/skills/bundled/media/media-spotify), [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram), [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams), [`baoyu-comic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-comic), [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic), [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer), [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search), [`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 看板视频编排器

将任何视频请求——从 15 秒的产品预告片到 5 分钟的叙事短片，再到音乐视频或 ASCII 循环——包装在一个 Hermes 看板流水线中，该流水线将工作分解给专门的 Agent 角色。

此技能**本身不**渲染任何内容。它是一个元流水线，负责：

1.  **探索**：通过有针对性的探索确定需求范围
2.  **设计**：根据风格设计合适的团队（哪些角色，每个角色使用哪些工具）
3.  **生成**：生成一个设置脚本，用于创建 Hermes 角色、项目工作空间和初始看板任务
4.  **移交**：移交给导演角色，后者通过看板进行分解
5.  **监控**：监控执行，在任务停滞或失败时帮助干预

实际的渲染发生在看板运行后，通过适合场景的任何现有技能和工具进行——`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`songwriting-and-ai-music`、`heartmula`、外部 API，或使用 PIL + ffmpeg 的纯 Python。

## 何时不应使用此技能

*   视频是一个连续的、无需专家的程序化项目。直接编写代码即可。
*   用户想要快速的一次性转换（例如“将此 mp4 转换为 GIF”）——直接使用 ffmpeg。
*   输出是静态图像、GIF 或纯音频文件——使用匹配的特定技能（`ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）。
*   工作完全适合单个现有技能（例如纯 ASCII 视频——直接使用 `ascii-video`）。

## 工作流

```
探索 → 需求简报 → 团队设计 → 设置 → 执行 → 监控
```

### 步骤 1 — 探索（提出正确的问题）

探索过程是**适应性的**：只询问实际需要的内容。始终从三个问题开始，以确定大致轮廓：

*   **视频内容是什么？**（一句话简介）
*   **时长多久？**（5-30 秒预告片 / 30-90 秒短片 / 90 秒-3 分钟解说 / 3-10 分钟影片 / 更长）
*   **宽高比和目标平台是什么？**（1:1 / 9:16 / 16:9；X、IG、YouTube、内部等）
根据回答，对风格类别进行分类。风格决定了后续要问哪些问题。**不要一次性问完所有问题。** 每次问 2-4 个问题，听取回答，然后继续。每当用户暗示答案时，做出合理的假设。

完整的需求收集模式和每种风格的问题库，请参见 **[references/intake.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/intake.md)**。

### 步骤 2 — 简报

一旦了解足够信息，使用 `assets/brief.md.tmpl` 中的模板生成结构化的 `brief.md`。阶段：

1.  **概念** — 一句话简介 + 情感北极星
2.  **范围** — 时长、画幅比、平台、截止日期
3.  **风格** — 视觉参考、品牌约束、基调
4.  **场景** — 逐节分解（时长、内容、目标工具）
5.  **音频** — 旁白 / 音乐 / 音效 / 静音（按场景需要）
6.  **交付物** — 文件格式、分辨率、可选替代版本（竖版剪辑、GIF 等）

在设计团队之前，向用户展示简报以确认。**简报即合同** — 所有下游任务都以此为依据。

### 步骤 3 — 团队设计

从库中挑选适合此视频的角色原型。**组合，而非克隆。** 大多数视频需要 4-7 个角色。导演始终在场；其余角色根据简报的实际需求挑选。

角色库和每种风格的团队构成，请参见 **[references/role-archetypes.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/role-archetypes.md)**。

关于角色 → 加载哪些 Hermes 技能 + 工具集的映射，请参见 **[references/tool-matrix.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/tool-matrix.md)**。

### 步骤 4 — 设置

生成一个设置脚本 (`setup.sh`) 并运行它。该脚本：

1.  创建项目工作空间 (`~/projects/video-pipeline/<slug>/`)
2.  将任何提供的素材复制到 `taste/`、`audio/`、`assets/`
3.  通过 `hermes profile create --clone` 创建每个 Hermes 角色
4.  编写每个角色的 `SOUL.md`（人格 + 角色定义）
5.  配置角色 YAML（工具集、always_load 技能、cwd）
6.  编写 `brief.md`、`TEAM.md` 和 `taste/` 内容
7.  触发分配给导演的初始 `hermes kanban create` 任务

使用 `scripts/bootstrap_pipeline.py` 根据简报 + 团队设计 JSON 生成 setup.sh。关于设置脚本结构、角色配置模式和关键的"共享工作空间"规则，请参见 **[references/kanban-setup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/kanban-setup.md)**。

### 步骤 5 — 执行

运行 `setup.sh`。然后向用户提供监控命令：

```bash
hermes kanban watch --tenant <project-tenant>     # 实时事件
hermes kanban list  --tenant <project-tenant>     # 看板快照
hermes dashboard                                   # 可视化看板 UI
```

导演角色将从此处接手，分解工作并通过看板工具集将任务路由给专家角色。

### 步骤 6 — 监控与干预

保持参与 — 看板自主运行，但遇到卡住的任务或不良输出时，需要人类（或 AI）的判断。

监控模式：定期轮询 `kanban list`，使用 `kanban show <id>` 检查任何超过预期时长的 RUNNING 任务，并检查心跳。当工作者的输出未通过审查时，标准的干预措施是：

1.  在工作者任务上评论并提供具体反馈 (`kanban_comment`)
2.  创建一个以原始任务为父任务的重运行任务
3.  调整简报范围，让导演重新分解

关于诊断模式、干预方案和"任务卡住"应对手册，请参见 **[references/monitoring.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/monitoring.md)**。

## 参考：工作示例

六个涵盖截然不同视频风格的具体流水线 — 叙事电影、产品/营销、音乐视频、数学/算法讲解、ASCII 视频、实时装置 — 展示了相同的工作流如何产生截然不同的团队和任务图。请参见 **[references/examples.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/examples.md)**。

## 关键规则

1.  **先探索，后行动。** 在没有至少询问三个基线问题之前，切勿开始生成简报或团队。糟糕的简报会波及整个流水线。
2.  **团队与视频匹配。** 不要为每个工作重用相同的 4 角色设置。没有节拍分析角色的音乐视频会出错。没有编剧角色的叙事电影会产生不连贯的场景。参见 `references/role-archetypes.md`。
3.  **每个项目一个工作空间。** 给定视频的所有角色共享相同的 `dir:` 工作空间。任务通过共享文件系统和结构化交接传递工件。**每个** `kanban_create` 调用都传递 `workspace_kind="dir"` + `workspace_path="<绝对项目路径>"`。
4.  **每个项目使用租户。** 使用项目特定的租户 (`--tenant <project-slug>`)。保持仪表板范围限定，并防止与其他正在进行的看板交叉影响。
5.  **尊重现有技能。** 当场景适合现有技能时，相关的渲染器应通过其任务上的 `--skill <name>` 或其角色中的 `always_load` 加载该技能。不要重新推导技能已提供的内容。
6.  **导演从不执行。** 即使拥有完整的 `kanban + terminal + file` 工具集，导演的 `SOUL.md` 规则也禁止其自行执行工作。它只负责分解和路由 — 每个具体任务都成为对专家角色的 `hermes kanban create` 调用。`kanban-orchestrator` 技能进一步阐明了这一点。
7.  **不要过度分解。** 一个 30 秒的产品视频**不需要** 20 个任务。目标是实现最小的任务图，同时仍能良好并行化并暴露适当的人工审查节点。
8. **在启动前验证 API 密钥。** 外部 API（TTS、图像生成、图像转视频）需要在 `~/.hermes/.env` 或用户的密钥存储中配置密钥。一个因缺少密钥而报错的 Worker 会浪费一个任务槽。如果缺少必需的密钥，设置脚本中的 `check_key` 辅助函数会干净地中止执行。

## 文件结构

```
SKILL.md                            ← 本文件（工作流 + 规则）
references/
  intake.md                         ← 按风格划分的发现性问题库
  role-archetypes.md                ← 角色库（作家、设计师、动画师等）
  tool-matrix.md                    ← 按角色划分的技能 + 工具集映射
  kanban-setup.md                   ← 设置脚本结构及配置文件
  monitoring.md                     ← 监控 + 干预模式
  examples.md                       ← 六个已实现的工作流示例
assets/
  brief.md.tmpl                     ← 简报骨架模板
  setup.sh.tmpl                     ← 设置脚本骨架模板
  soul.md.tmpl                      ← 配置文件人格骨架模板
scripts/
  bootstrap_pipeline.py             ← 根据简报和团队 JSON 生成 setup.sh
  monitor.py                        ← 轮询 + 干预辅助函数
```