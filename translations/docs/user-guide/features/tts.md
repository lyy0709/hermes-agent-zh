---
sidebar_position: 9
title: "语音与 TTS"
description: "支持所有平台上的文本转语音和语音消息转录"
---

# 语音与 TTS

Hermes Agent 支持在所有消息平台上进行文本转语音输出和语音消息转录。

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可以通过 **[工具网关](tool-gateway.md)** 使用 OpenAI TTS，无需单独的 OpenAI API 密钥。运行 `hermes model` 或 `hermes tools` 来启用它。
:::

## 文本转语音

支持十家提供商将文本转换为语音：

| 提供商 | 质量 | 成本 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **Mistral (Voxtral TTS)** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费额度 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 (本地) | 无需 |
| **KittenTTS** | 良好 | 免费 (本地) | 无需 |
| **Piper** | 良好 | 免费 (本地) | 无需 |

### 平台交付

| 平台 | 交付方式 | 格式 |
|----------|----------|--------|
| Telegram | 语音气泡 (内联播放) | Opus `.ogg` |
| Discord | 语音气泡 (Opus/OGG)，回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存到 `~/.hermes/audio_cache/` | MP3 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper"
  speed: 1.0                    # 全局语速乘数 (提供商特定设置会覆盖此值)
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 转换为速率百分比 (+/-%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 用于覆盖 OpenAI 兼容的 TTS 端点
    speed: 1.0                  # 0.25 - 4.0
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd (默认), speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # 参见 https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (默认)
  gemini:
    model: "gemini-2.5-flash-preview-tts"  # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预置语音: Zephyr, Puck, Kore, Enceladus, Gacrux 等
  xai:
    voice_id: "eve"             # 或自定义语音 ID — 参见下方文档
    language: "en"              # ISO 639-1 代码
    sample_rate: 24000          # 22050 / 24000 (默认) / 44100 / 48000
    bit_rate: 128000            # MP3 比特率；仅当 codec=mp3 时适用
    # base_url: "https://api.x.ai/v1"   # 通过 XAI_BASE_URL 环境变量覆盖
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
  kittentts:
    model: KittenML/kitten-tts-nano-0.8-int8   # 25MB int8；还有：kitten-tts-micro-0.8 (41MB), kitten-tts-mini-0.8 (80MB)
    voice: Jasper                               # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
    speed: 1.0                                  # 0.5 - 2.0
    clean_text: true                            # 扩展数字、货币、单位
  piper:
    voice: en_US-lessac-medium                  # 语音名称 (自动下载) 或 .onnx 文件的绝对路径
    # voices_dir: ''                            # 默认：~/.hermes/cache/piper-voices/
    # use_cuda: false                           # 需要 onnxruntime-gpu
    # length_scale: 1.0                         # 2.0 = 慢一倍
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = 音量减半
    # normalize_audio: true
```

**语速控制**：默认情况下，全局 `tts.speed` 值适用于所有提供商。每个提供商都可以用自己的 `speed` 设置覆盖它（例如，`tts.openai.speed: 1.5`）。提供商特定的语速设置优先于全局值。默认值为 `1.0`（正常语速）。

### 输入长度限制

每个提供商都有文档记录的每次请求输入字符上限。Hermes 在调用提供商之前会截断文本，因此请求永远不会因长度错误而失败：

| 提供商 | 默认上限 (字符) |
|----------|---------------------|
| Edge TTS | 5000 |
| OpenAI | 4096 |
| xAI | 15000 |
| MiniMax | 10000 |
| Mistral | 4000 |
| Google Gemini | 5000 |
| ElevenLabs | 模型感知 (见下文) |
| NeuTTS | 2000 |
| KittenTTS | 2000 |

**ElevenLabs** 根据配置的 `model_id` 选择上限：

| `model_id` | 上限 (字符) |
|------------|-------------|
| `eleven_flash_v2_5` | 40000 |
| `eleven_flash_v2` | 30000 |
| `eleven_multilingual_v2` (默认), `eleven_multilingual_v1`, `eleven_english_sts_v2`, `eleven_english_sts_v1` | 10000 |
| `eleven_v3`, `eleven_ttv_v3` | 5000 |
| 未知模型 | 回退到提供商默认值 (10000) |

**按提供商覆盖**：在 TTS 配置的提供商部分下使用 `max_text_length:`：

```yaml
tts:
  openai:
    max_text_length: 8192   # 提高或降低提供商上限
```

仅接受正整数。零、负数、非数字或布尔值将回退到提供商默认值，因此损坏的配置不会意外禁用截断。

### Telegram 语音气泡与 ffmpeg

Telegram 语音气泡需要 Opus/OGG 音频格式：

- **OpenAI、ElevenLabs 和 Mistral** 原生生成 Opus — 无需额外设置
- **Edge TTS** (默认) 输出 MP3，需要 **ffmpeg** 进行转换
- **MiniMax TTS** 输出 MP3，需要 **ffmpeg** 为 Telegram 语音气泡进行转换
- **Google Gemini TTS** 输出原始 PCM，并使用 **ffmpeg** 直接编码为 Opus 以用于 Telegram 语音气泡
- **xAI TTS** 输出 MP3，需要 **ffmpeg** 为 Telegram 语音气泡进行转换
- **NeuTTS** 输出 WAV，也需要 **ffmpeg** 为 Telegram 语音气泡进行转换
- **KittenTTS** 输出 WAV，也需要 **ffmpeg** 为 Telegram 语音气泡进行转换
- **Piper** 输出 WAV，也需要 **ffmpeg** 为 Telegram 语音气泡进行转换
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

如果没有安装 ffmpeg，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 和 Piper 的音频将作为常规音频文件发送（可以播放，但会显示为矩形播放器，而不是语音气泡）。

:::tip
如果您想在不安装 ffmpeg 的情况下使用语音气泡，请切换到 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

### xAI 自定义语音（语音克隆）

xAI 支持克隆您的声音并将其用于 TTS。在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义语音，然后在配置中设置生成的 `voice_id`：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # 您的自定义语音 ID
```

有关录音、支持的格式和限制的详细信息，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper（本地，44 种语言）

Piper 是来自 Open Home Foundation（Home Assistant 维护者）的快速本地神经 TTS 引擎。它完全在 CPU 上运行，支持 **44 种语言** 的预训练语音，并且不需要 API 密钥。

**通过 `hermes tools` 安装** → Voice & TTS → Piper — Hermes 会为您运行 `pip install piper-tts`。或者手动安装：`pip install piper-tts`。

**切换到 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

在首次调用本地未缓存的语音进行 TTS 时，Hermes 会运行 `python -m piper.download_voices <name>` 并将模型（约 20-90MB，取决于质量等级）下载到 `~/.hermes/cache/piper-voices/`。后续调用会重用缓存的模型。

**选择语音。** [完整的语音目录](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md) 涵盖英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等 — 每种语言都有 `x_low` / `low` / `medium` / `high` 质量等级。在 [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/) 试听语音样本。

**使用预下载的语音。** 将 `tts.piper.voice` 设置为以 `.onnx` 结尾的绝对路径：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数** (`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`, `use_cuda`) 与 Piper 的 `SynthesisConfig` 一一对应。在较旧的 `piper-tts` 版本上会被忽略。

### 自定义命令提供商

如果您想要的 TTS 引擎没有原生支持（VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或任何其他暴露 CLI 的工具），您可以将其配置为 **命令类型提供商**，而无需编写任何 Python 代码。Hermes 将输入文本写入一个临时的 UTF-8 文件，运行您的 shell 命令，并读取命令生成的音频文件。

在 `tts.providers.<name>` 下声明一个或多个提供商，并使用 `tts.provider: <name>` 在它们之间切换 — 就像在 `edge` 和 `openai` 等内置提供商之间切换一样。

```yaml
tts:
  provider: voxcpm                 # 选择 tts.providers 下的任意名称
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      timeout: 180
      voice_compatible: true       # 尝试以 Telegram 语音气泡形式交付

    mlx-kokoro:
      type: command
      command: "python -m mlx_kokoro --in {input_path} --out {output_path} --voice {voice}"
      voice: af_sky
      output_format: wav

    piper-custom:                  # 原生 Piper 也支持通过 tts.piper.voice 使用自定义 .onnx
      type: command
      command: "piper -m /path/to/custom.onnx -f {output_path} < {input_path}"
      output_format: wav
```

#### 示例：豆包（中文 seed-tts-2.0）

要通过字节跳动的 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流式 API 获得高质量的中文 TTS，请安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) PyPI 包，并将其配置为命令提供商：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
```

```yaml
tts:
  provider: doubao
  providers:
    doubao:
      type: command
      command: "doubao-speech say --text-file {input_path} --out {output_path}"
      output_format: mp3
      max_text_length: 1024
      timeout: 30
