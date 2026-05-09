---
type: wiki
tags: [mysql, sql, 数据库]
created: 2026-03-17
---
# MySQL JOIN 详解

## 核心区别图示

```
表 A                    表 B
┌────┬──────┐         ┌────┬──────┐
│ id │ name │         │ id │ age  │
├────┼──────┤         ├────┼──────┤
│ 1  │ 张三 │◄──────►│ 1  │ 20   │  ← INNER JOIN 结果（交集）
│ 2  │ 李四 │         │ 3  │ 25   │
│ 3  │ 王五 │◄──────►│      │      │  ← 表A独有
└────┴──────┘         └────┴──────┘
       │
       ▼
LEFT JOIN 结果：A全部 + B匹配（B无匹配则NULL）
RIGHT JOIN 结果：B全部 + A匹配（A无匹配则NULL）
FULL JOIN 结果：A全部 + B全部（MySQL不支持，需UNION模拟）
```

---

## 数据准备

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(20)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2)
);

-- 插入数据
INSERT INTO users VALUES (1, '张三'), (2, '李四'), (3, '王五');
INSERT INTO orders VALUES (1, 1, 100), (2, 1, 200), (3, 4, 300);  -- user_id=4 不存在
```

**users 表：**
| id | name |
|---:|:-----|
| 1  | 张三 |
| 2  | 李四 |
| 3  | 王五 |

**orders 表：**
| id | user_id | amount |
|---:|--------:|-------:|
| 1  | 1       | 100    |
| 2  | 1       | 200    |
| 3  | 4       | 300    |

---

## 1. INNER JOIN（内连接）

**只返回两个表中匹配的行**（交集）

```sql
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

**结果：**
| name | amount |
|:-----|-------:|
| 张三 | 100    |
| 张三 | 200    |

> > **特点**：<br>
> - 只保留两表匹配的数据<br>
> - 结果行数 ≤ 两表匹配行的笛卡尔积<br>
> - 李四、王五没有订单，不显示；user_id=4 的订单没有对应用户，也不显示

---

## 2. LEFT JOIN（左连接）

**返回左表全部 + 右表匹配的行**，右表无匹配则填充 NULL

```sql
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

**结果：**
| name | amount |
|:-----|-------:|
| 张三 | 100    |
| 张三 | 200    |
| 李四 | NULL   |  ← 没有订单，amount 为 NULL
| 王五 | NULL   |  ← 没有订单，amount 为 NULL

> > **典型场景**：<br>
> - 查询所有用户及其订单（包括没有订单的用户）<br>
> - 查找"有A无B"的数据：`WHERE B.id IS NULL`

### 实用技巧：查找没有订单的用户

```sql
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;  -- 筛选左表独有

-- 结果：李四、王五
```

---

## 3. RIGHT JOIN（右连接）

**返回右表全部 + 左表匹配的行**，左表无匹配则填充 NULL

```sql
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

**结果：**
| name | amount |
|:-----|-------:|
| 张三 | 100    |
| 张三 | 200    |
| NULL | 300    |  ← user_id=4 没有对应用户

> > **注意**：<br>
> - 实际开发中较少使用，通常用 LEFT JOIN 调换表顺序替代<br>
> - `A RIGHT JOIN B` 等价于 `B LEFT JOIN A`

---

## 4. FULL JOIN（全外连接）

**返回两表所有行**，不匹配处填充 NULL

```sql
-- MySQL 不直接支持 FULL JOIN，需用 UNION 模拟
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id

UNION

SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

**结果：**
| name | amount |
|:-----|-------:|
| 张三 | 100    |
| 张三 | 200    |
| 李四 | NULL   |
| 王五 | NULL   |
| NULL | 300    |

---

## 5. CROSS JOIN（交叉连接）

**笛卡尔积**，两表行数相乘，无 ON 条件

```sql
SELECT u.name, o.amount
FROM users u
CROSS JOIN orders o;
-- 或：FROM users u, orders o
```

**结果**：3 × 3 = 9 行（所有可能的组合）

> > **警告**：<br>
> - 大数据表慎用，结果集可能爆炸<br>
> - 常用于生成测试数据或组合查询

---

## 6. 自连接（SELF JOIN）

**表与自身连接**，常用于树形结构（如部门层级、上下级关系）

```sql
-- 查询员工及其上级
SELECT e.name AS 员工, m.name AS 上级
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

---

## 对比总结

| JOIN 类型   | 结果说明        | 使用频率  | 记忆口诀 |
| :-------- | :---------- | :---: | :--- |
| **INNER** | 两表匹配的行      | ⭐⭐⭐⭐⭐ | 交集   |
| **LEFT**  | 左表全部 + 右表匹配 | ⭐⭐⭐⭐⭐ | 左为主  |
| **RIGHT** | 右表全部 + 左表匹配 |  ⭐⭐   | 右为主  |
| **FULL**  | 两表全部        |  ⭐⭐   | 并集   |
| **CROSS** | 笛卡尔积        |   ⭐   | 全组合  |

---

## 多表连接示例

```sql
-- 查询：用户名、订单号、商品名
SELECT
    u.name AS 用户,
    o.id AS 订单号,
    p.name AS 商品
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE u.id = 1;
```

---

## 性能优化建议

1. **索引**：JOIN 条件的字段必须有索引（通常是外键）
2. **小表驱动大表**：LEFT JOIN 时左表尽量小
3. **避免 SELECT ***：只查询需要的字段
4. **EXPLAIN 分析**：使用 `EXPLAIN` 查看执行计划

```sql
EXPLAIN SELECT * FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

---

## 相关链接

- [[MySQL_索引优化]]
- [[MySQL_执行计划分析]]
- [[SQL_常用查询技巧]]

## 实践检查清单

- JOIN 条件是否使用主键、外键或高选择性索引。
- 是否确认 LEFT JOIN 的主表方向符合业务语义。
- 是否避免无条件 CROSS JOIN 造成笛卡尔积。
- 是否用 EXPLAIN 检查扫描行数、连接顺序和索引使用。
- 是否只选择需要字段，避免连接后传输过多列。

## 案例复盘

订单列表查询通常需要连接用户、订单、订单项和商品表。若页面只展示订单摘要，就不应一次性 JOIN 商品明细；可以先查订单分页，再按订单 ID 批量查询明细，避免分页被多表连接放大。
