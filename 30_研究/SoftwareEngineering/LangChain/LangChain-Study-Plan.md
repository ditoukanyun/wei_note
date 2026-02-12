---
type: reference
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [langchain, study-plan, python, ai, learning-path]
---

# LangChain 深度学习和实践方案

## 概述

基于官方文档 https://docs.langchain.com/ 的深度研究，为 [[Python持续学习]] 项目制定的系统化学习方案。

---

## 第一部分：Python 基础关联知识

### 1.1 装饰器模式（Decorator）

LangChain 大量使用装饰器模式：

```python
# 工具装饰器
from langchain.tools import tool

@tool
def my_tool(param: str) -> str:
    """工具描述"""
    return result

# 中间件装饰器
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def my_middleware(request, handler):
    return handler(request)
```

**Python 知识点**：
- 函数装饰器实现原理
- `functools.wraps` 保留元数据
- 带参数的装饰器
- 类装饰器

### 1.2 类型提示（Type Hints）

LangChain 是类型驱动的框架：

```python
from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel

# Pydantic 模型定义工具输入
class WeatherInput(BaseModel):
    location: str = Field(description="城市名称")
    units: Literal["celsius", "fahrenheit"] = "celsius"

# TypedDict 定义状态
class AgentState(TypedDict):
    messages: list[BaseMessage]
    user_preferences: dict
```

**Python 知识点**：
- `typing` 模块：TypedDict, Generic, Union, Optional
- Pydantic 数据验证
- 类型别名和 NewType
- 协变/逆变概念

### 1.3 异步编程（Async/Await）

现代 LangChain 基于异步架构：

```python
import asyncio
from langchain.agents import create_agent

# 异步工具
@tool
async def async_search(query: str) -> str:
    await asyncio.sleep(1)  # 模拟网络请求
    return f"Results for {query}"

# 异步调用
async def main():
    agent = create_agent(model, tools=[async_search])
    result = await agent.ainvoke({"messages": [...]})
    
asyncio.run(main())
```

**Python 知识点**：
- `async`/`await` 语法
- `asyncio` 事件循环
- 并发执行：`asyncio.gather()`
- 异步迭代器

### 1.4 上下文管理器

资源管理和运行时上下文：

```python
from contextlib import contextmanager

@contextmanager
def tool_runtime():
    """工具运行时上下文"""
    setup_resources()
    try:
        yield runtime
    finally:
        cleanup_resources()

# LangChain 中的使用
with get_openai_callback() as cb:
    result = agent.invoke(input)
    print(f"Tokens used: {cb.total_tokens}")
```

### 1.5 迭代器和生成器

流式输出的核心机制：

```python
# 同步流式
for chunk in agent.stream(input):
    print(chunk.text, end="")

# 异步流式
async for chunk in agent.astream(input):
    print(chunk.text, end="")

# 自定义生成器
def tool_stream_generator():
    for step in execution_steps:
        yield step.result
```

---

## 第二部分：核心组件深度解析

### 2.1 Agent 架构内幕

#### ReAct 循环详解

```
┌─────────────────────────────────────────────────────┐
│                    Agent Loop                        │
├─────────────────────────────────────────────────────┤
│  1. 接收输入（用户消息）                              │
│           ↓                                          │
│  2. 模型推理（Thought）                              │
│     - 分析用户意图                                    │
│     - 决定是否需要工具                                │
│     - 选择具体工具                                    │
│           ↓                                          │
│  3. 工具执行（Action）                               │
│     - 调用选定工具                                    │
│     - 传入参数                                        │
│     - 获取执行结果                                    │
│           ↓                                          │
│  4. 观察结果（Observation）                          │
│     - 将工具结果反馈给模型                            │
│     - 判断是否完成任务                                │
│           ↓                                          │
│  5. 循环或结束                                        │
│     - 需要更多工具 → 回到步骤2                        │
│     - 任务完成 → 生成最终回答                         │
└─────────────────────────────────────────────────────┘
```

#### 模型绑定机制

