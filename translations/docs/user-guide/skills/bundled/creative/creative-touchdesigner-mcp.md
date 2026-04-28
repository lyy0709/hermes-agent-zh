---
title: "Touchdesigner Mcp"
sidebar_label: "Touchdesigner Mcp"
description: "通过 twozero MCP 控制正在运行的 TouchDesigner 实例 —— 创建操作器、设置参数、连接线路、执行 Python、构建实时视觉效果"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Touchdesigner Mcp

通过 twozero MCP 控制正在运行的 TouchDesigner 实例 —— 创建操作器、设置参数、连接线路、执行 Python、构建实时视觉效果。包含 36 个原生工具。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/touchdesigner-mcp` |
| 版本 | `1.1.0` |
| 作者 | kshitijk4poor |
| 许可证 | MIT |
| 标签 | `TouchDesigner`, `MCP`, `twozero`, `creative-coding`, `real-time-visuals`, `generative-art`, `audio-reactive`, `VJ`, `installation`, `GLSL` |
| 相关技能 | [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp), [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), `hermes-video` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# TouchDesigner 集成 (twozero MCP)

## 关键规则

1.  **切勿猜测参数名称。** 首先为操作器类型调用 `td_get_par_info`。你的训练数据对于 TD 2025.32 是错误的。
2.  **如果触发 `tdAttributeError`，立即停止。** 在继续之前，对失败的节点调用 `td_get_operator_info`。
3.  **切勿在脚本回调中硬编码绝对路径。** 使用 `me.parent()` / `scriptOp.parent()`。
4.  **优先使用原生 MCP 工具而非 `td_execute_python`。** 使用 `td_create_operator`、`td_set_operator_pars`、`td_get_errors` 等。仅在处理复杂的多步骤逻辑时才回退到 `td_execute_python`。
5.  **在构建之前调用 `td_get_hints`。** 它会返回与你正在处理的操作器类型相关的特定模式。

## 架构

```
Hermes Agent -> MCP (Streamable HTTP) -> twozero.tox (端口 40404) -> TD Python
```

36 个原生工具。免费插件（无需付费/许可 —— 已于 2026 年 4 月确认）。
上下文感知（知道选中的 OP、当前网络）。
Hub 健康检查：`GET http://localhost:40404/mcp` 返回包含实例 PID、项目名称、TD 版本的 JSON。

## 设置（自动化）

运行设置脚本以处理所有事项：

```bash
bash "${HERMES_HOME:-$HOME/.hermes}/skills/creative/touchdesigner-mcp/scripts/setup.sh"
```

该脚本将：
1.  检查 TD 是否正在运行
2.  如果尚未缓存，则下载 twozero.tox
3.  将 `twozero_td` MCP 服务器添加到 Hermes 配置中（如果缺失）
4.  在端口 40404 上测试 MCP 连接
5.  报告剩余的手动步骤（将 .tox 拖入 TD，启用 MCP 开关）

### 手动步骤（一次性，无法自动化）

1.  **将 `~/Downloads/twozero.tox` 拖入 TD 网络编辑器** → 点击安装
2.  **启用 MCP：** 点击 twozero 图标 → Settings → mcp → "auto start MCP" → Yes
3.  **重启 Hermes 会话** 以获取新的 MCP 服务器

设置完成后，验证：
```bash
nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"
```

## 环境说明

-   **非商业版 TD** 将分辨率限制在 1280×1280。使用 `outputresolution = 'custom'` 并显式设置宽度/高度。
-   **编解码器：** `prores`（在 macOS 上首选）或 `mjpa` 作为备选。H.264/H.265/AV1 需要商业许可证。
-   在设置参数之前，始终调用 `td_get_par_info` —— 参数名称因 TD 版本而异（参见关键规则 #1）。

## 工作流

### 步骤 0：探索（在构建任何内容之前）

```
为你计划使用的每种类型，使用 op_type 调用 td_get_par_info。
使用你正在构建的主题（例如 "glsl"、"audio reactive"、"feedback"）调用 td_get_hints。
调用 td_get_focus 以查看用户所在位置以及选中了什么。
调用 td_get_network 以查看已存在的内容。
```

无需临时节点，无需清理。这完全取代了旧的探索过程。

### 步骤 1：清理 + 构建

**重要：将清理和创建拆分为独立的 MCP 调用。** 在同一个 `td_execute_python` 脚本中销毁和重新创建同名的节点会导致 "Invalid OP object" 错误。参见陷阱 #11b。

