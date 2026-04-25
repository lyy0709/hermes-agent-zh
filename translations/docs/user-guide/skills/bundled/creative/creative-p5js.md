---
title: "P5Js — 使用 p5 的交互式与生成式视觉艺术生产流水线"
sidebar_label: "P5Js"
description: "使用 p5 的交互式与生成式视觉艺术生产流水线"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# P5Js

使用 p5.js 的交互式与生成式视觉艺术生产流水线。创建基于浏览器的草图、生成艺术、数据可视化、交互体验、3D 场景、音频响应式视觉和动态图形——可导出为 HTML、PNG、GIF、MP4 或 SVG。涵盖：2D/3D 渲染、噪声和粒子系统、流场、着色器（GLSL）、像素操作、动态排版、WebGL 场景、音频分析、鼠标/键盘交互以及无头高分辨率导出。当用户请求以下内容时使用：p5.js 草图、创意编程、生成艺术、交互式可视化、画布动画、基于浏览器的视觉艺术、数据可视化、着色器效果或任何 p5.js 项目。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/p5js` |
| 版本 | `1.0.0` |
| 标签 | `creative-coding`, `generative-art`, `p5js`, `canvas`, `interactive`, `visualization`, `webgl`, `shaders`, `animation` |
| 相关技能 | [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# p5.js 生产流水线

## 创意标准

这是在浏览器中渲染的视觉艺术。画布是媒介；算法是画笔。

**在编写任何一行代码之前**，阐明创意概念。这件作品传达了什么？是什么让观众停止滚动？是什么让它与代码教程示例区分开来？用户的提示是一个起点——用创造性的雄心去诠释它。

**首次渲染的卓越性不容妥协。** 输出必须在首次加载时就具有视觉冲击力。如果它看起来像一个 p5.js 教程练习、默认配置或“AI 生成的创意编程”，那就是错误的。在交付前重新思考。

**超越参考词汇表。** 参考资料中的噪声函数、粒子系统、调色板和着色器效果是起始词汇。对于每个项目，都要组合、分层和创新。目录是颜料的调色板——你来创作这幅画。

**积极主动地创造。** 如果用户要求“一个粒子系统”，请提供一个具有涌现集群行为、拖尾幽灵回响、调色板偏移的深度雾化以及呼吸的背景噪声场的粒子系统。至少包含一个用户没有要求但会欣赏的视觉细节。

**密集、分层、深思熟虑。** 每一帧都应该值得观看。永远不要使用纯白背景。始终要有构图层次。始终要有意向性的色彩。始终要有只有在近距离观察时才会出现的微观细节。

**统一的美学优于功能数量。** 所有元素都必须服务于统一的视觉语言——共享的色温、一致的笔触粗细词汇、和谐的运动速度。一个包含十个无关效果的草图，不如一个包含三个相互协调效果的草图。

## 模式

| 模式 | 输入 | 输出 | 参考 |
|------|-------|--------|-----------|
| **生成艺术** | 种子 / 参数 | 程序化视觉构图（静态或动画） | `references/visual-effects.md` |
| **数据可视化** | 数据集 / API | 交互式图表、图形、自定义数据显示 | `references/interaction.md` |
| **交互体验** | 无（用户驱动） | 鼠标/键盘/触摸驱动的草图 | `references/interaction.md` |
| **动画 / 动态图形** | 时间线 / 故事板 | 定时序列、动态排版、过渡 | `references/animation.md` |
| **3D 场景** | 概念描述 | WebGL 几何体、光照、相机、材质 | `references/webgl-and-3d.md` |
| **图像处理** | 图像文件 | 像素操作、滤镜、马赛克、点彩画 | `references/visual-effects.md` § 像素操作 |
| **音频响应式** | 音频文件 / 麦克风 | 声音驱动的生成式视觉 | `references/interaction.md` § 音频输入 |

## 技术栈

每个项目都是单个自包含的 HTML 文件。无需构建步骤。

| 层级 | 工具 | 用途 |
|-------|------|---------|
| 核心 | p5.js 1.11.3 (CDN) | 画布渲染、数学、变换、事件处理 |
| 3D | p5.js WebGL 模式 | 3D 几何体、相机、光照、GLSL 着色器 |
| 音频 | p5.sound.js (CDN) | FFT 分析、振幅、麦克风输入、振荡器 |
| 导出 | 内置 `saveCanvas()` / `saveGif()` / `saveFrames()` | PNG、GIF、帧序列输出 |
| 捕获 | CCapture.js (可选) | 确定性帧率视频捕获 (WebM, GIF) |
| 无头 | Puppeteer + Node.js (可选) | 自动化高分辨率渲染，通过 ffmpeg 生成 MP4 |
| SVG | p5.js-svg 1.6.0 (可选) | 用于印刷的矢量输出——需要 p5.js 1.x |
| 自然媒介 | p5.brush (可选) | 水彩、木炭、钢笔——需要 p5.js 2.x + WEBGL |
| 纹理 | p5.grain (可选) | 胶片颗粒、纹理叠加 |
| 字体 | Google Fonts / `loadFont()` | 通过 OTF/TTF/WOFF2 实现自定义排版 |

### 版本说明

**p5.js 1.x** (1.11.3) 是默认版本——稳定、文档完善、库兼容性最广。除非项目需要 2.x 的功能，否则使用此版本。

**p5.js 2.x** (2.2+) 新增：`async setup()` 替换 `preload()`、OKLCH/OKLAB 色彩模式、`splineVertex()`、着色器 `.modify()` API、可变字体、`textToContours()`、指针事件。p5.brush 需要此版本。参见 `references/core-api.md` § p5.js 2.0。

## 流水线

每个项目都遵循相同的 6 阶段路径：

```
概念 → 设计 → 编码 → 预览 → 导出 → 验证
```

1.  **概念** —— 阐明创意愿景：情绪、色彩世界、运动词汇、独特之处
2.  **设计** —— 选择模式、画布尺寸、交互模型、色彩系统、导出格式。将概念映射到技术决策
3.  **编码** —— 编写包含内联 p5.js 的单个 HTML 文件。结构：全局变量 → `preload()` → `setup()` → `draw()` → 辅助函数 → 类 → 事件处理器
4.  **预览** —— 在浏览器中打开，验证视觉质量。在目标分辨率下测试。检查性能
5.  **导出** —— 捕获输出：PNG 用 `saveCanvas()`，GIF 用 `saveGif()`，MP4 用 `saveFrames()` + ffmpeg，无头批量处理用 Puppeteer
6.  **验证** —— 输出是否符合概念？在预期的显示尺寸下是否具有视觉冲击力？你会把它装裱起来吗？
## 创意方向

### 美学维度

| 维度 | 选项 | 参考 |
|-----------|---------|-----------|
| **色彩系统** | HSB/HSL, RGB, 命名调色板, 程序化和谐, 渐变插值 | `references/color-systems.md` |
| **噪波词汇** | Perlin 噪波, simplex 噪波, 分形（倍频）, 域扭曲, 旋度噪波 | `references/visual-effects.md` § 噪波 |
| **粒子系统** | 基于物理, 集群, 轨迹绘制, 吸引子驱动, 流场跟随 | `references/visual-effects.md` § 粒子 |
| **形状语言** | 几何图元, 自定义顶点, 贝塞尔曲线, SVG 路径 | `references/shapes-and-geometry.md` |
| **运动风格** | 缓动, 基于弹簧, 噪波驱动, 物理模拟, 线性插值, 步进 | `references/animation.md` |
| **排版** | 系统字体, 加载的 OTF 字体, `textToPoints()` 粒子文本, 动态 | `references/typography.md` |
| **着色器效果** | GLSL 片段/顶点, 滤镜着色器, 后处理, 反馈循环 | `references/webgl-and-3d.md` § 着色器 |
| **构图** | 网格, 放射状, 黄金比例, 三分法则, 有机散布, 平铺 | `references/core-api.md` § 构图 |
| **交互模型** | 鼠标跟随, 点击生成, 拖拽, 键盘状态, 滚动驱动, 麦克风输入 | `references/interaction.md` |
| **混合模式** | `BLEND`, `ADD`, `MULTIPLY`, `SCREEN`, `DIFFERENCE`, `EXCLUSION`, `OVERLAY` | `references/color-systems.md` § 混合模式 |
| **分层** | `createGraphics()` 离屏缓冲区, Alpha 合成, 遮罩 | `references/core-api.md` § 离屏缓冲区 |
| **纹理** | Perlin 表面, 点画, 排线, 半色调, 像素排序 | `references/visual-effects.md` § 纹理生成 |

### 项目级变化规则

绝不使用默认配置。对于每个项目：
- **自定义调色板** — 绝不使用原始的 `fill(255, 0, 0)`。始终使用包含 3-7 种颜色的设计调色板。
- **自定义描边粗细词汇** — 细线点缀 (0.5), 中等结构 (1-2), 粗体强调 (3-5)。
- **背景处理** — 绝不使用纯色 `background(0)` 或 `background(255)`。始终使用纹理、渐变或分层。
- **运动变化** — 不同元素使用不同速度。主元素 1x，次元素 0.3x，环境元素 0.1x。
- **至少一个创新元素** — 自定义粒子行为、新颖的噪波应用、独特的交互响应。

### 项目特定创新

对于每个项目，至少发明以下一项：
- 符合情绪的自定义调色板（非预设）
- 新颖的噪波场组合（例如，旋度噪波 + 域扭曲 + 反馈）
- 独特的粒子行为（自定义力、自定义轨迹、自定义生成）
- 用户未要求但能提升作品质量的交互机制
- 能创建视觉层次的构图技巧

### 参数设计理念

参数应源自算法本身，而非通用菜单。自问：“*这个*系统的哪些属性应该是可调的？”

**好的参数** 能展现算法的特性：
- **数量** — 粒子、分支、单元的数量（控制密度）
- **尺度** — 噪波频率、元素大小、间距（控制纹理）
- **速率** — 速度、生长速率、衰减（控制能量）
- **阈值** — 行为何时改变？（控制戏剧性）
- **比例** — 比例、力之间的平衡（控制和谐）

**不好的参数** 是与算法无关的通用控制：
- "color1", "color2", "size" — 脱离上下文则无意义
- 用于无关效果的切换开关
- 仅改变外观而不改变行为的参数

每个参数都应该改变算法的*思考方式*，而不仅仅是它的*外观*。改变噪波倍频的“湍流”参数是好的。仅改变 `ellipse()` 半径的“粒子大小”滑块则是肤浅的。

## 工作流程

### 步骤 1：创意构想

在编写任何代码之前，阐明：

- **情绪 / 氛围**：观众应感受到什么？沉思？充满活力？不安？有趣？
- **视觉故事**：随着时间的推移（或通过交互）会发生什么？构建？衰变？转化？振荡？
- **色彩世界**：暖色/冷色？单色？互补色？主色调是什么？强调色是什么？
- **形状语言**：有机曲线？锐利几何？点？线？混合？
- **运动词汇**：缓慢漂移？爆发性迸发？呼吸脉冲？机械精度？
- **独特之处**：是什么让这个草图独一无二？

将用户的提示映射到美学选择。“放松的生成背景”与“故障数据可视化”在各个方面都要求不同。

### 步骤 2：技术设计

- **模式** — 使用上表中 7 种模式中的哪一种
- **画布尺寸** — 横向 1920x1080, 纵向 1080x1920, 方形 1080x1080, 或响应式 `windowWidth/windowHeight`
- **渲染器** — `P2D`（默认）或 `WEBGL`（用于 3D、着色器、高级混合模式）
- **帧率** — 60fps（交互式）, 30fps（环境动画）, 或 `noLoop()`（静态生成）
- **导出目标** — 浏览器显示, PNG 静态图, GIF 循环, MP4 视频, SVG 矢量图
- **交互模型** — 被动（无输入）, 鼠标驱动, 键盘驱动, 音频响应, 滚动驱动
- **查看器 UI** — 对于交互式生成艺术，从 `templates/viewer.html` 开始，它提供了种子导航、参数滑块和下载功能。对于简单的草图或视频导出，使用裸 HTML

### 步骤 3：编写草图代码

对于**交互式生成艺术**（种子探索、参数调整）：从 `templates/viewer.html` 开始。先阅读模板，保留固定部分（种子导航、操作），替换算法和参数控制。这为用户提供了种子上/下/随机/跳转、带实时更新的参数滑块和 PNG 下载功能——全部已连接。

对于**动画、视频导出或简单草图**：使用裸 HTML：

单个 HTML 文件。结构：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Name</title>
  <script>p5.disableFriendlyErrors = true;</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/addons/p5.sound.min.js"></script> -->
  <!-- <script src="https://unpkg.com/p5.js-svg@1.6.0"></script> -->  <!-- SVG export -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script> -->  <!-- video capture -->
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
// === 配置 ===
const CONFIG = {
  seed: 42,
  // ... 项目特定参数
};

// === 调色板 ===
const PALETTE = {
  bg: '#0a0a0f',
  primary: '#e8d5b7',
  // ...
};

// === 全局状态 ===
let particles = [];

// === 预加载（字体、图像、数据） ===
function preload() {
  // font = loadFont('...');
}

// === 设置 ===
function setup() {
  createCanvas(1920, 1080);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  colorMode(HSB, 360, 100, 100, 100);
  // 初始化状态...
}

// === 绘制循环 ===
function draw() {
  // 渲染帧...
}

// === 辅助函数 ===
// ...

// === 类 ===
class Particle {
  // ...
}

// === 事件处理器 ===
function mousePressed() { /* ... */ }
function keyPressed() { /* ... */ }
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```
关键实现模式：
- **种子随机性**：始终使用 `randomSeed()` + `noiseSeed()` 以保证可复现性
- **颜色模式**：使用 `colorMode(HSB, 360, 100, 100, 100)` 以便直观地控制颜色
- **状态分离**：CONFIG 用于参数，PALETTE 用于颜色，全局变量用于可变状态
- **基于类的实体**：粒子、Agent、形状等作为类，具有 `update()` 和 `display()` 方法
- **离屏缓冲区**：使用 `createGraphics()` 进行分层合成、轨迹、遮罩

