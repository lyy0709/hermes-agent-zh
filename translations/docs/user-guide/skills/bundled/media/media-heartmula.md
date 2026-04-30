---
title: "Heartmula — HeartMuLa：根据歌词+标签生成类似 Suno 的歌曲"
sidebar_label: "Heartmula"
description: "HeartMuLa：根据歌词+标签生成类似 Suno 的歌曲"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Heartmula

HeartMuLa：根据歌词+标签生成类似 Suno 的歌曲。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/heartmula` |
| 版本 | `1.0.0` |
| 标签 | `music`, `audio`, `generation`, `ai`, `heartmula`, `heartcodec`, `lyrics`, `songs` |
| 相关技能 | `audiocraft` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# HeartMuLa - 开源音乐生成

## 概述
HeartMuLa 是一个开源音乐基础模型系列（Apache-2.0 许可），可根据歌词和标签生成音乐，并支持多语言。能够根据歌词+标签生成完整歌曲。是开源领域中与 Suno 相当的工具。包含：
- **HeartMuLa** - 音乐语言模型（3B/7B），用于根据歌词+标签生成音乐
- **HeartCodec** - 12.5Hz 音乐编解码器，用于高保真音频重建
- **HeartTranscriptor** - 基于 Whisper 的歌词转录
- **HeartCLAP** - 音频-文本对齐模型

## 使用场景
- 用户希望根据文本描述生成音乐/歌曲
- 用户想要一个开源的 Suno 替代品
- 用户希望进行本地/离线音乐生成
- 用户询问关于 HeartMuLa、heartlib 或 AI 音乐生成的问题

## 硬件要求
- **最低配置**：8GB VRAM，并启用 `--lazy_load true`（顺序加载/卸载模型）
- **推荐配置**：16GB+ VRAM，以获得舒适的单 GPU 使用体验
- **多 GPU**：使用 `--mula_device cuda:0 --codec_device cuda:1` 将负载分配到多个 GPU 上
- 3B 模型配合 lazy_load 峰值 VRAM 使用量约为 ~6.2GB

## 安装步骤

### 1. 克隆仓库
```bash
cd ~/  # 或目标目录
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
```

### 2. 创建虚拟环境（需要 Python 3.10）
```bash
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
```

### 3. 修复依赖兼容性问题

**重要提示**：截至 2026 年 2 月，固定的依赖项与新版本包存在冲突。应用以下修复：

```bash
# 升级 datasets（旧版本与当前 pyarrow 不兼容）
uv pip install --upgrade datasets

# 升级 transformers（需要与 huggingface-hub 1.x 兼容）
uv pip install --upgrade transformers
```

### 4. 修补源代码（transformers 5.x 必需）

**补丁 1 - RoPE 缓存修复**，位于 `src/heartlib/heartmula/modeling_heartmula.py`：

在 `HeartMuLa` 类的 `setup_caches` 方法中，在 `reset_caches` try/except 块之后、`with device:` 块之前，添加 RoPE 重新初始化代码：

```python
# 重新初始化在元设备加载期间被跳过的 RoPE 缓存
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**原因**：`from_pretrained` 首先在元设备上创建模型；`Llama3ScaledRoPE.rope_init()` 在元张量上跳过缓存构建，然后在权重加载到真实设备后永远不会重建。

**补丁 2 - HeartCodec 加载修复**，位于 `src/heartlib/pipelines/music_generation.py`：

在所有 `HeartCodec.from_pretrained()` 调用处（共有 2 处：`__init__` 中的急切加载和 `codec` 属性中的惰性加载）添加 `ignore_mismatched_sizes=True`。

**原因**：VQ 码本 `initted` 缓冲区在检查点中的形状为 `[1]`，而在模型中为 `[]`。数据相同，只是标量与 0 维张量的区别。可以安全忽略。

### 5. 下载模型检查点
```bash
cd heartlib  # 项目根目录
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

所有 3 个都可以并行下载。总大小为几个 GB。

## GPU / CUDA

HeartMuLa 默认使用 CUDA（`--mula_device cuda --codec_device cuda`）。如果用户已安装支持 PyTorch CUDA 的 NVIDIA GPU，则无需额外设置。

- 安装的 `torch==2.4.1` 默认包含 CUDA 12.1 支持
- `torchtune` 可能报告版本 `0.4.0+cpu` — 这只是包元数据，它仍然通过 PyTorch 使用 CUDA
- 要验证 GPU 是否正在使用，请在输出中查找 "CUDA memory" 行（例如 "CUDA memory before unloading: 6.20 GB"）
- **没有 GPU？** 您可以在 CPU 上运行，使用 `--mula_device cpu --codec_device cpu`，但预计生成速度**极慢**（一首歌曲可能需要 30-60+ 分钟，而在 GPU 上约为 4 分钟）。CPU 模式还需要大量 RAM（约 12GB+ 可用空间）。如果用户没有 NVIDIA GPU，建议使用云 GPU 服务（Google Colab 免费层 T4、Lambda Labs 等）或在线演示 https://heartmula.github.io/。

## 使用方法

### 基本生成
```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### 输入格式

**标签**（逗号分隔，无空格）：
```
piano,happy,wedding,synthesizer,romantic
```
或
```
rock,energetic,guitar,drums,male-vocal
```

**歌词**（使用括号内的结构标签）：
```
[Intro]

[Verse]
你的歌词在这里...

[Chorus]
副歌歌词...

[Bridge]
桥段歌词...

[Outro]
```

### 关键参数
| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | 最大长度（毫秒）（240秒 = 4 分钟） |
| `--topk` | 50 | Top-k 采样 |
| `--temperature` | 1.0 | 采样温度 |
| `--cfg_scale` | 1.5 | 分类器自由引导尺度 |
| `--lazy_load` | false | 按需加载/卸载模型（节省 VRAM） |
| `--mula_dtype` | bfloat16 | HeartMuLa 的数据类型（推荐 bf16） |
| `--codec_dtype` | float32 | HeartCodec 的数据类型（推荐 fp32 以保证质量） |

### 性能
- RTF（实时因子）≈ 1.0 — 一首 4 分钟的歌曲大约需要 4 分钟生成
- 输出：MP3，48kHz 立体声，128kbps

## 常见问题
1. **请勿对 HeartCodec 使用 bf16** — 会降低音频质量。请使用 fp32（默认）。
2. **标签可能被忽略** — 已知问题 (#90)。歌词往往占主导地位；可以尝试调整标签顺序。
3. **Triton 在 macOS 上不可用** — 仅限 Linux/CUDA 用于 GPU 加速。
4. **RTX 5080 不兼容**，上游问题中已有报告。
5. 依赖项固定冲突需要按照上述说明进行手动升级和打补丁。

## 链接
- 仓库：https://github.com/HeartMuLa/heartlib
- 模型：https://huggingface.co/HeartMuLa
- 论文：https://arxiv.org/abs/2601.10547
- 许可证：Apache-2.0