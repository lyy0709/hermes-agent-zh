---
title: "概念图"
sidebar_label: "概念图"
description: "生成扁平、极简、支持明暗模式的SVG图表，作为独立的HTML文件，采用统一的教育视觉语言，包含9种语义色阶、句子大小写排版和自动深色模式。最适合教育和非软件可视化——物理装置、化学机制、数学曲线、物理对象（飞机、涡轮机、智能手机、机械手表）、解剖结构、平面图、剖面图、叙事旅程（X的生命周期、Y的过程）、中心辐射型系统集成（智慧城市、物联网）以及爆炸图层视图。如果存在针对该主题的更专业技能（专门的软件/云架构、手绘草图、动画解释等），请优先使用——否则此技能也可作为具有简洁教育外观的通用SVG图表备用方案。附带15个示例图表。"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 概念图

生成扁平、极简、支持明暗模式的SVG图表，作为独立的HTML文件，采用统一的教育视觉语言，包含9种语义色阶、句子大小写排版和自动深色模式。最适合教育和非软件可视化——物理装置、化学机制、数学曲线、物理对象（飞机、涡轮机、智能手机、机械手表）、解剖结构、平面图、剖面图、叙事旅程（X的生命周期、Y的过程）、中心辐射型系统集成（智慧城市、物联网）以及爆炸图层视图。如果存在针对该主题的更专业技能（专门的软件/云架构、手绘草图、动画解释等），请优先使用——否则此技能也可作为具有简洁教育外观的通用SVG图表备用方案。附带15个示例图表。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/concept-diagrams` 安装 |
| 路径 | `optional-skills/creative/concept-diagrams` |
| 版本 | `0.1.0` |
| 作者 | v1k22 (原始 PR)，移植到 hermes-agent |
| 许可证 | MIT |
| 标签 | `diagrams`, `svg`, `visualization`, `education`, `physics`, `chemistry`, `engineering` |
| 相关技能 | [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), `generative-widgets` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 概念图

使用统一的扁平、极简设计系统生成生产质量的SVG图表。输出是单个自包含的HTML文件，在任何现代浏览器中渲染效果一致，并支持自动明暗模式。

## 范围

**最适合用于：**
- 物理装置、化学机制、数学曲线、生物学
- 物理对象（飞机、涡轮机、智能手机、机械手表、细胞）
- 解剖结构、剖面图、爆炸图层视图
- 平面图、建筑转换
- 叙事旅程（X的生命周期、Y的过程）
- 中心辐射型系统集成（智慧城市、物联网网络、电网）
- 任何领域的教育/教科书风格可视化
- 定量图表（分组条形图、能量分布图）

**以下情况请优先考虑其他技能：**
- 具有深色科技美学的专门软件/云基础设施架构（如果可用，考虑 `architecture-diagram`）
- 手绘白板草图（如果可用，考虑 `excalidraw`）
- 动画解释器或视频输出（考虑动画技能）

如果存在针对该主题的更专业技能，请优先使用。如果没有合适的，此技能可作为通用SVG图表备用方案——输出将采用下文描述的简洁教育美学，这几乎是任何主题的合理默认选择。

## 工作流程

1.  确定图表类型（见下文图表类型）。
2.  使用设计系统规则布局组件。
3.  使用 `templates/template.html` 作为包装器编写完整的HTML页面——将你的SVG粘贴到模板中 `<!-- PASTE SVG HERE -->` 的位置。
4.  保存为独立的 `.html` 文件（例如 `~/my-diagram.html` 或 `./my-diagram.html`）。
5.  用户直接在浏览器中打开——无需服务器，无依赖项。

可选：如果用户想要浏览多个图表的画廊，请查看底部的“本地预览服务器”。

加载HTML模板：
```
skill_view(name="concept-diagrams", file_path="templates/template.html")
```

模板嵌入了完整的CSS设计系统（`c-*` 颜色类、文本类、明暗模式变量、箭头标记样式）。你生成的SVG依赖于承载页面上存在的这些类。

---

## 设计系统

### 理念

- **扁平化**：无渐变、投影、模糊、发光或霓虹效果。
- **极简**：展示本质。框内无装饰性图标。
- **一致**：所有图表使用相同的颜色、间距、排版和描边宽度。
- **支持深色模式**：所有颜色通过CSS类自动适配——无需针对每种模式的SVG。

### 调色板

9种色阶，每种包含7个色阶。将类名放在 `<g>` 或形状元素上；模板CSS处理两种模式。

| 类名       | 50 (最浅) | 100    | 200    | 400    | 600    | 800    | 900 (最深) |
|------------|-----------|--------|--------|--------|--------|--------|------------|
| `c-purple` | #EEEDFE | #CECBF6 | #AFA9EC | #7F77DD | #534AB7 | #3C3489 | #26215C |
| `c-teal`   | #E1F5EE | #9FE1CB | #5DCAA5 | #1D9E75 | #0F6E56 | #085041 | #04342C |
| `c-coral`  | #FAECE7 | #F5C4B3 | #F0997B | #D85A30 | #993C1D | #712B13 | #4A1B0C |
| `c-pink`   | #FBEAF0 | #F4C0D1 | #ED93B1 | #D4537E | #993556 | #72243E | #4B1528 |
| `c-gray`   | #F1EFE8 | #D3D1C7 | #B4B2A9 | #888780 | #5F5E5A | #444441 | #2C2C2A |
| `c-blue`   | #E6F1FB | #B5D4F4 | #85B7EB | #378ADD | #185FA5 | #0C447C | #042C53 |
| `c-green`  | #EAF3DE | #C0DD97 | #97C459 | #639922 | #3B6D11 | #27500A | #173404 |
| `c-amber`  | #FAEEDA | #FAC775 | #EF9F27 | #BA7517 | #854F0B | #633806 | #412402 |
| `c-red`    | #FCEBEB | #F7C1C1 | #F09595 | #E24B4A | #A32D2D | #791F1F | #501313 |

#### 颜色分配规则

颜色编码**含义**，而非顺序。切勿像彩虹一样循环使用颜色。

- 按**类别**分组节点——同一类型的所有节点共享一种颜色。
- 使用 `c-gray` 表示中性/结构节点（开始、结束、通用步骤、用户）。
- 每个图表使用**2-3种颜色**，而非6种以上。
- 对于一般类别，优先使用 `c-purple`、`c-teal`、`c-coral`、`c-pink`。
- 保留 `c-blue`、`c-green`、`c-amber`、`c-red` 用于语义含义（信息、成功、警告、错误）。
明暗模式颜色映射（由模板 CSS 处理 — 只需使用对应的类）：
- 浅色模式：50 填充色 + 600 描边色 + 800 标题色 / 600 副标题色
- 深色模式：800 填充色 + 200 描边色 + 100 标题色 / 200 副标题色

### 排版

仅使用两种字体大小。没有例外。

| 类 | 大小 | 字重 | 用途 |
|-------|------|--------|-----|
| `th`  | 14px | 500    | 节点标题、区域标签 |
| `ts`  | 12px | 400    | 副标题、描述、箭头标签 |
| `t`   | 14px | 400    | 常规文本 |

- **始终使用句子大小写。** 不要使用标题大小写，不要全部大写。
- 每个 `<text>` 元素**必须**带有一个类（`t`、`ts` 或 `th`）。不能有无类的文本。
- 所有框内的文本都使用 `dominant-baseline="central"`。
- 框内居中的文本使用 `text-anchor="middle"`。

**宽度估算（近似值）：**
- 14px 字重 500：每个字符约 8px
- 12px 字重 400：每个字符约 6.5px
- 始终验证：`box_width >= (char_count × px_per_char) + 48`（每边 24px 内边距）

### 间距与布局

- **视口框**：`viewBox="0 0 680 H"`，其中 H = 内容高度 + 40px 缓冲。
- **安全区域**：x=40 到 x=640，y=40 到 y=(H-40)。
- **框之间**：最小间距 60px。
- **框内部**：水平内边距 24px，垂直内边距 12px。
- **箭头间隙**：箭头与框边缘之间 10px。
- **单行框**：高度 44px。
- **双行框**：高度 56px，标题与副标题基线之间 18px。
- **容器内边距**：每个容器内部至少 20px。
- **最大嵌套**：2-3 层深度。更深层次在 680px 宽度下会变得难以阅读。

### 描边与形状

- **描边宽度**：所有节点边框均为 0.5px。不是 1px，也不是 2px。
- **矩形圆角**：节点使用 `rx="8"`，内部容器使用 `rx="12"`，外部容器使用 `rx="16"` 到 `rx="20"`。
- **连接线路径**：**必须**有 `fill="none"`。否则 SVG 默认使用 `fill: black`。

### 箭头标记

在每个 SVG 的开头包含这个 `<defs>` 块：

```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

