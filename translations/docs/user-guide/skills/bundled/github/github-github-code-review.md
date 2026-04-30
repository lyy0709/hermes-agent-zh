---
title: "Github Code Review — 审查 PR：通过 gh 或 REST 查看差异和行内评论"
sidebar_label: "Github Code Review"
description: "审查 PR：通过 gh 或 REST 查看差异和行内评论"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Github Code Review

审查 PR：通过 gh 或 REST 查看差异和行内评论。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-code-review` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GitHub`, `Code-Review`, `Pull-Requests`, `Git`, `Quality` |
| 相关技能 | [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth), [`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitHub Code Review

在推送前审查本地更改，或审查 GitHub 上开放的 PR。此技能大部分使用纯 `git` — `gh`/`curl` 的分工仅对 PR 级别的交互有影响。

## 先决条件

- 已通过 GitHub 认证（参见 `github-auth` 技能）
- 位于 git 仓库内

### 设置（用于 PR 交互）

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. 审查本地更改（推送前）

这是纯 `git` 操作 — 随处可用，无需 API。

### 获取差异

```bash
# 暂存的更改（即将提交的内容）
git diff --staged

# 与 main 分支的所有差异（PR 将包含的内容）
git diff main...HEAD

# 仅文件名
git diff main...HEAD --name-only

# 统计摘要（每个文件的插入/删除）
git diff main...HEAD --stat
```

### 审查策略

1.  **首先了解整体情况：**

```bash
git diff main...HEAD --stat
git log main..HEAD --oneline
```

2.  **逐文件审查** — 对更改的文件使用 `read_file` 获取完整上下文，并使用 diff 查看具体更改：

```bash
git diff main...HEAD -- src/auth/login.py
```

3.  **检查常见问题：**

```bash
# 遗留的调试语句、TODO、console.log
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"

# 意外暂存的大文件
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10

# 密钥或凭据模式
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"

# 合并冲突标记
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

4.  **向用户呈现结构化的反馈。**

### 审查输出格式

审查本地更改时，按以下结构呈现发现：

```
## 代码审查摘要

### 关键问题
- **src/auth.py:45** — SQL 注入：用户输入直接传递给查询。
  建议：使用参数化查询。

### 警告
- **src/models/user.py:23** — 密码以明文存储。请使用 bcrypt 或 argon2。
- **src/api/routes.py:112** — 登录端点无限流控。

### 建议
- **src/utils/helpers.py:8** — 与 `src/core/utils.py:34` 的逻辑重复。建议合并。
- **tests/test_auth.py** — 缺少边界情况：过期 Token 测试。

### 良好之处
- 中间件层的关注点分离清晰
- 主流程的测试覆盖良好
```

---

## 2. 审查 GitHub 上的 Pull Request

### 查看 PR 详情

**使用 gh：**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**使用 git + curl：**

```bash
PR_NUMBER=123

# 获取 PR 详情
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f\"Title: {pr['title']}\")
print(f\"Author: {pr['user']['login']}\")
print(f\"Branch: {pr['head']['ref']} -> {pr['base']['ref']}\")
print(f\"State: {pr['state']}\")
print(f\"Body:\n{pr['body']}\")"

# 列出更改的文件
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### 在本地检出 PR 以进行全面审查

这使用纯 `git` 即可 — 无需 `gh`：

```bash
# 获取 PR 分支并检出
git fetch origin pull/123/head:pr-123
git checkout pr-123

# 现在你可以使用 read_file、search_files、运行测试等。

# 查看与基础分支的差异
git diff main...pr-123
```

**使用 gh（快捷方式）：**

```bash
gh pr checkout 123
```

### 在 PR 上留下评论

**通用 PR 评论 — 使用 gh：**

```bash
gh pr comment 123 --body "总体看起来不错，下面有一些建议。"
```

**通用 PR 评论 — 使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "总体看起来不错，下面有一些建议。"}'
```

### 留下行内审查评论

**单个行内评论 — 使用 gh（通过 API）：**

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="这可以通过列表推导式简化。" \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```
**单条行内评论 — 使用 curl：**

```bash
# 获取最新提交的 SHA
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{
    \"body\": \"这可以用列表推导式来简化。\",
    \"path\": \"src/auth/login.py\",
    \"commit_id\": \"$HEAD_SHA\",
    \"line\": 45,
    \"side\": \"RIGHT\"
  }"
```

### 提交正式评审（批准 / 请求更改）

**使用 gh：**

```bash
gh pr review 123 --approve --body "LGTM！"
gh pr review 123 --request-changes --body "请查看行内评论。"
gh pr review 123 --comment --body "一些建议，没有阻塞性问题。"
```

**使用 curl — 以原子方式提交包含多条评论的评审：**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"COMMENT\",
    \"body\": \"来自 Hermes Agent 的代码评审\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"使用参数化查询以防止 SQL 注入。\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"在存储前使用 bcrypt 对密码进行哈希。\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"为过期的 Token 边界情况添加测试。\"}
    ]
  }"
```

事件值：`"APPROVE"`、`"REQUEST_CHANGES"`、`"COMMENT"`

`line` 字段指的是文件*新*版本中的行号。对于已删除的行，使用 `"side": "LEFT"`。

---

## 3. 评审清单

执行代码评审（本地或 PR）时，系统性地检查：

### 正确性
- 代码是否实现了其声称的功能？
- 边界情况是否已处理（空输入、空值、大数据、并发访问）？
- 错误路径是否优雅处理？

### 安全性
- 没有硬编码的密钥、凭据或 API 密钥
- 对用户输入进行验证
- 没有 SQL 注入、XSS 或路径遍历漏洞
- 在需要的地方进行身份验证/授权检查

### 代码质量
- 命名清晰（变量、函数、类）
- 没有不必要的复杂性或过早的抽象
- DRY — 没有应该提取的重复逻辑
- 函数职责单一

### 测试
- 新的代码路径是否经过测试？
- 是否覆盖了正常路径和错误情况？
- 测试是否可读且可维护？

### 性能
- 没有 N+1 查询或不必要的循环
- 在有益处的地方进行适当的缓存
- 在异步代码路径中没有阻塞操作

### 文档
- 公共 API 已记录
- 非显而易见的逻辑有注释解释“为什么”
- 如果行为发生变更，README 已更新

---

## 4. 推送前评审工作流

当用户要求你“评审代码”或“推送前检查”时：

1. `git diff main...HEAD --stat` — 查看变更范围
2. `git diff main...HEAD` — 阅读完整的差异
3. 对于每个更改的文件，如果需要更多上下文，请使用 `read_file`
4. 应用上述清单
5. 以结构化格式呈现发现（关键问题 / 警告 / 建议 / 良好）
6. 如果发现关键问题，在用户推送前提供修复建议

---

## 5. PR 评审工作流（端到端）

当用户要求你“评审 PR #N”、“查看这个 PR”或给你一个 PR URL 时，请遵循此流程：

### 步骤 1：设置环境

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# 或者运行此技能顶部的内联设置代码块
```

### 步骤 2：收集 PR 上下文

在深入代码之前，获取 PR 元数据、描述和更改文件列表以了解范围。

**使用 gh：**
```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
```

**使用 curl：**
```bash
PR_NUMBER=123

# PR 详情（标题、作者、描述、分支）
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER

# 更改的文件及行数统计
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

### 步骤 3：在本地检出 PR

这让你可以完全访问 `read_file`、`search_files` 以及运行测试的能力。

```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

### 步骤 4：阅读差异并理解变更

```bash
# 相对于基础分支的完整差异
git diff main...HEAD

# 或者对于大型 PR，逐个文件查看
git diff main...HEAD --name-only
# 然后对每个文件：
git diff main...HEAD -- path/to/file.py
```

对于每个更改的文件，使用 `read_file` 查看变更周围的完整上下文 — 仅凭差异可能会遗漏只有在周围代码中才能看到的问题。

### 步骤 5：在本地运行自动化检查（如果适用）

```bash
# 如果有测试套件，则运行测试
python -m pytest 2>&1 | tail -20
# 或者：npm test, cargo test, go test ./... 等

# 如果配置了 linter，则运行
ruff check . 2>&1 | head -30
# 或者：eslint, clippy 等
```

### 步骤 6：应用评审清单（第 3 节）

逐项检查每个类别：正确性、安全性、代码质量、测试、性能、文档。

### 步骤 7：将评审发布到 GitHub

收集你的发现，并将其作为带有行内评论的正式评审提交。

**使用 gh：**
```bash
# 如果没有问题 — 批准
gh pr review $PR_NUMBER --approve --body "由 Hermes Agent 评审。代码看起来干净 — 测试覆盖良好，没有安全问题。"

# 如果发现问题 — 请求更改并附带行内评论
gh pr review $PR_NUMBER --request-changes --body "发现了一些问题 — 请查看行内评论。"
```

**使用 curl — 包含多条行内评论的原子评审：**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

# 构建评审 JSON — event 是 APPROVE、REQUEST_CHANGES 或 COMMENT
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"## Hermes Agent 评审\n\n发现 2 个问题，1 条建议。请查看行内评论。\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 **关键问题：** 用户输入直接传递给 SQL 查询 — 请使用参数化查询。\"},
      {\"path\": \"src/models.py\", \"line\": 23, \"body\": \"⚠️ **警告：** 密码未经哈希存储。\"},
      {\"path\": \"src/utils.py\", \"line\": 8, \"body\": \"💡 **建议：** 这与 core/utils.py:34 的逻辑重复。\"}
    ]
  }"
```
### 步骤 8：同时发布一个总结性评论

除了行内评论外，还要留下一个顶层的总结，以便 PR 作者能一目了然地了解全貌。使用 `references/review-output-template.md` 中的审查输出格式。

**使用 gh：**
```bash
gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
## 代码审查总结

**结论：需要修改** (2 个问题，1 个建议)

### 🔴 关键问题
- **src/auth.py:45** — SQL 注入漏洞

### ⚠️ 警告
- **src/models.py:23** — 明文密码存储

### 💡 建议
- **src/utils.py:8** — 逻辑重复，考虑合并

### ✅ 良好之处
- 清晰的 API 设计
- 中间件层良好的错误处理

---
*由 Hermes Agent 审查*
EOF
)"
```

### 步骤 9：清理

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```

### 决定：批准 vs 请求修改 vs 评论

- **批准** — 没有关键或警告级别的问题，只有次要建议或全部通过
- **请求修改** — 存在任何关键或警告级别的问题，应在合并前修复
- **评论** — 观察和建议，但无阻塞性问题（当你不确定或 PR 是草稿时使用）