---
title: "Comfyui"
sidebar_label: "Comfyui"
description: "使用 ComfyUI 生成图像、视频和音频 — 安装、启动、管理节点/模型，通过参数注入运行工作流"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Comfyui

使用 ComfyUI 生成图像、视频和音频 — 安装、启动、管理节点/模型，通过参数注入运行工作流。使用官方的 comfy-cli 进行生命周期管理，并使用直接的 REST API 进行执行。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/comfyui` |
| 版本 | `4.1.0` |
| 作者 | ['kshitijk4poor', 'alt-glitch'] |
| 许可证 | MIT |
| 平台 | macos, linux, windows |
| 标签 | `comfyui`, `image-generation`, `stable-diffusion`, `flux`, `creative`, `generative-ai`, `video-generation` |
| 相关技能 | [`stable-diffusion-image-generation`](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion), `image_gen` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# ComfyUI

通过 ComfyUI 生成图像、视频和音频，使用官方的 `comfy-cli` 进行设置/管理，并使用直接的 REST API 调用进行工作流执行。

**此技能中的参考文件：**

- `references/official-cli.md` — comfy-cli 命令参考（安装、启动、节点、模型）
- `references/rest-api.md` — ComfyUI REST API 端点（本地 + 云端）
- `references/workflow-format.md` — 工作流 JSON 格式、常见节点类型、参数映射

**此技能中的脚本：**

- `scripts/hardware_check.py` — 检测 GPU/VRAM/Apple Silicon，决定本地运行还是使用 Comfy Cloud
- `scripts/comfyui_setup.sh` — 完整的设置自动化（硬件检查 + 安装 + 启动 + 验证）
- `scripts/extract_schema.py` — 读取工作流 JSON，输出哪些参数是可控制的
- `scripts/run_workflow.py` — 注入用户参数、提交工作流、监控进度、下载输出
- `scripts/check_deps.py` — 检查所需的自定义节点和模型是否已安装

## 使用时机

- 用户要求使用 Stable Diffusion、SDXL、Flux 或其他扩散模型生成图像
- 用户想要运行特定的 ComfyUI 工作流
- 用户想要链接生成步骤（txt2img → 放大 → 面部修复）
- 用户需要 ControlNet、局部重绘、图生图或其他高级流水线
- 用户要求管理 ComfyUI 队列、检查模型或安装自定义节点
- 用户想要通过 AnimateDiff、Hunyuan、AudioCraft 等进行视频/音频生成

## 架构：两层

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────┐
│ 第一层：comfy-cli（官方）                           │
│  设置、生命周期、节点、模型                         │
│  comfy install / launch / stop / node / model       │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│ 第二层：REST API + 技能脚本                         │
│  工作流执行、参数注入、监控                         │
│  POST /api/prompt, GET /api/view, WebSocket         │
│  scripts/run_workflow.py, extract_schema.py         │
└─────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

**为什么是两层？** 官方 CLI 出色地处理了安装和服务器管理，但对工作流执行的支持非常有限（仅支持原始文件提交，没有参数注入，没有结构化输出）。REST API 填补了这一空白 — 此技能中的脚本处理了 CLI 不做的参数注入、执行监控和输出下载。

## 快速开始

### 检测环境

```bash
# 有什么可用的？
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: installed"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "server: running"