在线上使用 `marker-end="url(#arrow)"`。箭头通过 `context-stroke` 继承线条颜色。

### CSS 类（由模板提供）

模板页面提供：

- 文本：`.t`、`.ts`、`.th`
- 中性色：`.box`、`.arr`、`.leader`、`.node`
- 颜色渐变：`.c-purple`、`.c-teal`、`.c-coral`、`.c-pink`、`.c-gray`、`.c-blue`、`.c-green`、`.c-amber`、`.c-red`（全部自动适配明暗模式）

你**不需要**重新定义这些 — 只需在你的 SVG 中应用它们。模板文件包含完整的 CSS 定义。

---

## SVG 样板代码

模板页面内的每个 SVG 都以此确切结构开头：

```xml
<svg width="100%" viewBox="0 0 680 {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- 图表内容放在这里 -->

</svg>
```

将 `{HEIGHT}` 替换为实际计算出的高度（最后一个元素的底部 + 40px）。

### 节点模式

**单行节点 (44px)：**
```xml
<g class="node c-blue">
  <rect x="100" y="20" width="180" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="190" y="42" text-anchor="middle" dominant-baseline="central">服务名称</text>
</g>
```

**双行节点 (56px)：**
```xml
<g class="node c-teal">
  <rect x="100" y="20" width="200" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="200" y="38" text-anchor="middle" dominant-baseline="central">服务名称</text>
  <text class="ts" x="200" y="56" text-anchor="middle" dominant-baseline="central">简短描述</text>
</g>
```

