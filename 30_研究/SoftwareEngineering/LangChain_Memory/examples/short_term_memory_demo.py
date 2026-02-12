"""
短期记忆示例 - 对话历史管理
展示如何使用 checkpointer 实现多轮对话记忆
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义工具
@tool
def search_weather(location: str) -> str:
    """搜索指定位置的天气"""
    return f"{location} 的天气是晴天，25°C"

# 创建工具节点
tools = [search_weather]
tool_node = ToolNode(tools)

# 创建 LLM
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# 定义聊天节点
def chatbot(state: MessagesState):
    """聊天机器人节点"""
    return {"messages": [model.invoke(state["messages"])]}

# 决定下一步
def should_continue(state: MessagesState):
    """决定是继续工具调用还是结束"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

# 构建图
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue, {"tools": "tools", "__end__": "__end__"})
builder.add_edge("tools", "chatbot")

# 添加 checkpointer 实现短期记忆
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 使用示例
if __name__ == "__main__":
    # 配置 thread_id - 这是短期记忆的关键
    config = {"configurable": {"thread_id": "conversation_1"}}
    
    # 第一轮对话
    print("=== 第一轮对话 ===")
    result1 = graph.invoke(
        {"messages": [{"role": "user", "content": "你好，我叫张三"}]},
        config
    )
    print("AI:", result1["messages"][-1].content)
    
    # 第二轮对话 - 应该记住名字
    print("\n=== 第二轮对话 ===")
    result2 = graph.invoke(
        {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
        config
    )
    print("AI:", result2["messages"][-1].content)
    
    # 第三轮对话 - 使用工具
    print("\n=== 第三轮对话 ===")
    result3 = graph.invoke(
        {"messages": [{"role": "user", "content": "查询一下北京的天气"}]},
        config
    )
    print("AI:", result3["messages"][-1].content)
    
    # 新线程 - 没有之前的记忆
    print("\n=== 新线程对话 ===")
    new_config = {"configurable": {"thread_id": "conversation_2"}}
    result4 = graph.invoke(
        {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
        new_config
    )
    print("AI:", result4["messages"][-1].content)
    
    # 恢复到第一个线程
    print("\n=== 恢复第一个线程 ===")
    result5 = graph.invoke(
        {"messages": [{"role": "user", "content": "我们之前聊了什么？"}]},
        config
    )
    print("AI:", result5["messages"][-1].content)