```

凭据来自您的 shell 环境（`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`）或 `~/.doubao-speech/config.yaml`。通过在命令中添加 `--voice zh-female-warm`（或 `doubao-speech list-voices` 中的任何其他别名）来选择语音。`doubao-speech` 还捆绑了流式 ASR — 有关 Hermes 集成的信息，请参阅下面的 [STT 部分](#example-doubao--volcengine-asr)。源代码和完整文档：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

#### 占位符

您的命令模板可以引用这些占位符。Hermes 在渲染时替换它们，并为周围的上下文（裸字符串 / 单引号 / 双引号）对每个值进行 shell 引用，因此包含空格和其他 shell 敏感字符的路径是安全的。

| 占位符          | 含义                                              |
|------------------|------------------------------------------------------|
| `{input_path}`   | Hermes 写入的临时 UTF-8 文本文件的路径        |
| `{text_path}`    | `{input_path}` 的别名                             |
| `{output_path}`  | 命令必须将音频写入的路径                 |
| `{format}`       | `mp3` / `wav` / `ogg` / `flac`                       |
| `{voice}`        | `tts.providers.<name>.voice`，未设置时为空       |
| `{model}`        | `tts.providers.<name>.model`                         |
| `{speed}`        | 解析后的速度乘数（提供商或全局）       |

使用 `{{` 和 `}}` 表示字面量的大括号。

#### 可选键

| 键                | 默认值 | 含义                                                                                                    |
|--------------------|---------|------------------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 秒数；超时后进程树将被终止（Unix 使用 `killpg`，Windows 使用 `taskkill /T`）。                       |
| `output_format`    | `mp3`   | 可选 `mp3` / `wav` / `ogg` / `flac` 之一。如果 Hermes 选择路径，则从输出扩展名自动推断。      |
| `voice_compatible` | `false` | 当为 `true` 时，Hermes 通过 ffmpeg 将 MP3/WAV 输出转换为 Opus/OGG，以便 Telegram 渲染语音气泡。      |
| `max_text_length`  | `5000`  | 在渲染命令之前，输入将被截断为此长度。                                             |
| `voice` / `model`  | empty   | 仅作为占位符值传递给命令。                                                           |
#### 行为说明

- **内置名称始终优先。** `tts.providers.openai` 条目永远不会覆盖原生的 OpenAI 提供商，因此用户配置无法静默替换内置提供商。
- **默认交付方式是文档。** 命令提供商在所有平台上都作为常规音频附件交付。可以通过 `voice_compatible: true` 为每个提供商选择启用语音气泡交付。
- **命令失败会暴露给 Agent。** 非零退出码、空输出或超时都会返回错误，并包含命令的 stderr/stdout，以便您可以从会话中调试该提供商。
- **当设置了 `command:` 时，`type: command` 是默认值。** 显式编写 `type: command` 是良好的实践，但不是必需的；具有非空 `command` 字符串的条目将被视为命令提供商。
- **`{input_path}` / `{text_path}` 可以互换使用。** 使用在您的命令中可读性更好的那个。

#### 安全性

命令类型的提供商会运行您配置的任何 shell 命令，并具有您用户的权限。Hermes 会对占位符值进行引号转义并强制执行配置的超时时间，但命令模板本身是受信任的本地输入——请像对待您 PATH 上的 shell 脚本一样对待它。

## 语音消息转录 (STT)

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录并作为文本注入到会话中。Agent 将转录文本视为普通文本。

| 提供商 | 质量 | 成本 | API 密钥 |
|----------|---------|------|---------|
| **本地 Whisper** (默认) | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好–最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好–最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
当安装了 `faster-whisper` 时，本地转录开箱即用。如果不可用，Hermes 也可以使用来自常见安装位置（如 `/opt/homebrew/bin`）的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
:::

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
  xai:
    model: "grok-stt"         # xAI Grok STT
```

