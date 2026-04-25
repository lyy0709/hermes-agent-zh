---
title: "Faiss — Facebook 用于高效相似性搜索和稠密向量聚类的库"
sidebar_label: "Faiss"
description: "Facebook 用于高效相似性搜索和稠密向量聚类的库"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Faiss

Facebook 用于高效相似性搜索和稠密向量聚类的库。支持数十亿向量、GPU 加速和各种索引类型（Flat、IVF、HNSW）。用于快速 k-NN 搜索、大规模向量检索，或当你需要纯相似性搜索而无需元数据过滤时。最适合高性能应用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/faiss` 安装 |
| 路径 | `optional-skills/mlops/faiss` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `faiss-cpu`, `faiss-gpu`, `numpy` |
| 标签 | `RAG`, `FAISS`, `相似性搜索`, `向量搜索`, `Facebook AI`, `GPU 加速`, `十亿规模`, `K-NN`, `HNSW`, `高性能`, `大规模` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# FAISS - 高效相似性搜索

Facebook AI 用于十亿规模向量相似性搜索的库。

## 何时使用 FAISS

**在以下情况使用 FAISS：**
- 需要对大型向量数据集（百万/十亿级）进行快速相似性搜索
- 需要 GPU 加速
- 纯向量相似性（无需元数据过滤）
- 高吞吐量、低延迟至关重要
- 嵌入的离线/批处理

**指标**：
- **GitHub 星标 31,700+**
- Meta/Facebook AI Research
- **处理数十亿向量**
- **C++** 并带有 Python 绑定

**改用替代方案的情况**：
- **Chroma/Pinecone**：需要元数据过滤
- **Weaviate**：需要完整的数据库功能
- **Annoy**：更简单，功能较少

## 快速开始

### 安装

```bash
# 仅 CPU
pip install faiss-cpu

# GPU 支持
pip install faiss-gpu
```

### 基本用法

```python
import faiss
import numpy as np

# 创建示例数据（1000 个向量，128 维）
d = 128
nb = 1000
vectors = np.random.random((nb, d)).astype('float32')

# 创建索引
index = faiss.IndexFlatL2(d)  # L2 距离
index.add(vectors)             # 添加向量

# 搜索
k = 5  # 查找 5 个最近邻
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)

print(f"Nearest neighbors: {indices}")
print(f"Distances: {distances}")
```

## 索引类型

### 1. Flat（精确搜索）

```python
# L2（欧几里得）距离
index = faiss.IndexFlatL2(d)

# 内积（归一化后为余弦相似度）
index = faiss.IndexFlatIP(d)

# 最慢，最准确
```

### 2. IVF（倒排文件） - 快速近似

```python
# 创建量化器
quantizer = faiss.IndexFlatL2(d)

# 具有 100 个簇的 IVF 索引
nlist = 100
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# 在数据上训练
index.train(vectors)

# 添加向量
index.add(vectors)

# 搜索（nprobe = 要搜索的簇数）
index.nprobe = 10
distances, indices = index.search(query, k)
```

### 3. HNSW（分层可导航小世界） - 最佳质量/速度

```python
# HNSW 索引
M = 32  # 每层连接数
index = faiss.IndexHNSWFlat(d, M)

# 无需训练
index.add(vectors)

# 搜索
distances, indices = index.search(query, k)
```

### 4. 乘积量化 - 内存高效

```python
# PQ 将内存减少 16-32 倍
m = 8   # 子量化器数量
nbits = 8
index = faiss.IndexPQ(d, m, nbits)

# 训练并添加
index.train(vectors)
index.add(vectors)
```

## 保存和加载

```python
# 保存索引
faiss.write_index(index, "large.index")

# 加载索引
index = faiss.read_index("large.index")

# 继续使用
distances, indices = index.search(query, k)
```

## GPU 加速

```python
# 单 GPU
res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatL2(d)
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # GPU 0

# 多 GPU
index_gpu = faiss.index_cpu_to_all_gpus(index_cpu)

# 比 CPU 快 10-100 倍
```

## LangChain 集成

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 创建 FAISS 向量存储
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())

# 保存
vectorstore.save_local("faiss_index")

# 加载
vectorstore = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

# 搜索
results = vectorstore.similarity_search("query", k=5)
```

## LlamaIndex 集成

```python
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# 创建 FAISS 索引
d = 1536
faiss_index = faiss.IndexFlatL2(d)

vector_store = FaissVectorStore(faiss_index=faiss_index)
```

## 最佳实践

1. **选择正确的索引类型** - Flat 用于 &lt;10K，IVF 用于 10K-1M，HNSW 用于质量
2. **为余弦相似度归一化** - 对归一化向量使用 IndexFlatIP
3. **对大型数据集使用 GPU** - 快 10-100 倍
4. **保存训练好的索引** - 训练成本高
5. **调整 nprobe/ef_search** - 平衡速度/精度
6. **监控内存** - 对大型数据集使用 PQ
7. **批量查询** - 更好的 GPU 利用率

## 性能

| 索引类型 | 构建时间 | 搜索时间 | 内存 | 准确率 |
|------------|------------|-------------|--------|----------|
| Flat | 快 | 慢 | 高 | 100% |
| IVF | 中等 | 快 | 中等 | 95-99% |
| HNSW | 慢 | 最快 | 高 | 99% |
| PQ | 中等 | 快 | 低 | 90-95% |

## 资源

- **GitHub**: https://github.com/facebookresearch/faiss ⭐ 31,700+
- **Wiki**: https://github.com/facebookresearch/faiss/wiki
- **许可证**: MIT