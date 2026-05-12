---
title: SpringBoot Actuator健康检查与就绪探针
date: 2026-05-11
tags:
  - springboot
  - java
  - 可观测性
module: 67-SpringBoot-actuator-health-readiness
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot Actuator健康检查与就绪探针

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/67-SpringBoot-actuator-health-readiness`

## 核心思路

本模块演示 Spring Boot Actuator 健康检查的核心机制：自定义 `HealthIndicator`、liveness/readiness 健康组、依赖健康聚合和诊断 API。

## 能力点

- `spring-boot-starter-actuator`
- `HealthIndicator`
- `/actuator/health`
- `/actuator/health/readiness`
- `/actuator/health/liveness`
- 必需依赖与可选依赖的健康聚合
- readiness 拒绝流量原因诊断
- MockMvc 验证 Actuator 端点

## 配置要点

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
      group:
        readiness:
          include: readinessState,dependencyAggregate
        liveness:
          include: livenessState
```

`dependencyAggregate` 是本模块注册的自定义健康贡献者。它把业务服务中的依赖健康快照适配为 Actuator 的 `Health` 对象。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Actuator健康检查与就绪探针 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ActuatorHealthController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ActuatorHealthController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/actuator-health")
public class ActuatorHealthController {
    private final DependencyHealthService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ActuatorHealthController(DependencyHealthService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "67-SpringBoot-actuator-health-readiness");
        data.put("desc", "Actuator HealthIndicator、liveness/readiness 与依赖健康聚合");
        data.put("apis", new String[]{
                "GET /api/actuator-health",
                "GET /api/actuator-health/dependencies",
                "POST /api/actuator-health/dependencies/{name}",
                "GET /api/actuator-health/snapshot",
                "GET /api/actuator-health/readiness"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/dependencies")
    public ApiResult<List<DependencyHealthRecord>> dependencies() {
        return ApiResult.success(service.dependencies());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/dependencies/{name}")
    public ApiResult<DependencyHealthRecord> update(@PathVariable String name,
                                                    @RequestBody UpdateDependencyHealthRequest request) {
        return ApiResult.success(service.update(name, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/snapshot")
    public ApiResult<HealthSnapshot> snapshot() {
        return ApiResult.success(service.snapshot());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/readiness")
    public ApiResult<Map<String, Object>> readiness() {
        // This mirrors the readiness decision in a diagnostic-friendly API with explicit refusal reasons.
        return ApiResult.success(service.readiness());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/DependencyHealthService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/DependencyHealthService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class DependencyHealthService {
    private final Map<String, DependencyHealthRecord> dependencies = new LinkedHashMap<>();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DependencyHealthService() {
        dependencies.put("database", healthy("database", "database", true));
        dependencies.put("redis", healthy("redis", "cache", true));
        dependencies.put("mq", healthy("mq", "message-queue", false));
    }

    public List<DependencyHealthRecord> dependencies() {
        return new ArrayList<>(dependencies.values());
    }

    public DependencyHealthRecord update(String name, UpdateDependencyHealthRequest request) {
        validateName(name);
        validateRequest(request);
        DependencyHealthRecord current = dependencies.get(name);
        DependencyHealthRecord updated = new DependencyHealthRecord(current.getName(), current.getKind(),
                current.isRequired(), request.getStatus(), request.getLatencyMs(), request.getMessage(),
                request.getCheckedAt());
        dependencies.put(name, updated);
        return updated;
    }

    public HealthSnapshot snapshot() {
        List<DependencyHealthRecord> records = dependencies();
        List<String> downDependencies = records.stream()
                .filter(record -> record.getStatus() == DependencyStatus.DOWN)
                .map(DependencyHealthRecord::getName)
                .toList();
        boolean requiredDown = records.stream()
                .anyMatch(record -> record.isRequired() && record.getStatus() == DependencyStatus.DOWN);
        DependencyStatus aggregateStatus = requiredDown ? DependencyStatus.DOWN : DependencyStatus.UP;
        String readinessState = requiredDown ? "REFUSING_TRAFFIC" : "ACCEPTING_TRAFFIC";
        return new HealthSnapshot(aggregateStatus, readinessState, records.size(), downDependencies, records);
    }

    public Map<String, Object> readiness() {
        HealthSnapshot snapshot = snapshot();
        Map<String, Object> readiness = new LinkedHashMap<>();
        readiness.put("state", snapshot.getReadinessState());
        List<String> requiredDown = snapshot.getDependencies().stream()
                .filter(record -> record.isRequired() && record.getStatus() == DependencyStatus.DOWN)
                .map(DependencyHealthRecord::getName)
                .toList();
        readiness.put("reason", requiredDown.isEmpty()
                ? "all required dependencies are healthy"
                : "required dependencies down: " + String.join(", ", requiredDown));
        readiness.put("requiredDown", requiredDown);
        return readiness;
    }

    private DependencyHealthRecord healthy(String name, String kind, boolean required) {
        return new DependencyHealthRecord(name, kind, required, DependencyStatus.UP, 5, "healthy",
                LocalDateTime.now());
    }

    private void validateName(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("dependency 不能为空");
        }
        if (!dependencies.containsKey(name)) {
            throw new IllegalArgumentException("dependency 不存在: " + name);
        }
    }

    private void validateRequest(UpdateDependencyHealthRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (request.getStatus() == null) throw new IllegalArgumentException("status 不能为空");
        if (request.getLatencyMs() < 0) throw new IllegalArgumentException("latencyMs 不能小于 0");
        if (request.getMessage() == null || request.getMessage().isBlank()) {
            throw new IllegalArgumentException("message 不能为空");
        }
        if (request.getCheckedAt() == null) throw new IllegalArgumentException("checkedAt 不能为空");
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

- `GET /api/actuator-health`：模块说明
- `GET /api/actuator-health/dependencies`：查看所有依赖状态
- `POST /api/actuator-health/dependencies/{name}`：更新依赖状态
- `GET /api/actuator-health/snapshot`：查看聚合健康快照
- `GET /api/actuator-health/readiness`：查看 readiness 诊断原因

## 调用验证

```bash
curl "http://localhost:8147/actuator/health"
```

```bash
curl -X POST "http://localhost:8147/api/actuator-health/dependencies/redis" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DOWN",
    "latencyMs": 180,
    "message": "connection timeout",
    "checkedAt": "2026-05-09T10:20:00"
  }'
```

```bash
curl "http://localhost:8147/api/actuator-health/readiness"
```

```bash
curl -i "http://localhost:8147/actuator/health/readiness"
```

当必需依赖失败时，readiness 端点会返回 `DOWN`，HTTP 状态为 `503`。

## 生产映射

生产系统通常会把这个模块扩展为：

- 数据库、缓存、消息队列、对象存储等依赖探活
- Kubernetes readiness/liveness 探针
- 可选依赖降级但不摘流
- 运维诊断接口解释 readiness 失败原因
- 结合告警系统聚合依赖故障

## 生产差距

该示例用于隔离学习 Actuator健康检查与就绪探针 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 67-SpringBoot-actuator-health-readiness test
```

测试覆盖：

- 服务层依赖状态聚合和 readiness 决策
- 自定义 `HealthIndicator` 状态和 details
- 业务诊断 API
- `/actuator/health` 自定义健康组件
- `/actuator/health/readiness` 和 `/actuator/health/liveness`
- 必需依赖失败时 readiness 返回 `503`

## 要点总结

1. `spring-boot-starter-actuator`
2. `HealthIndicator`
3. `/actuator/health`
4. `/actuator/health/readiness`
5. `/actuator/health/liveness`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
