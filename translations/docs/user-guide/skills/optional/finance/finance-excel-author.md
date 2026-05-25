---
title: "Excel 文件生成器"
sidebar_label: "Excel 文件生成器"
description: "使用 openpyxl 无头构建可审计的 Excel 工作簿——蓝/黑/绿单元格约定、使用公式而非硬编码、命名范围、平衡检查、敏感性分析表。适用于财务模型、审计输出、对账。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。*/}

# Excel 文件生成器

使用 `openpyxl` 无头生成 .xlsx 文件。遵循以下银行级约定，使模型可审计、灵活且可供构建者以外的人员审阅。

改编自 Anthropic 在 [anthropics/financial-services](https://github.com/anthropics/financial-services) 仓库中的 `xlsx-author` 和 `audit-xls` 技能。移除了原始版本中特定于 MCP / Office-JS / Cowork 的分支——此技能假设为无头 Python 环境。

## 输出约定

-   写入 `./out/<名称>.xlsx`。如果 `./out/` 不存在则创建它。
-   在最终消息中返回相对路径，以便下游工具可以拾取。
-   每个文件一个逻辑模型。除非明确要求，否则不要追加到现有工作簿。

## 设置

```bash
pip install "openpyxl>=3.0"
```

## 核心约定（不可协商）

### 蓝 / 黑 / 绿单元格颜色
-   **蓝色** (`Font(color="0000FF")`) — 人工输入的硬编码假设。收入驱动因素、WACC 输入、终值增长率、市场数据。
-   **黑色** (默认) — 公式。每个衍生单元格都是一个活动的 Excel 公式。
-   **绿色** (`Font(color="006100")`) — 链接到另一个工作表或外部文件。

审阅者可以扫描工作表，立即区分哪些是假设，哪些是计算结果。

### 使用公式而非硬编码
每个计算单元格**必须**是公式字符串，绝不能是在 Python 中计算并作为值粘贴的数字。

```python
# 错误 —— 等待发生的静默错误
ws["D20"] = revenue_prior_year * (1 + growth)

# 正确 —— 当用户更改假设时，公式会随之调整
ws["D20"] = "=D19*(1+$B$8)"
```

唯一允许的硬编码数字：
1.  原始历史输入（实际收入、报告的 EBITDA 等）
2.  用户需要调整的假设驱动因素（增长率、WACC 输入、终值增长率 g）
3.  当前市场数据（股价、债务余额）—— 附带单元格批注，记录来源和日期

如果你发现自己在 Python 中计算一个值并写入结果，请停止。

### 跨工作表引用使用命名范围
对于从另一个工作表、演示文稿或备忘录引用的任何数字，请使用命名范围。

```python
from openpyxl.workbook.defined_name import DefinedName
wb.defined_names["WACC"] = DefinedName("WACC", attr_text="Inputs!$C$8")
# 然后在其他地方：
calc["D30"] = "=D29/WACC"
```

### 平衡检查工作表
包含一个 `Checks` 工作表，用于关联所有内容并显示 TRUE/FALSE：
-   资产负债表平衡（资产 = 负债 + 所有者权益）
-   现金流量表与资产负债表上期间现金变动相匹配
-   分部加总与合并总额相匹配
-   计算范围内没有杂散的硬编码

示例：
```python
checks = wb.create_sheet("Checks")
checks["A2"] = "资产负债表平衡"
checks["B2"] = "=IS!D20-IS!D21-IS!D22"
checks["C2"] = "=ABS(B2)<0.01"  # TRUE/FALSE
```

### 每个硬编码输入都添加单元格批注
在创建单元格时**立即**添加批注，而不是之后。

```python
from openpyxl.comments import Comment
ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")
ws["C2"].comment = Comment("来源：10-K FY2024，第47页，收入行", "分析师")
```

格式：`来源：[系统/文档]，[日期]，[参考]，[URL（如果适用）]`。

切勿推迟记录来源。切勿写入 `待办：添加来源`。

## 框架：典型的财务模型

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from pathlib import Path

BLUE = Font(color="0000FF")
BLACK = Font(color="000000")
GREEN = Font(color="006100")
BOLD = Font(bold=True)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)

wb = Workbook()

# --- 输入工作表 ---
inp = wb.active
inp.title = "输入"
inp["A1"] = "市场数据与关键输入"
inp["A1"].font = HEADER_FONT
inp["A1"].fill = HEADER_FILL
inp.merge_cells("A1:C1")

inp["B3"] = "收入 FY2024"
inp["C3"] = 1_250_000_000
inp["C3"].font = BLUE
inp["C3"].comment = Comment("来源：10-K FY2024 第47页", "模型")

inp["B4"] = "增长率"
inp["C4"] = 0.12
inp["C4"].font = BLUE

