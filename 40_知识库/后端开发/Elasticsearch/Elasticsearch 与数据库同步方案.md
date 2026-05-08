---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Elasticsearch
  - 数据同步
created: 2026-05-08
---
# Elasticsearch 与数据库同步方案

## 定义

Elasticsearch 与数据库同步方案是把主数据库中的业务数据同步到搜索索引的工程机制。核心目标是在主库负责强一致写入的前提下，让 Elasticsearch 承担搜索和分析查询。

## 常见模式

- 应用双写：业务写库后同步写 Elasticsearch，实现简单但一致性风险高。
- 事务性发件箱：业务事务内写 Outbox，再异步投递索引更新事件。
- Binlog/CDC：监听数据库变更日志，增量更新索引。
- 定时全量/增量任务：适合低频变化或离线重建。

## 实践要点

- 明确主库是事实来源，Elasticsearch 索引可重建。
- 同步失败要有重试、死信和人工修复入口。
- 索引结构变更要支持重建和别名切换。
- 接受搜索结果存在短暂延迟，并在产品体验上处理。

## 相关概念

- [[Elasticsearch 搜索体系总览]]
- [[Transactional Outbox]]
- [[最终一致性]]
- [[消息队列总览：RabbitMQ、Kafka 与可靠消息]]
