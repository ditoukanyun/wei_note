---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 云原生
  - 部署
  - DevOps
created: 2026-04-30
---
# 云原生部署总览：Docker、Kubernetes 与 CI-CD

## 学习目标

- 理解从本地开发、镜像构建、持续集成到 Kubernetes 部署的完整链路。
- 掌握 Docker、Docker Compose、Kubernetes、CI/CD 在部署体系中的职责。
- 能为前后端项目设计基础自动化部署流程。

## 核心概念

- **Docker Image**：应用和运行时依赖的不可变交付物。
- **Docker Compose**：本地编排多个服务，适合开发和集成测试环境。
- **Kubernetes Deployment**：声明应用副本、滚动更新和回滚策略。
- **Service / Ingress**：提供集群内访问和外部入口。
- **CI/CD**：自动执行检查、构建、测试、镜像推送和部署。

## 推荐阅读顺序

1. [[Docker]]：理解容器和镜像。
2. [[前后端项目部署方案详解]]
3. [[Nginx 多前端项目部署]]
4. 本文：建立云原生部署总览。
5. 后续拆分文章：Compose、Kubernetes、CI/CD、HTTPS、回滚。

## 工程实践清单

- 本地环境优先用 Docker Compose 固化数据库、缓存、消息队列等依赖。
- 应用部署前先统一配置来源、健康检查、日志输出和镜像版本规则。
- CI 流水线至少包含安装依赖、静态检查、测试和构建。
- 部署流水线必须保留回滚路径，避免只能向前修复。

## 后续可拆分文章

- [[Docker Compose 搭建本地开发环境]]
- [[Kubernetes 基础对象：Pod、Deployment、Service]]
- [[Kubernetes 部署 SpringBoot 应用]]
- [[Nginx 反向代理与 HTTPS 配置]]
- [[CI-CD 自动化部署流程]]

## 相关链接

- [[后端开发 MOC]]
- [[Vite 原理与插件机制总览]]
- [[可观测性总览：日志、指标与链路追踪]]
