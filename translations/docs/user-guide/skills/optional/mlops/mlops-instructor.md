---
title: "Instructor"
sidebar_label: "Instructor"
description: "通过 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，以类型安全的方式解析复杂的 JSON，并流式传输..."
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Instructor

通过 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，以类型安全的方式解析复杂的 JSON，并流式传输部分结果——使用经过实战检验的结构化输出库 Instructor。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/instructor` 安装 |
| 路径 | `optional-skills/mlops/instructor` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `instructor`, `pydantic`, `openai`, `anthropic` |
| 标签 | `Prompt Engineering`, `Instructor`, `Structured Output`, `Pydantic`, `Data Extraction`, `JSON Parsing`, `Type Safety`, `Validation`, `Streaming`, `OpenAI`, `Anthropic` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Instructor：结构化 LLM 输出

## 何时使用此技能

在以下情况使用 Instructor：
- 需要可靠地从 LLM 响应中**提取结构化数据**
- 需要根据 Pydantic 模式**自动验证输出**
- 需要**自动重试失败的提取**并处理错误
- 需要以类型安全和验证的方式**解析复杂的 JSON**
- 需要**流式传输部分结果**以进行实时处理
- 需要**支持多个 LLM 提供商**并保持一致的 API

**GitHub 星标数**: 15,000+ | **实战检验**: 100,000+ 开发者

## 安装

```bash
# 基础安装
pip install instructor

# 安装特定提供商支持
pip install "instructor[anthropic]"  # Anthropic Claude
pip install "instructor[openai]"     # OpenAI
pip install "instructor[all]"        # 所有提供商
```

## 快速开始

### 基础示例：提取用户数据

```python
import instructor
from pydantic import BaseModel
from anthropic import Anthropic

# 定义输出结构
class User(BaseModel):
    name: str
    age: int
    email: str

# 创建 instructor 客户端
client = instructor.from_anthropic(Anthropic())

# 提取结构化数据
user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "John Doe is 30 years old. His email is john@example.com"
    }],
    response_model=User
)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

### 使用 OpenAI

```python
from openai import OpenAI

client = instructor.from_openai(OpenAI())

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=User,
    messages=[{"role": "user", "content": "Extract: Alice, 25, alice@email.com"}]
)
```

## 核心概念

### 1. 响应模型 (Pydantic)

响应模型定义了 LLM 输出的结构和验证规则。

#### 基础模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Number of words", gt=0)
    tags: list[str] = Field(description="List of relevant tags")

article = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Analyze this article: [article text]"
    }],
    response_model=Article
)
```

**优势：**
- 使用 Python 类型提示实现类型安全
- 自动验证 (例如 word_count > 0)
- 通过 Field 描述实现自文档化
- 支持 IDE 自动补全

#### 嵌套模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # 嵌套模型

person = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "John lives at 123 Main St, Boston, USA"
    }],
    response_model=Person
)

print(person.address.city)  # "Boston"
```

#### 可选字段

```python
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    discount: Optional[float] = None  # 可选
    description: str = Field(default="No description")  # 默认值

# LLM 无需提供 discount 或 description
```

#### 用于约束的枚举

```python
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Review(BaseModel):
    text: str
    sentiment: Sentiment  # 只允许这三个值

review = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "This product is amazing!"
    }],
    response_model=Review
)

print(review.sentiment)  # Sentiment.POSITIVE
```

### 2. 验证

Pydantic 自动验证 LLM 输出。如果验证失败，Instructor 会自动重试。

#### 内置验证器

```python
from pydantic import Field, EmailStr, HttpUrl

class Contact(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)  # 0 <= age <= 120
    email: EmailStr  # 验证邮箱格式
    website: HttpUrl  # 验证 URL 格式

# 如果 LLM 提供无效数据，Instructor 会自动重试
```

#### 自定义验证器

```python
from pydantic import field_validator

class Event(BaseModel):
    name: str
    date: str
    attendees: int

    @field_validator('date')
    def validate_date(cls, v):
        """确保日期格式为 YYYY-MM-DD。"""
        import re
        if not re.match(r'\d{4}-\d{2}-\d{2}', v):
            raise ValueError('Date must be YYYY-MM-DD format')
        return v

    @field_validator('attendees')
    def validate_attendees(cls, v):
        """确保参会人数为正数。"""
        if v < 1:
            raise ValueError('Must have at least 1 attendee')
        return v
```
#### 模型级验证

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_dates(self):
        """确保 end_date 在 start_date 之后。"""
        from datetime import datetime
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')

        if end < start:
            raise ValueError('end_date must be after start_date')
        return self
