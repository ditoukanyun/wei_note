---
type: wiki
created: 2025-02-12
tags: [langchain, memory, storage]
---

# Store（长期记忆存储）

## 定义

Store 是 LangGraph 提供的长期记忆存储机制，用于跨会话保存和召回用户特定或应用级别的数据。

## 核心特点

1. **持久化**: 数据在会话结束后仍然保留
2. **命名空间**: 使用层级命名空间组织数据
3. **跨线程**: 可在任何线程中访问
4. **JSON 文档**: 以 JSON 格式存储记忆

## 存储结构

```
Namespace (命名空间)
  └── Key (键)
        └── Value (JSON 文档)
```

## API 方法

- `get(namespace, key)`: 获取指定记忆
- `put(namespace, key, value)`: 保存/更新记忆
- `search(namespace, query)`: 搜索记忆
- `delete(namespace, key)`: 删除记忆

## 命名空间设计示例

```python
# 用户偏好
("users", user_id, "preferences")

# 应用配置
("app", "settings")

# 会话历史
("conversations", user_id)
```

## 相关概念

- [[LangChain_Memory]] - 记忆系统概述
- [[Checkpointer]] - 短期记忆的检查点器
- [[长期记忆]] - 长期记忆详细说明