### 步骤 4：预览与迭代

- 直接在浏览器中打开 HTML 文件 —— 基础草图无需服务器
- 对于从本地文件 `loadImage()`/`loadFont()`：使用 `scripts/serve.sh` 或 `python3 -m http.server`
- 使用 Chrome DevTools 性能标签页验证 60fps
- 在目标导出分辨率下测试，而不仅仅是窗口大小
- 调整参数，直到视觉效果与步骤 1 中的概念相符

### 步骤 5：导出

| 格式 | 方法 | 命令 |
|--------|--------|---------|
| **PNG** | 在 `keyPressed()` 中使用 `saveCanvas('output', 'png')` | 按 's' 键保存 |
| **高分辨率 PNG** | Puppeteer 无头捕获 | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| **GIF** | `saveGif('output', 5)` —— 捕获 N 秒 | 按 'g' 键保存 |
| **帧序列** | `saveFrames('frame', 'png', 10, 30)` —— 10 秒，30fps | 然后 `ffmpeg -i frame-%04d.png -c:v libx264 output.mp4` |
| **MP4** | Puppeteer 帧捕获 + ffmpeg | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| **SVG** | 使用 p5.js-svg 的 `createCanvas(w, h, SVG)` | `save('output.svg')` |

### 步骤 6：质量验证

