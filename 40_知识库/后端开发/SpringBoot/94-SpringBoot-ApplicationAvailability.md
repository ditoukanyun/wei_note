---
title: SpringBoot ApplicationAvailability
date: 2026-05-11
tags:
  - springboot
  - java
module: 94-SpringBoot-application-availability
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ApplicationAvailability

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/94-SpringBoot-application-availability`

## 核心思路

本模块演示 Spring Boot 的 `ApplicationAvailability`：通过 `AvailabilityChangeEvent` 发布运行时可用性变化，再由 `ApplicationAvailabilityBean` 记录最新的 liveness/readiness 状态。它和前面的 Actuator 健康探针模块不同，本模块聚焦 Boot 内部的 availability 状态模型和事件更新链路。

## 能力点

- `ApplicationAvailability`
- `ApplicationAvailabilityBean`
- `AvailabilityChangeEvent`
- `ReadinessState`
- `LivenessState`
- readiness traffic draining
- liveness broken signaling
- ApplicationContextRunner 验证事件发布后的状态变化
- MockMvc 验证完整应用上下文中的状态变更接口

## 关键实现

```java
AvailabilityChangeEvent.publish(eventPublisher, this, ReadinessState.REFUSING_TRAFFIC);
AvailabilityChangeEvent.publish(eventPublisher, this, ReadinessState.ACCEPTING_TRAFFIC);
AvailabilityChangeEvent.publish(eventPublisher, this, LivenessState.BROKEN);
```

这个调用是理解 Boot 可用性模型的关键：状态不是直接写入 `ApplicationAvailability`，而是通过事件发布，再由 `ApplicationAvailabilityBean` 维护最新状态。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ApplicationAvailability 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ApplicationAvailabilityController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ApplicationAvailabilityController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/application-availability")
public class ApplicationAvailabilityController {
    private final AvailabilityStateService availabilityStateService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ApplicationAvailabilityController(AvailabilityStateService availabilityStateService) {
        this.availabilityStateService = availabilityStateService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "94-SpringBoot-application-availability",
                "topic", "Spring Boot ApplicationAvailability and AvailabilityChangeEvent",
                "apis", List.of(
                        "GET /api/application-availability",
                        "GET /api/application-availability/state",
                        "POST /api/application-availability/readiness/refuse",
                        "POST /api/application-availability/readiness/accept",
                        "POST /api/application-availability/liveness/break"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/state")
    public ApiResult<AvailabilitySnapshot> state() {
        return ApiResult.success(availabilityStateService.snapshot());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/readiness/refuse")
    public ApiResult<AvailabilitySnapshot> refuseTraffic() {
        return ApiResult.success(availabilityStateService.refuseTraffic());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/readiness/accept")
    public ApiResult<AvailabilitySnapshot> acceptTraffic() {
        return ApiResult.success(availabilityStateService.acceptTraffic());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/liveness/break")
    public ApiResult<AvailabilitySnapshot> breakLiveness() {
        return ApiResult.success(availabilityStateService.breakLiveness());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/availability/AvailabilityStateService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/availability/AvailabilityStateService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class AvailabilityStateService {
    private final ApplicationAvailability availability;
    private final ApplicationEventPublisher eventPublisher;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public AvailabilityStateService(ApplicationAvailability availability, ApplicationEventPublisher eventPublisher) {
        this.availability = availability;
        this.eventPublisher = eventPublisher;
    }

    public AvailabilitySnapshot snapshot() {
        return new AvailabilitySnapshot(
                availability.getLivenessState().name(),
                availability.getReadinessState().name(),
                lastChange(LivenessState.class),
                lastChange(ReadinessState.class)
        );
    }

    public AvailabilitySnapshot refuseTraffic() {
        // Boot availability changes are event-driven; ApplicationAvailabilityBean records the latest event.
        AvailabilityChangeEvent.publish(eventPublisher, this, ReadinessState.REFUSING_TRAFFIC);
        return snapshot();
    }

    public AvailabilitySnapshot acceptTraffic() {
        AvailabilityChangeEvent.publish(eventPublisher, this, ReadinessState.ACCEPTING_TRAFFIC);
        return snapshot();
    }

    public AvailabilitySnapshot breakLiveness() {
        AvailabilityChangeEvent.publish(eventPublisher, this, LivenessState.BROKEN);
        return snapshot();
    }

    private <S extends AvailabilityState> String lastChange(Class<S> stateType) {
        AvailabilityChangeEvent<S> event = availability.getLastChangeEvent(stateType);
        return event == null ? "none" : event.getState().toString();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/availability/AvailabilityDemoConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/availability/AvailabilityDemoConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class AvailabilityDemoConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    // 只有容器里还没有同类型 Bean 时才创建默认实现，给业务方留下覆盖点。
    @ConditionalOnMissingBean(ApplicationAvailability.class)
    ApplicationAvailabilityBean applicationAvailability() {
        return new ApplicationAvailabilityBean();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    AvailabilityStateService availabilityStateService(ApplicationAvailability availability,
                                                      ApplicationEventPublisher eventPublisher) {
        return new AvailabilityStateService(availability, eventPublisher);
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

1. AvailabilityDemoConfig：启动时注册配置、Bean 或扩展点
2. ApplicationAvailabilityController：接收 HTTP 请求并转换成 Java 方法调用
3. AvailabilityStateService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/application-availability`：模块说明
- `GET /api/application-availability/state`：当前 liveness/readiness 快照
- `POST /api/application-availability/readiness/refuse`：发布拒绝流量状态
- `POST /api/application-availability/readiness/accept`：发布接受流量状态
- `POST /api/application-availability/liveness/break`：发布 liveness broken 状态

## 调用验证

```bash
curl "http://localhost:8174/api/application-availability"
```

```bash
curl "http://localhost:8174/api/application-availability/state"
```

```bash
curl -X POST "http://localhost:8174/api/application-availability/readiness/refuse"
```

readiness refusal 核心响应：

```json
{
  "livenessState": "CORRECT",
  "readinessState": "REFUSING_TRAFFIC",
  "lastLivenessChange": "none",
  "lastReadinessChange": "REFUSING_TRAFFIC"
}
```

## 生产映射

`ApplicationAvailability` 适合表达应用运行时状态，而不是替代业务监控。典型使用场景包括：

- 关闭前先把 readiness 改为 `REFUSING_TRAFFIC`，让负载均衡停止转发新请求；
- 依赖严重降级时临时拒绝流量，保留进程继续运行和恢复机会；
- 检测到不可恢复的内部状态时发布 `LivenessState.BROKEN`；
- 阅读 Boot actuator health probe、kubernetes probe 和 graceful shutdown 相关源码。

生产里不要把普通业务异常直接映射为 broken liveness。liveness 更适合表达“当前进程已经无法自我恢复”，readiness 更适合表达“当前进程暂时不应该接流量”。

## 生产差距

该示例用于隔离学习 ApplicationAvailability 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 94-SpringBoot-application-availability test
```

测试覆盖：

- 发布 readiness refusal 后状态变为 `REFUSING_TRAFFIC`
- 发布 readiness acceptance 后状态变为 `ACCEPTING_TRAFFIC`
- 发布 liveness broken 后状态变为 `BROKEN`
- MockMvc 验证 metadata、readiness refusal 和 liveness broken 接口

## 要点总结

1. `ApplicationAvailability`
2. `ApplicationAvailabilityBean`
3. `AvailabilityChangeEvent`
4. `ReadinessState`
5. `LivenessState`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
