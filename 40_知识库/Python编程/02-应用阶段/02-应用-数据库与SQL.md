---
title: Python数据库与SQL
description: MySQL数据库、SQL语句、Python数据库操作、ORM基础（Day36-45）
date: 2026-02-10
tags:
  - python
  - mysql
  - sql
  - database
  - orm
  - pymysql
category: 应用阶段
status: active
aliases:
  - 数据库
  - SQL
  - MySQL
  - Day36-45
parent: "[[00-导航-Python编程导航]]"
up: "[[00-MOC-知识地图]]"
---

# Python数据库与SQL (Day 36-45)

> 掌握关系型数据库MySQL和SQL语言，学会用Python操作数据库

---

## Day 36-40: SQL基础

### SQL分类

| 类型 | 全称 | 用途 | 常用命令 |
|------|------|------|----------|
| **DDL** | Data Definition Language | 定义数据结构 | CREATE, ALTER, DROP |
| **DML** | Data Manipulation Language | 操作数据 | INSERT, UPDATE, DELETE |
| **DQL** | Data Query Language | 查询数据 | SELECT |
| **DCL** | Data Control Language | 控制权限 | GRANT, REVOKE |

### DDL - 数据定义

```sql
-- 创建数据库
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mydb;

-- 创建表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) COMMENT '邮箱',
    age INT CHECK (age >= 0 AND age <= 150) COMMENT '年龄',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 修改表
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;
ALTER TABLE users MODIFY COLUMN age TINYINT UNSIGNED;
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users RENAME TO customers;

-- 删除表
DROP TABLE IF EXISTS users;

-- 创建索引
CREATE INDEX idx_username ON users(username);
CREATE UNIQUE INDEX idx_email ON users(email);
```

### DML - 数据操作

```sql
-- 插入数据
INSERT INTO users (username, email, age) VALUES ('alice', 'alice@example.com', 25);

INSERT INTO users (username, email, age) VALUES 
    ('bob', 'bob@example.com', 30),
    ('charlie', 'charlie@example.com', 35);

-- 更新数据
UPDATE users SET age = 26, email = 'alice.new@example.com' WHERE id = 1;
UPDATE users SET status = 'inactive' WHERE age > 100;

-- 删除数据
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- 安全模式 (防止忘记WHERE)
SET SQL_SAFE_UPDATES = 1;
```

### DQL - 数据查询

```sql
-- 基础查询
SELECT * FROM users;
SELECT username, email FROM users;
SELECT DISTINCT status FROM users;

-- 条件查询
SELECT * FROM users WHERE age > 25;
SELECT * FROM users WHERE age BETWEEN 20 AND 30;
SELECT * FROM users WHERE username LIKE 'a%';  -- 以a开头
SELECT * FROM users WHERE email IS NOT NULL;
SELECT * FROM users WHERE status IN ('active', 'pending');

-- 排序和分页
SELECT * FROM users ORDER BY age DESC;
SELECT * FROM users ORDER BY age ASC, created_at DESC;
SELECT * FROM users LIMIT 10;                    -- 前10条
SELECT * FROM users LIMIT 10 OFFSET 20;          -- 第3页 (每页10条)
SELECT * FROM users LIMIT 20, 10;                -- 同上 (MySQL语法)

-- 聚合函数
SELECT 
    COUNT(*) AS total_users,
    AVG(age) AS avg_age,
    MAX(age) AS max_age,
    MIN(age) AS min_age,
    SUM(salary) AS total_salary
FROM users;

-- 分组查询
SELECT status, COUNT(*) AS count, AVG(age) AS avg_age
FROM users
GROUP BY status
HAVING count > 5;  -- 分组后的过滤

-- 多表查询
-- 内连接
SELECT u.username, o.order_id, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 左连接
SELECT u.username, o.order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;  -- 所有用户,包括没订单的

-- 右连接
SELECT u.username, o.order_id
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- 全外连接 (MySQL不支持,需要UNION)
SELECT u.username, o.order_id FROM users u LEFT JOIN orders o ON u.id = o.user_id
UNION
SELECT u.username, o.order_id FROM users u RIGHT JOIN orders o ON u.id = o.user_id;

-- 子查询
SELECT * FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- EXISTS
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 窗口函数 (MySQL 8.0+)
SELECT 
    username,
    age,
    RANK() OVER (ORDER BY age DESC) AS age_rank,
    ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at) AS row_num
FROM users;
```

---

## Day 41-43: MySQL进阶

### 索引优化

```sql
-- 索引类型
-- 1. 主键索引: PRIMARY KEY
-- 2. 唯一索引: UNIQUE
-- 3. 普通索引: INDEX
-- 4. 全文索引: FULLTEXT (MySQL 5.6+ InnoDB支持)
-- 5. 组合索引: INDEX(a, b, c)

-- 创建索引
CREATE INDEX idx_age ON users(age);
CREATE INDEX idx_name_age ON users(username, age);

-- 查看索引
SHOW INDEX FROM users;

-- 删除索引
DROP INDEX idx_age ON users;

-- 分析查询 (查看执行计划)
EXPLAIN SELECT * FROM users WHERE age > 25;
```

