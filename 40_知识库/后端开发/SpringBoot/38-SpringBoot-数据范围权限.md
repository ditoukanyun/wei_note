---
title: SpringBoot 数据范围权限
date: 2026-05-11
tags:
  - springboot
  - java
  - 权限
module: 38-SpringBoot-data-scope-permission
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 数据范围权限

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/38-SpringBoot-data-scope-permission`

## 核心思路

本模块演示企业后台常见的数据权限范围：同一个订单查询接口，根据当前用户上下文返回本人、本部门或全部数据。

## 能力点

- `X-User-Id` 当前用户
- `X-Dept-Id` 当前部门
- `X-Data-Scope` 数据范围
- `SELF` 仅本人数据
- `DEPARTMENT` 本部门数据
- `ALL` 全部数据

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 数据范围权限 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/DataScopePermissionController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/DataScopePermissionController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/data-scope")
public class DataScopePermissionController {

    private final OrderDataScopeService orderDataScopeService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DataScopePermissionController(OrderDataScopeService orderDataScopeService) {
        this.orderDataScopeService = orderDataScopeService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "38-SpringBoot-data-scope-permission");
        data.put("desc", "数据权限范围：SELF、DEPARTMENT、ALL 三种查询过滤规则");
        data.put("apis", new String[]{
                "GET /api/data-scope/context",
                "GET /api/data-scope/orders",
                "GET /api/data-scope/orders/summary"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/context")
    public ApiResult<DataScopeContext> context() {
        return ApiResult.success(DataScopeContextHolder.require());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders")
    public ApiResult<List<ScopedOrder>> orders() {
        return ApiResult.success(orderDataScopeService.visibleOrders());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders/summary")
    public ApiResult<OrderScopeSummary> summary() {
        return ApiResult.success(orderDataScopeService.summary());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/OrderDataScopeService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/OrderDataScopeService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class OrderDataScopeService {

    private final InMemoryScopedOrderRepository orderRepository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public OrderDataScopeService(InMemoryScopedOrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public List<ScopedOrder> visibleOrders() {
        DataScopeContext context = DataScopeContextHolder.require();
        return orderRepository.findAll().stream()
                .filter(order -> visible(order, context))
                .toList();
    }

    public OrderScopeSummary summary() {
        DataScopeContext context = DataScopeContextHolder.require();
        List<ScopedOrder> orders = visibleOrders();
        BigDecimal total = orders.stream()
                .map(ScopedOrder::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        return new OrderScopeSummary(context.scope().name(), orders.size(), total);
    }

    private boolean visible(ScopedOrder order, DataScopeContext context) {
        if (context.scope() == DataScope.ALL) {
            return true;
        }
        if (context.scope() == DataScope.DEPARTMENT) {
            return order.getDeptId().equals(context.deptId());
        }
        return order.getOwnerUserId().equals(context.userId());
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/web/DataScopeContextInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/web/DataScopeContextInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class DataScopeContextInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        Long userId = parseLong(request.getHeader("X-User-Id"), "用户 ID 必须为正数");
        Long deptId = parseLong(request.getHeader("X-Dept-Id"), "部门 ID 必须为正数");
        String scopeHeader = request.getHeader("X-Data-Scope");
        if (scopeHeader == null || scopeHeader.isBlank()) {
            throw new IllegalArgumentException("数据范围不能为空");
        }
        DataScopeContextHolder.set(userId, deptId, DataScope.valueOf(scopeHeader));
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        DataScopeContextHolder.clear();
    }

    private Long parseLong(String value, String message) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(message);
        }
        return Long.valueOf(value);
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

    private final DataScopeContextInterceptor dataScopeContextInterceptor;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WebConfig(DataScopeContextInterceptor dataScopeContextInterceptor) {
        this.dataScopeContextInterceptor = dataScopeContextInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(dataScopeContextInterceptor)
                .addPathPatterns("/api/data-scope/context", "/api/data-scope/orders", "/api/data-scope/orders/**");
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. WebConfig：启动时注册配置、Bean 或扩展点
2. DataScopeContextInterceptor：请求进入 Controller 前准备上下文或校验
3. DataScopePermissionController：接收 HTTP 请求并转换成 Java 方法调用
4. OrderDataScopeService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/data-scope`：模块说明
- `GET /api/data-scope/context`：查看当前数据权限上下文
- `GET /api/data-scope/orders`：按当前范围查询可见订单
- `GET /api/data-scope/orders/summary`：按当前范围统计订单数量和金额

## 调用验证

```bash
curl "http://localhost:8118/api/data-scope/orders" \
  -H "X-User-Id: 1001" \
  -H "X-Dept-Id: 10" \
  -H "X-Data-Scope: SELF"

curl "http://localhost:8118/api/data-scope/orders" \
  -H "X-User-Id: 1001" \
  -H "X-Dept-Id: 10" \
  -H "X-Data-Scope: DEPARTMENT"

curl "http://localhost:8118/api/data-scope/orders/summary" \
  -H "X-User-Id: 1001" \
  -H "X-Dept-Id: 10" \
  -H "X-Data-Scope: ALL"
```

## 生产差距

该示例用于隔离学习 数据范围权限 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 38-SpringBoot-data-scope-permission test
```

## 要点总结

1. `X-User-Id` 当前用户
2. `X-Dept-Id` 当前部门
3. `X-Data-Scope` 数据范围
4. `SELF` 仅本人数据
5. `DEPARTMENT` 本部门数据

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
