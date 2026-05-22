# 密钥管理

Hermes 可以在进程启动时从外部密钥管理器拉取 API 密钥，而不是将它们存储在 `~/.hermes/.env` 文件中。密钥管理器的引导 Token 存放在 `.env` 文件中；所有其他提供商密钥（OpenAI、Anthropic、OpenRouter 等）都可以保留在管理器中并进行集中轮换。

已支持：

- [Bitwarden Secrets Manager](./bitwarden) — `bws` CLI，按需安装，免费版可用。

更多后端（Vault、AWS Secrets Manager、1Password CLI）可以轻松地通过相同接口添加——只需在 `agent/secret_sources/` 目录中添加一个模块和一个 CLI 处理器即可。如果您有特定的需求，请提交请求。