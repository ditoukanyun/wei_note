---
title: SpringBoot 可观测性与业务指标
date: 2026-04-28
tags:
  - springboot
  - java
  - 可观测性
  - micrometer
  - prometheus
module: 23-SpringBoot-observability-metrics
---
# SpringBoot 可观测性与业务指标

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/23-SpringBoot-observability-metrics`

## 核心思路

本模块演示 [[SpringBoot]] 应用中的指标可观测最小闭环：业务接口改变运行状态，[[Micrometer]] 注册业务指标，[[Spring Boot Actuator]] 暴露指标端点，[[Prometheus]] 通过 `/actuator/prometheus` 抓取指标。

## 项目结构

```text
src/main/java/com/cloud/
├── controller/ObservabilityDemoController.java  (业务演示接口)
├── service/
│   ├── BusinessMetricsService.java              (指标注册与记录)
│   └── InMemoryWorkQueueService.java            (内存待处理队列)
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 依赖与配置

| 配置 | 说明 |
|------|------|
| `management.endpoints.web.exposure.include` | 暴露 `health`、`info`、`metrics`、`prometheus` |
| `management.endpoint.prometheus.enabled` | 启用 Prometheus 端点 |
| `management.prometheus.metrics.export.enabled` | 开启 Prometheus 指标导出 |
| `management.metrics.tags.application` | 给所有指标追加应用维度标签 |

```yaml
server:
  port: 8103

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    prometheus:
      enabled: true
  prometheus:
    metrics:
      export:
        enabled: true
```

## 指标模型

| 指标 | 类型 | 含义 |
|------|------|------|
| `demo_order_created_total` | `Counter` | 创建订单总数，只增不减 |
| `demo_order_processed_total{result="success"}` | `Counter` | 处理成功订单总数 |
| `demo_order_processed_total{result="failed"}` | `Counter` | 处理失败订单总数 |
| `demo_order_process_duration_ms` | `Timer` | 订单处理耗时分布 |
| `demo_order_pending_count` | `Gauge` | 当前待处理订单数量 |

## 核心代码解析

### BusinessMetricsService — 注册和记录指标

```java
this.orderCreatedCounter = Counter.builder("demo_order_created_total")
        .description("Total count of created demo orders")
        .register(meterRegistry);

this.processedSuccessCounter = Counter.builder("demo_order_processed_total")
        .tag("result", "success")
        .register(meterRegistry);

this.processDurationTimer = Timer.builder("demo_order_process_duration_ms")
        .register(meterRegistry);

Gauge.builder("demo_order_pending_count", workQueueService, InMemoryWorkQueueService::pendingCount)
        .register(meterRegistry);
```

> [!important] 指标类型选择
> 事件累计值用 `Counter`，耗时分布用 `Timer`，当前状态值用 `Gauge`。不要用一个指标类型表达所有业务含义。

### 指标记录流程

```java
public MetricsSnapshot createOrders(int count) {
    workQueueService.addOrders(count);
    orderCreatedCounter.increment(count);
    return snapshot();
}

public MetricsSnapshot processOne(boolean success, long durationMs) {
    boolean taken = workQueueService.takeOne();
    if (!taken) throw new IllegalStateException("暂无待处理订单");

    processDurationTimer.record(Duration.ofMillis(durationMs));
    if (success) {
        processedSuccessCounter.increment();
    } else {
        processedFailedCounter.increment();
    }
    return snapshot();
}
```

业务状态变化与指标记录放在同一个服务方法里，保证指标能反映真实业务动作。

## 指标基数控制

本模块只给处理结果增加 `result=success|failed` 标签，避免把 `orderId`、`userId` 这类高基数字段放进指标标签。

| 标签设计 | 是否推荐 | 原因 |
|----------|----------|------|
| `result=success|failed` | 推荐 | 取值有限，便于聚合 |
| `userId=1001` | 不推荐 | 用户数越多时间序列越多 |
| `orderId=xxx` | 不推荐 | 每个订单生成新时间序列 |

> [!warning] 高基数标签
> Prometheus 的存储成本与时间序列数量强相关，高基数标签会让指标系统快速膨胀。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/observability` | 模块信息与当前快照 |
| POST | `/api/observability/orders/create?count=1` | 创建待处理订单 |
| POST | `/api/observability/orders/process?success=true&durationMs=120` | 处理一个订单 |
| GET | `/api/observability/metrics/snapshot` | 查看业务指标快照 |
| GET | `/actuator/metrics` | Actuator 指标索引 |
| GET | `/actuator/prometheus` | Prometheus 文本指标 |

## 调用验证

```bash
mvn -pl 23-SpringBoot-observability-metrics spring-boot:run

curl -X POST "http://localhost:8103/api/observability/orders/create?count=2"
curl -X POST "http://localhost:8103/api/observability/orders/process?success=true&durationMs=120"
curl -X POST "http://localhost:8103/api/observability/orders/process?success=false&durationMs=80"
curl "http://localhost:8103/actuator/prometheus" | grep demo_order
```

## 要点总结

1. [[Micrometer]] 负责统一指标 API，底层可对接 Prometheus 等监控系统
2. [[Spring Boot Actuator]] 提供 `/actuator/metrics` 与 `/actuator/prometheus` 等管理端点
3. 业务指标要围绕关键动作建模：创建量、成功量、失败量、积压量、耗时
4. 指标标签必须控制基数，只保留稳定、低基数、可聚合的维度
5. `Counter`、`Timer`、`Gauge` 分别对应累计事件、耗时分布、当前状态
