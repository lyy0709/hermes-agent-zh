---
title: "Comfyui"
sidebar_label: "Comfyui"
description: "使用 ComfyUI 生成图像、视频和音频——安装、启动、管理节点/模型，通过参数注入运行工作流"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Comfyui

使用 ComfyUI 生成图像、视频和音频——安装、启动、管理节点/模型，通过参数注入运行工作流。使用官方的 comfy-cli 进行生命周期管理，并使用直接的 REST/WebSocket API 进行执行。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/comfyui` |
| 版本 | `5.0.0` |
| 作者 | ['kshitijk4poor', 'alt-glitch'] |
| 许可证 | MIT |
| 平台 | macos, linux, windows |
| 标签 | `comfyui`, `image-generation`, `stable-diffusion`, `flux`, `sd3`, `wan-video`, `hunyuan-video`, `creative`, `generative-ai`, `video-generation` |
| 相关技能 | [`stable-diffusion-image-generation`](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion), `image_gen` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# ComfyUI

通过 ComfyUI 生成图像、视频、音频和 3D 内容，使用官方的 `comfy-cli` 进行设置/生命周期管理，并使用直接的 REST/WebSocket API 进行工作流执行。

## 本技能包含的内容

**参考文档 (`references/`):**

- `official-cli.md` — 每个 `comfy ...` 命令及其标志
- `rest-api.md` — REST + WebSocket 端点（本地 + 云端）、负载模式
- `workflow-format.md` — API 格式的 JSON、常见节点类型、参数映射

**脚本 (`scripts/`):**

| 脚本 | 用途 |
|--------|---------|
| `_common.py` | 共享的 HTTP、云端路由、节点目录（不要直接运行） |
| `hardware_check.py` | 探测 GPU/VRAM/磁盘 → 推荐本地运行还是使用 Comfy Cloud |
| `comfyui_setup.sh` | 硬件检查 + comfy-cli + ComfyUI 安装 + 启动 + 验证 |
| `extract_schema.py` | 读取工作流 → 列出可控参数和模型依赖 |
| `check_deps.py` | 根据运行中的服务器检查工作流 → 列出缺失的节点/模型 |
| `auto_fix_deps.py` | 运行 check_deps 然后执行 `comfy node install` / `comfy model download` |
| `run_workflow.py` | 注入参数、提交、监控、下载输出（HTTP 或 WS） |
| `run_batch.py` | 使用参数扫描提交工作流 N 次，并行数量取决于您的套餐等级 |
| `ws_monitor.py` | 用于执行任务的实时 WebSocket 查看器（实时进度） |
| `health_check.py` | 验证检查清单运行器 — comfy-cli + 服务器 + 模型 + 冒烟测试 |
| `fetch_logs.py` | 获取给定 prompt_id 的回溯 / 状态消息 |

**示例工作流 (`workflows/`):** SD 1.5, SDXL, Flux Dev, SDXL img2img, SDXL inpaint, ESRGAN upscale, AnimateDiff video, Wan T2V。请参阅 `workflows/README.md`。

## 使用时机

- 用户要求使用 Stable Diffusion、SDXL、Flux、SD3 等生成图像时
- 用户想要运行特定的 ComfyUI 工作流文件时
- 用户想要链接生成步骤（txt2img → 放大 → 面部修复）时
- 用户需要使用 ControlNet、inpainting、img2img 或其他高级流水线时
- 用户要求管理 ComfyUI 队列、检查模型或安装自定义节点时
- 用户想要通过 AnimateDiff、Hunyuan、Wan、AudioCraft 等生成视频/音频/3D 内容时

## 架构：两层

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────┐
│ 第一层：comfy-cli（官方生命周期工具）                │
│   设置、服务器生命周期、自定义节点、模型              │
│   → comfy install / launch / stop / node / model    │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│ 第二层：REST/WebSocket API + 技能脚本                │
│   工作流执行、参数注入、监控                          │
│   POST /api/prompt, GET /api/view, WS /ws           │
│   → run_workflow.py, run_batch.py, ws_monitor.py    │
└─────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

**为什么是两层？** 官方 CLI 在安装和服务器管理方面非常出色，但对工作流执行的支持有限。REST/WS API 填补了这一空白——脚本处理了 CLI 不做的参数注入、执行监控和输出下载。

## 快速开始

### 检测环境

```bash
# 有什么可用的？
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: installed"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "server: running"

