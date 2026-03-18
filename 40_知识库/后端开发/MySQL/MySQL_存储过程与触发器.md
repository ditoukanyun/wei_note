---
type: wiki
tags: [mysql, 存储过程, 触发器]
created: 2026-03-18
---
# MySQL 存储过程与触发器
## 存储过程
适合封装重复 SQL 逻辑，减少应用侧重复代码。

```sql
DELIMITER //
CREATE PROCEDURE GetUserById(IN p_user_id INT)
BEGIN
  SELECT * FROM users WHERE id = p_user_id;
END //
DELIMITER ;

CALL GetUserById(1001);
```

## 触发器
用于在 `INSERT/UPDATE/DELETE` 前后自动执行逻辑。

```sql
CREATE TRIGGER trg_order_after_insert
AFTER INSERT ON orders
FOR EACH ROW
INSERT INTO order_log(order_id, action, created_at)
VALUES (NEW.id, 'INSERT', NOW());
```

## 适用边界
- 适合：强约束、审计日志、规则固化。
- 谨慎：复杂业务流程，排障和版本管理成本高。

## 配套阅读
- [[MySQL_事务与锁]]
