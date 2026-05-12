---
title: SpringBoot SpringApplicationRunListener
date: 2026-05-11
tags:
  - springboot
  - java
module: 86-SpringBoot-run-listener
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot SpringApplicationRunListener

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/86-SpringBoot-run-listener`

## 核心思路

本模块演示 Spring Boot 的 `SpringApplicationRunListener`：在应用上下文创建 Bean 之前监听 `SpringApplication.run(...)` 的早期启动阶段。

## 能力点

- `SpringApplicationRunListener`
- `META-INF/spring.factories`
- 早期启动回调顺序
- `ConfigurableBootstrapContext`
- `ConfigurableEnvironment`
- context prepared / loaded / started / ready
- failed 回调诊断
- MockMvc 验证完整启动中 listener 已被触发

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot SpringApplicationRunListener 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/RunListenerController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/RunListenerController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/run-listener")
public class RunListenerController {
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "86-SpringBoot-run-listener",
                "topic", "SpringApplicationRunListener",
                "apis", List.of(
                        "GET /api/run-listener",
                        "GET /api/run-listener/events"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/events")
    public ApiResult<RunListenerSummary> events() {
        return ApiResult.success(RunListenerEventRecorder.summary());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/runlistener/DemoSpringApplicationRunListener.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runlistener/DemoSpringApplicationRunListener.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class DemoSpringApplicationRunListener implements SpringApplicationRunListener {
    private final String[] args;

    // SpringApplication constructs run listeners through spring.factories with this exact constructor.
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DemoSpringApplicationRunListener(SpringApplication application, String[] args) {
        this.args = args == null ? new String[0] : args.clone();
        RunListenerEventRecorder.record("constructed", "args=" + this.args.length);
    }

    @Override
    public void starting(ConfigurableBootstrapContext bootstrapContext) {
        RunListenerEventRecorder.record("starting", "bootstrapContext=available");
    }

    @Override
    public void environmentPrepared(ConfigurableBootstrapContext bootstrapContext, ConfigurableEnvironment environment) {
        RunListenerEventRecorder.record(
                "environment-prepared",
                "application=" + environment.getProperty("spring.application.name", "unknown")
        );
    }

    @Override
    public void contextPrepared(ConfigurableApplicationContext context) {
        RunListenerEventRecorder.record("context-prepared", "contextPrepared=true");
    }

    @Override
    public void contextLoaded(ConfigurableApplicationContext context) {
        RunListenerEventRecorder.record("context-loaded", "contextLoaded=true");
    }

    @Override
    public void started(ConfigurableApplicationContext context, Duration timeTaken) {
        RunListenerEventRecorder.record("started", "timeTakenMs=" + toMillis(timeTaken));
    }

    @Override
    public void ready(ConfigurableApplicationContext context, Duration timeTaken) {
        RunListenerEventRecorder.record("ready", "timeTakenMs=" + toMillis(timeTaken));
    }

    @Override
    public void failed(ConfigurableApplicationContext context, Throwable exception) {
        RunListenerEventRecorder.record("failed", exception.getClass().getSimpleName() + ": " + exception.getMessage());
    }

    private long toMillis(Duration duration) {
        return duration == null ? -1 : duration.toMillis();
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/runlistener/RunListenerEvent.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runlistener/RunListenerEvent.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RunListenerEvent {
    private int sequence;
    private String stage;
    private String detail;
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/runlistener/RunListenerEventRecorder.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runlistener/RunListenerEventRecorder.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public final class RunListenerEventRecorder {
    private static final AtomicInteger SEQUENCE = new AtomicInteger();
    private static final List<RunListenerEvent> EVENTS = new CopyOnWriteArrayList<>();

    private RunListenerEventRecorder() {
    }

    public static void reset() {
        EVENTS.clear();
        SEQUENCE.set(0);
    }

    public static void record(String stage, String detail) {
        EVENTS.add(new RunListenerEvent(SEQUENCE.incrementAndGet(), stage, detail));
    }

    public static List<RunListenerEvent> snapshot() {
        return new ArrayList<>(EVENTS);
    }

    public static RunListenerSummary summary() {
        List<RunListenerEvent> events = snapshot();
        return new RunListenerSummary(events.size(), events);
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

- `GET /api/run-listener`：模块说明
- `GET /api/run-listener/events`：已记录的 run listener events

## 调用验证

```bash
curl "http://localhost:8166/api/run-listener"
```

```bash
curl "http://localhost:8166/api/run-listener/events"
```

`/events` 核心响应：

```json
{
  "eventCount": 7,
  "events": [
    {
      "sequence": 1,
      "stage": "constructed",
      "detail": "args=0"
    },
    {
      "sequence": 2,
      "stage": "starting",
      "detail": "bootstrapContext=available"
    }
  ]
}
```

## 生产映射

生产系统可以用这个模式：

- 在 Spring Bean 创建前采集启动诊断
- 为内部框架或 starter 插入最早期启动钩子
- 区分 `SpringApplicationRunListener`、`ApplicationListener`、runner 和 lifecycle 的执行位置
- 学习 Spring Boot 源码中 `SpringApplicationRunListeners` 的调用链

如果只是业务初始化，优先用 `ApplicationRunner` 或 `SmartLifecycle`；如果必须早于 Environment/context 普通 Bean 阶段，才考虑 run listener。

## 生产差距

该示例用于隔离学习 SpringApplicationRunListener 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 86-SpringBoot-run-listener test
```

测试覆盖：

- 直接调用 listener 回调并验证阶段顺序
- `failed` 回调记录异常类型和消息
- MockMvc 验证 metadata 接口
- MockMvc 验证完整 Spring Boot 测试启动触发了 `spring.factories` 中注册的 listener

## 要点总结

1. `SpringApplicationRunListener`
2. `META-INF/spring.factories`
3. 早期启动回调顺序
4. `ConfigurableBootstrapContext`
5. `ConfigurableEnvironment`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
