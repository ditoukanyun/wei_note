---
area: [[后端开发]]
tags:
  - moc
  - 后端开发
created: 2026-04-30
---
# ⚙️ 后端开发 MOC

> 后端开发技术栈的知识地图。当前主线是“语言与框架 → API 与数据 → 系统设计 → 交付与治理”。

## 语言与框架

- [[Node.js 后端开发总览]]
- [[Java核心/Java核心 MOC|Java 核心 MOC]]
- [[Java核心/Java 集合框架]]
- [[Java核心/Java 泛型]]
- [[Java核心/Java IO与NIO]]
- [[Java核心/Java 反射]]
- [[Java核心/Java Stream API]]
- [[SpringBoot/SpringBoot 学习计划|SpringBoot 学习计划]]
- [[Python编程/MOC-Python编程|Python 编程 MOC]]

## API 设计与前后端协作

- [[RESTful API 设计]]
- [[API 版本管理]]
- [[前后端接口契约]]
- [[OpenAPI 与类型生成]]
- [[BFF]]
- [[认证授权总览：Session、JWT、OAuth2 与 OIDC]]
- [[API 安全基础]]

## 数据与搜索

- [[MySQL/MySQL_高级操作总览|MySQL 高级操作总览]]
- [[MySQL/MySQL_索引优化|MySQL 索引优化]]
- [[MySQL/MySQL_事务与锁|MySQL 事务与锁]]
- [[MySQL/MySQL_分库分表与读写分离|分库分表与读写分离]]
- [[PostgreSQL 核心能力总览]]
- [[Elasticsearch 搜索体系总览]]
- [[倒排索引与分词器]]
- [[Elasticsearch 查询 DSL]]
- [[搜索相关性与排序]]
- [[Elasticsearch 与数据库同步方案]]
- [[缓存系统总览]]
- [[缓存穿透]]
- [[缓存击穿]]
- [[缓存雪崩]]
- [[热点 Key]]
- [[Redis]]

## 系统设计

- [[领域驱动设计]]
- [[消息队列总览：RabbitMQ、Kafka 与可靠消息]]
- [[最终一致性]]
- [[领域事件]]
- [[Transactional Outbox]]
- [[Saga]]
- [[CQRS]]
- [[Event Sourcing]]
- [[Snapshot]]

## 流量治理与发布策略

- [[熔断器]]
- [[超时控制]]
- [[重试]]
- [[降级]]
- [[稳定哈希]]
- [[Feature Flag]]
- [[灰度发布]]
- [[幂等性]]
- [[限流]]

## 云原生、DevOps 与可观测性

- [[云原生部署总览：Docker、Kubernetes 与 CI-CD]]
- [[CI-CD 流水线]]
- [[前后端项目部署方案详解]]
- [[Nginx 多前端项目部署]]
- [[可观测性总览：日志、指标与链路追踪]]

## 与前端开发的连接

- [[TypeScript 工程实践总览]]
- [[前端测试体系总览]]
- [[Web Vitals 与前端性能监控总览]]
- [[前端安全总览：XSS、CSRF 与 CSP]]
- [[组件设计与状态边界]]

## 学习路径

1. **基础阶段**：一门后端语言 + HTTP/API + 数据库基础。
2. **应用阶段**：认证授权 + 缓存 + 搜索 + 文件/任务/消息等业务能力。
3. **系统阶段**：一致性、事件驱动、DDD、流量治理和发布策略。
4. **交付阶段**：容器化、CI/CD、可观测性、回滚和生产问题定位。

## 🔗 相关资源

- [[50_资源/项目收藏/GitHub项目|GitHub 项目]]
- [[50_资源/项目收藏/本地项目/README|本地项目]]
- [[50_资源/Docker命令集|Docker 命令集]]

---

## 📊 统计

```dataview
table file.mtime as "更新时间", status as "状态"
from "40_知识库/后端开发"
sort file.mtime desc
```
