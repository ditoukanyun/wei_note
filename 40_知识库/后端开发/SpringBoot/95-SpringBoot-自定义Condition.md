---
title: SpringBoot 自定义Condition
date: 2026-05-11
tags:
  - springboot
  - java
  - 条件装配
module: 95-SpringBoot-custom-condition
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 自定义Condition

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/95-SpringBoot-custom-condition`

## 核心思路

本模块演示 Spring 的自定义 `@Conditional`：通过组合注解把条件参数交给 `Condition`，再由 `ConditionContext` 读取环境配置，决定某个 BeanDefinition 是否应该注册。这是理解 Spring Boot 条件装配源码的基础路径。

## 能力点

- `@Conditional`
- custom composed condition annotation
- `Condition`
- `ConditionContext`
- `AnnotatedTypeMetadata`
- annotation attribute reading
- environment property matching
- `matchIfMissing`
- ApplicationContextRunner 验证条件 Bean 注册
- MockMvc 验证完整应用上下文中的条件报告

## 关键实现

组合注解：

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Conditional(DemoModeCondition.class)
public @interface ConditionalOnDemoMode {
    String value() default "enabled";
    String property() default "demo.condition.mode";
    boolean matchIfMissing() default false;
}
```

条件匹配：

```java
Map<String, Object> attributes =
        metadata.getAnnotationAttributes(ConditionalOnDemoMode.class.getName());
String actualMode = context.getEnvironment().getProperty(property);
```

这两个 API 是本模块的重点：`AnnotatedTypeMetadata` 代表正在被评估的注解元数据，`ConditionContext` 代表条件判断可访问的容器上下文。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 自定义Condition 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- Spring 扩展点案例先判断发生在启动生命周期的哪个阶段，再看具体代码。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/CustomConditionController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/CustomConditionController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/custom-condition")
public class CustomConditionController {
    private final DemoModeReportService demoModeReportService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CustomConditionController(DemoModeReportService demoModeReportService) {
        this.demoModeReportService = demoModeReportService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "95-SpringBoot-custom-condition",
                "topic", "Spring custom @Conditional annotation and Condition matching",
                "apis", List.of(
                        "GET /api/custom-condition",
                        "GET /api/custom-condition/report"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/report")
    public ApiResult<ModeReport> report() {
        return ApiResult.success(demoModeReportService.report());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/condition/DemoModeReportService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/condition/DemoModeReportService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class DemoModeReportService {
    private final Environment environment;
    private final List<ModeReporter> reporters;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DemoModeReportService(Environment environment, List<ModeReporter> reporters) {
        this.environment = environment;
        this.reporters = reporters;
    }

    public ModeReport report() {
        List<ModeReporter> activeReporters = reporters.stream()
                .sorted(Comparator.comparing(ModeReporter::name))
                .toList();
        return new ModeReport(
                environment.getProperty("demo.condition.mode", "missing"),
                activeReporters,
                activeReporters.size()
        );
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/condition/ConditionalOnDemoMode.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/condition/ConditionalOnDemoMode.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Conditional(DemoModeCondition.class)
public @interface ConditionalOnDemoMode {
    String value() default "enabled";

    String property() default "demo.condition.mode";

    boolean matchIfMissing() default false;
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 条件装配：Bean 是否创建由谁决定

源码位置：`src/main/java/com/cloud/condition/DemoModeCondition.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/condition/DemoModeCondition.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class DemoModeCondition implements Condition {
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        // Spring passes the attributes declared on the @Conditional metadata being evaluated.
        Map<String, Object> attributes = metadata.getAnnotationAttributes(ConditionalOnDemoMode.class.getName());
        if (attributes == null) {
            return false;
        }

        String property = (String) attributes.get("property");
        String expectedMode = (String) attributes.get("value");
        boolean matchIfMissing = (Boolean) attributes.get("matchIfMissing");
        String actualMode = context.getEnvironment().getProperty(property);

        if (!StringUtils.hasText(actualMode)) {
            return matchIfMissing;
        }
        return expectedMode.equalsIgnoreCase(actualMode.trim());
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
- 把框架扩展点当普通业务代码使用，后续排查启动问题会很困难。

## API 接口

- `GET /api/custom-condition`：模块说明
- `GET /api/custom-condition/report`：当前激活的条件 reporter

## 调用验证

```bash
curl "http://localhost:8175/api/custom-condition"
```

```bash
curl "http://localhost:8175/api/custom-condition/report"
```

`/report` 核心响应：

```json
{
  "configuredMode": "enabled",
  "reporterCount": 2,
  "reporters": [
    {
      "name": "enabled-mode-reporter",
      "mode": "enabled"
    },
    {
      "name": "missing-mode-reporter",
      "mode": "fallback"
    }
  ]
}
```

## 生产映射

自定义 `Condition` 适合框架层或 starter 层表达装配条件，例如：

- 根据配置开关注册某个能力；
- 根据注解参数复用一套条件判断；
- 给业务 starter 提供更贴近领域语义的条件注解；
- 阅读 `@ConditionalOnProperty`、`@ConditionalOnBean`、`@ConditionalOnClass` 等 Boot 条件源码。

如果需要详细的匹配/不匹配原因，Boot 的 `SpringBootCondition` 和 `ConditionOutcome` 会更适合；如果只需要一个轻量布尔判断，普通 Spring `Condition` 足够。

## 生产差距

该示例用于隔离学习 自定义Condition 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 95-SpringBoot-custom-condition test
```

测试覆盖：

- `demo.condition.mode=enabled` 时注册 enabled reporter，不注册 preview reporter
- `demo.condition.mode=preview` 时注册 preview reporter，不注册 enabled reporter
- 缺少 `demo.condition.optional-mode` 时通过 `matchIfMissing=true` 注册 fallback reporter
- MockMvc 验证 metadata 和 report 接口

## 要点总结

1. `@Conditional`
2. custom composed condition annotation
3. `Condition`
4. `ConditionContext`
5. `AnnotatedTypeMetadata`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