- **是否符合预期？** 将输出与创意概念进行比较。如果看起来普通，请返回步骤 1
- **分辨率检查**：在目标显示尺寸下是否清晰？没有锯齿伪影？
- **性能检查**：在浏览器中是否能保持 60fps？（动画至少需要 30fps）
- **颜色检查**：颜色搭配是否协调？在亮色和暗色显示器上测试
- **边界情况**：在画布边缘会发生什么？调整大小时？运行 10 分钟后？

## 关键实现说明

### 性能 —— 首先禁用 FES

友好错误系统 (FES) 会增加高达 10 倍的开销。在每个生产草图中禁用它：

```javascript
p5.disableFriendlyErrors = true;  // 在 setup() 之前

function setup() {
  pixelDensity(1);  // 防止在视网膜屏幕上进行 2x-4x 的过度绘制
  createCanvas(1920, 1080);
}
```

在热循环（粒子、像素操作）中，使用 `Math.*` 而不是 p5 包装器 —— 速度明显更快：

```javascript
// 在 draw() 或 update() 的热路径中：
let a = Math.sin(t);          // 不是 sin(t)
let r = Math.sqrt(dx*dx+dy*dy); // 不是 dist() —— 或者更好：跳过 sqrt，比较 magSq
let v = Math.random();        // 不是 random() —— 当不需要种子时
let m = Math.min(a, b);       // 不是 min(a, b)
```