# 这台机器能在本地运行 ComfyUI 吗？（GPU/VRAM/磁盘检查）
python3 scripts/hardware_check.py
```

如果什么都没安装，请参阅下面的 **设置与入门** —— 但请务必先运行硬件检查。

### 一行式健康检查

```bash
python3 scripts/health_check.py
# → JSON: comfy_cli 在 PATH 中吗？服务器可达吗？至少有一个检查点吗？冒烟测试通过吗？
```

## 核心工作流

### 步骤 1：获取 API 格式的工作流 JSON

工作流必须是 API 格式（每个节点都有 `class_type`）。它们来自：

- ComfyUI 网页界面 → **Workflow → Export (API)**（新版界面）或
  旧版界面中的 "Save (API Format)" 按钮
- 本技能的 `workflows/` 目录（可直接运行的示例）
- 社区下载（civitai, Reddit, Discord）—— 通常是编辑器格式，
  必须加载到 ComfyUI 中然后重新导出

编辑器格式（顶层的 `nodes` 和 `links` 数组）**不能直接执行**。脚本会检测到这一点并提示您重新导出。

### 步骤 2：查看哪些参数可控

```bash
python3 scripts/extract_schema.py workflow_api.json --summary-only
# → {"parameter_count": 12, "has_negative_prompt": true, "has_seed": true, ...}

python3 scripts/extract_schema.py workflow_api.json
# → 包含参数、模型依赖、嵌入引用的完整模式
```

### 步骤 3：使用参数运行

```bash
# 本地（默认使用 http://127.0.0.1:8188）
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": -1, "steps": 30}' \
  --output-dir ./outputs

# 云端（导出一次 API 密钥；自动使用正确的 /api 路由）
export COMFY_CLOUD_API_KEY="comfyui-..."
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "..."}' \
  --host https://cloud.comfy.org \
  --output-dir ./outputs

# 通过 WebSocket 实时查看进度（需要 `pip install websocket-client`）
python3 scripts/run_workflow.py \
  --workflow flux_dev.json \
  --args '{"prompt": "..."}' \
  --ws

# img2img / inpaint：传递 --input-image 来自动上传 + 引用
python3 scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}'

# 批量 / 参数扫描：8 个随机种子，并行数量取决于云端套餐限制
python3 scripts/run_batch.py \
  --workflow sdxl.json \
  --args '{"prompt": "abstract"}' \
  --count 8 --randomize-seed --parallel 3 \
  --output-dir ./outputs/batch
```
`-1` 作为 `seed` 值（或使用 `--randomize-seed` 参数省略它）会在每次运行时生成一个全新的随机种子。

### 步骤 4：呈现结果

脚本会向标准输出（stdout）发送描述每个输出文件的 JSON：

```json
{
  "status": "success",
  "prompt_id": "abc-123",
  "outputs": [
    {"file": "./outputs/sdxl_00001_.png", "node_id": "9",
     "type": "image", "filename": "sdxl_00001_.png"}
  ]
}
```

## 决策树

| 用户说 | 工具 | 命令 |
|-----------|------|---------|
| **生命周期 (使用 comfy-cli)** | | |
| "安装 ComfyUI" | comfy-cli | `bash scripts/comfyui_setup.sh` |
| "启动 ComfyUI" | comfy-cli | `comfy launch --background` |
| "停止 ComfyUI" | comfy-cli | `comfy stop` |
| "安装 X 节点" | comfy-cli | `comfy node install <name>` |
| "下载 X 模型" | comfy-cli | `comfy model download --url <url> --relative-path models/checkpoints` |
| "列出已安装的模型" | comfy-cli | `comfy model list` |
| "列出已安装的节点" | comfy-cli | `comfy node show installed` |
| **执行 (使用脚本)** | | |
| "一切就绪了吗？" | script | `health_check.py` (可选 `--workflow X --smoke-test`) |
| "这个工作流里我能改什么？" | script | `extract_schema.py W.json` |
| "检查 W 的依赖是否满足" | script | `check_deps.py W.json` |
| "修复缺失的依赖" | script | `auto_fix_deps.py W.json` |
| "生成一张图片" | script | `run_workflow.py --workflow W --args '{...}'` |
| "使用这张图片" (img2img) | script | `run_workflow.py --input-image image=./x.png ...` |
| "生成 8 个带随机种子的变体" | script | `run_batch.py --count 8 --randomize-seed ...` |
| "给我看实时进度" | script | `ws_monitor.py --prompt-id <id>` |
| "获取任务 X 的错误信息" | script | `fetch_logs.py <prompt_id>` |
| **直接 REST** | | |
| "队列里有什么？" | REST | `curl http://HOST:8188/queue` (本地) 或 `--host https://cloud.comfy.org` |
| "取消那个任务" | REST | `curl -X POST http://HOST:8188/interrupt` |
| "释放 GPU 内存" | REST | `curl -X POST http://HOST:8188/free` |

