---
type: wiki
created: 2026-02-12
updated: 2026-02-12
area: "[[AI_ML]]"
tags: [langchain, memory, ai, llm, context, checkpointer]
---

# LangChain Memory 记忆系统

## 概述

Memory（记忆）让 AI Agent 能够在多轮对话中保持上下文。LangChain 1.0+ 引入了全新的记忆管理机制，基于 **Checkpointer** 和 **State** 实现更灵活、更强大的记忆功能。

---

## LangChain 1.0+ 新机制（推荐）

### 核心概念：Checkpointer

Checkpointer 是 LangChain 1.0+ 管理短期记忆的标准方式：

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  # 内存存储
from langgraph.checkpoint.postgres import PostgresSaver  # PostgreSQL 存储

# 开发环境：内存存储
checkpointer = InMemorySaver()

agent = create_agent(
    model="gpt-5",
    tools=[get_user_info],
    checkpointer=checkpointer,  # 启用记忆功能
)

# 调用时需要指定 thread_id
agent.invoke(
    {"messages": [{"role": "user", "content": "你好！我叫张三"}]},
    {"configurable": {"thread_id": "1"}}  # 会话ID
)
```

**关键概念**：
- **Thread（线程）**：一个对话会话，类似邮件会话
- **Checkpointer**：保存和恢复对话状态的检查点机制
- **State**：包含消息历史和其他自定义数据的状态对象

### 生产环境配置

```python
# PostgreSQL 持久化
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost:5432/db"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # 自动创建表
    
    agent = create_agent(
        model="gpt-5",
        tools=tools,
        checkpointer=checkpointer,
    )
```

### 自定义 State（扩展记忆字段）

```python
from langchain.agents import create_agent, AgentState

class CustomAgentState(AgentState):
    """扩展 AgentState 添加自定义字段"""
    user_id: str
    preferences: dict
    conversation_count: int

agent = create_agent(
    model="gpt-5",
    tools=tools,
    state_schema=CustomAgentState,  # 使用自定义状态
    checkpointer=InMemorySaver(),
)

# 调用时传入自定义字段
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Hello"}],
        "user_id": "user_123",
        "preferences": {"theme": "dark"},
        "conversation_count": 0
    },
    {"configurable": {"thread_id": "1"}}
)
```

---

## 管理长对话：消息处理策略

长对话会超出 LLM 的上下文窗口，LangChain 提供多种策略：

### 策略 1：修剪消息（Trim Messages）

使用 `@before_model` 中间件保留最近的 N 条消息：

```python
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

@before_model
def trim_messages(state, runtime):
    """保留最近的3-4条消息"""
    messages = state["messages"]
    
    if len(messages) <= 3:
        return None  # 不需要修剪
    
    # 保留系统消息 + 最近的消息
    first_msg = messages[0]  # 通常是 system message
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages
    
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),  # 删除所有旧消息
            *new_messages
        ]
    }

agent = create_agent(
    model="gpt-5",
    tools=tools,
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)
```

### 策略 2：删除特定消息（Delete Messages）

```python
from langchain.messages import RemoveMessage

# 删除特定消息
def delete_old_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的2条消息
        return {
            "messages": [RemoveMessage(id=m.id) for m in messages[:2]]
        }

# 删除所有消息（清空对话）
from langgraph.graph.message import REMOVE_ALL_MESSAGES

def clear_all_messages(state):
    return {
        "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]
    }
```

**⚠️ 注意事项**：
- 确保消息序列有效性（如 user 消息开头）
- 保留 tool call 和 tool result 的配对关系

### 策略 3：消息摘要（Summarize Messages）

使用内置的 `SummarizationMiddleware`：

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4.1",
    tools=tools,
    middleware=[
        SummarizationMiddleware(
            model="gpt-4.1-mini",      # 用于摘要的模型
            trigger=("tokens", 4000),   # token 超过 4000 时触发
            keep=("messages", 20)       # 保留最近 20 条消息
        )
    ],
    checkpointer=InMemorySaver(),
)
```

**摘要机制**：
- 当对话长度达到触发条件时，较早的消息被摘要
- 摘要以 System Message 形式插入
- 最近的消息保持完整

---

## 在工具中访问和修改记忆

### 读取 State（在工具中）

