---
area: [[后端开发]]
tags:
  - springboot
  - 事件驱动
  - 最终一致性
created: 2026-04-28
---
# Transactional Outbox

## 定义

Transactional Outbox 是一种解决业务数据写入与消息发布一致性的模式：在同一个本地事务中同时写入业务表和 outbox 事件表，再由异步发布器扫描 outbox 表并发布消息。

## 要点

- 业务数据和待发布事件必须同事务写入。
- 发布器只处理 `PENDING` 事件，成功后标记 `SENT`。
- 发布失败时保留重试次数和错误信息，达到上限后进入死信状态。
- 消息可能重复发布，消费者需要基于稳定 `eventId` 做 [[幂等性]]。
- Outbox 强调最终一致性，而不是同步强一致。

## 示例

创建订单时同时写入 `OrderCreated` outbox 事件；发布器稍后扫描并发送消息。如果消息系统短暂不可用，事件仍保留在 outbox 中等待重试。

对应模块：[[SpringBoot/31-SpringBoot-事务性发件箱]]。

## 相关概念

- [[领域事件]]
- [[幂等性]]
- [[最终一致性]]
- [[Saga]]
