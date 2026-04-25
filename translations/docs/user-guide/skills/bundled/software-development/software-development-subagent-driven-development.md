---
title: "子 Agent 驱动开发 — 适用于执行包含独立任务的实施计划"
sidebar_label: "子 Agent 驱动开发"
description: "适用于执行包含独立任务的实施计划"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 子 Agent 驱动开发

适用于执行包含独立任务的实施计划。为每个任务分派新的 `delegate_task`，并进行两阶段审查（规范符合性审查，然后是代码质量审查）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/subagent-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent (adapted from obra/superpowers) |
| 许可证 | MIT |
| 标签 | `delegation`, `subagent`, `implementation`, `workflow`, `parallel` |
| 相关技能 | [`writing-plans`](/docs/user-guide/skills/bundled/software-development/software-development-writing-plans), [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review), [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 子 Agent 驱动开发

## 概述

通过为每个任务分派新的子 Agent 并执行系统性的两阶段审查，来执行实施计划。

**核心原则：** 每个任务使用新的子 Agent + 两阶段审查（先规范后质量）= 高质量、快速迭代。

## 使用时机

在以下情况使用此技能：
- 你有一个实施计划（来自 writing-plans 技能或用户需求）
- 任务大多是独立的
- 质量和规范符合性很重要
- 你希望在任务之间进行自动化审查

**与手动执行对比：**
- 每个任务都有新的上下文（避免了累积状态造成的混淆）
- 自动化审查流程能及早发现问题
- 对所有任务进行一致的质量检查
- 子 Agent 可以在开始工作前提出问题

## 流程

### 1. 读取并解析计划

读取计划文件。预先提取所有任务及其完整文本和上下文。创建一个待办事项列表：

```python
# 读取计划
read_file("docs/plans/feature-plan.md")

# 创建包含所有任务的待办事项列表
todo([
    {"id": "task-1", "content": "创建带有 email 字段的 User 模型", "status": "pending"},
    {"id": "task-2", "content": "添加密码哈希工具", "status": "pending"},
    {"id": "task-3", "content": "创建登录端点", "status": "pending"},
])
```

**关键点：** 只读取计划**一次**。提取所有内容。不要让子 Agent 读取计划文件——直接在上下文中提供完整的任务文本。

### 2. 每个任务的工作流

对于计划中的**每个**任务：

#### 步骤 1：分派实现者子 Agent

使用 `delegate_task` 并提供完整的上下文：

```python
delegate_task(
    goal="实现任务 1：创建带有 email 和 password_hash 字段的 User 模型",
    context="""
    计划中的任务：
    - 创建：src/models/user.py
    - 添加带有 email (str) 和 password_hash (str) 字段的 User 类
    - 使用 bcrypt 进行密码哈希
    - 包含用于调试的 __repr__

    遵循 TDD：
    1. 在 tests/models/test_user.py 中编写失败的测试
    2. 运行：pytest tests/models/test_user.py -v (验证失败)
    3. 编写最小实现
    4. 运行：pytest tests/models/test_user.py -v (验证通过)
    5. 运行：pytest tests/ -q (验证没有回归)
    6. 提交：git add -A && git commit -m "feat: add User model with password hashing"

    项目上下文：
    - Python 3.11，Flask 应用在 src/app.py
    - 现有模型在 src/models/
    - 测试使用 pytest，从项目根目录运行
    - bcrypt 已在 requirements.txt 中
    """,
    toolsets=['terminal', 'file']
)
```

#### 步骤 2：分派规范符合性审查者

在实现者完成后，对照原始规范进行验证：

```python
delegate_task(
    goal="审查实现是否符合计划中的规范",
    context="""
    原始任务规范：
    - 创建带有 User 类的 src/models/user.py
    - 字段：email (str), password_hash (str)
    - 使用 bcrypt 进行密码哈希
    - 包含 __repr__

    检查：
    - [ ] 规范中的所有要求都实现了吗？
    - [ ] 文件路径符合规范吗？
    - [ ] 函数签名符合规范吗？
    - [ ] 行为符合预期吗？
    - [ ] 没有额外添加内容（没有范围蔓延）？

    输出：PASS 或需要修复的具体规范差距列表。
    """,
    toolsets=['file']
)
```

**如果发现规范问题：** 修复差距，然后重新运行规范审查。只有在规范符合后才继续。

#### 步骤 3：分派代码质量审查者

在规范符合性通过后：

```python
delegate_task(
    goal="审查任务 1 实现的代码质量",
    context="""
    要审查的文件：
    - src/models/user.py
    - tests/models/test_user.py

    检查：
    - [ ] 遵循项目约定和风格吗？
    - [ ] 有适当的错误处理吗？
    - [ ] 变量/函数名称清晰吗？
    - [ ] 测试覆盖率足够吗？
    - [ ] 没有明显的错误或遗漏的边缘情况吗？
    - [ ] 没有安全问题吗？

    输出格式：
    - 关键问题：[必须修复才能继续]
    - 重要问题：[应该修复]
    - 次要问题：[可选]
    - 结论：APPROVED 或 REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**如果发现质量问题：** 修复问题，重新审查。只有在批准后才继续。

#### 步骤 4：标记完成

```python
todo([{"id": "task-1", "content": "创建带有 email 字段的 User 模型", "status": "completed"}], merge=True)
```

### 3. 最终审查

在**所有**任务完成后，分派一个最终的集成审查者：

```python
delegate_task(
    goal="审查整个实现的一致性和集成问题",
    context="""
    计划中的所有任务都已完成。审查完整实现：
    - 所有组件能协同工作吗？
    - 任务之间有任何不一致吗？
    - 所有测试都通过吗？
    - 准备好合并了吗？
    """,
    toolsets=['terminal', 'file']
)
```

### 4. 验证并提交

```bash
# 运行完整的测试套件
pytest tests/ -q

# 审查所有更改
git diff --stat

# 如果需要，进行最终提交
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## 任务粒度

**每个任务 = 2-5 分钟的专注工作。**

**太大：**
- "实现用户认证系统"

**大小合适：**
- "创建带有 email 和 password 字段的 User 模型"
- "添加密码哈希函数"
- "创建登录端点"
- "添加 JWT Token 生成"
- "创建注册端点"

## 危险信号 — 切勿做这些事

- 没有计划就开始实现
- 跳过审查（规范符合性**或**代码质量）
- 在未修复关键/重要问题的情况下继续
- 为涉及相同文件的任务分派多个实现者子 Agent
- 让子 Agent 读取计划文件（改为在上下文中提供完整文本）
- 跳过场景设定上下文（子 Agent 需要理解任务所处的位置）
- 忽略子 Agent 的问题（在让他们继续之前回答）
- 在规范符合性上接受"差不多就行"
- 跳过审查循环（审查者发现问题 → 实现者修复 → 再次审查）
- 让实现者自我审查代替实际审查（两者都需要）
- **在规范符合性为 PASS 之前开始代码质量审查**（顺序错误）
- 在任一审查存在未解决问题时移动到下一个任务

## 处理问题

### 如果子 Agent 提出问题

- 清晰完整地回答
- 如果需要，提供额外的上下文
- 不要催促他们进入实现阶段

### 如果审查者发现问题

- 实现者子 Agent（或一个新的）修复它们
- 审查者再次审查
- 重复直到批准
- 不要跳过重新审查

### 如果子 Agent 任务失败

- 分派一个新的修复子 Agent，并附带关于出错原因的具体说明
- 不要尝试在控制器会话中手动修复（避免上下文污染）

## 效率说明

**为什么每个任务使用新的子 Agent：**
- 防止累积状态造成的上下文污染
- 每个子 Agent 获得干净、专注的上下文
- 不会因先前任务的代码或推理而产生混淆

**为什么采用两阶段审查：**
- 规范审查能及早发现构建不足或过度构建的问题
- 质量审查确保实现构建良好
- 在问题跨任务累积之前发现问题

**成本权衡：**
- 更多的子 Agent 调用（每个任务：实现者 + 2 个审查者）
- 但能及早发现问题（比后期调试复合问题更便宜）

## 与其他技能的集成

### 与 writing-plans

此技能**执行**由 writing-plans 技能创建的计划：
1. 用户需求 → writing-plans → 实施计划
2. 实施计划 → subagent-driven-development → 可工作的代码

### 与 test-driven-development

实现者子 Agent 应遵循 TDD：
1. 首先编写失败的测试
2. 实现最小代码
3. 验证测试通过
4. 提交

在每个实现者上下文中包含 TDD 说明。

### 与 requesting-code-review

两阶段审查过程**就是**代码审查。对于最终的集成审查，使用 requesting-code-review 技能的审查维度。

### 与 systematic-debugging

如果子 Agent 在实现过程中遇到错误：
1. 遵循 systematic-debugging 流程
2. 在修复前找到根本原因
3. 编写回归测试
4. 恢复实现

## 示例工作流

```
[读取计划：docs/plans/auth-feature.md]
[创建包含 5 个任务的待办事项列表]

--- 任务 1：创建 User 模型 ---
[分派实现者子 Agent]
  实现者："email 应该是唯一的吗？"
  你："是的，email 必须是唯一的"
  实现者：已实现，3/3 测试通过，已提交。

[分派规范审查者]
  规范审查者：✅ PASS — 所有要求都已满足

[分派质量审查者]
  质量审查者：✅ APPROVED — 代码清晰，测试良好

[标记任务 1 完成]

--- 任务 2：密码哈希 ---
[分派实现者子 Agent]
  实现者：没有问题，已实现，5/5 测试通过。

[分派规范审查者]
  规范审查者：❌ 缺失：密码强度验证（规范要求"最少 8 个字符"）

[实现者修复]
  实现者：添加了验证，7/7 测试通过。

[再次分派规范审查者]
  规范审查者：✅ PASS

[分派质量审查者]
  质量审查者：重要：魔法数字 8，提取为常量
  实现者：提取了 MIN_PASSWORD_LENGTH 常量
  质量审查者：✅ APPROVED

[标记任务 2 完成]

... (继续所有任务)

[所有任务完成后：分派最终集成审查者]
[运行完整测试套件：全部通过]
[完成！]
```

## 记住

```
每个任务使用新的子 Agent
每次都进行两阶段审查
规范符合性优先
代码质量其次
永不跳过审查
及早发现问题
```

**质量不是偶然的。它是系统性流程的结果。**