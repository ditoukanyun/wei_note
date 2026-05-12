---
title: SpringBoot ExitCode
date: 2026-05-11
tags:
  - springboot
  - java
module: 80-SpringBoot-exit-code
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ExitCode

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/80-SpringBoot-exit-code`

## 核心思路

本模块演示 Spring Boot 的退出码机制：`ExitCodeGenerator`、`ExitCodeExceptionMapper` 和 `SpringApplication.exit(...)`。

## 能力点

- `ExitCodeGenerator`
- `ExitCodeExceptionMapper`
- `SpringApplication.exit(...)`
- 异常到退出码的稳定映射
- 安全的退出码场景评估
- MockMvc 验证 API 输出

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ExitCode 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ExitCodeController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ExitCodeController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/exit-code")
public class ExitCodeController {
    private final ExitCodeEvaluationService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ExitCodeController(ExitCodeEvaluationService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "80-SpringBoot-exit-code",
                "apis", List.of(
                        "GET /api/exit-code",
                        "GET /api/exit-code/scenarios",
                        "GET /api/exit-code/evaluate/{scenario}"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/scenarios")
    public ApiResult<List<ExitScenarioDescriptor>> scenarios() {
        return ApiResult.success(service.scenarios());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/evaluate/{scenario}")
    public ApiResult<ExitCodeReport> evaluate(@PathVariable String scenario) {
        return ApiResult.success(service.evaluate(scenario));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/exitcode/ExitCodeEvaluationService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/exitcode/ExitCodeEvaluationService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ExitCodeEvaluationService {
    private final MaintenanceExitCodeGenerator maintenanceExitCodeGenerator;
    private final ExitCodePolicy exitCodePolicy;

    public ExitCodeEvaluationService(MaintenanceExitCodeGenerator maintenanceExitCodeGenerator,
                                     ExitCodePolicy exitCodePolicy) {
        this.maintenanceExitCodeGenerator = maintenanceExitCodeGenerator;
        this.exitCodePolicy = exitCodePolicy;
    }

    public List<ExitScenarioDescriptor> scenarios() {
        return List.of(
                new ExitScenarioDescriptor("maintenance", 10, "ExitCodeGenerator", "planned maintenance"),
                new ExitScenarioDescriptor("migration-failure", 20, "ExitCodeExceptionMapper", "database migration failed"),
                new ExitScenarioDescriptor("dependency-unavailable", 30, "ExitCodeExceptionMapper", "required dependency unavailable")
        );
    }

    public ExitCodeReport evaluate(String scenario) {
        // HTTP calls calculate exit codes only; process termination belongs in command-line bootstrap code.
        return switch (scenario) {
            case "maintenance" -> new ExitCodeReport(
                    scenario,
                    maintenanceExitCodeGenerator.getExitCode(),
                    "ExitCodeGenerator",
                    "planned maintenance"
            );
            case "migration-failure" -> new ExitCodeReport(
                    scenario,
                    exitCodePolicy.getExitCode(new DataMigrationException("database migration failed")),
                    "ExitCodeExceptionMapper",
                    "database migration failed"
            );
            case "dependency-unavailable" -> new ExitCodeReport(
                    scenario,
                    exitCodePolicy.getExitCode(new DependencyUnavailableException("required dependency unavailable")),
                    "ExitCodeExceptionMapper",
                    "required dependency unavailable"
            );
            default -> throw new IllegalArgumentException("Unsupported exit-code scenario: " + scenario);
        };
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

- `GET /api/exit-code`：模块说明
- `GET /api/exit-code/scenarios`：支持的退出码场景
- `GET /api/exit-code/evaluate/{scenario}`：计算指定场景的退出码

## 调用验证

```bash
curl "http://localhost:8160/api/exit-code"
```

```bash
curl "http://localhost:8160/api/exit-code/scenarios"
```

```bash
curl "http://localhost:8160/api/exit-code/evaluate/maintenance"
```

```bash
curl "http://localhost:8160/api/exit-code/evaluate/migration-failure"
```

## 生产映射

生产系统可以用这个模式：

- 批处理或命令行应用用非 0 退出码表达失败类型
- 启动失败时把已知异常映射到运维手册里的稳定编码
- 在 Java 代码里集中维护退出码策略，避免散落到 shell 脚本
- 用 `SpringApplication.exit(...)` 计算退出码，再由 bootstrap 层决定是否 `System.exit(code)`

## 生产差距

该示例用于隔离学习 ExitCode 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 80-SpringBoot-exit-code test
```

测试覆盖：

- `SpringApplication.exit(context)` 读取 `ExitCodeGenerator` Bean
- `ExitCodeExceptionMapper` 映射 migration/dependency 异常
- 未知异常返回 `0`
- service 场景评估和未知场景拒绝
- MockMvc 验证 metadata、场景列表和退出码计算接口

## 要点总结

1. `ExitCodeGenerator`
2. `ExitCodeExceptionMapper`
3. `SpringApplication.exit(...)`
4. 异常到退出码的稳定映射
5. 安全的退出码场景评估

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
