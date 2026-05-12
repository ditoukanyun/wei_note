---
title: SpringBoot ApplicationStartup
date: 2026-05-11
tags:
  - springboot
  - java
module: 84-SpringBoot-application-startup
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ApplicationStartup

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/84-SpringBoot-application-startup`

## 核心思路

本模块演示 Spring 的 `ApplicationStartup`、`StartupStep`，以及 Spring Boot 的 `BufferingApplicationStartup`：用可控的启动步骤记录理解 Boot 启动诊断机制。

## 能力点

- `ApplicationStartup`
- `StartupStep`
- `BufferingApplicationStartup`
- `StartupTimeline`
- step name 和 tags
- startup step filter
- MockMvc 验证 API 输出

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ApplicationStartup 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ApplicationStartupController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ApplicationStartupController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/application-startup")
public class ApplicationStartupController {
    private final ApplicationStartupDemoService applicationStartupDemoService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ApplicationStartupController(ApplicationStartupDemoService applicationStartupDemoService) {
        this.applicationStartupDemoService = applicationStartupDemoService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "84-SpringBoot-application-startup",
                "topic", "Spring ApplicationStartup and StartupStep",
                "apis", List.of(
                        "GET /api/application-startup",
                        "GET /api/application-startup/timeline",
                        "GET /api/application-startup/filtered"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/timeline")
    public ApiResult<StartupTimelineView> timeline() {
        return ApiResult.success(applicationStartupDemoService.recordDemoTimeline());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/filtered")
    public ApiResult<StartupTimelineView> filtered() {
        return ApiResult.success(applicationStartupDemoService.recordFilteredTimeline());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/startup/ApplicationStartupDemoService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/startup/ApplicationStartupDemoService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ApplicationStartupDemoService {
    public StartupTimelineView recordDemoTimeline() {
        // Real applications normally pass this to SpringApplication.setApplicationStartup(...).
        BufferingApplicationStartup startup = new BufferingApplicationStartup(16);
        startup.startRecording();

        recordStep(startup, "demo.config-load", Map.of("phase", "config"));
        recordStep(startup, "demo.bean-warmup", Map.of("phase", "beans"));

        return toView(startup.getBufferedTimeline());
    }

    public StartupTimelineView recordFilteredTimeline() {
        BufferingApplicationStartup startup = new BufferingApplicationStartup(16);
        startup.addFilter(step -> step.getName().startsWith("demo."));
        startup.startRecording();

        recordStep(startup, "demo.visible-step", Map.of("filter", "kept"));
        recordStep(startup, "spring.ignored-step", Map.of("filter", "ignored"));

        return toView(startup.getBufferedTimeline());
    }

    private void recordStep(BufferingApplicationStartup startup, String name, Map<String, String> tags) {
        StartupStep step = startup.start(name);
        tags.forEach(step::tag);
        step.end();
    }

    private StartupTimelineView toView(StartupTimeline timeline) {
        List<StartupStepView> events = timeline.getEvents().stream()
                .map(this::toView)
                .toList();
        return new StartupTimelineView(events.size(), events);
    }

    private StartupStepView toView(StartupTimeline.TimelineEvent event) {
        StartupStep startupStep = event.getStartupStep();
        return new StartupStepView(
                startupStep.getName(),
                startupStep.getId(),
                startupStep.getParentId(),
                tagsToMap(startupStep.getTags()),
                event.getDuration().toMillis()
        );
    }

    private Map<String, String> tagsToMap(StartupStep.Tags tags) {
        Map<String, String> result = new LinkedHashMap<>();
        for (StartupStep.Tag tag : tags) {
            result.put(tag.getKey(), tag.getValue());
        }
        return result;
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

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/application-startup`：模块说明
- `GET /api/application-startup/timeline`：返回两个 demo startup steps
- `GET /api/application-startup/filtered`：返回 filter 后的 startup steps

## 调用验证

```bash
curl "http://localhost:8164/api/application-startup"
```

```bash
curl "http://localhost:8164/api/application-startup/timeline"
```

```bash
curl "http://localhost:8164/api/application-startup/filtered"
```

`/timeline` 核心响应：

```json
{
  "eventCount": 2,
  "events": [
    {
      "name": "demo.config-load",
      "tags": {
        "phase": "config"
      }
    },
    {
      "name": "demo.bean-warmup",
      "tags": {
        "phase": "beans"
      }
    }
  ]
}
```

## 生产映射

生产系统可以用这个模式：

- 定位启动慢的 Bean、自动配置或初始化阶段
- 给关键启动步骤打标签，辅助排查环境差异
- 过滤掉噪声 step，只保留业务或框架关心的启动阶段
- 阅读 Spring Boot 源码时理解 `StartupStep` 如何贯穿启动流程

如果只是业务日志，普通 logger 更直接；如果要分析应用启动链路和阶段耗时，`ApplicationStartup` 更贴近框架机制。

## 生产差距

该示例用于隔离学习 ApplicationStartup 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 84-SpringBoot-application-startup test
```

测试覆盖：

- demo timeline 记录两个命名 startup steps
- step tags 被保留到 DTO
- filter 排除非 `demo.` step
- MockMvc 验证 metadata、timeline、filtered 三个接口

## 要点总结

1. `ApplicationStartup`
2. `StartupStep`
3. `BufferingApplicationStartup`
4. `StartupTimeline`
5. step name 和 tags

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