**连接线（无标签）：**
```xml
<line x1="200" y1="76" x2="200" y2="120" class="arr" marker-end="url(#arrow)"/>
```

**容器（虚线或实线）：**
```xml
<g class="c-purple">
  <rect x="40" y="92" width="600" height="300" rx="16" stroke-width="0.5"/>
  <text class="th" x="66" y="116">容器标签</text>
  <text class="ts" x="66" y="134">副标题信息</text>
</g>
```

---

## 图表类型

选择适合主题的布局：

1.  **流程图** — CI/CD 流水线、请求生命周期、审批工作流、数据处理。单向流动（自上而下或从左到右）。每行最多 4-5 个节点。
2.  **结构/包含图** — 云基础设施嵌套、分层系统架构。大型外部容器包含内部区域。虚线矩形用于逻辑分组。
3.  **API/端点映射图** — REST 路由、GraphQL 模式。从根开始的树状结构，分支到资源组，每个组包含端点节点。
4.  **微服务拓扑图** — 服务网格、事件驱动系统。服务作为节点，箭头表示通信模式，消息队列位于其间。
5.  **数据流图** — ETL 流水线、流式架构。从左到右的流动，从源经过处理到汇。
6.  **物理/结构图** — 车辆、建筑、硬件、解剖结构。使用匹配物理形态的形状 — 曲线体使用 `<path>`，锥形形状使用 `<polygon>`，圆柱形部件使用 `<ellipse>`/`<circle>`，隔间使用嵌套的 `<rect>`。参见 `references/physical-shape-cookbook.md`。
7.  **基础设施/系统集成图** — 智慧城市、物联网网络、多领域系统。中心辐射型布局，中央平台连接子系统。语义线样式（`.data-line`、`.power-line`、`.water-pipe`、`.road`）。参见 `references/infrastructure-patterns.md`。
8.  **UI/仪表板模拟图** — 管理面板、监控仪表板。屏幕框架包含嵌套的图表/仪表/指示器元素。参见 `references/dashboard-patterns.md`。

