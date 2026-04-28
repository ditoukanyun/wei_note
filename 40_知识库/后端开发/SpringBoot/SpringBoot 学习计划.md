---
title: SpringBoot 学习计划
date: 2026-04-20
tags:
  - springboot
  - java
  - 学习计划
status: completed
---
# SpringBoot 学习计划

> 将 [[learn-springboot]] 项目中各模块代码整理为阅读笔记，源码路径：`/Users/chenwei/Documents/code/java/learn-springboot`

## 基础集成

- [x] 01-SpringBoot-init — 项目初始化与基本配置 ✅ [[SpringBoot/01-SpringBoot-项目初始化|笔记]]
- [x] 02-SpringBoot-mysql — MySQL 数据库集成 ✅ [[SpringBoot/02-SpringBoot-MySQL与MyBatis|笔记]]
- [x] 03-SpringBoot-redis — Redis 缓存集成 ✅ [[SpringBoot/03-SpringBoot-Redis集成|笔记]]
- [x] 04-SpringBoot-lombok — Lombok 注解使用 ✅ [[SpringBoot/04-SpringBoot-Lombok注解|笔记]]
- [x] 05-SpringBoot-mysql-redis — MySQL + Redis 联合使用 ✅ [[SpringBoot/05-SpringBoot-MySQL与Redis缓存实战|笔记]]

## 功能实战

- [x] 06-SpringBoot-excel-export — Excel 导出 ✅ [[SpringBoot/06-SpringBoot-Excel导出|笔记]]
- [x] 07-SpringBoot-file-upload — 文件上传 ✅ [[SpringBoot/07-SpringBoot-文件上传|笔记]]
- [x] 08-SpringBoot-aop-log — AOP 日志切面 ✅ [[SpringBoot/08-SpringBoot-AOP日志切面|笔记]]
- [x] 09-SpringBoot-jwt-auth — JWT 认证 ✅ [[SpringBoot/09-SpringBoot-JWT认证|笔记]]
- [x] 10-SpringBoot-schedule-async — 定时任务与异步 ✅ [[SpringBoot/10-SpringBoot-定时任务|笔记]]
- [x] 11-SpringBoot-exception-log-trace — 异常处理与日志追踪 ✅ [[SpringBoot/11-SpringBoot-异常处理与日志追踪|笔记]]

## 认证授权

- [x] 12-SpringBoot-session-login — Session 登录 ✅ [[SpringBoot/12-SpringBoot-Session登录|笔记]]
- [x] 13-SpringBoot-header-token-login — Header Token 登录 ✅ [[SpringBoot/13-SpringBoot-Header-Token登录|笔记]]
- [x] 14-SpringBoot-redis-token-login — Redis Token 登录 ✅ [[SpringBoot/14-SpringBoot-Redis-Token登录|笔记]]
- [x] 15-SpringBoot-jwt-refresh-blacklist — JWT 刷新与黑名单 ✅ [[SpringBoot/15-SpringBoot-JWT刷新与黑名单|笔记]]
- [x] 16-SpringBoot-jwt-rbac-authz — JWT RBAC 权限控制 ✅ [[SpringBoot/16-SpringBoot-JWT-RBAC权限控制|笔记]]

## 高级应用

- [x] 17-SpringBoot-websocket-chat — WebSocket 聊天 ✅ [[SpringBoot/17-SpringBoot-WebSocket聊天|笔记]]
- [x] 18-SpringBoot-idempotency — 接口幂等性 ✅ [[SpringBoot/18-SpringBoot-接口幂等性|笔记]]
- [x] 19-SpringBoot-rate-limit — 接口限流 ✅ [[SpringBoot/19-SpringBoot-接口限流|笔记]]
- [x] 20-SpringBoot-order-create-pay — 订单创建与支付 ✅ [[SpringBoot/20-SpringBoot-订单创建与支付|笔记]]
- [x] 21-SpringBoot-mq-event-driven — 消息队列事件驱动 ✅ [[SpringBoot/21-SpringBoot-消息队列事件驱动|笔记]]
- [x] 22-SpringBoot-api-versioning — API 版本管理 ✅ [[SpringBoot/22-SpringBoot-API版本管理|笔记]]

