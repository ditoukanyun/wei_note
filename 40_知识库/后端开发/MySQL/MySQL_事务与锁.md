---
type: wiki
tags: [mysql, 事务, 锁, 并发]
created: 2026-03-18
---
# MySQL 事务与锁
## ACID
- 原子性（Atomicity）
- 一致性（Consistency）
- 隔离性（Isolation）
- 持久性（Durability）

## 隔离级别
- 读未提交 `READ UNCOMMITTED`
- 读已提交 `READ COMMITTED`
- 可重复读 `REPEATABLE READ`（MySQL 默认）
- 串行化 `SERIALIZABLE`

## 常见锁
- 共享锁（S 锁）：`LOCK IN SHARE MODE`
- 排他锁（X 锁）：`FOR UPDATE`
- 间隙锁/临键锁：防止幻读（InnoDB）

## 示例
```sql
START TRANSACTION;
SELECT * FROM account WHERE id = 1 FOR UPDATE;
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

## 实战建议
1. 事务尽量短，减少锁持有时间。
2. 访问顺序保持一致，降低死锁概率。
3. 为条件列建索引，避免锁范围扩大。
4. 出现死锁时允许应用层重试。

## 配套阅读
- [[MySQL_执行计划分析]]
