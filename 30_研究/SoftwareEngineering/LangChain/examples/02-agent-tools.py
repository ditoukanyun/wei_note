"""
LangChain 基础示例 2: Agent + Tools
展示如何创建一个可以调用多个工具的代理
"""

from langchain.agents import create_agent, AgentExecutor
from langchain.tools import tool
import requests
import json


@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式。
    
    Args:
        expression: 数学表达式，如 "2 + 2"、"10 * 5"、"sqrt(16)"
    
    Returns:
        计算结果
    """
    try:
        # 安全计算：只允许基本数学运算
        allowed_names = {
            "abs": abs,
            "max": max,
            "min": min,
            "pow": pow,
            "round": round,
            "sum": sum
        }
        
        # 简单的安全检查
        if any(keyword in expression.lower() for keyword in ['import', 'exec', 'eval', '__']):
            return "错误：表达式包含不安全的代码"
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def search_web(query: str) -> str:
    """
    搜索网络信息（模拟）。
    
    Args:
        query: 搜索查询
    
    Returns:
        搜索结果摘要
    """
    # 实际使用时应该调用真实搜索 API，如 Google Custom Search、Bing API 等
    # 这里使用模拟数据
    mock_results = {
        "python": "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。",
        "langchain": "LangChain 是一个用于构建 LLM 应用的 Python 框架。",
        "人工智能": "人工智能是计算机科学的一个分支，致力于创造智能机器。",
        "机器学习": "机器学习是 AI 的子集，让计算机能够从数据中学习。"
    }
    
    for key, value in mock_results.items():
        if key.lower() in query.lower():
            return f"搜索结果: {value}"
    
    return f"搜索 '{query}' 的结果：找到相关信息（模拟数据）"


@tool
def get_news(category: str = "tech") -> str:
    """
    获取最新新闻（模拟）。
    
    Args:
        category: 新闻类别，可选 "tech"、"business"、"sports"
    
    Returns:
        新闻摘要
    """
    news_data = {
        "tech": [
            "AI 技术在 2026 年取得重大突破",
            "新型量子计算机问世",
            "SpaceX 成功发射新卫星"
        ],
        "business": [
            "全球股市今日上涨",
            "新能源汽车销量创新高",
            "科技巨头发布财报"
        ],
        "sports": [
            "世界杯预选赛火热进行",
            "NBA 季后赛即将开始",
            "网球大满贯赛事开幕"
        ]
    }
    
    news = news_data.get(category, news_data["tech"])
    return f"{category} 新闻:\n" + "\n".join([f"- {item}" for item in news])


@tool
def translate(text: str, target_lang: str = "Chinese") -> str:
    """
    翻译文本（模拟）。
    
    Args:
        text: 要翻译的文本
        target_lang: 目标语言，如 "Chinese"、"English"、"Japanese"
    
    Returns:
        翻译后的文本
    """
    # 实际使用时应该调用翻译 API
    mock_translations = {
        ("Hello", "Chinese"): "你好",
        ("Hello", "Japanese"): "こんにちは",
        ("你好", "English"): "Hello",
        ("谢谢", "English"): "Thank you",
    }
    
    result = mock_translations.get((text, target_lang))
    if result:
        return f"翻译结果: {result}"
    return f"[{target_lang}] {text} (翻译模拟)"


def main():
    """主函数"""
    
    # 创建工具列表
    tools = [calculate, search_web, get_news, translate]
    
    # 创建系统提示词
    system_prompt = """你是一个多功能的 AI 助手，可以使用以下工具帮助用户：

1. calculate - 计算数学表达式
2. search_web - 搜索网络信息
3. get_news - 获取最新新闻
4. translate - 翻译文本

使用规则：
- 对于数学问题，使用 calculate 工具
- 对于需要最新信息的问题，使用 search_web 工具
- 对于新闻相关的问题，使用 get_news 工具
- 对于翻译需求，使用 translate 工具
- 可以组合使用多个工具来解决复杂问题

始终保持友好和专业。"""
    
    # 创建代理
    agent = create_agent(
        model="claude-sonnet-4-5-20250929",
        tools=tools,
        system_prompt=system_prompt
    )
    
    # 使用 AgentExecutor 进行更精细的控制
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=5,
        verbose=True  # 显示详细执行过程
    )
    
    # 测试查询
    test_queries = [
        "计算 123 * 456",
        "Python 是什么？",
        "最新的科技新闻",
        "把 'Hello' 翻译成中文",
        "如果我有 1000 元，买了 3 个每个 125 元的东西，还剩多少钱？"
    ]
    
    print("=" * 60)
    print("LangChain Agent + Tools 示例")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"用户: {query}")
        print('-' * 60)
        
        try:
            # 使用 agent_executor
            result = agent_executor.invoke({"input": query})
            print(f"\n最终结果: {result['output']}")
        except Exception as e:
            print(f"错误: {e}")
    
    # 交互模式
    print("\n" + "=" * 60)
    print("进入交互模式 (输入 'exit' 退出)")
    print("=" * 60)
    
    while True:
        user_input = input("\n用户: ").strip()
        if user_input.lower() == 'exit':
            print("再见！")
            break
        
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n代理: {result['output']}")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
