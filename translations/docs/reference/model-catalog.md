---
sidebar_position: 11
title: 模型目录
description: 远程托管的清单，用于驱动 OpenRouter 和 Nous Portal 的精选模型选择器列表。
---

# 模型目录

Hermes 从与文档站点一同托管的 JSON 清单中获取 **OpenRouter** 和 **Nous Portal** 的精选模型列表。这使得维护者无需发布新的 `hermes-agent` 版本即可更新选择器列表。

当清单无法访问时（离线、网络被阻断、托管失败），Hermes 会静默回退到 CLI 附带的仓库内快照。清单永远不会破坏选择器——最坏的情况是你只能看到安装版本所捆绑的列表。

## 实时清单 URL

```
https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
```

每次合并到 `main` 分支时，通过现有的 `deploy-site.yml` GitHub Pages 流水线发布。权威来源位于仓库的 `website/static/api/model-catalog.json`。

## 模式

```json
{
  "version": 1,
  "updated_at": "2026-04-25T22:00:00Z",
  "metadata": {},
  "providers": {
    "openrouter": {
      "metadata": {},
      "models": [
        {"id": "moonshotai/kimi-k2.6", "description": "recommended", "metadata": {}},
        {"id": "openai/gpt-5.4",       "description": ""}
      ]
    },
    "nous": {
      "metadata": {},
      "models": [
        {"id": "anthropic/claude-opus-4.7"},
        {"id": "moonshotai/kimi-k2.6"}
      ]
    }
  }
}
```

字段说明：

- **`version`** — 整数模式版本。未来模式更新时会增加此值；Hermes 会拒绝无法理解的版本清单，并回退到硬编码的快照。
- **`metadata`** — 在清单、提供商和模型级别的自由格式字典。可以是任何键。Hermes 会忽略未知字段，因此你可以在不协调模式变更的情况下为条目添加注释（例如 `"tier": "paid"`、`"tags": [...]` 等）。
- **`description`** — 仅用于 OpenRouter。驱动选择器徽章文本（`"recommended"`、`"free"` 或空）。Nous Portal 不使用此字段——免费层限制由 Portal 的定价端点实时确定。
- **定价和上下文长度** 不在清单中。这些信息在获取时来自实时的提供商 API（`/v1/models` 端点，models.dev）。

## 获取行为

| 何时 | 发生什么 |
|---|---|
| `/model` 或 `hermes model` | 如果磁盘缓存已过期则获取，否则使用缓存 |
| 磁盘缓存新鲜（< TTL） | 不进行网络请求 |
| 网络失败但有缓存 | 静默回退到缓存，记录一行日志 |
| 网络失败，无缓存 | 静默回退到仓库内快照 |
| 清单模式验证失败 | 视为无法访问 |

缓存位置：`~/.hermes/cache/model_catalog.json`。

## 配置

```yaml
model_catalog:
  enabled: true
  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
  ttl_hours: 24
  providers: {}
```

设置 `enabled: false` 可以完全禁用远程获取，并始终使用仓库内快照。

### 按提供商覆盖 URL

第三方可以使用相同的模式自托管自己的精选列表。将提供商指向自定义 URL：

```yaml
model_catalog:
  providers:
    openrouter:
      url: https://example.com/my-openrouter-curation.json
```

覆盖清单只需要填充其关心的提供商块。其他提供商将继续根据主 URL 解析。

## 更新清单

维护者：

```bash
# 从仓库内硬编码列表重新生成（在编辑 hermes_cli/models.py 中的 OPENROUTER_MODELS 或 _PROVIDER_MODELS["nous"] 后保持清单同步）。
python scripts/build_model_catalog.py
```

然后将生成的更改 PR 到 `main` 分支的 `website/static/api/model-catalog.json`。文档站点在合并后会自动部署，新清单将在几分钟内生效。

你也可以直接手动编辑 JSON，进行不属于仓库内快照的细粒度元数据更改——生成脚本是为了方便，并非单一事实来源。