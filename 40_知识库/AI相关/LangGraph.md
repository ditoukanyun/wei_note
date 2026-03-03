---
created: 2025-03-02
area: "[[AI相关]]"
tags: [ai, framework, langchain, agent]
---

# LangGraph

## 定义

LangGraph是LangChain生态系统中的一个库，专门用于构建复杂的、有状态的Agent工作流。它通过图结构（StateGraph）来定义Agent的执行流程，支持循环、条件分支、并行执行等高级特性。

## 核心概念

### StateGraph（状态图）

**核心思想**：将Agent的执行过程建模为图，其中：

- **节点（Nodes）**：执行具体逻辑的函数
- **边（Edges）**：控制流程走向
- **状态（State）**：在整个图中传递的共享数据

### 与基础ReAct的区别

| 特性     | 基础ReAct  | LangGraph  |
| -------- | ---------- | ---------- |
| 流程控制 | 简单循环   | 任意图结构 |
| 状态管理 | 隐式       | 显式State  |
| 条件分支 | 有限       | 灵活       |
| 并行执行 | 不支持     | 支持       |
| 持久化   | 需自行实现 | 内置支持   |
| 人机协作 | 需自行实现 | 内置支持   |

## 基本用法

### 定义State

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph

# 定义状态结构
class AgentState(TypedDict):
    messages: List[dict]  # 对话历史
    next_step: str        # 下一步动作
    iteration: int        # 迭代计数
    finished: bool        # 是否完成
```

### 构建图

```python
# 创建工作流图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("agent", call_agent)
workflow.add_node("tools", call_tools)
workflow.add_node("end", end_node)

# 添加边
workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "agent")

# 添加条件边
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": "end"
    }
)

# 设置入口点
workflow.set_entry_point("agent")

# 编译图
app = workflow.compile()
```

### 节点实现

```python
def call_agent(state: AgentState):
    """Agent推理节点"""
    messages = state["messages"]

    # 调用LLM
    response = llm.invoke(messages)

    return {
        "messages": messages + [response],
        "iteration": state["iteration"] + 1
    }

def call_tools(state: AgentState):
    """工具执行节点"""
    messages = state["messages"]
    last_message = messages[-1]

    # 解析工具调用
    tool_calls = parse_tool_calls(last_message)

    # 执行工具
    results = []
    for tool_call in tool_calls:
        result = execute_tool(tool_call)
        results.append(result)

    return {"messages": messages + results}

def should_continue(state: AgentState):
    """判断是否继续执行"""
    if state["iteration"] > 10:
        return "end"

    last_message = state["messages"][-1]
    if has_tool_calls(last_message):
        return "continue"

    return "end"
```

## 高级特性

### 1. 条件分支

```python
def route_based_on_intent(state: AgentState):
    """根据意图路由到不同分支"""
    last_message = state["messages"][-1]
    intent = classify_intent(last_message)

    if intent == "search":
        return "search_branch"
    elif intent == "calculate":
        return "calc_branch"
    else:
        return "chat_branch"

workflow.add_conditional_edges(
    "agent",
    route_based_on_intent,
    {
        "search_branch": "search_tool",
        "calc_branch": "calculator",
        "chat_branch": "respond"
    }
)
```

### 2. 并行执行

```python
from langgraph.graph import END

# 添加并行节点
workflow.add_node("branch_a", process_a)
workflow.add_node("branch_b", process_b)
workflow.add_node("merge", merge_results)

# 从同一节点出发的多个边表示并行
workflow.add_edge("start", "branch_a")
workflow.add_edge("start", "branch_b")

# 使用同步点等待所有并行分支
workflow.add_edge("branch_a", "merge")
workflow.add_edge("branch_b", "merge")
```

### 3. 循环和迭代

```python
def should_continue(state: AgentState):
    """循环控制条件"""
    if state["iteration"] >= state["max_iterations"]:
        return "end"

    if state["task_complete"]:
        return "end"

    return "continue"

workflow.add_conditional_edges(
    "process",
    should_continue,
    {
        "continue": "process",  # 循环回自身
        "end": END
    }
)
```

### 4. 人机协作（Human-in-the-loop）

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 添加中断点
workflow.add_node("human_review", human_review_node)

# 在需要人工审核的地方中断
workflow.add_conditional_edges(
    "agent",
    needs_human_review,
    {
        "review": "human_review",
        "auto": "tools"
    }
)

# 编译时添加检查点
memory = SqliteSaver.from_conn_string(":memory:")
app = workflow.compile(checkpointer=memory)

# 运行时可以中断等待人工输入
for event in app.stream(inputs, thread_id="thread-1"):
    if event["type"] == "interrupt":
        # 等待人工输入
        human_input = input("请审核：")
        app.update_state(thread_id="thread-1", values={"human_input": human_input})
```

### 5. 持久化状态

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 创建持久化存储
memory = SqliteSaver.from_conn_string("checkpoints.db")

# 编译时启用检查点
app = workflow.compile(checkpointer=memory)

# 运行时会自动保存状态
checkpoint = app.get_state(thread_id="thread-1")

# 可以从任意检查点恢复
app.update_state(thread_id="thread-1", checkpoint_id=checkpoint.id)
```

## Multi-Agent系统

```python
# 定义多个Agent
class MultiAgentState(TypedDict):
    messages: List[dict]
    sender: str
    next_agent: str

# 创建主协调图
workflow = StateGraph(MultiAgentState)

# 添加各个Agent节点
workflow.add_node("researcher", researcher_agent)
workflow.add_node("analyst", analyst_agent)
workflow.add_node("writer", writer_agent)

# 定义Agent间的通信
workflow.add_conditional_edges(
    "researcher",
    route_to_next,
    {"analyst": "analyst", END: END}
)

workflow.add_conditional_edges(
    "analyst",
    route_to_next,
    {"writer": "writer", "researcher": "researcher", END: END}
)

workflow.add_edge("writer", END)
```

## 与LangChain的关系

```
LangChain (基础框架)
    ├── Chains (链式调用)
    ├── Agents (Agent抽象)
    ├── Tools (工具集成)
    └── ...

LangGraph (工作流编排)
    ├── StateGraph (状态图)
    ├── Persistence (持久化)
    └── Human-in-the-loop (人机协作)
```

**关系**：LangGraph构建在LangChain之上，专注于复杂的、有状态的Agent工作流编排。

## 适用场景

| 场景             | LangGraph优势            |
| ---------------- | ------------------------ |
| **复杂工作流**   | 循环、条件、并行都能表达 |
| **长时运行任务** | 状态持久化，可断点续传   |
| **人机协作**     | 内置中断和人工审核机制   |
| **Multi-Agent**  | 清晰的Agent通信和协调    |
| **调试追踪**     | 完整的执行轨迹记录       |

## 相关概念

- [[LangChain]] - 底层LLM应用框架
- [[ReAct]] - Agent的基础推理模式
- [[AI Agent]] - Agent的核心概念
- [[Plan-and-Execute]] - LangGraph可以实现的规划模式
- [[StateGraph]] - LangGraph的核心抽象

## 最佳实践

1. **状态设计**：State要精简，只存必要信息
2. **错误处理**：每个节点都要有错误处理逻辑
3. **超时控制**：设置合理的迭代上限和超时
4. **日志记录**：记录关键节点的输入输出
5. **状态检查点**：在长任务中设置检查点
6. **测试覆盖**：对工作流的各个路径进行测试

## 参考资料

- LangGraph官方文档
- LangChain官方文档