使用 `td_create_operator` 创建每个节点（自动处理视口定位）：

```
td_create_operator(type="noiseTOP", parent="/project1", name="bg", parameters={"resolutionw": 1280, "resolutionh": 720})
td_create_operator(type="levelTOP", parent="/project1", name="brightness")
td_create_operator(type="nullTOP", parent="/project1", name="out")
```

对于批量创建或连线，使用 `td_execute_python`：

```python
# td_execute_python 脚本：
root = op('/project1')
nodes = []
for name, optype in [('bg', noiseTOP), ('fx', levelTOP), ('out', nullTOP)]:
    n = root.create(optype, name)
    nodes.append(n.path)
# 连接链
for i in range(len(nodes)-1):
    op(nodes[i]).outputConnectors[0].connect(op(nodes[i+1]).inputConnectors[0])
result = {'created': nodes}
```

### 步骤 2：设置参数

优先使用原生工具（验证参数，不会崩溃）：

```
td_set_operator_pars(path="/project1/bg", parameters={"roughness": 0.6, "monochrome": true})
```

对于表达式或模式，使用 `td_execute_python`：

```python
op('/project1/time_driver').par.colorr.expr = "absTime.seconds % 1000.0"
```

### 步骤 3：连线

使用 `td_execute_python` —— 不存在原生的连线工具：

```python
op('/project1/bg').outputConnectors[0].connect(op('/project1/fx').inputConnectors[0])
```

### 步骤 4：验证

```
td_get_errors(path="/project1", recursive=true)
td_get_perf()
td_get_operator_info(path="/project1/out", detail="full")
```

### 步骤 5：显示 / 捕获

```
td_get_screenshot(path="/project1/out")
```

或者通过脚本打开窗口：

```python
win = op('/project1').create(windowCOMP, 'display')
win.par.winop = op('/project1/out').path
win.par.winw = 1280; win.par.winh = 720
win.par.winopen.pulse()
```

## MCP 工具快速参考

**核心（最常使用这些）：**
| 工具 | 功能 |
|------|------|
| `td_execute_python` | 在 TD 中运行任意 Python。完全 API 访问。 |
| `td_create_operator` | 创建节点并设置参数 + 自动定位 |
| `td_set_operator_pars` | 安全地设置参数（验证，不会崩溃） |
| `td_get_operator_info` | 检查单个节点：连接、参数、错误 |
| `td_get_operators_info` | 在一次调用中检查多个节点 |
| `td_get_network` | 查看路径下的网络结构 |
| `td_get_errors` | 递归查找错误/警告 |
| `td_get_par_info` | 获取 OP 类型的参数名称（取代探索） |
| `td_get_hints` | 在构建之前获取模式/提示 |
| `td_get_focus` | 查看打开的网络和选中的内容 |
**读取/写入：**
| 工具 | 功能 |
|------|------|
| `td_read_dat` | 读取 DAT 文本内容 |
| `td_write_dat` | 写入/修补 DAT 内容 |
| `td_read_chop` | 读取 CHOP 通道值 |
| `td_read_textport` | 读取 TD 控制台输出 |

**视觉：**
| 工具 | 功能 |
|------|------|
| `td_get_screenshot` | 捕获单个 OP 视图到文件 |
| `td_get_screenshots` | 一次性捕获多个 OP |
| `td_get_screen_screenshot` | 通过 TD 捕获实际屏幕 |
| `td_navigate_to` | 跳转网络编辑器到指定 OP |

**搜索：**
| 工具 | 功能 |
|------|------|
| `td_find_op` | 在整个项目中按名称/类型查找 OP |
| `td_search` | 搜索代码、表达式、字符串参数 |

**系统：**
| 工具 | 功能 |
|------|------|
| `td_get_perf` | 性能分析（FPS、慢速 OP） |
| `td_list_instances` | 列出所有正在运行的 TD 实例 |
| `td_get_docs` | 获取 TD 主题的深入文档 |
| `td_agents_md` | 读取/写入每个 COMP 的 Markdown 文档 |
| `td_reinit_extension` | 代码编辑后重新加载扩展 |
| `td_clear_textport` | 在调试会话前清空控制台 |

