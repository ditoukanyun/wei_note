---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - SpringCloud
  - 网关
created: 2026-05-08
---
# Spring Cloud Gateway

## 定义

Spring Cloud Gateway 是 Spring Cloud 生态中的 API 网关，用于路由转发、过滤、认证、限流、灰度路由和统一横切处理。

## 要点

- Predicate 决定请求是否命中路由。
- Filter 在转发前后修改请求或响应。
- 可接入 TraceId、鉴权、限流、熔断和灰度发布。
- 网关应保持轻量，避免承载过多业务编排。

## 相关概念

- [[SpringBoot/27-SpringBoot-Gateway路由]]
- [[限流]]
- [[灰度发布]]
- [[BFF]]
