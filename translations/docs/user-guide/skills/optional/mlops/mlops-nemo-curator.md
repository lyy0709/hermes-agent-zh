---
title: "Nemo Curator — 用于 LLM 训练的 GPU 加速数据整理"
sidebar_label: "Nemo Curator"
description: "用于 LLM 训练的 GPU 加速数据整理"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Nemo Curator

用于 LLM 训练的 GPU 加速数据整理。支持文本/图像/视频/音频。特性包括模糊去重（快 16 倍）、质量过滤（30+ 种启发式方法）、语义去重、PII 脱敏、NSFW 检测。通过 RAPIDS 在多个 GPU 上扩展。用于准备高质量训练数据集、清理网络数据或对大型语料库进行去重。

## 技能元数据

| | |
|---|---|
| 来源 | Optional — 使用 `hermes skills install official/mlops/nemo-curator` 安装 |
| 路径 | `optional-skills/mlops/nemo-curator` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `nemo-curator`, `cudf`, `dask`, `rapids` |
| 标签 | `Data Processing`, `NeMo Curator`, `Data Curation`, `GPU Acceleration`, `Deduplication`, `Quality Filtering`, `NVIDIA`, `RAPIDS`, `PII Redaction`, `Multimodal`, `LLM Training Data` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# NeMo Curator - GPU 加速数据整理

NVIDIA 用于为 LLM 准备高质量训练数据的工具包。

## 何时使用 NeMo Curator

**在以下情况使用 NeMo Curator：**
- 从网络抓取（Common Crawl）准备 LLM 训练数据
- 需要快速去重（比 CPU 快 16 倍）
- 整理多模态数据集（文本、图像、视频、音频）
- 过滤低质量或有毒内容
- 在 GPU 集群上扩展数据处理

**性能**：
- **模糊去重快 16 倍**（8TB RedPajama v2）
- 与 CPU 替代方案相比**总拥有成本降低 40%**
- 在 GPU 节点间**接近线性扩展**

**改用替代方案的情况**：
- **datatrove**：基于 CPU 的开源数据处理
- **dolma**：Allen AI 的数据工具包
- **Ray Data**：通用 ML 数据处理（无整理重点）

## 快速开始

### 安装

```bash
# 文本整理 (CUDA 12)
uv pip install "nemo-curator[text_cuda12]"

# 所有模态
uv pip install "nemo-curator[all_cuda12]"

# 仅 CPU（较慢）
uv pip install "nemo-curator[cpu]"
```

### 基础文本整理流水线

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.datasets import DocumentDataset
import pandas as pd

# 加载数据
df = pd.DataFrame({"text": ["Good document", "Bad doc", "Excellent text"]})
dataset = DocumentDataset(df)

# 质量过滤
def quality_score(doc):
    return len(doc["text"].split()) > 5  # 过滤短文档

filtered = ScoreFilter(quality_score)(dataset)

# 去重
from nemo_curator.modules import ExactDuplicates
deduped = ExactDuplicates()(filtered)

# 保存
deduped.to_parquet("curated_data/")
```

## 数据整理流水线

### 阶段 1：质量过滤

```python
from nemo_curator.filters import (
    WordCountFilter,
    RepeatedLinesFilter,
    UrlRatioFilter,
    NonAlphaNumericFilter
)

# 应用 30+ 种启发式过滤器
from nemo_curator import ScoreFilter

# 词数过滤器
dataset = dataset.filter(WordCountFilter(min_words=50, max_words=100000))

# 移除重复内容
dataset = dataset.filter(RepeatedLinesFilter(max_repeated_line_fraction=0.3))

# URL 比例过滤器
dataset = dataset.filter(UrlRatioFilter(max_url_ratio=0.2))
```

### 阶段 2：去重

**精确去重**：
```python
from nemo_curator.modules import ExactDuplicates

# 移除完全重复项
deduped = ExactDuplicates(id_field="id", text_field="text")(dataset)
```

**模糊去重**（在 GPU 上快 16 倍）：
```python
from nemo_curator.modules import FuzzyDuplicates

# MinHash + LSH 去重
fuzzy_dedup = FuzzyDuplicates(
    id_field="id",
    text_field="text",
    num_hashes=260,      # MinHash 参数
    num_buckets=20,
    hash_method="md5"
)

deduped = fuzzy_dedup(dataset)
```

**语义去重**：
```python
from nemo_curator.modules import SemanticDuplicates

# 基于嵌入的去重
semantic_dedup = SemanticDuplicates(
    id_field="id",
    text_field="text",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    threshold=0.8  # 余弦相似度阈值
)

deduped = semantic_dedup(dataset)
```

### 阶段 3：PII 脱敏

```python
from nemo_curator.modules import Modify
from nemo_curator.modifiers import PIIRedactor

# 脱敏个人可识别信息
pii_redactor = PIIRedactor(
    supported_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION"],
    anonymize_action="replace"  # 或 "redact"
)

redacted = Modify(pii_redactor)(dataset)
```

### 阶段 4：分类器过滤

```python
from nemo_curator.classifiers import QualityClassifier

# 质量分类
quality_clf = QualityClassifier(
    model_path="nvidia/quality-classifier-deberta",
    batch_size=256,
    device="cuda"
)

# 过滤低质量文档
high_quality = dataset.filter(lambda doc: quality_clf(doc["text"]) > 0.5)
```

## GPU 加速

### GPU 与 CPU 性能对比

| 操作 | CPU (16 核) | GPU (A100) | 加速比 |
|-----------|----------------|------------|---------|
| 模糊去重 (8TB) | 120 小时 | 7.5 小时 | 16× |
| 精确去重 (1TB) | 8 小时 | 0.5 小时 | 16× |
| 质量过滤 | 2 小时 | 0.2 小时 | 10× |

### 多 GPU 扩展

```python
from nemo_curator import get_client
import dask_cuda

