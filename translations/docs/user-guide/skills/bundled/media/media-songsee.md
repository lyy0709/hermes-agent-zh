---
title: "Songsee — 生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）"
sidebar_label: "Songsee"
description: "生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Songsee

通过 CLI 从音频文件生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）。适用于音频分析、音乐制作调试和视觉文档记录。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/songsee` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 标签 | `Audio`, `Visualization`, `Spectrogram`, `Music`, `Analysis` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# songsee

从音频文件生成频谱图和多面板音频特征可视化。

## 先决条件

需要安装 [Go](https://go.dev/doc/install)：
```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

可选：`ffmpeg`，用于处理 WAV/MP3 以外的格式。

## 快速开始

```bash
# 基本频谱图
songsee track.mp3

# 保存到指定文件
songsee track.mp3 -o spectrogram.png

# 多面板可视化网格
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# 时间切片（从 12.5 秒开始，持续 8 秒）
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg

# 从 stdin 读取
cat track.mp3 | songsee - --format png -o out.png
```

## 可视化类型

使用 `--viz` 并传入逗号分隔的值：

| 类型 | 描述 |
|------|-------------|
| `spectrogram` | 标准频率频谱图 |
| `mel` | 梅尔标度频谱图 |
| `chroma` | 音高类别分布 |
| `hpss` | 谐波/打击乐分离 |
| `selfsim` | 自相似矩阵 |
| `loudness` | 随时间变化的响度 |
| `tempogram` | 节奏估计 |
| `mfcc` | 梅尔频率倒谱系数 |
| `flux` | 频谱通量（起始点检测） |

多个 `--viz` 类型会以网格形式渲染到单个图像中。

## 常用标志

| 标志 | 描述 |
|------|-------------|
| `--viz` | 可视化类型（逗号分隔） |
| `--style` | 调色板：`classic`, `magma`, `inferno`, `viridis`, `gray` |
| `--width` / `--height` | 输出图像尺寸 |
| `--window` / `--hop` | FFT 窗口和跳跃大小 |
| `--min-freq` / `--max-freq` | 频率范围过滤器 |
| `--start` / `--duration` | 音频的时间切片 |
| `--format` | 输出格式：`jpg` 或 `png` |
| `-o` | 输出文件路径 |

## 注意

- WAV 和 MP3 格式原生解码；其他格式需要 `ffmpeg`
- 输出图像可使用 `vision_analyze` 进行检查，以进行自动化音频分析
- 适用于比较音频输出、调试合成或记录音频处理流水线