---
title: SpringBoot API 版本管理
date: 2026-04-20
tags:
  - springboot
  - java
  - api版本
  - 灰度发布
  - 兼容性
module: 22-SpringBoot-api-versioning
area: [[后端开发]]
created: 2026-04-20
---
# SpringBoot API 版本管理

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/22-SpringBoot-api-versioning`

## 核心思路

实现 API 多版本共存与灰度演进：URL 路径版本（`/v1`、`/v2`）、请求头版本（`X-API-Version`）、客户端标签路由（`X-Client-Tag`）、灰度百分比分流四种版本路由策略。

## 项目结构

```
src/main/java/com/cloud/
├── controller/ApiVersioningController.java
├── service/
│   ├── ApiVersionRoutingService.java     (版本路由)
│   ├── InMemoryUserProfileService.java   (用户数据)
│   └── UserViewAssembler.java            (视图组装)
├── model/UserProfile.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 依赖与配置

| 依赖 | 说明 |
|------|------|
| `spring-boot-starter-web` | Web 框架 |

```yaml
server:
  port: 8102

demo:
  api:
    gray-v2-percent: 20         # 灰度比例 0-100
    v1-sunset-date: 2026-12-31  # v1 废弃日期
```

## 核心代码解析

### ApiVersionRoutingService — 版本路由核心

```java
public String resolveVersion(String explicitVersion, String clientTag, String userId) {
    // 1. 显式版本（X-API-Version Header）
    String normalizedVersion = normalizeVersion(explicitVersion);
    if (normalizedVersion != null) return normalizedVersion;

    // 2. 客户端标签（beta → v2）
    if ("beta".equalsIgnoreCase(trimToNull(clientTag))) return "v2";

    // 3. 灰度百分比（userId hashCode 取模）
    int bucket = Math.floorMod(userId.hashCode(), 100);
    return bucket < grayV2Percent ? "v2" : "v1";
}
```

> [!important] 灰度分桶一致性
> `userId.hashCode() % 100` 保证同一用户始终路由到同一版本，避免用户看到版本闪烁。

### UserViewAssembler — 视图组装

```java
// v1：只返回基础字段
public Map<String, Object> toV1(UserProfile profile) {
    return Map.of("apiVersion", "v1", "userId", ..., "nickname", ...);
}

// v2：返回完整字段
public Map<String, Object> toV2(UserProfile profile) {
    return Map.of("apiVersion", "v2", "userId", ..., "nickname", ...,
        "membershipLevel", ..., "city", ..., "riskTags", ...);
}
```

### ApiVersioningController — 版本路由接口

```java
// URL 路径版本
@GetMapping("/v1/users/{userId}")
@GetMapping("/v2/users/{userId}")

// 兼容路由（自动版本解析）
@GetMapping("/users/{userId}")
public ApiResult<Map<String, Object>> getCompatibleUser(
        @PathVariable String userId,
        @RequestHeader(value = "X-API-Version", required = false) String explicitVersion,
        @RequestHeader(value = "X-Client-Tag", required = false) String clientTag) {
    String version = routingService.resolveVersion(explicitVersion, clientTag, userId);
    // 根据 version 选择 toV1 或 toV2
}

// v1 废弃标记
private void markV1Deprecated(HttpServletResponse response) {
    response.setHeader("Deprecation", "true");
    response.setHeader("Sunset", v1SunsetDate);
}
```

> [!tip] Deprecation + Sunset Header
> HTTP 标准草案定义：`Deprecation: true` 表示接口已废弃，`Sunset` 表示废弃日期，客户端可据此提前迁移。

## 版本路由策略

```mermaid
flowchart TD
    A[请求到达 /users/{userId}] --> B{X-API-Version Header?}
    B -->|有| C[使用显式版本]
    B -->|无| D{X-Client-Tag = beta?}
    D -->|是| E[路由到 v2]
    D -->|否| F{灰度百分比}
    F -->|userId % 100 < grayPercent| G[路由到 v2]
    F -->|其他| H[路由到 v1]

    C --> I{v1 / v2?}
    I -->|v1| J[toV1 + Deprecation Header]
    I -->|v2| K[toV2]

    style J fill:#ffd43b
    style K fill:#51cf66,color:#fff
```

### 路由优先级

| 优先级 | 策略 | 请求头 | 说明 |
|--------|------|--------|------|
| 1 | 显式版本 | `X-API-Version` | 客户端指定，最高优先 |
| 2 | 客户端标签 | `X-Client-Tag: beta` | beta 用户走 v2 |
| 3 | 灰度百分比 | 无 | userId 取模分流 |

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot API 版本管理 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ApiVersioningController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ApiVersioningController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api")
public class ApiVersioningController {

