"""
LangChain Hello World - 第一个 Agent

这个示例展示如何创建一个简单的 Agent，它可以：
1. 理解用户输入
2. 决定调用哪个工具
3. 返回结果
"""

from langchain.agents import create_agent
from langchain.tools import tool

# ========== 步骤1：定义工具 ==========
# 工具必须有清晰的 docstring，Agent 用它来理解工具用途

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的当前天气信息。
    
    Args:
        city: 城市名称，如"北京"、"上海"
    
    Returns:
        天气描述字符串
    """
    # 实际应用中，这里应该调用真实的天气 API
    # 示例：使用 OpenWeatherMap、和风天气等
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，22°C",
        "广州": "小雨，28°C",
        "深圳": "阴天，26°C"
    }
    return weather_data.get(city, f"{city} 天气良好，适宜出行")

@tool
def calculate(expression: str) -> str:
    """
    执行数学计算。
    
    Args:
        expression: 数学表达式，如"2 + 2"、"10 * 5"
    
    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

# ========== 步骤2：创建 Agent ==========
# 使用 create_agent 快速创建一个 Agent

agent = create_agent(
    model="gpt-4o",  # 模型名称
    tools=[get_weather, calculate],  # 可用工具列表
    system_prompt="""你是一个有帮助的助手。你可以：
1. 查询天气信息
2. 执行数学计算
请根据用户的问题，选择合适的工具来回答。"""
)

# ========== 步骤3：运行 Agent ==========

def main():
    """主函数：运行 Agent 对话"""
    print("🤖 Agent 已启动！输入 'exit' 退出\n")
    
    while True:
        user_input = input("你: ").strip()
        
        if user_input.lower() == 'exit':
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        try:
            # 调用 Agent
            response = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            # 提取并显示回复
            if isinstance(response, dict):
                print(f"🤖: {response}\n")
            else:
                print(f"🤖: {response.content}\n")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}\n")

if __name__ == "__main__":
    # 测试一些示例问题
    test_questions = [
        "北京今天天气怎么样？",
        "25 乘以 4 等于多少？",
        "上海和深圳哪个更热？"
    ]
    
    print("🚀 运行测试示例...\n")
    for question in test_questions:
        print(f"你: {question}")
        response = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        print(f"🤖: {response}\n")
    
    # 进入交互模式
    print("=" * 50)
    main()
