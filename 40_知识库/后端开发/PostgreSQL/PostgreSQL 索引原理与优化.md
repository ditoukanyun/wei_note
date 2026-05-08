---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - PostgreSQL
  - 索引
created: 2026-05-08
---
# PostgreSQL 索引原理与优化

## 定义

PostgreSQL 索引用于加速查询、排序和约束检查，常见类型包括 B-tree、GIN、GiST、BRIN 和 Hash。

## 要点

- B-tree 适合等值、范围和排序。
- GIN 适合 JSONB、数组和全文检索。
- 低选择性字段不一定适合单列索引。
- 索引会增加写入和存储成本。

## 相关概念

- [[PostgreSQL 核心能力总览]]
- [[PostgreSQL JSONB 与全文检索]]
