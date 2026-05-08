---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - PostgreSQL
  - 事务
created: 2026-05-08
---
# PostgreSQL 事务与锁

## 定义

PostgreSQL 事务与锁机制用于保证并发读写下的数据一致性，核心包括 MVCC、隔离级别、行锁、表锁和死锁检测。

## 要点

- MVCC 让读写并发更高效。
- 长事务会影响清理和膨胀。
- 行锁适合控制同一业务资源并发修改。
- 死锁需要通过固定访问顺序和短事务降低概率。

## 相关概念

- [[PostgreSQL 核心能力总览]]
- [[MySQL/MySQL_事务与锁]]
