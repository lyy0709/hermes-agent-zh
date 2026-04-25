---
title: "像素艺术 — 使用硬件精确调色板（NES、Game Boy、PICO-8、C64 等）将图像转换为复古像素艺术"
sidebar_label: "像素艺术"
description: "使用硬件精确调色板（NES、Game Boy、PICO-8、C64 等）将图像转换为复古像素艺术"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 像素艺术

使用硬件精确调色板（NES、Game Boy、PICO-8、C64 等）将图像转换为复古像素艺术，并可将其动画化为短视频。预设涵盖街机、SNES 及 10 多种符合时代特征的风格。使用 `clarify` 让用户在生成前选择样式。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pixel-art` |
| 版本 | `2.0.0` |
| 作者 | dodo-reach |
| 许可证 | MIT |
| 标签 | `creative`, `pixel-art`, `arcade`, `snes`, `nes`, `gameboy`, `retro`, `image`, `video` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 像素艺术

将任何图像转换为复古像素艺术，然后可选择地使用符合时代风格的效果（雨、萤火虫、雪、余烬）将其动画化为简短的 MP4 或 GIF。

此技能附带两个脚本：

- `scripts/pixel_art.py` — 照片 → 像素艺术 PNG（弗洛伊德-斯坦伯格抖动）
- `scripts/pixel_art_video.py` — 像素艺术 PNG → 动画 MP4（+ 可选 GIF）

每个脚本都可导入或直接运行。当您需要时代精确的色彩（NES、Game Boy、PICO-8 等）时，预设会匹配硬件调色板；或者使用自适应 N 色量化来获得街机/SNES 风格的外观。

## 使用时机

- 用户希望将源图像转换为复古像素艺术
- 用户要求 NES / Game Boy / PICO-8 / C64 / 街机 / SNES 风格
- 用户想要一个简短的循环动画（雨景、夜空、雪景等）
- 海报、专辑封面、社交媒体帖子、精灵图、角色、头像

## 工作流

在生成之前，请与用户确认样式。不同的预设会产生非常不同的输出，重新生成成本很高。

### 步骤 1 — 提供样式选择

使用 4 个代表性预设调用 `clarify`。根据用户的要求选择预设集——不要直接列出全部 14 个。

当用户意图不明确时的默认菜单：

```python
clarify(
    question="您想要哪种像素艺术风格？",
    choices=[
        "arcade — 粗犷、厚重的 80 年代街机感（16 色，8px）",
        "nes — 任天堂 8 位硬件调色板（54 色，8px）",
        "gameboy — 4 阶绿色的 Game Boy DMG",
        "snes — 更干净的 16 位外观（32 色，4px）",
    ],
)
```

当用户已经指定了时代（例如 "80s arcade"、"Gameboy"）时，跳过 `clarify` 并直接使用匹配的预设。

### 步骤 2 — 提供动画选项（可选）

如果用户要求视频/GIF，或者输出可能受益于动态效果，询问选择哪个场景：

```python
clarify(
    question="想要动画化吗？选择一个场景或跳过。",
    choices=[
        "night — 星星 + 萤火虫 + 落叶",
        "urban — 雨 + 霓虹脉冲",
        "snow — 飘落的雪花",
        "skip — 仅生成图像",
    ],
)
```

**不要**连续调用 `clarify` 超过两次。一次用于样式，一次用于场景（如果考虑动画）。如果用户在消息中明确要求了特定样式和场景，则完全跳过 `clarify`。

### 步骤 3 — 生成

首先运行 `pixel_art()`；如果请求了动画，则将结果链式传递给 `pixel_art_video()`。

## 预设目录

| 预设 | 时代 | 调色板 | 块大小 | 最适合 |
|--------|-----|---------|-------|----------|
| `arcade` | 80 年代街机 | 自适应 16 色 | 8px | 粗犷海报、英雄艺术 |
| `snes` | 16 位 | 自适应 32 色 | 4px | 角色、详细场景 |
| `nes` | 8 位 | NES (54 色) | 8px | 真实的 NES 外观 |
| `gameboy` | DMG 掌机 | 4 种绿色调 | 8px | 单色 Game Boy |
| `gameboy_pocket` | Pocket 掌机 | 4 种灰色调 | 8px | 单色 GB Pocket |
| `pico8` | PICO-8 | 16 种固定色 | 6px | 幻想主机外观 |
| `c64` | Commodore 64 | 16 种固定色 | 8px | 8 位家用电脑 |
| `apple2` | Apple II 高分辨率 | 6 种固定色 | 10px | 极致复古，6 色 |
| `teletext` | BBC 图文电视 | 8 种纯色 | 10px | 厚重的原色 |
| `mspaint` | Windows 画图 | 24 种固定色 | 8px | 怀旧桌面风格 |
| `mono_green` | CRT 磷光体 | 2 种绿色 | 6px | 终端/CRT 美学 |
| `mono_amber` | CRT 琥珀色 | 2 种琥珀色 | 6px | 琥珀色显示器外观 |
| `neon` | 赛博朋克 | 10 种霓虹色 | 6px | 蒸汽波/赛博风格 |
| `pastel` | 柔和粉彩 | 10 种粉彩色 | 6px | 可爱 / 柔和风格 |

命名的调色板位于 `scripts/palettes.py` 中（完整列表见 `references/palettes.md` — 总共 28 个命名调色板）。任何预设都可以被覆盖：

```python
pixel_art("in.png", "out.png", preset="snes", palette="PICO_8", block=6)
```

## 场景目录（用于视频）

| 场景 | 效果 |
|-------|---------|
| `night` | 闪烁的星星 + 萤火虫 + 飘落的树叶 |
| `dusk` | 萤火虫 + 闪光 |
| `tavern` | 尘埃微粒 + 温暖的火花 |
| `indoor` | 尘埃微粒 |
| `urban` | 雨 + 霓虹脉冲 |
| `nature` | 树叶 + 萤火虫 |
| `magic` | 闪光 + 萤火虫 |
| `storm` | 雨 + 闪电 |
| `underwater` | 气泡 + 光点闪烁 |
| `fire` | 余烬 + 火花 |
| `snow` | 雪花 + 闪光 |
| `desert` | 热浪 + 尘埃 |

## 调用模式

### Python（导入）

```python
import sys
sys.path.insert(0, "/home/teknium/.hermes/skills/creative/pixel-art/scripts")
from pixel_art import pixel_art
from pixel_art_video import pixel_art_video