## 设置与入门

当用户要求设置 ComfyUI 时，**第一件要做的事是询问他们想要 Comfy Cloud（托管式，零安装，需要 API 密钥）还是 Local（在他们的机器上安装 ComfyUI）**。在他们回答之前，不要开始运行安装命令或硬件检查。

**官方文档:** https://docs.comfy.org/installation
**CLI 文档:** https://docs.comfy.org/comfy-cli/getting-started
**Cloud 文档:** https://docs.comfy.org/get_started/cloud
**Cloud API:** https://docs.comfy.org/development/cloud/overview

### 步骤 0：询问本地还是云端（始终第一步）

建议脚本：

> "您想在本地机器上运行 ComfyUI，还是使用 Comfy Cloud？
>
> - **Comfy Cloud** — 托管在 RTX 6000 Pro GPU 上，所有常用模型已预装，零设置。需要 API 密钥（实际运行工作流需要付费订阅；免费层是只读的）。如果您没有合适的 GPU，这是最佳选择。
> - **Local** — 免费，但您的机器**必须**满足硬件要求：
>   - **≥6 GB VRAM** 的 NVIDIA GPU（SDXL 需要 ≥8 GB，Flux/视频需要 ≥12 GB），或
>   - 支持 ROCm 的 AMD GPU（Linux），或
>   - **≥16 GB 统一内存**的 Apple Silicon Mac（M1+）（推荐 ≥32 GB）。
>   - Intel Mac 和没有 GPU 的机器将**无法工作** — 请改用 Cloud。
>
> 您想要哪种方式？"

路由：

- **Cloud** → 跳转到 **路径 A**。
- **Local** → 首先运行硬件检查，然后根据检查结果从路径 B–E 中选择一个路径。
- **不确定** → 运行硬件检查，让检查结果决定。

### 步骤 1：验证硬件（仅在用户选择本地时）

```bash
python3 scripts/hardware_check.py --json
# 可选：同时探测 `torch` 以检查实际的 CUDA/MPS：
python3 scripts/hardware_check.py --json --check-pytorch
```

| 检查结果 | 含义 | 操作 |
|------------|---------------------------------------------------------------|--------|
| `ok` | ≥8 GB VRAM（独立显卡）或 ≥32 GB 统一内存（Apple Silicon） | 本地安装 — 使用报告中的 `comfy_cli_flag` |
| `marginal` | SD1.5 可用；SDXL 勉强；Flux/视频不太可能 | 轻量级工作流可本地运行，否则选择 **路径 A (Cloud)** |
| `cloud` | 无可用 GPU，VRAM <6 GB，Apple 统一内存 <16 GB，Intel Mac，Rosetta Python | **切换到 Cloud**，除非用户明确强制本地安装 |

脚本还会显示 `wsl: true`（WSL2 与 NVIDIA 直通）和 `rosetta: true`（Apple Silicon 上的 x86_64 Python — 必须重新安装为 ARM64）。