### 提供商详情

**本地 (faster-whisper)** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好 (默认) |
| `small` | ~500 MB | 中等 | 更好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当您需要一个免费的托管 STT 选项时，是良好的云端备选方案。

**OpenAI API** — 优先接受 `VOICE_TOOLS_OPENAI_KEY`，并回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人分离和词级时间戳。通过 `pip install hermes-agent[mistral]` 安装。

**xAI Grok STT** — 需要 `XAI_API_KEY`。以 multipart/form-data 格式发送到 `https://api.x.ai/v1/stt`。如果您已经在使用 xAI 进行聊天或 TTS，并希望使用一个 API 密钥处理所有事情，这是一个不错的选择。自动检测顺序将其放在 Groq 之后——显式设置 `stt.provider: xai` 以强制使用它。

**自定义本地 CLI 回退** — 如果您希望 Hermes 直接调用本地转录命令，请设置 `HERMES_LOCAL_STT_COMMAND`。命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。您的命令必须在 `{output_dir}` 下的某个位置写入一个 `.txt` 转录文件。

#### 示例：Doubao / Volcengine ASR

如果您使用 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 进行 Doubao TTS（参见[上文](#example-doubao-chinese-seed-tts-20)），同一个包通过本地命令 STT 接口处理语音转文本：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
export HERMES_LOCAL_STT_COMMAND='doubao-speech transcribe {input_path} --out {output_dir}/transcript.txt'
```

```yaml
stt:
  provider: local_command
```

Hermes 将传入的语音消息写入 `{input_path}`，运行命令，并读取在 `{output_dir}` 下生成的 `.txt` 文件。语言由 Volcengine 大模型端点自动检测。

### 回退行为

如果配置的提供商不可用，Hermes 会自动回退：
- **本地 faster-whisper 不可用** → 在尝试云端提供商之前，先尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`
- **未设置 Groq 密钥** → 回退到本地转录，然后是 OpenAI
- **未设置 OpenAI 密钥** → 回退到本地转录，然后是 Groq
- **未设置 Mistral 密钥/SDK** → 在自动检测中被跳过；回退到下一个可用的提供商
- **没有可用的提供商** → 语音消息会原样传递，并向用户提供准确的说明