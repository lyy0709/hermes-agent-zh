---
title: "Lambda Labs GPU 云 — 用于 ML 训练和推理的预留及按需 GPU 云实例"
sidebar_label: "Lambda Labs GPU 云"
description: "用于 ML 训练和推理的预留及按需 GPU 云实例"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Lambda Labs GPU 云

用于 ML 训练和推理的预留及按需 GPU 云实例。当您需要具有简单 SSH 访问权限、持久性文件系统或用于大规模训练的高性能多节点集群的专用 GPU 实例时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/lambda-labs` 安装 |
| 路径 | `optional-skills/mlops/lambda-labs` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `lambda-cloud-client>=1.0.0` |
| 标签 | `Infrastructure`, `GPU Cloud`, `Training`, `Inference`, `Lambda Labs` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Lambda Labs GPU 云

在 Lambda Labs GPU 云上使用按需实例和 1-Click Clusters 运行 ML 工作负载的完整指南。

## 何时使用 Lambda Labs

**在以下情况使用 Lambda Labs：**
- 需要具有完整 SSH 访问权限的专用 GPU 实例
- 运行长时间的训练任务（数小时到数天）
- 希望获得简单定价且无出口费用
- 需要在会话间保持持久存储
- 需要高性能多节点集群（16-512 个 GPU）
- 希望使用预安装的 ML 堆栈（包含 PyTorch、CUDA、NCCL 的 Lambda Stack）

**主要特性：**
- **GPU 多样性**：B200、H100、GH200、A100、A10、A6000、V100
- **Lambda Stack**：预安装 PyTorch、TensorFlow、CUDA、cuDNN、NCCL
- **持久性文件系统**：在实例重启间保留数据
- **1-Click Clusters**：具有 InfiniBand 的 16-512 GPU Slurm 集群
- **简单定价**：按分钟付费，无出口费用
- **全球区域**：全球 12+ 个区域

**改用其他方案：**
- **Modal**：适用于无服务器、自动扩缩的工作负载
- **SkyPilot**：适用于多云编排和成本优化
- **RunPod**：适用于更便宜的 Spot 实例和无服务器端点
- **Vast.ai**：适用于价格最低的 GPU 市场

## 快速开始

### 账户设置

1. 在 https://lambda.ai 创建账户
2. 添加付款方式
3. 从仪表板生成 API 密钥
4. 添加 SSH 密钥（启动实例前必需）

### 通过控制台启动

1. 访问 https://cloud.lambda.ai/instances
2. 点击 "Launch instance"
3. 选择 GPU 类型和区域
4. 选择 SSH 密钥
5. （可选）附加文件系统
6. 启动并等待 3-15 分钟

### 通过 SSH 连接

```bash
# 从控制台获取实例 IP
ssh ubuntu@<INSTANCE-IP>

# 或使用特定密钥
ssh -i ~/.ssh/lambda_key ubuntu@<INSTANCE-IP>
```

## GPU 实例

### 可用 GPU

| GPU | VRAM | 价格/GPU/小时 | 最佳用途 |
|-----|------|--------------|----------|
| B200 SXM6 | 180 GB | $4.99 | 最大模型，最快训练 |
| H100 SXM | 80 GB | $2.99-3.29 | 大模型训练 |
| H100 PCIe | 80 GB | $2.49 | 性价比高的 H100 |
| GH200 | 96 GB | $1.49 | 单 GPU 大模型 |
| A100 80GB | 80 GB | $1.79 | 生产训练 |
| A100 40GB | 40 GB | $1.29 | 标准训练 |
| A10 | 24 GB | $0.75 | 推理，微调 |
| A6000 | 48 GB | $0.80 | 良好的 VRAM/价格比 |
| V100 | 16 GB | $0.55 | 预算训练 |

### 实例配置

```
8x GPU: 最适合分布式训练 (DDP, FSDP)
4x GPU: 大模型，多 GPU 训练
2x GPU: 中等工作量
1x GPU: 微调，推理，开发
```

### 启动时间

- 单 GPU：3-5 分钟
- 多 GPU：10-15 分钟

## Lambda Stack

所有实例都预装了 Lambda Stack：

```bash
# 包含的软件
- Ubuntu 22.04 LTS
- NVIDIA 驱动程序（最新）
- CUDA 12.x
- cuDNN 8.x
- NCCL（用于多 GPU）
- PyTorch（最新）
- TensorFlow（最新）
- JAX
- JupyterLab
```

### 验证安装

```bash
# 检查 GPU
nvidia-smi

# 检查 PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# 检查 CUDA 版本
nvcc --version
```

## Python API

### 安装

```bash
pip install lambda-cloud-client
```

### 认证

```python
import os
import lambda_cloud_client

