---
title: "Hyperliquid — Hyperliquid 市场数据、账户历史、交易回顾"
sidebar_label: "Hyperliquid"
description: "Hyperliquid 市场数据、账户历史、交易回顾"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Hyperliquid

Hyperliquid 市场数据、账户历史、交易回顾。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/blockchain/hyperliquid` 安装 |
| 路径 | `optional-skills/blockchain/hyperliquid` |
| 版本 | `0.1.0` |
| 作者 | Hugo Sequier (Hugo-SEQUIER), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Hyperliquid`, `Blockchain`, `Crypto`, `Trading`, `Perpetuals`, `Spot`, `DeFi` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Hyperliquid 技能

通过公共 `/info` 端点查询 Hyperliquid 市场和账户数据。
只读 — 无需 API 密钥，无需签名，不下单。

12 个命令：`dexs`, `markets`, `spots`, `candles`, `funding`, `l2`, `state`,
`spot-balances`, `fills`, `orders`, `review`, `export`。仅使用标准库
(`urllib`, `json`, `argparse`)。

---

## 使用时机

- 用户询问 Hyperliquid 永续或现货市场数据、K线、资金费率或 L2 订单簿
- 用户想要检查钱包的永续仓位、现货余额、成交记录或订单
- 用户想要结合近期成交记录与市场背景进行交易后回顾
- 用户想要检查构建器部署的永续 DEX 或 HIP-3 市场
- 用户想要用于回测准备的 K线 + 资金费率标准化 JSON 导出

---

## 前提条件

仅需标准库 — 无需外部包，无需 API 密钥。

脚本会读取 `~/.hermes/.env` 获取两个可选的默认值：

- `HYPERLIQUID_API_URL` — 默认为 `https://api.hyperliquid.xyz`。可设置为
  `https://api.hyperliquid-testnet.xyz` 以使用测试网。
- `HYPERLIQUID_USER_ADDRESS` — `state`、`spot-balances`、`fills`、`orders` 和 `review` 命令的默认地址。如果未设置，请将地址作为第一个位置参数传入。

当前工作目录中的项目 `.env` 文件将作为开发备用配置。

辅助脚本：`~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py`

---

## 如何运行

通过 `terminal` 工具调用：

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py <command> [args]
```

在任何命令后添加 `--json` 以获取机器可读的输出。

---

## 快速参考

```bash
hyperliquid_client.py dexs
hyperliquid_client.py markets [--dex DEX] [--limit N] [--sort volume|oi|funding_abs|change_abs|name]
hyperliquid_client.py spots [--limit N]
hyperliquid_client.py candles <coin> [--interval 1h] [--hours 24] [--limit N]
hyperliquid_client.py funding <coin> [--hours 72] [--limit N]
hyperliquid_client.py l2 <coin> [--levels N]
hyperliquid_client.py state [address] [--dex DEX]
hyperliquid_client.py spot-balances [address] [--limit N]
hyperliquid_client.py fills [address] [--hours N] [--limit N] [--aggregate-by-time]
hyperliquid_client.py orders [address] [--limit N]
hyperliquid_client.py review [address] [--coin COIN] [--hours N] [--fills N]
hyperliquid_client.py export <coin> [--interval 1h] [--hours N] [--output PATH]
```

对于 `state`、`spot-balances`、`fills`、`orders` 和 `review` 命令，当 `~/.hermes/.env` 中设置了 `HYPERLIQUID_USER_ADDRESS` 时，地址参数是可选的。

---

## 操作流程

### 1. 发现 DEX 和市场

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py dexs

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 15 --sort volume

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spots --limit 15
```

- `--dex` 仅适用于永续端点；对于第一个永续 DEX，可省略。
- 现货交易对可能显示为 `PURR/USDC` 或别名如 `@107`。
- HIP-3 市场在币种前加上 DEX 前缀，例如 `mydex:BTC`。

### 2. 拉取历史市场数据

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  candles BTC --interval 1h --hours 72 --limit 48

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  funding BTC --hours 168 --limit 30
```

时间范围端点支持分页。对于更大的时间窗口，使用更晚的 `startTime` 重复调用或使用 `export` 命令（见下文）。

### 3. 检查实时订单簿

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  l2 BTC --levels 10
```

当被问及订单簿深度、近期流动性或大订单的潜在市场影响时使用。

### 4. 查看账户

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  state 0xabc...

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  spot-balances
```

`state` 返回永续仓位；`spot-balances` 返回现货库存。
用于回答“我的仓位如何？”、“我持有什么？”、“可提取多少？”等问题。

### 5. 查看成交记录和订单

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  fills 0xabc... --hours 72 --limit 25

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  orders --limit 25
```

### 6. 生成交易回顾

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review 0xabc... --hours 72 --fills 50

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  review --coin BTC --hours 168
```

报告已实现盈亏、手续费、胜/负交易次数、币种细分、每个交易永续币种的市场趋势和平均资金费率，以及启发式分析（手续费拖累、集中度、逆势亏损）。

要进行更深入的交易后分析：从 `review` 开始，找出问题币种或时间段 → 拉取该时间段的 `fills` 和 `orders` → 拉取每个交易币种的 `candles` 和 `funding` → 分别评估决策质量与结果质量。

### 7. 导出可复用的数据集

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 1h --hours 168 --output ./btc-1h-7d.json

python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  export BTC --interval 15m --hours 72 --end-time-ms 1760000000000
```

输出的 JSON 包含：模式版本、来源元数据、精确时间窗口、标准化的 K线行、标准化的资金费率行、汇总统计信息。使用 `--end-time-ms` 以获得可复现的时间窗口。

---

## 注意事项

- 公共信息端点有速率限制。大型历史查询可能返回截断的时间窗口；使用更晚的 `startTime` 值进行迭代。
- `fills --hours ...` 使用 `userFillsByTime`，它只暴露最近的一个滚动窗口 — 不是完整的存档历史。
- `historicalOrders` 仅返回最近的订单；不是完整导出。
- `review` 命令是启发式的。它无法仅从成交记录中重建意图、订单放置质量或真实滑点。
- `export` 命令写入标准化的数据集，而不是回测引擎。你仍然需要自己的滑点/成交模型。
- 像 `@107` 这样的现货别名是有效的标识符，即使 UI 显示的是更友好的名称。
- `l2` 是时间点快照，不是时间序列。

---

## 验证

```bash
python3 ~/.hermes/skills/blockchain/hyperliquid/scripts/hyperliquid_client.py \
  markets --limit 5
```

应打印按 24 小时名义交易量排名的前 5 个 Hyperliquid 永续市场。