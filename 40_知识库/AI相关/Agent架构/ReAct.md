---
created: 2025-03-02
area: "[[AI相关]]"
tags: [ai, agent, architecture, llm]
---

# ReAct

## 定义

ReAct（Reasoning + Acting）是一种让LLM交替进行"推理"和"行动"的Agent架构模式。它通过显式地展示推理过程（Thought）和行动（Action），使Agent能够更好地处理复杂任务。

## 核心思想

ReAct的核心理念是：**推理和行动应该交替进行，而不是分离的**。

传统的做法要么只有推理（纯LLM生成），要么只有行动（函数调用）。ReAct将两者结合，让Agent在每一步都能：

1. **思考**（Reasoning）：基于当前状态，思考下一步该做什么
2. **行动**（Acting）：执行具体的工具调用或操作
3. **观察**（Observation）：获取行动的结果
4. **循环**：重复上述过程直到任务完成

## 工作流程

```python
def react_agent(task):
    history = []
    while not is_finished():
        # 1. 推理：下一步该做什么
        thought = llm.generate(
            f"Task: {task}\nHistory: {history}\nThought:"
        )

        # 2. 行动：执行工具
        action = parse_action(thought)
        observation = execute_tool(action)

        # 3. 记录历史
        history.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

    return final_answer
```

## ReAct的Prompt模板

```
You are an AI assistant that helps users by reasoning through problems and taking actions.

When responding, follow this format:
Thought: [Your reasoning about what to do next]
Action: [The tool or action to take]
Observation: [The result of the action]
... (repeat Thought/Action/Observation as needed)
Thought: [Final reasoning]
Final Answer: [Your final answer to the user]

Available tools:
- search: Search for information
- calculator: Perform calculations
- code: Execute Python code
```

## 优点

1. **可解释性强**：每一步的推理过程都是透明的，便于调试和理解
2. **错误恢复**：当行动失败时，Agent可以根据观察结果重新推理
3. **灵活适应**：适用于需要多步推理和工具调用的复杂任务
4. **Few-shot学习**：通过示例Prompt，可以快速教会Agent新的任务模式

## 常见问题及解决方案

| 问题                   | 解决方案                                       |
| ---------------------- | ---------------------------------------------- |
| 推理错误               | 引入 [[Reflexion]] 机制，让Agent反思自己的错误 |
| 推理效率低             | 提供高质量的Few-shot示例                       |
| 任务太长导致上下文溢出 | 分层ReAct，把任务拆成子任务                    |
| 陷入无限循环           | 设置最大迭代次数，引入进展检测机制             |

## 与Plan-and-Execute的区别

| 维度       | ReAct                | Plan-and-Execute       |
| ---------- | -------------------- | ---------------------- |
| 规划方式   | 逐步推理，边想边做   | 先制定完整计划，再执行 |
| 适应性     | 高，每步都可以调整   | 中，需要显式触发重规划 |
| 适用场景   | 探索性任务、动态环境 | 目标明确的复杂任务     |
| 实现复杂度 | 相对简单             | 需要额外的计划生成器   |

## 相关概念

- [[AI Agent]] - Agent的核心概念
- [[Reflexion]] - Agent自我反思机制
- [[Plan-and-Execute]] - 计划-执行模式
- [[LangChain]] - 提供ReAct实现的框架
- [[LangGraph]] - 更灵活的Agent工作流框架
- [[Chain-of-Thought]] - 思维链提示技术

## 参考资料

- 论文：_ReAct: Synergizing Reasoning and Acting in Language Models_ (Yao et al., 2022)
- LangChain ReAct Agent文档
