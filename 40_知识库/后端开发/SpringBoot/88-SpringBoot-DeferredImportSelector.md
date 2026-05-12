---
title: SpringBoot DeferredImportSelector
date: 2026-05-11
tags:
  - springboot
  - java
module: 88-SpringBoot-deferred-import-selector
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot DeferredImportSelector

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/88-SpringBoot-deferred-import-selector`

## 核心思路

本模块演示 Spring 的 `DeferredImportSelector`：通过启用注解导入 selector，再由 selector 延迟返回配置类名称，最终注册业务 Bean。这个路径是理解 Spring Boot `AutoConfigurationImportSelector` 的一个最小可验证版本。

## 能力点

- `@Import`
- `DeferredImportSelector`
- `AnnotationMetadata`
- annotation-driven configuration import
- `@Configuration(proxyBeanMethods = false)`
- Spring Boot `AutoConfigurationImportSelector` 源码映射
- ApplicationContextRunner 验证导入链
- MockMvc 验证导入 Bean 已进入完整应用上下文

## 关键实现

`DeferredGreetingImportSelector` 返回配置类全限定名：

```java
return new String[]{DeferredGreetingConfig.class.getName()};
```

`DeferredGreetingConfig` 只负责提供被导入的 Bean：

```java
@Bean
DeferredGreetingService deferredGreetingService() {
    return new DeferredGreetingService();
}
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot DeferredImportSelector 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/DeferredImportSelectorController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/DeferredImportSelectorController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/deferred-import-selector")
public class DeferredImportSelectorController {
    private final DeferredGreetingService deferredGreetingService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DeferredImportSelectorController(DeferredGreetingService deferredGreetingService) {
        this.deferredGreetingService = deferredGreetingService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "88-SpringBoot-deferred-import-selector",
                "topic", "Spring DeferredImportSelector and Spring Boot AutoConfigurationImportSelector",
                "apis", List.of(
                        "GET /api/deferred-import-selector",
                        "GET /api/deferred-import-selector/greeting"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/greeting")
    public ApiResult<Map<String, String>> greeting() {
        return ApiResult.success(Map.of(
                "message", deferredGreetingService.message(),
                "source", deferredGreetingService.source()
        ));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/deferred/DeferredGreetingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/deferred/DeferredGreetingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class DeferredGreetingService {
    public String message() {
        return "hello from deferred import";
    }

    public String source() {
        return "DeferredGreetingConfig";
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/deferred/DeferredGreetingConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/deferred/DeferredGreetingConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class DeferredGreetingConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    DeferredGreetingService deferredGreetingService() {
        return new DeferredGreetingService();
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
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

1. DeferredGreetingConfig：启动时注册配置、Bean 或扩展点
2. DeferredImportSelectorController：接收 HTTP 请求并转换成 Java 方法调用
3. DeferredGreetingService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/deferred-import-selector`：模块说明
- `GET /api/deferred-import-selector/greeting`：返回由 deferred selector 导入的 Bean 输出

## 调用验证

```bash
curl "http://localhost:8168/api/deferred-import-selector"
```

```bash
curl "http://localhost:8168/api/deferred-import-selector/greeting"
```

`/greeting` 核心响应：

```json
{
  "message": "hello from deferred import",
  "source": "DeferredGreetingConfig"
}
```

## 生产映射

Spring Boot 自动配置的核心入口 `AutoConfigurationImportSelector` 也是 selector 思路：根据启动上下文和元数据选出要导入的配置类。真实 Boot 会继续处理 `.imports` 文件、条件过滤、排除项和排序，本模块只保留最核心的一段：注解触发 selector，selector 返回配置类，配置类贡献 Bean。

适合使用这个模式的场景：

- 构建 opt-in 功能开关注解
- 把启用入口和配置实现分离
- 阅读 auto-configuration import 源码
- 给 starter 或框架扩展点设计最小导入链

普通业务 Bean 不需要使用 `DeferredImportSelector`；直接使用 `@Bean`、`@Component` 或自动配置更清晰。

## 生产差距

该示例用于隔离学习 DeferredImportSelector 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 88-SpringBoot-deferred-import-selector test
```

测试覆盖：

- `DeferredGreetingImportSelector` 返回 `DeferredGreetingConfig`
- `@EnableDeferredGreeting` 能把 `DeferredGreetingService` 导入上下文
- MockMvc 验证 metadata 接口
- MockMvc 验证完整应用启动后可访问 imported greeting Bean

## 要点总结

1. `@Import`
2. `DeferredImportSelector`
3. `AnnotationMetadata`
4. annotation-driven configuration import
5. `@Configuration(proxyBeanMethods = false)`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
