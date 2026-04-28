---
area: [[后端开发]]
tags:
  - springboot
  - 事件驱动
  - 审计
created: 2026-04-28
---
# Event Sourcing

## 定义

Event Sourcing 是一种以事件流作为事实来源的建模方式：系统不直接覆盖保存当前状态，而是追加描述状态变化的事件，并通过重放事件流计算当前状态。

## 要点

- 事件是事实来源，当前状态是事件重放的结果。
- 事件应只追加，不应随意修改历史事件。
- 每个聚合内通常需要版本号保证事件顺序。
- 天然保留审计轨迹，可以追溯状态如何变化。
- 当事件过多时，可使用 [[Snapshot]] 减少重放成本。

## 示例

账户不直接保存余额变更后的最终值，而是保存 `AccountOpened`、`MoneyDeposited`、`MoneyWithdrawn` 事件；查询账户时按顺序 replay 得到账户余额。

对应模块：[[SpringBoot/34-SpringBoot-事件溯源与快照]]。

## 相关概念

- [[Snapshot]]
- [[领域事件]]
- [[CQRS]]
- [[最终一致性]]
