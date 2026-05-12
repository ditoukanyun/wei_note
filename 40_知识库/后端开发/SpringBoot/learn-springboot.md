---
type: project-reference
area: "[[后端开发]]"
tags:
  - SpringBoot
  - 项目实践
created: 2026-05-08
updated: 2026-05-11
---
# learn-springboot

learn-springboot 是 SpringBoot 学习与示例项目集合，用于沉淀接口、认证、缓存、消息、网关、可观测性、业务中台能力、Spring 容器扩展点和分布式模式练习。

> 源码目录：`/Users/chenwei/Documents/code/java/learn-springboot`

## 相关概念

- [[SpringBoot/SpringBoot 学习计划]]
- [[SpringBoot]]
- [[SpringBoot MOC]]

## 同步状态

- 源模块数量：97
- 已同步目标笔记：97
- 缺失 README 的模块：0
- 遗留模块：0

## 学习流程

```mermaid
flowchart LR
  A[基础接口] --> B[认证授权]
  B --> C[数据访问和事务]
  C --> D[缓存、消息与搜索]
  D --> E[网关、监控和部署]
  E --> F[业务中台场景]
  F --> G[Spring 容器与启动扩展]
```

## 模块覆盖表

| 编号 | 源模块 | 目标笔记 | 知识点摘要 |
|---|---|---|---|
| 01 | `01-SpringBoot-init` | [[01-SpringBoot-项目初始化]] | 本模块是 Spring Boot 最小启动示例，用来确认项目结构、启动类、Web Controller 和 Maven 测试流程。 |
| 02 | `02-SpringBoot-mysql` | [[02-SpringBoot-MySQL与MyBatis]] | 本模块演示 Spring Boot + MyBatis + MySQL 的基础 CRUD 和多表关联查询。它依赖本地 MySQL，适合作为数据库访问入门模块。 |
| 03 | `03-SpringBoot-redis` | [[03-SpringBoot-Redis集成]] | 本模块演示 Spring Boot + Redis 的基础数据操作和典型场景，包括缓存、限流、分布式锁、点赞和排行榜。 |
| 04 | `04-SpringBoot-lombok` | [[04-SpringBoot-Lombok注解]] | ## Lombok 使用案例演示 |
| 05 | `05-SpringBoot-mysql-redis` | [[05-SpringBoot-MySQL与Redis缓存实战]] | MySQL + Redis 经典使用场景演示，包含缓存穿透、击穿、雪崩防护及数据一致性处理。 |
| 06 | `06-SpringBoot-excel-export` | [[06-SpringBoot-Excel导出]] | 完整模板模块，包含： |
| 07 | `07-SpringBoot-file-upload` | [[07-SpringBoot-文件上传]] | 本模块演示 Spring Boot 中文件上传的常见基础能力，适合作为入门学习案例。 |
| 08 | `08-SpringBoot-aop-log` | [[08-SpringBoot-AOP日志切面]] | 本模块演示 Spring Boot 中 AOP 的常见用法，通过自定义注解统一记录操作日志。 |
| 09 | `09-SpringBoot-jwt-auth` | [[09-SpringBoot-JWT认证]] | 本模块演示基于 MySQL 的登录校验、JWT 生成与解析、拦截器鉴权，以及通过 `ThreadLocal` 获取当前登录用户。 |
| 10 | `10-SpringBoot-schedule-async` | [[10-SpringBoot-定时任务]] | 本模块演示 Spring Boot 中三种常见的定时任务调度方式：`fixedRate`、`fixedDelay`、`cron`。 |
| 11 | `11-SpringBoot-exception-log-trace` | [[11-SpringBoot-异常处理与日志追踪]] | 本模块演示 Spring Boot 中的请求链路日志和统一异常处理，通过 `traceId` 将一次请求的日志与响应关联起来。 |
| 12 | `12-SpringBoot-session-login` | [[12-SpringBoot-Session登录]] | 本模块演示 `Session + Cookie + Interceptor` 的传统登录态校验流程，重点是页面重定向登录流与 API 统一错误响应并存。 |
| 13 | `13-SpringBoot-header-token-login` | [[13-SpringBoot-Header-Token登录]] | 本模块演示 `Header Token + Interceptor` 的登录态校验流程，重点是通过自定义请求头 `X-Auth-Token` 传递令牌并访问受保护 API。 |
| 14 | `14-SpringBoot-redis-token-login` | [[14-SpringBoot-Redis-Token登录]] | 本模块演示 `Redis + Header Token + Interceptor` 的登录态校验流程，重点是将 token 存入 Redis 并设置过期时间。 |
| 15 | `15-SpringBoot-jwt-refresh-blacklist` | [[15-SpringBoot-JWT刷新与黑名单]] | 本模块演示 `JWT + Refresh Token + Redis Blacklist` 的登录态治理流程，重点是 access token 无状态校验、refresh token 轮换，以及登出后 access token 拉黑。 |
| 16 | `16-SpringBoot-jwt-rbac-authz` | [[16-SpringBoot-JWT-RBAC权限控制]] | 本模块演示 `JWT + Refresh Token + RBAC 授权`，在登录态校验基础上新增角色权限控制： |
| 17 | `17-SpringBoot-websocket-chat` | [[17-SpringBoot-WebSocket聊天]] | 本模块演示 Spring Boot WebSocket(STOMP) 聊天场景：实时通信、在线用户统计、服务端消息推送。 |
| 18 | `18-SpringBoot-idempotency` | [[18-SpringBoot-接口幂等性]] | 本模块演示 Spring Boot 接口幂等的常见实现：通过一次性 Token 防止重复提交，支持内存与 Redis 两种存储。 |
| 19 | `19-SpringBoot-rate-limit` | [[19-SpringBoot-接口限流]] | 本模块演示 Spring Boot 中常见的接口限流方案，覆盖单机内存限流与 Redis 限流两种实现。 |
| 20 | `20-SpringBoot-order-create-pay` | [[20-SpringBoot-订单创建与支付]] | 本模块演示订单创建与支付主链路，覆盖订单状态机、超时取消、消息补偿三个核心场景。 |
| 21 | `21-SpringBoot-mq-event-driven` | [[21-SpringBoot-消息队列事件驱动]] | 本模块演示事件驱动架构的核心链路：生产者发布事件、消费者异步处理、失败重试、死信队列与人工重放。 |
| 22 | `22-SpringBoot-api-versioning` | [[22-SpringBoot-API版本管理]] | 本模块演示 API 版本治理的最小闭环：`v1/v2` 并行、兼容路由、灰度演进、旧版本退役提示。 |
| 23 | `23-SpringBoot-observability-metrics` | [[23-SpringBoot-可观测性与业务指标]] | 本模块演示 Spring Boot 指标可观测最小闭环：业务接口驱动指标变化，Actuator 暴露指标，Prometheus 可抓取。 |
| 24 | `24-SpringBoot-cache-patterns` | [[24-SpringBoot-缓存治理模式]] | 本模块演示缓存治理四类核心问题：缓存穿透、缓存击穿、缓存雪崩、热点 key。 |
| 25 | `25-SpringBoot-multi-datasource-tx` | [[25-SpringBoot-多数据源与事务边界]] | 本模块演示多数据源下的事务边界与读写分离：主库写入、从库读取、手动同步，以及跨库失败时的非原子性。 |
| 26 | `26-SpringBoot-openapi-client-sdk` | [[26-SpringBoot-OpenAPI与客户端SDK]] | 本模块演示 OpenAPI 文档自动生成、接口分组（public/admin）以及 SDK 生成命令输出。 |
| 27 | `27-SpringBoot-gateway-routing` | [[27-SpringBoot-Gateway路由]] | 本模块演示 Spring Cloud Gateway 的最小可运行能力： |
| 28 | `28-SpringBoot-openfeign-fallback` | [[28-SpringBoot-OpenFeign与降级]] | 本模块演示 OpenFeign 调用下游服务，以及在下游异常时通过 fallback 返回降级结果。 |
| 29 | `29-SpringBoot-resilience-retry-timeout` | [[29-SpringBoot-弹性治理重试超时熔断限流]] | 本模块演示 Resilience4j 在 Spring Boot 服务调用中的常见韧性策略：重试、超时、熔断和限流。 |
| 30 | `30-SpringBoot-bff-aggregation` | [[30-SpringBoot-BFF聚合接口]] | 本模块演示 BFF/API 聚合层：一个接口聚合商品主数据、库存、促销、评论摘要，并在部分下游失败或超时时返回可用的部分结果。 |
| 31 | `31-SpringBoot-transactional-outbox` | [[31-SpringBoot-事务性发件箱]] | 本模块演示 Transactional Outbox 模式：业务数据和待发布事件同写，发布器异步扫描 outbox 并负责重试、成功确认和死信标记。 |
| 32 | `32-SpringBoot-saga-compensation` | [[32-SpringBoot-Saga补偿事务]] | 本模块演示 Saga 编排式补偿事务：订单创建、库存预留、支付扣款按顺序执行；后续步骤失败时，按相反顺序补偿已完成步骤。 |
| 33 | `33-SpringBoot-cqrs-read-model` | [[33-SpringBoot-CQRS读模型]] | 本模块演示 CQRS 读写分离：命令侧修改订单写模型并产生领域事件，投影器消费事件生成查询友好的订单摘要读模型。 |
| 34 | `34-SpringBoot-event-sourcing-snapshot` | [[34-SpringBoot-事件溯源与快照]] | 本模块演示 Event Sourcing：账户状态不直接覆盖保存，而是通过开户、入账、出账事件流重放得到；保存 snapshot 后可从快照版本继续重放增量事件。 |
| 35 | `35-SpringBoot-feature-flag-gray-release` | [[35-SpringBoot-FeatureFlag与灰度发布]] | 本模块演示 Feature Flag 与灰度发布：通过运行时配置控制功能是否开放，支持白名单用户优先命中和稳定哈希百分比灰度。 |
| 36 | `36-SpringBoot-multi-tenant-context` | [[36-SpringBoot-多租户上下文]] | 本模块演示多租户上下文：从请求头 `X-Tenant-Id` 解析租户，服务层从统一上下文读取租户，仓储层按租户隔离订单数据，并在请求结束清理 ThreadLocal。 |
| 37 | `37-SpringBoot-audit-trail` | [[37-SpringBoot-审计轨迹]] | 本模块演示审计日志：写操作从请求头读取操作人和请求 ID，业务变更时同步记录动作、资源、变更前后状态和操作时间。 |
| 38 | `38-SpringBoot-data-scope-permission` | [[38-SpringBoot-数据范围权限]] | 本模块演示企业后台常见的数据权限范围：同一个订单查询接口，根据当前用户上下文返回本人、本部门或全部数据。 |
| 39 | `39-SpringBoot-sensitive-data-mask` | [[39-SpringBoot-敏感数据脱敏]] | 本模块演示在 Spring Boot 响应序列化阶段做敏感数据脱敏：服务层保留原始客户资料，Controller 返回对象时由 Jackson 根据字段注解统一输出脱敏值。 |
| 40 | `40-SpringBoot-request-signature-replay` | [[40-SpringBoot-请求签名与重放防护]] | 本模块演示机器到机器接口常见的 HMAC 请求签名与防重放机制。客户端按固定规则生成签名，服务端在拦截器中校验 appId、timestamp、nonce 和 signature。 |
| 41 | `41-SpringBoot-validation-error-code` | [[41-SpringBoot-参数校验与错误码]] | 本模块演示企业接口常见的统一参数校验、错误码和业务异常响应。 |
| 42 | `42-SpringBoot-api-response-i18n` | [[42-SpringBoot-API响应国际化]] | 本模块演示 API 响应消息国际化：错误码保持稳定，`message` 和字段校验消息根据 `Accept-Language` 返回中文或英文。 |
| 43 | `43-SpringBoot-dynamic-config-refresh` | [[43-SpringBoot-动态配置刷新]] | 本模块演示一个内存版动态配置中心：通过 API 修改配置，服务发布变更事件，运行时设置监听事件后刷新快照，不需要重启应用。 |
| 44 | `44-SpringBoot-batch-import-export` | [[44-SpringBoot-批量导入导出]] | 本模块演示批量导入和导出元数据原型：提交 JSON 行数据后创建导入任务，后台异步处理并记录进度、成功数量、失败数量和逐行失败明细；导出接口基于已导入客户生成虚拟 CSV 文件元数据。 |
| 45 | `45-SpringBoot-testcontainers-integration-test` | [[45-SpringBoot-Testcontainers集成测试]] | 本模块演示如何用 Testcontainers 补强 MySQL/Redis 集成测试。普通单元测试和接口测试不依赖 Docker；真正启动容器的 smoke tests 使用 `@Testcontainers(disabledWithoutDocker = true)`，本机 Docker 可用时会运行真实容器，不可用时自动跳过。 |
| 46 | `46-SpringBoot-distributed-lock-job` | [[46-SpringBoot-分布式锁与定时任务]] | 本模块演示用分布式锁保护定时任务：多个实例同时尝试执行同一个任务时，只有抢到锁的实例真正执行，其他实例记录为跳过；任务结束后必须用 owner token 校验所有权再释放锁。 |
| 47 | `47-SpringBoot-object-storage-presigned-url` | [[47-SpringBoot-对象存储预签名URL]] | 本模块演示对象存储的预签名上传/下载流程：服务端先生成带过期时间和约束条件的上传链接，客户端再使用 token 上传内容；下载时服务端生成带 HMAC 签名和过期时间的下载链接，读取时校验签名与有效期。 |
| 48 | `48-SpringBoot-search-index-sync` | [[48-SpringBoot-搜索索引同步]] | 本模块演示搜索索引同步和查询流程：把业务文档同步到内存索引，支持关键词检索、分类/状态过滤、排序和高亮式摘要。 |
| 49 | `49-SpringBoot-webhook-delivery` | [[49-SpringBoot-Webhook可靠投递]] | 本模块演示出站 Webhook 投递：订阅事件类型，发布事件后按订阅生成投递记录，使用 HMAC SHA-256 签名，失败后进入重试等待，超过最大次数后进入死信，并支持死信重放。 |
| 50 | `50-SpringBoot-rule-engine-decision-table` | [[50-SpringBoot-规则引擎决策表]] | 本模块演示规则引擎里的决策表原型：创建规则版本，发布某个版本为当前生效版本，按优先级匹配规则，并返回可解释的执行结果。 |
| 51 | `51-SpringBoot-graphql-api` | [[51-SpringBoot-GraphQL API]] | 本模块演示 Spring for GraphQL：显式 schema、resolver、查询聚合、mutation 校验，以及用批量加载统计说明 N+1 问题的规避思路。 |
| 52 | `52-SpringBoot-cdc-incremental-sync` | [[52-SpringBoot-CDC增量同步]] | 本模块演示 CDC 增量同步原型：源端变更写入 change log，消费者按 offset checkpoint 同步到读模型，使用 eventId 做幂等，并支持 rebuild 与 replay 控制。 |
| 53 | `53-SpringBoot-workflow-approval` | [[53-SpringBoot-工作流审批]] | 本模块演示顺序审批流原型：定义审批步骤，提交审批实例，按当前处理人逐级通过或驳回，并保留审计时间线。 |
| 54 | `54-SpringBoot-notification-center` | [[54-SpringBoot-通知中心]] | 本模块演示通知中心原型：通知模板、用户偏好、渠道路由、站内信、模拟邮件/短信投递、失败状态和重试。 |
| 55 | `55-SpringBoot-payment-reconciliation` | [[55-SpringBoot-支付对账]] | 本模块演示支付对账原型：记录内部支付单，导入渠道账单，按渠道和交易日期生成对账批次，并识别匹配、金额不一致、渠道缺失和内部缺失。 |
| 56 | `56-SpringBoot-inventory-reservation` | [[56-SpringBoot-库存预占]] | 本模块演示库存预占原型：维护 SKU 可用库存、预占库存和已售库存，支持下单预占、支付确认扣减、主动释放、超时过期释放，并在预占阶段防止超卖。 |
| 57 | `57-SpringBoot-gateway-auth-policy` | [[57-SpringBoot-网关认证策略]] | 本模块演示网关路由鉴权策略原型：按路由路径匹配策略，并根据 HTTP 方法、用户角色和客户端 IP 生成允许或拒绝决策，同时返回稳定的拒绝原因。 |
| 58 | `58-SpringBoot-tenant-quota-billing` | [[58-SpringBoot-租户配额与计费]] | 本模块演示 SaaS 租户配额与计量计费原型：为租户配置套餐和账期，记录用量，计算预估费用，并根据软限制和硬限制返回 `ALLOW`、`WARN` 或 `BLOCK` 决策。 |
| 59 | `59-SpringBoot-contract-lifecycle` | [[59-SpringBoot-合同生命周期]] | 本模块演示合同生命周期管理原型：创建合同草稿，更新版本化条款，提交签署，记录客户方和公司方签署，双方签署后生效，并支持到期扫描和主动终止。 |
| 60 | `60-SpringBoot-invoice-billing` | [[60-SpringBoot-发票与账单]] | 本模块演示发票申请与状态流转原型：从可开票明细创建发票申请，按类别聚合发票行，计算总金额，并支持开票、付款和作废。 |
| 61 | `61-SpringBoot-coupon-promotion` | [[61-SpringBoot-优惠券与促销]] | 本模块演示优惠券促销的核心链路：创建优惠券模板，向用户发券，按订单金额和有效期试算优惠，并在订单创建时核销优惠券。 |
| 62 | `62-SpringBoot-risk-control` | [[62-SpringBoot-风控规则]] | 本模块演示风控决策的核心链路：配置风险规则，维护黑名单，接收业务事件，按规则输出 `ALLOW`、`REVIEW`、`REJECT` 决策，并返回命中规则和解释原因。 |
| 63 | `63-SpringBoot-points-ledger` | [[63-SpringBoot-积分流水账]] | 本模块演示积分系统的核心账本模型：用户获得积分、兑换积分、积分过期、流水冲正，并通过不可变流水计算账户余额。 |
| 64 | `64-SpringBoot-data-archive-retention` | [[64-SpringBoot-数据归档与保留]] | 本模块演示数据生命周期治理的核心流程：配置保留策略，扫描可归档候选记录，执行归档，恢复已归档记录，并保留操作审计流水。 |
| 65 | `65-SpringBoot-autoconfigure-inspector` | [[65-SpringBoot-自动配置检查器]] | 本模块演示 Spring Boot 自动配置的核心机制：自动配置导入、类型化属性绑定、条件装配、用户 Bean 覆盖，以及 `ApplicationContextRunner` 测试。 |
| 66 | `66-SpringBoot-application-lifecycle-events` | [[66-SpringBoot-应用生命周期事件]] | 本模块演示 Spring Boot 应用启动生命周期中的关键扩展点：`ApplicationRunner`、`ApplicationReadyEvent`、生命周期事件记录、显式排序时间线和事件摘要。 |
| 67 | `67-SpringBoot-actuator-health-readiness` | [[67-SpringBoot-Actuator健康检查与就绪探针]] | 本模块演示 Spring Boot Actuator 健康检查的核心机制：自定义 `HealthIndicator`、liveness/readiness 健康组、依赖健康聚合和诊断 API。 |
| 68 | `68-SpringBoot-configuration-properties-validation` | [[68-SpringBoot-配置属性校验]] | 本模块演示 Spring Boot 类型化配置的常见生产写法：`@ConfigurationProperties`、嵌套属性、Bean Validation、启动期失败诊断和安全配置展示。 |
| 69 | `69-SpringBoot-webmvc-extension-points` | [[69-SpringBoot-WebMVC扩展点]] | 本模块演示 Spring MVC 常见扩展点：`HandlerInterceptor`、`HandlerMethodArgumentResolver`、`ResponseBodyAdvice` 和统一请求上下文增强。 |
| 70 | `70-SpringBoot-custom-starter-pattern` | [[70-SpringBoot-自定义Starter模式]] | 本模块演示 Spring Boot 3 自定义 starter 的核心结构：starter 代码放在应用扫描包之外，通过 `AutoConfiguration.imports` 导入自动配置，再用条件注解和用户 Bean 覆盖点完成可插拔装配。 |
| 71 | `71-SpringBoot-environment-postprocessor` | [[71-SpringBoot-EnvironmentPostProcessor]] | 本模块演示 Spring Boot 启动早期扩展点 `EnvironmentPostProcessor`：在 Bean 创建和 `@ConfigurationProperties` 绑定之前，向 `Environment` 插入一个自定义 `PropertySource`。 |
| 72 | `72-SpringBoot-failure-analyzer` | [[72-SpringBoot-FailureAnalyzer]] | 本模块演示 Spring Boot 启动失败诊断机制：业务代码抛出一个有语义的启动异常，`FailureAnalyzer` 把异常转换成可读的失败说明和修复动作。 |
| 73 | `73-SpringBoot-application-context-initializer` | [[73-SpringBoot-ApplicationContextInitializer]] | 本模块演示 Spring Boot 启动流程中的 `ApplicationContextInitializer`：应用上下文已经创建，但还没有 refresh，此时可以读取环境信息并注册早期单例。 |
| 74 | `74-SpringBoot-bean-factory-post-processor` | [[74-SpringBoot-BeanFactoryPostProcessor]] | 本模块演示 Spring 容器 refresh 过程中的 `BeanFactoryPostProcessor`：在 Bean 实例化之前修改 `BeanDefinition`，让最终创建出来的 Bean 使用新的属性值。 |
| 75 | `75-SpringBoot-bean-definition-registry-post-processor` | [[75-SpringBoot-BeanDefinitionRegistryPostProcessor]] | 本模块演示 `BeanDefinitionRegistryPostProcessor`：在 BeanFactory 后处理之前，直接向 `BeanDefinitionRegistry` 注册新的 BeanDefinition。 |
| 76 | `76-SpringBoot-bean-post-processor` | [[76-SpringBoot-BeanPostProcessor]] | 本模块演示 `BeanPostProcessor`：Bean 已经创建之后，在初始化前后对对象本身做加工。 |
| 77 | `77-SpringBoot-smart-initializing-singleton` | [[77-SpringBoot-SmartInitializingSingleton]] | 本模块演示 `SmartInitializingSingleton`：所有普通单例 Bean 实例化完成后，再执行一次统一的生命周期回调。 |
| 78 | `78-SpringBoot-runner-ordering` | [[78-SpringBoot-Runner执行顺序]] | 本模块演示 Spring Boot 启动末段的两个 runner：`ApplicationRunner` 和 `CommandLineRunner`。 |
| 79 | `79-SpringBoot-smart-lifecycle` | [[79-SpringBoot-SmartLifecycle]] | 本模块演示 `SmartLifecycle`：Spring 容器启动和停止阶段的自动生命周期管理、phase 排序、运行状态和 `stop(Runnable)` 回调。 |
| 80 | `80-SpringBoot-exit-code` | [[80-SpringBoot-ExitCode]] | 本模块演示 Spring Boot 的退出码机制：`ExitCodeGenerator`、`ExitCodeExceptionMapper` 和 `SpringApplication.exit(...)`。 |
| 81 | `81-SpringBoot-conversion-service` | [[81-SpringBoot-ConversionService]] | 本模块演示 Spring Boot 的 `ApplicationConversionService` 和 Spring `Converter`：把外部字符串集中转换为业务类型。 |
| 82 | `82-SpringBoot-validation-groups` | [[82-SpringBoot-Validation分组]] | 本模块演示 Bean Validation 分组校验：同一个请求 DTO 在 create 和 update 场景下使用不同规则。 |
| 83 | `83-SpringBoot-binder-api` | [[83-SpringBoot-Binder API]] | 本模块演示 Spring Boot 底层 `Binder` API：不使用 `@ConfigurationProperties`，直接从 `Environment` 手动绑定一组配置到 JavaBean。 |
| 84 | `84-SpringBoot-application-startup` | [[84-SpringBoot-ApplicationStartup]] | 本模块演示 Spring 的 `ApplicationStartup`、`StartupStep`，以及 Spring Boot 的 `BufferingApplicationStartup`：用可控的启动步骤记录理解 Boot 启动诊断机制。 |
| 85 | `85-SpringBoot-condition-evaluation-report` | [[85-SpringBoot-ConditionEvaluationReport]] | 本模块演示 Spring Boot 的 `ConditionEvaluationReport`：查看条件装配为什么匹配或不匹配，并把诊断结果过滤成稳定 API。 |
| 86 | `86-SpringBoot-run-listener` | [[86-SpringBoot-SpringApplicationRunListener]] | 本模块演示 Spring Boot 的 `SpringApplicationRunListener`：在应用上下文创建 Bean 之前监听 `SpringApplication.run(...)` 的早期启动阶段。 |
| 87 | `87-SpringBoot-bootstrap-registry` | [[87-SpringBoot-BootstrapRegistry]] | 本模块演示 Spring Boot 的 `BootstrapRegistryInitializer` 和 `BootstrapRegistry`：在普通 Spring Bean 创建之前注册早期对象，并监听 bootstrap context close。 |
| 88 | `88-SpringBoot-deferred-import-selector` | [[88-SpringBoot-DeferredImportSelector]] | 本模块演示 Spring 的 `DeferredImportSelector`：通过启用注解导入 selector，再由 selector 延迟返回配置类名称，最终注册业务 Bean。这个路径是理解 Spring Boot `AutoConfigurationImportSelector` 的一个最小可验证版本。 |
| 89 | `89-SpringBoot-import-bean-definition-registrar` | [[89-SpringBoot-ImportBeanDefinitionRegistrar]] | 本模块演示 Spring 的 `ImportBeanDefinitionRegistrar`：通过启用注解导入 registrar，再由 registrar 直接向 `BeanDefinitionRegistry` 写入 BeanDefinition。它和 `88-SpringBoot-deferred-import-selector` 形成对照：selector 返回配置类名称，registrar 直接注册 BeanDefinition。 |
| 90 | `90-SpringBoot-factory-bean` | [[90-SpringBoot-FactoryBean]] | 本模块演示 Spring 的 `FactoryBean`：容器里注册的是工厂 Bean，但普通 bean name 返回的是工厂生产的产品对象；使用 `&beanName` 才能取到工厂本身。 |
| 91 | `91-SpringBoot-object-provider` | [[91-SpringBoot-ObjectProvider]] | 本模块演示 Spring 的 `ObjectProvider`：在不强制依赖 Bean 必须存在的情况下，延迟读取候选 Bean、按顺序选择策略，并为缺失依赖提供 fallback。 |
| 92 | `92-SpringBoot-spring-factories-loader` | [[92-SpringBoot-SpringFactoriesLoader]] | 本模块演示 `SpringFactoriesLoader` 如何读取 `META-INF/spring.factories`：先发现实现类名，再按 SPI 类型实例化扩展对象。前面的环境后处理器、失败分析器、run listener 等模块都用过 `spring.factories`，本模块专门拆开 loader 本身。 |
| 93 | `93-SpringBoot-resolvable-type` | [[93-SpringBoot-ResolvableType]] | 本模块演示 Spring 的 `ResolvableType`：从 `EventHandler<T>` 的具体实现类反推出泛型参数类型。这个模式在 Spring 源码里很常见，例如 converter、listener、serializer、handler registry 等框架组件都需要从用户实现类推断支持的领域类型。 |
| 94 | `94-SpringBoot-application-availability` | [[94-SpringBoot-ApplicationAvailability]] | 本模块演示 Spring Boot 的 `ApplicationAvailability`：通过 `AvailabilityChangeEvent` 发布运行时可用性变化，再由 `ApplicationAvailabilityBean` 记录最新的 liveness/readiness 状态。它和前面的 Actuator 健康探针模块不同，本模块聚焦 Boot 内部的 availability 状态模型和事件更新链路。 |
| 95 | `95-SpringBoot-custom-condition` | [[95-SpringBoot-自定义Condition]] | 本模块演示 Spring 的自定义 `@Conditional`：通过组合注解把条件参数交给 `Condition`，再由 `ConditionContext` 读取环境配置，决定某个 BeanDefinition 是否应该注册。这是理解 Spring Boot 条件装配源码的基础路径。 |
| 96 | `96-SpringBoot-event-multicaster` | [[96-SpringBoot-ApplicationEventMulticaster]] | 本模块演示 Spring 的应用事件广播链路：`ApplicationEventPublisher` 发布事件后，应用上下文把事件交给名为 `applicationEventMulticaster` 的 `ApplicationEventMulticaster`，再由 `SimpleApplicationEventMulticaster` 解析并调用匹配的 listener。 |
| 97 | `97-SpringBoot-resource-loader` | [[97-SpringBoot-ResourceLoader]] | 本模块演示 Spring 的资源抽象：用 `ResourceLoader` 读取单个 `classpath:` 资源，用 `PathMatchingResourcePatternResolver` 扫描 `classpath*:` pattern，并把资源转换成稳定的描述信息。 |