    private final InMemoryUserProfileService profileService;
    private final UserViewAssembler viewAssembler;
    private final ApiVersionRoutingService routingService;
    private final String v1SunsetDate;

    public ApiVersioningController(InMemoryUserProfileService profileService,
                                   UserViewAssembler viewAssembler,
                                   ApiVersionRoutingService routingService,
                                   @Value("${demo.api.v1-sunset-date:2026-12-31}") String v1SunsetDate) {
        this.profileService = profileService;
        this.viewAssembler = viewAssembler;
        this.routingService = routingService;
        this.v1SunsetDate = v1SunsetDate;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/versioning")
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "22-SpringBoot-api-versioning");
        data.put("desc", "API版本管理、兼容路由、灰度演进");
        data.put("grayV2Percent", routingService.getGrayV2Percent());
        data.put("v1SunsetDate", v1SunsetDate);
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/versioning/resolve")
    public ApiResult<ApiVersionRoutingService.RouteDecision> resolveVersion(@RequestParam String userId,
                                                                             @RequestHeader(value = "X-API-Version", required = false) String explicitVersion,
                                                                             @RequestHeader(value = "X-Client-Tag", required = false) String clientTag) {
        return ApiResult.success(routingService.resolveDecision(explicitVersion, clientTag, userId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/v1/users/{userId}")
    public ApiResult<Map<String, Object>> getUserV1(@PathVariable String userId, HttpServletResponse response) {
        UserProfile profile = profileService.getByUserId(userId);
        markV1Deprecated(response);
        return ApiResult.success(viewAssembler.toV1(profile));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/v2/users/{userId}")
    public ApiResult<Map<String, Object>> getUserV2(@PathVariable String userId) {
        UserProfile profile = profileService.getByUserId(userId);
        return ApiResult.success(viewAssembler.toV2(profile));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/users/{userId}")
    public ApiResult<Map<String, Object>> getCompatibleUser(@PathVariable String userId,
                                                             @RequestHeader(value = "X-API-Version", required = false) String explicitVersion,
                                                             @RequestHeader(value = "X-Client-Tag", required = false) String clientTag,
                                                             HttpServletResponse response) {
        UserProfile profile = profileService.getByUserId(userId);
        String version = routingService.resolveVersion(explicitVersion, clientTag, userId);

        if ("v2".equals(version)) {
            return ApiResult.success(viewAssembler.toV2(profile));
        }

        markV1Deprecated(response);
        return ApiResult.success(viewAssembler.toV1(profile));
    }

    private void markV1Deprecated(HttpServletResponse response) {
        response.setHeader("Deprecation", "true");
        response.setHeader("Sunset", v1SunsetDate);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ApiVersionRoutingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ApiVersionRoutingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ApiVersionRoutingService {

    private final int grayV2Percent;

    public ApiVersionRoutingService(@Value("${demo.api.gray-v2-percent:0}") int grayV2Percent) {
        if (grayV2Percent < 0 || grayV2Percent > 100) {
            throw new IllegalArgumentException("gray-v2-percent必须在0到100之间");
        }
        this.grayV2Percent = grayV2Percent;
    }

    public String resolveVersion(String explicitVersion, String clientTag, String userId) {
        String normalizedVersion = normalizeVersion(explicitVersion);
        if (normalizedVersion != null) {
            if (!"v1".equals(normalizedVersion) && !"v2".equals(normalizedVersion)) {
                throw new IllegalArgumentException("不支持的API版本: " + explicitVersion);
            }
            return normalizedVersion;
        }

        if ("beta".equalsIgnoreCase(trimToNull(clientTag))) {
            return "v2";
        }

        if (grayV2Percent == 0) {
            return "v1";
        }
        if (grayV2Percent == 100) {
            return "v2";
        }

        if (trimToNull(userId) == null) {
            throw new IllegalArgumentException("userId不能为空");
        }

        int bucket = Math.floorMod(userId.hashCode(), 100);
        return bucket < grayV2Percent ? "v2" : "v1";
    }

    public RouteDecision resolveDecision(String explicitVersion, String clientTag, String userId) {
        String normalizedVersion = normalizeVersion(explicitVersion);
        if (normalizedVersion != null) {
            if (!"v1".equals(normalizedVersion) && !"v2".equals(normalizedVersion)) {
                throw new IllegalArgumentException("不支持的API版本: " + explicitVersion);
            }
            return new RouteDecision(normalizedVersion, "EXPLICIT", -1, grayV2Percent);
        }

        if ("beta".equalsIgnoreCase(trimToNull(clientTag))) {
            return new RouteDecision("v2", "BETA_TAG", -1, grayV2Percent);
        }

        if (trimToNull(userId) == null) {
            throw new IllegalArgumentException("userId不能为空");
        }

        int bucket = Math.floorMod(userId.hashCode(), 100);
        String resolved = bucket < grayV2Percent ? "v2" : "v1";
        return new RouteDecision(resolved, "GRAY_PERCENT", bucket, grayV2Percent);
    }

    public int getGrayV2Percent() {
        return grayV2Percent;
    }

    private String normalizeVersion(String version) {
        String trimmed = trimToNull(version);
        if (trimmed == null) {
            return null;
        }
        return trimmed.toLowerCase();
    }

    private String trimToNull(String text) {
        if (text == null) {
            return null;
        }
        String trimmed = text.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    public record RouteDecision(String version, String reason, int bucket, int grayPercent) {
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/InMemoryUserProfileService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/InMemoryUserProfileService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class InMemoryUserProfileService {

    private final Map<String, UserProfile> profileStore = new ConcurrentHashMap<>();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InMemoryUserProfileService() {
        profileStore.put("u1", new UserProfile("u1", "Alice", "GOLD", "Shanghai", List.of("LOW_RISK")));
        profileStore.put("u2", new UserProfile("u2", "Bob", "SILVER", "Hangzhou", List.of("NEW_DEVICE", "PHONE_UNVERIFIED")));
        profileStore.put("u3", new UserProfile("u3", "Cindy", "PLATINUM", "Shenzhen", List.of("VIP")));
    }

    public UserProfile getByUserId(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("userId不能为空");
        }
        UserProfile profile = profileStore.get(userId);
        if (profile == null) {
            throw new IllegalArgumentException("用户不存在: " + userId);
        }
        return profile;
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

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MissingServletRequestParameterException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResult<Void> handleMissingServletRequestParameterException(MissingServletRequestParameterException ex) {
        return ApiResult.fail(400, "缺少请求参数: " + ex.getParameterName());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResult<Void> handleIllegalArgumentException(IllegalArgumentException ex) {
        return ApiResult.fail(400, ex.getMessage());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResult<Void> handleException(Exception ex) {
        log.error("Unhandled exception", ex);
        return ApiResult.fail(500, "系统异常，请稍后重试");
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

| 方法 | 路径 | 版本 | 说明 |
|------|------|------|------|
| GET | `/api/versioning` | - | 模块信息 |
| GET | `/api/versioning/resolve` | - | 解析版本路由决策 |
| GET | `/api/v1/users/{userId}` | v1 | 用户信息 v1（已废弃） |
| GET | `/api/v2/users/{userId}` | v2 | 用户信息 v2 |
| GET | `/api/users/{userId}` | 自动 | 兼容路由 |

## API 版本管理方案对比

| 方案 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **URL 路径** | `/v1/users` | 直观、易缓存 | URL 膨胀 |
| 请求头 | `X-API-Version: v2` | URL 不变 | 不直观、需文档 |
| Content Negotiation | `Accept: application/vnd.api.v2+json` | RESTful | 复杂 |
| 参数 | `?version=2` | 简单 | 不规范 |

## 生产差距

这个示例适合帮助初学者理解 API 版本管理 的核心机制，但生产项目不能只停留在“能跑通”。真实落地时至少要补齐：统一鉴权、参数边界校验、异常响应、结构化日志、监控指标、自动化测试、配置隔离和容量评估。

如果模块涉及数据库、缓存、消息、网关、认证或外部服务，还要进一步考虑连接池、超时、重试、幂等、事务边界、数据一致性和故障告警。学习时可以先记住主流程，再用这些生产差距反向检查自己是否真正理解了案例。

## 要点总结

1. **URL 路径版本**：最常见、最直观，`/v1` 和 `/v2` 可同时存在
2. **灰度发布**：userId 取模保证一致性，灰度比例可动态调整（0→100% 即全量）
3. **Deprecation / Sunset Header**：标准化废弃通知，客户端可自动检测
4. **UserViewAssembler**：同一数据模型，不同版本输出不同字段，向后兼容
5. **路由优先级**：显式版本 > 客户端标签 > 灰度百分比，层次清晰
