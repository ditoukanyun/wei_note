---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - SpringBoot
  - 可观测性
created: 2026-05-08
---
# SpringBoot Actuator 监控实践

## 定义

SpringBoot Actuator 监控实践是通过 Actuator 端点暴露健康状态、指标和 Prometheus 数据，并把它接入监控告警系统。

## 要点

- 暴露 `health` 给负载均衡和 Kubernetes 探针。
- 暴露 `prometheus` 给 Prometheus 抓取。
- 生产环境需要保护敏感端点。
- 自定义业务指标通过 [[Micrometer]] 注册。

## 相关概念

- [[Spring Boot Actuator]]
- [[Prometheus 与 Grafana 入门]]
- [[SpringBoot/23-SpringBoot-可观测性与业务指标]]