如果检查结果是 `cloud` 但用户想要本地安装，不要静默继续。原样显示 `notes` 数组，并询问用户是否想要 (a) 切换到 Cloud 或 (b) 强制本地安装（在现代模型上会导致 OOM 或慢到无法使用）。

### 选择安装路径

首先使用硬件检查。下表是当用户已经告知您其硬件情况时的备用方案：

| 情况 | 推荐路径 |
|-----------|------------------|
| 硬件检查结果为 `verdict: cloud` | **路径 A: Comfy Cloud** |
| 无 GPU / 想在不承诺的情况下尝试 | **路径 A: Comfy Cloud** |
| Windows + NVIDIA + 非技术用户 | **路径 B: ComfyUI Desktop** |
| Windows + NVIDIA + 技术用户 | **路径 C: Portable** 或 **路径 D: comfy-cli** |
| Linux + 任何 GPU | **路径 D: comfy-cli**（最简单） |
| macOS + Apple Silicon | **路径 B: Desktop** 或 **路径 D: comfy-cli** |
| 无头模式 / 服务器 / CI / Agent | **路径 D: comfy-cli** |

对于完全自动化的路径（硬件检查 → 安装 → 启动 → 验证）：

```bash
bash scripts/comfyui_setup.sh
# 或使用覆盖参数：
bash scripts/comfyui_setup.sh --m-series --port=8190 --workspace=/data/comfy
```

它内部运行 `hardware_check.py`，当检查结果为 `cloud` 时拒绝本地安装（除非使用 `--force-cloud-override`），选择正确的 `comfy-cli` 标志，并优先使用 `pipx`/`uvx` 而非全局 `pip` 以避免污染系统 Python。

---

### 路径 A: Comfy Cloud（无需本地安装）

适用于没有合适 GPU 或希望零设置的用户。托管在 RTX 6000 Pro 上。

**文档:** https://docs.comfy.org/get_started/cloud
1. 在 https://comfy.org/cloud 注册
2. 在 https://platform.comfy.org/login 生成 API 密钥
3. 设置密钥：
   ```bash
   export COMFY_CLOUD_API_KEY="comfyui-xxxxxxxxxxxx"
   ```
4. 运行工作流：
   ```bash
   python3 scripts/run_workflow.py \
     --workflow workflows/flux_dev_txt2img.json \
     --args '{"prompt": "..."}' \
     --host https://cloud.comfy.org \
     --output-dir ./outputs
   ```

**定价：** https://www.comfy.org/cloud/pricing
**并发任务数：** 免费版/标准版 1，创作者版 3，专业版 5。免费版**无法通过 API 运行工作流**——只能浏览模型。需要付费订阅才能使用 `/api/prompt`、`/api/upload/*`、`/api/view` 等接口。

---

### 路径 B：ComfyUI 桌面版 (Windows / macOS)

面向非技术用户的一键安装程序。目前处于 Beta 阶段。

**文档：** https://docs.comfy.org/installation/desktop
- **Windows (NVIDIA)：** https://download.comfy.org/windows/nsis/x64
- **macOS (Apple Silicon)：** https://comfy.org

Linux **不支持**桌面版——请使用路径 D。

---

### 路径 C：ComfyUI 便携版 (仅限 Windows)

**文档：** https://docs.comfy.org/installation/comfyui_portable_windows

从 https://github.com/comfyanonymous/ComfyUI/releases 下载，解压后运行 `run_nvidia_gpu.bat`。通过 `update/update_comfyui_stable.bat` 更新。

---

### 路径 D：comfy-cli (全平台——推荐用于 Agent)

官方 CLI 是无头/自动化设置的最佳路径。

**文档：** https://docs.comfy.org/comfy-cli/getting-started

#### 安装 comfy-cli

```bash
# 推荐：
pipx install comfy-cli
# 或者使用 uvx 无需安装：
uvx --from comfy-cli comfy --help
# 或者（如果 pipx/uvx 不可用）：
pip install --user comfy-cli
```

非交互式禁用分析：
```bash
comfy --skip-prompt tracking disable
```

