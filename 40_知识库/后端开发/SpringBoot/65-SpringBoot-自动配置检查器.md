---
title: SpringBoot 自动配置检查器
date: 2026-05-11
tags:
  - springboot
  - java
  - 配置
  - 自动配置
module: 65-SpringBoot-autoconfigure-inspector
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 自动配置检查器

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/65-SpringBoot-autoconfigure-inspector`

## 核心思路

本模块演示 Spring Boot 自动配置的核心机制：自动配置导入、类型化属性绑定、条件装配、用户 Bean 覆盖，以及 `ApplicationContextRunner` 测试。

## 能力点

- `@AutoConfiguration`
- `AutoConfiguration.imports`
- `@ConfigurationProperties`
- `@EnableConfigurationProperties`
- `@ConditionalOnProperty`
- `@ConditionalOnMissingBean`
- `ApplicationContextRunner`
- `ObjectProvider`

## 配置要点

模块通过以下文件注册自动配置：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

自动配置类为 `FeatureAutoConfiguration`，它会在满足条件时创建 `GreetingService`：

- `demo.feature.enabled=true` 或未配置该属性
- 当前容器中没有用户自定义的 `GreetingService`

这对应 Spring Boot starter 中常见的两个扩展点：属性开关和用户 Bean 覆盖。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 自动配置检查器 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- starter/自动配置案例重点看条件注解、配置绑定和用户覆盖点。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/AutoConfigureInspectorController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/AutoConfigureInspectorController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/autoconfig")
public class AutoConfigureInspectorController {
    private final FeatureProperties properties;
    private final ObjectProvider<GreetingService> greetingService;

    public AutoConfigureInspectorController(FeatureProperties properties,
                                            ObjectProvider<GreetingService> greetingService) {
        this.properties = properties;
        this.greetingService = greetingService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "65-SpringBoot-autoconfigure-inspector");
        data.put("desc", "自动配置、条件装配、属性绑定和用户 Bean 覆盖");
        data.put("apis", new String[]{
                "GET /api/autoconfig",
                "GET /api/autoconfig/properties",
                "GET /api/autoconfig/greet?name=java"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/properties")
    public ApiResult<Map<String, Object>> properties() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("enabled", properties.isEnabled());
        data.put("prefix", properties.getPrefix());
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/greet")
    public ApiResult<Map<String, Object>> greet(@RequestParam(defaultValue = "java") String name) {
        GreetingService service = greetingService.getIfAvailable();
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("available", service != null);
        data.put("message", service == null ? "GreetingService unavailable" : service.greet(name));
        return ApiResult.success(data);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 自动配置入口：Starter 如何装配 Bean

源码位置：`src/main/java/com/cloud/autoconfig/FeatureAutoConfiguration.java`

AutoConfiguration 是 starter 的核心，它决定“什么条件下自动创建哪些 Bean”。

```java
// 文件：com/cloud/autoconfig/FeatureAutoConfiguration.java
// 学习重点：AutoConfiguration 是 starter 的核心，它决定“什么条件下自动创建哪些 Bean”。
@AutoConfiguration
@EnableConfigurationProperties(FeatureProperties.class)
public class FeatureAutoConfiguration {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    // Property condition mirrors common starter switches: missing means enabled unless explicitly false.
    // 通过配置开关控制这个 Bean 或配置类是否生效。
    @ConditionalOnProperty(prefix = "demo.feature", name = "enabled", havingValue = "true", matchIfMissing = true)
    // Missing-bean condition is the standard user override hook used heavily in Spring Boot auto-configurations.
    // 只有容器里还没有同类型 Bean 时才创建默认实现，给业务方留下覆盖点。
    @ConditionalOnMissingBean(GreetingService.class)
    public GreetingService greetingService(FeatureProperties properties) {
        return new DefaultGreetingService(properties);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/autoconfig/DefaultGreetingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/autoconfig/DefaultGreetingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class DefaultGreetingService implements GreetingService {
    private final FeatureProperties properties;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DefaultGreetingService(FeatureProperties properties) {
        this.properties = properties;
    }

    @Override
    public String greet(String name) {
        return properties.getPrefix() + " " + name;
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/autoconfig/GreetingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/autoconfig/GreetingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public interface GreetingService {
    String greet(String name);
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. AutoConfigureInspectorController：启动时注册配置、Bean 或扩展点
2. AutoConfigureInspectorController：接收 HTTP 请求并转换成 Java 方法调用
3. DefaultGreetingService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/autoconfig`：模块说明
- `GET /api/autoconfig/properties`：查询绑定后的配置
- `GET /api/autoconfig/greet?name=java`：调用自动配置出来的服务

## 调用验证

```bash
curl "http://localhost:8145/api/autoconfig/properties"
```

```bash
curl "http://localhost:8145/api/autoconfig/greet?name=java"
```

## 生产映射

生产中的内部 starter 通常使用同样模式：

- 通过 `AutoConfiguration.imports` 注册自动配置
- 用 `@ConfigurationProperties` 承载配置
- 用 `@ConditionalOnProperty` 做功能开关
- 用 `@ConditionalOnMissingBean` 留出用户覆盖点
- 用 `ApplicationContextRunner` 做轻量上下文测试

## 生产差距

该示例用于隔离学习 自动配置检查器 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 65-SpringBoot-autoconfigure-inspector test
```

## 要点总结

1. `@AutoConfiguration`
2. `AutoConfiguration.imports`
3. `@ConfigurationProperties`
4. `@EnableConfigurationProperties`
5. `@ConditionalOnProperty`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
