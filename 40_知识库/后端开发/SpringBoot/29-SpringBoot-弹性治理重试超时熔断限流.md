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
area: [[后端开发]]
created: 2026-04-28
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

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 弹性治理：重试、超时、熔断与限流 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/MockSupplierController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/MockSupplierController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/mock/supplier")
public class MockSupplierController {

    private final MockSupplierClient mockSupplierClient;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public MockSupplierController(MockSupplierClient mockSupplierClient) {
        this.mockSupplierClient = mockSupplierClient;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/products/{id}")
    public ProductQuote queryProduct(@PathVariable Long id,
                                     @RequestParam(defaultValue = "0") int failTimes,
                                     @RequestParam(defaultValue = "0") long delayMs) {
        QueryOptions options = QueryOptions.builder()
                .failTimes(failTimes)
                .delayMs(delayMs)
                .build();
        return mockSupplierClient.fetchProduct(id, options);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ResilienceDemoController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ResilienceDemoController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/resilience")
public class ResilienceDemoController {

    private final ResilienceProductService resilienceProductService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ResilienceDemoController(ResilienceProductService resilienceProductService) {
        this.resilienceProductService = resilienceProductService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "29-SpringBoot-resilience-retry-timeout");
        data.put("desc", "Resilience4j 重试、超时、熔断与限流示例");
        data.put("apis", new String[]{
                "GET /api/resilience/products/{id}",
                "GET /api/resilience/products/{id}?failTimes=1",
                "GET /api/resilience/products/{id}?delayMs=800",
                "GET /api/resilience/products/{id}?forceOpen=true",
                "GET /api/resilience/products/{id}?limited=true",
                "GET /mock/supplier/products/{id}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/products/{id}")
    public ResponseEntity<ApiResult<ProductQuote>> queryProduct(@PathVariable Long id,
                                                                 @RequestParam(defaultValue = "0") int failTimes,
                                                                 @RequestParam(defaultValue = "0") long delayMs,
                                                                 @RequestParam(defaultValue = "false") boolean forceOpen,
                                                                 @RequestParam(defaultValue = "false") boolean limited) {
        QueryOptions options = QueryOptions.builder()
                .failTimes(failTimes)
                .delayMs(delayMs)
                .forceOpen(forceOpen)
                .limited(limited)
                .build();
        return ResponseEntity.ok(ApiResult.success(resilienceProductService.queryProduct(id, options)));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ResilienceProductService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ResilienceProductService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ResilienceProductService {

    private final SupplierClient supplierClient;
    private final Retry retry;
    private final CircuitBreaker circuitBreaker;
    private final RateLimiter rateLimiter;
    private final TimeLimiter timeLimiter;
    private final ExecutorService executorService;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ResilienceProductService(SupplierClient supplierClient) {
        this(supplierClient, 3, 300, 5);
    }

    public ResilienceProductService(SupplierClient supplierClient,
                                    int maxAttempts,
                                    long timeoutMs,
                                    int rateLimitForPeriod) {
        this.supplierClient = supplierClient;
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
        this.executorService = Executors.newCachedThreadPool();
    }

    public ProductQuote queryProduct(Long productId, QueryOptions options) {
        if (productId == null || productId <= 0) {
            throw new IllegalArgumentException("商品 ID 必须为正数");
        }

        if (options.isLimited()) {
            rateLimiter.acquirePermission();
        }
        if (options.isForceOpen()) {
            circuitBreaker.transitionToOpenState();
        }

        Supplier<ProductQuote> supplier = () -> queryWithTimeout(productId, options);
        supplier = Retry.decorateSupplier(retry, supplier);
        supplier = CircuitBreaker.decorateSupplier(circuitBreaker, supplier);
        supplier = RateLimiter.decorateSupplier(rateLimiter, supplier);

        try {
            return supplier.get();
        } catch (Exception ex) {
            return fallback(productId, rootCause(ex));
        } finally {
            if (options.isForceOpen()) {
                circuitBreaker.reset();
            }
        }
    }

    public void shutdown() {
        executorService.shutdownNow();
    }

    private ProductQuote queryWithTimeout(Long productId, QueryOptions options) {
        try {
            return TimeLimiter.decorateFutureSupplier(timeLimiter, () -> CompletableFuture.supplyAsync(
                    () -> supplierClient.fetchProduct(productId, options),
                    executorService
            )).call();
        } catch (RuntimeException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new CompletionException(ex);
        }
    }

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

    private String reasonOf(Throwable ex) {
        if (ex instanceof RequestNotPermitted) {
            return "RATE_LIMITED";
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：MockSupplierClient

源码位置：`src/main/java/com/cloud/service/MockSupplierClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/service/MockSupplierClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
public class MockSupplierClient implements SupplierClient {

    private static final Map<Long, ProductQuote> PRODUCTS = Map.of(
            1L, new ProductQuote(1L, "iPhone 15", new BigDecimal("5999.00"), 56, "AVAILABLE", false, "NONE", 1),
            2L, new ProductQuote(2L, "MacBook Pro", new BigDecimal("13999.00"), 18, "AVAILABLE", false, "NONE", 1),
            3L, new ProductQuote(3L, "AirPods Pro", new BigDecimal("1899.00"), 103, "AVAILABLE", false, "NONE", 1)
    );

    private final Map<String, AtomicInteger> requestAttempts = new ConcurrentHashMap<>();

    @Override
    public ProductQuote fetchProduct(Long productId, QueryOptions options) {
        sleep(options.getDelayMs());

        int attempt = requestAttempts
                .computeIfAbsent(requestKey(productId, options), key -> new AtomicInteger())
                .incrementAndGet();
        if (attempt <= options.getFailTimes()) {
            throw new IllegalStateException("supplier temporary failure, attempt=" + attempt);
        }

        ProductQuote product = PRODUCTS.get(productId);
        if (product == null) {
            throw new IllegalArgumentException("商品不存在");
        }

        return new ProductQuote(
                product.getProductId(),
                product.getName(),
                product.getPrice(),
                product.getStock(),
                "AVAILABLE",
                false,
                "NONE",
                attempt
        );
    }

    public void reset() {
        requestAttempts.clear();
    }

    private String requestKey(Long productId, QueryOptions options) {
        return productId + ":" + options.getFailTimes() + ":" + options.getDelayMs();
    }

    private void sleep(long delayMs) {
        if (delayMs <= 0L) {
            return;
        }
        try {
            Thread.sleep(delayMs);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("supplier request interrupted", ex);
        }
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

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

## 生产差距

这个示例适合帮助初学者理解 弹性治理：重试、超时、熔断与限流 的核心机制，但生产项目不能只停留在“能跑通”。真实落地时至少要补齐：统一鉴权、参数边界校验、异常响应、结构化日志、监控指标、自动化测试、配置隔离和容量评估。

如果模块涉及数据库、缓存、消息、网关、认证或外部服务，还要进一步考虑连接池、超时、重试、幂等、事务边界、数据一致性和故障告警。学习时可以先记住主流程，再用这些生产差距反向检查自己是否真正理解了案例。

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
