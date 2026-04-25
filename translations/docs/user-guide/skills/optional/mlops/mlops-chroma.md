---
title: "Chroma — 面向 AI 应用的开源嵌入数据库"
sidebar_label: "Chroma"
description: "面向 AI 应用的开源嵌入数据库"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Chroma

面向 AI 应用的开源嵌入数据库。存储嵌入向量和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。可从笔记本扩展到生产集群。用于语义搜索、RAG 应用或文档检索。最适合本地开发和开源项目。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/chroma` 安装 |
| 路径 | `optional-skills/mlops/chroma` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `chromadb`, `sentence-transformers` |
| 标签 | `RAG`, `Chroma`, `向量数据库`, `嵌入`, `语义搜索`, `开源`, `自托管`, `文档检索`, `元数据过滤` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Chroma - 开源嵌入数据库

用于构建具有记忆的 LLM 应用的 AI 原生数据库。

## 何时使用 Chroma

**在以下情况下使用 Chroma：**
- 构建 RAG（检索增强生成）应用
- 需要本地/自托管的向量数据库
- 想要开源解决方案（Apache 2.0）
- 在笔记本中进行原型设计
- 对文档进行语义搜索
- 存储带有元数据的嵌入向量

**指标**：
- **24,300+ GitHub stars**
- **1,900+ forks**
- **v1.3.3**（稳定版，每周发布）
- **Apache 2.0 许可证**

**改用替代方案的情况**：
- **Pinecone**：托管云服务，自动扩缩容
- **FAISS**：纯相似性搜索，无元数据
- **Weaviate**：生产级 ML 原生数据库
- **Qdrant**：高性能，基于 Rust

## 快速开始

### 安装

```bash
# Python
pip install chromadb

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

### 基本用法（Python）

```python
import chromadb

# 创建客户端
client = chromadb.Client()

# 创建集合
collection = client.create_collection(name="my_collection")

# 添加文档
collection.add(
    documents=["This is document 1", "This is document 2"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# 查询
results = collection.query(
    query_texts=["document about topic"],
    n_results=2
)

print(results)
```

## 核心操作

### 1. 创建集合

```python
# 简单集合
collection = client.create_collection("my_docs")

# 使用自定义嵌入函数
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="my_docs",
    embedding_function=openai_ef
)

# 获取现有集合
collection = client.get_collection("my_docs")

# 删除集合
client.delete_collection("my_docs")
```

### 2. 添加文档

```python
# 使用自动生成的 ID 添加
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)

# 使用自定义嵌入向量添加
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

### 3. 查询（相似性搜索）

```python
# 基本查询
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# 带过滤器的查询
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# 带元数据过滤器的查询
results = collection.query(
    query_texts=["advanced topics"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }
)

# 访问结果
print(results["documents"])      # 匹配文档列表
print(results["metadatas"])      # 每个文档的元数据
print(results["distances"])      # 相似性分数
print(results["ids"])            # 文档 ID
```

### 4. 获取文档

```python
# 按 ID 获取
docs = collection.get(
    ids=["id1", "id2"]
)

# 使用过滤器获取
docs = collection.get(
    where={"category": "tutorial"},
    limit=10
)

# 获取所有文档
docs = collection.get()
```

### 5. 更新文档

```python
# 更新文档内容
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)
```

### 6. 删除文档

```python
# 按 ID 删除
collection.delete(ids=["id1", "id2"])

# 使用过滤器删除
collection.delete(
    where={"source": "outdated"}
)
```

## 持久化存储

```python
# 持久化到磁盘
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.create_collection("my_docs")
collection.add(documents=["Doc 1"], ids=["id1"])

# 数据自动持久化
# 稍后使用相同路径重新加载
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
```

## 嵌入函数

### 默认（Sentence Transformers）

```python
# 默认使用 sentence-transformers
collection = client.create_collection("my_docs")
# 默认模型：all-MiniLM-L6-v2
```

### OpenAI

```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

### HuggingFace

```python
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key="your-key",
    model_name="sentence-transformers/all-mpnet-base-v2"
)

collection = client.create_collection(
    name="hf_docs",
    embedding_function=huggingface_ef
)
```

### 自定义嵌入函数

```python
from chromadb import Documents, EmbeddingFunction, Embeddings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # 你的嵌入逻辑
        return embeddings

my_ef = MyEmbeddingFunction()
collection = client.create_collection(
    name="custom_docs",
    embedding_function=my_ef
)
```

## 元数据过滤

```python
# 精确匹配
results = collection.query(
    query_texts=["query"],
    where={"category": "tutorial"}
)

# 比较运算符
results = collection.query(
    query_texts=["query"],
    where={"page": {"$gt": 10}}  # $gt, $gte, $lt, $lte, $ne
)

# 逻辑运算符
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$lte": 3}}
        ]
    }  # 还有：$or
)

# 包含
results = collection.query(
    query_texts=["query"],
    where={"tags": {"$in": ["python", "ml"]}}
)
```

## LangChain 集成

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 分割文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# 创建 Chroma 向量存储
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# 查询
results = vectorstore.similarity_search("machine learning", k=3)

# 作为检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

## LlamaIndex 集成

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import chromadb

# 初始化 Chroma
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")

# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# 查询
query_engine = index.as_query_engine()
response = query_engine.query("What is machine learning?")
```

## 服务器模式

```python
# 运行 Chroma 服务器
# 终端：chroma run --path ./chroma_db --port 8000

# 连接到服务器
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

# 正常使用
collection = client.get_or_create_collection("my_docs")
```

## 最佳实践

1. **使用持久化客户端** - 重启时不会丢失数据
2. **添加元数据** - 支持过滤和追踪
3. **批量操作** - 一次添加多个文档
4. **选择合适的嵌入模型** - 平衡速度和质量
5. **使用过滤器** - 缩小搜索空间
6. **唯一 ID** - 避免冲突
7. **定期备份** - 复制 chroma_db 目录
8. **监控集合大小** - 需要时进行扩展
9. **测试嵌入函数** - 确保质量
10. **生产环境使用服务器模式** - 更适合多用户

## 性能

| 操作 | 延迟 | 备注 |
|-----------|---------|-------|
| 添加 100 个文档 | ~1-3s | 包含嵌入 |
| 查询（前 10 个） | ~50-200ms | 取决于集合大小 |
| 元数据过滤 | ~10-50ms | 使用适当的索引时很快 |

## 资源

- **GitHub**: https://github.com/chroma-core/chroma ⭐ 24,300+
- **文档**: https://docs.trychroma.com
- **Discord**: https://discord.gg/MMeYNTmh3x
- **版本**: 1.3.3+
- **许可证**: Apache 2.0