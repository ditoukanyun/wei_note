---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Elasticsearch
  - 查询
created: 2026-05-08
---
# Elasticsearch 查询 DSL

## 定义

Elasticsearch 查询 DSL 是用 JSON 描述搜索、过滤、排序、分页和聚合的查询语言。它把全文匹配、结构化过滤和相关性评分组合在同一个请求中。

## 常用查询

- `match`：对文本分词后进行全文匹配。
- `term`：精确匹配 keyword、数字、布尔等字段。
- `bool`：组合 `must`、`should`、`filter`、`must_not`。
- `range`：范围查询，常用于时间和数值。
- `aggregations`：聚合统计，用于分组、计数和指标计算。

## 实践要点

- 过滤条件优先放入 `filter`，避免不必要评分。
- 深分页要谨慎，必要时使用 `search_after`。
- 查询字段和 Mapping 设计必须一起考虑。

## 相关概念

- [[倒排索引与分词器]]
- [[搜索相关性与排序]]
- [[Elasticsearch 基础概念]]
- [[Elasticsearch 搜索体系总览]]
