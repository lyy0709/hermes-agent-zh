---
title: "Oss Forensics — GitHub 仓库的供应链调查、证据恢复和取证分析"
sidebar_label: "Oss Forensics"
description: "GitHub 仓库的供应链调查、证据恢复和取证分析"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Oss Forensics

GitHub 仓库的供应链调查、证据恢复和取证分析。
涵盖已删除提交的恢复、强制推送检测、IOC 提取、多源证据收集、假设形成/验证以及结构化取证报告。
灵感来源于 RAPTOR 的 1800+ 行 OSS Forensics 系统。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/oss-forensics` 安装 |
| 路径 | `optional-skills/security/oss-forensics` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# OSS 安全取证技能

一个用于研究开源供应链攻击的 7 阶段多 Agent 调查框架。
改编自 RAPTOR 的取证系统。涵盖 GitHub Archive、Wayback Machine、GitHub API、本地 git 分析、IOC 提取、基于证据的假设形成和验证，以及最终的取证报告生成。

---

## ⚠️ 反幻觉护栏

在每个调查步骤之前阅读这些内容。违反它们将使报告无效。

1.  **证据优先规则**：任何报告、假设或摘要中的每个主张**必须**引用至少一个证据 ID (`EV-XXXX`)。禁止没有引用的断言。
2.  **各司其职**：每个子 Agent（调查员）只有一个数据源。**不要**混合来源。GH Archive 调查员不查询 GitHub API，反之亦然。角色边界是硬性的。
3.  **事实与假设分离**：将所有未经验证的推论标记为 `[HYPOTHESIS]`。只有对照原始来源验证过的陈述才能作为事实陈述。
4.  **禁止捏造证据**：假设验证器**必须**在接收假设之前，机械地检查每个引用的证据 ID 是否确实存在于证据存储中。
5.  **需要证据的证伪**：没有具体、有证据支持的反驳论点，不能驳回一个假设。“未找到证据”不足以证伪——它只会使假设无法定论。
6.  **SHA/URL 双重验证**：任何作为证据引用的提交 SHA、URL 或外部标识符，在被标记为已验证之前，必须从至少两个来源独立确认。
7.  **可疑代码规则**：**切勿**在本地运行在调查仓库内发现的代码。仅进行静态分析，或在沙盒环境中使用 `execute_code`。
8.  **密钥脱敏**：调查期间发现的任何 API 密钥、Token 或凭证必须在最终报告中脱敏。仅在内部记录它们。

---

## 示例场景

-   **场景 A：依赖混淆**：恶意包 `internal-lib-v2` 以高于内部版本的版本号上传到 NPM。调查员必须追踪该包首次出现的时间，以及目标仓库中是否有任何 PushEvents 将 `package.json` 更新为此版本。
-   **场景 B：维护者接管**：一个长期贡献者的账户被用来推送一个被植入后门的 `.github/workflows/build.yml`。调查员会查找该用户在长时间不活动后或来自新 IP/位置（如果可通过 BigQuery 检测到）的 PushEvents。
-   **场景 C：强制推送隐藏**：开发者意外提交了生产密钥，然后强制推送以“修复”。调查员使用 `git fsck` 和 GH Archive 来恢复原始提交 SHA 并验证泄露的内容。

---

> **路径约定**：在整个技能中，`SKILL_DIR` 指的是此技能安装目录的根目录（包含此 `SKILL.md` 的文件夹）。当技能加载时，将 `SKILL_DIR` 解析为实际路径——例如 `~/.hermes/skills/security/oss-forensics/` 或 `optional-skills/` 的等效路径。所有脚本和模板引用都相对于它。

## 阶段 0：初始化

1.  创建调查工作目录：
    ```bash
    mkdir investigation_$(echo "REPO_NAME" | tr '/' '_')
    cd investigation_$(echo "REPO_NAME" | tr '/' '_')
    ```
2.  初始化证据存储：
    ```bash
    python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list
    ```
3.  复制取证报告模板：
    ```bash
    cp SKILL_DIR/templates/forensic-report.md ./investigation-report.md
    ```
4.  创建一个 `iocs.md` 文件，用于跟踪发现的危害指标。
5.  记录调查开始时间、目标仓库和声明的调查目标。

---

## 阶段 1：提示词解析与 IOC 提取

**目标**：从用户请求中提取所有结构化的调查目标。

**操作**：
-   解析用户提示词并提取：
    -   目标仓库 (`owner/repo`)
    -   目标参与者（GitHub 用户名、电子邮件地址）
    -   感兴趣的时间窗口（提交日期范围、PR 时间戳）
    -   提供的危害指标：提交 SHA、文件路径、包名、IP 地址、域名、API 密钥/Token、恶意 URL
    -   任何链接的供应商安全报告或博客文章

**工具**：仅推理，或使用 `execute_code` 从大文本块中进行正则表达式提取。

**输出**：用提取的 IOC 填充 `iocs.md`。每个 IOC 必须包含：
-   类型（来自：COMMIT_SHA, FILE_PATH, API_KEY, SECRET, IP_ADDRESS, DOMAIN, PACKAGE_NAME, ACTOR_USERNAME, MALICIOUS_URL, OTHER）
-   值
-   来源（用户提供，推断）

**参考**：有关 IOC 分类法，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md)。

---

## 阶段 2：并行证据收集

使用 `delegate_task`（批量模式，最多 3 个并发）生成最多 5 个专业调查员子 Agent。每个调查员有**单一数据源**，不得混合来源。
> **编排器说明**：将第一阶段获取的 IOC 列表和调查时间窗口传递到每个委派任务的 `context` 字段中。

---

### 调查员 1：本地 Git 调查员

**角色边界**：你仅查询**本地 Git 仓库**。不要调用任何外部 API。

**操作**：
```bash
# 克隆仓库
git clone https://github.com/OWNER/REPO.git target_repo && cd target_repo

