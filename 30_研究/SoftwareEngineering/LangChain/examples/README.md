# LangChain 快速开始 示例集合

此目录用于存放 LangChain 的快速开始示例、最小可运行代码片段。

## 示例列表

| 文件 | 说明 |
|------|------|
| `hello_world.py` | 第一个 Agent，展示工具调用 |
| `simple_chat.py` | 直接调用 LLM，无需 Agent |

## 运行方法

```bash
# 安装依赖
pip install langchain openai python-dotenv

# 设置环境变量
export OPENAI_API_KEY="your-key"

# 运行示例
python hello_world.py
``` 