```

### 3. 自动重试

当验证失败时，Instructor 会自动重试，并向 LLM 提供错误反馈。

```python
# 如果验证失败，最多重试 3 次
user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Extract user from: John, age unknown"
    }],
    response_model=User,
    max_retries=3  # 默认值为 3
)

# 如果无法提取年龄，Instructor 会告诉 LLM：
# "Validation error: age - field required"
# LLM 会尝试使用更好的提取方法再次执行
```

**工作原理：**
1.  LLM 生成输出
2.  Pydantic 进行验证
3.  如果无效：错误信息发送回 LLM
4.  LLM 根据错误反馈再次尝试
5.  重复此过程，直到达到最大重试次数

### 4. 流式处理

流式处理部分结果，实现实时处理。

#### 流式处理部分对象

```python
from instructor import Partial

class Story(BaseModel):
    title: str
    content: str
    tags: list[str]

# 在 LLM 生成时流式传输部分更新
for partial_story in client.messages.create_partial(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Write a short sci-fi story"
    }],
    response_model=Story
):
    print(f"Title: {partial_story.title}")
    print(f"Content so far: {partial_story.content[:100]}...")
    # 实时更新 UI
```

#### 流式处理可迭代对象

```python
class Task(BaseModel):
    title: str
    priority: str

# 在列表项生成时流式传输
tasks = client.messages.create_iterable(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Generate 10 project tasks"
    }],
    response_model=Task
)

for task in tasks:
    print(f"- {task.title} ({task.priority})")
    # 在每个任务到达时进行处理
```

## 提供商配置

### Anthropic Claude

```python
import instructor
from anthropic import Anthropic

client = instructor.from_anthropic(
    Anthropic(api_key="your-api-key")
)

# 与 Claude 模型一起使用
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[...],
    response_model=YourModel
)
```

### OpenAI

```python
from openai import OpenAI

client = instructor.from_openai(
    OpenAI(api_key="your-api-key")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=YourModel,
    messages=[...]
)
```

### 本地模型 (Ollama)

```python
from openai import OpenAI

# 指向本地 Ollama 服务器
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # 必需但会被忽略
    ),
    mode=instructor.Mode.JSON
)

response = client.chat.completions.create(
    model="llama3.1",
    response_model=YourModel,
    messages=[...]
)
```

## 常见模式

### 模式 1：从文本中提取数据

```python
class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int
    headquarters: str

text = """
Tesla, Inc. was founded in 2003. It operates in the automotive and energy
industry with approximately 140,000 employees. The company is headquartered
in Austin, Texas.
"""

company = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Extract company information from: {text}"
    }],
    response_model=CompanyInfo
)
```

### 模式 2：分类

```python
class Category(str, Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"

class ArticleClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    keywords: list[str]

classification = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Classify this article: [article text]"
    }],
    response_model=ArticleClassification
)
```

### 模式 3：多实体提取

```python
class Person(BaseModel):
    name: str
    role: str

class Organization(BaseModel):
    name: str
    industry: str

class Entities(BaseModel):
    people: list[Person]
    organizations: list[Organization]
    locations: list[str]

text = "Tim Cook, CEO of Apple, announced at the event in Cupertino..."

entities = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Extract all entities from: {text}"
    }],
    response_model=Entities
)

for person in entities.people:
    print(f"{person.name} - {person.role}")
```

### 模式 4：结构化分析

```python
class SentimentAnalysis(BaseModel):
    overall_sentiment: Sentiment
    positive_aspects: list[str]
    negative_aspects: list[str]
    suggestions: list[str]
    score: float = Field(ge=-1.0, le=1.0)

review = "The product works well but setup was confusing..."

analysis = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Analyze this review: {review}"
    }],
    response_model=SentimentAnalysis
)
```

### 模式 5：批量处理

```python
def extract_person(text: str) -> Person:
    return client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Extract person from: {text}"
        }],
        response_model=Person
    )

texts = [
    "John Doe is a 30-year-old engineer",
    "Jane Smith, 25, works in marketing",
    "Bob Johnson, age 40, software developer"
]

people = [extract_person(text) for text in texts]
```
## 高级功能

### 联合类型

```python
from typing import Union

class TextContent(BaseModel):
    type: str = "text"
    content: str