#### 安装 ComfyUI

```bash
comfy --skip-prompt install --nvidia              # NVIDIA (CUDA)
comfy --skip-prompt install --amd                 # AMD (ROCm, Linux)
comfy --skip-prompt install --m-series            # Apple Silicon (MPS)
comfy --skip-prompt install --cpu                 # 仅 CPU (慢)
comfy --skip-prompt install --nvidia --fast-deps  # 基于 uv 的依赖解析
```

默认位置：`~/comfy/ComfyUI` (Linux)，`~/Documents/comfy/ComfyUI` (macOS/Win)。使用 `comfy --workspace /custom/path install` 覆盖。

#### 启动 / 验证

```bash
comfy launch --background                       # 在 :8188 端口启动后台守护进程
comfy launch -- --listen 0.0.0.0 --port 8190    # 可局域网访问的自定义端口
curl -s http://127.0.0.1:8188/system_stats      # 健康检查
```

---

### 路径 E：手动安装 (高级 / 不受支持的硬件)

适用于昇腾 NPU、寒武纪 MLU、Intel Arc 或其他不受支持的硬件。

**文档：** https://docs.comfy.org/installation/manual_install

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

---

### 安装后：下载模型

```bash
# SDXL (通用，~6.5 GB)
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5 (更轻量，~4 GB，适用于 6 GB 显存显卡)
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8 (较小变体，~12 GB)
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI (先设置 token)：
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```

列出已安装模型：`comfy model list`。

### 安装后：安装自定义节点

```bash
comfy node install comfyui-impact-pack             # 流行的工具包
comfy node install comfyui-animatediff-evolved     # 视频生成
comfy node install comfyui-controlnet-aux          # ControlNet 预处理器
comfy node install comfyui-essentials              # 常用辅助工具
comfy node update all
comfy node install-deps --workflow=workflow.json   # 安装工作流所需的一切
```

### 安装后：验证

```bash
python3 scripts/health_check.py
# → comfy_cli 在 PATH 中吗？服务器可达吗？检查点文件？冒烟测试？

python3 scripts/check_deps.py my_workflow.json
# → 此工作流所需的节点/模型/嵌入是否已安装？

python3 scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```

## 图片上传 (img2img / 局部重绘)

最简单的方法是使用 `run_workflow.py` 的 `--input-image` 参数：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it cyberpunk", "denoise": 0.6}'
```

该标志会上传 `photo.png`，然后将其服务器端文件名注入到任何名为 `image` 的模式参数中。对于局部重绘，同时传递两者：

```bash
python3 scripts/run_workflow.py \
  --workflow workflows/sdxl_inpaint.json \
  --input-image image=./photo.png \
  --input-image mask_image=./mask.png \
  --args '{"prompt": "fill with flowers"}'
```

通过 REST 手动上传：
```bash
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# 返回：{"name": "photo.png", "subfolder": "", "type": "input"}

# 云端等效操作：
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```

## 云端特定说明

- **基础 URL：** `https://cloud.comfy.org`
- **认证：** `X-API-Key` 请求头（或 WebSocket 使用 `?token=KEY`）
- **API 密钥：** 设置一次 `$COMFY_CLOUD_API_KEY`，脚本会自动获取
- **输出下载：** `/api/view` 返回一个指向签名 URL 的 302 重定向；脚本会跟随它，并在从存储后端获取之前移除 `X-API-Key`（避免将 API 密钥泄露给 S3/CloudFront）。
- **与本地 ComfyUI 的端点差异：**
  - `/api/object_info`、`/api/queue`、`/api/userdata` —— **免费版返回 403**；仅限付费用户。
  - `/history` 在云端重命名为 `/history_v2`（脚本会自动路由）。
  - `/models/<folder>` 在云端重命名为 `/experiment/models/<folder>`（脚本会自动路由）。
  - WebSocket 中的 `clientId` 目前被忽略——用户的所有连接都接收相同的广播。请在客户端根据 `prompt_id` 进行过滤。
  - 上传时接受 `subfolder` 参数但会被忽略——云端使用扁平命名空间。
