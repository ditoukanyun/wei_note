---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 可观测性
  - 指标
created: 2026-05-08
---
# Micrometer

## 定义

Micrometer 是 JVM 应用的指标门面，提供统一 API 记录 Counter、Gauge、Timer 等指标，并适配 Prometheus、Datadog、Graphite 等后端。

## 要点

- Counter 表示只增不减的事件计数。
- Gauge 表示当前状态值。
- Timer 表示耗时分布和调用次数。
- 标签维度要控制基数，避免指标系统膨胀。

## 相关概念

- [[SpringBoot/23-SpringBoot-可观测性与业务指标]]
- [[Spring Boot Actuator]]
- [[Prometheus]]
- [[可观测性总览：日志、指标与链路追踪]]
