---
title: SpringBoot BootstrapRegistry
date: 2026-05-11
tags:
  - springboot
  - java
module: 87-SpringBoot-bootstrap-registry
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot BootstrapRegistry

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/87-SpringBoot-bootstrap-registry`

## 核心思路

本模块演示 Spring Boot 的 `BootstrapRegistryInitializer` 和 `BootstrapRegistry`：在普通 Spring Bean 创建之前注册早期对象，并监听 bootstrap context close。

## 能力点

- `BootstrapRegistryInitializer`
- `BootstrapRegistry`
- `DefaultBootstrapContext`
- `BootstrapContextClosedEvent`
- `META-INF/spring.factories`
- bootstrap close listener
- MockMvc 验证完整启动中 initializer 已被触发

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot BootstrapRegistry 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/BootstrapRegistryController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/BootstrapRegistryController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/bootstrap-registry")
public class BootstrapRegistryController {
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "87-SpringBoot-bootstrap-registry",
                "topic", "Spring Boot BootstrapRegistryInitializer",
                "apis", List.of(
                        "GET /api/bootstrap-registry",
                        "GET /api/bootstrap-registry/events"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/events")
    public ApiResult<BootstrapRegistrySummary> events() {
        return ApiResult.success(BootstrapRegistryEventRecorder.summary());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 上下文初始化：刷新容器前做什么

源码位置：`src/main/java/com/cloud/bootstrap/DemoBootstrapRegistryInitializer.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/bootstrap/DemoBootstrapRegistryInitializer.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class DemoBootstrapRegistryInitializer implements BootstrapRegistryInitializer {
    @Override
    public void initialize(BootstrapRegistry registry) {
        BootstrapRegistryEventRecorder.record("initializer-called", "registry=available");
        registry.register(BootstrapDemoClient.class, context ->
                new BootstrapDemoClient("demo-bootstrap-client", "BootstrapRegistryInitializer"));
        BootstrapRegistryEventRecorder.record("client-registered", "type=BootstrapDemoClient");
        registry.addCloseListener(event -> {
            BootstrapDemoClient client = event.getBootstrapContext().get(BootstrapDemoClient.class);
            BootstrapRegistryEventRecorder.record("bootstrap-closed", "client=" + client.getName());
        });
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：BootstrapDemoClient

源码位置：`src/main/java/com/cloud/bootstrap/BootstrapDemoClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/bootstrap/BootstrapDemoClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class BootstrapDemoClient {
    private String name;
    private String source;
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

## API 接口

- `GET /api/bootstrap-registry`：模块说明
- `GET /api/bootstrap-registry/events`：已记录的 bootstrap registry events

## 调用验证

```bash
curl "http://localhost:8167/api/bootstrap-registry"
```

```bash
curl "http://localhost:8167/api/bootstrap-registry/events"
```

`/events` 核心响应：

```json
{
  "eventCount": 3,
  "events": [
    {
      "stage": "initializer-called",
      "detail": "registry=available"
    },
    {
      "stage": "client-registered",
      "detail": "type=BootstrapDemoClient"
    },
    {
      "stage": "bootstrap-closed",
      "detail": "client=demo-bootstrap-client"
    }
  ]
}
```

## 生产映射

生产系统可以用这个模式：

- 在 application context 创建前准备早期客户端
- 给框架启动流程共享 bootstrap-time 对象
- 在 bootstrap context 关闭时做诊断或转移状态
- 阅读 Spring Boot 源码时理解 bootstrap registry 和 run listener 的边界

如果只是普通业务 Bean 初始化，使用 `@Bean`、`ApplicationRunner` 或 `SmartLifecycle` 更合适；只有需要早于 application context 的对象注册时才使用 bootstrap registry。

## 生产差距

该示例用于隔离学习 BootstrapRegistry 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 87-SpringBoot-bootstrap-registry test
```

测试覆盖：

- 直接调用 initializer 注册 `BootstrapDemoClient`
- `DefaultBootstrapContext.close(...)` 触发 close listener
- MockMvc 验证 metadata 接口
- MockMvc 验证完整 Spring Boot 启动触发了 `spring.factories` 中注册的 initializer

## 要点总结

1. `BootstrapRegistryInitializer`
2. `BootstrapRegistry`
3. `DefaultBootstrapContext`
4. `BootstrapContextClosedEvent`
5. `META-INF/spring.factories`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
