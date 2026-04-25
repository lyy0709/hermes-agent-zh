---
title: "Openclaw 迁移 — 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent"
sidebar_label: "Openclaw 迁移"
description: "将用户的 OpenClaw 自定义配置迁移到 Hermes Agent"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Openclaw 迁移

将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。从 `~/.openclaw` 导入与 Hermes 兼容的记忆、SOUL.md、命令允许列表、用户技能以及选定的工作区资源，然后准确报告无法迁移的内容及其原因。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/migration/openclaw-migration` 安装 |
| 路径 | `optional-skills/migration/openclaw-migration` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent (Nous Research) |
| 许可证 | MIT |
| 标签 | `Migration`, `OpenClaw`, `Hermes`, `Memory`, `Persona`, `Import` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# OpenClaw -> Hermes 迁移

当用户希望以最少的手动清理工作将其 OpenClaw 设置迁移到 Hermes Agent 时，请使用此技能。

## CLI 命令

要进行快速、非交互式的迁移，请使用内置的 CLI 命令：

```bash
hermes claw migrate              # 完整的交互式迁移
hermes claw migrate --dry-run    # 预览将要迁移的内容
hermes claw migrate --preset user-data   # 迁移但不包含密钥
hermes claw migrate --overwrite  # 覆盖现有冲突项
hermes claw migrate --source /custom/path/.openclaw  # 自定义源路径
```

CLI 命令运行的是下文描述的同一个迁移脚本。当您希望通过 Agent 进行交互式、引导式迁移，并包含试运行预览和逐项冲突解决时，请使用此技能（通过 Agent）。

**首次设置：** `hermes setup` 向导会自动检测 `~/.openclaw`，并在配置开始前提供迁移选项。

## 此技能的功能

它使用 `scripts/openclaw_to_hermes.py` 来：

- 将 `SOUL.md` 导入到 Hermes 主目录作为 `SOUL.md`
- 将 OpenClaw 的 `MEMORY.md` 和 `USER.md` 转换为 Hermes 记忆条目
- 将 OpenClaw 命令批准模式合并到 Hermes 的 `command_allowlist`
- 迁移与 Hermes 兼容的消息设置，例如 `TELEGRAM_ALLOWED_USERS` 和 `MESSAGING_CWD`
- 将 OpenClaw 技能复制到 `~/.hermes/skills/openclaw-imports/`
- 可选地将 OpenClaw 工作区说明文件复制到选定的 Hermes 工作区
- 将兼容的工作区资源（如 `workspace/tts/`）镜像到 `~/.hermes/tts/`
- 归档没有直接 Hermes 对应目标的非机密文档
- 生成一份结构化报告，列出已迁移项、冲突项、跳过项及其原因

## 路径解析

辅助脚本位于此技能目录中：

- `scripts/openclaw_to_hermes.py`

当此技能从技能中心安装时，通常位于：

- `~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`

请勿猜测更短的路径，如 `~/.hermes/skills/openclaw-migration/...`。

运行辅助脚本前：

1. 优先使用 `~/.hermes/skills/migration/openclaw-migration/` 下的安装路径。
2. 如果该路径失败，请检查已安装的技能目录，并根据已安装的 `SKILL.md` 解析脚本的相对路径。
3. 仅当安装位置缺失或技能被手动移动时，才将 `find` 作为备用方案。
4. 调用终端工具时，不要传递 `workdir: "~"`。请使用绝对目录（如用户的主目录），或完全省略 `workdir`。

使用 `--migrate-secrets` 时，它还会导入一小部分与 Hermes 兼容的、允许的密钥，目前包括：

- `TELEGRAM_BOT_TOKEN`

## 默认工作流

1. 首先使用试运行进行检查。
2. 呈现一个简单的摘要，说明可以迁移什么、无法迁移什么以及什么将被归档。
3. 如果 `clarify` 工具可用，请使用它来获取用户决策，而不是请求自由格式的文本回复。
4. 如果试运行发现导入的技能目录存在冲突，请在执行前询问如何处理这些冲突。
5. 在执行前，请用户在两个支持的迁移模式之间进行选择。
6. 仅当用户希望迁移工作区说明文件时，才询问目标工作区路径。
7. 使用匹配的预设和标志执行迁移。
8. 总结结果，特别是：
   - 已迁移的内容
   - 已归档以供手动审查的内容
   - 已跳过内容及其原因

## 用户交互协议

Hermes CLI 支持使用 `clarify` 工具进行交互式提示，但它仅限于：

- 一次一个选择
- 最多 4 个预定义选项
- 一个自动的 `Other` 自由文本选项

它**不**支持在单个提示中使用真正的多选复选框。

对于每次 `clarify` 调用：

- 始终包含一个非空的 `question`
- 仅在实际可选择的提示中包含 `choices`
- 将 `choices` 限制在 2-4 个纯字符串选项
- 切勿发出占位符或截断的选项，如 `...`
- 切勿使用额外的空白字符填充或样式化选项
- 切勿在问题中包含虚假的表单字段，例如 `在此输入目录`、需要填写的空行或下划线 `_____`
- 对于开放式路径问题，只询问简单的句子；用户在面板下方的普通 CLI 提示符中输入

如果 `clarify` 调用返回错误，请检查错误文本，更正有效负载，并使用有效的 `question` 和干净的选项重试一次。

当 `clarify` 可用且试运行显示需要用户决策时，您的**下一个操作必须是调用 `clarify` 工具**。
不要以普通的助手消息结束回合，例如：

- "让我展示一下选项"
- "您想做什么？"
- "以下是选项"

如果需要用户决策，请在生成更多文本之前通过 `clarify` 收集决策。
如果仍有多个未解决的决策，请不要在它们之间插入解释性的助手消息。在收到一个 `clarify` 响应后，您的下一个操作通常应该是下一个必需的 `clarify` 调用。
当试运行报告出现以下情况时，将 `workspace-agents` 视为未解决的决策：

- `kind="workspace-agents"`
- `status="skipped"`
- 原因包含 `No workspace target was provided`

在这种情况下，你必须在执行前询问工作区指令。不要默默地将其视为跳过决策。

由于此限制，请使用以下简化的决策流程：

1.  对于 `SOUL.md` 冲突，使用 `clarify`，并提供如下选择：
    - `keep existing`
    - `overwrite with backup`
    - `review first`
2.  如果试运行显示一个或多个 `kind="skill"` 项且 `status="conflict"`，使用 `clarify`，并提供如下选择：
    - `keep existing skills`
    - `overwrite conflicting skills with backup`
    - `import conflicting skills under renamed folders`
3.  对于工作区指令，使用 `clarify`，并提供如下选择：
    - `skip workspace instructions`
    - `copy to a workspace path`
    - `decide later`
4.  如果用户选择复制工作区指令，则提出一个后续的开放式 `clarify` 问题，要求提供一个**绝对路径**。
5.  如果用户选择 `skip workspace instructions` 或 `decide later`，则继续执行而不使用 `--workspace-target`。
6.  对于迁移模式，使用 `clarify`，并提供以下 3 个选择：
    - `user-data only`
    - `full compatible migration`
    - `cancel`
7.  `user-data only` 意味着：迁移用户数据和兼容的配置，但**不**导入允许列表中的密钥。
8.  `full compatible migration` 意味着：迁移相同的兼容用户数据，并在存在时导入允许列表中的密钥。
9.  如果 `clarify` 不可用，则以普通文本形式询问相同的问题，但仍将答案限制为 `user-data only`、`full compatible migration` 或 `cancel`。

执行门控：

-   当由 `No workspace target was provided` 引起的 `workspace-agents` 跳过仍未解决时，不要执行。
-   解决此问题的唯一有效方法是：
    -   用户明确选择 `skip workspace instructions`
    -   用户明确选择 `decide later`
    -   用户在选择 `copy to a workspace path` 后提供了工作区路径
-   试运行中缺少工作区目标本身并不构成执行许可。
-   当任何必需的 `clarify` 决策仍未解决时，不要执行。

使用以下确切的 `clarify` 载荷结构作为默认模式：

-   `{"question":"您现有的 SOUL.md 与导入的文件冲突。我应该怎么做？","choices":["keep existing","overwrite with backup","review first"]}`
-   `{"question":"一个或多个导入的 OpenClaw 技能已存在于 Hermes 中。我应该如何处理这些技能冲突？","choices":["keep existing skills","overwrite conflicting skills with backup","import conflicting skills under renamed folders"]}`
-   `{"question":"选择迁移模式：仅迁移用户数据，还是运行包括允许列表密钥在内的完整兼容迁移？","choices":["user-data only","full compatible migration","cancel"]}`
-   `{"question":"您是否希望将 OpenClaw 工作区指令文件复制到 Hermes 工作区？","choices":["skip workspace instructions","copy to a workspace path","decide later"]}`
-   `{"question":"请提供工作区指令应复制到的绝对路径。"}`

## 决策到命令的映射

将用户决策精确映射到命令标志：

-   如果用户为 `SOUL.md` 选择 `keep existing`，则**不**添加 `--overwrite`。
-   如果用户选择 `overwrite with backup`，则添加 `--overwrite`。
-   如果用户选择 `review first`，则在执行前停止并审查相关文件。
-   如果用户选择 `keep existing skills`，则添加 `--skill-conflict skip`。
-   如果用户选择 `overwrite conflicting skills with backup`，则添加 `--skill-conflict overwrite`。
-   如果用户选择 `import conflicting skills under renamed folders`，则添加 `--skill-conflict rename`。
-   如果用户选择 `user-data only`，则使用 `--preset user-data` 执行，并且**不**添加 `--migrate-secrets`。
-   如果用户选择 `full compatible migration`，则使用 `--preset full --migrate-secrets` 执行。
-   仅当用户明确提供了绝对工作区路径时，才添加 `--workspace-target`。
-   如果用户选择 `skip workspace instructions` 或 `decide later`，则不添加 `--workspace-target`。

在执行之前，用通俗语言重述确切的命令计划，并确保其与用户的选择一致。

## 运行后报告规则

执行后，将脚本的 JSON 输出视为事实来源。

1.  所有计数均基于 `report.summary`。
2.  仅当项目的 `status` 恰好为 `migrated` 时，才将其列在"成功迁移"下。
3.  除非报告显示该项目为 `migrated`，否则不要声称冲突已解决。
4.  除非 `kind="soul"` 的报告项的 `status="migrated"`，否则不要说 `SOUL.md` 被覆盖。
5.  如果 `report.summary.conflict > 0`，则包含一个冲突部分，而不是默默地暗示成功。
6.  如果计数和列出的项目不一致，请在响应前修复列表以匹配报告。
7.  当报告中有 `output_dir` 路径时，请包含该路径，以便用户可以检查 `report.json`、`summary.md`、备份和归档文件。
8.  对于记忆或用户配置文件溢出，除非报告明确显示归档路径，否则不要说条目已归档。如果存在 `details.overflow_file`，则说明完整的溢出列表已导出到该处。
9.  如果技能被导入到重命名的文件夹下，请报告最终目的地并提及 `details.renamed_from`。
10. 如果存在 `report.skill_conflict_mode`，则将其用作所选导入技能冲突策略的事实来源。
11. 如果某个项目的 `status="skipped"`，则不要将其描述为已覆盖、已备份、已迁移或已解决。
12. 如果 `kind="soul"` 的 `status="skipped"` 且原因为 `Target already matches source`，则说明其保持不变，并且不要提及备份。
13. 如果重命名的导入技能具有空的 `details.backup`，则不要暗示现有的 Hermes 技能已被重命名或备份。只需说明导入的副本已放置在新目的地，并引用 `details.renamed_from` 作为保留在原处的预先存在的文件夹。
## 迁移预设

在正常使用中，优先使用以下两个预设：

- `user-data`
- `full`

`user-data` 包含：

- `soul`
- `workspace-agents`
- `memory`
- `user-profile`
- `messaging-settings`
- `command-allowlist`
- `skills`
- `tts-assets`
- `archive`

`full` 包含 `user-data` 中的所有内容，外加：

- `secret-settings`

辅助脚本仍然支持类别级别的 `--include` / `--exclude`，但请将其视为高级备用方案，而非默认用户体验。

## 命令

执行完整发现的试运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

使用终端工具时，优先使用绝对路径调用模式，例如：

```json
{"command":"python3 /home/USER/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py","workdir":"/home/USER"}
```

使用 user-data 预设进行试运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --preset user-data
```