切勿在 `draw()` 内部使用 `console.log()`。切勿在 `draw()` 中操作 DOM。参见 `references/troubleshooting.md` § 性能。

### 种子随机性 —— 必须使用

每个生成式草图都必须是可复现的。相同的种子，相同的输出。

```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  // 现在所有的 random() 和 noise() 调用都是确定性的
}
```

切勿将 `Math.random()` 用于生成式内容 —— 仅用于性能关键的非视觉代码。对于视觉元素，始终使用 `random()`。如果需要随机种子：`CONFIG.seed = floor(random(99999))`。

### 生成式艺术平台支持 (fxhash / Art Blocks)

对于生成式艺术平台，将 p5 的 PRNG 替换为平台的确定性随机函数：

```javascript
// fxhash 约定
const SEED = $fx.hash;              // 每次铸造唯一
const rng = $fx.rand;               // 确定性 PRNG
$fx.features({ palette: 'warm', complexity: 'high' });

// 在 setup() 中：
randomSeed(SEED);   // 用于 p5 的 noise()
noiseSeed(SEED);

// 将 random() 替换为 rng() 以实现平台确定性
let x = rng() * width;  // 而不是 random(width)
```

参见 `references/export-pipeline.md` § 平台导出。

### 颜色模式 —— 使用 HSB

