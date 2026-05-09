---
title: SpringBoot 弹性治理：重试、超时、熔断与限流
date: 2026-04-28
tags:
  - springboot
  - java
  - resilience4j
  - 重试
  - 熔断
  - 限流
module: 29-SpringBoot-resilience-retry-timeout
---
# SpringBoot 弹性治理：重试、超时、熔断与限流

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/29-SpringBoot-resilience-retry-timeout`

## 核心思路

本模块演示 [[Resilience4j]] 在 [[SpringBoot]] 服务调用中的常见韧性策略：[[重试]]、[[超时控制]]、[[熔断器]] 和 [[限流]]。当下游供应商接口短暂失败、慢调用、熔断打开或入口过载时，服务返回带原因的降级报价。

## 项目结构

```text
src/main/java/com/cloud/
├── controller/
│   ├── ResilienceDemoController.java      (业务入口)
│   └── MockSupplierController.java        (mock 下游供应商)
├── service/
│   ├── ResilienceProductService.java      (弹性治理核心)
│   ├── SupplierClient.java
│   └── MockSupplierClient.java
├── model/
│   ├── ProductQuote.java
│   └── QueryOptions.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 四类弹性策略

| 策略 | 适用场景 | 本模块表现 |
|------|----------|------------|
| [[重试]] Retry | 短暂网络抖动、一次性失败 | `failTimes=1` 后第二次成功 |
| [[超时控制]] TimeLimiter | 下游响应太慢 | `delayMs=800` 返回 `TIMEOUT` 降级 |
| [[熔断器]] CircuitBreaker | 下游持续失败，避免继续压垮 | `forceOpen=true` 返回 `CIRCUIT_OPEN` |
| [[限流]] RateLimiter | 入口请求过载 | `limited=true` 返回 `RATE_LIMITED` |

## ResilienceProductService 配置

```java
this.retry = Retry.of("supplierRetry", RetryConfig.custom()
        .maxAttempts(maxAttempts)
        .waitDuration(Duration.ofMillis(10))
        .retryExceptions(IllegalStateException.class, TimeoutException.class, CompletionException.class)
        .build());

this.circuitBreaker = CircuitBreaker.of("supplierCircuitBreaker", CircuitBreakerConfig.custom()
        .failureRateThreshold(50)
        .slidingWindowSize(4)
        .minimumNumberOfCalls(2)
        .waitDurationInOpenState(Duration.ofSeconds(1))
        .build());

this.rateLimiter = RateLimiter.of("supplierRateLimiter", RateLimiterConfig.custom()
        .limitForPeriod(rateLimitForPeriod)
        .limitRefreshPeriod(Duration.ofSeconds(1))
        .timeoutDuration(Duration.ZERO)
        .build());

this.timeLimiter = TimeLimiter.of(TimeLimiterConfig.custom()
        .timeoutDuration(Duration.ofMillis(timeoutMs))
        .cancelRunningFuture(true)
        .build());
```

## 调用装饰链

```java
Supplier<ProductQuote> supplier = () -> queryWithTimeout(productId, options);
supplier = Retry.decorateSupplier(retry, supplier);
supplier = CircuitBreaker.decorateSupplier(circuitBreaker, supplier);
supplier = RateLimiter.decorateSupplier(rateLimiter, supplier);

try {
    return supplier.get();
} catch (Exception ex) {
    return fallback(productId, rootCause(ex));
}
```

> [!important] 装饰顺序
> 本模块将超时逻辑包在实际下游调用中，再叠加 Retry、CircuitBreaker、RateLimiter。不同顺序会影响统计口径和失败传播方式。

## 超时保护

```java
private ProductQuote queryWithTimeout(Long productId, QueryOptions options) {
    return TimeLimiter.decorateFutureSupplier(timeLimiter, () -> CompletableFuture.supplyAsync(
            () -> supplierClient.fetchProduct(productId, options),
            executorService
    )).call();
}
```

慢调用被放入 `CompletableFuture`，由 `TimeLimiter` 控制最大等待时间。超过时间后抛出超时异常并进入 fallback。

## 降级结果

```java
private ProductQuote fallback(Long productId, Throwable ex) {
    String reason = reasonOf(ex);
    return new ProductQuote(
            productId,
            "fallback-product-" + productId,
            BigDecimal.ZERO,
            -1,
            "DEGRADED",
            true,
            reason,
            0
    );
}
```

| 异常类型 | 降级原因 |
|----------|----------|
| `RequestNotPermitted` | `RATE_LIMITED` |
| `CallNotPermittedException` | `CIRCUIT_OPEN` |
| `TimeoutException` | `TIMEOUT` |
| 其他下游异常 | `DOWNSTREAM_ERROR` |

> [!tip] 降级数据要可识别
> `degraded=true` 和 `reason` 让调用方知道当前结果不是实时真实报价，而是保护系统稳定性的保守响应。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/resilience` | 模块说明 |
| GET | `/api/resilience/products/{id}` | 正常查询商品报价 |
| GET | `/api/resilience/products/{id}?failTimes=1` | 短暂失败后重试成功 |
| GET | `/api/resilience/products/{id}?delayMs=800` | 慢调用超时降级 |
| GET | `/api/resilience/products/{id}?forceOpen=true` | 熔断打开快速降级 |
| GET | `/api/resilience/products/{id}?limited=true` | 限流拒绝降级 |

## 调用验证

```bash
mvn -pl 29-SpringBoot-resilience-retry-timeout spring-boot:run

curl "http://localhost:8109/api/resilience/products/1"
curl "http://localhost:8109/api/resilience/products/1?failTimes=1"
curl "http://localhost:8109/api/resilience/products/1?delayMs=800"
curl "http://localhost:8109/api/resilience/products/1?forceOpen=true"
curl "http://localhost:8109/api/resilience/products/1?limited=true"
```

## 要点总结

1. [[重试]] 适合短暂失败，不适合不可恢复的业务错误
2. [[超时控制]] 防止线程长期等待慢下游
3. [[熔断器]] 在失败率过高时快速失败，保护调用方和下游
4. [[限流]] 在入口处拒绝超额请求，避免系统被突发流量压垮
5. 降级响应要显式标记原因，避免调用方误用保守数据

## 实践流程

```mermaid
flowchart LR
  A[识别下游依赖] --> B[设置超时]
  B --> C[按错误类型配置重试]
  C --> D[配置熔断和限流]
  D --> E[返回可识别降级结果]
```

## 实践检查清单

- 是否先设置超时，再讨论重试。
- 重试是否只用于幂等、短暂失败的请求。
- 熔断阈值是否基于真实错误率和慢调用比例。
- 限流是否区分入口流量和下游保护。
- 降级结果是否带有原因，调用方不会误用。

## 案例

商品报价接口依赖第三方服务。第三方慢时先超时降级；连续失败后熔断打开，短时间内快速返回保守报价，避免线程池被拖满。

## 常见误区

- 对非幂等写请求无脑重试。
- 没有超时，重试只会放大拥塞。
- 降级数据没有标记，前端当成真实数据展示。
