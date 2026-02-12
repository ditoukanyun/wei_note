"""
LangChain 基础示例 4: 记忆系统
展示如何在多轮对话中使用记忆
"""

from langchain.agents import create_agent
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory
)
from langchain.tools import tool
from langchain.llms import OpenAI
import os


@tool
def get_user_info() -> str:
    """获取当前用户信息（模拟）"""
    return "用户ID: 12345, 会员等级: VIP"


@tool
def search_products(query: str) -> str:
    """
    搜索产品（模拟）
    
    Args:
        query: 搜索关键词
    """
    products = {
        "手机": ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8"],
        "电脑": ["MacBook Pro", "Dell XPS 15", "ThinkPad X1"],
        "耳机": ["AirPods Pro", "Sony WH-1000XM5", "Bose QC45"]
    }
    
    for category, items in products.items():
        if category in query:
            return f"找到 {len(items)} 个 {category}: {', '.join(items)}"
    
    return f"搜索 '{query}' 的结果：未找到相关产品"


def demo_buffer_memory():
    """
    演示 ConversationBufferMemory
    保存完整的对话历史
    """
    print("\n" + "=" * 60)
    print("演示 1: ConversationBufferMemory")
    print("=" * 60)
    print("特点：保存完整的对话历史")
    
    # 创建记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # 模拟多轮对话
    conversations = [
        ("你好，我叫张三", "你好张三！很高兴认识你。"),
        ("我喜欢编程", "太棒了！编程是个很有用的技能。"),
        ("我在学习 Python", "Python 是很棒的语言，适合初学者。"),
        ("我叫什么名字？", "你叫张三。"),
        ("我喜欢什么？", "你喜欢编程，特别是 Python。")
    ]
    
    for user_msg, ai_msg in conversations:
        print(f"\n用户: {user_msg}")
        print(f"AI: {ai_msg}")
        memory.save_context(
            {"input": user_msg},
            {"output": ai_msg}
        )
    
    # 查看记忆内容
    print("\n" + "-" * 60)
    print("记忆内容:")
    print("-" * 60)
    memory_vars = memory.load_memory_variables({})
    for msg in memory_vars["chat_history"]:
        print(f"{msg.type}: {msg.content}")


def demo_window_memory():
    """
    演示 ConversationBufferWindowMemory
    只保留最近的 k 轮对话
    """
    print("\n" + "=" * 60)
    print("演示 2: ConversationBufferWindowMemory (k=2)")
    print("=" * 60)
    print("特点：只保留最近 2 轮对话")
    
    memory = ConversationBufferWindowMemory(
        k=2,  # 只保留最近 2 轮
        memory_key="chat_history",
        return_messages=True
    )
    
    # 模拟多轮对话
    for i in range(5):
        user_msg = f"这是第 {i+1} 条消息"
        ai_msg = f"收到第 {i+1} 条消息"
        
        memory.save_context(
            {"input": user_msg},
            {"output": ai_msg}
        )
    
    # 查看记忆内容
    print("\n记忆内容 (应该只有最近 2 轮):")
    print("-" * 60)
    memory_vars = memory.load_memory_variables({})
    for msg in memory_vars["chat_history"]:
        print(f"{msg.type}: {msg.content}")


def demo_summary_memory():
    """
    演示 ConversationSummaryMemory
    对历史对话进行摘要
    """
    print("\n" + "=" * 60)
    print("演示 3: ConversationSummaryMemory")
    print("=" * 60)
    print("特点：对长对话进行摘要，节省 token")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("跳过：需要 OPENAI_API_KEY 来生成摘要")
        return
    
    memory = ConversationSummaryMemory(
        llm=OpenAI(temperature=0),
        memory_key="chat_history",
        return_messages=True
    )
    
    # 模拟长对话
    long_conversation = [
        ("你好，我叫李四", "你好李四！有什么我可以帮助你的吗？"),
        ("我想买一台笔记本电脑", "好的，您有什么具体需求吗？比如用途、预算？"),
        ("主要用于编程，预算 8000-10000", "明白了。您偏好 Windows 还是 Mac？"),
        ("我习惯 Windows，但听说 Mac 也不错", "Mac 确实在开发领域很受欢迎，特别是续航和屏幕质量。"),
        ("那 Mac 能跑 Windows 软件吗？", "可以通过虚拟机或 Boot Camp 运行 Windows。"),
        ("好的，那我考虑一下 MacBook Pro", "MacBook Pro 是不错的选择，特别是 M3 芯片版本。"),
    ]
    
    print("\n对话内容:")
    for user_msg, ai_msg in long_conversation:
        print(f"\n用户: {user_msg}")
        print(f"AI: {ai_msg}")
        memory.save_context(
            {"input": user_msg},
            {"output": ai_msg}
        )
    
    # 查看摘要
    print("\n" + "-" * 60)
    print("对话摘要:")
    print("-" * 60)
    memory_vars = memory.load_memory_variables({})
    print(memory_vars["chat_history"][0].content)


