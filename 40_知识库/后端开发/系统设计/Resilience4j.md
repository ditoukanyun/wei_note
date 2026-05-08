---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 稳定性
  - Java
created: 2026-05-08
---
# Resilience4j

## 定义

Resilience4j 是 Java 生态的轻量级容错库，提供熔断、限流、重试、隔离、超时和降级装饰器，用于提升服务间调用的稳定性。

## 能力

- CircuitBreaker：熔断异常或慢调用过多的依赖。
- Retry：对临时失败执行受控重试。
- RateLimiter：限制调用速率。
- TimeLimiter：控制异步调用最长等待时间。
- Bulkhead：限制并发，隔离资源。

## 相关概念

- [[熔断器]]
- [[重试]]
- [[限流]]
- [[超时控制]]