对于物理、基础设施和仪表板图表，请在生成前加载相应的参考文件 — 每个文件都提供了现成的 CSS 类和形状基元。
---

## 验证清单

在最终确定任何 SVG 之前，请验证以下所有内容：

1.  每个 `<text>` 元素都有 `t`、`ts` 或 `th` 类。
2.  框内的每个 `<text>` 元素都有 `dominant-baseline="central"` 属性。
3.  每个用作箭头的连接器 `<path>` 或 `<line>` 都有 `fill="none"` 属性。
4.  没有箭头线穿过不相关的框。
5.  对于 14px 文本，`box_width >= (最长标签字符数 × 8) + 48`。
6.  对于 12px 文本，`box_width >= (最长标签字符数 × 6.5) + 48`。
7.  ViewBox 高度 = 最底部元素 + 40px。
8.  所有内容保持在 x=40 到 x=640 的范围内。
9.  颜色类 (`c-*`) 位于 `<g>` 或形状元素上，绝不在 `<path>` 连接器上。
10. 箭头 `<defs>` 块存在。
11. 没有渐变、阴影、模糊或发光效果。
12. 所有节点边框的描边宽度为 0.5px。

---

## 输出与预览

### 默认：独立的 HTML 文件

编写一个用户可以直接打开的单个 `.html` 文件。无需服务器，无依赖，可离线工作。模式如下：

```python
# 1. 加载模板
template = skill_view("concept-diagrams", "templates/template.html")

# 2. 填入标题、副标题并粘贴你的 SVG
html = template.replace(
    "<!-- DIAGRAM TITLE HERE -->", "SN2 反应机理"
).replace(
    "<!-- OPTIONAL SUBTITLE HERE -->", "双分子亲核取代"
).replace(
    "<!-- PASTE SVG HERE -->", svg_content
)

# 3. 写入用户选择的路径（或默认 ./）
write_file("./sn2-mechanism.html", html)
```

告诉用户如何打开它：

```
# macOS
open ./sn2-mechanism.html
# Linux
xdg-open ./sn2-mechanism.html
```

### 可选：本地预览服务器（多图表库）

仅当用户明确想要一个可浏览的多图表库时使用此选项。

**规则：**
- 仅绑定到 `127.0.0.1`。切勿使用 `0.0.0.0`。在共享网络上将所有网络接口上的图表暴露出来存在安全风险。
- 选择一个空闲端口（不要硬编码端口号）并告知用户所选的 URL。
- 服务器是可选的且需要用户选择启用——优先使用独立的 HTML 文件。

推荐模式（让操作系统选择一个空闲的临时端口）：

```bash
# 将每个图表放在 .diagrams/ 下的独立文件夹中
mkdir -p .diagrams/sn2-mechanism
# ...写入 .diagrams/sn2-mechanism/index.html...

# 仅在环回地址上提供服务，使用空闲端口
cd .diagrams && python3 -c "
import http.server, socketserver
with socketserver.TCPServer(('127.0.0.1', 0), http.server.SimpleHTTPRequestHandler) as s:
    print(f'Serving at http://127.0.0.1:{s.server_address[1]}/')
    s.serve_forever()
" &
```

