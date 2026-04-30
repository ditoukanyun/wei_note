---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - PostgreSQL
  - 数据库
created: 2026-04-30
---
# PostgreSQL 核心能力总览

## 学习目标

- 理解 PostgreSQL 与 MySQL 在类型系统、索引、事务和扩展能力上的差异。
- 掌握 PostgreSQL 常用数据类型、索引、事务、锁和查询优化入口。
- 能判断哪些业务场景适合优先考虑 PostgreSQL。

## 核心概念

- **丰富类型系统**：数组、JSONB、枚举、范围类型和自定义类型。
- **索引能力**：B-tree、GIN、GiST、BRIN 等索引适配不同查询模式。
- **MVCC**：通过多版本并发控制提升读写并发能力。
- **JSONB**：兼顾关系模型和半结构化数据查询。
- **扩展机制**：通过 extension 扩展全文检索、地理信息、向量检索等能力。

## 推荐阅读顺序

1. [[MySQL/MySQL_高级操作总览]]：先建立关系数据库基础。
2. [[MySQL/MySQL_索引优化]]：理解索引和执行计划。
3. 本文：对比学习 PostgreSQL 核心能力。
4. 后续拆分文章：数据类型、索引、事务锁、JSONB、全文检索。

## 工程实践清单

- 复杂查询、JSON 字段检索、全文检索和扩展能力强依赖场景优先评估 PostgreSQL。
- 查询优化仍从 SQL、索引、执行计划和数据分布开始。
- JSONB 适合半结构化扩展字段，不应替代清晰的核心关系模型。
- 生产环境需要关注 autovacuum、连接池、慢查询和备份恢复。

## 后续可拆分文章

- [[PostgreSQL 基础与数据类型]]
- [[PostgreSQL 索引原理与优化]]
- [[PostgreSQL 事务与锁]]
- [[PostgreSQL JSONB 与全文检索]]
- [[PostgreSQL 与 MySQL 对比]]

## 相关链接

- [[后端开发 MOC]]
- [[MySQL/MySQL_高级操作总览]]
- [[Elasticsearch 搜索体系总览]]
