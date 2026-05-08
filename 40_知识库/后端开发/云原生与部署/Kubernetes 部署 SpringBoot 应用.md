---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Kubernetes
  - SpringBoot
created: 2026-05-08
---
# Kubernetes 部署 SpringBoot 应用

## 定义

Kubernetes 部署 SpringBoot 应用是把 SpringBoot 服务打包为容器镜像，再通过 Deployment、Service、ConfigMap、Secret 和探针运行在集群中。

## 要点

- 镜像应包含明确版本标签。
- 健康检查可接入 Spring Boot Actuator。
- 配置和密钥应与镜像分离。
- 滚动发布前要有回滚策略和监控指标。

## 相关概念

- [[SpringBoot]]
- [[Spring Boot Actuator]]
- [[Kubernetes 基础对象：Pod、Deployment、Service]]
