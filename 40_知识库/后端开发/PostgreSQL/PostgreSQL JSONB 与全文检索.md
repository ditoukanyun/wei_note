---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - PostgreSQL
  - 搜索
created: 2026-05-08
---
# PostgreSQL JSONB 与全文检索

## 定义

PostgreSQL JSONB 与全文检索让关系数据库在结构化数据之外支持半结构化文档查询和基础文本搜索。

## 要点

- JSONB 支持索引、字段查询和包含关系判断。
- 全文检索可用 `tsvector`、`tsquery` 和 GIN 索引。
- 复杂搜索体验仍可考虑 [[Elasticsearch 搜索体系总览]]。

## 相关概念

- [[PostgreSQL 核心能力总览]]
- [[Elasticsearch 搜索体系总览]]
