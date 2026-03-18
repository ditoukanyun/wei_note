---
created: 2025-03-02
area: "[[AI相关]]"
tags: [ai, agent, reflection, learning]
---

# Reflexion

## 定义

Reflexion（自我反思）是一种让Agent能够从错误中学习和改进的机制。通过让Agent回顾自己的行动历史，识别错误并生成改进策略，从而提升后续任务的成功率。

## 核心思想

传统Agent（如基础ReAct）的问题：

- 犯过的错误会重复犯
- 没有从失败中学习的能力
- 每次都是"从零开始"

Reflexion的解决方案：

- **显式反思**：让Agent用语言描述自己的错误
- **经验积累**：将反思结果保存为"经验教训"
- **持续改进**：后续任务可以参考之前的经验

## 工作流程

```python
def reflexion_agent(task):
    # 加载历史经验
    experiences = memory.retrieve_relevant(task)

    # 执行任务（带试错）
    result, history = execute_with_trial(task, experiences)

    # 如果失败，进行反思
    if not result.success:
        reflection = generate_reflection(history, result.error)

        # 保存经验教训
        memory.store({
            "task_type": task.type,
            "mistake": reflection.mistake,
            "lesson": reflection.lesson,
            "better_approach": reflection.suggestion
        })

        # 重试
        result = execute_with_lesson(task, reflection)

    return result
```

## 反思的类型

### 1. 行动层面反思（Action Reflection）

**问题**：选择了错误的工具或参数

**反思内容**：

```
反思：我之前使用了search工具查找代码问题，
但实际上应该用code_analyzer工具来分析。

教训：对于代码相关的问题，优先使用专门的代码分析工具，
而不是通用的搜索。
```

### 2. 推理层面反思（Reasoning Reflection）

**问题**：推理过程有逻辑错误

**反思内容**：

```
反思：我假设用户想要的是A，但实际上从上下文来看，
用户真正想要的是B。

教训：在做假设之前，应该先确认用户的真实意图，
可以通过clarify工具来澄清。
```

### 3. 知识层面反思（Knowledge Reflection）

**问题**：缺乏必要的知识

**反思内容**：

```
反思：我不知道如何处理这种文件格式，
导致任务失败。

教训：遇到不熟悉的文件格式时，
应该先使用file_info工具查看格式信息。
```

## 实现示例

```python
class ReflexionMemory:
    def __init__(self):
        self.experiences = []

    def store_experience(self, task, outcome, reflection):
        """存储一次经验"""
        experience = {
            "task_summary": self.summarize_task(task),
            "outcome": outcome,
            "reflection": reflection,
            "timestamp": time.time()
        }
        self.experiences.append(experience)

    def retrieve_relevant(self, current_task, k=3):
        """检索相关的历史经验"""
        # 计算相似度
        similarities = [
            (exp, self.calculate_similarity(current_task, exp["task_summary"]))
            for exp in self.experiences
        ]

        # 返回最相关的k条经验
        sorted_exp = sorted(similarities, key=lambda x: x[1], reverse=True)
        return [exp for exp, _ in sorted_exp[:k]]


def generate_reflection(history, error):
    """生成反思内容"""
    prompt = f"""
    你刚刚执行了一个任务，但失败了。

    执行历史：
    {format_history(history)}

    错误信息：
    {error}

    请进行反思：
    1. 你犯了什么错误？
    2. 为什么会犯这个错误？
    3. 下次如何避免？
    4. 更好的做法是什么？

    用第一人称回答。
    """

    reflection = llm.generate(prompt)
    return parse_reflection(reflection)
```

## 与强化学习的对比

| 维度     | 传统RL           | Reflexion              |
| -------- | ---------------- | ---------------------- |
| 学习信号 | 奖励/惩罚数值    | 语言形式的反思         |
| 可解释性 | 低（黑盒）       | 高（自然语言）         |
| 样本效率 | 需要大量尝试     | 少量失败即可学习       |
| 泛化能力 | 依赖神经网络泛化 | 显式经验可以跨任务复用 |
| 存储方式 | 模型参数         | 显式记忆库             |

## 实际效果

根据论文实验数据：

- **决策任务**：成功率提升约 20-30%
- **编程任务**：测试通过率提升约 10-15%
- **推理任务**：准确率提升约 15-25%

## 最佳实践

1. **及时反思**：任务失败后立即进行反思，不要积累多个错误
2. **具体明确**：反思要具体到行动和决策，避免泛泛而谈
3. **定期整理**：定期整理和归纳相似的经验教训
4. **优先级管理**：给经验设置重要性评分，优先应用高价值经验
5. **遗忘机制**：定期清理过时或错误的经验

## 相关概念

- [[AI Agent]] - Agent的核心概念
- [[ReAct]] - Reflexion通常与ReAct结合使用
- [[Memory]] - Reflexion需要记忆系统支持
- [[强化学习]] - 传统的试错学习方法

## 参考资料

- 论文：_Reflexion: Language Agents with Verbal Reinforcement Learning_ (Shinn et al., 2023)
