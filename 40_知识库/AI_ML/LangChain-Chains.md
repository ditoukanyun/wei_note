---
type: wiki
created: 2026-02-12
area: "[[AI_ML]]"
tags: [langchain, chains, ai, llm]
---

# LangChain Chains

Chains（链）是将多个组件组合成可复用工作流的方式。虽然现在 LangChain 更推荐使用 [[LangChain-Agents|Agents]]，但理解 Chains 有助于掌握组件组合的概念。

## 什么是 Chain

Chain 是一种将**输入 → 处理 → 输出**流程封装成可复用单元的方式。最简单的 Chain 就是：

```
输入 → 格式化提示词 → 调用 LLM → 解析输出 → 结果
```

## 核心组件

### 1. Prompt Template（提示词模板）

定义输入如何转换为提示词：

```python
from langchain.prompts import PromptTemplate

template = """Translate the following text from {input_language} to {output_language}:

{text}"""

prompt = PromptTemplate(
    template=template,
    input_variables=["input_language", "output_language", "text"]
)

# 使用
formatted_prompt = prompt.format(
    input_language="English",
    output_language="French",
    text="Hello, how are you?"
)
```

### 2. LLM（大语言模型）

标准化的模型接口：

```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# 文本补全模型
llm = OpenAI(temperature=0.7)

# 聊天模型
chat_model = ChatOpenAI(model="gpt-4", temperature=0)
```

### 3. Output Parser（输出解析器）

将 LLM 的输出解析为结构化数据：

```python
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

response_schemas = [
    ResponseSchema(name="answer", description="answer to the user's question"),
    ResponseSchema(name="source", description="source used to answer the question")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
```

## Chain 类型

### LLMChain

最基础的 Chain，组合 Prompt + LLM + Output Parser：

```python
from langchain.chains import LLMChain

chain = LLMChain(
    llm=chat_model,
    prompt=prompt,
    output_parser=output_parser
)

result = chain.predict(input_language="English", output_language="Chinese", text="Hello")
```

### Sequential Chain

顺序执行多个 Chain：

```python
from langchain.chains import SimpleSequentialChain

# 第一个 Chain：生成故事标题
title_chain = LLMChain(llm=llm, prompt=title_template)

# 第二个 Chain：基于标题写故事
story_chain = LLMChain(llm=llm, prompt=story_template)

# 顺序组合
overall_chain = SimpleSequentialChain(
    chains=[title_chain, story_chain],
    verbose=True
)

story = overall_chain.run("一个关于AI的科幻故事")
```

### Retrieval Chain

结合检索的 Chain，用于 RAG：

```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 或 "map_reduce", "refine", "map_rerank"
    retriever=vectorstore.as_retriever()
)

result = qa_chain.run("文档的主要内容是什么？")
```

## Chain 的替代品：LCEL

LangChain Expression Language（LCEL）是更现代的组件组合方式：

```python
from langchain.schema.runnable import RunnableSequence

# 使用 | 操作符组合组件
chain = prompt | llm | output_parser

# 调用
result = chain.invoke({"input": "Hello"})
```

LCEL 的优势：
- 更直观的语法
- 更好的流式支持
- 更容易调试
- 与 Agents 更好的集成

## 何时使用 Chains

### 适合使用 Chains 的场景

- 固定的处理流程
- 简单的转换任务（翻译、摘要）
- 不需要动态决策的流程
- 性能敏感的场景（Chains 通常比 Agents 快）

### 适合使用 Agents 的场景

- 需要动态决策
- 多步骤复杂任务
- 不确定需要哪些工具
- 需要与用户交互确认

## 最佳实践

1. **优先使用 LCEL**：现代 LangChain 推荐 LCEL 语法
2. **流式处理**：利用 `.stream()` 实现更好的用户体验
3. **错误处理**：使用 `with_fallbacks` 添加回退机制
4. **缓存**：使用 `CacheBackedEmbeddings` 缓存中间结果

## 从 Chains 迁移到 Agents

如果你的 Chain 需要变得更智能：

```python
# 之前：使用 Chain
chain = prompt | llm

# 之后：使用 Agent，让 LLM 决定是否调用工具
agent = create_agent(
    model="claude",
    tools=[tool_from_chain(chain)],  # 将 Chain 转换为工具
    system_prompt="..."
)
```

## 相关概念

- [[LangChain-Agents]] - 智能代理，替代 Chains 的推荐方案
- [[LangChain-Prompts]] - 提示词管理
- [[LangChain-Models]] - 模型接口
- [[LangChain-Retrieval]] - 检索增强 Chain
