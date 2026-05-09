---
type: wiki
area: "[[后端开发]]"
tags:
  - Redis
  - 数据结构
created: 2026-05-08
---
# Redis数据类型

Redis 常用数据类型包括 String、Hash、List、Set、Sorted Set、Bitmap、HyperLogLog、Stream 和 Geo。

## 相关概念

- [[Redis]]
- [[缓存系统总览]]

## 选择流程

```mermaid
flowchart TD
  A[明确访问模式] --> B{数据形态}
  B -->|简单值| C[String]
  B -->|对象字段| D[Hash]
  B -->|队列| E[List 或 Stream]
  B -->|去重集合| F[Set]
  B -->|排行榜| G[Sorted Set]
```

## 实践检查清单

- Key 命名是否包含业务、环境和对象 ID。
- 是否为缓存 Key 设置合理 TTL。
- 大对象是否拆分，避免单 Key 过大。
- 集合类数据是否评估成员数量和内存占用。
- 是否区分缓存、计数、队列和事件流的使用边界。

## 案例

用户资料缓存适合 Hash，短信验证码适合带过期时间的 String，排行榜适合 Sorted Set，订单事件流更适合 Stream。

## 常见误区

- 所有数据都用 String 存 JSON，导致局部更新和统计困难。
- Key 没有 TTL，长期积累形成内存压力。
- 用 Redis 队列承载关键消息却没有确认和重试机制。