# 使用 API 密钥配置
configuration = lambda_cloud_client.Configuration(
    host="https://cloud.lambdalabs.com/api/v1",
    access_token=os.environ["LAMBDA_API_KEY"]
)
```

### 列出可用实例

```python
with lambda_cloud_client.ApiClient(configuration) as api_client:
    api = lambda_cloud_client.DefaultApi(api_client)

    # 获取可用实例类型
    types = api.instance_types()
    for name, info in types.data.items():
        print(f"{name}: {info.instance_type.description}")
```

### 启动实例

```python
from lambda_cloud_client.models import LaunchInstanceRequest

request = LaunchInstanceRequest(
    region_name="us-west-1",
    instance_type_name="gpu_1x_h100_sxm5",
    ssh_key_names=["my-ssh-key"],
    file_system_names=["my-filesystem"],  # 可选
    name="training-job"
)

response = api.launch_instance(request)
instance_id = response.data.instance_ids[0]
print(f"Launched: {instance_id}")
```

### 列出运行中的实例

```python
instances = api.list_instances()
for instance in instances.data:
    print(f"{instance.name}: {instance.ip} ({instance.status})")
```

### 终止实例

```python
from lambda_cloud_client.models import TerminateInstanceRequest

request = TerminateInstanceRequest(
    instance_ids=[instance_id]
)
api.terminate_instance(request)
```

### SSH 密钥管理

```python
from lambda_cloud_client.models import AddSshKeyRequest

# 添加 SSH 密钥
request = AddSshKeyRequest(
    name="my-key",
    public_key="ssh-rsa AAAA..."
)
api.add_ssh_key(request)

# 列出密钥
keys = api.list_ssh_keys()

# 删除密钥
api.delete_ssh_key(key_id)
```

## 使用 curl 的 CLI
### 列出实例类型

```bash
curl -u $LAMBDA_API_KEY: \
  https://cloud.lambdalabs.com/api/v1/instance-types | jq
```

### 启动实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/launch \
  -H "Content-Type: application/json" \
  -d '{
    "region_name": "us-west-1",
    "instance_type_name": "gpu_1x_h100_sxm5",
    "ssh_key_names": ["my-key"]
  }' | jq
```

### 终止实例

```bash
curl -u $LAMBDA_API_KEY: \
  -X POST https://cloud.lambdalabs.com/api/v1/instance-operations/terminate \
  -H "Content-Type: application/json" \
  -d '{"instance_ids": ["<INSTANCE-ID>"]}' | jq
```

## 持久化存储

### 文件系统

文件系统在实例重启后仍保留数据：

```bash
# 挂载位置
/lambda/nfs/<FILESYSTEM_NAME>

# 示例：保存检查点
python train.py --checkpoint-dir /lambda/nfs/my-storage/checkpoints
```

### 创建文件系统

1.  进入 Lambda 控制台的 Storage 页面
2.  点击 "Create filesystem"
3.  选择区域（必须与实例区域匹配）
4.  命名并创建

### 挂载到实例

文件系统必须在实例启动时挂载：
-   通过控制台：启动时选择文件系统
-   通过 API：在启动请求中包含 `file_system_names`

### 最佳实践

```bash
# 存储在文件系统上（持久化）
/lambda/nfs/storage/
  ├── datasets/
  ├── checkpoints/
  ├── models/
  └── outputs/

# 本地 SSD（更快，临时性）
/home/ubuntu/
  └── working/  # 临时文件
```

## SSH 配置

### 添加 SSH 密钥

```bash
# 本地生成密钥
ssh-keygen -t ed25519 -f ~/.ssh/lambda_key

# 将公钥添加到 Lambda 控制台
# 或通过 API 添加
```

### 多个密钥

```bash
# 在实例上，添加更多密钥
echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys
```

### 从 GitHub 导入

```bash
# 在实例上
ssh-import-id gh:username
```

### SSH 隧道

```bash
# 转发 Jupyter
ssh -L 8888:localhost:8888 ubuntu@<IP>

# 转发 TensorBoard
ssh -L 6006:localhost:6006 ubuntu@<IP>

# 多个端口
ssh -L 8888:localhost:8888 -L 6006:localhost:6006 ubuntu@<IP>
```

## JupyterLab

### 从控制台启动

1.  进入 Instances 页面
2.  点击 Cloud IDE 列的 "Launch"
3.  JupyterLab 将在浏览器中打开

### 手动访问

```bash
# 在实例上
jupyter lab --ip=0.0.0.0 --port=8888

# 从本地机器通过隧道访问
ssh -L 8888:localhost:8888 ubuntu@<IP>
# 打开 http://localhost:8888
```

## 训练工作流

### 单 GPU 训练

