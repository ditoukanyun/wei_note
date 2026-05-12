---
title: SpringBoot SmartLifecycle
date: 2026-05-11
tags:
  - springboot
  - java
  - 生命周期
module: 79-SpringBoot-smart-lifecycle
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot SmartLifecycle

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/79-SpringBoot-smart-lifecycle`

## 核心思路

本模块演示 `SmartLifecycle`：Spring 容器启动和停止阶段的自动生命周期管理、phase 排序、运行状态和 `stop(Runnable)` 回调。

## 能力点

- `SmartLifecycle`
- `isAutoStartup`
- `getPhase`
- `start`
- `stop`
- `stop(Runnable)`
- 启动顺序和停止顺序预览
- MockMvc 验证真实 Spring Boot 自动启动事件

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot SmartLifecycle 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/SmartLifecycleController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/SmartLifecycleController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/smart-lifecycle")
public class SmartLifecycleController {
    private final LifecycleEventRecorder recorder;
    private final LifecyclePhaseInspector inspector;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SmartLifecycleController(LifecycleEventRecorder recorder, LifecyclePhaseInspector inspector) {
        this.recorder = recorder;
        this.inspector = inspector;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "79-SpringBoot-smart-lifecycle",
                "apis", List.of(
                        "GET /api/smart-lifecycle",
                        "GET /api/smart-lifecycle/components",
                        "GET /api/smart-lifecycle/events"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/components")
    public ApiResult<Map<String, List<LifecycleComponentStatus>>> components() {
        return ApiResult.success(Map.of(
                "startOrder", inspector.startOrder(),
                "stopOrderPreview", inspector.stopOrderPreview()
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/events")
    public ApiResult<List<LifecycleEventRecord>> events() {
        return ApiResult.success(recorder.snapshot());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：AbstractProbeLifecycle

源码位置：`src/main/java/com/cloud/lifecycle/AbstractProbeLifecycle.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/lifecycle/AbstractProbeLifecycle.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public abstract class AbstractProbeLifecycle implements SmartLifecycleProbe {
    private final LifecycleEventRecorder recorder;
    private final String componentName;
    private final int phase;
    private volatile boolean running;

    protected AbstractProbeLifecycle(LifecycleEventRecorder recorder, String componentName, int phase) {
        this.recorder = recorder;
        this.componentName = componentName;
        this.phase = phase;
    }

    @Override
    public void start() {
        this.running = true;
        recorder.record(new LifecycleEventRecord(componentName, "start", phase, true));
    }

    @Override
    public void stop() {
        this.running = false;
        recorder.record(new LifecycleEventRecord(componentName, "stop", phase, false));
    }

    @Override
    public void stop(Runnable callback) {
        // SmartLifecycle uses this callback to signal that graceful stop work is finished.
        stop();
        callback.run();
    }

    @Override
    public boolean isRunning() {
        return running;
    }

    @Override
    public boolean isAutoStartup() {
        return true;
    }

    @Override
    public int getPhase() {
        return phase;
    }

    @Override
    public String componentName() {
        return componentName;
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：CacheWarmupLifecycle

源码位置：`src/main/java/com/cloud/lifecycle/CacheWarmupLifecycle.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/lifecycle/CacheWarmupLifecycle.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
public class CacheWarmupLifecycle extends AbstractProbeLifecycle {
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CacheWarmupLifecycle(LifecycleEventRecorder recorder) {
        super(recorder, "cacheWarmupLifecycle", 0);
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：LifecycleComponentStatus

源码位置：`src/main/java/com/cloud/lifecycle/LifecycleComponentStatus.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/lifecycle/LifecycleComponentStatus.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public record LifecycleComponentStatus(
        String componentName,
        int phase,
        boolean running,
        boolean autoStartup
) {
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

- `GET /api/smart-lifecycle`：模块说明
- `GET /api/smart-lifecycle/components`：组件状态、启动顺序、停止顺序预览
- `GET /api/smart-lifecycle/events`：生命周期事件记录

## 调用验证

```bash
curl "http://localhost:8159/api/smart-lifecycle"
```

```bash
curl "http://localhost:8159/api/smart-lifecycle/components"
```

```bash
curl "http://localhost:8159/api/smart-lifecycle/events"
```

## 生产映射

生产系统可以用这个模式：

- 先启动底层缓存预热，再启动消息消费者
- 停止时先停消费者，再停底层依赖
- 用 phase 固定多个生命周期组件的启动和停止顺序
- 用 `stop(Runnable)` 表达异步或优雅停机完成信号

如果只需要启动后执行一次任务，看 78 的 runner；如果要参与容器启动和关闭生命周期，看 79 的 `SmartLifecycle`。

## 生产差距

该示例用于隔离学习 SmartLifecycle 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 79-SpringBoot-smart-lifecycle test
```

测试覆盖：

- phase、autoStartup、running 状态
- `start()` 和 `stop()` 事件记录
- `stop(Runnable)` 回调执行
- start 升序、stop 降序排序
- MockMvc 验证 Spring Boot 自动启动后的事件和组件状态

## 要点总结

1. `SmartLifecycle`
2. `isAutoStartup`
3. `getPhase`
4. `start`
5. `stop`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