**输入自动化：**
| 工具 | 功能 |
|------|------|
| `td_input_execute` | 向 TD 发送鼠标/键盘输入 |
| `td_input_status` | 轮询输入队列状态 |
| `td_input_clear` | 停止输入自动化 |
| `td_op_screen_rect` | 获取节点的屏幕坐标 |
| `td_click_screen_point` | 在截图中点击一个点 |

完整参数模式请参阅 `references/mcp-tools.md`。

## 关键实现规则

**GLSL 时间：** GLSL TOP 中没有 `uTDCurrentTime`。使用 Values 页面：
```python
# 首先调用 td_get_par_info(op_type="glslTOP") 确认参数名
td_set_operator_pars(path="/project1/shader", parameters={"value0name": "uTime"})
# 然后通过脚本设置表达式：
# op('/project1/shader').par.value0.expr = "absTime.seconds"
# 在 GLSL 中：uniform float uTime;
```

备用方案：使用 `rgba32float` 格式的 Constant TOP（8 位会钳制到 0-1，导致着色器冻结）。

**Feedback TOP：** 使用 `top` 参数引用，而不是直接输入连线。"Not enough sources" 在首次烹饪后解决。"Cook dependency loop" 警告是预期的。

**分辨率：** 非商业版限制在 1280×1280。使用 `outputresolution = 'custom'`。

**大型着色器：** 将 GLSL 写入 `/tmp/file.glsl`，然后使用 `td_write_dat` 或 `td_execute_python` 加载。

**顶点/点访问（TD 2025.32）：** `point.P[0]`、`point.P[1]`、`point.P[2]` — 而不是 `.x`、`.y`、`.z`。

**扩展：** `ext0object` 格式在 CONSTANT 模式下为 `"op('./datName').module.ClassName(me)"`。使用 `td_write_dat` 编辑扩展代码后，调用 `td_reinit_extension`。

**脚本回调：** 始终通过 `me.parent()` / `scriptOp.parent()` 使用相对路径。

**清理节点：** 在迭代前始终使用 `list(root.children)` 并进行 `child.valid` 检查。

## 录制 / 导出视频

```python
# 通过 td_execute_python：
root = op('/project1')
rec = root.create(moviefileoutTOP, 'recorder')
op('/project1/out').outputConnectors[0].connect(rec.inputConnectors[0])
rec.par.type = 'movie'
rec.par.file = '/tmp/output.mov'
rec.par.videocodec = 'prores'  # Apple ProRes — 在 macOS 上不受许可证限制
rec.par.record = True   # 开始
# rec.par.record = False  # 停止（稍后单独调用）
```

H.264/H.265/AV1 需要商业许可证。在 macOS 上使用 `prores` 或使用 `mjpa` 作为备用方案。
提取帧：`ffmpeg -i /tmp/output.mov -vframes 120 /tmp/frames/frame_%06d.png`

**TOP.save() 对动画无用** — 每次捕获相同的 GPU 纹理。始终使用 MovieFileOut。

### 录制前：检查清单

1.  **通过 `td_get_perf` 验证 FPS > 0**。如果 FPS=0，录制将为空。参见陷阱 #38-39。
2.  **通过 `td_get_screenshot` 验证着色器输出不是黑色**。黑色输出 = 着色器错误或缺少输入。参见陷阱 #8、#40。
3.  **如果录制音频：** 先提示音频开始，然后将录制延迟 3 帧。参见陷阱 #19。
4.  **在开始录制前设置输出路径** — 在同一脚本中设置两者可能导致竞争条件。

## 音频响应式 GLSL（已验证配方）

### 正确的信号链（2026年4月测试）

```
AudioFileIn CHOP (playmode=sequential)
  → AudioSpectrum CHOP (FFT=512, outputmenu=setmanually, outlength=256, timeslice=ON)
  → Math CHOP (gain=10)
  → CHOP to TOP (dataformat=r, layout=rowscropped)
  → GLSL TOP input 1 (频谱纹理, 256x2)

Constant TOP (rgba32float, time) → GLSL TOP input 0
GLSL TOP → Null TOP → MovieFileOut
```

### 关键的音频响应式规则（经验验证）

