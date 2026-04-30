---
title: "Outlines — Outlines：结构化 JSON/正则表达式/Pydantic LLM 生成"
sidebar_label: "Outlines"
description: "Outlines：结构化 JSON/正则表达式/Pydantic LLM 生成"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Outlines

Outlines：结构化 JSON/正则表达式/Pydantic LLM 生成。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/outlines` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `outlines`, `transformers`, `vllm`, `pydantic` |
| 标签 | `Prompt Engineering`, `Outlines`, `Structured Generation`, `JSON Schema`, `Pydantic`, `Local Models`, `Grammar-Based Generation`, `vLLM`, `Transformers`, `Type Safety` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Outlines：结构化文本生成

## 何时使用此技能

在以下情况下使用 Outlines：
- **保证生成有效的 JSON/XML/代码** 结构
- 使用 **Pydantic 模型** 进行类型安全的输出
- **支持本地模型**（Transformers、llama.cpp、vLLM）
- 通过零开销的结构化生成 **最大化推理速度**
- **根据 JSON 模式** 自动生成
- 在语法级别 **控制 Token 采样**

**GitHub Stars**: 8,000+ | **来自**: dottxt.ai (formerly .txt)

## 安装

```bash
# 基础安装
pip install outlines

# 使用特定后端
pip install outlines transformers  # Hugging Face 模型
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # vLLM 用于高吞吐量
```

## 快速开始

### 基础示例：分类

```python
import outlines
from typing import Literal

# 加载模型
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 使用类型约束生成
prompt = "Sentiment of 'This product is amazing!': "
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive" (保证是其中之一)
```

### 使用 Pydantic 模型

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 生成结构化输出
prompt = "Extract user: John Doe, 30 years old, john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

## 核心概念

### 1. 约束 Token 采样

Outlines 使用有限状态机（FSM）在 logit 级别约束 Token 生成。

**工作原理：**
1. 将模式（JSON/Pydantic/正则表达式）转换为上下文无关语法（CFG）
2. 将 CFG 转换为有限状态机（FSM）
3. 在生成过程中每一步过滤无效 Token
4. 当只有一个有效 Token 时快速前进

**优势：**
- **零开销**：过滤发生在 Token 级别
- **速度提升**：快速通过确定性路径
- **保证有效性**：不可能产生无效输出

```python
import outlines

# Pydantic 模型 -> JSON 模式 -> CFG -> FSM
class Person(BaseModel):
    name: str
    age: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 幕后过程：
# 1. Person -> JSON 模式
# 2. JSON 模式 -> CFG
# 3. CFG -> FSM
# 4. FSM 在生成过程中过滤 Token

generator = outlines.generate.json(model, Person)
result = generator("Generate person: Alice, 25")
```

### 2. 结构化生成器

Outlines 为不同的输出类型提供专门的生成器。

#### 选择生成器

```python
# 多项选择
generator = outlines.generate.choice(
    model,
    ["positive", "negative", "neutral"]
)

sentiment = generator("Review: This is great!")
# 结果：三个选项之一
```

#### JSON 生成器

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# 生成符合模式的有效 JSON
generator = outlines.generate.json(model, Product)
product = generator("Extract: iPhone 15, $999, available")

# 保证是有效的 Product 实例
print(type(product))  # <class '__main__.Product'>
```

#### 正则表达式生成器

```python
# 生成匹配正则表达式的文本
generator = outlines.generate.regex(
    model,
    r"[0-9]{3}-[0-9]{3}-[0-9]{4}"  # 电话号码模式
)

phone = generator("Generate phone number:")
# 结果："555-123-4567" (保证匹配模式)
```

#### 整数/浮点数生成器

```python
# 生成特定数值类型
int_generator = outlines.generate.integer(model)
age = int_generator("Person's age:")  # 保证是整数

float_generator = outlines.generate.float(model)
price = float_generator("Product price:")  # 保证是浮点数
```

### 3. 模型后端

Outlines 支持多个本地和基于 API 的后端。

#### Transformers (Hugging Face)

```python
import outlines

# 从 Hugging Face 加载
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"  # 或 "cpu"
)

# 与任何生成器一起使用
generator = outlines.generate.json(model, YourModel)
```

#### llama.cpp

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

