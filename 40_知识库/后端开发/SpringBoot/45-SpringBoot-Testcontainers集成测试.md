---
title: SpringBoot Testcontainers集成测试
date: 2026-05-11
tags:
  - springboot
  - java
  - 集成测试
module: 45-SpringBoot-testcontainers-integration-test
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot Testcontainers集成测试

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/45-SpringBoot-testcontainers-integration-test`

## 核心思路

本模块演示如何用 Testcontainers 补强 MySQL/Redis 集成测试。普通单元测试和接口测试不依赖 Docker；真正启动容器的 smoke tests 使用 `@Testcontainers(disabledWithoutDocker = true)`，本机 Docker 可用时会运行真实容器，不可用时自动跳过。

## 能力点

- MySQL Testcontainers smoke test
- Redis Testcontainers smoke test
- Docker readiness 检查
- 早期外部依赖模块的集成测试场景目录
- 无 Docker 环境下仍可稳定执行 `mvn test`

## 关键实现

检查命令：

```bash
docker info --format '{{.ServerVersion}}'
```

如果 Docker 正在运行，`MySqlContainerSmokeTest` 和 `RedisContainerSmokeTest` 会真实启动容器。如果 Docker 不可用，这两个测试会被 Testcontainers 跳过，普通单元测试和 MockMvc 测试仍会执行。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Testcontainers集成测试 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/TestcontainersGuideController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/TestcontainersGuideController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/testcontainers")
public class TestcontainersGuideController {

    private final TestcontainersGuideService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public TestcontainersGuideController(TestcontainersGuideService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        DockerReadiness readiness = service.dockerReadiness();
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "45-SpringBoot-testcontainers-integration-test");
        data.put("desc", "Testcontainers MySQL/Redis 集成测试示例和 Docker readiness 指引");
        data.put("dockerAvailable", readiness.isAvailable());
        data.put("scenarioCount", service.scenarios().size());
        data.put("apis", new String[]{
                "GET /api/testcontainers",
                "GET /api/testcontainers/scenarios",
                "GET /api/testcontainers/scenarios/{scenarioId}",
                "GET /api/testcontainers/readiness"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/scenarios")
    public ApiResult<List<ContainerScenario>> scenarios() {
        return ApiResult.success(service.scenarios());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/scenarios/{scenarioId}")
    public ApiResult<ContainerScenario> scenario(@PathVariable String scenarioId) {
        return ApiResult.success(service.findScenario(scenarioId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/readiness")
    public ApiResult<DockerReadiness> readiness() {
        return ApiResult.success(service.dockerReadiness());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/TestcontainersGuideService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/TestcontainersGuideService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class TestcontainersGuideService {

    private static final String CHECKED_COMMAND = "docker info --format {{.ServerVersion}}";
    private static final String RECOMMENDED_COMMAND = "mvn -pl 45-SpringBoot-testcontainers-integration-test test";

    private final List<ContainerScenario> scenarios = List.of(
            new ContainerScenario(
                    "mysql-user-read",
                    "MySQL JDBC integration test",
                    "02-SpringBoot-mysql",
                    List.of("mysql:8.0"),
                    List.of("start isolated MySQL", "create demo table", "insert user row", "query row count")
            ),
            new ContainerScenario(
                    "redis-cache-roundtrip",
                    "Redis round-trip integration test",
                    "03-SpringBoot-redis",
                    List.of("redis:7-alpine"),
                    List.of("start isolated Redis", "SET/GET key round-trip", "close Lettuce connection")
            ),
            new ContainerScenario(
                    "mysql-redis-cache-aside",
                    "MySQL + Redis cache-aside integration target",
                    "05-SpringBoot-mysql-redis",
                    List.of("mysql:8.0", "redis:7-alpine"),
                    List.of("load source row from MySQL", "cache computed result in Redis", "verify cache hit")
            )
    );

    public List<ContainerScenario> scenarios() {
        return scenarios;
    }

    public ContainerScenario findScenario(String scenarioId) {
        return scenarios.stream()
                .filter(scenario -> scenario.getScenarioId().equals(scenarioId))
                .findFirst()
                .orElseThrow(() -> new NoSuchElementException("测试场景不存在: " + scenarioId));
    }

    public DockerReadiness dockerReadiness() {
        return dockerReadiness(Duration.ofSeconds(2));
    }

    public DockerReadiness dockerReadiness(Duration timeout) {
        Process process = null;
        try {
            process = new ProcessBuilder("docker", "info", "--format", "{{.ServerVersion}}")
                    .redirectErrorStream(true)
                    .start();
            boolean finished = process.waitFor(timeout.toMillis(), TimeUnit.MILLISECONDS);
            if (!finished) {
                process.destroyForcibly();
                return unavailable("Docker readiness check timed out");
            }
            String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8).trim();
            if (process.exitValue() == 0 && !output.isBlank()) {
                return new DockerReadiness(
                        true,
                        output,
                        CHECKED_COMMAND,
                        "Docker is available; Testcontainers smoke tests will run real containers.",
                        RECOMMENDED_COMMAND
                );
            }
            return unavailable(output.isBlank() ? "Docker command failed" : output);
        } catch (IOException exception) {
            return unavailable(exception.getMessage());
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            return unavailable("Docker readiness check was interrupted");
        } finally {
            if (process != null && process.isAlive()) {
                process.destroyForcibly();
            }
        }
    }

    private DockerReadiness unavailable(String reason) {
        return new DockerReadiness(
                false,
                "",
                CHECKED_COMMAND,
                "Docker is unavailable; Testcontainers smoke tests are skipped. Reason: " + reason,
                RECOMMENDED_COMMAND
        );
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

    @ExceptionHandler(NoSuchElementException.class)
    public ResponseEntity<ApiResult<Void>> handleNotFound(NoSuchElementException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResult.fail(404, exception.getMessage()));
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

- `GET /api/testcontainers`：模块信息和 Docker 可用性
- `GET /api/testcontainers/scenarios`：场景列表
- `GET /api/testcontainers/scenarios/{scenarioId}`：场景详情
- `GET /api/testcontainers/readiness`：Docker readiness 和推荐测试命令

## 生产映射

- `mysql-user-read`：对应 `02-SpringBoot-mysql`
- `redis-cache-roundtrip`：对应 `03-SpringBoot-redis`
- `mysql-redis-cache-aside`：对应 `05-SpringBoot-mysql-redis`

## 生产差距

该示例用于隔离学习 Testcontainers集成测试 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 45-SpringBoot-testcontainers-integration-test test
```

## 要点总结

1. MySQL Testcontainers smoke test
2. Redis Testcontainers smoke test
3. Docker readiness 检查
4. 早期外部依赖模块的集成测试场景目录
5. 无 Docker 环境下仍可稳定执行 `mvn test`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
