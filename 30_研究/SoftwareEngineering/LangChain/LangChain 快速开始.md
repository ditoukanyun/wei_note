---
type: reference
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [research, langchain, ai, python, quickstart]
status: complete
---

# LangChain 快速开始

本笔记帮助你在 10 分钟内快速上手 LangChain，构建你的第一个 AI 应用。

## 概述

**LangChain** 是一个开源框架，用于快速构建基于大语言模型（LLM）的应用和 AI Agent。它提供了预构建的 Agent 架构和模型集成，让你可以在不到 10 行代码内连接到 OpenAI、Anthropic、Google 等主流模型。

### 为什么选择 LangChain？

1. **标准模型接口** - 统一不同 LLM 提供商的 API，避免供应商锁定
2. **简单易用** - 10 行代码即可构建简单 Agent
3. **高度灵活** - 支持复杂的工作流和自定义需求
4. **基于 LangGraph** - 内置持久化、流式传输、人机协同等能力
5. **LangSmith 集成** - 深度调试和可观测性

## 核心概念

| 概念 | 说明 |
|------|------|
| **[[Agent]]** | 可以调用工具、进行推理的 AI 系统 |
| **[[LLM]]** | 大语言模型，如 GPT-4、Claude、Gemini |
| **[[PromptTemplate]]** | 提示词模板，用于结构化输入 |
| **[[Tool]]** | Agent 可调用的外部功能 |
| **[[LangChain_Memory]]** | 对话历史管理能力 |
| **Chain** | 多个组件的顺序执行流程 |

## 快速开始步骤

### 1. 安装

```bash
# 基础安装
pip install langchain

# 包含 OpenAI 支持（推荐）
pip install langchain openai

# 包含 Anthropic Claude
pip install "langchain[anthropic]"
```

### 2. 配置 API Key

```bash
# 方式1：环境变量
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"

# 方式2：代码中设置（不推荐用于生产）
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

### 3. 你的第一个 Agent（Hello World）

```python
from langchain.agents import create_agent
from langchain.tools import tool

# 定义一个简单的工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    return f"{city} 今天阳光明媚，温度 25°C！"

# 创建 Agent
agent = create_agent(
    model="gpt-4o",  # 或 claude-sonnet-4-5-20250929
    tools=[get_weather],
    system_prompt="你是一个有帮助的助手"
)

# 运行 Agent
response = agent.invoke({
    "messages": [{"role": "user", "content": "北京天气如何？"}]
})

print(response)
```

### 4. 简单对话示例

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# 初始化模型
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# 构建消息
messages = [
    SystemMessage(content="你是一个友善的助手"),
    HumanMessage(content="用一句话介绍 LangChain")
]

# 获取回复
response = llm.invoke(messages)
print(response.content)
```

### 5. 使用提示词模板

```python
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

# 创建模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}专家"),
    ("human", "请解释{topic}，用{style}风格")
])

# 填充并执行
llm = ChatOpenAI()
prompt = template.format_messages(
    role="Python",
    topic="装饰器",
    style="通俗易懂"
)
response = llm.invoke(prompt)
print(response.content)
```

## 最佳实践

1. **使用环境变量管理密钥** - 永远不要硬编码 API Key
2. **选择合适的模型** - 根据任务复杂度选择 gpt-4o（通用）或 claude（推理）
3. **利用提示词模板** - 保持代码整洁，便于维护
4. **开启 LangSmith 追踪** - 生产环境必须启用，便于调试
5. **渐进式开发** - 从简单 Chain 开始，逐步添加 Agent、Memory

## 常见陷阱

| 问题 | 解决方案 |
|------|----------|
| API Key 未设置 | 检查环境变量或使用 dotenv |
| 模型响应慢 | 使用流式传输 `stream=True` |
| Agent 循环 | 设置 `max_iterations` 限制 |
| 上下文过长 | 使用 [[LangChain_Memory]] 的压缩功能 |
| 工具调用失败 | 确保工具函数有正确的 docstring |

## 相关阅读

- [[LangChain]] - LangChain 完整学习笔记
- [[LangChain_Memory]] - 对话历史管理
- [[Agent]] - 智能体概念详解
- [[PromptTemplate]] - 提示词模板

## 参考资源

- [官方文档](https://python.langchain.com)
- [LangSmith 平台](https://smith.langchain.com)
- [GitHub 仓库](https://github.com/langchain-ai/langchain)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/blob/master/cookbook)
- [模型提供商列表](https://python.langchain.com/docs/integrations/providers/)

---

**下一步行动：**
- [ ] 运行上面的 Hello World 示例
- [ ] 尝试添加自定义工具
- [ ] 启用 LangSmith 查看调用追踪
- [ ] 一周后复习 [[LangChain_Memory]]
