"""
记忆管理高级示例 - 对话摘要和窗口管理
展示如何处理长对话上下文，避免 token 超限
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage
from typing import Literal

# 创建 LLM
model = ChatOpenAI(model="gpt-4o-mini")

# 系统提示词
SYSTEM_PROMPT = """你是一个有用的助手。保持对对话上下文的理解，
如果之前的对话内容太长，你会收到一个总结。请基于可用信息回答用户问题。"""

def summarize_messages(state: MessagesState) -> MessagesState:
    """
    当消息历史过长时，进行摘要
    保留最近的几条消息，将更早的消息总结为一条
    """
    messages = state["messages"]
    
    # 如果消息少于 6 条，不需要摘要
    if len(messages) < 6:
        return state
    
    # 保留最近 4 条消息
    recent_messages = messages[-4:]
    
    # 将之前的消息总结为一条
    messages_to_summarize = messages[:-4]
    summary_prompt = f"""将以下对话总结为 2-3 句话的摘要，保留关键信息：
    
{messages_to_summarize}"""
    
    summary = model.invoke([
        SystemMessage(content="你是一个对话摘要助手。"),
        HumanMessage(content=summary_prompt)
    ])
    
    # 创建新的消息列表：摘要 + 最近消息
    new_messages = [
        SystemMessage(content=f"对话摘要: {summary.content}"),
        *recent_messages
    ]
    
    return {"messages": new_messages}

def sliding_window(state: MessagesState, window_size: int = 10) -> MessagesState:
    """
    滑动窗口：只保留最近的 N 条消息
    
    Args:
        window_size: 保留的消息数量
    """
    messages = state["messages"]
    
    if len(messages) <= window_size:
        return state
    
    # 只保留最近的消息
    recent_messages = messages[-window_size:]
    
    # 标记旧消息为待删除（可选，用于调试）
    removed_count = len(messages) - window_size
    
    return {
        "messages": recent_messages,
        "metadata": {
            "removed_messages": removed_count,
            "window_size": window_size
        }
    }

def should_summarize(state: MessagesState) -> Literal["summarize", "continue"]:
    """
    决定是否需要摘要
    """
    messages = state["messages"]
    
    # 简单启发式：消息数量或总 token 数
    if len(messages) > 10:
        return "summarize"
    
    return "continue"

def chatbot(state: MessagesState):
    """
    聊天节点
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# 构建图
builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("summarize", summarize_messages)
builder.add_node("chatbot", chatbot)

# 添加条件边
builder.add_conditional_edges(
    START,
    should_summarize,
    {
        "summarize": "summarize",
        "continue": "chatbot"
    }
)

builder.add_edge("summarize", "chatbot")

# 编译图
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 演示使用
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "memory_management_demo"}}
    
    print("=== 模拟长对话 ===\n")
    
    # 模拟一系列对话
    conversations = [
        "你好，我想了解一些关于 Python 的知识",
        "Python 适合做什么类型的开发？",
        "那数据分析方面有什么优势？",
        "能推荐一些学习资源吗？",
        "有没有好的书籍推荐？",
        "视频教程呢？",
        "实践项目有什么建议？",
        "初学者容易犯什么错误？",
        "如何避免这些错误？",
        "Python 2 和 3 有什么区别？",
        "现在应该学哪个版本？",
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"用户 ({i}): {message}")
        result = graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config
        )
        ai_response = result["messages"][-1].content
        print(f"AI: {ai_response[:100]}...\n")  # 只显示前100字符
        
        # 显示当前消息数量
        current_messages = len(result["messages"])
        print(f"[系统] 当前消息数: {current_messages}\n")