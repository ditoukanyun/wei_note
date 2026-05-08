---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 可观测性
  - 监控
created: 2026-05-08
---
# Prometheus

## 定义

Prometheus 是以时间序列为核心的开源监控系统，通过拉取方式采集指标，并使用 PromQL 进行查询、聚合和告警。

## 要点

- 适合采集服务指标、业务指标和基础设施指标。
- 标签用于区分维度，但高基数标签会显著增加存储成本。
- 常与 Grafana 展示面板、Alertmanager 告警配合使用。

## 相关概念

- [[Micrometer]]
- [[Spring Boot Actuator]]
- [[Prometheus 与 Grafana 入门]]
- [[可观测性总览：日志、指标与链路追踪]]
