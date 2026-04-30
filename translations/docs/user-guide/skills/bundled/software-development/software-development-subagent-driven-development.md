---
title: "子代理驱动开发 — 通过 delegate_task 子代理执行计划（两阶段评审）"
sidebar_label: "子代理驱动开发"
description: "通过 delegate_task 子代理执行计划（两阶段评审）"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 子代理驱动开发

通过 delegate_task 子代理执行计划（两阶段评审）。

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

# 子代理驱动开发

## 概述

通过为每个任务分派新的子代理并执行系统性的两阶段评审来执行实施计划。

**核心原则：** 每个任务使用新的子代理 + 两阶段评审（规范符合性，然后代码质量）= 高质量、快速迭代。

## 何时使用

在以下情况使用此技能：
- 你有一个实施计划（来自 writing-plans 技能或用户需求）
- 任务基本独立
- 质量和规范符合性很重要
- 你希望在任务之间进行自动化评审

**与手动执行对比：**
- 每个任务都有新的上下文（不会因累积状态而产生混淆）
- 自动化评审流程能及早发现问题
- 所有任务都进行一致的质量检查
- 子代理可以在开始工作前提出问题

## 流程

### 1. 读取并解析计划

读取计划文件。预先提取所有任务及其完整文本和上下文。创建一个待办事项列表：

```python
# 读取计划
read_file("docs/plans/feature-plan.md")

# 创建包含所有任务的待办事项列表
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**关键点：** 只读取计划**一次**。提取所有内容。不要让子代理读取计划文件——直接在上下文中提供完整的任务文本。

### 2. 每个任务的工作流

对于计划中的**每个**任务：

#### 步骤 1：分派实施者子代理

使用 `delegate_task` 并提供完整上下文：

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### 步骤 2：分派规范符合性评审员

实施者完成后，对照原始规范进行验证：

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**如果发现规范问题：** 修复差距，然后重新运行规范评审。只有在规范符合后才继续。

#### 步骤 3：分派代码质量评审员

规范符合性通过后：

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**如果发现质量问题：** 修复问题，重新评审。只有在批准后才继续。

#### 步骤 4：标记为完成

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. 最终评审

在**所有**任务完成后，分派一个最终的集成评审员：

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. 验证并提交

```bash
# 运行完整的测试套件
pytest tests/ -q

# 查看所有更改
git diff --stat

# 如有需要，进行最终提交
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## 任务粒度

**每个任务 = 2-5 分钟的专注工作。**

**太大：**
- "实现用户认证系统"

**大小合适：**
- "创建包含邮箱和密码字段的 User 模型"
- "添加密码哈希函数"
- "创建登录端点"
- "添加 JWT Token 生成"
- "创建注册端点"

## 危险信号 — 切勿做这些事

- 没有计划就开始实施
- 跳过评审（规范符合性或代码质量）
- 在未修复关键/重要问题的情况下继续
- 为涉及相同文件的任务分派多个实施者子代理
- 让子代理读取计划文件（应在上下文中提供完整文本）
- 忽略场景设置上下文（子代理需要理解任务所处的位置）
- 忽略子代理的问题（在让他们继续之前回答）
- 在规范符合性上接受"差不多就行"
- 跳过评审循环（评审员发现问题 → 实施者修复 → 再次评审）
- 让实施者自我评审代替实际评审（两者都需要）
- **在规范符合性通过之前开始代码质量评审**（顺序错误）
- 在任一评审存在未解决问题时进入下一个任务

## 处理问题

### 如果子代理提问

- 清晰完整地回答
- 如果需要，提供额外的上下文
- 不要催促他们进入实施阶段

### 如果评审员发现问题

- 实施者子代理（或一个新的子代理）修复它们
- 评审员再次评审
- 重复直到批准
- 不要跳过重新评审

### 如果子代理任务失败

- 分派一个新的修复子代理，并附上关于出错原因的具体说明
- 不要尝试在控制器会话中手动修复（会造成上下文污染）

## 效率说明

**为什么每个任务使用新的子代理：**
- 防止因累积状态造成的上下文污染
- 每个子代理获得干净、专注的上下文
- 不会因先前任务的代码或推理而产生混淆

**为什么需要两阶段评审：**
- 规范评审能及早发现构建不足或过度构建
- 质量评审确保实现是精心构建的
- 在问题在任务间累积之前发现它们

**成本权衡：**
- 更多的子代理调用（每个任务：实施者 + 2 个评审员）
- 但能及早发现问题（比后期调试复合问题更便宜）

## 与其他技能的集成

### 与 writing-plans

此技能**执行**由 writing-plans 技能创建的计划：
1. 用户需求 → writing-plans → 实施计划
2. 实施计划 → subagent-driven-development → 可工作的代码

### 与 test-driven-development

实施者子代理应遵循 TDD：
1. 首先编写失败的测试
2. 实现最少的代码
3. 验证测试通过
4. 提交

在每个实施者上下文中包含 TDD 说明。

### 与 requesting-code-review

两阶段评审过程**就是**代码评审。对于最终的集成评审，使用 requesting-code-review 技能的评审维度。

### 与 systematic-debugging

如果子代理在实施过程中遇到 Bug：
1. 遵循 systematic-debugging 流程
2. 在修复前找到根本原因
3. 编写回归测试
4. 恢复实施

## 示例工作流

```
[读取计划：docs/plans/auth-feature.md]
[创建包含 5 个任务的待办事项列表]

--- 任务 1：创建 User 模型 ---
[分派实施者子代理]
  实施者："邮箱需要唯一吗？"
  你："是的，邮箱必须唯一"
  实施者：已实施，3/3 测试通过，已提交。

[分派规范评审员]
  规范评审员：✅ 通过 — 所有要求均已满足

[分派质量评审员]
  质量评审员：✅ 批准 — 代码清晰，测试良好

[标记任务 1 完成]

--- 任务 2：密码哈希 ---
[分派实施者子代理]
  实施者：无问题，已实施，5/5 测试通过。

[分派规范评审员]
  规范评审员：❌ 缺失：密码强度验证（规范要求"最少 8 个字符"）

[实施者修复]
  实施者：添加了验证，7/7 测试通过。

[再次分派规范评审员]
  规范评审员：✅ 通过

[分派质量评审员]
  质量评审员：重要：魔法数字 8，提取为常量
  实施者：提取了 MIN_PASSWORD_LENGTH 常量
  质量评审员：✅ 批准

[标记任务 2 完成]

... (继续所有任务)

[所有任务完成后：分派最终集成评审员]
[运行完整测试套件：全部通过]
[完成！]
```

## 记住

```
每个任务使用新的子代理
每次都进行两阶段评审
规范符合性优先
代码质量其次
永不跳过评审
及早发现问题
```

**质量不是偶然的。它是系统性流程的结果。**

## 延伸阅读（相关时加载）

当编排涉及大量上下文使用、长评审循环或复杂的验证检查点时，加载这些参考资料以获取特定规程：

- **`references/context-budget-discipline.md`** — 四层上下文退化模型（PEAK / GOOD / DEGRADING / POOR）、随上下文窗口大小扩展的读取深度规则，以及无声退化的早期预警信号。当运行显然会消耗大量上下文时加载（多阶段计划、许多子代理、大型工件）。
- **`references/gates-taxonomy.md`** — 四种规范门类型（Pre-flight, Revision, Escalation, Abort）及其行为、恢复和示例。在设计或评审任何包含验证检查点的工作流时加载——明确使用该词汇，以便每个门都有定义的进入条件、失败行为和恢复规则。

以上参考资料改编自 gsd-build/get-shit-done (MIT © 2025 Lex Christopherson)。