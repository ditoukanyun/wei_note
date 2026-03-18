---
type: wiki
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [langchain, ai, llm]
---

# LLM

大语言模型（Large Language Model）是 LangChain 的核心组件，负责理解输入并生成响应。

## 支持的模型

| 提供商 | 推荐模型 |
|--------|----------|
| OpenAI | gpt-4o, gpt-4o-mini |
| Anthropic | claude-sonnet-4-5 |
| Google | gemini-pro |
| 开源 | Llama, Mistral (通过 Ollama) |

## 关键参数

- **temperature** - 创造力（0=确定性，1=随机）
- **max_tokens** - 最大输出长度
- **model** - 模型名称

## 使用示例

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)

response = llm.invoke("你好")
```

## 相关概念

- [[PromptTemplate]] - 构建输入
- [[Agent]] - 使用 LLM 的智能体
- [模型提供商](https://python.langchain.com/docs/integrations/providers/)