```python
# 1. 基础绑定
model_with_tools = model.bind_tools([tool1, tool2])

# 2. 强制使用特定工具
model_with_tools = model.bind_tools(
    [tool1], 
    tool_choice="any"  # 或 tool_choice="tool1"
)

# 3. 禁用并行调用
model_with_tools = model.bind_tools(
    [tool1, tool2],
    parallel_tool_calls=False
)
```

**关键概念**：
- `tool_choice` 控制工具选择策略
- `parallel_tool_calls` 控制是否允许多工具并行
- 绑定后模型输出的 `tool_calls` 字段包含调用信息

#### 动态模型选择

```python
from langchain.agents.middleware import wrap_model_call

basic_model = ChatOpenAI(model="gpt-4.1-mini")
advanced_model = ChatOpenAI(model="gpt-4.1")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler):
    """基于对话复杂度动态选择模型"""
    message_count = len(request.state["messages"])
    
    if message_count > 10:
        model = advanced_model  # 长对话使用高级模型
    else:
        model = basic_model     # 短对话使用基础模型
    
    return handler(request.override(model=model))
```

### 2.2 Tools 工具系统深度剖析

#### 工具定义的多层架构

```python
from langchain.tools import tool, ToolRuntime
from pydantic import BaseModel, Field

# Level 1: 基础工具
@tool
def simple_tool(query: str) -> str:
    """简单工具，只有基础参数"""
    return f"Result: {query}"

# Level 2: 结构化输入工具
class SearchInput(BaseModel):
    query: str = Field(description="搜索查询")
    limit: int = Field(default=10, ge=1, le=100)
    filters: dict = Field(default_factory=dict)

@tool(args_schema=SearchInput)
def advanced_search(query: str, limit: int, filters: dict) -> str:
    """高级搜索工具，结构化输入"""
    return search_api(query, limit=limit, filters=filters)

# Level 3: 上下文感知工具
@tool
def context_aware_tool(
    param: str,
    runtime: ToolRuntime  # 自动注入，对LLM隐藏
) -> str:
    """可以访问运行时状态的工具"""
    user_id = runtime.context.user_id
    state = runtime.state
    store = runtime.store
    
    # 使用上下文信息
    user_prefs = store.get(("preferences",), user_id)
    return process_with_context(param, user_prefs)
```

#### 工具运行时的三层记忆体系

```python
"""
┌─────────────────────────────────────────────────────┐
│              工具运行时记忆体系                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │    State     │  │   Context    │  │  Store   │ │
│  │   (短期)     │  │   (运行时)   │  │  (长期)  │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │               │       │
│    对话历史              用户信息        持久化数据 │
│    临时计数器            会话信息        用户配置   │
│    当前状态              认证信息        知识库     │
│                                                     │
└─────────────────────────────────────────────────────┘
"""

# State - 短期记忆（当前对话）
@tool
def state_aware_tool(runtime: ToolRuntime) -> str:
    messages = runtime.state["messages"]  # 完整对话历史
    counter = runtime.state.get("call_count", 0)
    return f"Call #{counter}"

# Context - 运行时上下文（不可变配置）
@tool  
def context_aware_tool(runtime: ToolRuntime) -> str:
    user_id = runtime.context.user_id      # 用户ID
    session_id = runtime.context.session   # 会话ID
    return f"User: {user_id}"

# Store - 长期记忆（跨会话持久化）
@tool
def store_aware_tool(user_id: str, runtime: ToolRuntime) -> str:
    # 获取长期记忆
    prefs = runtime.store.get(("users",), user_id)
    # 更新长期记忆
    runtime.store.put(("users",), user_id, {"last_visit": now()})
    return "Updated"
```

### 2.3 Middleware 中间件系统

#### 中间件钩子全解析

