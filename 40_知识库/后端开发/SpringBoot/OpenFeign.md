---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - SpringCloud
  - 服务调用
created: 2026-05-08
---
# OpenFeign

## 定义

OpenFeign 是声明式 HTTP 客户端，允许开发者用接口和注解描述远程调用，由框架生成请求实现。它常用于 Spring Cloud 服务间调用。

## 要点

- 接口方法映射远程 HTTP API。
- 需要配置超时、日志、错误解码和重试策略。
- 与 [[Resilience4j]] 配合可实现熔断、限流和降级。
- 远程调用边界必须关注 [[超时控制]] 和 [[幂等性]]。

## 相关概念

- [[SpringBoot/28-SpringBoot-OpenFeign与降级]]
- [[RESTful API 设计]]
- [[Resilience4j]]