# 这台机器真的能在本地运行 ComfyUI 吗？（GPU/VRAM/Apple Silicon 检查）
python3 scripts/hardware_check.py
```

如果什么都没安装，请转到下面的 **设置与入门** — 但在选择安装路径之前，务必先运行硬件检查。
如果服务器已经在运行，请跳到 **核心工作流**。

## 核心工作流

### 步骤 1：获取工作流

用户提供工作流 JSON 文件。这些文件来自：
- ComfyUI 网页编辑器 → "Save (API Format)" 按钮
- 社区下载（civitai, Reddit, Discord）
- 此技能的 `scripts/` 目录（示例工作流）

**工作流必须是 API 格式**（节点 ID 作为键，包含 `class_type`）。
如果用户拥有编辑器格式（顶层有 `nodes[]` 和 `links[]`），他们需要使用 ComfyUI 网页编辑器中的 "Save (API Format)" 重新导出。

### 步骤 2：了解哪些参数可控制

```bash
python3 scripts/extract_schema.py workflow_api.json
```

输出（JSON）：
```json
{
  "parameters": {
    "prompt": {"node_id": "6", "field": "text", "type": "string", "value": "a cat"},
    "negative_prompt": {"node_id": "7", "field": "text", "type": "string", "value": "bad quality"},
    "seed": {"node_id": "3", "field": "seed", "type": "int", "value": 42},
    "steps": {"node_id": "3", "field": "steps", "type": "int", "value": 20},
    "width": {"node_id": "5", "field": "width", "type": "int", "value": 512},
    "height": {"node_id": "5", "field": "height", "type": "int", "value": 512}
  }
}
```

### 步骤 3：使用参数运行

**本地：**
```bash
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": 123, "steps": 30}' \
  --output-dir ./outputs
```

**云端：**
```bash
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset", "seed": 123}' \
  --host https://cloud.comfy.org \
  --api-key "$COMFY_CLOUD_API_KEY" \
  --output-dir ./outputs
```

### 步骤 4：呈现结果

脚本输出包含文件路径的 JSON：
```json
{
  "status": "success",
  "outputs": [
    {"file": "./outputs/ComfyUI_00001_.png", "node_id": "9", "type": "image"}
  ]
}
```
通过 `vision_analyze` 向用户展示图像或直接返回文件路径。

## 决策树

| 用户说 | 工具 | 命令 |
|-----------|------|---------|
| "安装 ComfyUI" | comfy-cli | `comfy install` |
| "启动 ComfyUI" | comfy-cli | `comfy launch --background` |
| "停止 ComfyUI" | comfy-cli | `comfy stop` |
| "安装 X 节点" | comfy-cli | `comfy node install <name>` |
| "下载 X 模型" | comfy-cli | `comfy model download --url <url>` |
| "列出已安装的模型" | comfy-cli | `comfy model list` |
| "列出已安装的节点" | comfy-cli | `comfy node show installed` |
| "生成一张图片" | script | `run_workflow.py --args '{"prompt": "..."}'` |
| "使用这张图片" (img2img) | REST | 上传图片，然后运行 run_workflow.py |
| "在这个工作流中我可以修改什么？" | script | `extract_schema.py workflow.json` |
| "检查工作流依赖是否满足" | script | `check_deps.py workflow.json` |
| "队列里有什么？" | REST | `curl http://HOST:8188/queue` |
| "取消那个" | REST | `curl -X POST http://HOST:8188/interrupt` |
| "释放 GPU 内存" | REST | `curl -X POST http://HOST:8188/free` |

## 设置与入门

当用户要求设置 ComfyUI 时，**第一件**要做的事是询问他们想要 **Comfy Cloud**（托管、零安装、需要 API 密钥）还是 **本地**（在他们的机器上安装 ComfyUI）。在得到回答之前，**不要**开始运行安装命令或硬件检查。

**官方文档：** https://docs.comfy.org/installation
**CLI 文档：** https://docs.comfy.org/comfy-cli/getting-started
**云服务文档：** https://docs.comfy.org/get_started/cloud

### 步骤 0：询问本地还是云服务（**始终第一步**）

清晰地展示两者的权衡，并等待用户选择。建议话术：

> "您想在本地机器上运行 ComfyUI，还是使用 Comfy Cloud？
>
> - **Comfy Cloud** — 托管在 RTX 6000 Pro GPU 上，所有模型预安装，零设置。需要 API 密钥（付费订阅）。如果您没有合适的 GPU 或想跳过安装，这是最佳选择。
> - **本地** — 免费，但您的机器**必须**满足硬件要求：
>   - **≥6 GB VRAM** 的 NVIDIA GPU（SDXL 推荐 ≥8 GB，Flux/视频推荐 ≥12 GB），**或**
>   - 支持 ROCm 的 AMD GPU（Linux），**或**
>   - **≥16 GB 统一内存**的 Apple Silicon Mac（M1 或更新型号，推荐 ≥32 GB）。
>   - Intel Mac 和没有 GPU 的机器**无法运行** — 请改用 Cloud。
>
> 您选择哪个？"