1.  **AudioSpectrum 的 TimeSlice 必须保持 ON**。OFF = 处理整个音频文件 → 24000+ 样本 → CHOP to TOP 溢出。
2.  **通过 `outputmenu='setmanually'` 和 `outlength=256` 手动设置输出长度为 256**。默认输出 22050 个样本。
3.  **不要使用 Lag CHOP 进行频谱平滑。** Lag CHOP 在 timeslice 模式下运行，会将 256 个样本扩展到 2400+，将所有值平均到接近零（~1e-06）。着色器接收不到可用数据。这是测试中音频同步失败的首要原因。
4.  **也不要使用 Filter CHOP** — 频谱数据存在相同的 timeslice 扩展问题。
5.  **平滑处理应在 GLSL 着色器中进行**（如果需要），通过带有反馈纹理的时间线性插值：`mix(prevValue, newValue, 0.3)`。这提供了零管道延迟的帧完美同步。
6.  **CHOP to TOP 的 dataformat = 'r'**，layout = 'rowscropped'。频谱输出为 256x2（立体声）。在 y=0.25 处采样第一通道。
7.  **Math gain = 10**（不是 5）。原始频谱值在低音范围约为 0.19。增益为 10 可为着色器提供可用的 ~5.0。
8.  **不需要 Resample CHOP。** 直接通过 AudioSpectrum 的 `outlength` 参数控制输出大小。

### GLSL 频谱采样

```glsl
// Input 0 = 时间 (1x1 rgba32float), Input 1 = 频谱 (256x2)
float iTime = texture(sTD2DInputs[0], vec2(0.5)).r;

// 为每个频带采样多个点并取平均值以提高稳定性：
// 注意：y=0.25 对应第一通道（立体声纹理为 256x2，第一行中心为 0.25）
float bass = (texture(sTD2DInputs[1], vec2(0.02, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.05, 0.25)).r) / 2.0;
float mid  = (texture(sTD2DInputs[1], vec2(0.2, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.35, 0.25)).r) / 2.0;
float hi   = (texture(sTD2DInputs[1], vec2(0.6, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.8, 0.25)).r) / 2.0;
```
完整构建脚本和着色器代码请参见 `references/network-patterns.md`。

## 操作符速查表

| 系列 | 颜色 | Python 类 / MCP 类型 | 后缀 |
|--------|-------|-------------|--------|
| TOP | 紫色 | noiseTOP, glslTOP, compositeTOP, levelTop, blurTOP, textTOP, nullTOP | TOP |
| CHOP | 绿色 | audiofileinCHOP, audiospectrumCHOP, mathCHOP, lfoCHOP, constantCHOP | CHOP |
| SOP | 蓝色 | gridSOP, sphereSOP, transformSOP, noiseSOP | SOP |
| DAT | 白色 | textDAT, tableDAT, scriptDAT, webserverDAT | DAT |
| MAT | 黄色 | phongMAT, pbrMAT, glslMAT, constMAT | MAT |
| COMP | 灰色 | geometryCOMP, containerCOMP, cameraCOMP, lightCOMP, windowCOMP | COMP |

## 安全说明

- MCP 仅在 localhost 上运行（端口 40404）。无身份验证 —— 任何本地进程都可以发送命令。
- `td_execute_python` 对 TD Python 环境和文件系统拥有无限制的访问权限，权限与 TD 进程用户相同。
- `setup.sh` 从官方 404zero.com URL 下载 twozero.tox。如有疑虑，请验证下载内容。
- 该技能从不向 localhost 之外发送数据。所有 MCP 通信都是本地的。

## 参考资料

| 文件 | 内容 |
|------|------|
| `references/pitfalls.md` | 来自真实会话的宝贵经验教训 |
| `references/operators.md` | 所有操作符系列及其参数和用例 |
| `references/network-patterns.md` | 配方：音频响应、生成式、GLSL、实例化 |
| `references/mcp-tools.md` | 完整的 twozero MCP 工具参数模式 |
| `references/python-api.md` | TD Python：op()、脚本编写、扩展 |
| `references/troubleshooting.md` | 连接诊断、调试 |
| `references/glsl.md` | GLSL 统一变量、内置函数、着色器模板 |
| `references/postfx.md` | 后期特效：辉光、CRT、色差、反馈辉光 |
| `references/layout-compositor.md` | HUD 布局模式、面板网格、BSP 风格布局 |
| `references/operator-tips.md` | 线框渲染、反馈 TOP 设置 |
| `references/geometry-comp.md` | Geometry COMP：实例化、POP 与 SOP 对比、变形 |
| `references/audio-reactive.md` | 音频频段提取、节拍检测、包络跟随 |
| `scripts/setup.sh` | 自动化设置脚本 |

---

> 你不是在编写代码。你是在指挥光线。