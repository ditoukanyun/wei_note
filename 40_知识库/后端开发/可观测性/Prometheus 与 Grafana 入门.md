---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Prometheus
  - Grafana
created: 2026-05-08
---
# Prometheus 与 Grafana 入门

## 定义

Prometheus 负责采集和查询指标，Grafana 负责可视化仪表盘和告警展示，二者常组成服务监控基础栈。

## 要点

- Prometheus 通过 scrape 拉取指标。
- Grafana 使用数据源查询指标并展示面板。
- 面板应围绕延迟、错误率、吞吐、饱和度和业务指标设计。

## 相关概念

- [[Prometheus]]
- [[Micrometer]]
- [[可观测性总览：日志、指标与链路追踪]]