根据他们的回答进行引导：

- **用户选择 Cloud** → 跳转到 **路径 A**（无需硬件检查）。
- **用户选择 Local** → 进入 **步骤 1：硬件检查**，以验证他们的机器是否真正满足要求，然后根据检查结果从路径 B-E 中选择一个安装路径。
- **用户不确定 / 请求推荐** → 无论如何先运行硬件检查，让检查结果来决定。

### 步骤 1：验证硬件（**仅当用户选择本地时**）

```bash
python3 scripts/hardware_check.py --json
```

它会检测操作系统、GPU（NVIDIA CUDA / AMD ROCm / Apple Silicon / Intel Arc）、VRAM 和统一/系统内存，然后返回一个判定结果以及一个建议的 `comfy-cli` 标志：

| 判定结果 | 含义 | 操作 |
|------------|-----------------------------------------------------------|-------------------------------------------------|
| `ok` | ≥8 GB VRAM（独立显卡）**或** ≥32 GB 统一内存（Apple Silicon） | 本地安装 — 使用报告中的 `comfy_cli_flag` |
| `marginal` | SD1.5 可用；SDXL 勉强；Flux/视频不太可能 | 轻量级工作流可本地安装，否则选择 **路径 A (Cloud)** |
| `cloud` | 无可用的 GPU、<6 GB VRAM、<16 GB Apple 统一内存、Intel Mac | **用户选择了本地但其机器不满足要求** — 展示 `notes` 数组，并询问他们是否想切换到 Cloud |

技能强制执行的硬件阈值：

- **独立 GPU 最低要求：** 6 GB VRAM。低于此值，大多数现代模型将无法加载。
- **Apple Silicon：** M1 或更新型号（ARM64）。Intel Mac 没有 MPS 后端 — 仅限 Cloud。
- **Apple Silicon 内存：** 最低 16 GB 统一内存。8 GB 的 M1/M2 在运行 SDXL/Flux 时会交换/内存不足。
- **完全没有加速器：** CPU 模式在 comfy-cli 中是一个选项，但单张 SDXL 图片需要 10 分钟以上 — 视为不可用并引导至 Cloud。

如果判定结果是 `cloud` 但用户明确想要本地安装，**不要**静默继续。逐字展示 `notes` 数组，解释他们不满足哪项要求，并询问他们是否想 (a) 切换到 Cloud 或 (b) 强制进行本地安装（判定为 marginal/cloud 的本地安装在现代模型上会导致内存不足或速度极慢）。

报告中的 `comfy_cli_flag` 字段为您提供了步骤 2 所需的确切标志：`--nvidia`、`--amd` 或 `--m-series`。对于 Intel Arc，使用路径 E（手动安装）。

将 `notes` 数组逐字展示给用户，以便他们理解为何推荐特定路径。

### 选择安装路径

首先使用硬件检查结果。下表是备用方案，适用于用户已告知其硬件情况或您需要在多个可行路径中做出选择时：

| 情况 | 推荐路径 |
|-----------|-----------------|
| 硬件检查结果为 `verdict: cloud` | **路径 A: Comfy Cloud** |
| 没有 GPU / 只想尝试一下 | **路径 A: Comfy Cloud**（零设置） |
| Windows + NVIDIA GPU + 非技术用户 | **路径 B: ComfyUI Desktop**（一键安装程序） |
| Windows + NVIDIA GPU + 技术用户 | **路径 C: Portable** 或 **路径 D: comfy-cli** |
| Linux + 任何 GPU | **路径 D: comfy-cli**（最简单）或 路径 E 手动安装 |
| macOS + Apple Silicon | **路径 B: ComfyUI Desktop** 或 **路径 D: comfy-cli** |
| 无头模式 / 服务器 / CI | **路径 D: comfy-cli** |

对于完全自动化的路径（硬件检查 → 安装 → 启动），只需运行：