执行 user-data 迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict skip
```

执行完整兼容迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip
```

执行迁移并包含工作区指令：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```

默认情况下，不要使用 `$PWD` 或主目录作为工作区目标。首先请求明确的工作区路径。

## 重要规则

1.  除非用户明确表示立即进行，否则在写入前先运行试运行。
2.  默认情况下不迁移密钥。Token、身份验证数据块、设备凭证和原始消息网关配置应保留在 Hermes 之外，除非用户明确要求迁移密钥。
3.  除非用户明确希望如此，否则不要静默覆盖非空的 Hermes 目标。辅助脚本在启用覆盖时会保留备份。
4.  始终向用户提供已跳过项目的报告。该报告是迁移的一部分，不是可选的额外内容。
5.  优先使用主要的 OpenClaw 工作区 (`~/.openclaw/workspace/`)，而不是 `workspace.default/`。仅当主要文件缺失时，才使用默认工作区作为备用。
6.  即使在密钥迁移模式下，也只迁移具有干净 Hermes 目标的密钥。不受支持的身份验证数据块仍必须报告为已跳过。
7.  如果试运行显示有大量资产复制、冲突的 `SOUL.md` 或溢出的记忆条目，请在执行前单独指出这些情况。
8.  如果用户不确定，默认使用 `仅 user-data`。
9.  仅当用户明确提供了目标工作区路径时，才包含 `workspace-agents`。
10. 将类别级别的 `--include` / `--exclude` 视为高级逃生舱口，而非正常流程。
11. 如果 `clarify` 可用，不要在试运行摘要的结尾使用模糊的“您想做什么？”。使用结构化的后续提示。
12. 当可以使用真实的选择提示时，不要使用开放式的 `clarify` 提示。优先使用可选择的选项，然后仅在请求绝对路径或文件审查时才使用自由文本。
13. 试运行后，如果仍有未解决的决策，不要在总结后就停止。立即使用 `clarify` 处理最高优先级的阻塞决策。
14. 后续问题的优先级顺序：
    - `SOUL.md` 冲突
    - 导入的技能冲突
    - 迁移模式
    - 工作区指令目标
15. 不要承诺在同一消息中稍后呈现选项。通过实际调用 `clarify` 来呈现它们。
16. 在回答迁移模式问题后，明确检查 `workspace-agents` 是否仍未解决。如果是，你的下一个操作必须是工作区指令的 `clarify` 调用。
17. 在任何 `clarify` 回答之后，如果仍有其他必需的决策，不要叙述刚刚决定的内容。立即询问下一个必需的问题。

## 预期结果

成功运行后，用户应拥有：

- 导入的 Hermes 人格状态
- 用转换后的 OpenClaw 知识填充的 Hermes 记忆文件
- 在 `~/.hermes/skills/openclaw-imports/` 下可用的 OpenClaw 技能
- 一份显示任何冲突、遗漏或不受支持数据的迁移报告