# --- 计算工作表 ---
calc = wb.create_sheet("DCF")
calc["B2"] = "预计收入"
calc["C2"] = "=输入!C3*(1+输入!C4)"   # 公式，黑色

# --- 检查工作表 ---
chk = wb.create_sheet("检查")
chk["A2"] = "资产负债表平衡"
chk["B2"] = "=ABS(资产负债表!D20-资产负债表!D21-资产负债表!D22)<0.01"

Path("./out").mkdir(exist_ok=True)
wb.save("./out/model.xlsx")
```

## 带合并单元格的章节标题

openpyxl 的注意事项：合并单元格时，在左上角单元格设置值，并单独设置整个范围的样式。

```python
ws["A7"] = "现金流量预测"
ws["A7"].font = HEADER_FONT
ws.merge_cells("A7:H7")
for col in range(1, 9):  # A..H
    ws.cell(row=7, column=col).fill = HEADER_FILL
```

## 敏感性分析表

使用循环构建，而不是每个单元格硬编码公式。规则：

-   **行/列数为奇数**（5×5 或 7×7）—— 确保有一个真正的中心单元格。
-   **中心单元格 = 基准情况。** 中间行/列的标题必须等于模型的实际 WACC 和终值增长率 g，这样中心输出才等于基准情况的隐含股价。这是完整性检查。
-   **突出显示中心单元格**，使用中蓝色填充 (`"BDD7EE"`) 和加粗字体。
-   用完整的重新计算公式填充每个单元格——绝不能是近似值。

```python
# 5x5 WACC（行）x 终值增长率（列）敏感性分析
wacc_axis = [0.08, 0.085, 0.09, 0.095, 0.10]        # 中间行 = 基准 9.0%
term_axis = [0.02, 0.025, 0.03, 0.035, 0.04]        # 中间列 = 基准 3.0%

start_row = 40
ws.cell(row=start_row, column=1).value = "隐含股价 ($)"
ws.cell(row=start_row, column=1).font = BOLD

for j, g in enumerate(term_axis):
    ws.cell(row=start_row+1, column=2+j).value = g
    ws.cell(row=start_row+1, column=2+j).font = BLUE

for i, w in enumerate(wacc_axis):
    r = start_row + 2 + i
    ws.cell(row=r, column=1).value = w
    ws.cell(row=r, column=1).font = BLUE
    for j, g in enumerate(term_axis):
        c = 2 + j
        # 完整的 DCF 重新计算公式（为说明而简化）。
        # 在实际模型中，这会引用完整的预测块。
        ws.cell(row=r, column=c).value = (
            f"=SUMPRODUCT(FCF_range,1/(1+{w})^year_offset) + "
            f"FCF_terminal*(1+{g})/({w}-{g})/(1+{w})^terminal_year"
        )

# 突出显示中心单元格（基准情况）
center = ws.cell(row=start_row+2+len(wacc_axis)//2,
                 column=2+len(term_axis)//2)
center.fill = PatternFill("solid", fgColor="BDD7EE")
center.font = BOLD
```

## 交付前重新计算

openpyxl 写入公式字符串但不计算它们。Excel 在打开时会重新计算，但下游消费者（自动检查脚本、CI）需要计算后的值。

在交付前运行 LibreOffice 或专用的重新计算步骤：

```bash
# LibreOffice 无头重新计算
libreoffice --headless --calc --convert-to xlsx ./out/model.xlsx --outdir ./out/
```

或者使用 Python 重新计算辅助工具（参见此技能中的 `scripts/recalc.py`）。

## 模型布局规划

在编写任何公式之前：
1.  定义**所有**章节的行位置
2.  编写**所有**标题和标签
3.  编写**所有**章节分隔符和空行
4.  **然后**使用锁定的行位置编写公式

这可以防止在公式编写后插入标题行导致每个下游引用偏移的级联公式破坏模式。

## 与用户逐步验证

对于大型模型（DCF、三张报表、LBO），在继续之前停下来向用户展示中间产物。在构建下游敏感性分析表之前发现错误的利润率假设可以节省一个小时。

检查点模式：
-   输入块之后 → 显示原始输入，在预测前确认
-   收入预测之后 → 确认收入总额和增长率
-   FCF 构建之后 → 确认完整的计划表
-   WACC 之后 → 确认输入
-   估值之后 → 确认权益桥接
-   **然后**构建敏感性分析表

## 何时不应使用此技能

-   用户处于实时 Excel 会话中且有 Office MCP 可用时 —— 直接驱动他们的实时工作簿。
-   纯表格数据导出，无公式 —— `csv` 或 `pandas.to_excel` 更简单。
-   具有大量交互性的仪表板/图表 —— 使用真正的 BI 工具。

## 归属

约定（蓝/黑/绿、公式优于硬编码、命名范围、敏感性分析规则）改编自 Anthropic 的 Claude for Financial Services 插件套件，Apache-2.0 许可。原始来源：https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/xlsx-author