class ImageContent(BaseModel):
    type: str = "image"
    url: HttpUrl
    caption: str

class Post(BaseModel):
    title: str
    content: Union[TextContent, ImageContent]  # 任选一种类型

# LLM 根据内容选择适当的类型
```

### 动态模型

```python
from pydantic import create_model

# 在运行时创建模型
DynamicUser = create_model(
    'User',
    name=(str, ...),
    age=(int, Field(ge=0)),
    email=(EmailStr, ...)
)

user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[...],
    response_model=DynamicUser
)
```

### 自定义模式

```python
# 适用于不支持原生结构化输出的提供商
client = instructor.from_anthropic(
    Anthropic(),
    mode=instructor.Mode.JSON  # JSON 模式
)

# 可用模式：
# - Mode.ANTHROPIC_TOOLS (Claude 推荐)
# - Mode.JSON (备用)
# - Mode.TOOLS (OpenAI 工具)
```

### 上下文管理

```python
# 单次使用的客户端
with instructor.from_anthropic(Anthropic()) as client:
    result = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[...],
        response_model=YourModel
    )
    # 客户端自动关闭
```

## 错误处理

### 处理验证错误

```python
from pydantic import ValidationError

try:
    user = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[...],
        response_model=User,
        max_retries=3
    )
except ValidationError as e:
    print(f"重试后失败: {e}")
    # 优雅地处理

except Exception as e:
    print(f"API 错误: {e}")
```

### 自定义错误消息

```python
class ValidatedUser(BaseModel):
    name: str = Field(description="全名，2-100 个字符")
    age: int = Field(description="年龄在 0 到 120 之间", ge=0, le=120)
    email: EmailStr = Field(description="有效的电子邮件地址")

    class Config:
        # 自定义错误消息
        json_schema_extra = {
            "examples": [
                {
                    "name": "John Doe",
                    "age": 30,
                    "email": "john@example.com"
                }
            ]
        }
```

## 最佳实践

### 1. 清晰的字段描述

```python
# ❌ 不好：模糊
class Product(BaseModel):
    name: str
    price: float

# ✅ 好：描述性
class Product(BaseModel):
    name: str = Field(description="文本中的产品名称")
    price: float = Field(description="以美元计的价格，不带货币符号")
```

### 2. 使用适当的验证

```python
# ✅ 好：约束值
class Rating(BaseModel):
    score: int = Field(ge=1, le=5, description="1 到 5 星的评分")
    review: str = Field(min_length=10, description="评论文本，至少 10 个字符")
```

### 3. 在提示词中提供示例

```python
messages = [{
    "role": "user",
    "content": """从以下文本提取人员信息："John, 30, engineer"

示例格式：
{
  "name": "John Doe",
  "age": 30,
  "occupation": "engineer"
}"""
}]
```

### 4. 对固定类别使用枚举

```python
# ✅ 好：枚举确保有效值
class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    status: Status  # LLM 必须从枚举中选择
```

### 5. 优雅地处理缺失数据

```python
class PartialData(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    default_field: str = "default_value"

# LLM 只需要提供 required_field
```

## 与其他方案的比较

| 功能 | Instructor | 手动 JSON | LangChain | DSPy |
|---------|------------|-------------|-----------|------|
| 类型安全 | ✅ 是 | ❌ 否 | ⚠️ 部分 | ✅ 是 |
| 自动验证 | ✅ 是 | ❌ 否 | ❌ 否 | ⚠️ 有限 |
| 自动重试 | ✅ 是 | ❌ 否 | ❌ 否 | ✅ 是 |
| 流式处理 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 多提供商 | ✅ 是 | ⚠️ 手动 | ✅ 是 | ✅ 是 |
| 学习曲线 | 低 | 低 | 中等 | 高 |

**何时选择 Instructor：**
- 需要结构化、经过验证的输出
- 想要类型安全和 IDE 支持
- 需要自动重试
- 构建数据提取系统

**何时选择其他方案：**
- DSPy：需要提示词优化
- LangChain：构建复杂链
- 手动：简单、一次性的提取

## 资源

- **文档**: https://python.useinstructor.com
- **GitHub**: https://github.com/jxnl/instructor (15k+ stars)
- **Cookbook**: https://python.useinstructor.com/examples
- **Discord**: 提供社区支持

## 另请参阅

- `references/validation.md` - 高级验证模式
- `references/providers.md` - 提供商特定配置
- `references/examples.md` - 真实世界用例