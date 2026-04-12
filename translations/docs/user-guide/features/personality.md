---
sidebar_position: 9
title: "人格与 SOUL.md"
description: "通过全局 SOUL.md、内置人格和自定义角色定义来定制 Hermes Agent 的人格"
---

# 人格与 SOUL.md

Hermes Agent 的人格是完全可定制的。`SOUL.md` 是**主要身份**——它是系统提示词中的第一项，定义了 Agent 是谁。

- `SOUL.md` —— 一个持久的角色文件，位于 `HERMES_HOME` 中，作为 Agent 的身份（系统提示词中的插槽 #1）
- 内置或自定义的 `/personality` 预设 —— 会话级别的系统提示词覆盖层

如果你想改变 Hermes 是谁——或者用一个完全不同的 Agent 角色替换它——请编辑 `SOUL.md`。

## SOUL.md 现在如何工作

Hermes 现在会自动在以下位置生成一个默认的 `SOUL.md`：

```text
~/.hermes/SOUL.md
```

更准确地说，它使用当前实例的 `HERMES_HOME`，因此如果你使用自定义的主目录运行 Hermes，它将使用：

```text
$HERMES_HOME/SOUL.md
```

### 重要行为

- **SOUL.md 是 Agent 的主要身份。** 它占据系统提示词中的插槽 #1，替换了硬编码的默认身份。
- 如果 `SOUL.md` 尚不存在，Hermes 会自动创建一个初始版本
- 现有的用户 `SOUL.md` 文件永远不会被覆盖
- Hermes 只从 `HERMES_HOME` 加载 `SOUL.md`
- Hermes 不会在当前工作目录中查找 `SOUL.md`
- 如果 `SOUL.md` 存在但为空，或无法加载，Hermes 将回退到内置的默认身份
- 如果 `SOUL.md` 有内容，该内容在安全扫描和截断后会逐字注入
- SOUL.md **不会**在上下文文件部分重复出现——它只出现一次，作为身份

这使得 `SOUL.md` 成为真正的每用户或每实例身份，而不仅仅是一个附加层。

## 为什么采用这种设计

这使人格保持可预测性。

如果 Hermes 从你碰巧启动它的任何目录加载 `SOUL.md`，你的人格可能会在不同项目之间意外改变。通过只从 `HERMES_HOME` 加载，人格属于 Hermes 实例本身。

这也使得教育用户更容易：
- "编辑 `~/.hermes/SOUL.md` 来改变 Hermes 的默认人格。"

## 在哪里编辑它

对于大多数用户：

```bash
~/.hermes/SOUL.md
```

如果你使用自定义主目录：

```bash
$HERMES_HOME/SOUL.md
```

## SOUL.md 中应该放什么？

用它来提供持久的语气和人格指导，例如：
- 语调
- 沟通风格
- 直接程度
- 默认交互风格
- 风格上要避免什么
- Hermes 应如何处理不确定性、分歧或模糊性

少用它来放：
- 一次性项目指令
- 文件路径
- 仓库惯例
- 临时工作流细节

这些属于 `AGENTS.md`，而不是 `SOUL.md`。

## 好的 SOUL.md 内容

一个好的 SOUL 文件是：
- 在不同上下文中保持稳定
- 足够宽泛，适用于许多对话
- 足够具体，能实质性地塑造声音
- 专注于沟通和身份，而不是特定任务的指令

### 示例

```markdown
# 人格

你是一位务实的资深工程师，品味很高。
你优先考虑真相、清晰度和实用性，而不是礼貌的表演。

## 风格
- 直接但不冷漠
- 偏爱实质内容而非填充物
- 当某个想法不好时，要提出反对意见
- 坦率承认不确定性
- 除非深度有用，否则保持解释简洁

## 要避免什么
- 谄媚
- 炒作语言
- 如果用户的框架是错误的，不要重复它
- 过度解释显而易见的事情

## 技术姿态
- 偏爱简单系统而非巧妙系统
- 关心操作现实，而非理想化的架构
- 将边缘情况视为设计的一部分，而不是清理工作
```

## Hermes 向提示词中注入什么

`SOUL.md` 的内容直接进入系统提示词的插槽 #1——Agent 身份位置。其周围不会添加任何包装语言。

内容会经过：
- 提示词注入扫描
- 如果太大，则进行截断

如果文件为空、仅包含空白字符或无法读取，Hermes 将回退到内置的默认身份（"你是 Hermes Agent，一个由 Nous Research 创建的智能 AI 助手……"）。当设置了 `skip_context_files` 时（例如，在子代理/委派上下文中），也会应用此回退。