- **并发任务数：** 免费版/标准版：1，创作者版：3，专业版：5。额外任务会自动排队。使用 `run_batch.py --parallel N` 来充分利用你的套餐额度。
## 队列与系统管理

```bash
# 本地
curl -s http://127.0.0.1:8188/queue | python3 -m json.tool
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'    # 取消待处理任务
curl -X POST http://127.0.0.1:8188/interrupt                      # 取消运行中任务
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# 云端 — 路径相同，但位于 /api/ 下，此外还有：
python3 scripts/fetch_logs.py --tail-queue --host https://cloud.comfy.org
```

## 常见问题与注意事项

1.  **需要 API 格式** — 所有脚本和 `/api/prompt` 端点都期望 API 格式的工作流 JSON。脚本会检测编辑器格式（顶层的 `nodes` 和 `links` 数组）并提示你通过 "Workflow → Export (API)"（新版 UI）或 "Save (API Format)"（旧版 UI）重新导出。

2.  **服务器必须正在运行** — 所有执行都需要一个活跃的服务器。使用 `comfy launch --background` 启动一个。通过 `curl http://127.0.0.1:8188/system_stats` 验证。

3.  **模型名称必须精确** — 区分大小写，包含文件扩展名。`check_deps.py` 会进行模糊匹配（带或不带扩展名和文件夹前缀），但工作流本身必须使用规范名称。使用 `comfy model list` 来查看已安装的模型。

4.  **缺少自定义节点** — "class_type not found" 意味着所需的节点未安装。`check_deps.py` 会报告需要安装哪个包；`auto_fix_deps.py` 会为你运行安装。

5.  **工作目录** — `comfy-cli` 会自动检测 ComfyUI 工作区。如果命令因 "no workspace found" 而失败，请使用 `comfy --workspace /path/to/ComfyUI <command>` 或 `comfy set-default /path/to/ComfyUI`。

6.  **云端免费层 API 限制** — `/api/prompt`、`/api/view`、`/api/upload/*`、`/api/object_info` 在免费账户上都会返回 403。`health_check.py` 和 `check_deps.py` 会优雅地处理此情况并显示明确的信息。

7.  **视频/音频工作流的超时设置** — 当输出节点是 `VHS_VideoCombine`、`SaveVideo` 等时，会自动检测；默认超时从 300 秒增加到 900 秒。可以使用 `--timeout 1800` 显式覆盖。

8.  **输出文件名中的路径遍历** — 服务器提供的文件名会经过 `safe_path_join` 处理，以防止任何路径逃逸出 `--output-dir`。请保持此保护开启 — 使用自定义保存节点的工作流可能会产生任意路径。

9.  **工作流 JSON 是任意代码** — 自定义节点运行 Python，因此提交未知工作流与执行 `eval` 具有相同的信任风险。在运行来自不受信任来源的工作流之前，请先进行检查。

10. **自动随机化种子** — 在 `--args` 中传递 `seed: -1`（或使用 `--randomize-seed` 并省略种子）以在每次运行时获得新的种子。实际的种子会记录到 stderr。

11. **`tracking` 提示** — 首次运行 `comfy` 可能会提示进行数据分析。使用 `comfy --skip-prompt tracking disable` 以非交互方式跳过。`comfyui_setup.sh` 会为你执行此操作。

## 验证清单

使用 `python3 scripts/health_check.py` 一次性运行整个清单。手动检查：

- [ ] `hardware_check.py` 的结论是 `ok` 或者用户明确选择了 Comfy Cloud
- [ ] `comfy --version` 正常工作（或 `uvx --from comfy-cli comfy --help`）
- [ ] `curl http://HOST:PORT/system_stats` 返回 JSON
- [ ] `comfy model list` 显示至少一个检查点（本地）或者 `/api/experiment/models/checkpoints` 返回模型（云端）
- [ ] 工作流 JSON 是 API 格式
- [ ] `check_deps.py` 报告 `is_ready: true`（或者在云端免费层仅报告 `node_check_skipped`）
- [ ] 使用小型工作流进行测试运行可以完成；输出文件位于 `--output-dir` 中