# 初始化 GPU 集群
client = get_client(cluster_type="gpu", n_workers=8)

# 使用 8 个 GPU 处理
deduped = FuzzyDuplicates(...)(dataset)
```

## 多模态整理

### 图像整理

```python
from nemo_curator.image import (
    AestheticFilter,
    NSFWFilter,
    CLIPEmbedder
)

# 美学评分
aesthetic_filter = AestheticFilter(threshold=5.0)
filtered_images = aesthetic_filter(image_dataset)

# NSFW 检测
nsfw_filter = NSFWFilter(threshold=0.9)
safe_images = nsfw_filter(filtered_images)

# 生成 CLIP 嵌入
clip_embedder = CLIPEmbedder(model="openai/clip-vit-base-patch32")
image_embeddings = clip_embedder(safe_images)
```

### 视频整理

```python
from nemo_curator.video import (
    SceneDetector,
    ClipExtractor,
    InternVideo2Embedder
)

# 检测场景
scene_detector = SceneDetector(threshold=27.0)
scenes = scene_detector(video_dataset)

# 提取片段
clip_extractor = ClipExtractor(min_duration=2.0, max_duration=10.0)
clips = clip_extractor(scenes)

# 生成嵌入
video_embedder = InternVideo2Embedder()
video_embeddings = video_embedder(clips)
```

### 音频整理

```python
from nemo_curator.audio import (
    ASRInference,
    WERFilter,
    DurationFilter
)

# ASR 转录
asr = ASRInference(model="nvidia/stt_en_fastconformer_hybrid_large_pc")
transcribed = asr(audio_dataset)

# 按 WER（词错误率）过滤
wer_filter = WERFilter(max_wer=0.3)
high_quality_audio = wer_filter(transcribed)

# 时长过滤
duration_filter = DurationFilter(min_duration=1.0, max_duration=30.0)
filtered_audio = duration_filter(high_quality_audio)
```

## 常见模式

### 网络抓取整理 (Common Crawl)

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.filters import *
from nemo_curator.modules import *
from nemo_curator.datasets import DocumentDataset

# 加载 Common Crawl 数据
dataset = DocumentDataset.read_parquet("common_crawl/*.parquet")

# 流水线
pipeline = [
    # 1. 质量过滤
    WordCountFilter(min_words=100, max_words=50000),
    RepeatedLinesFilter(max_repeated_line_fraction=0.2),
    SymbolToWordRatioFilter(max_symbol_to_word_ratio=0.3),
    UrlRatioFilter(max_url_ratio=0.3),

    # 2. 语言过滤
    LanguageIdentificationFilter(target_languages=["en"]),

    # 3. 去重
    ExactDuplicates(id_field="id", text_field="text"),
    FuzzyDuplicates(id_field="id", text_field="text", num_hashes=260),

    # 4. PII 脱敏
    PIIRedactor(),

    # 5. NSFW 过滤
    NSFWClassifier(threshold=0.8)
]

# 执行
for stage in pipeline:
    dataset = stage(dataset)

# 保存
dataset.to_parquet("curated_common_crawl/")
```

### 分布式处理

```python
from nemo_curator import get_client
from dask_cuda import LocalCUDACluster

# 多 GPU 集群
cluster = LocalCUDACluster(n_workers=8)
client = get_client(cluster=cluster)

# 处理大型数据集
dataset = DocumentDataset.read_parquet("s3://large_dataset/*.parquet")
deduped = FuzzyDuplicates(...)(dataset)

# 清理
client.close()
cluster.close()
```

## 性能基准测试

### 模糊去重 (8TB RedPajama v2)

- **CPU (256 核)**: 120 小时
- **GPU (8× A100)**: 7.5 小时
- **加速比**: 16×

### 精确去重 (1TB)

- **CPU (64 核)**: 8 小时
- **GPU (4× A100)**: 0.5 小时
- **加速比**: 16×

### 质量过滤 (100GB)

- **CPU (32 核)**: 2 小时
- **GPU (2× A100)**: 0.2 小时
- **加速比**: 10×

## 成本对比

**基于 CPU 的整理** (AWS c5.18xlarge × 10):
- 成本: $3.60/小时 × 10 = $36/小时
- 处理 8TB 时间: 120 小时
- **总计**: $4,320

**基于 GPU 的整理** (AWS p4d.24xlarge × 2):
- 成本: $32.77/小时 × 2 = $65.54/小时
- 处理 8TB 时间: 7.5 小时
- **总计**: $491.55

**节省**: 减少 89%（节省 $3,828）

## 支持的数据格式

- **输入**: Parquet, JSONL, CSV
- **输出**: Parquet（推荐）, JSONL
- **WebDataset**: 用于多模态的 TAR 归档

## 使用案例

**生产部署**：
- NVIDIA 使用 NeMo Curator 准备 Nemotron-4 训练数据
- 整理的开源数据集: RedPajama v2, The Pile

## 参考资料

- **[过滤指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/filtering.md)** - 30+ 种质量过滤器、启发式方法
- **[去重指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/deduplication.md)** - 精确、模糊、语义方法

## 资源

- **GitHub**: https://github.com/NVIDIA/NeMo-Curator ⭐ 500+
- **文档**: https://docs.nvidia.com/nemo-framework/user-guide/latest/datacuration/
- **版本**: 0.4.0+
- **许可证**: Apache 2.0