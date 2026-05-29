---
title: "Pptx Author — 使用 python-pptx 无头构建 PowerPoint 演示文稿"
sidebar_label: "Pptx Author"
description: "使用 python-pptx 无头构建 PowerPoint 演示文稿"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pptx Author

使用 python-pptx 无头构建 PowerPoint 演示文稿。可与 excel-author 技能搭配使用，创建每个数字都能追溯到工作簿单元格的模型驱动演示文稿。适用于推介演示文稿、投资委员会备忘录、财报说明。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/finance/pptx-author` 安装 |
| 路径 | `optional-skills/finance/pptx-author` |
| 版本 | `1.0.0` |
| 作者 | Anthropic (由 Nous Research 改编) |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `powerpoint`, `pptx`, `python-pptx`, `presentation`, `finance` |
| 相关技能 | [`excel-author`](/docs/user-guide/skills/optional/finance/finance-excel-author), [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# pptx-author

使用 `python-pptx` 在磁盘上生成 .pptx 文件。当您需要交付演示文稿作为文件产物，而不是驱动实时 PowerPoint 会话时使用。

改编自 Anthropic 在 [anthropics/financial-services](https://github.com/anthropics/financial-services) 中的 `pptx-author` 和 `pitch-deck` 技能。原始版本中的 MCP / Office-JS 分支已被移除——此技能假定使用无头 Python。

对于更广泛、已内置的 PowerPoint 创作技能（幻灯片、演讲者备注、嵌入、媒体），请参阅内置的 `powerpoint` 技能。此技能是一个更轻量级的模式，专为模型驱动的演示文稿（推介演示文稿、投资委员会备忘录、财报说明）调整，其中每个数字都必须追溯到源工作簿。

## 输出约定

- 写入 `./out/<名称>.pptx`。如果 `./out/` 不存在，则创建它。
- 在您的最终消息中返回相对路径。

## 设置

```bash
pip install "python-pptx>=0.6"
```

## 核心约定

### 每张幻灯片一个核心观点
标题陈述要点；正文提供支持。标题为 "Q3 Revenue" 的幻灯片较弱；"Revenue growth accelerated to 14% Y/Y in Q3" 则较强。

### 每个数字都追溯到模型
如果幻灯片上的数字来自 `./out/model.xlsx`，请用脚注注明工作表和单元格。

```
Revenue: $1,250M  (Source: model.xlsx, Inputs!C3)
```

切勿凭记忆或摘要转录数字——打开工作簿，读取命名范围，并在可能的情况下以编程方式将演示文稿中的值绑定到该范围。

### 当挂载了公司模板时使用它
如果 `./templates/firm-template.pptx` 存在，则加载它，以便演示文稿继承品牌颜色、字体和母版布局。

```python
from pptx import Presentation
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()
```

### 图表：来自模型的 PNG 优于原生 pptx 图表
当保真度很重要时（模型的图表样式必须与演示文稿完全匹配），请从源工作簿将图表渲染为 PNG 并嵌入图像。原生的 `pptx.chart` 图表很脆弱，并且通常不符合公司惯例。

```python
from pptx.util import Inches
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(2),
                         width=Inches(8))
```

### 无外部发送
此技能仅写入文件。它从不发送电子邮件、上传或发布。编排层负责交付。

## 骨架代码

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()

# 标题幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Project Aurora — Strategic Alternatives"
slide.placeholders[1].text = "Preliminary Discussion Materials"

# 估值摘要幻灯片（仅标题布局）
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Valuation implies $38–$52 per share across methodologies"

# 添加一个绑定到模型输出的表格
rows, cols = 5, 4
tbl_shape = slide.shapes.add_table(rows, cols,
                                   Inches(0.5), Inches(1.5),
                                   Inches(9), Inches(3))
tbl = tbl_shape.table
headers = ["Methodology", "Low ($)", "Mid ($)", "High ($)"]
for c, h in enumerate(headers):
    tbl.cell(0, c).text = h

# 在实际演示文稿中，使用 openpyxl 从模型工作簿读取这些数据
data = [
    ("Trading comps",     "35", "41", "48"),
    ("Precedent M&A",     "39", "45", "52"),
    ("DCF (base)",        "36", "43", "51"),
    ("LBO (10% IRR)",     "33", "38", "44"),
]
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        tbl.cell(r, c).text = val

# 嵌入从模型渲染的图表
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Football field — current price $42"
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(1.8), width=Inches(8))

Path("./out").mkdir(exist_ok=True)
prs.save("./out/pitch-aurora.pptx")
```

## 将演示文稿数字绑定到源工作簿

从您的 Excel 模型中读取命名范围或特定单元格，以确保演示文稿中的数字永不漂移。

```python
from openpyxl import load_workbook

wb = load_workbook("./out/model.xlsx", data_only=True)
def nr(name):
    """将命名范围解析为其当前计算值。"""
    rng = wb.defined_names[name]
    sheet, coord = next(rng.destinations)
    return wb[sheet][coord].value

revenue_fy24 = nr("RevenueFY24")
implied_mid  = nr("ImpliedSharePriceBase")
```

然后使用这些值构建演示文稿内容：
```python
slide.shapes.title.text = f"Implied share price of ${implied_mid:.2f} (base case)"
```

请记住，在读取工作簿之前重新计算它——只有当某些内容已经计算过工作表时，openpyxl 才能看到计算值。请先运行 `excel-author` 技能中的重新计算辅助函数，或通过真实的 Excel 会话打开/保存。

## 推介演示文稿的幻灯片类型清单

典型的银行推介演示文稿遵循此结构。并非规定性要求，但可作为起始骨架：

1. 封面 / 标题
2. 免责声明
3. 目录
4. 情况概述
5. 公司概况（目标公司）
6. 市场 / 行业背景
7. 估值摘要（足球场图）—— 核心幻灯片
8. 交易可比公司详情
9. 先例交易详情
10. DCF 摘要
11. 示例性 LBO / 赞助商案例
12. 流程考虑因素
13. 附录

## 何时不应使用此技能

- 用户处于实时 PowerPoint 会话中且 Office MCP 可用时——改为驱动他们的实时文档。
- 非财务幻灯片（季度全员会议、营销演示文稿）——使用更广泛的 `powerpoint` 技能。
- 具有大量动画、过渡或演讲者备注的演示文稿——使用更广泛的 `powerpoint` 技能。

## 归属

约定改编自 Anthropic 的 Claude for Financial Services 插件套件，Apache-2.0 许可证。原始来源：https://github.com/anthropics/financial-services/tree/main/plugins/agent-plugins/pitch-agent/skills/pptx-author