### 视图

```sql
-- 创建视图
CREATE VIEW active_users AS
SELECT id, username, email
FROM users
WHERE status = 'active';

-- 使用视图
SELECT * FROM active_users WHERE age > 25;

-- 删除视图
DROP VIEW IF EXISTS active_users;
```

### 存储过程

```sql
-- 创建存储过程
DELIMITER //
CREATE PROCEDURE GetUserById(IN user_id INT)
BEGIN
    SELECT * FROM users WHERE id = user_id;
END //
DELIMITER ;

-- 调用
CALL GetUserById(1);

-- 带输出参数的存储过程
DELIMITER //
CREATE PROCEDURE GetUserCount(OUT total INT)
BEGIN
    SELECT COUNT(*) INTO total FROM users;
END //
DELIMITER ;

CALL GetUserCount(@total);
SELECT @total;
```

---

## Day 44: Python操作MySQL

### 使用 pymysql

```python
import pymysql
from pymysql.cursors import DictCursor

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='mydb',
    charset='utf8mb4',
    cursorclass=DictCursor  # 返回字典格式
)

try:
    with conn.cursor() as cursor:
        # 查询
        sql = "SELECT * FROM users WHERE age > %s"
        cursor.execute(sql, (25,))
        results = cursor.fetchall()
        
        for row in results:
            print(f"{row['username']}: {row['age']}")
        
        # 插入
        sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
        cursor.execute(sql, ('david', 'david@example.com'))
        
        # 批量插入
        data = [
            ('eve', 'eve@example.com'),
            ('frank', 'frank@example.com')
        ]
        cursor.executemany(sql, data)
        
        # 更新
        sql = "UPDATE users SET age = %s WHERE id = %s"
        cursor.execute(sql, (28, 1))
        
        # 提交事务
        conn.commit()
        print(f"影响了 {cursor.rowcount} 行")
        
except Exception as e:
    conn.rollback()
    print(f"错误：{e}")
finally:
    conn.close()
```

### 使用 ORM (SQLAlchemy)

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

# 连接数据库
engine = create_engine('mysql+pymysql://root:password@localhost/mydb')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# CRUD操作
# 创建
new_user = User(username='alice', email='alice@example.com', age=25)
session.add(new_user)
session.commit()

# 查询
user = session.query(User).filter_by(username='alice').first()
users = session.query(User).filter(User.age > 20).all()

# 更新
user.age = 26
session.commit()

# 删除
session.delete(user)
session.commit()

session.close()
```

---

## 🎯 实战案例

### 案例: 用户管理系统

```python
import pymysql
from contextlib import contextmanager

class Database:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    
    @contextmanager
    def get_cursor(self):
        conn = pymysql.connect(**self.config)
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class UserManager:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, username, email, age):
        with self.db.get_cursor() as cursor:
            sql = "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, email, age))
            return cursor.lastrowid
    
    def get_user(self, user_id):
        with self.db.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
    
    def list_users(self, page=1, per_page=10):
        with self.db.get_cursor() as cursor:
            offset = (page - 1) * per_page
            sql = "SELECT * FROM users LIMIT %s OFFSET %s"
            cursor.execute(sql, (per_page, offset))
            return cursor.fetchall()
    
    def update_user(self, user_id, **kwargs):
        with self.db.get_cursor() as cursor:
            fields = ', '.join(f"{k} = %s" for k in kwargs)
            sql = f"UPDATE users SET {fields} WHERE id = %s"
            values = list(kwargs.values()) + [user_id]
            cursor.execute(sql, values)
            return cursor.rowcount
    
    def delete_user(self, user_id):
        with self.db.get_cursor() as cursor:
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            return cursor.rowcount

# 使用
db = Database('localhost', 'root', 'password', 'mydb')
user_manager = UserManager(db)

# 创建用户
user_id = user_manager.create_user('张三', 'zhangsan@example.com', 25)

# 查询用户
user = user_manager.get_user(user_id)
print(user)

# 列出用户
users = user_manager.list_users(page=1, per_page=5)
for user in users:
    print(user)
```

---

## 📝 重点总结

### SQL优化原则

1. **索引优化**: 为WHERE、ORDER BY、JOIN字段添加索引
2. **避免SELECT ***: 只查询需要的字段
3. **分页优化**: 大数据量使用游标或覆盖索引
4. **批量操作**: 使用INSERT批量插入，减少连接次数
5. **事务控制**: 合理使用事务，避免长事务

### Python数据库最佳实践

```python
# ✅ 使用上下文管理器
with conn.cursor() as cursor:
    cursor.execute(sql)

# ✅ 使用参数化查询 (防止SQL注入)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# ❌ 不要这样
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ 使用连接池
from sqlalchemy.pool import QueuePool
engine = create_engine('mysql+pymysql://...', poolclass=QueuePool, pool_size=10)
```

---

**下一步**: [[03-方向A-Web开发-Django全栈|Django全栈]] → 学习Django框架