```bash
# SSH 连接到实例
ssh ubuntu@<IP>

# 克隆仓库
git clone https://github.com/user/project
cd project

# 安装依赖
pip install -r requirements.txt

# 训练
python train.py --epochs 100 --checkpoint-dir /lambda/nfs/storage/checkpoints
```

### 多 GPU 训练（单节点）

```python
# train_ddp.py
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def main():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    device = rank % torch.cuda.device_count()

    model = MyModel().to(device)
    model = DDP(model, device_ids=[device])

    # 训练循环...

if __name__ == "__main__":
    main()
```

```bash
# 使用 torchrun 启动（8 个 GPU）
torchrun --nproc_per_node=8 train_ddp.py
```

### 将检查点保存到文件系统

```python
import os

checkpoint_dir = "/lambda/nfs/my-storage/checkpoints"
os.makedirs(checkpoint_dir, exist_ok=True)

# 保存检查点
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, f"{checkpoint_dir}/checkpoint_{epoch}.pt")
```

## 一键式集群

### 概述

高性能 Slurm 集群，包含：
-   16-512 个 NVIDIA H100 或 B200 GPU
-   NVIDIA Quantum-2 400 Gb/s InfiniBand
-   GPUDirect RDMA，速度达 3200 Gb/s
-   预装的分布式 ML 软件栈

### 包含的软件

-   Ubuntu 22.04 LTS + Lambda Stack
-   NCCL, Open MPI
-   支持 DDP 和 FSDP 的 PyTorch
-   TensorFlow
-   OFED 驱动程序

### 存储

-   每个计算节点 24 TB NVMe（临时性）
-   Lambda 文件系统用于持久化数据

### 多节点训练

```bash
# 在 Slurm 集群上
srun --nodes=4 --ntasks-per-node=8 --gpus-per-node=8 \
  torchrun --nnodes=4 --nproc_per_node=8 \
  --rdzv_backend=c10d --rdzv_endpoint=$MASTER_ADDR:29500 \
  train.py
```

## 网络

### 带宽

-   实例间（同一区域）：最高 200 Gbps
-   互联网出站：最高 20 Gbps

### 防火墙

-   默认：仅开放端口 22 (SSH)
-   在 Lambda 控制台中配置其他端口
-   默认允许 ICMP 流量

### 私有 IP

```bash
# 查找私有 IP
ip addr show | grep 'inet '
```

## 常见工作流

### 工作流 1：微调 LLM

```bash
# 1. 启动带有文件系统的 8x H100 实例

# 2. SSH 连接并设置
ssh ubuntu@<IP>
pip install transformers accelerate peft

# 3. 将模型下载到文件系统
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-hf')
model.save_pretrained('/lambda/nfs/storage/models/llama-2-7b')
"

# 4. 在文件系统上进行微调并保存检查点
accelerate launch --num_processes 8 train.py \
  --model_path /lambda/nfs/storage/models/llama-2-7b \
  --output_dir /lambda/nfs/storage/outputs \
  --checkpoint_dir /lambda/nfs/storage/checkpoints
```

### 工作流 2：批量推理

```bash
# 1. 启动 A10 实例（推理成本效益高）

# 2. 运行推理
python inference.py \
  --model /lambda/nfs/storage/models/fine-tuned \
  --input /lambda/nfs/storage/data/inputs.jsonl \
  --output /lambda/nfs/storage/data/outputs.jsonl
```

## 成本优化

### 选择合适的 GPU

| 任务 | 推荐的 GPU |
|------|-----------------|
| LLM 微调 (7B) | A100 40GB |
| LLM 微调 (70B) | 8x H100 |
| 推理 | A10, A6000 |
| 开发 | V100, A10 |
| 最大性能 | B200 |

### 降低成本

1.  **使用文件系统**：避免重复下载数据
2.  **频繁保存检查点**：恢复中断的训练
3.  **合理配置规模**：不要过度配置 GPU
4.  **终止闲置实例**：无自动停止，需手动终止
### 监控使用情况

- 仪表板显示实时 GPU 利用率
- 提供用于编程监控的 API

## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 实例无法启动 | 检查区域可用性，尝试不同的 GPU |
| SSH 连接被拒绝 | 等待实例初始化（3-15 分钟） |
| 终止后数据丢失 | 使用持久性文件系统 |
| 数据传输缓慢 | 使用同一区域内的文件系统 |
| 未检测到 GPU | 重启实例，检查驱动程序 |

## 参考文档

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/advanced-usage.md)** - 多节点训练、API 自动化
- **[故障排除](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/lambda-labs/references/troubleshooting.md)** - 常见问题及解决方案

## 资源

- **文档**: https://docs.lambda.ai
- **控制台**: https://cloud.lambda.ai
- **定价**: https://lambda.ai/instances
- **支持**: https://support.lambdalabs.com
- **博客**: https://lambda.ai/blog