generator = outlines.generate.json(model, YourModel)
```

#### vLLM (高吞吐量)

```python
# 用于生产部署
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2  # 多 GPU
)

generator = outlines.generate.json(model, YourModel)
```

#### OpenAI (有限支持)

```python
# 基础 OpenAI 支持
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key"
)

# 注意：API 模型的部分功能受限
generator = outlines.generate.json(model, YourModel)
```
### 4. Pydantic 集成

Outlines 提供一流的 Pydantic 支持，支持自动模式转换。

#### 基础模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Number of words", gt=0)
    tags: list[str] = Field(description="List of tags")

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, Article)

article = generator("Generate article about AI")
print(article.title)
print(article.word_count)  # Guaranteed > 0
```

#### 嵌套模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # Nested model

generator = outlines.generate.json(model, Person)
person = generator("Generate person in New York")

print(person.address.city)  # "New York"
```

#### 枚举和字面量

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status  # Must be one of enum values
    priority: Literal["low", "medium", "high"]  # Must be one of literals

generator = outlines.generate.json(model, Application)
app = generator("Generate application")

print(app.status)  # Status.PENDING (or APPROVED/REJECTED)
```

## 常用模式

### 模式 1：数据提取

```python
from pydantic import BaseModel
import outlines

class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, CompanyInfo)

text = """
Apple Inc. was founded in 1976 in the technology industry.
The company employs approximately 164,000 people worldwide.
"""

prompt = f"Extract company information:\n{text}\n\nCompany:"
company = generator(prompt)

print(f"Name: {company.name}")
print(f"Founded: {company.founded_year}")
print(f"Industry: {company.industry}")
print(f"Employees: {company.employees}")
```

### 模式 2：分类

```python
from typing import Literal
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Binary classification
generator = outlines.generate.choice(model, ["spam", "not_spam"])
result = generator("Email: Buy now! 50% off!")

# Multi-class classification
categories = ["technology", "business", "sports", "entertainment"]
category_gen = outlines.generate.choice(model, categories)
category = category_gen("Article: Apple announces new iPhone...")

# With confidence
class Classification(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

classifier = outlines.generate.json(model, Classification)
result = classifier("Review: This product is okay, nothing special")
```

### 模式 3：结构化表单

```python
class UserProfile(BaseModel):
    full_name: str
    age: int
    email: str
    phone: str
    country: str
    interests: list[str]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, UserProfile)

prompt = """
Extract user profile from:
Name: Alice Johnson
Age: 28
Email: alice@example.com
Phone: 555-0123
Country: USA
Interests: hiking, photography, cooking
"""

profile = generator(prompt)
print(profile.full_name)
print(profile.interests)  # ["hiking", "photography", "cooking"]
```

### 模式 4：多实体提取

```python
class Entity(BaseModel):
    name: str
    type: Literal["PERSON", "ORGANIZATION", "LOCATION"]

class DocumentEntities(BaseModel):
    entities: list[Entity]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, DocumentEntities)

text = "Tim Cook met with Satya Nadella at Microsoft headquarters in Redmond."
prompt = f"Extract entities from: {text}"

result = generator(prompt)
for entity in result.entities:
    print(f"{entity.name} ({entity.type})")
```

### 模式 5：代码生成

```python
class PythonFunction(BaseModel):
    function_name: str
    parameters: list[str]
    docstring: str
    body: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, PythonFunction)

prompt = "Generate a Python function to calculate factorial"
func = generator(prompt)

print(f"def {func.function_name}({', '.join(func.parameters)}):")
print(f'    """{func.docstring}"""')
print(f"    {func.body}")
```

### 模式 6：批量处理

```python
def batch_extract(texts: list[str], schema: type[BaseModel]):
    """Extract structured data from multiple texts."""
    model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
    generator = outlines.generate.json(model, schema)

    results = []
    for text in texts:
        result = generator(f"Extract from: {text}")
        results.append(result)

    return results

class Person(BaseModel):
    name: str
    age: int

texts = [
    "John is 30 years old",
    "Alice is 25 years old",
    "Bob is 40 years old"
]

people = batch_extract(texts, Person)
for person in people:
    print(f"{person.name}: {person.age}")
```

## 后端配置

### Transformers

