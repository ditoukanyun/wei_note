"""
长期记忆示例 - 用户信息持久化
展示如何使用 Store 实现跨会话的长期记忆
"""

from typing import Any
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore

# 初始化长期记忆存储
# 生产环境应使用 PostgresStore 等持久化实现
store = InMemoryStore()

# 从长期记忆中读取用户信息
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """
    从长期记忆中查询用户信息
    
    Args:
        user_id: 用户唯一标识
    """
    store = runtime.store
    user_data = store.get(("users",), user_id)
    
    if user_data and user_data.value:
        info = user_data.value
        return f"用户信息：\n- 姓名: {info.get('name', '未知')}\n- 年龄: {info.get('age', '未知')}\n- 邮箱: {info.get('email', '未知')}"
    return f"未找到用户 {user_id} 的信息"

# 保存用户信息到长期记忆
@tool
def save_user_info(
    user_id: str, 
    name: str, 
    age: int, 
    email: str,
    runtime: ToolRuntime
) -> str:
    """
    保存用户信息到长期记忆
    
    Args:
        user_id: 用户唯一标识
        name: 姓名
        age: 年龄
        email: 邮箱
    """
    store = runtime.store
    user_info = {
        "name": name,
        "age": age,
        "email": email
    }
    store.put(("users",), user_id, user_info)
    return f"成功保存用户 {user_id} 的信息"

# 更新用户偏好
@tool
def update_user_preference(
    user_id: str,
    preference_key: str,
    preference_value: Any,
    runtime: ToolRuntime
) -> str:
    """
    更新用户偏好设置
    
    Args:
        user_id: 用户唯一标识
        preference_key: 偏好项名称
        preference_value: 偏好值
    """
    store = runtime.store
    
    # 获取现有偏好
    existing = store.get(("users", user_id, "preferences"), "settings")
    preferences = existing.value if existing else {}
    
    # 更新偏好
    preferences[preference_key] = preference_value
    
    # 保存回存储
    store.put(("users", user_id, "preferences"), "settings", preferences)
    return f"已更新用户 {user_id} 的偏好: {preference_key} = {preference_value}"

# 获取用户偏好
@tool
def get_user_preferences(user_id: str, runtime: ToolRuntime) -> str:
    """
    获取用户的所有偏好设置
    
    Args:
        user_id: 用户唯一标识
    """
    store = runtime.store
    prefs = store.get(("users", user_id, "preferences"), "settings")
    
    if prefs and prefs.value:
        pref_list = "\n".join([f"- {k}: {v}" for k, v in prefs.value.items()])
        return f"用户 {user_id} 的偏好设置:\n{pref_list}"
    return f"用户 {user_id} 暂无偏好设置"

# 创建智能体
tools = [get_user_info, save_user_info, update_user_preference, get_user_preferences]
model = ChatOpenAI(model="gpt-4o-mini")

agent = create_agent(
    model=model,
    tools=tools,
    store=store
)

# 模拟多会话场景
if __name__ == "__main__":
    print("=== 会话 1: 创建用户 ===")
    result1 = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": "请保存以下用户信息：用户ID: user001, 姓名: 李四, 年龄: 28, 邮箱: lisi@example.com"
        }]
    })
    print("AI:", result1["messages"][-1].content)
    
    print("\n=== 会话 2: 设置偏好（模拟新会话）===")
    result2 = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": "为用户 user001 设置语言偏好为中文，主题偏好为深色模式"
        }]
    })
    print("AI:", result2["messages"][-1].content)
    
    print("\n=== 会话 3: 查询信息（模拟新会话）===")
    result3 = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": "获取用户 user001 的完整信息和偏好设置"
        }]
    })
    print("AI:", result3["messages"][-1].content)
    
    print("\n=== 会话 4: 新用户 ===")
    result4 = agent.invoke({
        "messages": [{
            "role": "user", 
            "content": "查询用户 user002 的信息"
        }]
    })
    print("AI:", result4["messages"][-1].content)