```bash
bash scripts/comfyui_setup.sh
```

它内部会运行 `hardware_check.py`，当判定结果为 `cloud` 时拒绝本地安装，否则选择正确的 `comfy-cli` 标志，然后进行安装和启动。

---

### 路径 A: Comfy Cloud（无需本地安装）

适用于没有合适 GPU 或希望零设置的用户。
由 RTX 6000 Pro GPU 提供支持，所有模型预安装。
**文档：** https://docs.comfy.org/get_started/cloud

1.  访问 https://comfy.org/cloud 并注册
2.  在 https://platform.comfy.org/login 获取 API 密钥
    - 点击 API Keys 部分的 `+ New` → Generate
    - 立即保存（仅显示一次）
3.  设置密钥：
    ```bash
    export COMFY_CLOUD_API_KEY="comfyui-xxxxxxxxxxxx"
    ```
4.  通过脚本或 Web UI 运行工作流：
    ```bash
    python3 scripts/run_workflow.py \
      --workflow workflow_api.json \
      --args '{"prompt": "a cat"}' \
      --host https://cloud.comfy.org \
      --api-key "$COMFY_CLOUD_API_KEY" \
      --output-dir ./outputs
    ```

**定价：** https://www.comfy.org/cloud/pricing
需要订阅。并发限制：免费/标准版：1 个任务，创作者版：3 个，专业版：5 个。

---

### 路径 B：ComfyUI 桌面版 (Windows/macOS)

面向非技术用户的一键安装程序。目前为 Beta 版。

**文档：** https://docs.comfy.org/installation/desktop

-   **Windows (NVIDIA)：** https://download.comfy.org/windows/nsis/x64
-   **macOS (Apple Silicon)：** 可从 https://comfy.org 获取（下载页面）

步骤：
1.  下载并运行安装程序
2.  选择 GPU 类型（推荐 NVIDIA，或 CPU 模式）
3.  选择安装位置（推荐 SSD，约需 15GB）
4.  可选：从现有的 ComfyUI 便携版安装迁移
5.  桌面版自动启动 — Web UI 在浏览器中打开

桌面版管理其自己的 Python 环境。要访问捆绑环境的 CLI：
```bash
cd <install_dir>/ComfyUI
.venv/Scripts/activate   # Windows
# 或在桌面版 UI 中使用内置终端
```

**限制：** 桌面版使用稳定版本（可能滞后于最新版）。
桌面版不支持 Linux — 请使用 comfy-cli 或手动安装。

---

### 路径 C：ComfyUI 便携版 (仅限 Windows)

包含嵌入式 Python 的独立包。解压即用，无需安装。

**文档：** https://docs.comfy.org/installation/comfyui_portable_windows

1.  从 https://github.com/comfyanonymous/ComfyUI/releases 下载
    -   标准版：Python 3.13 + CUDA 13.0（现代 NVIDIA GPU）
    -   替代版：PyTorch CUDA 12.6 + Python 3.12（NVIDIA 10 系列及更旧型号）
    -   AMD（实验性）
2.  使用 7-Zip 解压
3.  运行 `run_nvidia_gpu.bat`（或 `run_cpu.bat`）
4.  等待显示 "To see the GUI go to: http://127.0.0.1:8188"

更新：运行 `update/update_comfyui.bat`（最新提交）或
`update/update_comfyui_stable.bat`（最新稳定版本）。

---

### 路径 D：comfy-cli (所有平台 — 推荐用于 Agent)

官方 CLI 是无头/自动化设置的最佳路径。

**文档：** https://docs.comfy.org/comfy-cli/getting-started
**仓库：** https://github.com/Comfy-Org/comfy-cli

#### 先决条件
-   Python 3.10+（推荐 3.13）
-   pip（或 conda/uv）
-   已安装 GPU 驱动程序（NVIDIA 用 CUDA，AMD 用 ROCm）

#### 安装 comfy-cli

```bash
pip install comfy-cli
# 或
uvx --from comfy-cli comfy --help
```