## 实践检查清单

- 每个示例是否有 README、接口说明和启动方式。
- 是否覆盖成功、失败和边界请求。
- 是否把示例和真实工程最佳实践区分开。
- 是否记录关键设计取舍，例如为什么用 Redis、消息队列、网关策略或 Spring 扩展点。
- 学完一个模块后是否沉淀为原子知识笔记，并从 [[SpringBoot MOC]] 能找到入口。

## 学习边界

示例项目的价值在于隔离概念，而不是模拟完整生产系统。学习时可以先让每个模块保持小而清楚：一个模块验证一种机制，例如拦截器、事务、缓存、消息、链路追踪、业务状态机或 Spring 容器扩展。等理解机制后，再把多个模块组合成更接近真实项目的端到端示例。

每个示例都应补“生产差距”说明：缺少哪些安全、性能、监控、测试、容量和部署要素。这样复习时不会把教学代码误当最佳实践。

## 常见误区

- 只把示例跑通，不总结适用场景和限制。
- 示例代码逐渐堆成大杂烩，没有模块边界。
- 忽略测试和异常路径，只演示 happy path。
- 把 Spring 扩展点当作业务代码常规入口，导致启动流程难以排查。

## 复盘问题

- 这个示例对应的生产差距是什么。
- 学完后是否沉淀到 SpringBoot 知识点或项目实践中。
- 它和认证、网关、缓存、消息、可观测性或 Spring 容器扩展中的哪个主题相连。