如果用户坚持使用固定端口，请使用 `127.0.0.1:<端口>`——仍然不要使用 `0.0.0.0`。记录如何停止服务器（`kill %1` 或 `pkill -f "http.server"`）。

---

## 示例参考

`examples/` 目录提供了 15 个完整、经过测试的图表。在编写类似类型的新图表之前，请浏览它们以获取有效模式：

| 文件 | 类型 | 演示内容 |
|------|------|--------------|
| `hospital-emergency-department-flow.md` | 流程图 | 带有语义颜色的优先级路由 |
| `feature-film-production-pipeline.md` | 流程图 | 分阶段工作流，水平子流程 |
| `automated-password-reset-flow.md` | 流程图 | 带有错误分支的认证流程 |
| `autonomous-llm-research-agent-flow.md` | 流程图 | 回环箭头，决策分支 |
| `place-order-uml-sequence.md` | 序列图 | UML 序列图样式 |
| `commercial-aircraft-structure.md` | 物理结构 | 用于真实形状的路径、多边形、椭圆 |
| `wind-turbine-structure.md` | 物理横截面 | 地下/地上分离，颜色编码 |
| `smartphone-layer-anatomy.md` | 分解视图 | 交替的左右标签，分层组件 |
| `apartment-floor-plan-conversion.md` | 平面图 | 墙壁、门，用红色虚线表示提议的更改 |
| `banana-journey-tree-to-smoothie.md` | 叙事旅程 | 蜿蜒路径，渐进状态变化 |
| `cpu-ooo-microarchitecture.md` | 硬件流水线 | 扇出，内存层次结构侧边栏 |
| `sn2-reaction-mechanism.md` | 化学 | 分子、曲线箭头、能量曲线 |
| `smart-city-infrastructure.md` | 中心辐射型 | 每个系统的语义线样式 |
| `electricity-grid-flow.md` | 多阶段流程 | 电压层次结构，流程标记 |
| `ml-benchmark-grouped-bar-chart.md` | 图表 | 分组条形图，双轴 |

使用以下命令加载任何示例：
```
skill_view(name="concept-diagrams", file_path="examples/<文件名>")
```

---

## 快速参考：何时使用何种图表

| 用户说 | 图表类型 | 建议颜色 |
|-----------|--------------|------------------|
| "展示流水线" | 流程图 | 灰色开始/结束，紫色步骤，红色错误，青色部署 |
| "绘制数据流" | 数据流水线（从左到右） | 灰色源，紫色处理，青色接收器 |
| "可视化系统" | 结构图（包含关系） | 紫色容器，青色服务，珊瑚色数据 |
| "映射端点" | API 树 | 紫色根，每个资源组一个渐变 |
| "展示服务" | 微服务拓扑 | 灰色入口，青色服务，紫色总线，珊瑚色工作器 |
| "绘制飞机/车辆" | 物理结构 | 用于真实形状的路径、多边形、椭圆 |
| "智慧城市 / IoT" | 中心辐射型集成 | 每个子系统的语义线样式 |
| "展示仪表板" | UI 线框图 | 深色屏幕，图表颜色：青色、紫色、珊瑚色用于警报 |
| "电网 / 电力" | 多阶段流程 | 电压层次结构（高压/中压/低压线宽） |
| "风力涡轮机 / 涡轮机" | 物理横截面 | 基础 + 塔架剖视图 + 机舱颜色编码 |
| "X 的旅程 / 生命周期" | 叙事旅程 | 蜿蜒路径，渐进状态变化 |
| "X 的层次 / 分解" | 分解层视图 | 垂直堆叠，交替标签 |
| "CPU / 流水线" | 硬件流水线 | 垂直阶段，扇出到执行端口 |
| "平面图 / 公寓" | 平面图 | 墙壁、门，用红色虚线表示提议的更改 |
| "反应机理" | 化学 | 原子、键、曲线箭头、过渡态、能量曲线 |