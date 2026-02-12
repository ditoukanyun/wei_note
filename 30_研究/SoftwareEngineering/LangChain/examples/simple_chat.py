"""
LangChain 简单对话示例

展示如何直接使用 LLM 进行对话，无需 Agent。
适用于简单的问答场景。
"""

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

def simple_chat():
    """简单对话示例"""
    
    # 初始化 LLM
    # temperature: 0=确定性回答，1=更有创意
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7
    )
    
    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个友善的技术助手，擅长解释编程概念。"),
        HumanMessage(content="什么是 LangChain？")
    ]
    
    # 获取回复
    response = llm.invoke(messages)
    
    print("💬 对话示例 1：简单问答")
    print(f"你: {messages[1].content}")
    print(f"AI: {response.content}\n")

def multi_turn_chat():
    """多轮对话示例"""
    
    llm = ChatOpenAI(model="gpt-4o")
    
    # 维护对话历史
    messages = [
        SystemMessage(content="你是一个 Python 专家。")
    ]
    
    # 第一轮
    messages.append(HumanMessage(content="Python 的装饰器是什么？"))
    response1 = llm.invoke(messages)
    messages.append(AIMessage(content=response1.content))
    
    print("💬 对话示例 2：多轮对话")
    print(f"你: {messages[1].content}")
    print(f"AI: {response1.content}\n")
    
    # 第二轮（引用上文）
    messages.append(HumanMessage(content="能给我举个例子吗？"))
    response2 = llm.invoke(messages)
    
    print(f"你: {messages[3].content}")
    print(f"AI: {response2.content}\n")

def streaming_chat():
    """流式输出示例 - 实时显示响应"""
    
    llm = ChatOpenAI(
        model="gpt-4o",
        streaming=True  # 启用流式传输
    )
    
    print("💬 对话示例 3：流式输出")
    print("你: 写一首关于 AI 的短诗")
    print("AI: ", end="", flush=True)
    
    messages = [HumanMessage(content="写一首关于 AI 的短诗，4句话")]
    
    # 流式获取响应
    for chunk in llm.stream(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    
    print("\n")

def main():
    """运行所有示例"""
    print("=" * 60)
    print("LangChain 简单对话示例")
    print("=" * 60 + "\n")
    
    simple_chat()
    multi_turn_chat()
    streaming_chat()
    
    print("=" * 60)
    print("提示：要运行这些示例，需要设置 OPENAI_API_KEY 环境变量")
    print("export OPENAI_API_KEY='your-api-key'")
    print("=" * 60)

if __name__ == "__main__":
    main()
