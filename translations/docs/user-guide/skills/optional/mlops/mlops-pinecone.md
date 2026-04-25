---
title: "Pinecone — 面向生产级 AI 应用的托管向量数据库"
sidebar_label: "Pinecone"
description: "面向生产级 AI 应用的托管向量数据库"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pinecone

面向生产级 AI 应用的托管向量数据库。完全托管、自动扩缩容，支持混合搜索（稠密 + 稀疏向量）、元数据过滤和命名空间。低延迟（p95 <100ms）。用于生产级 RAG、推荐系统或大规模语义搜索。最适合无服务器、托管的基础设施。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/pinecone` 安装 |
| 路径 | `optional-skills/mlops/pinecone` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `pinecone-client` |
| 标签 | `RAG`, `Pinecone`, `向量数据库`, `托管服务`, `无服务器`, `混合搜索`, `生产环境`, `自动扩缩容`, `低延迟`, `推荐系统` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Pinecone - 托管向量数据库

面向生产级 AI 应用的向量数据库。

## 何时使用 Pinecone

**在以下情况使用：**
- 需要托管的、无服务器的向量数据库
- 生产级 RAG 应用
- 需要自动扩缩容
- 低延迟至关重要（<100ms）
- 不想管理基础设施
- 需要混合搜索（稠密 + 稀疏向量）

**指标**:
- 完全托管的 SaaS
- 自动扩缩容至数十亿向量
- **p95 延迟 <100ms**
- 99.9% 正常运行时间 SLA

**改用替代方案的情况**:
- **Chroma**: 自托管，开源
- **FAISS**: 离线，纯相似性搜索
- **Weaviate**: 自托管，功能更多

## 快速开始

### 安装

```bash
pip install pinecone-client
```

### 基本用法

```python
from pinecone import Pinecone, ServerlessSpec

# 初始化
pc = Pinecone(api_key="your-api-key")

# 创建索引
pc.create_index(
    name="my-index",
    dimension=1536,  # 必须与嵌入维度匹配
    metric="cosine",  # 或 "euclidean", "dotproduct"
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

# 连接到索引
index = pc.Index("my-index")

# 插入/更新向量
index.upsert(vectors=[
    {"id": "vec1", "values": [0.1, 0.2, ...], "metadata": {"category": "A"}},
    {"id": "vec2", "values": [0.3, 0.4, ...], "metadata": {"category": "B"}}
])

# 查询
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    include_metadata=True
)

print(results["matches"])
```

## 核心操作

### 创建索引

```python
# 无服务器（推荐）
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",         # 或 "gcp", "azure"
        region="us-east-1"
    )
)

# 基于 Pod（用于一致性能）
from pinecone import PodSpec

pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-east1-gcp",
        pod_type="p1.x1"
    )
)
```

### 插入/更新向量

```python
# 单次插入/更新
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # 1536 维度
        "metadata": {
            "text": "Document content",
            "category": "tutorial",
            "timestamp": "2025-01-01"
        }
    }
])

# 批量插入/更新（推荐）
vectors = [
    {"id": f"vec{i}", "values": embedding, "metadata": metadata}
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas))
]

index.upsert(vectors=vectors, batch_size=100)
```

### 查询向量

```python
# 基本查询
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=10,
    include_metadata=True,
    include_values=False
)

# 带元数据过滤
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    filter={"category": {"$eq": "tutorial"}}
)

# 命名空间查询
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    namespace="production"
)

# 访问结果
for match in results["matches"]:
    print(f"ID: {match['id']}")
    print(f"Score: {match['score']}")
    print(f"Metadata: {match['metadata']}")
```

### 元数据过滤

```python
# 精确匹配
filter = {"category": "tutorial"}

# 比较
filter = {"price": {"$gte": 100}}  # $gt, $gte, $lt, $lte, $ne

# 逻辑运算符
filter = {
    "$and": [
        {"category": "tutorial"},
        {"difficulty": {"$lte": 3}}
    ]
}  # 还有：$or

# In 运算符
filter = {"tags": {"$in": ["python", "ml"]}}
```

## 命名空间

```python
# 按命名空间分区数据
index.upsert(
    vectors=[{"id": "vec1", "values": [...]}],
    namespace="user-123"
)

# 查询特定命名空间
results = index.query(
    vector=[...],
    namespace="user-123",
    top_k=5
)

# 列出命名空间
stats = index.describe_index_stats()
print(stats['namespaces'])
```

## 混合搜索（稠密 + 稀疏）

```python
# 插入带稀疏向量
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # 稠密向量
        "sparse_values": {
            "indices": [10, 45, 123],  # Token ID
            "values": [0.5, 0.3, 0.8]   # TF-IDF 分数
        },
        "metadata": {"text": "..."}
    }
])

# 混合查询
results = index.query(
    vector=[0.1, 0.2, ...],
    sparse_vector={
        "indices": [10, 45],
        "values": [0.5, 0.3]
    },
    top_k=5,
    alpha=0.5  # 0=稀疏，1=稠密，0.5=混合
)
```

## LangChain 集成

```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# 创建向量存储
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index_name="my-index"
)

# 查询
results = vectorstore.similarity_search("query", k=5)

# 带元数据过滤器
results = vectorstore.similarity_search(
    "query",
    k=5,
    filter={"category": "tutorial"}
)

# 作为检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
```

## LlamaIndex 集成

```python
from llama_index.vector_stores.pinecone import PineconeVectorStore

# 连接到 Pinecone
pc = Pinecone(api_key="your-key")
pinecone_index = pc.Index("my-index")

# 创建向量存储
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# 在 LlamaIndex 中使用
from llama_index.core import StorageContext, VectorStoreIndex

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

## 索引管理

```python
# 列出索引
indexes = pc.list_indexes()

# 描述索引
index_info = pc.describe_index("my-index")
print(index_info)

# 获取索引统计信息
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")

# 删除索引
pc.delete_index("my-index")
```

## 删除向量

```python
# 按 ID 删除
index.delete(ids=["vec1", "vec2"])

# 按过滤器删除
index.delete(filter={"category": "old"})

# 删除命名空间中的所有向量
index.delete(delete_all=True, namespace="test")

# 删除整个索引
index.delete(delete_all=True)
```

## 最佳实践

1. **使用无服务器** - 自动扩缩容，成本效益高
2. **批量插入/更新** - 更高效（每批 100-200 个）
3. **添加元数据** - 启用过滤
4. **使用命名空间** - 按用户/租户隔离数据
5. **监控使用情况** - 检查 Pinecone 仪表板
6. **优化过滤器** - 为频繁过滤的字段建立索引
7. **使用免费层测试** - 1 个索引，10 万向量免费
8. **使用混合搜索** - 质量更好
9. **设置合适的维度** - 匹配嵌入模型
10. **定期备份** - 导出重要数据

## 性能

| 操作 | 延迟 | 备注 |
|-----------|---------|-------|
| 插入/更新 | ~50-100ms | 每批次 |
| 查询 (p50) | ~50ms | 取决于索引大小 |
| 查询 (p95) | ~100ms | SLA 目标 |
| 元数据过滤 | ~+10-20ms | 额外开销 |

## 定价（截至 2025 年）

**无服务器**:
- 每百万读取单位 $0.096
- 每百万写入单位 $0.06
- 每 GB 存储/月 $0.06

**免费层**:
- 1 个无服务器索引
- 10 万向量（1536 维度）
- 非常适合原型设计

## 资源

- **网站**: https://www.pinecone.io
- **文档**: https://docs.pinecone.io
- **控制台**: https://app.pinecone.io
- **定价**: https://www.pinecone.io/pricing