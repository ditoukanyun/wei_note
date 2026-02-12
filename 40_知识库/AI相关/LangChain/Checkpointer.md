---
type: wiki
created: 2025-02-12
tags: [langchain, memory, langgraph]
---

# Checkpointer（检查点器）

## 定义

Checkpointer 是 LangGraph 中用于将智能体状态持久化到数据库的组件。它允许线程在任何时间点被保存和恢复。

## 核心功能

1. **状态持久化**: 将图的状态保存到存储后端
2. **线程恢复**: 通过 thread_id 恢复之前的对话状态
3. **版本控制**: 支持状态的历史版本

## 常见实现

| 实现类 | 用途 | 适用场景 |
|--------|------|----------|
| MemorySaver | 内存存储 | 开发和测试 |
| PostgresSaver | PostgreSQL 存储 | 生产环境 |
| RedisSaver | Redis 存储 | 高性能缓存场景 |
| SQLiteSaver | SQLite 存储 | 轻量级本地应用 |

## 使用示例

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

checkpointer = MemorySaver()

builder = StateGraph(State)
# ... 添加节点和边

graph = builder.compile(checkpointer=checkpointer)
```

## 相关概念

- [[LangChain_Memory]] - 记忆系统概述
- [[短期记忆]] - 使用 checkpointer 的短期记忆
- [[Store]] - 长期记忆的存储机制