## 工程治理

- [x] 23-SpringBoot-observability-metrics — 可观测性与业务指标 ✅ [[SpringBoot/23-SpringBoot-可观测性与业务指标|笔记]]
- [x] 24-SpringBoot-cache-patterns — 缓存治理模式 ✅ [[SpringBoot/24-SpringBoot-缓存治理模式|笔记]]
- [x] 25-SpringBoot-multi-datasource-tx — 多数据源与事务边界 ✅ [[SpringBoot/25-SpringBoot-多数据源与事务边界|笔记]]
- [x] 26-SpringBoot-openapi-client-sdk — OpenAPI 与客户端 SDK ✅ [[SpringBoot/26-SpringBoot-OpenAPI与客户端SDK|笔记]]
- [x] 27-SpringBoot-gateway-routing — 网关路由 ✅ [[SpringBoot/27-SpringBoot-Gateway路由|笔记]]
- [x] 28-SpringBoot-openfeign-fallback — OpenFeign 与降级 ✅ [[SpringBoot/28-SpringBoot-OpenFeign与降级|笔记]]
- [x] 29-SpringBoot-resilience-retry-timeout — 弹性治理：重试与超时 ✅ [[SpringBoot/29-SpringBoot-弹性治理重试超时熔断限流|笔记]]
- [x] 30-SpringBoot-bff-aggregation — BFF 聚合接口 ✅ [[SpringBoot/30-SpringBoot-BFF聚合接口|笔记]]
- [x] 31-SpringBoot-transactional-outbox — 事务性发件箱 ✅ [[SpringBoot/31-SpringBoot-事务性发件箱|笔记]]
- [x] 32-SpringBoot-saga-compensation — Saga 补偿事务 ✅ [[SpringBoot/32-SpringBoot-Saga补偿事务|笔记]]
- [x] 33-SpringBoot-cqrs-read-model — CQRS 读模型 ✅ [[SpringBoot/33-SpringBoot-CQRS读模型|笔记]]
- [x] 34-SpringBoot-event-sourcing-snapshot — 事件溯源与快照 ✅ [[SpringBoot/34-SpringBoot-事件溯源与快照|笔记]]
- [x] 35-SpringBoot-feature-flag-gray-release — Feature Flag 与灰度发布 ✅ [[SpringBoot/35-SpringBoot-FeatureFlag与灰度发布|笔记]]

## 核心概念索引

### 分布式一致性与事件驱动

- [[Saga]] — 跨服务长事务的补偿事务模式
- [[Transactional Outbox]] — 业务数据与待发布事件同事务写入
- [[最终一致性]] — 异步系统在一段时间后收敛到一致状态
- [[领域事件]] — 表示业务中已经发生的事实
- [[CQRS]] — 命令模型与查询模型分离
- [[Event Sourcing]] — 通过事件流重建当前状态
- [[Snapshot]] — 事件溯源中的状态快照优化

### 流量治理与发布策略

- [[熔断器]] — 下游异常时快速失败并触发降级
- [[BFF]] — 面向前端页面的 API 聚合层
- [[Feature Flag]] — 用运行时配置控制功能开放
- [[灰度发布]] — 小流量逐步放量的新版本发布方式
- [[稳定哈希]] — 保证同一用户灰度命中结果稳定

## 进度

| 阶段 | 总数 | 已完成 | 进度 |
|------|------|--------|------|
| 基础集成 | 5 | 5 | 100% |
| 功能实战 | 6 | 6 | 100% |
| 认证授权 | 5 | 5 | 100% |
| 高级应用 | 6 | 6 | 100% |
| 工程治理 | 13 | 13 | 100% |
| **合计** | **35** | **35** | **100%** |