## 安全扫描

在包含之前，`SOUL.md` 会像其他承载上下文的文件一样，接受提示词注入模式的扫描。

这意味着你仍应将其重点放在角色/声音上，而不是试图偷偷加入奇怪的元指令。

## SOUL.md 与 AGENTS.md

这是最重要的区别。

### SOUL.md
用于：
- 身份
- 语调
- 风格
- 沟通默认值
- 人格层面的行为

### AGENTS.md
用于：
- 项目架构
- 编码惯例
- 工具偏好
- 仓库特定的工作流
- 命令、端口、路径、部署说明

一个有用的规则：
- 如果它应该跟随你到任何地方，它属于 `SOUL.md`
- 如果它属于一个项目，它属于 `AGENTS.md`

## SOUL.md 与 `/personality`

`SOUL.md` 是你持久的默认人格。

`/personality` 是一个会话级别的覆盖层，用于更改或补充当前的系统提示词。

所以：
- `SOUL.md` = 基线声音
- `/personality` = 临时模式切换

示例：
- 保持一个务实的默认 SOUL，然后在辅导对话中使用 `/personality teacher`
- 保持一个简洁的 SOUL，然后在头脑风暴中使用 `/personality creative`

## 内置人格

Hermes 附带了一些内置人格，你可以使用 `/personality` 切换到它们。

| 名称 | 描述 |
|------|-------------|
| **helpful** | 友好、通用的助手 |
| **concise** | 简短、切中要点的回答 |
| **technical** | 详细、准确的技术专家 |
| **creative** | 创新、跳出框框的思维 |
| **teacher** | 耐心的教育者，提供清晰的例子 |
| **kawaii** | 可爱的表达、星星和热情 ★ |
| **catgirl** | 猫娘，带有猫一样的表达，nya~ |
| **pirate** | Hermes 船长，精通技术的海盗 |
| **shakespeare** | 带有戏剧色彩的诗人散文 |
| **surfer** | 完全放松的兄弟氛围 |
| **noir** | 硬汉侦探的叙述 |
| **uwu** | 极致的可爱，带有 uwu 语 |
| **philosopher** | 对每个查询都进行深度思考 |
| **hype** | 最大能量和热情！！！ |

## 使用命令切换人格

### CLI

```text
/personality
/personality concise
/personality technical
```

### 消息平台

```text
/personality teacher
```

这些是方便的覆盖层，但你的全局 `SOUL.md` 仍然为 Hermes 提供其持久的默认人格，除非覆盖层有意义地改变了它。

## 在配置中自定义人格

你也可以在 `~/.hermes/config.yaml` 中的 `agent.personalities` 下定义命名的自定义人格。

```yaml
agent:
  personalities:
    codereviewer: >
      你是一位细致的代码审查员。识别错误、安全问题、
      性能问题和不清楚的设计选择。要精确且有建设性。
```

然后使用以下命令切换到它：

```text
/personality codereviewer
```

## 推荐的工作流

一个强大的默认设置是：

1. 在 `~/.hermes/SOUL.md` 中保留一个经过深思熟虑的全局 `SOUL.md`
2. 将项目指令放在 `AGENTS.md` 中
3. 仅当你想要临时模式切换时才使用 `/personality`

这为你提供了：
- 稳定的声音
- 项目特定的行为放在合适的位置
- 需要时的临时控制

## 人格如何与完整提示词交互

从高层次看，提示词堆栈包括：
1. **SOUL.md**（Agent 身份——如果 SOUL.md 不可用，则使用内置回退）
2. 工具感知行为指导
3. 记忆/用户上下文
4. 技能指导
5. 上下文文件（`AGENTS.md`、`.cursorrules`）
6. 时间戳
7. 平台特定的格式化提示
8. 可选的系统提示词覆盖层，例如 `/personality`

`SOUL.md` 是基础——其他一切都建立在它之上。

## 相关文档

- [上下文文件](/docs/user-guide/features/context-files)
- [配置](/docs/user-guide/configuration)
- [技巧与最佳实践](/docs/guides/tips)
- [SOUL.md 指南](/docs/guides/use-soul-with-hermes)

## CLI 外观与会话人格

会话人格和 CLI 外观是分开的：

- `SOUL.md`、`agent.system_prompt` 和 `/personality` 影响 Hermes 的说话方式
- `display.skin` 和 `/skin` 影响 Hermes 在终端中的外观

关于终端外观，请参阅[皮肤与主题](./skins.md)。