def demo_memory_with_agent():
    """
    演示在 Agent 中使用记忆
    """
    print("\n" + "=" * 60)
    print("演示 4: Agent 中的记忆")
    print("=" * 60)
    
    # 创建记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # 创建工具
    tools = [get_user_info, search_products]
    
    # 创建带记忆的 Agent
    system_prompt = """你是一个智能购物助手。

之前的对话：
{chat_history}

请根据对话历史和当前问题提供帮助。"""
    
    agent = create_agent(
        model="claude-sonnet-4-5-20250929",
        tools=tools,
        system_prompt=system_prompt
    )
    
    # 模拟对话
    print("\n模拟对话 (带记忆):")
    print("-" * 60)
    
    queries = [
        "你好，我想买一部手机",
        "我之前问过什么？",  # 应该记得问过手机
        "还有什么推荐的吗？"
    ]
    
    for query in queries:
        print(f"\n用户: {query}")
        
        try:
            # 加载记忆
            memory_vars = memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", "")
            
            # 调用代理
            response = agent.invoke({
                "messages": [{"role": "user", "content": query}],
                "chat_history": chat_history
            })
            
            print(f"AI: {response}")
            
            # 保存对话
            memory.save_context(
                {"input": query},
                {"output": str(response)}
            )
            
        except Exception as e:
            print(f"错误: {e}")
            print("提示: 请确保已设置 API Key")


def demo_different_memory_comparison():
    """
    对比不同记忆类型的 token 消耗
    """
    print("\n" + "=" * 60)
    print("演示 5: 不同记忆类型对比")
    print("=" * 60)
    
    # 模拟 10 轮对话
    conversation = [(f"问题 {i}", f"答案 {i}") for i in range(10)]
    
    memories = {
        "Buffer": ConversationBufferMemory(),
        "Window (k=3)": ConversationBufferWindowMemory(k=3),
    }
    
    print("\nToken 消耗对比（估计）:")
    print("-" * 60)
    
    for name, mem in memories.items():
        for q, a in conversation:
            mem.save_context({"input": q}, {"output": a})
        
        history = mem.load_memory_variables({})["history"]
        tokens = len(history) // 4  # 粗略估计
        print(f"{name:20s}: ~{tokens:4d} tokens")


def main():
    """主函数"""
    
    print("=" * 60)
    print("LangChain 记忆系统示例")
    print("=" * 60)
    print("\n本示例展示不同类型的记忆系统")
    print("记忆让 AI 能够记住对话历史")
    
    # 运行各个演示
    demo_buffer_memory()
    input("\n按 Enter 继续...")
    
    demo_window_memory()
    input("\n按 Enter 继续...")
    
    demo_summary_memory()
    input("\n按 Enter 继续...")
    
    demo_memory_with_agent()
    input("\n按 Enter 继续...")
    
    demo_different_memory_comparison()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("""
记忆类型选择指南：

1. ConversationBufferMemory
   - 适合：短对话（< 10 轮）
   - 优点：完整保留所有信息
   - 缺点：token 消耗随对话增长

2. ConversationBufferWindowMemory
   - 适合：中等对话（10-50 轮）
   - 优点：控制 token 消耗
   - 缺点：会丢失旧信息

3. ConversationSummaryMemory
   - 适合：长对话（> 50 轮）
   - 优点：长对话也能保持高效
   - 缺点：摘要可能丢失细节

4. VectorStoreRetrieverMemory
   - 适合：需要精确检索相关上下文
   - 优点：只返回相关的记忆
   - 缺点：需要向量数据库
""")


if __name__ == "__main__":
    main()