```python
from langchain.agents.middleware import (
    AgentMiddleware,
    before_model,
    after_model,
    wrap_model_call,
    wrap_tool_call
)

# 1. before_model: 模型调用前处理状态
@before_model
def preprocess_messages(state: AgentState, runtime) -> dict:
    """在调用模型前处理消息"""
    # 修剪过长的对话历史
    if len(state["messages"]) > 20:
        state["messages"] = state["messages"][-20:]
    return {"messages": state["messages"]}

# 2. after_model: 模型响应后处理
@after_model(can_jump_to=["tools", "end"])  # 可以跳转到工具节点或结束
def postprocess_response(state: AgentState, runtime) -> dict:
    """处理模型响应"""
    last_message = state["messages"][-1]
    
    # 内容安全审查
    if contains_sensitive_content(last_message.content):
        last_message.content = "[Content filtered]"
    
    return {"messages": [last_message]}

# 3. wrap_model_call: 包装模型调用
@wrap_model_call
def logging_wrapper(request: ModelRequest, handler):
    """记录模型调用日志"""
    start_time = time.time()
    
    print(f"Calling model with {len(request.state['messages'])} messages")
    response = handler(request)
    
    elapsed = time.time() - start_time
    print(f"Model response took {elapsed:.2f}s")
    
    return response

# 4. wrap_tool_call: 包装工具调用
@wrap_tool_call
def retry_tool_wrapper(request: ToolCallRequest, handler):
    """工具重试逻辑"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return handler(request)
        except ToolError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
    
    return handler(request)
```

### 2.4 Structured Output 结构化输出

#### 两种策略对比

```python
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy

# Strategy 1: ProviderStrategy（原生支持）
# 优点：更准确、更可靠
# 缺点：仅部分提供商支持（OpenAI、Anthropic、xAI）

agent = create_agent(
    model="gpt-5",
    response_format=ProviderStrategy(ContactInfo)
)

# Strategy 2: ToolStrategy（通用方案）
# 优点：所有支持工具调用的模型都可用
# 缺点：通过工具调用模拟，可能不够精确

agent = create_agent(
    model="any-model",
    response_format=ToolStrategy(ContactInfo)
)

# 自动选择：LangChain 根据模型能力自动选择
agent = create_agent(
    model="gpt-5",  # 支持原生结构化输出
    response_format=ContactInfo  # 自动使用 ProviderStrategy
)
```

### 2.5 Streaming 流式输出系统

#### 三种流模式详解

```python
# Mode 1: updates - 状态更新流
for chunk in agent.stream(input, stream_mode="updates"):
    for node_name, state_update in chunk.items():
        print(f"{node_name}: {state_update}")

# Mode 2: messages - Token级流
for token, metadata in agent.stream(input, stream_mode="messages"):
    print(token.text, end="")

# Mode 3: custom - 自定义更新
for update in agent.stream(input, stream_mode="custom"):
    print(f"Progress: {update}")
```

---

## 第三部分：系统化学习路径（6周）

### Week 1: Python 基础强化
- Day 1-2: 装饰器与元编程
- Day 3-4: 类型系统与 Pydantic
- Day 5-7: 异步编程实战

### Week 2: LangChain 基础掌握
- Day 1-2: Agent 核心概念
- Day 3-4: Tools 工具系统
- Day 5-7: 记忆系统

### Week 3: 进阶组件深入
- Day 1-2: Middleware 中间件
- Day 3-4: 结构化输出
- Day 5-7: 流式输出

### Week 4: RAG 系统实战
- Day 1-2: 文档处理
- Day 3-4: 向量存储
- Day 5-7: 完整 RAG 系统

### Week 5: 生产级项目
- Day 1-3: Web 集成
- Day 4-5: 监控与调试
- Day 6-7: 部署优化

### Week 6: 综合实战
- Day 1-3: 多 Agent 系统
- Day 4-5: 高级功能
- Day 6-7: 项目收尾

---

## 参考资源

### 官方文档
- [Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
- [Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Streaming](https://docs.langchain.com/oss/python/langchain/streaming)

### 相关笔记
- [[LangChain]] - 主研究笔记
- [[Python持续学习]] - Python 学习项目
