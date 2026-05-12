---
title: SpringBoot SpringFactoriesLoader
date: 2026-05-11
tags:
  - springboot
  - java
module: 92-SpringBoot-spring-factories-loader
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot SpringFactoriesLoader

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/92-SpringBoot-spring-factories-loader`

## 核心思路

本模块演示 `SpringFactoriesLoader` 如何读取 `META-INF/spring.factories`：先发现实现类名，再按 SPI 类型实例化扩展对象。前面的环境后处理器、失败分析器、run listener 等模块都用过 `spring.factories`，本模块专门拆开 loader 本身。

## 能力点

- `SpringFactoriesLoader`
- `META-INF/spring.factories`
- `loadFactoryNames(...)`
- `loadFactories(...)`
- SPI key 到实现类列表的映射
- no-arg factory implementation
- `@Order` 控制实例顺序
- MockMvc 验证完整应用上下文中的 loader 结果

## 关键实现

读取 class names：

```java
List<String> factoryNames =
        SpringFactoriesLoader.loadFactoryNames(DemoFactoryExtension.class, classLoader);
```

实例化扩展：

```java
List<DemoFactoryExtension> extensions =
        SpringFactoriesLoader.loadFactories(DemoFactoryExtension.class, classLoader);
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot SpringFactoriesLoader 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/SpringFactoriesLoaderController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/SpringFactoriesLoaderController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/spring-factories-loader")
public class SpringFactoriesLoaderController {
    private final SpringFactoriesInspectionService inspectionService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SpringFactoriesLoaderController(SpringFactoriesInspectionService inspectionService) {
        this.inspectionService = inspectionService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "92-SpringBoot-spring-factories-loader",
                "topic", "SpringFactoriesLoader and META-INF/spring.factories discovery",
                "apis", List.of(
                        "GET /api/spring-factories-loader",
                        "GET /api/spring-factories-loader/summary"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/summary")
    public ApiResult<SpringFactoriesSummary> summary() {
        return ApiResult.success(inspectionService.summary());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/factories/SpringFactoriesInspectionService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/factories/SpringFactoriesInspectionService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
@SuppressWarnings("deprecation")
public class SpringFactoriesInspectionService {
    private final ClassLoader classLoader;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SpringFactoriesInspectionService() {
        this(SpringFactoriesInspectionService.class.getClassLoader());
    }

    SpringFactoriesInspectionService(ClassLoader classLoader) {
        this.classLoader = classLoader;
    }

    public SpringFactoriesSummary summary() {
        // This is the low-level source path behind many spring.factories extension points.
        List<String> factoryNames = SpringFactoriesLoader.loadFactoryNames(DemoFactoryExtension.class, classLoader);
        List<DemoFactoryExtension> extensions = SpringFactoriesLoader.loadFactories(DemoFactoryExtension.class, classLoader);
        List<String> extensionNames = extensions.stream().map(DemoFactoryExtension::name).toList();

        return new SpringFactoriesSummary(
                SpringFactoriesLoader.FACTORIES_RESOURCE_LOCATION,
                DemoFactoryExtension.class.getName(),
                factoryNames,
                extensionNames,
                extensionNames.size()
        );
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：AlphaFactoryExtension

源码位置：`src/main/java/com/cloud/factories/AlphaFactoryExtension.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/factories/AlphaFactoryExtension.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Order(10)
public class AlphaFactoryExtension implements DemoFactoryExtension {
    @Override
    public String name() {
        return "alpha";
    }

    @Override
    public String description() {
        return "alpha extension loaded from spring.factories";
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：BetaFactoryExtension

源码位置：`src/main/java/com/cloud/factories/BetaFactoryExtension.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/factories/BetaFactoryExtension.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Order(20)
public class BetaFactoryExtension implements DemoFactoryExtension {
    @Override
    public String name() {
        return "beta";
    }

    @Override
    public String description() {
        return "beta extension loaded from spring.factories";
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

- `GET /api/spring-factories-loader`：模块说明
- `GET /api/spring-factories-loader/summary`：返回 factory names 和已实例化 extensions

## 调用验证

```bash
curl "http://localhost:8172/api/spring-factories-loader"
```

```bash
curl "http://localhost:8172/api/spring-factories-loader/summary"
```

`/summary` 核心响应：

```json
{
  "resourceLocation": "META-INF/spring.factories",
  "factoryType": "com.cloud.factories.DemoFactoryExtension",
  "factoryNames": [
    "com.cloud.factories.AlphaFactoryExtension",
    "com.cloud.factories.BetaFactoryExtension"
  ],
  "extensionNames": ["alpha", "beta"],
  "extensionCount": 2
}
```

## 生产映射

`spring.factories` 是很多 Spring Boot 扩展点的发现机制，常见于早期启动 hook、失败分析、环境加工和 bootstrap 扩展。阅读源码时要区分两步：读取 class name 只是发现候选；实例化会要求实现类可加载、构造方式符合 loader 规则，并可能受到排序规则影响。

适合关注这个机制的场景：

- 排查扩展点为什么没有被加载
- 检查 classpath 上的多个 `spring.factories`
- 理解 Spring Boot 早期启动扩展点发现流程
- 编写框架级 SPI 而不是普通业务 Bean

普通应用内 Bean 装配不需要使用 `SpringFactoriesLoader`；优先使用 `@Bean`、条件装配或自动配置 imports。

## 生产差距

该示例用于隔离学习 SpringFactoriesLoader 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 92-SpringBoot-spring-factories-loader test
```

测试覆盖：

- `loadFactoryNames(...)` 读取两个实现类名
- `loadFactories(...)` 实例化两个扩展
- `@Order` 后扩展顺序为 `alpha`、`beta`
- MockMvc 验证 metadata 和 summary 接口

## 要点总结

1. `SpringFactoriesLoader`
2. `META-INF/spring.factories`
3. `loadFactoryNames(...)`
4. `loadFactories(...)`
5. SPI key 到实现类列表的映射

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
