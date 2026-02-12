---
type: reference
created: 2025-02-12
area: "[[AI相关]]"
tags: [research, langchain, memory, ai-agent, langgraph]
status: complete
---

# LangChain Memory 系统

## 概述

Memory（记忆）是 AI Agent 记住先前交互信息的系统。对于 AI 智能体而言，记忆至关重要，因为它能够：

- 记住先前的交互
- 从反馈中学习
- 适应用户偏好

随着智能体处理更复杂的任务和大量的用户交互，这种能力对于提高效率和用户满意度变得不可或缺。

LangChain/LangGraph 提供了**两种类型**的记忆，基于它们的召回范围：

## 核心概念

### 1. 短期记忆 (Short-term Memory)

**别名**: Thread-scoped memory（线程级记忆）

**定义**: 在单个会话（thread）中跟踪正在进行的对话，通过在会话内维护消息历史来实现。

**特点**:
- 范围: 单个对话线程
- 生命周期: 随会话存在而存在
- 管理方式: LangGraph 将其作为智能体状态的一部分进行管理
- 持久化: 使用 [[Checkpointer]] 将状态持久化到数据库，以便随时可以恢复线程

**工作原理**:
1. 短期记忆在图被调用或步骤完成时更新
2. 状态在每个步骤开始时读取
3. 可以包含对话历史、上传的文件、检索的文档或生成的产物

**常见挑战**:
- 长对话可能超出 LLM 的上下文窗口，导致上下文丢失或错误
- 即使模型支持完整上下文长度，大多数 LLM 在长上下文上表现不佳
- 会被陈旧或离题内容"分散注意力"
- 响应时间变慢，成本增加

**解决方案**:
- 使用技术移除或"遗忘"陈旧信息
- 消息摘要（Summarization）
- 滑动窗口（Sliding Window）
- 相关性过滤

### 2. 长期记忆 (Long-term Memory)

**定义**: 跨会话存储用户特定或应用级别的数据，可在多个对话线程之间共享。

**特点**:
- 范围: 跨线程共享
- 生命周期: 永久存储（直到显式删除）
- 管理方式: LangGraph 提供 [[Store]] 用于保存和召回长期记忆
- 命名空间: 记忆可作用于任何自定义命名空间，而不仅限于单个线程 ID

**存储结构**:
- LangGraph 将长期记忆存储为 JSON 文档
- 每个记忆都组织在自定义命名空间（类似文件夹）和唯一键（类似文件名）下
- 命名空间通常包含用户 ID、组织 ID 或其他便于组织信息的标签
- 支持跨命名空间搜索（通过内容过滤器）

**两种写入方式**:
1. **热路径写入** (In the hot path): 在执行流程中直接写入
2. **后台写入** (In the background): 异步后台处理时写入

### 3. 情景记忆 (Episodic Memory)

**定义**: 回忆过去的事件或行动，类似于人类的 episodic memory。

**应用场景**:
- 帮助智能体记住如何完成某项任务
- 通过少样本示例（few-shot examples）提示实现

**实现方式**:
- 使用过去的交互序列作为示例
- 动态选择最相关的示例
- 可以使用 LangSmith Dataset 存储示例数据

## 实现机制

### 短期记忆实现

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

# 创建 checkpointer
checkpointer = MemorySaver()

# 构建图时添加 checkpointer
builder = StateGraph(...)
graph = builder.compile(checkpointer=checkpointer)

# 调用时指定 thread_id
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke(
    {"messages": [{"role": "user", "content": "hi! i am Bob"}]},
    config
)
```

### 在 Tool 中访问短期记忆

```python
from typing import Any
from langchain.tools import tool, ToolRuntime

@tool
def my_tool(input_data: str, runtime: ToolRuntime) -> str:
    """访问短期记忆（状态）"""
    # runtime 对 LLM 隐藏，但工具可以通过它访问状态
    state = runtime.state
    # 使用 state 中的信息
    return f"Previous context: {state.get('context', '')}"
```

### 长期记忆实现

```python
from langgraph.store.memory import InMemoryStore
from typing import Any

# 初始化存储（生产环境使用 PostgresStore 等持久化实现）
store = InMemoryStore()

# 访问记忆
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """查询用户信息"""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

# 更新记忆
@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """保存用户信息"""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info."

# 创建智能体时传入 store
agent = create_agent(
    model,
    tools=[get_user_info, save_user_info],
    store=store
)
```

### 使用 Functional API

```python
from langgraph.func import entrypoint
from typing import Any

@entrypoint(checkpointer=checkpointer)
def my_workflow(number: int, *, previous: Any = None) -> int:
    previous = previous or 0
    return number + previous

config = {
    "configurable": {
        "thread_id": "some_thread_id"
    }
}

my_workflow.invoke(1, config)  # 返回 1 (previous 为 None)
my_workflow.invoke(2, config)  # 返回 3 (previous 为 1)
```

## 关键组件

### Checkpointer（检查点器）

**作用**: 将智能体状态持久化到数据库，使线程可以在任何时候恢复。

**常见实现**:
- [[MemorySaver]]: 内存存储（开发和测试用）
- [[PostgresSaver]]: PostgreSQL 持久化存储（生产环境）
- [[RedisSaver]]: Redis 存储
- [[SQLiteSaver]]: SQLite 本地存储

### Store（存储）

**作用**: 提供跨会话的持久化存储。

**特点**:
- 使用 namespace/key 模式组织数据
- 支持层级命名空间
- 可跨命名空间搜索

**常见实现**:
- [[InMemoryStore]]: 内存存储
- [[PostgresStore]]: PostgreSQL 持久化
- [[AgentCoreMemoryStore]]: AWS Bedrock 语义搜索存储

## 最佳实践

1. **选择合适的记忆类型**
   - 对话上下文 → 短期记忆
   - 用户偏好/历史 → 长期记忆
   - 任务示例 → 情景记忆

2. **生产环境考虑**
   - 使用持久化存储（Postgres、Redis 等）
   - 实施适当的访问控制
   - 定期清理过期数据

3. **性能优化**
   - 限制短期记忆长度（使用滑动窗口或摘要）
   - 为长期记忆建立合适的索引
   - 缓存频繁访问的记忆

4. **命名空间设计**
   - 使用清晰的层级结构（如 `("users", user_id, "preferences")`）
   - 避免过于扁平的命名空间
   - 考虑多租户场景

5. **上下文工程**
   - 从静态提示和工具开始，只在需要时添加动态内容
   - 一次只添加一个上下文工程特性
   - 监控模型调用、token 使用和延迟
   - 记录上下文策略

## 常见陷阱

1. **上下文窗口溢出**
   - 没有限制消息历史长度
   - 导致 token 超限错误

2. **记忆冲突**
   - 多个线程同时写入同一记忆
   - 需要适当的并发控制

3. **隐私问题**
   - 长期记忆可能存储敏感信息
   - 需要数据加密和访问审计

4. **过度依赖记忆**
   - 过多历史信息可能使模型"困惑"
   - 需要权衡记忆量和模型性能

5. **命名空间混乱**
   - 不清晰的命名空间设计
   - 导致记忆检索困难

## 相关阅读

- [[LangGraph]] - LangChain 的编排框架
- [[AI-Agent]] - AI 智能体概念
- [[RAG]] - 检索增强生成
- [[Prompt-Engineering]] - 提示工程

## 参考资源

- [LangChain Memory 官方文档](https://docs.langchain.com/oss/python/concepts/memory)
- [LangGraph Memory Guide](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Short-term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Long-term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [CoALA Paper](https://arxiv.org/abs/2309.02427) - 记忆分类理论基础