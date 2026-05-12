---
title: SpringBoot ApplicationContextInitializer
date: 2026-05-11
tags:
  - springboot
  - java
module: 73-SpringBoot-application-context-initializer
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ApplicationContextInitializer

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/73-SpringBoot-application-context-initializer`

## 核心思路

本模块演示 Spring Boot 启动流程中的 `ApplicationContextInitializer`：应用上下文已经创建，但还没有 refresh，此时可以读取环境信息并注册早期单例。

## 能力点

- `ApplicationContextInitializer`
- `ConfigurableApplicationContext`
- refresh 前注册 singleton
- `META-INF/spring.factories`
- active profile 读取
- 启动期元数据进入普通依赖注入

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ApplicationContextInitializer 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- Spring 扩展点案例先判断发生在启动生命周期的哪个阶段，再看具体代码。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ContextInitializerController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ContextInitializerController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/context-initializer")
public class ContextInitializerController {
    private final StartupMarker startupMarker;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ContextInitializerController(StartupMarker startupMarker) {
        this.startupMarker = startupMarker;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "73-SpringBoot-application-context-initializer",
                "apis", List.of(
                        "GET /api/context-initializer",
                        "GET /api/context-initializer/marker"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/marker")
    public ApiResult<StartupMarker> marker() {
        return ApiResult.success(startupMarker);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 上下文初始化：刷新容器前做什么

源码位置：`src/main/java/com/cloud/initializer/StartupMarkerInitializer.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/initializer/StartupMarkerInitializer.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class StartupMarkerInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    public static final String BEAN_NAME = "startupMarker";

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        StartupMarker marker = new StartupMarker(
                "application-context-initializer",
                applicationContext.getEnvironment().getProperty("spring.application.name", "unknown"),
                activeProfiles(applicationContext),
                applicationContext.getClass().getName(),
                "before-refresh"
        );

        // ApplicationContextInitializer runs before refresh, so this singleton is available to normal beans later.
        applicationContext.getBeanFactory().registerSingleton(BEAN_NAME, marker);
    }

    private List<String> activeProfiles(ConfigurableApplicationContext applicationContext) {
        String[] activeProfiles = applicationContext.getEnvironment().getActiveProfiles();
        if (activeProfiles.length == 0) {
            return List.of("default");
        }
        return Arrays.asList(activeProfiles);
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
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

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。
- 使用 `ThreadLocal` 后忘记清理，在线程池环境会造成上下文串号。

## API 接口

- `GET /api/context-initializer`：模块说明
- `GET /api/context-initializer/marker`：返回 refresh 前注册的 marker

## 调用验证

```bash
curl "http://localhost:8153/api/context-initializer"
```

```bash
curl "http://localhost:8153/api/context-initializer/marker"
```

使用 profile：

```bash
mvn -pl 73-SpringBoot-application-context-initializer spring-boot:run \
  -Dspring-boot.run.profiles=dev
```

## 生产映射

生产系统可以用这个模式：

- 注册轻量启动标记对象
- 把 context 创建阶段的环境信息转成可注入对象
- 初始化不依赖其他 Bean 的基础设施数据
- 在 refresh 前准备后续 Bean 会使用的简单元数据

复杂 Bean 定义改写应交给 `BeanFactoryPostProcessor` 或 `BeanDefinitionRegistryPostProcessor`，不要塞进 initializer。

## 生产差距

该示例用于隔离学习 ApplicationContextInitializer 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 73-SpringBoot-application-context-initializer test
```

测试覆盖：

- 直接调用 initializer 注册 `startupMarker`
- application name 和 active profiles 读取
- `spring.factories` 注册内容
- Spring Boot 启动时加载 initializer
- controller 注入并返回 `StartupMarker`

## 要点总结

1. `ApplicationContextInitializer`
2. `ConfigurableApplicationContext`
3. refresh 前注册 singleton
4. `META-INF/spring.factories`
5. active profile 读取

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
