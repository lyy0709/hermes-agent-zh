---
title: "地图 — 通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线、时区查询"
sidebar_label: "地图"
description: "通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线、时区查询"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 地图

通过 OpenStreetMap/OSRM 实现地理编码、兴趣点、路线、时区查询。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/maps` |
| 版本 | `1.2.0` |
| 作者 | Mibayy |
| 许可证 | MIT |
| 标签 | `maps`, `geocoding`, `places`, `routing`, `distance`, `directions`, `nearby`, `location`, `openstreetmap`, `nominatim`, `overpass`, `osrm` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 地图技能

使用免费、开放的数据源进行位置智能分析。8 个命令，44 个兴趣点类别，零依赖（仅使用 Python 标准库），无需 API 密钥。

数据源：OpenStreetMap/Nominatim、Overpass API、OSRM、TimeAPI.io。

此技能取代了旧的 `find-nearby` 技能 — `find-nearby` 的所有功能都由下面的 `nearby` 命令涵盖，并具有相同的 `--near "<place>"` 快捷方式和多类别支持。

## 使用时机

- 用户发送 Telegram 位置标记（消息中包含纬度/经度）→ `nearby`
- 用户想要某个地名的坐标 → `search`
- 用户有坐标并想要地址 → `reverse`
- 用户询问附近的餐厅、医院、药店、酒店等 → `nearby`
- 用户想要驾驶/步行/骑行的距离或旅行时间 → `distance`
- 用户想要两个地点之间的逐向导航 → `directions`
- 用户想要某个位置的时区信息 → `timezone`
- 用户想要搜索地理区域内的兴趣点 → `area` + `bbox`

## 先决条件

Python 3.8+（仅需标准库 — 无需 pip 安装）。

脚本路径：`~/.hermes/skills/maps/scripts/maps_client.py`

## 命令

```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
```

### search — 对地名进行地理编码

```bash
python3 $MAPS search "Eiffel Tower"
python3 $MAPS search "1600 Pennsylvania Ave, Washington DC"
```

返回：纬度、经度、显示名称、类型、边界框、重要性评分。

### reverse — 坐标转地址

```bash
python3 $MAPS reverse 48.8584 2.2945
```

返回：完整的地址细分（街道、城市、州、国家、邮政编码）。

### nearby — 按类别查找地点

```bash
# 通过坐标（例如，来自 Telegram 位置标记）
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10
python3 $MAPS nearby 40.7128 -74.0060 hospital --radius 2000

# 通过地址 / 城市 / 邮编 / 地标 — --near 自动进行地理编码
python3 $MAPS nearby --near "Times Square, New York" --category cafe
python3 $MAPS nearby --near "90210" --category pharmacy

# 多个类别合并到一个查询中
python3 $MAPS nearby --near "downtown austin" --category restaurant --category bar --limit 10
```

46 个类别：restaurant, cafe, bar, hospital, pharmacy, hotel, guest_house,
camp_site, supermarket, atm, gas_station, parking, museum, park, school,
university, bank, police, fire_station, library, airport, train_station,
bus_stop, church, mosque, synagogue, dentist, doctor, cinema, theatre, gym,
swimming_pool, post_office, convenience_store, bakery, bookshop, laundry,
car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground,
stadium, nightclub.

每个结果包括：`name`, `address`, `lat`/`lon`, `distance_m`,
`maps_url`（可点击的 Google 地图链接）, `directions_url`（从搜索点到该点的 Google 地图导航链接），以及可用的推广标签 —
`cuisine`, `hours` (opening_hours), `phone`, `website`.

### distance — 旅行距离和时间

```bash
python3 $MAPS distance "Paris" --to "Lyon"
python3 $MAPS distance "New York" --to "Boston" --mode driving
python3 $MAPS distance "Big Ben" --to "Tower Bridge" --mode walking
```

模式：driving（默认）, walking, cycling。返回道路距离、持续时间以及用于比较的直线距离。

### directions — 逐向导航

```bash
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking
python3 $MAPS directions "JFK Airport" --to "Times Square" --mode driving
```

返回带编号的步骤，包括指令、距离、持续时间、道路名称和操作类型（转弯、出发、到达等）。

### timezone — 坐标的时区

```bash
python3 $MAPS timezone 48.8584 2.2945
python3 $MAPS timezone 35.6762 139.6503
```

返回时区名称、UTC 偏移量和当前本地时间。

### area — 地点的边界框和面积

```bash
python3 $MAPS area "Manhattan, New York"
python3 $MAPS area "London"
```

返回边界框坐标、宽度/高度（公里）和近似面积。用作 bbox 命令的输入。

### bbox — 在边界框内搜索

```bash
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

查找地理矩形内的兴趣点。首先使用 `area` 获取命名地点的边界框坐标。

## 处理 Telegram 位置标记

当用户发送位置标记时，消息包含 `latitude:` 和 `longitude:` 字段。提取这些字段并直接传递给 `nearby`：

```bash
# 用户在 36.17, -115.14 发送了一个标记并询问“查找附近的咖啡馆”
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

将结果呈现为带编号的列表，包含名称、距离和 `maps_url` 字段，以便用户在聊天中获得可点击打开的链接。对于“现在开门吗？”这类问题，检查 `hours` 字段；如果缺失或不明确，请使用 `web_search` 验证，因为 OSM 的营业时间由社区维护，不一定是最新的。

## 工作流示例

**“查找罗马斗兽场附近的意大利餐厅”：**
1. `nearby --near "Colosseum Rome" --category restaurant --radius 500`
   — 一个命令，自动地理编码

**“他们发送的这个位置标记附近有什么？”：**
1. 从 Telegram 消息中提取纬度/经度
2. `nearby LAT LON cafe --radius 1500`

**“我从酒店步行到会议中心怎么走？”：**
1. `directions "Hotel Name" --to "Conference Center" --mode walking`

**“西雅图市中心有哪些餐厅？”：**
1. `area "Downtown Seattle"` → 获取边界框
2. `bbox S W N E restaurant --limit 30`

## 注意事项

- Nominatim 服务条款：最大 1 次请求/秒（脚本自动处理）
- `nearby` 需要纬度/经度 或 `--near "<address>"` — 两者之一必须提供
- OSRM 路线覆盖范围在欧洲和北美最佳
- Overpass API 在高峰时段可能较慢；脚本会自动在镜像之间回退（overpass-api.de → overpass.kumi.systems）
- `distance` 和 `directions` 使用 `--to` 标志指定目的地（非位置参数）
- 如果仅邮政编码在全球范围内产生歧义结果，请包含国家/州信息

## 验证

```bash
python3 ~/.hermes/skills/maps/scripts/maps_client.py search "Statue of Liberty"
# 应返回纬度 ~40.689，经度 ~-74.044

python3 ~/.hermes/skills/maps/scripts/maps_client.py nearby --near "Times Square" --category restaurant --limit 3
# 应返回时代广场约 500 米范围内的餐厅列表
```