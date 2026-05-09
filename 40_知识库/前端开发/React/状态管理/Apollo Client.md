---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - React
  - GraphQL
created: 2026-05-08
---
# Apollo Client

## 定义

Apollo Client 是 GraphQL 客户端状态管理和数据获取库，负责发送查询、缓存规范化数据、管理加载/错误状态，并支持本地状态和乐观更新。

## 要点

- 适合 GraphQL API 和复杂对象图数据。
- 规范化缓存可以按实体 ID 合并和更新结果。
- Schema、Query 和缓存策略需要协同设计。

## 相关概念

- [[React Query]]
- [[前后端接口契约]]
- [[OpenAPI 与类型生成]]

## 工作流程

```mermaid
flowchart LR
  A[组件声明 Query] --> B[Apollo 发送请求]
  B --> C[GraphQL 服务返回数据]
  C --> D[规范化写入缓存]
  D --> E[订阅组件自动更新]
```

## 适用场景

- API 以 GraphQL 为主，并且前端需要灵活组合字段。
- 页面存在共享实体，例如用户、组织、订单在多处展示。
- 需要乐观更新、分页缓存、局部缓存更新和错误状态管理。

如果后端是 REST API，且数据关系简单，React Query 往往更轻量。

## 实践检查清单

- Schema 是否有稳定 ID，便于规范化缓存识别实体。
- Query 是否只请求页面需要的字段，避免过度获取。
- Mutation 后是否明确更新缓存、失效查询或使用乐观更新。
- 错误处理是否区分网络错误、GraphQL 错误和权限错误。
- 分页策略是否明确 cursor、offset 或 relay-style connection。

## 常见误区

- 以为 Apollo 缓存会自动理解所有业务关系。
- Mutation 成功后不更新缓存，页面仍显示旧数据。
- 把本地 UI 状态过度放进 Apollo，增加调试复杂度。