禁用分析（避免交互式提示）：
```bash
comfy --skip-prompt tracking disable
```

#### 安装 ComfyUI

```bash
# 交互式（提示选择 GPU 类型）
comfy install

# 非交互式变体：
comfy --skip-prompt install --nvidia              # NVIDIA (CUDA)
comfy --skip-prompt install --amd                 # AMD (ROCm, Linux)
comfy --skip-prompt install --m-series            # Apple Silicon (MPS)
comfy --skip-prompt install --cpu                 # 仅 CPU（较慢）

# 使用更快的依赖项解析：
comfy --skip-prompt install --nvidia --fast-deps
```

默认位置：`~/comfy/ComfyUI` (Linux), `~/Documents/comfy/ComfyUI` (macOS/Win)。
使用以下命令覆盖：`comfy --workspace /custom/path install`

#### 启动服务器

```bash
comfy launch --background              # 后台守护进程，端口 :8188
comfy launch                           # 前台运行（查看日志）
comfy launch -- --listen 0.0.0.0       # 可在局域网访问
comfy launch -- --port 8190            # 自定义端口
comfy launch -- --lowvram              # 低 VRAM 模式（6GB 显卡）
```

验证服务器是否正在运行：
```bash
curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool
```

停止后台服务器：
```bash
comfy stop
```

---

### 路径 E：手动安装 (高级 / 所有硬件)

适用于需要完全控制或不受支持的硬件（昇腾 NPU、寒武纪 MLU、Intel Arc）。

**文档：** https://docs.comfy.org/installation/manual_install
**GitHub：** https://github.com/comfyanonymous/ComfyUI

```bash
# 1. 创建环境
conda create -n comfyenv python=3.13
conda activate comfyenv

# 2. 克隆
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 3. 安装 PyTorch（根据你的硬件选择）
# NVIDIA:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
# AMD (ROCm 6.4):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.4
# Apple Silicon:
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
# Intel Arc:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/xpu
# 仅 CPU:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

# 4. 安装 ComfyUI 依赖项
pip install -r requirements.txt

# 5. 运行
python main.py
# 带选项运行: python main.py --listen 0.0.0.0 --port 8188
```

---

### 安装后：下载模型

ComfyUI 至少需要一个检查点模型才能生成图像。

**使用 comfy-cli：**
```bash
# SDXL（通用，~6.5GB）
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5（更轻量，~4GB，适合低 VRAM）
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# 从 CivitAI 下载（可能需要 API 令牌）：
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"

# LoRA 适配器：
comfy model download --url "<URL>" --relative-path models/loras
```
**手动下载：** 将 `.safetensors` / `.ckpt` 文件直接放入 `ComfyUI/models/checkpoints/` 目录（或 `loras/`、`vae/` 等目录）。

列出已安装的模型：
```bash
comfy model list
```

---

### 安装后：安装自定义节点

自定义节点扩展了 ComfyUI 的功能（如超分辨率、视频、ControlNet 等）。

```bash
comfy node install comfyui-impact-pack           # 流行的实用工具包
comfy node install comfyui-animatediff-evolved    # 视频生成
comfy node install comfyui-controlnet-aux         # ControlNet 预处理器
comfy node install comfyui-essentials             # 常用辅助节点
comfy node update all                            # 更新所有节点
```

检查已安装内容：
```bash
comfy node show installed
```

为特定工作流安装依赖：
```bash
comfy node install-deps --workflow=workflow_api.json
```

---

### 安装后：验证设置

```bash
# 检查服务器是否响应
curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool

# 检查工作流的依赖项
python3 scripts/check_deps.py workflow_api.json --host 127.0.0.1 --port 8188

# 测试生成
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "test image, high quality"}' \
  --output-dir ./test-outputs
```

## 图片上传（图生图 / 局部重绘）

通过 REST API 直接上传文件：

```bash
# 上传输入图片
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# 返回：{"name": "photo.png", "subfolder": "", "type": "input"}

# 上传用于局部重绘的遮罩
curl -X POST "http://127.0.0.1:8188/upload/mask" \
  -F "image=@mask.png" -F "type=input" \
  -F 'original_ref={"filename":"photo.png","subfolder":"","type":"input"}'
```