# 完整的提交日志（带统计信息）
git log --all --full-history --stat --format="%H|%ae|%an|%ai|%s" > ../git_log.txt

# 检测强制推送证据（孤立/悬空提交）
git fsck --lost-found --unreachable 2>&1 | grep commit > ../dangling_commits.txt

# 检查 reflog 以查找重写的历史记录
git reflog --all > ../reflog.txt

# 列出所有分支（包括已删除的远程引用）
git branch -a -v > ../branches.txt

# 查找可疑的大型二进制文件添加
git log --all --diff-filter=A --name-only --format="%H %ai" -- "*.so" "*.dll" "*.exe" "*.bin" > ../binary_additions.txt

# 检查 GPG 签名异常
git log --show-signature --format="%H %ai %aN" > ../signature_check.txt 2>&1
```

**需要收集的证据**（通过 `python3 SKILL_DIR/scripts/evidence-store.py add` 添加）：
- 每个悬空提交的 SHA → 类型：`git`
- 强制推送证据（reflog 显示历史记录被重写）→ 类型：`git`
- 已验证贡献者的未签名提交 → 类型：`git`
- 可疑的二进制文件添加 → 类型：`git`

**参考**：关于访问强制推送的提交，请参阅 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)。

---

### 调查员 2：GitHub API 调查员

**角色边界**：你仅查询 **GitHub REST API**。不要在本地运行 git 命令。

**操作**：
```bash
# 提交（分页）
curl -s "https://api.github.com/repos/OWNER/REPO/commits?per_page=100" > api_commits.json

# 拉取请求（包括已关闭/已删除的）
curl -s "https://api.github.com/repos/OWNER/REPO/pulls?state=all&per_page=100" > api_prs.json

# 议题
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=all&per_page=100" > api_issues.json

# 贡献者和协作者变更
curl -s "https://api.github.com/repos/OWNER/REPO/contributors" > api_contributors.json

# 仓库事件（最近 300 条）
curl -s "https://api.github.com/repos/OWNER/REPO/events?per_page=100" > api_events.json

# 检查特定可疑提交 SHA 的详细信息
curl -s "https://api.github.com/repos/OWNER/REPO/git/commits/SHA" > commit_detail.json

# 发布版本
curl -s "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" > api_releases.json

# 检查特定提交是否存在（强制推送的提交可能在 commits/ 端点返回 404，但在 git/commits/ 端点成功）
curl -s "https://api.github.com/repos/OWNER/REPO/commits/SHA" | jq .sha
```

**交叉引用目标**（将差异标记为证据）：
- 存档中存在但 API 中缺失的 PR → 删除证据
- 存档事件中存在但贡献者列表中不存在的贡献者 → 权限撤销证据
- 存档 PushEvents 中存在但 API 提交列表中不存在的提交 → 强制推送/删除证据

**参考**：关于 GH 事件类型，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md)。

---

### 调查员 3：Wayback Machine 调查员

**角色边界**：你仅查询 **Wayback Machine CDX API**。不要使用 GitHub API。

**目标**：恢复已删除的 GitHub 页面（README、议题、PR、发布版本、Wiki 页面）。

**操作**：
```bash
# 搜索仓库主页的存档快照
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO&output=json&limit=100&from=YYYYMMDD&to=YYYYMMDD" > wayback_main.json

# 搜索特定的已删除议题
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/issues/NUM&output=json&limit=50" > wayback_issue_NUM.json

# 搜索特定的已删除 PR
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/pull/NUM&output=json&limit=50" > wayback_pr_NUM.json

# 获取页面的最佳快照
# 使用 Wayback Machine URL: https://web.archive.org/web/TIMESTAMP/ORIGINAL_URL
# 示例：https://web.archive.org/web/20240101000000*/github.com/OWNER/REPO

