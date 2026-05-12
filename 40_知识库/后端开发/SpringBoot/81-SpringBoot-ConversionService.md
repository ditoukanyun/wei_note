---
title: SpringBoot ConversionService
date: 2026-05-11
tags:
  - springboot
  - java
  - 类型转换
module: 81-SpringBoot-conversion-service
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ConversionService

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/81-SpringBoot-conversion-service`

## 核心思路

本模块演示 Spring Boot 的 `ApplicationConversionService` 和 Spring `Converter`：把外部字符串集中转换为业务类型。

## 能力点

- `ApplicationConversionService`
- `Converter<String, T>`
- 字符串到 enum 的转换
- 字符串到 value object 的转换
- 转换输入校验
- MockMvc 验证 API 输出

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ConversionService 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ConversionServiceController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ConversionServiceController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/conversion-service")
public class ConversionServiceController {
    private final ConversionDemoService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ConversionServiceController(ConversionDemoService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "81-SpringBoot-conversion-service",
                "apis", List.of(
                        "GET /api/conversion-service",
                        "GET /api/conversion-service/status?value=paid",
                        "GET /api/conversion-service/money?value=CNY:12.50"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/status")
    public ApiResult<OrderStatus> status(@RequestParam String value) {
        return ApiResult.success(service.convertStatus(value));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/money")
    public ApiResult<MoneyAmount> money(@RequestParam String value) {
        return ApiResult.success(service.convertMoney(value));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/conversion/ConversionServiceConfig.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/conversion/ConversionServiceConfig.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class ConversionServiceConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public ApplicationConversionService applicationConversionService(OrderStatusConverter orderStatusConverter,
                                                                     MoneyAmountConverter moneyAmountConverter) {
        ApplicationConversionService conversionService = new ApplicationConversionService();
        // Boot's ApplicationConversionService is the shared place for application-level type conversion.
        conversionService.addConverter(orderStatusConverter);
        conversionService.addConverter(moneyAmountConverter);
        return conversionService;
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/conversion/ConversionDemoService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/conversion/ConversionDemoService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ConversionDemoService {
    private final ApplicationConversionService conversionService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ConversionDemoService(ApplicationConversionService conversionService) {
        this.conversionService = conversionService;
    }

    public OrderStatus convertStatus(String value) {
        return conversionService.convert(value, OrderStatus.class);
    }

    public MoneyAmount convertMoney(String value) {
        return conversionService.convert(value, MoneyAmount.class);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：GlobalExceptionHandler

源码位置：`src/main/java/com/cloud/exception/GlobalExceptionHandler.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/exception/GlobalExceptionHandler.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler({IllegalArgumentException.class, NoSuchElementException.class})
    @ResponseStatus(BAD_REQUEST)
    public ApiResult<Void> handleBadRequest(RuntimeException exception) {
        return ApiResult.fail(400, exception.getMessage());
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. ConversionServiceConfig：启动时注册配置、Bean 或扩展点
2. ConversionServiceController：接收 HTTP 请求并转换成 Java 方法调用
3. ConversionServiceController：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/conversion-service`：模块说明
- `GET /api/conversion-service/status?value=paid`：转换订单状态
- `GET /api/conversion-service/money?value=CNY:12.50`：转换金额值对象

## 调用验证

```bash
curl "http://localhost:8161/api/conversion-service"
```

```bash
curl "http://localhost:8161/api/conversion-service/status?value=order-cancelled"
```

```bash
curl "http://localhost:8161/api/conversion-service/money?value=CNY:12.50"
```

## 生产映射

生产系统可以用这个模式：

- 集中维护字符串到业务类型的转换规则
- 避免 controller 和 service 中散落手写解析逻辑
- 让非法输入尽早失败
- 复用转换逻辑给参数绑定、配置绑定或内部服务使用

如果只是临时解析一个字符串，手写解析也能工作；如果多个入口都要转换同一类业务值，应该沉淀为 `Converter` 并交给 conversion service 管理。

## 生产差距

该示例用于隔离学习 ConversionService 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 81-SpringBoot-conversion-service test
```

测试覆盖：

- 状态转换大小写和连字符归一化
- 金额转换和 `BigDecimal` 解析
- 非法状态和非法金额拒绝
- `ApplicationConversionService` 注册后实际执行自定义转换
- MockMvc 验证模块信息、状态转换和金额转换接口

## 要点总结

1. `ApplicationConversionService`
2. `Converter<String, T>`
3. 字符串到 enum 的转换
4. 字符串到 value object 的转换
5. 转换输入校验

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
