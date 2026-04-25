---
title: "Solana"
sidebar_label: "Solana"
description: "查询附带美元定价的 Solana 区块链数据——钱包余额、带价值的代币投资组合、交易详情、NFT、巨鲸检测以及实时网络状态..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Solana

查询附带美元定价的 Solana 区块链数据——钱包余额、带价值的代币投资组合、交易详情、NFT、巨鲸检测以及实时网络状态。使用 Solana RPC + CoinGecko。无需 API 密钥。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/blockchain/solana` 安装 |
| 路径 | `optional-skills/blockchain/solana` |
| 版本 | `0.2.0` |
| 作者 | Deniz Alagoz (gizdusum)，由 Hermes Agent 增强 |
| 许可证 | MIT |
| 标签 | `Solana`, `Blockchain`, `Crypto`, `Web3`, `RPC`, `DeFi`, `NFT` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Solana 区块链技能

通过 CoinGecko 查询附带美元定价的 Solana 链上数据。
8 个命令：钱包投资组合、代币信息、交易、活动、NFT、巨鲸检测、网络状态和价格查询。

无需 API 密钥。仅使用 Python 标准库（urllib, json, argparse）。

---

## 使用时机

- 用户询问 Solana 钱包余额、代币持有量或投资组合价值时
- 用户想通过签名检查特定交易时
- 用户需要 SPL 代币元数据、价格、供应量或顶级持有者信息时
- 用户需要地址的近期交易历史时
- 用户想查看钱包拥有的 NFT 时
- 用户想查找大额 SOL 转账（巨鲸检测）时
- 用户需要 Solana 网络健康状况、TPS、纪元或 SOL 价格时
- 用户询问“BONK/JUP/SOL 的价格是多少？”时

---

## 先决条件

辅助脚本仅使用 Python 标准库（urllib, json, argparse）。
无需外部包。

定价数据来自 CoinGecko 的免费 API（无需密钥，速率限制约为每分钟 10-30 次请求）。如需更快查询，请使用 `--no-prices` 标志。

---

## 快速参考

RPC 端点（默认）：https://api.mainnet-beta.solana.com
覆盖方法：export SOLANA_RPC_URL=https://your-private-rpc.com

辅助脚本路径：~/.hermes/skills/blockchain/solana/scripts/solana_client.py

```
python3 solana_client.py wallet   <地址> [--limit N] [--all] [--no-prices]
python3 solana_client.py tx       <签名>
python3 solana_client.py token    <铸币地址>
python3 solana_client.py activity <地址> [--limit N]
python3 solana_client.py nft      <地址>
python3 solana_client.py whales   [--min-sol N]
python3 solana_client.py stats
python3 solana_client.py price    <铸币地址或符号>
```

---

## 操作流程

### 0. 设置检查

```bash
python3 --version

# 可选：设置私有 RPC 以获得更好的速率限制
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# 确认连接性
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 1. 钱包投资组合

获取 SOL 余额、附带美元价值的 SPL 代币持有量、NFT 数量以及投资组合总值。代币按价值排序，过滤小额代币，已知代币按名称（BONK, JUP, USDC 等）标记。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

标志：
- `--limit N` — 显示前 N 个代币（默认：20）
- `--all` — 显示所有代币，不过滤小额代币，无限制
- `--no-prices` — 跳过 CoinGecko 价格查询（更快，仅使用 RPC）

输出包括：SOL 余额 + 美元价值、按价值排序的代币列表及价格、小额代币数量、NFT 摘要、以美元计的总投资组合价值。

### 2. 交易详情

通过其 base58 签名检查完整交易。显示 SOL 和美元两种单位的余额变化。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  tx 5j7s8K...your_signature_here
```

输出：区块、时间戳、手续费、状态、余额变化（SOL + 美元）、程序调用。

### 3. 代币信息

获取 SPL 代币元数据、当前价格、市值、供应量、小数位数、铸币/冻结权限以及前 5 名持有者。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  token DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

输出：名称、符号、小数位数、供应量、价格、市值、前 5 名持有者及其百分比。

### 4. 近期活动

列出地址的近期交易（默认：最近 10 笔，最多：25 笔）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  activity 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --limit 25
```

### 5. NFT 投资组合

列出钱包拥有的 NFT（启发式方法：数量=1 且小数位数=0 的 SPL 代币）。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  nft 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

注意：压缩 NFT（cNFT）无法通过此启发式方法检测到。

### 6. 巨鲸检测器

扫描最新区块中的大额 SOL 转账及其美元价值。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py \
  whales --min-sol 500
```

注意：仅扫描最新区块——是时间点快照，非历史数据。

### 7. 网络状态

实时 Solana 网络健康状况：当前区块、纪元、TPS、供应量、验证器版本、SOL 价格和市值。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```

### 8. 价格查询

通过铸币地址或已知符号快速查询任何代币的价格。

```bash
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price BONK
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price JUP
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price SOL
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py price DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

已知符号：SOL, USDC, USDT, BONK, JUP, WETH, JTO, mSOL, stSOL, PYTH, HNT, RNDR, WEN, W, TNSR, DRIFT, bSOL, JLP, WIF, MEW, BOME, PENGU。

---

## 注意事项

- **CoinGecko 速率限制** — 免费层级允许每分钟约 10-30 次请求。价格查询每个代币使用 1 次请求。持有大量代币的钱包可能无法获取所有代币的价格。如需速度，请使用 `--no-prices`。
- **公共 RPC 速率限制** — Solana 主网公共 RPC 限制请求次数。生产环境使用，请将 SOLANA_RPC_URL 设置为私有端点（Helius, QuickNode, Triton）。
- **NFT 检测是启发式的** — 数量=1 + 小数位数=0。压缩 NFT（cNFT）和 Token-2022 NFT 不会出现。
- **巨鲸检测器仅扫描最新区块** — 非历史数据。结果因查询时刻而异。
- **交易历史** — 公共 RPC 保留约 2 天。较早的交易可能无法获取。
- **代币名称** — 约 25 个知名代币按名称标记。其他代币显示缩写的铸币地址。使用 `token` 命令获取完整信息。
- **429 错误重试** — RPC 和 CoinGecko 调用在遇到速率限制错误时，最多重试 2 次，并采用指数退避策略。

---

## 验证

```bash
# 应打印当前 Solana 区块、TPS 和 SOL 价格
python3 ~/.hermes/skills/blockchain/solana/scripts/solana_client.py stats
```