---
area: [[后端开发]]
tags:
  - springboot
  - 架构模式
  - 读写分离
created: 2026-04-28
---
# CQRS

## 定义

CQRS（Command Query Responsibility Segregation）是一种将写入命令模型与读取查询模型分离的架构模式。命令侧处理业务变更和约束，查询侧维护面向展示或检索优化的读模型。

## 要点

- Command 负责改变状态，例如创建订单、支付订单。
- Query 只负责读取数据，不承担业务写入。
- 写模型可以产生 [[领域事件]]，由投影器生成读模型。
- 读模型通常是可重建的，可以从事件重新投影。
- CQRS 会引入最终一致性：读模型可能短暂落后于写模型。

## 示例

订单写模型接收 `OrderCreated`、`OrderPaid` 等业务动作并产生事件；投影器消费事件生成订单摘要读模型，供列表页和详情页查询。

对应模块：[[SpringBoot/33-SpringBoot-CQRS读模型]]。

## 相关概念

- [[领域事件]]
- [[Event Sourcing]]
- [[最终一致性]]
- [[读写分离]]
