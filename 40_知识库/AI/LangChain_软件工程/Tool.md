---
type: wiki
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [langchain, ai, tool]
---

# Tool

工具是 Agent 可调用的外部功能，扩展了 LLM 的能力边界。

## 定义方式

### 使用装饰器（推荐）

```python
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """搜索网页获取信息。"""
    # 实现搜索逻辑
    return f"搜索结果: {query}"
```

### 使用 Tool 类

```python
from langchain.tools import Tool

tool = Tool(
    name="calculator",
    func=lambda x: eval(x),
    description="执行数学计算"
)
```

## 常用工具类型

- **搜索** - Google Search, DuckDuckGo
- **计算** - Python REPL, 计算器
- **数据库** - SQL, NoSQL 查询
- **API** - REST, GraphQL 调用

## 关键要点

- 工具必须有清晰的 docstring（Agent 用它决定何时调用）
- 返回字符串格式
- 处理可能的错误

## 相关概念

- [[Agent]] - 使用工具的实体
- [工具集成](https://python.langchain.com/docs/integrations/tools/)
