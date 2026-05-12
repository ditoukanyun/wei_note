---
title: SpringBoot Runner执行顺序
date: 2026-05-11
tags:
  - springboot
  - java
  - 启动流程
module: 78-SpringBoot-runner-ordering
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot Runner执行顺序

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/78-SpringBoot-runner-ordering`

## 核心思路

本模块演示 Spring Boot 启动末段的两个 runner：`ApplicationRunner` 和 `CommandLineRunner`。

## 能力点

- `ApplicationRunner`
- `CommandLineRunner`
- `@Order`
- `ApplicationArguments`
- 原始命令行参数
- 启动 runner 执行记录
- MockMvc 验证真实启动参数

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Runner执行顺序 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/RunnerOrderingController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/RunnerOrderingController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/runner-ordering")
public class RunnerOrderingController {
    private final RunnerExecutionRecorder recorder;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RunnerOrderingController(RunnerExecutionRecorder recorder) {
        this.recorder = recorder;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "78-SpringBoot-runner-ordering",
                "apis", List.of(
                        "GET /api/runner-ordering",
                        "GET /api/runner-ordering/executions"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/executions")
    public ApiResult<List<RunnerExecutionRecord>> executions() {
        return ApiResult.success(recorder.snapshot());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 启动回调：应用启动后执行什么

源码位置：`src/main/java/com/cloud/runner/ApplicationArgumentsStartupRunner.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runner/ApplicationArgumentsStartupRunner.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
@Order(10)
public class ApplicationArgumentsStartupRunner implements ApplicationRunner {
    private final RunnerExecutionRecorder recorder;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ApplicationArgumentsStartupRunner(RunnerExecutionRecorder recorder) {
        this.recorder = recorder;
    }

    @Override
    public void run(ApplicationArguments args) {
        // ApplicationRunner receives Spring Boot's parsed ApplicationArguments view.
        List<String> optionNames = new ArrayList<>(args.getOptionNames());
        optionNames.sort(String::compareTo);

        Map<String, List<String>> optionValues = new LinkedHashMap<>();
        for (String optionName : optionNames) {
            List<String> values = args.getOptionValues(optionName);
            optionValues.put(optionName, values == null ? List.of() : List.copyOf(values));
        }

        recorder.record(new RunnerExecutionRecord(
                "ApplicationRunner",
                10,
                Arrays.asList(args.getSourceArgs()),
                optionNames,
                optionValues
        ));
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 启动回调：应用启动后执行什么

源码位置：`src/main/java/com/cloud/runner/RawArgumentsStartupRunner.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runner/RawArgumentsStartupRunner.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
@Order(20)
public class RawArgumentsStartupRunner implements CommandLineRunner {
    private final RunnerExecutionRecorder recorder;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RawArgumentsStartupRunner(RunnerExecutionRecorder recorder) {
        this.recorder = recorder;
    }

    @Override
    public void run(String... args) {
        // CommandLineRunner receives the raw String array after SpringApplication starts.
        recorder.record(new RunnerExecutionRecord(
                "CommandLineRunner",
                20,
                Arrays.asList(args),
                List.of(),
                Map.of()
        ));
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 启动回调：应用启动后执行什么

源码位置：`src/main/java/com/cloud/runner/RunnerExecutionRecord.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/runner/RunnerExecutionRecord.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public record RunnerExecutionRecord(
        String runnerType,
        int orderNo,
        List<String> sourceArgs,
        List<String> optionNames,
        Map<String, List<String>> optionValues
) {
    public RunnerExecutionRecord {
        sourceArgs = List.copyOf(sourceArgs);
        optionNames = List.copyOf(optionNames);

        Map<String, List<String>> copiedValues = new LinkedHashMap<>();
        optionValues.forEach((key, value) -> copiedValues.put(key, List.copyOf(value)));
        optionValues = Collections.unmodifiableMap(copiedValues);
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

- `GET /api/runner-ordering`：模块说明
- `GET /api/runner-ordering/executions`：返回 runner 执行记录

## 调用验证

```bash
curl "http://localhost:8158/api/runner-ordering"
```

```bash
curl "http://localhost:8158/api/runner-ordering/executions"
```

## 生产映射

生产系统可以用这个模式：

- 用 `ApplicationRunner` 处理命名参数和可重复 option
- 用 `CommandLineRunner` 保留最原始的命令行输入
- 用 `@Order` 固定多个启动任务的执行顺序
- 暴露启动诊断接口确认 runner 是否执行过

如果需要应用 ready 前后的事件时间线，看 66；如果只关心 runner 入参模型和排序，看 78。

## 生产差距

该示例用于隔离学习 Runner执行顺序 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 78-SpringBoot-runner-ordering test
```

测试覆盖：

- `ApplicationArgumentsStartupRunner` 记录解析后的 option 名称和值
- `RawArgumentsStartupRunner` 记录原始参数
- recorder 返回不可变快照
- MockMvc 使用 `@SpringBootTest(args = ...)` 验证真实 Boot 启动后两个 runner 的顺序和接口输出

## 要点总结

1. `ApplicationRunner`
2. `CommandLineRunner`
3. `@Order`
4. `ApplicationArguments`
5. 原始命令行参数

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
