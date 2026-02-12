"""
LangChain 基础示例 1: 基础代理
展示如何创建一个简单的天气查询代理
"""

from langchain.agents import create_agent
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    
    Args:
        city: 城市名称，如 "北京"、"Shanghai"
    
    Returns:
        该城市的天气描述
    """
    # 这里应该是真实 API 调用
    weather_data = {
        "北京": "晴朗，25°C",
        "上海": "多云，22°C",
        "深圳": "小雨，28°C",
        "New York": "Sunny, 72°F",
        "London": "Rainy, 15°C"
    }
    return weather_data.get(city, f"抱歉，我没有 {city} 的天气信息")


@tool
def get_time(city: str) -> str:
    """
    获取指定城市的当前时间。
    
    Args:
        city: 城市名称
    
    Returns:
        该城市的当前时间
    """
    from datetime import datetime
    import pytz
    
    timezones = {
        "北京": "Asia/Shanghai",
        "上海": "Asia/Shanghai",
        "纽约": "America/New_York",
        "London": "Europe/London"
    }
    
    tz = timezones.get(city, "UTC")
    current_time = datetime.now(pytz.timezone(tz))
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数：演示基础代理的使用"""
    
    # 创建代理
    # 注意：需要设置 ANTHROPIC_API_KEY 环境变量
    agent = create_agent(
        model="claude-sonnet-4-5-20250929",  # 或其他可用模型
        tools=[get_weather, get_time],
        system_prompt="""你是一个有帮助的助手，可以查询天气和时间。
        
当用户询问天气时，使用 get_weather 工具。
当用户询问时间时，使用 get_time 工具。

始终保持友好和专业的态度。"""
    )
    
    # 测试不同的查询
    test_queries = [
        "北京今天天气怎么样？",
        "现在纽约几点了？",
        "上海天气如何？",
        "伦敦的时间和天气"
    ]
    
    print("=" * 50)
    print("LangChain 基础代理示例")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n用户: {query}")
        print("-" * 50)
        
        try:
            response = agent.invoke({
                "messages": [{"role": "user", "content": query}]
            })
            print(f"代理: {response}")
        except Exception as e:
            print(f"错误: {e}")
            print("提示: 请确保已设置 ANTHROPIC_API_KEY 环境变量")
    
    # 交互模式
    print("\n" + "=" * 50)
    print("进入交互模式 (输入 'exit' 退出)")
    print("=" * 50)
    
    while True:
        user_input = input("\n用户: ").strip()
        if user_input.lower() == 'exit':
            break
        
        try:
            response = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            print(f"代理: {response}")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
