---
sidebar_position: 9
title: "语音与 TTS"
description: "跨所有平台的文本转语音和语音消息转录"
---

# 语音与 TTS

Hermes Agent 支持跨所有消息平台的文本转语音输出和语音消息转录。

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可以通过 **[工具网关](tool-gateway.md)** 使用 OpenAI TTS，无需单独的 OpenAI API 密钥。新安装可以通过运行 `hermes setup --portal` 登录并一次性开启所有网关工具；现有安装可以通过 `hermes model` 或 `hermes tools` 选择 **Nous Subscription** 来仅启用 TTS。
:::

## 文本转语音

支持十个提供商的文本转语音：

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
  speed: 1.0                    # 全局速度乘数 (提供商特定设置会覆盖此值)
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 转换为速率百分比 (+/-%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容的 TTS 端点
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
    voice: "Kore"               # 30 种预置语音: Zephyr, Puck, Kore, Enceladus, Gacrux 等。
  xai:
    voice_id: "eve"             # 或自定义语音 ID — 参见下文文档
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
    # length_scale: 1.0                         # 2.0 = 慢两倍
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = 音量减半
    # normalize_audio: true
```

**速度控制**：默认情况下，全局 `tts.speed` 值适用于所有提供商。每个提供商都可以用自己的 `speed` 设置覆盖它（例如，`tts.openai.speed: 1.5`）。提供商特定的速度优先于全局值。默认值为 `1.0`（正常速度）。

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
| Piper | 5000 |

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

- **OpenAI、ElevenLabs 和 Mistral** 原生生成 Opus 格式 —— 无需额外设置
- **Edge TTS**（默认）输出 MP3，需要 **ffmpeg** 进行转换
- **MiniMax TTS** 输出 MP3，需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **Google Gemini TTS** 输出原始 PCM，并使用 **ffmpeg** 直接编码为 Opus 以用于 Telegram 语音气泡
- **xAI TTS** 输出 MP3，需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **NeuTTS** 输出 WAV，同样需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **KittenTTS** 输出 WAV，同样需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **Piper** 输出 WAV，同样需要 **ffmpeg** 转换以用于 Telegram 语音气泡

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

如果没有 ffmpeg，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 和 Piper 的音频将作为常规音频文件发送（可播放，但显示为矩形播放器而非语音气泡）。

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

有关录音、支持格式和限制的详细信息，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper（本地，44 种语言）

Piper 是来自 Open Home Foundation（Home Assistant 维护者）的快速本地神经 TTS 引擎。它完全在 CPU 上运行，支持 **44 种语言** 的预训练语音，并且不需要 API 密钥。

**通过 `hermes tools` 安装** → Voice & TTS → Piper —— Hermes 会为您运行 `pip install piper-tts`。或者手动安装：`pip install piper-tts`。

**切换到 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

在首次调用本地未缓存的语音进行 TTS 时，Hermes 会运行 `python -m piper.download_voices <name>` 并将模型（约 20-90MB，取决于质量等级）下载到 `~/.hermes/cache/piper-voices/` 中。后续调用会重用缓存的模型。

**选择语音。** [完整的语音目录](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md) 涵盖英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等 —— 每种语言都有 `x_low` / `low` / `medium` / `high` 质量等级。在 [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/) 试听语音样本。

**使用预下载的语音。** 将 `tts.piper.voice` 设置为以 `.onnx` 结尾的绝对路径：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数** (`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`, `use_cuda`) 与 Piper 的 `SynthesisConfig` 一一对应。在较旧的 `piper-tts` 版本上这些参数会被忽略。

### 自定义命令提供商

如果您想要的 TTS 引擎不受原生支持（VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或任何其他暴露 CLI 的工具），您可以将其配置为 **命令类型提供商**，而无需编写任何 Python 代码。Hermes 将输入文本写入临时 UTF-8 文件，运行您的 shell 命令，并读取命令生成的音频文件。

在 `tts.providers.<name>` 下声明一个或多个提供商，并使用 `tts.provider: <name>` 在它们之间切换 —— 与在 `edge` 和 `openai` 等内置提供商之间切换的方式相同。

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

要通过字节跳动的 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流式 API 获得高质量中文 TTS，请安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) PyPI 包，并将其配置为命令提供商：

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

凭据来自您的 shell 环境（`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`）或 `~/.doubao-speech/config.yaml`。通过在命令中添加 `--voice zh-female-warm`（或 `doubao-speech list-voices` 中的任何其他别名）来选择语音。`doubao-speech` 还捆绑了流式 ASR —— 有关 Hermes 集成，请参阅下面的 [STT 部分](#example-doubao--volcengine-asr)。源代码和完整文档：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

#### 占位符

您的命令模板可以引用这些占位符。Hermes 在渲染时替换它们，并为每个值根据上下文（裸值 / 单引号 / 双引号）进行 shell 引用，因此包含空格和其他 shell 敏感字符的路径是安全的。

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

| 键                 | 默认值  | 含义                                                                                                    |
|--------------------|---------|------------------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 秒数；超时后进程树将被终止（Unix 使用 `killpg`，Windows 使用 `taskkill /T`）。                       |
| `output_format`    | `mp3`   | 可选值：`mp3` / `wav` / `ogg` / `flac`。如果 Hermes 选择了输出路径，则从文件扩展名自动推断。      |
| `voice_compatible` | `false` | 当为 `true` 时，Hermes 通过 ffmpeg 将 MP3/WAV 输出转换为 Opus/OGG，以便 Telegram 渲染语音气泡。      |
| `max_text_length`  | `5000`  | 在渲染命令之前，输入文本将被截断到此长度。                                             |
| `voice` / `model`  | 空      | 仅作为占位符值传递给命令。                                                           |

#### 行为说明

- **内置名称始终优先。** `tts.providers.openai` 条目永远不会覆盖原生的 OpenAI 提供商，因此用户配置无法静默替换内置提供商。
- **默认交付方式是文档。** 命令提供商在所有平台上都作为常规音频附件交付。可以通过 `voice_compatible: true` 为每个提供商选择启用语音气泡交付。
- **命令失败会暴露给 Agent。** 非零退出码、空输出或超时都会返回一个错误，其中包含命令的 stderr/stdout，以便您可以从会话中调试提供商。
- **当设置了 `command:` 时，`type: command` 是默认值。** 显式写上 `type: command` 是好习惯，但不是必需的；具有非空 `command` 字符串的条目将被视为命令提供商。
- **`{input_path}` / `{text_path}` 可以互换使用。** 使用在您的命令中读起来更顺的那个。

#### 安全性

命令类型的提供商会运行您配置的任何 shell 命令，并具有您用户的权限。Hermes 会对占位符值进行引号处理并强制执行配置的超时时间，但命令模板本身是受信任的本地输入——请像对待您 PATH 上的 shell 脚本一样对待它。

### Python 插件提供商

对于无法用单个 shell 命令表达的 TTS 引擎——没有 CLI 的 Python SDK、流式引擎、语音列表 API、需要 OAuth 刷新的身份验证——可以通过 `ctx.register_tts_provider()` 注册一个 Python 插件。该插件**与**[自定义命令提供商](#custom-command-providers)注册表**共存**（不会替换它）；选择适合您引擎的接口。

#### 何时选择哪个

| 您的后端有… | 使用 |
|---|---|
| 一个从文件/stdin 读取文本并将音频写入文件/stdout 的单一 CLI | **命令提供商**（无需 Python） |
| 两三个通过 shell 管道连接的 CLI | **命令提供商** |
| 只有 Python SDK——没有 CLI | **插件** |
| 您希望分块交付的流式字节（生成中的语音气泡） | **插件**（覆盖 `stream()`） |
| 被 `hermes setup` 使用的语音列表 API | **插件**（覆盖 `list_voices()`） |
| OAuth 刷新流程（不是静态的 Bearer Token） | **插件** |

内置提供商始终优先，命令提供商优先于同名的插件——因此插件可以安全地注册到任何非内置的名称，而无需担心会覆盖您现有的配置。

#### 最小插件

将此文件放入 `~/.hermes/plugins/my-tts/`：

`plugin.yaml`：
```yaml
name: my-tts
version: 0.1.0
description: "My custom Python TTS backend"
```

`__init__.py`：
```python
from agent.tts_provider import TTSProvider


class MyTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "my-tts"  # what tts.provider matches against

    @property
    def display_name(self) -> str:
        return "My Custom TTS"

    def is_available(self) -> bool:
        # Return False when credentials/deps are missing — picker skips
        # this row but the dispatcher still routes here on explicit config.
        import os
        return bool(os.environ.get("MY_TTS_API_KEY"))

    def synthesize(self, text, output_path, *, voice=None, model=None,
                   speed=None, format="mp3", **extra) -> str:
        # Write audio bytes to output_path, return the path.
        # Raise on failure — the dispatcher converts exceptions to a
        # standard error envelope.
        import my_tts_sdk
        client = my_tts_sdk.Client()
        audio_bytes = client.synthesize(text=text, voice=voice or "default")
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path


def register(ctx):
    ctx.register_tts_provider(MyTTSProvider())
```

启用它（`hermes plugins enable my-tts`），将 `tts.provider` 指向它（在 `config.yaml` 中设置 `tts.provider: my-tts`），`text_to_speech` 工具就会通过您的插件进行路由。

#### 可选钩子

在您的提供商类上覆盖这些方法以实现更丰富的集成：

- `list_voices()` → 返回 `{id, display, language, gender, preview_url}` 字典列表，显示在 `hermes tools` 中。
- `list_models()` → 返回 `{id, display, languages, max_text_length}` 字典列表。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}` 以支持 `hermes tools` / `hermes setup` 中的选择器行。如果没有这个，插件仍然有效，但其在选择器中的行信息会很少。
- `stream(text, *, voice, model, format, **extra)` → 返回一个迭代器，生成用于流式交付的音频字节（默认抛出 `NotImplementedError`）。
- `voice_compatible` 属性 → 如果您的输出与 Opus 兼容并且消息网关应将其作为语音气泡交付，则设置为 `True`（默认 `False` = 常规音频附件）。

完整的抽象基类（包括文档字符串）请参见 `agent/tts_provider.py`。

## 语音消息转录 (STT)

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录，并将文本注入到会话中。Agent 将转录文本视为普通文本。
| 提供商 | 质量 | 成本 | API 密钥 |
|----------|---------|------|---------|
| **Local Whisper** (默认) | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好–最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好–最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
当 `faster-whisper` 安装后，本地转录即可开箱即用。如果不可用，Hermes 也可以使用来自常见安装位置（如 `/opt/homebrew/bin`）的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
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

**Local (faster-whisper)** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好（默认） |
| `small` | ~500 MB | 中等 | 更好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当您需要一个免费的托管 STT 选项时，是很好的云端备选方案。

**OpenAI API** — 优先接受 `VOICE_TOOLS_OPENAI_KEY`，并回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人分离和词级时间戳。通过 `pip install hermes-agent[mistral]` 安装。

**xAI Grok STT** — 需要 `XAI_API_KEY`。以 multipart/form-data 格式发送到 `https://api.x.ai/v1/stt`。如果您已经在使用 xAI 进行聊天或 TTS，并希望所有功能使用一个 API 密钥，这是一个不错的选择。自动检测顺序将其放在 Groq 之后——显式设置 `stt.provider: xai` 以强制使用它。

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

Hermes 将传入的语音消息写入 `{input_path}`，运行命令，并读取在 `{output_dir}` 下生成的 `.txt` 文件。语言由 Volcengine bigmodel 端点自动检测。

### 回退行为

如果配置的提供商不可用，Hermes 会自动回退：
- **Local faster-whisper 不可用** → 在尝试云端提供商之前，先尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`
- **Groq 密钥未设置** → 回退到本地转录，然后是 OpenAI
- **OpenAI 密钥未设置** → 回退到本地转录，然后是 Groq
- **Mistral 密钥/SDK 未设置** → 在自动检测中被跳过；回退到下一个可用的提供商
- **没有可用的** → 语音消息会原样传递，并向用户提供准确的说明

### STT 自定义命令提供商

如果您想要的 STT 引擎没有原生支持（Doubao ASR、NVIDIA Parakeet、whisper.cpp 构建、开源 SenseVoice CLI，任何暴露 shell 命令的工具），您可以将其配置为**命令类型提供商**，而无需编写任何 Python 代码。Hermes 会针对音频文件运行您的 shell 命令并读回转录文本。

在 `stt.providers.<name>` 下声明一个或多个提供商，并通过 `stt.provider: <name>` 在它们之间切换——其结构与 TTS [命令提供商注册表](#custom-command-providers) 相同，但适配了输入=音频 → 输出=转录的方向。

```yaml
stt:
  provider: parakeet                # 选择 stt.providers 下的任意名称
  providers:
    parakeet:
      type: command
      command: "parakeet-asr --model nvidia/parakeet-tdt-0.6b-v2 --in {input_path} --out {output_path}"
      format: txt
      language: en
      timeout: 300

    whispercpp:
      type: command
      command: "whisper-cli -m ~/models/ggml-large-v3.bin -f {input_path} -otxt -of {output_dir}/transcript"
      format: txt

    sensevoice:
      type: command
      command: "sensevoice-cli {input_path} --json | tee {output_path}"
      format: json
```

这补充了传统的 `HERMES_LOCAL_STT_COMMAND` 应急方案——该环境变量仍然通过内置的 `local_command` 路径正常工作。当您想要**多个** shell 驱动的 STT 引擎、一个可以通过 `stt.provider` 选择的名称，或者任何需要按提供商设置 `language` / `model` / `timeout` 的情况时，请使用 `stt.providers.<name>`。

#### STT 占位符

您的命令模板可以引用这些占位符。Hermes 会在渲染时替换它们，并为每个值进行 shell 引用（裸引用 / 单引号 / 双引号），因此包含空格的路径是安全的。

| 占位符       | 含义                                                              |
|-------------------|----------------------------------------------------------------------|
| `{input_path}`    | 输入音频文件的绝对路径（原始位置，只读） |
| `{output_path}`   | 命令应将转录文本写入的绝对路径             |
| `{output_dir}`    | `{output_path}` 的父目录（对于 whisper 风格的工具很方便）  |
| `{format}`        | 配置的输出格式：`txt` / `json` / `srt` / `vtt`             |
| `{language}`      | 配置的语言代码（默认为 `en`）                          |
| `{model}`         | `stt.providers.<name>.model`，未设置时为空                       |
使用 `{{` 和 `}}` 表示字面量的大括号（在命令中嵌入 JSON 片段时很方便）。

#### 转录文本如何被读取

在你的命令成功退出后：

1. 如果 `{output_path}` 存在且非空 → Hermes 将其作为 UTF-8 文本读取。
2. 否则，如果命令写入了 stdout → Hermes 使用该输出。
3. 否则 → 错误："Command STT provider wrote no output file and produced no stdout"。

这让你可以在注册表中同时使用写入文件的 CLI（`whisper-cli`、`parakeet-asr`）和将转录文本输出到 stdout 的 curl 风格单行命令（`curl … | jq -r .text`）。

对于 `format: json` / `srt` / `vtt`，Hermes 将原始文件内容作为 `transcript` 字段返回。从 JSON 中提取 `.text` 超出了运行器的范围——要么配置 `format: txt`，要么在下游对 JSON 进行后处理。

#### STT 命令提供程序的可选键

| 键             | 默认值 | 含义                                                                                              |
|-----------------|---------|------------------------------------------------------------------------------------------------------|
| `timeout`       | `300`   | 秒数；超时时进程树将被终止（Unix 使用 `start_new_session`，Windows 使用 `taskkill /T`）。     |
| `format`        | `txt`   | 可选 `txt` / `json` / `srt` / `vtt` 之一。设置 `{output_path}` 的扩展名。                       |
| `language`      | `en`    | 传递给 `{language}`。默认为 `stt.language`，然后是 `en`。                                     |
| `model`         | 空      | 传递给 `{model}`。`transcribe_audio()` 的 `model=` 参数会覆盖此值。                |

#### STT 命令提供程序行为说明

- **内置提供程序始终优先。** 声明 `stt.providers.openai: type: command` **不会**覆盖真正的 OpenAI Whisper 处理器。内置名称在命令提供程序解析器运行之前就被短路处理了。
- **进程树清理。** 运行超过 `timeout` 的命令，其整个进程树（不仅仅是 shell 包装器）都会被终止。这样可以可靠地回收那些 fork 模型加载子进程的长时间运行的 ASR 流水线。
- **Shell 引用是自动的。** 在 `'…'` 内的占位符会进行单引号安全转义；在 `"…"` 内的占位符会进行 `$`/`` ` ``/`"` 转义；引号外的占位符会使用 `shlex.quote`。不要预先引用占位符的值。

#### STT 命令提供程序安全性

shell 命令在与 Hermes 相同的用户下运行，拥有完整的文件系统访问权限——其信任模型与 `tts.providers.<name>: type: command` 和 `HERMES_LOCAL_STT_COMMAND` 相同。只声明你信任的来源的命令提供程序。

### Python 插件提供程序 (STT)

对于既非内置、也无法用 shell 命令表达的 STT 引擎（需要 Python SDK、OAuth 刷新认证、流式分块等），可以通过 `ctx.register_transcription_provider()` 注册一个 Python 插件。该插件**与** 6 个内置提供程序（`local`、`local_command`、`groq`、`openai`、`mistral`、`xai`）以及 `stt.providers.<name>: type: command` 注册表**共存**——内置提供程序保留其原生实现，并且在名称冲突时始终优先；命令提供程序优先于同名的插件（配置比插件安装更本地化）。

#### 何时选择哪种 (STT)

| 后端具有…                                                 | 使用                                                              |
|--------------------------------------------------------------|------------------------------------------------------------------|
| 一个接收音频文件并输出文本的单一 shell 命令 | `stt.providers.<name>: type: command`（无需 Python）        |
| 只需要旧版单一命令的应急方案        | `HERMES_LOCAL_STT_COMMAND` 环境变量（为向后兼容保留）  |
| 没有 CLI 的 Python SDK                                     | `register_transcription_provider()` 插件                      |
| OAuth 刷新认证、流式分块、语音列表元数据 | `register_transcription_provider()` 插件                      |
| 已有内置提供程序覆盖（`local`、`groq`、`openai`、…）  | 设置 `stt.provider: <name>` —— 内置提供程序是内联的               |

#### 解析顺序

1. **`stt.provider` 是内置名称** → 内置分发。**始终优先。**
2. **`stt.provider` 匹配 `stt.providers.<name>` 且设置了 `command:`** → 命令提供程序运行器（参见 [STT 自定义命令提供程序](#stt-custom-command-providers)）。优先于同名的插件。
3. **`stt.provider` 匹配插件注册的 `TranscriptionProvider`** → 插件分发：
   - 如果插件的 `is_available()` 返回 `False`（缺少凭据或 SDK），调用会抛出一个标识该插件的不可用错误信封——**不是**通用的 "No STT provider available" 消息。
   - 否则，将调用插件的 `transcribe()`，并传入 `model`（来自公共的 `model=` 参数，回退到 `stt.<provider>.model`）和 `language`（来自 `stt.<provider>.language`）。
4. **无匹配项** → "No STT provider available" 错误。

#### 每个提供程序的配置命名空间

插件从 `config.yaml` 中的 `stt.<provider>` 读取其每个提供程序的配置，这与内置提供程序读取 `stt.openai.model` / `stt.mistral.model` 的方式类似：

```yaml
stt:
  provider: my-stt
  my-stt:
    model: whisper-large-v3
    language: ja          # 作为 language= 参数传递给 transcribe()
    # 任何其他插件特定的键放在这里；在你的 __init__/is_available/transcribe 中通过你自己的 config.yaml 访问来读取它们
```

分发器从这个部分转发 `model` 和 `language`；其他所有内容，插件可以自行读取。

#### 最小插件

将此文件放在 `~/.hermes/plugins/my-stt/` 中：

`plugin.yaml`：
```yaml
name: my-stt
version: 0.1.0
description: "My custom Python STT backend"
```

`__init__.py`：
```python
from agent.transcription_provider import TranscriptionProvider


class MySTTProvider(TranscriptionProvider):
    @property
    def name(self) -> str:
        return "my-stt"  # stt.provider 匹配的名称

    @property
    def display_name(self) -> str:
        return "My Custom STT"

    def is_available(self) -> bool:
        # 当凭据/依赖项缺失时返回 False —— 选择器会跳过
        # 这一行，但分发器在显式配置时仍会路由到这里。
        import os
        return bool(os.environ.get("MY_STT_API_KEY"))

    def transcribe(self, file_path, *, model=None, language=None, **extra):
        # 返回标准的转录信封：
        #   {"success": bool, "transcript": str, "provider": str, "error": str}
        # 不要抛出异常 —— 将异常转换为错误信封，以便
        # gateway/CLI 调用者在失败时看到一致的形状。
        try:
            import my_stt_sdk
            client = my_stt_sdk.Client()
            text = client.transcribe(open(file_path, "rb"))
            return {
                "success": True,
                "transcript": text,
                "provider": "my-stt",
            }
        except Exception as exc:
            return {
                "success": False,
                "transcript": "",
                "error": f"my-stt failed: {exc}",
                "provider": "my-stt",
            }


def register(ctx):
    ctx.register_transcription_provider(MySTTProvider())
```
启用它（`hermes plugins enable my-stt`），在 `config.yaml` 中设置 `stt.provider: my-stt`，语音消息转录就会通过你的插件进行路由。

#### 可选钩子

在你的提供商类中重写这些方法，以实现更丰富的集成：

- `list_models()` → 返回一个 `{id, display, languages, max_audio_seconds}` 字典的列表。
- `default_model()` → 当用户未覆盖模型时返回的字符串。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}`，以便在 `hermes tools` / `hermes setup` 中为选择器行提供支持（STT 的选择器类别尚未发布——此元数据可供插件使用，以实现向前兼容）。

完整的抽象基类（包括文档字符串）请参见 `agent/transcription_provider.py`。