```python
import outlines

# Basic usage
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# GPU configuration
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# Popular models
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
```

### llama.cpp

```python
# Load GGUF model
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,         # Context window
    n_gpu_layers=35,    # GPU layers
    n_threads=8         # CPU threads
)

# Full GPU offload
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_gpu_layers=-1  # All layers on GPU
)
```
### vLLM（生产环境）

```python
# 单 GPU
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

# 多 GPU
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4  # 4 个 GPU
)

# 使用量化
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="awq"  # 或 "gptq"
)
```

## 最佳实践

### 1. 使用具体类型

```python
# ✅ 良好：具体类型
class Product(BaseModel):
    name: str
    price: float  # 不是 str
    quantity: int  # 不是 str
    in_stock: bool  # 不是 str

# ❌ 不佳：所有字段都用字符串
class Product(BaseModel):
    name: str
    price: str  # 应该是 float
    quantity: str  # 应该是 int
```

### 2. 添加约束

```python
from pydantic import Field

# ✅ 良好：带约束
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# ❌ 不佳：无约束
class User(BaseModel):
    name: str
    age: int
    email: str
```

### 3. 对分类使用枚举

```python
# ✅ 良好：枚举用于固定集合
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority

# ❌ 不佳：自由格式字符串
class Task(BaseModel):
    title: str
    priority: str  # 可以是任何内容
```

### 4. 在提示词中提供上下文

```python
# ✅ 良好：清晰的上下文
prompt = """
从以下文本中提取产品信息。
文本：iPhone 15 Pro 售价 999 美元，目前有货。
产品：
"""

# ❌ 不佳：最少的上下文
prompt = "iPhone 15 Pro 售价 999 美元，目前有货。"
```

### 5. 处理可选字段

```python
from typing import Optional

# ✅ 良好：可选字段用于不完整数据
class Article(BaseModel):
    title: str  # 必需
    author: Optional[str] = None  # 可选
    date: Optional[str] = None  # 可选
    tags: list[str] = []  # 默认空列表

# 即使缺少作者/日期也能成功
```

## 与其他方案的比较

| 特性 | Outlines | Instructor | Guidance | LMQL |
|---------|----------|------------|----------|------|
| Pydantic 支持 | ✅ 原生 | ✅ 原生 | ❌ 无 | ❌ 无 |
| JSON Schema | ✅ 是 | ✅ 是 | ⚠️ 有限 | ✅ 是 |
| 正则表达式约束 | ✅ 是 | ❌ 无 | ✅ 是 | ✅ 是 |
| 本地模型 | ✅ 完整 | ⚠️ 有限 | ✅ 完整 | ✅ 完整 |
| API 模型 | ⚠️ 有限 | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| 零开销 | ✅ 是 | ❌ 无 | ⚠️ 部分 | ✅ 是 |
| 自动重试 | ❌ 无 | ✅ 是 | ❌ 无 | ❌ 无 |
| 学习曲线 | 低 | 低 | 低 | 高 |

**何时选择 Outlines：**
- 使用本地模型（Transformers, llama.cpp, vLLM）
- 需要最大推理速度
- 需要 Pydantic 模型支持
- 需要零开销的结构化生成
- 需要控制 Token 采样过程

**何时选择其他方案：**
- Instructor：需要具有自动重试功能的 API 模型
- Guidance：需要 Token 修复和复杂工作流
- LMQL：偏好声明式查询语法

## 性能特征

**速度：**
- **零开销**：结构化生成与无约束生成一样快
- **快速前向优化**：跳过确定性 Token
- 比后生成验证方法**快 1.2-2 倍**

**内存：**
- 每个模式编译一次 FSM（已缓存）
- 最小的运行时开销
- 与 vLLM 配合使用可实现高吞吐量

**准确性：**
- **100% 有效输出**（由 FSM 保证）
- 无需重试循环
- 确定性 Token 过滤

## 资源

- **文档**：https://outlines-dev.github.io/outlines
- **GitHub**：https://github.com/outlines-dev/outlines (8k+ stars)
- **Discord**：https://discord.gg/R9DSu34mGd
- **博客**：https://blog.dottxt.co

## 另请参阅

- `references/json_generation.md` - 全面的 JSON 和 Pydantic 模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产就绪示例