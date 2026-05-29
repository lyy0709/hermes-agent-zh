---
title: "Stocks — 通过 Yahoo 获取股票报价、历史数据、搜索、对比和加密货币信息"
sidebar_label: "Stocks"
description: "通过 Yahoo 获取股票报价、历史数据、搜索、对比和加密货币信息"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Stocks

通过 Yahoo 获取股票报价、历史数据、搜索、对比和加密货币信息。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/finance/stocks` 安装 |
| 路径 | `optional-skills/finance/stocks` |
| 版本 | `0.1.0` |
| 作者 | Mibay (Mibayy), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Stocks`, `Finance`, `Market`, `Crypto`, `Investing` |
| 相关技能 | [`dcf-model`](/docs/user-guide/skills/optional/finance/finance-dcf-model), [`comps-analysis`](/docs/user-guide/skills/optional/finance/finance-comps-analysis), [`lbo-model`](/docs/user-guide/skills/optional/finance/finance-lbo-model) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Stocks 技能

通过 Yahoo Finance 获取只读市场数据。包含五个命令：`quote`、`search`、`history`、`compare`、`crypto`。仅使用 Python 标准库 — 无需 API 密钥，无需 pip 安装。Yahoo 的端点是非官方的，可能会进行速率限制或发生变更。

## 使用场景

- 用户询问当前股票价格（AAPL、TSLA、MSFT 等）
- 用户希望通过公司名称查找股票代码
- 用户需要特定日期范围内的 OHLCV 历史数据或表现
- 用户希望并排比较多个股票代码
- 用户询问加密货币价格（BTC、ETH、SOL 等）

## 先决条件

仅需 Python 3.8+ 标准库。可选：设置 `ALPHA_VANTAGE_KEY` 环境变量，以便在 Yahoo 受 crumb 保护的字段返回 null 时，补充 `market_cap`、`pe_ratio` 和 52 周高低点数据。免费密钥：https://www.alphavantage.co/support/#api-key

## 如何运行

通过 `terminal` 工具调用。安装后：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL
```

所有输出均为 JSON 格式到 stdout — 如需筛选，可通过 `jq` 管道处理。

## 快速参考

```
python3 $SCRIPT quote AAPL
python3 $SCRIPT quote AAPL MSFT GOOGL TSLA
python3 $SCRIPT search "Tesla"
python3 $SCRIPT history NVDA --range 6mo
python3 $SCRIPT compare AAPL MSFT GOOGL
python3 $SCRIPT crypto BTC ETH SOL
```

## 命令

### `quote SYMBOL [SYMBOL2 ...]`

获取当前价格、涨跌额、涨跌幅、成交量、52 周最高/最低价。

### `search QUERY`

通过公司名称查找股票代码。返回前 5 个结果：代码、名称、交易所、类型。

### `history SYMBOL [--range RANGE]`

获取每日 OHLCV 数据及统计信息（最小值、最大值、平均值、总回报率百分比）。范围：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认：`1mo`。

### `compare SYMBOL1 SYMBOL2 [...]`

并排比较：价格、涨跌幅、52 周表现。

### `crypto SYMBOL [SYMBOL2 ...]`

获取加密货币价格。传递 `BTC`（脚本会自动追加 `-USD`）。

## 注意事项

- Yahoo Finance 的 API 是非官方的。端点可能未经通知就发生变更或进行速率限制 — 如果请求开始失败，这就是原因。
- 当 Yahoo 的 crumb 会话未建立时，`quote` 命令的 `market_cap` 和 `pe_ratio` 可能返回 null。设置 `ALPHA_VANTAGE_KEY` 以进行数据回填。
- 批量请求之间请添加少量延迟，以避免触发速率限制。
- 此为只读技能 — 无法下单，无账户集成。

## 验证

```
python3 ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

返回一个包含 `symbol: "AAPL"` 和数值型 `price` 字段的 JSON 对象。