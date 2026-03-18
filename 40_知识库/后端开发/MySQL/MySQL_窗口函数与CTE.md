---
type: wiki
tags: [mysql, 窗口函数, cte, sql]
created: 2026-03-18
---
# MySQL 窗口函数与 CTE
## 窗口函数（MySQL 8.0+）
适合做排名、分组内累计、同比环比等分析。

```sql
SELECT
  user_id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM orders;
```

## CTE（公用表表达式）
让复杂查询更可读，支持递归查询。

```sql
WITH recent_orders AS (
  SELECT * FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
)
SELECT user_id, COUNT(*) AS cnt, SUM(amount) AS total
FROM recent_orders
GROUP BY user_id;
```

## 实战建议
1. 复杂分析优先考虑窗口函数，减少自连接。
2. 对窗口排序字段建索引，降低排序成本。
3. CTE 可读性好，但要关注执行计划是否物化。

## 配套阅读
- [[MySQL_执行计划分析]]
