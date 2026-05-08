---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - OpenTelemetry
  - 链路追踪
created: 2026-05-08
---
# OpenTelemetry 链路追踪

## 定义

OpenTelemetry 是开放可观测性标准，提供 Trace、Metric、Log 的采集规范和 SDK，其中链路追踪用于还原一次请求跨服务调用路径。

## 要点

- Trace 表示完整调用链。
- Span 表示链路中的一次操作。
- TraceId 用于关联跨服务日志和调用。
- 采样策略影响成本和排障精度。

## 相关概念

- [[日志、指标、链路追踪三件套]]
- [[可观测性总览：日志、指标与链路追踪]]