对于生成式艺术，HSB（色相、饱和度、亮度）比 RGB 更容易使用：

```javascript
colorMode(HSB, 360, 100, 100, 100);
// 现在：fill(hue, sat, bri, alpha)
// 旋转色相：fill((baseHue + offset) % 360, 80, 90)
// 降低饱和度：fill(hue, sat * 0.3, bri)
// 变暗：fill(hue, sat, bri * 0.5)
```

切勿硬编码原始 RGB 值。定义一个调色板对象，通过程序化方式派生变体。参见 `references/color-systems.md`。

### 噪声 —— 多倍频程，而非原始值

原始的 `noise(x, y)` 看起来像平滑的斑点。叠加倍频程以获得自然的纹理：

```javascript
function fbm(x, y, octaves = 4) {
  let val = 0, amp = 1, freq = 1, sum = 0;
  for (let i = 0; i < octaves; i++) {
    val += noise(x * freq, y * freq) * amp;
    sum += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return val / sum;
}
```

对于流动的有机形态，使用**域扭曲**：将噪声输出作为噪声输入的坐标反馈回去。参见 `references/visual-effects.md`。

### 使用 createGraphics() 进行分层 —— 非可选

平坦的单通道渲染看起来很平淡。使用离屏缓冲区进行合成：

```javascript
let bgLayer, fgLayer, trailLayer;
function setup() {
  createCanvas(1920, 1080);
  bgLayer = createGraphics(width, height);
  fgLayer = createGraphics(width, height);
  trailLayer = createGraphics(width, height);
}
function draw() {
  renderBackground(bgLayer);
  renderTrails(trailLayer);   // 持久化，逐渐淡出
  renderForeground(fgLayer);  // 每帧清除
  image(bgLayer, 0, 0);
  image(trailLayer, 0, 0);
  image(fgLayer, 0, 0);
}
```

### 性能 —— 尽可能向量化

p5.js 的绘制调用开销很大。对于成千上万的粒子：

