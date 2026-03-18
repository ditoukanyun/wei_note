---
type: wiki
tags: [mysql, explain, 执行计划, 性能优化]
created: 2026-03-18
---
# MySQL 执行计划分析
## 基本命令
```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 1001 AND status = 'PAID';
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1001;
```

## 重点关注字段
- `type`：访问方式（`const > ref > range > index > ALL`）
- `key`：实际使用索引
- `rows`：预估扫描行数
- `Extra`：是否出现 `Using filesort`、`Using temporary`

## 诊断思路
1. 先看是否命中预期索引（`key`）。
2. 再看扫描量（`rows`）是否过大。
3. 检查 `Extra` 是否有临时表或文件排序。
4. 对比优化前后计划，验证收益。

## 常见优化动作
- 补充或调整组合索引顺序
- 改写条件，避免索引失效
- 缩小返回列，避免 `SELECT *`
- 将大分页改为游标/延迟关联

## 配套阅读
- [[MySQL_索引优化]]
- [[MySQL_JOIN_详解]]