```python
from langchain.tools import tool, ToolRuntime

@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """从 state 中读取用户信息"""
    user_id = runtime.state["user_id"]
    preferences = runtime.state.get("preferences", {})
    
    return f"User: {user_id}, Preferences: {preferences}"
```

**关键点**：
- `runtime` 参数对 LLM 隐藏，不会出现在工具 schema 中
- 通过 `runtime.state` 访问完整对话状态

### 写入 State（在工具中）

使用 `Command` 更新 state：

```python
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage

@tool
def update_user_info(runtime: ToolRuntime) -> Command:
    """更新用户信息到 state"""
    user_id = runtime.context.user_id
    
    # 查询用户信息
    user_info = fetch_user_from_db(user_id)
    
    return Command(update={
        "user_name": user_info["name"],      # 更新 state 字段
        "user_role": user_info["role"],
        "messages": [                        # 同时更新消息历史
            ToolMessage(
                content=f"User info updated for {user_info['name']}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })
```

---

## 在 Prompt 中使用记忆

### 动态系统提示词

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    """根据用户偏好生成动态提示词"""
    user_name = request.runtime.state.get("user_name", "User")
    preferences = request.runtime.state.get("preferences", {})
    
    theme = preferences.get("theme", "light")
    language = preferences.get("language", "zh")
    
    return f"""你是一个 helpful assistant。
    
Address the user as {user_name}.
Current theme: {theme}
Respond in: {language}
"""

agent = create_agent(
    model="gpt-5",
    tools=tools,
    middleware=[personalized_prompt],
    checkpointer=InMemorySaver(),
)
```

---

## 完整示例：带记忆的多轮对话 Agent

```python
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import before_model, dynamic_prompt
from langgraph.types import Command

# 1. 定义自定义 State
class ChatState(AgentState):
    user_name: str = ""
    conversation_count: int = 0

# 2. 定义工具
@tool
def remember_name(name: str, runtime: ToolRuntime) -> Command:
    """记住用户名字"""
    return Command(update={
        "user_name": name,
        "conversation_count": runtime.state.get("conversation_count", 0) + 1,
        "messages": [
            ToolMessage(
                content=f"Nice to meet you, {name}!",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

@tool
def get_conversation_stats(runtime: ToolRuntime) -> str:
    """获取对话统计"""
    count = runtime.state.get("conversation_count", 0)
    name = runtime.state.get("user_name", "unknown")
    return f"{name} has had {count} conversations."

# 3. 消息修剪中间件
@before_model
def smart_trim(state, runtime):
    """智能修剪：保留系统消息 + 最近5轮"""
    messages = state["messages"]
    if len(messages) <= 11:  # system + 5轮 (10条)
        return None
    
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            messages[0],  # system message
            *messages[-10:]  # 最近5轮
        ]
    }

# 4. 动态提示词
@dynamic_prompt
def chat_prompt(request):
    name = request.runtime.state.get("user_name", "there")
    return f"You are a helpful assistant chatting with {name}."

# 5. 创建 Agent
checkpointer = InMemorySaver()

agent = create_agent(
    model="gpt-5",
    tools=[remember_name, get_conversation_stats],
    state_schema=ChatState,
    middleware=[chat_prompt, smart_trim],
    checkpointer=checkpointer,
)

# 6. 使用
config = {"configurable": {"thread_id": "user_123"}}

# 第一轮
result = agent.invoke(
    {"messages": [{"role": "user", "content": "My name is Alice"}]},
    config
)

# 第二轮（能记住名字）
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config
)
```

---

## 新旧版本对比

| 特性 | 旧版 (<1.0) | 新版 (1.0+) |
|------|------------|------------|
| 核心机制 | Memory 类 | Checkpointer |
| 状态管理 | 手动 save/load | 自动持久化 |
| 消息修剪 | 内置策略 | 中间件自定义 |
| 摘要功能 | 单独 Memory 类 | SummarizationMiddleware |
| 工具访问 | 通过参数传递 | ToolRuntime.state |
| 多线程 | 手动管理 | thread_id 自动隔离 |

---

## 相关概念

- [[LangChain-Agents]] - Agent 核心概念
- [[LangChain-Middleware]] - 中间件系统（修剪、摘要）
- [[LangGraph]] - 底层状态图机制
- [[RAG-技术概述]] - 长期记忆（向量检索）