```javascript
// 慢：单独的形状
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// 快：使用 beginShape() 的单一形状
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// 最快：用于大量粒子的像素缓冲区
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 255;
}
updatePixels();
```
参见 `references/troubleshooting.md` § 性能。

### 多画布的实例模式

全局模式会污染 `window`。对于生产环境，请使用实例模式：

```javascript
const sketch = (p) => {
  p.setup = function() {
    p.createCanvas(800, 800);
  };
  p.draw = function() {
    p.background(0);
    p.ellipse(p.mouseX, p.mouseY, 50);
  };
};
new p5(sketch, 'canvas-container');
```

当在一个页面中嵌入多个画布或与框架集成时，这是必需的。

### WebGL 模式注意事项

- `createCanvas(w, h, WEBGL)` — 原点在中心，而非左上角
- Y 轴是反转的（在 WEBGL 中，正 Y 向上；在 P2D 中，正 Y 向下）
- 使用 `translate(-width/2, -height/2)` 来获得类似 P2D 的坐标
- 在每个变换周围使用 `push()`/`pop()` — 矩阵栈会静默溢出
- 在 `rect()`/`plane()` 之前调用 `texture()` — 而不是之后
- 自定义着色器：使用 `createShader(vert, frag)` — 在多个浏览器上测试

### 导出 — 按键绑定约定

每个画布都应在 `keyPressed()` 中包含以下内容：

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === 'r' || key === 'R') { randomSeed(millis()); noiseSeed(millis()); }
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

### 无头视频导出 — 使用 noLoop()

对于通过 Puppeteer 进行无头渲染，画布**必须**在 setup 中使用 `noLoop()`。如果没有它，p5 的绘制循环会自由运行，而截图速度很慢 — 画布会超前运行，导致帧被跳过或重复。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // 捕获脚本控制帧前进
  window._p5Ready = true;      // 向捕获脚本发出就绪信号
}
```

捆绑的 `scripts/export-frames.js` 会检测 `_p5Ready` 并在每次捕获时调用 `redraw()` 一次，以实现精确的 1:1 帧对应关系。参见 `references/export-pipeline.md` § 确定性捕获。

对于多场景视频，请使用按片段架构：每个场景一个 HTML，独立渲染，使用 `ffmpeg -f concat` 拼接。参见 `references/export-pipeline.md` § 按片段架构。

### Agent 工作流

构建 p5.js 画布时：

1.  **编写 HTML 文件** — 单个自包含文件，所有代码内联
2.  **在浏览器中打开** — `open sketch.html` (macOS) 或 `xdg-open sketch.html` (Linux)
3.  **本地资源**（字体、图像）需要服务器：在项目目录中运行 `python3 -m http.server 8080`，然后打开 `http://localhost:8080/sketch.html`
4.  **导出 PNG/GIF** — 添加上面所示的 `keyPressed()` 快捷键，告诉用户按哪个键
5.  **无头导出** — `node scripts/export-frames.js sketch.html --frames 300` 用于自动帧捕获（画布必须使用 `noLoop()` + `_p5Ready`）
6.  **MP4 渲染** — `bash scripts/render.sh sketch.html output.mp4 --duration 30`
7.  **迭代优化** — 编辑 HTML 文件，用户刷新浏览器以查看更改
8.  **按需加载参考** — 使用 `skill_view(name="p5js", file_path="references/...")` 在实现过程中根据需要加载特定的参考文件

## 性能目标

| 指标 | 目标 |
|--------|--------|
| 帧率（交互式） | 持续 60fps |
| 帧率（动画导出） | 最低 30fps |
| 粒子数量（P2D 形状） | 5,000-10,000 个粒子，60fps |
| 粒子数量（像素缓冲区） | 50,000-100,000 个粒子，60fps |
| 画布分辨率 | 最高 3840x2160（导出），1920x1080（交互式） |
| 文件大小（HTML） | &lt; 100KB（不包括 CDN 库） |
| 加载时间 | &lt; 2s 到第一帧 |

## 参考