# 高级：搜索已删除的发布版本/标签
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/releases/tag/*&output=json" > wayback_tags.json

# 高级：搜索历史 Wiki 变更
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/wiki/*&output=json" > wayback_wiki.json
```

**需要收集的证据**：
- 包含其内容的已删除议题/PR 的存档快照
- 显示变更的历史 README 版本
- 存档中存在但当前 GitHub 状态中缺失的内容证据

**参考**：关于 CDX API 参数，请参阅 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md)。

---

### 调查员 4：GH Archive / BigQuery 调查员

**角色边界**：你仅通过 **BigQuery** 查询 **GitHub Archive**。这是所有公共 GitHub 事件的防篡改记录。

> **先决条件**：需要具有 BigQuery 访问权限的 Google Cloud 凭据（`gcloud auth application-default login`）。如果不可用，请跳过此调查员并在报告中注明。

**成本优化规则**（**强制遵守**）：
1. 在每次查询之前，**始终**先运行 `--dry_run` 以估算成本。
2. 使用 `_TABLE_SUFFIX` 按日期范围过滤，以最小化扫描的数据量。
3. 仅 SELECT 你需要的列。
4. 除非进行聚合，否则添加 LIMIT。

```bash
# 模板：针对 OWNER/REPO 的 PushEvents 的安全 BigQuery 查询
bq query --use_legacy_sql=false --dry_run "
SELECT created_at, actor.login, payload.commits, payload.before, payload.head,
       payload.size, payload.distinct_size
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'PushEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 1000
"
# 如果成本可接受，重新运行（不带 --dry_run）

# 检测强制推送：distinct_size 为零的 PushEvents 意味着提交被强制擦除
# payload.distinct_size = 0 AND payload.size > 0 → 强制推送指示器

# 检查已删除分支事件
bq query --use_legacy_sql=false "
SELECT created_at, actor.login, payload.ref, payload.ref_type
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'DeleteEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 200
"
```
**需要收集的证据**：
- 强制推送事件（`payload.size > 0`，`payload.distinct_size = 0`）
- 针对分支/标签的 `DeleteEvent` 事件
- 可疑 CI/CD 自动化的 `WorkflowRunEvent` 事件
- 在 git 日志中出现在“空白”之前的 `PushEvent` 事件（重写证据）

**参考**：所有 12 种事件类型和查询模式，请参阅 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md)。

---

### 调查员 5：IOC 丰富化调查员

**角色边界**：你**仅**使用被动的公开来源来丰富**现有**的来自第 1 阶段的 IOC。**不要执行**目标仓库中的任何代码。

**行动**：
- 对于每个提交 SHA：尝试通过直接的 GitHub URL 恢复（`github.com/OWNER/REPO/commit/SHA.patch`）
- 对于每个域名/IP：检查被动 DNS、WHOIS 记录（通过公共 WHOIS 服务上的 `web_extract`）
- 对于每个包名：检查 npm/PyPI 以匹配恶意包报告
- 对于每个参与者用户名：检查 GitHub 个人资料、贡献历史、账户年龄
- 使用 3 种方法恢复强制推送的提交（参见 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)）

---

## 第 3 阶段：证据整合

在所有调查员完成后：

1. 运行 `python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list` 以查看所有收集到的证据。
2. 对于每条证据，验证 `content_sha256` 哈希是否与原始来源匹配。
3. 按以下方式对证据进行分组：
   - **时间线**：按时间顺序对所有带时间戳的证据进行排序
   - **参与者**：按 GitHub 用户名或邮箱分组
   - **IOC**：将证据与其相关的 IOC 关联起来
4. 识别**差异**：存在于一个来源但另一个来源中缺失的项目（关键删除指标）。
5. 将证据标记为 `[VERIFIED]`（已从 2 个以上独立来源确认）或 `[UNVERIFIED]`（仅单一来源）。

---

## 第 4 阶段：假设形成

假设必须：
- 陈述一个具体的声明（例如，“参与者 X 在 DATE 强制推送至 BRANCH 以删除提交 SHA”）
- 引用至少 2 个支持它的证据 ID（`EV-XXXX`，`EV-YYYY`）
- 指出哪些证据可以证伪它
- 在验证前标记为 `[HYPOTHESIS]`

**常见假设模板**（参见 [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md)）：
- 维护者账户被入侵：被接管的合法账户被用于注入恶意代码
- 依赖混淆：通过抢注包名来拦截安装
- CI/CD 注入：恶意的工作流变更以在构建期间运行代码
- 仿冒包：针对拼写错误的、几乎相同的包名
- 凭证泄露：意外提交的 token/密钥，随后通过强制推送删除

对于每个假设，在确认之前，生成一个 `delegate_task` 子 Agent 来尝试寻找证伪证据。

---

## 第 5 阶段：假设验证

验证子 Agent **必须**机械地检查：

1. 对于每个假设，提取所有引用的证据 ID。
2. 验证每个 ID 是否存在于 `evidence.json` 中（如果任何 ID 缺失，则视为硬性失败 → 假设因可能被捏造而被拒绝）。
3. 验证每条 `[VERIFIED]` 证据是否已从 2 个以上来源确认。
4. 检查逻辑一致性：证据所描绘的时间线是否支持该假设？
5. 检查是否存在替代解释：相同的证据模式是否可能由良性原因引起？

**输出**：
- `VALIDATED`：所有证据均已引用、验证、逻辑一致，且没有合理的替代解释。
- `INCONCLUSIVE`：证据支持假设，但存在替代解释或证据不足。
- `REJECTED`：缺失证据 ID、未经证实的证据被引用为事实、检测到逻辑不一致。

被拒绝的假设将反馈到第 4 阶段进行完善（最多 3 次迭代）。

---

## 第 6 阶段：最终报告生成

使用 [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) 中的模板填充 `investigation-report.md`。

**必填部分**：
- 执行摘要：一段式结论（已入侵 / 干净 / 无法确定）及置信度
- 时间线：按时间顺序重建所有重要事件，并附证据引用
- 已验证的假设：每个假设的状态及支持证据 ID
- 证据登记表：所有 `EV-XXXX` 条目的表格，包含来源、类型和验证状态
- IOC 列表：所有提取并丰富化的入侵指标
- 证据链：证据如何收集、从哪些来源、在什么时间戳
- 建议：如果检测到入侵，立即采取的缓解措施；监控建议

**报告规则**：
- 每个事实声明必须至少有一个 `[EV-XXXX]` 引用
- 执行摘要必须说明置信度（高 / 中 / 低）
- 所有秘密/凭证必须被编辑为 `[REDACTED]`

---

## 第 7 阶段：完成

1. 运行最终证据计数：`python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list`
2. 归档完整的调查目录。
3. 如果确认入侵：
   - 列出立即的缓解措施（轮换凭证、固定依赖哈希、通知受影响的用户）
   - 识别受影响的版本/包
   - 注意披露义务（如果是公共包：与包注册表协调）
4. 向用户呈现最终的 `investigation-report.md`。

---

## 道德使用准则

此技能设计用于**防御性安全调查**——保护开源软件免受供应链攻击。**不得**用于：

- **骚扰或跟踪**贡献者或维护者
- **人肉搜索**——将 GitHub 活动与真实身份关联以用于恶意目的
- **竞争情报**——未经授权调查专有或内部仓库
- **虚假指控**——在未经证据验证的情况下发布调查结果（参见反幻觉护栏）
调查应遵循**最小侵入**原则：仅收集验证或反驳假设所需的证据。发布结果时，应遵循负责任的披露实践，并在公开披露前与受影响的维护者协调。

如果调查发现确实存在入侵，请遵循协调漏洞披露流程：
1. 首先私下通知仓库维护者
2. 给予合理的修复时间（通常为 90 天）
3. 如果发布的软件包受到影响，请与软件包注册中心（npm、PyPI 等）协调
4. 在适当时提交 CVE

---

## API 速率限制

GitHub REST API 强制执行速率限制，如果管理不当，会中断大型调查。

**认证请求**：5,000 次/小时（需要 `GITHUB_TOKEN` 环境变量或 `gh` CLI 认证）
**未认证请求**：60 次/小时（不适用于调查）

**最佳实践**：
- 始终进行认证：`export GITHUB_TOKEN=ghp_...` 或使用 `gh` CLI（自动认证）
- 使用条件请求（`If-None-Match` / `If-Modified-Since` 头）以避免在未更改的数据上消耗配额
- 对于分页端点，按顺序获取所有页面——不要对同一端点进行并行请求
- 检查 `X-RateLimit-Remaining` 头；如果低于 100，则暂停到 `X-RateLimit-Reset` 时间戳
- BigQuery 有自己的配额（免费层为 10 TiB/天）——始终先进行试运行
- Wayback Machine CDX API：没有正式的速率限制，但请保持礼貌（最大 1-2 次请求/秒）

如果在调查过程中受到速率限制，请在证据存储中记录部分结果，并在报告中注明此限制。

---

## 参考资料

- [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md) — BigQuery 查询、CDX API、12 种事件类型
- [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md) — IOC 分类、证据来源类型、观察类型
- [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md) — 恢复已删除的提交、PR、问题
- [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md) — 针对每种攻击类型的预构建假设模板
- [evidence-store.py](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/scripts/evidence-store.py) — 用于管理证据 JSON 存储的 CLI 工具
- [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) — 结构化报告模板