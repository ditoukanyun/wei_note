---
type: wiki
created: 2026-02-12
area: "[[SoftwareEngineering]]"
tags: [langchain, ai, llm]
---

# Agent

Agent 是一种能够感知环境、进行推理并采取行动的智能体。在 LangChain 中，Agent 是一个可以调用工具（Tools）的 AI 系统。

## 核心特征

- **推理能力** - 能够分析输入并决定如何响应
- **工具调用** - 可以访问外部 API、数据库等
- **状态管理** - 维护对话上下文和工作流状态
- **自主决策** - 根据目标自主规划执行步骤

## 使用场景

- 问答系统（结合检索）
- 任务自动化（如预订、查询）
- 代码助手
- 数据分析代理

## 相关概念

- [[Tool]] - Agent 调用的外部功能
- [[Chain]] - Agent 的基础执行单元
- [[Memory]] - 状态管理组件
- [官方文档](https://python.langchain.com/docs/concepts/agents/)
