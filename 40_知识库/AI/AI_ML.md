---
type: wiki
area: "[[AI]]"
tags: [AI, ML]
created: 2026-05-08
---
# AI_ML
AI_ML 是机器学习、LLM 应用开发和 LangChain 相关能力的聚合分类。

## 相关概念
- [[LangChain-Agents]]
- [[LangChain-Chains]]
- [[LangChain-Retrieval]]

## 学习路径

```mermaid
flowchart LR
  A[LLM 基础] --> B[Prompt 和 Chain]
  B --> C[Retrieval 和 Memory]
  C --> D[Agents 和工具]
  D --> E[评测和部署]
```

## 实践检查清单

- 是否能用最小 Chain 跑通输入、模型和输出解析。
- 检索系统是否有文档切分、向量库和召回评估。
- Memory 是否区分短期状态和长期记忆。
- Agent 工具是否有 schema、权限和错误处理。
- 是否用 LangSmith 或日志记录运行过程。

## 案例

做一个问答机器人时，先实现简单 Prompt，再加入 Retrieval，最后再考虑 Agent 工具调用。这样能逐层定位质量问题。

## 常见误区

- 一开始就上 Agent，基础链路还不可控。
- 把 Memory 当作无限聊天记录存储。
- 没有评测集，调整参数全凭感觉。
