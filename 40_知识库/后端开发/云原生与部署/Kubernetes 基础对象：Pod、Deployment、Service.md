---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - Kubernetes
  - 云原生
created: 2026-05-08
---
# Kubernetes 基础对象：Pod、Deployment、Service

## 定义

Pod、Deployment、Service 是 Kubernetes 部署应用的基础对象：Pod 承载容器，Deployment 管理副本和滚动更新，Service 提供稳定访问入口。

## 要点

- Pod 是最小调度单元。
- Deployment 声明期望副本数和更新策略。
- Service 通过标签选择后端 Pod。
- Ingress 通常负责 HTTP 外部入口。

## 相关概念

- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]
- [[Kubernetes 部署 SpringBoot 应用]]
