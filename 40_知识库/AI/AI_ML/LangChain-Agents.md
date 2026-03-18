---
type: wiki
created: 2026-02-12
area: "[[AI_ML]]"
tags: [langchain, agents, ai, llm]
---

# LangChain Agents

Agents（代理）是 LangChain 的核心组件，它让 LLM 能够**自主决定采取什么行动**，而不是按照预定义的流程执行。

## 核心概念

### ReAct 模式

Agents 使用 **ReAct**（Reasoning + Acting，推理+行动）模式：

1. **Thought（思考）**：分析问题并决定下一步行动
2. **Action（行动）**：调用工具或执行操作
3. **Observation（观察）**：收集结果
4. **循环**：重复上述步骤直到完成任务

```
用户: "北京今天天气怎么样？"

Thought: 用户询问北京的天气，我需要使用天气工具
Action: get_weather(city="北京")
Observation: "北京今天晴，25°C"

Thought: 我已经获得了天气信息，可以回答用户
Final Answer: 北京今天天气晴朗，气温25摄氏度。
```

## 创建 Agent

### 基础创建

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
```

### 关键参数

- **model**：使用的 LLM 模型
- **tools**：代理可调用的工具列表
- **system_prompt**：系统提示词，定义代理的角色和行为

## 工具定义

工具是代理与外部世界交互的方式：

```python
def calculator(expression: str) -> str:
    """
    Calculate mathematical expression.
    
    Args:
        expression: Mathematical expression like "2 + 2" or "10 * 5"
    
    Returns:
        Result of the calculation
    """
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"
```

**重要**：工具的 docstring 直接影响代理的表现，要写得清晰明确。

## 执行 Agent

```python
# 单次调用
response = agent.invoke(
    {"messages": [{"role": "user", "content": "What is 123 * 456?"}]}
)

# 流式输出
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Tell me a story"}]}
):
    print(chunk, end="", flush=True)
```

## Agent Executor

对于更精细的控制，使用 AgentExecutor：

```python
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,     # 处理解析错误
    max_iterations=5,               # 最大迭代次数
    early_stopping_method="generate" # 超时处理方法
)

result = agent_executor.invoke({"input": "复杂问题"})
```

## 最佳实践

1. **工具数量**：建议 3-7 个，过多会让代理选择困难
2. **工具命名**：使用动词开头，如 `search_web`、`calculate_math`
3. **错误处理**：工具内部要处理异常，返回友好的错误信息
4. **系统提示词**：明确代理的角色、限制和风格

## 常见类型

- **Zero-shot ReAct**：通用型代理，根据描述选择工具
- **Structured Chat**：支持多输入工具的对话代理
- **OpenAI Functions**：利用 OpenAI 的函数调用能力
- **Plan-and-Execute**：先制定计划再执行

## 相关概念

- [[LangChain-Chains]] - 替代 Agents 的链式方法
- [[LangChain-Tools]] - 工具的详细说明
- [[LangChain-Memory]] - 代理的记忆系统
- [[LangGraph]] - 构建更复杂的多代理系统