| 文件 | 内容 |
|------|----------|
| `references/core-api.md` | 画布设置、坐标系、绘制循环、`push()`/`pop()`、离屏缓冲区、合成模式、`pixelDensity()`、响应式设计 |
| `references/shapes-and-geometry.md` | 2D 图元、`beginShape()`/`endShape()`、贝塞尔曲线/Catmull-Rom 曲线、`vertex()` 系统、自定义形状、`p5.Vector`、有向距离场、SVG 路径转换 |
| `references/visual-effects.md` | 噪声（Perlin、分形、域扭曲、旋度）、流场、粒子系统（物理、集群、轨迹）、像素操作、纹理生成（点画、影线、半色调）、反馈循环、反应-扩散 |
| `references/animation.md` | 基于帧的动画、缓动函数、`lerp()`/`map()`、弹簧物理、状态机、时间线序列、基于 `millis()` 的计时、过渡模式 |
| `references/typography.md` | `text()`、`loadFont()`、`textToPoints()`、动态排版、文本遮罩、字体度量、响应式文本大小调整 |
| `references/color-systems.md` | `colorMode()`、HSB/HSL/RGB、`lerpColor()`、`paletteLerp()`、程序化调色板、色彩和谐、`blendMode()`、渐变渲染、精选调色板库 |
| `references/webgl-and-3d.md` | WEBGL 渲染器、3D 图元、相机、光照、材质、自定义几何体、GLSL 着色器（`createShader()`、`createFilterShader()`）、帧缓冲区、后处理 |
| `references/interaction.md` | 鼠标事件、键盘状态、触摸输入、DOM 元素、`createSlider()`/`createButton()`、音频输入（p5.sound FFT/振幅）、滚动驱动动画、响应式事件 |
| `references/export-pipeline.md` | `saveCanvas()`、`saveGif()`、`saveFrames()`、确定性无头捕获、ffmpeg 帧到视频、CCapture.js、SVG 导出、按片段架构、平台导出（fxhash）、视频注意事项 |
| `references/troubleshooting.md` | 性能分析、每像素预算、常见错误、浏览器兼容性、WebGL 调试、字体加载问题、像素密度陷阱、内存泄漏、CORS |
| `templates/viewer.html` | 交互式查看器模板：种子导航（上一个/下一个/随机/跳转）、参数滑块、下载 PNG、响应式画布。从此模板开始，用于可探索的生成艺术 |

---

## 创意发散（仅在用户请求实验性/创意性/独特输出时使用）

如果用户要求创意性、实验性、令人惊讶或非传统的输出，请选择最合适的策略，并在生成代码之前逐步推理。
- **概念融合** — 当用户提出要融合两个事物或想要混合美学风格时
- **SCAMPER** — 当用户想要对已知的生成艺术模式进行创意改造时
- **远距离联想** — 当用户给出单一概念并希望进行探索时（例如“创作关于时间的作品”）

### 概念融合
1. 命名两个不同的视觉系统（例如：粒子物理学 + 手写字体）
2. 建立对应关系（粒子 = 墨滴，力 = 笔压，场 = 字母形态）
3. 选择性融合 — 保留能产生有趣涌现视觉效果的对映关系
4. 将融合体编码为统一系统，而非两个系统的简单并列

### SCAMPER 转换法
选取已知的生成模式（流场、粒子系统、L系统、元胞自动机）并进行系统性转换：
- **替代**：用文本字符替换圆形，用渐变替换线条
- **组合**：合并两种模式（流场 + 沃罗诺伊图）
- **调整**：将2D模式应用于3D投影
- **修改**：夸张化比例，扭曲坐标空间
- **改变用途**：用物理模拟实现排版，用排序算法处理色彩
- **消除**：移除网格、移除色彩、移除对称性
- **逆向**：反向运行模拟，反转参数空间

### 远距离联想
1. 锚定用户概念（例如“孤独”）
2. 生成三个距离层次的联想：
   - 近距离（明显联想）：空房间、独处身影、寂静
   - 中距离（有趣联想）：鱼群中反向游动的孤鱼、没有通知的手机、地铁车厢间的缝隙
   - 远距离（抽象联想）：质数、渐近曲线、凌晨三点的天色
3. 重点发展中距离联想 — 它们既具体到足以可视化，又足够出人意料而引人入胜