然后在工作流参数中引用上传的文件名：
```bash
python3 scripts/run_workflow.py --workflow inpaint.json \
  --args '{"image": "photo.png", "mask": "mask.png", "prompt": "fill with flowers"}'
```

## 云端执行

基础 URL：`https://cloud.comfy.org`
认证：`X-API-Key` 请求头

```bash
# 提交工作流
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "cyberpunk city"}' \
  --host https://cloud.comfy.org \
  --api-key "$COMFY_CLOUD_API_KEY" \
  --output-dir ./outputs \
  --timeout 300

# 为云端工作流上传图片
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@input.png" -F "type=input" -F "overwrite=true"
```

并发任务限制：
| 套餐 | 并发任务数 |
|------|----------------|
| 免费/标准版 | 1 |
| 创作者版 | 3 |
| 专业版 | 5 |

额外的提交会自动排队。

## 队列与系统管理

```bash
# 检查队列
curl -s http://127.0.0.1:8188/queue | python3 -m json.tool

# 清空待处理队列
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'

# 取消正在运行的任务
curl -X POST http://127.0.0.1:8188/interrupt

# 释放 GPU 内存（卸载所有模型）
curl -X POST http://127.0.0.1:8188/free -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# 系统状态（显存、内存、GPU 信息）
curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool
```

## 常见问题

1.  **需要 API 格式** — `comfy run` 和脚本只接受 API 格式的工作流 JSON。
    如果用户拥有编辑器格式（来自“保存”而非“保存（API 格式）”），则需要重新导出。
    检查方法：API 格式在每个节点对象中包含 `class_type`，编辑器格式包含顶层的 `nodes` 和 `links` 数组。

2.  **服务器必须正在运行** — 所有执行都需要一个活动的服务器。使用 `comfy launch --background` 启动一个。
    使用 `curl http://127.0.0.1:8188/system_stats` 检查。

3.  **模型名称需完全匹配** — 区分大小写，包含文件扩展名。使用 `comfy model list` 来查看已安装的内容。

4.  **缺少自定义节点** — “class_type not found” 意味着缺少所需的节点。
    运行 `check_deps.py` 来查找缺失项，然后运行 `comfy node install <name>`。

5.  **工作目录** — `comfy-cli` 会自动检测 ComfyUI 工作空间。如果命令因“未找到工作空间”而失败，
    请使用 `comfy --workspace /path/to/ComfyUI <command>` 或 `comfy set-default /path/to/ComfyUI`。

6.  **云端与本地输出下载** — 云端的 `/api/view` 返回一个 302 重定向到一个签名 URL。始终跟随重定向（使用 `curl -L`）。
    `run_workflow.py` 脚本会自动处理此问题。

7.  **视频/音频生成的超时设置** — 长时间生成（视频、高步数）可能需要数分钟。向 `run_workflow.py` 传递 `--timeout 600`。默认是 120 秒。

8.  **跟踪提示** — 首次运行 `comfy` 可能会提示是否同意分析跟踪。
    使用 `comfy --skip-prompt tracking disable` 以非交互方式跳过。

9.  **通过 uvx 调用 comfy-cli** — 如果 comfy-cli 未全局安装，请使用 `uvx --from comfy-cli comfy <command>` 调用。
    本技能中的所有示例都使用裸 `comfy`，但如有需要，请在前面加上 `uvx --from comfy-cli`。

## 验证清单

- [ ] `hardware_check.py` 的结论是 `ok` 或者用户明确选择了 Comfy Cloud
- [ ] `comfy` 在 PATH 中可用（或者 `uvx --from comfy-cli comfy --help` 有效）
- [ ] `curl http://127.0.0.1:8188/system_stats` 返回 JSON
- [ ] `comfy model list` 显示至少一个检查点模型
- [ ] 工作流 JSON 是 API 格式（包含 `class_type` 键）
- [ ] `check_deps.py` 报告没有缺失的节点/模型
- [ ] 测试运行完成且输出已保存