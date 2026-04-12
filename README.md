# hermes-agent-zh

[hermes-agent](https://github.com/NousResearch/hermes-agent) 中文翻译版 —— 自动翻译、自动同步、自动发版。

> **The agent that grows with you** — 与你一同成长的 AI Agent

## 项目简介

本项目是 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 的中文翻译版本，采用 **翻译覆盖层** 架构：

- 仓库中只存储翻译配置、翻译脚本和翻译结果
- 构建时自动克隆上游源码并应用翻译
- 使用 OpenAI 兼容 API 进行自动翻译
- 增量翻译：上游未变更的文件不会重复翻译

## 特性

- **自动翻译**：使用 LLM API 高质量翻译技术文档
- **增量更新**：基于文件内容 hash 的增量翻译，节省 API 费用
- **自动同步**：每日检测上游更新，自动翻译变更内容
- **双轨发布**：Nightly 自动构建 + 稳定版手动发布
- **术语一致**：通过术语表确保翻译一致性
- **兼容广泛**：支持任意 OpenAI 兼容 API 服务

## 翻译范围

| 优先级 | 内容 | 状态 |
|--------|------|------|
| P0 | 核心文档（README、CONTRIBUTING、AGENTS.md） | 进行中 |
| P0 | 文档站（website/docs/ ~70 个文件） | 进行中 |
| P1 | CLI 用户界面文本（banner、tips、setup 等） | 计划中 |
| P1 | Landing Page | 计划中 |
| P1 | GitHub Issue/PR 模板 | 计划中 |

## 快速开始

### 环境要求

- Python >= 3.11
- Git

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 配置
```

环境变量说明：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI 兼容 API 密钥 | （必填） |
| `OPENAI_BASE_URL` | API 基础地址 | `https://api.openai.com/v1` |
| `TRANSLATION_MODEL` | 翻译模型 | `gpt-4o` |
| `TRANSLATION_WORKERS` | 并发线程数 | `5` |
| `TRANSLATION_RPM` | 每分钟最大请求数 | `1000` |
| `TRANSLATION_TPM` | 每分钟最大 token 数 | `100000` |
| `TRANSLATION_TIMEOUT` | 单次 API 超时秒数 | `300` |

### 本地翻译

```bash
# 翻译所有待翻译文件（增量，5 线程并发，RPM+TPM 双限速）
python scripts/translate.py

# 强制重新翻译所有文件
python scripts/translate.py --force

# 只翻译指定文件
python scripts/translate.py --file README.md

# 自定义并发和限速（适配你的 API 套餐）
python scripts/translate.py --workers 5 --rpm 1000 --tpm 100000 --timeout 600

# 串行模式（调试用）
python scripts/translate.py --serial
```

### 构建中文版

```bash
# 克隆上游 + 应用翻译 + 构建
python scripts/build.py
```

### 检测上游变更

```bash
# 检测哪些文件需要重新翻译
python scripts/detect_changes.py
```

## 项目结构

```
hermes-agent-zh/
├── .github/workflows/       # CI/CD 工作流
├── translations/
│   ├── config.json          # 翻译主配置
│   ├── glossary.json        # 术语表
│   ├── .hash-cache.json     # 翻译缓存（自动生成）
│   ├── docs/                # 文档站翻译
│   ├── readme/              # 核心文档翻译
│   ├── cli/                 # CLI 文本翻译
│   ├── landing/             # Landing Page 翻译
│   └── github/              # GitHub 模板翻译
├── scripts/
│   ├── translate.py         # 翻译引擎
│   ├── apply.py             # 翻译应用
│   ├── detect_changes.py    # 变更检测
│   ├── verify.py            # 翻译验证
│   ├── extract_strings.py   # 字符串提取
│   └── build.py             # 构建脚本
└── ...
```

## 架构说明

本项目参考 [OpenClawChineseTranslation](https://github.com/1186258278/OpenClawChineseTranslation) 的翻译覆盖层架构：

1. **翻译覆盖层**：不 fork 上游，仓库只存翻译内容和自动化脚本
2. **构建时合并**：CI/CD 中克隆上游源码，将翻译覆盖上去
3. **增量翻译**：通过 SHA-256 hash 追踪文件变更，仅翻译变化的内容
4. **双轨发布**：
   - **Nightly**：每日自动检测上游 → 翻译变更 → 构建 → 发布
   - **Stable**：手动打 tag 触发稳定版发布

## 贡献

欢迎贡献翻译改进！请参阅上游项目 [CONTRIBUTING.md](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md)。

## 许可证

本项目遵循 [MIT License](LICENSE)，与上游项目保持一致。

## 致谢

- [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — 上游项目
- [OpenClawChineseTranslation](https://github.com/1186258278/OpenClawChineseTranslation) — 架构灵感来源
