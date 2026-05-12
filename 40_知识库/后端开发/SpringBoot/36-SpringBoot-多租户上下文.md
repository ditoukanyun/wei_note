---
title: SpringBoot 多租户上下文
date: 2026-05-11
tags:
  - springboot
  - java
  - 多租户
module: 36-SpringBoot-multi-tenant-context
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 多租户上下文

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/36-SpringBoot-multi-tenant-context`

## 核心思路

本模块演示多租户上下文：从请求头 `X-Tenant-Id` 解析租户，服务层从统一上下文读取租户，仓储层按租户隔离订单数据，并在请求结束清理 ThreadLocal。

## 能力点

- Web 拦截器解析租户请求头
- ThreadLocal 保存和清理租户上下文
- 服务层统一读取当前租户
- 内存仓储按租户隔离数据
- 缺少租户头时快速失败

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 多租户上下文 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- 认证/上下文类案例要特别关注“在哪里写入、在哪里校验、在哪里清理”。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/MultiTenantController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/MultiTenantController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/tenants")
public class MultiTenantController {

    private final TenantOrderService tenantOrderService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public MultiTenantController(TenantOrderService tenantOrderService) {
        this.tenantOrderService = tenantOrderService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "36-SpringBoot-multi-tenant-context");
        data.put("desc", "多租户上下文：从 X-Tenant-Id 解析租户，服务层和仓储层按租户隔离数据");
        data.put("apis", new String[]{
                "GET /api/tenants/context",
                "POST /api/tenants/orders?userId=1001&amount=99.90",
                "GET /api/tenants/orders"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/context")
    public ApiResult<TenantContextResponse> context() {
        return ApiResult.success(new TenantContextResponse(TenantContextHolder.requireTenantId()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/orders")
    public ResponseEntity<ApiResult<TenantOrder>> createOrder(@RequestParam Long userId,
                                                               @RequestParam BigDecimal amount) {
        return ResponseEntity.ok(ApiResult.success(tenantOrderService.createOrder(userId, amount)));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders")
    public ApiResult<List<TenantOrder>> listOrders() {
        return ApiResult.success(tenantOrderService.listOrders());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/TenantOrderService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/TenantOrderService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class TenantOrderService {

    private final InMemoryTenantOrderRepository orderRepository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public TenantOrderService(InMemoryTenantOrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public TenantOrder createOrder(Long userId, BigDecimal amount) {
        String tenantId = TenantContextHolder.requireTenantId();
        if (userId == null || userId <= 0) {
            throw new IllegalArgumentException("用户 ID 必须为正数");
        }
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("订单金额必须大于 0");
        }
        TenantOrder order = new TenantOrder(null, tenantId, userId, amount, "CREATED", Instant.now());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return orderRepository.save(tenantId, order);
    }

    public List<TenantOrder> listOrders() {
        return orderRepository.findByTenantId(TenantContextHolder.requireTenantId());
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/web/TenantContextInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/web/TenantContextInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class TenantContextInterceptor implements HandlerInterceptor {

    public static final String TENANT_HEADER = "X-Tenant-Id";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        // 在请求进入业务前写入上下文，后续 Service 就不用再传 tenantId 参数。
        TenantContextHolder.setTenantId(request.getHeader(TENANT_HEADER));
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        // 请求结束后清理上下文，这是 ThreadLocal 用法的安全底线。
        TenantContextHolder.clear();
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/WebConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/WebConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final TenantContextInterceptor tenantContextInterceptor;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WebConfig(TenantContextInterceptor tenantContextInterceptor) {
        this.tenantContextInterceptor = tenantContextInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(tenantContextInterceptor)
                .addPathPatterns("/api/tenants/orders", "/api/tenants/orders/**", "/api/tenants/context");
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. WebConfig：启动时注册配置、Bean 或扩展点
2. TenantContextInterceptor：请求进入 Controller 前准备上下文或校验
3. MultiTenantController：接收 HTTP 请求并转换成 Java 方法调用
4. TenantOrderService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。
- 使用 `ThreadLocal` 后忘记清理，在线程池环境会造成上下文串号。

## API 接口

- `GET /api/tenants`：模块说明
- `GET /api/tenants/context`：查看当前租户上下文
- `POST /api/tenants/orders?userId=1001&amount=99.90`：当前租户下创建订单
- `GET /api/tenants/orders`：查询当前租户订单

## 调用验证

```bash
curl -X POST "http://localhost:8116/api/tenants/orders?userId=1001&amount=99.90" \
  -H "X-Tenant-Id: tenant-a"

curl "http://localhost:8116/api/tenants/orders" \
  -H "X-Tenant-Id: tenant-a"

curl "http://localhost:8116/api/tenants/orders" \
  -H "X-Tenant-Id: tenant-b"
```

## 生产差距

该示例用于隔离学习 多租户上下文 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 36-SpringBoot-multi-tenant-context test
```

## 要点总结

1. Web 拦截器解析租户请求头
2. ThreadLocal 保存和清理租户上下文
3. 服务层统一读取当前租户
4. 内存仓储按租户隔离数据
5. 缺少租户头时快速失败

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