# 1. 转换为像素艺术
pixel_art("/path/to/photo.jpg", "/tmp/pixel.png", preset="nes")

# 2. 动画化（可选）
pixel_art_video(
    "/tmp/pixel.png",
    "/tmp/pixel.mp4",
    scene="night",
    duration=6,
    fps=15,
    seed=42,
    export_gif=True,
)
```

### CLI

```bash
cd /home/teknium/.hermes/skills/creative/pixel-art/scripts

python pixel_art.py in.jpg out.png --preset gameboy
python pixel_art.py in.jpg out.png --preset snes --palette PICO_8 --block 6

python pixel_art_video.py out.png out.mp4 --scene night --duration 6 --gif
```

## 流水线原理

**像素转换：**
1.  增强对比度/色彩/锐度（对于较小的调色板效果更强）
2.  色调分离以简化量化前的色调区域
3.  按 `block` 使用 `Image.NEAREST` 下采样（硬像素，无插值）
4.  使用弗洛伊德-斯坦伯格抖动进行量化 — 针对自适应 N 色调色板或命名的硬件调色板
5.  使用 `Image.NEAREST` 重新上采样

**在下采样后进行量化**，使抖动与最终的像素网格对齐。在之前量化会浪费误差扩散在即将消失的细节上。

**视频叠加：**
- 每帧复制基础帧（静态背景）
- 叠加无状态逐帧粒子绘制（每种效果一个函数）
- 通过 ffmpeg `libx264 -pix_fmt yuv420p -crf 18` 编码
- 通过 `palettegen` + `paletteuse` 可选生成 GIF

## 依赖项

- Python 3.9+
- Pillow (`pip install Pillow`)
- PATH 中的 ffmpeg（仅视频需要 — Hermes 会安装此包）

## 注意事项

- 调色板键名区分大小写（`"NES"`, `"PICO_8"`, `"GAMEBOY_ORIGINAL"`）。
- 非常小的源图像（宽度 <100px）在 8-10px 的块大小下会崩溃。如果源图像很小，请先将其放大。
- 非整数的 `block` 或 `palette` 会破坏量化 — 保持它们为正整数。
- 动画粒子数量针对约 640x480 的画布进行了调整。在非常大的图像上，您可能需要使用不同的种子进行第二次传递以获得合适的密度。
- `mono_green` / `mono_amber` 强制 `color=0.0`（去饱和）。如果覆盖此设置并保留色度，2 色调色板可能会在平滑区域产生条纹。
- `clarify` 循环：每轮最多调用两次（样式，然后是场景）。不要用更多选择来打扰用户。

## 验证

- PNG 在输出路径创建
- 在预设的块大小下可见清晰的方形像素块
- 颜色数量与预设匹配（目测图像或运行 `Image.open(p).getcolors()`）
- 视频是有效的 MP4（`ffprobe` 可以打开）且大小非零

## 归属

命名的硬件调色板和 `pixel_art_video.py` 中的程序化动画循环移植自 [pixel-art-studio](https://github.com/Synero/pixel-art-studio) (MIT)。详细信息请参阅此技能目录中的 `ATTRIBUTION.md`。