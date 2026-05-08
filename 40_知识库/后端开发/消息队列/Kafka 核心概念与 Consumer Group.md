---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Kafka
  - 消息队列
created: 2026-05-08
---
# Kafka 核心概念与 Consumer Group

## 定义

Kafka 是分布式事件流平台，核心概念包括 Topic、Partition、Producer、Consumer、Consumer Group 和 Offset。

## 要点

- Topic 被拆成多个 Partition 以提升吞吐。
- 同一 Consumer Group 内一个分区同一时刻只被一个消费者消费。
- Offset 表示消费进度。
- 同一 Key 的消息通常进入同一分区以保持局部顺序。

## 相关概念

- [[消息队列总览：RabbitMQ、Kafka 与可靠消息]]
- [[消息幂等与顺序消费]]
