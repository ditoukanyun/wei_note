---
title: SpringBoot 审计轨迹
date: 2026-05-11
tags:
  - springboot
  - java
  - 审计
module: 37-SpringBoot-audit-trail
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 审计轨迹

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/37-SpringBoot-audit-trail`

## 核心思路

本模块演示审计日志：写操作从请求头读取操作人和请求 ID，业务变更时同步记录动作、资源、变更前后状态和操作时间。

## 能力点

- `X-Operator-Id` 操作人上下文
- `X-Request-Id` 请求追踪上下文
- 业务写操作同步写审计日志
- 审计日志包含 before/after
- 按资源、操作人查询审计记录

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 审计轨迹 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/AuditTrailController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/AuditTrailController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/audit")
public class AuditTrailController {

    private final AuditedOrderService orderService;
    private final AuditTrailService auditTrailService;

    public AuditTrailController(AuditedOrderService orderService,
                                AuditTrailService auditTrailService) {
        this.orderService = orderService;
        this.auditTrailService = auditTrailService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "37-SpringBoot-audit-trail");
        data.put("desc", "审计日志：记录操作人、请求 ID、动作、资源和变更前后状态");
        data.put("apis", new String[]{
                "POST /api/audit/orders?amount=99.90",
                "PATCH /api/audit/orders/{id}/status?status=PAID",
                "GET /api/audit/orders",
                "GET /api/audit/logs"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/orders")
    public ResponseEntity<ApiResult<AuditedOrder>> createOrder(@RequestParam BigDecimal amount) {
        return ResponseEntity.ok(ApiResult.success(orderService.createOrder(amount)));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PatchMapping("/orders/{id}/status")
    public ResponseEntity<ApiResult<AuditedOrder>> updateStatus(@PathVariable Long id,
                                                                 @RequestParam String status) {
        return ResponseEntity.ok(ApiResult.success(orderService.updateStatus(id, status)));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders")
    public ApiResult<List<AuditedOrder>> orders() {
        return ApiResult.success(orderService.listOrders());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/logs")
    public ApiResult<List<AuditLogEntry>> logs(@RequestParam(required = false) String resourceType,
                                               @RequestParam(required = false) String resourceId,
                                               @RequestParam(required = false) String operatorId) {
        return ApiResult.success(auditTrailService.search(resourceType, resourceId, operatorId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/AuditedOrderService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/AuditedOrderService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class AuditedOrderService {

    private final InMemoryAuditedOrderRepository orderRepository;
    private final AuditTrailService auditTrailService;

    public AuditedOrderService(InMemoryAuditedOrderRepository orderRepository,
                               AuditTrailService auditTrailService) {
        this.orderRepository = orderRepository;
        this.auditTrailService = auditTrailService;
    }

    public AuditedOrder createOrder(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("订单金额必须大于 0");
        }
        Instant now = Instant.now();
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        AuditedOrder order = orderRepository.save(new AuditedOrder(null, amount, "CREATED", now, now));
        auditTrailService.record("CREATE_ORDER", "ORDER", order.getId().toString(), "null", order.getStatus());
        return order;
    }

    public AuditedOrder updateStatus(Long orderId, String status) {
        if (status == null || status.isBlank()) {
            throw new IllegalArgumentException("订单状态不能为空");
        }
        AuditedOrder order = orderRepository.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException(orderId));
        String before = order.getStatus();
        order.setStatus(status);
        order.setUpdatedAt(Instant.now());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        orderRepository.save(order);
        auditTrailService.record("UPDATE_ORDER_STATUS", "ORDER", order.getId().toString(), before, status);
        return order;
    }

    public List<AuditedOrder> listOrders() {
        return orderRepository.findAll();
    }

    public static class OrderNotFoundException extends RuntimeException {

        // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
        public OrderNotFoundException(Long orderId) {
            super("订单不存在: " + orderId);
        }
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/AuditTrailService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/AuditTrailService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class AuditTrailService {

    private final InMemoryAuditLogRepository auditLogRepository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public AuditTrailService(InMemoryAuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    public AuditLogEntry record(String action,
                                String resourceType,
                                String resourceId,
                                String beforeValue,
                                String afterValue) {
        AuditContext context = AuditContextHolder.require();
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return auditLogRepository.save(new AuditLogEntry(
                null,
                context.operatorId(),
                context.requestId(),
                action,
                resourceType,
                resourceId,
                beforeValue,
                afterValue,
                Instant.now()
        ));
    }

    public List<AuditLogEntry> search(String resourceType, String resourceId, String operatorId) {
        return auditLogRepository.search(resourceType, resourceId, operatorId);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/web/AuditContextInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/web/AuditContextInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class AuditContextInterceptor implements HandlerInterceptor {

    public static final String OPERATOR_HEADER = "X-Operator-Id";
    public static final String REQUEST_HEADER = "X-Request-Id";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        AuditContextHolder.set(request.getHeader(OPERATOR_HEADER), request.getHeader(REQUEST_HEADER));
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        AuditContextHolder.clear();
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. AuditContextInterceptor：请求进入 Controller 前准备上下文或校验
2. AuditTrailController：接收 HTTP 请求并转换成 Java 方法调用
3. AuditedOrderService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/audit`：模块说明
- `POST /api/audit/orders?amount=99.90`：创建订单并记录审计
- `PATCH /api/audit/orders/{id}/status?status=PAID`：更新订单状态并记录审计
- `GET /api/audit/orders`：查询订单列表
- `GET /api/audit/logs`：查询审计日志

## 调用验证

```bash
curl -X POST "http://localhost:8117/api/audit/orders?amount=99.90" \
  -H "X-Operator-Id: operator-a" \
  -H "X-Request-Id: req-1"

curl -X PATCH "http://localhost:8117/api/audit/orders/1001/status?status=PAID" \
  -H "X-Operator-Id: operator-b" \
  -H "X-Request-Id: req-2"

curl "http://localhost:8117/api/audit/logs?operatorId=operator-b"
```

## 生产差距

该示例用于隔离学习 审计轨迹 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 37-SpringBoot-audit-trail test
```

## 要点总结

1. `X-Operator-Id` 操作人上下文
2. `X-Request-Id` 请求追踪上下文
3. 业务写操作同步写审计日志
4. 审计日志包含 before/after
5. 按资源、操作人查询审计记录

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
