---
title: SpringBoot ObjectProvider
date: 2026-05-11
tags:
  - springboot
  - java
module: 91-SpringBoot-object-provider
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ObjectProvider

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/91-SpringBoot-object-provider`

## 核心思路

本模块演示 Spring 的 `ObjectProvider`：在不强制依赖 Bean 必须存在的情况下，延迟读取候选 Bean、按顺序选择策略，并为缺失依赖提供 fallback。

## 能力点

- `ObjectProvider<T>`
- `orderedStream()`
- `getIfAvailable(Supplier<T>)`
- optional dependency lookup
- ordered strategy candidates
- missing bean fallback
- ApplicationContextRunner 验证不同候选集合
- MockMvc 验证完整应用上下文中的 provider 行为

## 关键实现

按顺序读取候选 Bean：

```java
List<AlertChannel> ordered = alertChannels.orderedStream().toList();
```

缺失依赖 fallback：

```java
AuditSink sink = auditSink.getIfAvailable(DisabledAuditSink::new);
```

无 channel 时使用 no-op fallback：

```java
AlertChannel primary = ordered.stream().findFirst().orElseGet(NoopAlertChannel::new);
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ObjectProvider 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ObjectProviderController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ObjectProviderController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/object-provider")
public class ObjectProviderController {
    private final AlertRoutingService alertRoutingService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ObjectProviderController(AlertRoutingService alertRoutingService) {
        this.alertRoutingService = alertRoutingService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "91-SpringBoot-object-provider",
                "topic", "Spring ObjectProvider optional and ordered dependency lookup",
                "apis", List.of(
                        "GET /api/object-provider",
                        "GET /api/object-provider/summary?payload=boot"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/summary")
    public ApiResult<AlertRoutingSummary> summary(@RequestParam(defaultValue = "boot") String payload) {
        return ApiResult.success(alertRoutingService.summary(payload));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/provider/ObjectProviderConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/provider/ObjectProviderConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class ObjectProviderConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    AlertChannel emailAlertChannel() {
        return new EmailAlertChannel();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    AlertChannel smsAlertChannel() {
        return new SmsAlertChannel();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    AlertRoutingService alertRoutingService(ObjectProvider<AlertChannel> alertChannels,
                                            ObjectProvider<AuditSink> auditSink) {
        return new AlertRoutingService(alertChannels, auditSink);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/provider/AlertRoutingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/provider/AlertRoutingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class AlertRoutingService {
    private final ObjectProvider<AlertChannel> alertChannels;
    private final ObjectProvider<AuditSink> auditSink;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public AlertRoutingService(ObjectProvider<AlertChannel> alertChannels, ObjectProvider<AuditSink> auditSink) {
        this.alertChannels = alertChannels;
        this.auditSink = auditSink;
    }

    public AlertRoutingSummary summary(String payload) {
        // Boot auto-configuration often uses ObjectProvider to inspect optional collaborators lazily.
        List<AlertChannel> ordered = alertChannels.orderedStream().toList();
        AlertChannel primary = ordered.stream().findFirst().orElseGet(NoopAlertChannel::new);
        AuditSink sink = auditSink.getIfAvailable(DisabledAuditSink::new);

        return new AlertRoutingSummary(
                primary.name(),
                ordered.stream().map(AlertChannel::name).toList(),
                primary.deliver(payload),
                sink.mode()
        );
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

1. ObjectProviderConfig：启动时注册配置、Bean 或扩展点
2. ObjectProviderController：接收 HTTP 请求并转换成 Java 方法调用
3. AlertRoutingService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/object-provider`：模块说明
- `GET /api/object-provider/summary?payload=boot`：返回有序候选和 fallback 摘要

## 调用验证

```bash
curl "http://localhost:8171/api/object-provider"
```

```bash
curl "http://localhost:8171/api/object-provider/summary?payload=boot"
```

`/summary` 核心响应：

```json
{
  "primaryChannel": "email",
  "orderedChannels": ["email", "sms"],
  "delivered": "email:boot",
  "auditMode": "disabled-fallback"
}
```

## 生产映射

Spring Boot 自动配置大量使用 `ObjectProvider` 处理可选协作者：有 Bean 就用，没有 Bean 就 fallback，或者在真正需要时才遍历候选。这样可以避免为了一个可选能力导致应用启动失败。

适合使用这个模式的场景：

- 自动配置中读取用户自定义 Bean
- 多个策略 Bean 按顺序选择
- 可选基础设施不存在时提供 no-op fallback
- 避免过早实例化候选 Bean
- 阅读 Spring Boot auto-configuration 源码

如果依赖是业务强依赖，应直接构造器注入，让缺失依赖在启动时失败。

## 生产差距

该示例用于隔离学习 ObjectProvider 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 91-SpringBoot-object-provider test
```

测试覆盖：

- `orderedStream()` 按 `email`、`sms` 排序
- primary channel 选择 `email`
- 缺失 `AuditSink` 使用 `disabled-fallback`
- 无 `AlertChannel` 上下文使用 `noop`
- MockMvc 验证 metadata 和 summary 接口

## 要点总结

1. `ObjectProvider<T>`
2. `orderedStream()`
3. `getIfAvailable(Supplier<T>)`
4. optional dependency lookup
5. ordered strategy candidates

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
