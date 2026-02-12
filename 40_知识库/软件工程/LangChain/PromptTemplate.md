---
type: wiki
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [langchain, ai, prompt]
---

# PromptTemplate

提示词模板是 LangChain 中用于结构化 LLM 输入的工具，支持变量替换和复杂场景。

## 类型

### ChatPromptTemplate

用于对话场景：

```python
from langchain.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])

prompt = template.format_messages(
    role="专家",
    question="什么是AI？"
)
```

### FewShotPromptTemplate

用于少样本学习：

```python
from langchain.prompts import FewShotPromptTemplate

examples = [
    {"input": "开心", "output": "喜悦"},
    {"input": "悲伤", "output": "难过"}
]
```

## 最佳实践

- 使用清晰的变量命名
- 添加示例（Few-shot）提高效果
- 保持模板简洁，避免过长

## 相关概念

- [[LLM]] - 接收提示词的模型
- [[Chain]] - 组合模板和执行
- [提示词指南](https://python.langchain.com/docs/concepts/prompt_templates/)
