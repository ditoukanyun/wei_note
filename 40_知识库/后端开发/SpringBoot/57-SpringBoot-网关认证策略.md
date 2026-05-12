---
title: SpringBoot 网关认证策略
date: 2026-05-11
tags:
  - springboot
  - java
  - 网关
module: 57-SpringBoot-gateway-auth-policy
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 网关认证策略

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/57-SpringBoot-gateway-auth-policy`

## 核心思路

本模块演示网关路由鉴权策略原型：按路由路径匹配策略，并根据 HTTP 方法、用户角色和客户端 IP 生成允许或拒绝决策，同时返回稳定的拒绝原因。

## 能力点

- 路由权限策略
- 路径模式匹配
- HTTP 方法约束
- 角色约束
- IP allowlist
- 策略优先级
- 拒绝原因解释

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 网关认证策略 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- 认证/上下文类案例要特别关注“在哪里写入、在哪里校验、在哪里清理”。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/GatewayAuthPolicyController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/GatewayAuthPolicyController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/gateway-auth")
public class GatewayAuthPolicyController {
    private final GatewayAuthPolicyService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public GatewayAuthPolicyController(GatewayAuthPolicyService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "57-SpringBoot-gateway-auth-policy");
        data.put("desc", "网关路由权限策略、角色/IP/方法约束和策略解释");
        data.put("apis", new String[]{
                "GET /api/gateway-auth",
                "POST /api/gateway-auth/policies",
                "GET /api/gateway-auth/policies",
                "POST /api/gateway-auth/evaluate"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/policies")
    public ApiResult<RouteAuthPolicy> savePolicy(@RequestBody RouteAuthPolicy policy) {
        return ApiResult.success(service.savePolicy(policy));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/policies")
    public ApiResult<List<RouteAuthPolicy>> policies() {
        return ApiResult.success(service.policies());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/evaluate")
    public ApiResult<PolicyEvaluation> evaluate(@RequestBody AccessRequest request) {
        return ApiResult.success(service.evaluate(request));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/GatewayAuthPolicyService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/GatewayAuthPolicyService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class GatewayAuthPolicyService {
    private final PolicyRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public GatewayAuthPolicyService(PolicyRepository repository) {
        this.repository = repository;
    }

    public RouteAuthPolicy savePolicy(RouteAuthPolicy policy) {
        validatePolicy(policy);
        policy.setAllowedMethods(normalizeList(policy.getAllowedMethods(), true));
        policy.setRequiredRoles(normalizeList(policy.getRequiredRoles(), true));
        policy.setIpAllowlist(normalizeList(policy.getIpAllowlist(), false));
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(policy);
    }

    public List<RouteAuthPolicy> policies() {
        return repository.findAll().stream()
                .sorted(Comparator.comparingInt(RouteAuthPolicy::getPriority).thenComparing(RouteAuthPolicy::getPolicyId))
                .toList();
    }

    public PolicyEvaluation evaluate(AccessRequest request) {
        validateRequest(request);
        String method = request.getMethod().trim().toUpperCase(Locale.ROOT);
        List<String> roles = normalizeList(request.getRoles(), true);
        String clientIp = request.getClientIp().trim();

        RouteAuthPolicy policy = policies().stream()
                .filter(RouteAuthPolicy::isEnabled)
                .filter(candidate -> pathMatches(candidate.getPathPattern(), request.getPath().trim()))
                .findFirst()
                .orElse(null);

        if (policy == null) {
            return PolicyEvaluation.deny("NO_MATCHING_POLICY", "没有匹配当前路径的启用策略");
        }
        if (!allows(policy.getAllowedMethods(), method)) {
            return PolicyEvaluation.deny(policy, "METHOD_NOT_ALLOWED", "HTTP 方法不允许: " + method);
        }
        if (!hasRequiredRole(policy.getRequiredRoles(), roles)) {
            return PolicyEvaluation.deny(policy, "ROLE_REQUIRED", "缺少访问该路由所需角色");
        }
        if (!allows(policy.getIpAllowlist(), clientIp)) {
            return PolicyEvaluation.deny(policy, "IP_NOT_ALLOWED", "客户端 IP 不在允许列表");
        }
        return PolicyEvaluation.allow(policy);
    }

    private void validatePolicy(RouteAuthPolicy policy) {
        if (policy == null) throw new IllegalArgumentException("policy 不能为空");
        if (isBlank(policy.getPolicyId())) throw new IllegalArgumentException("policyId 不能为空");
        if (isBlank(policy.getRouteId())) throw new IllegalArgumentException("routeId 不能为空");
        if (isBlank(policy.getPathPattern())) throw new IllegalArgumentException("pathPattern 不能为空");
        if (!policy.getPathPattern().startsWith("/")) throw new IllegalArgumentException("pathPattern 必须以 / 开头");
        if (policy.getPathPattern().contains("**") && !policy.getPathPattern().endsWith("/**")) {
            throw new IllegalArgumentException("pathPattern 仅支持 /** 结尾通配");
        }
        if (policy.getPriority() < 0) throw new IllegalArgumentException("priority 不能小于 0");
    }

    private void validateRequest(AccessRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getPath())) throw new IllegalArgumentException("path 不能为空");
        if (isBlank(request.getMethod())) throw new IllegalArgumentException("method 不能为空");
        if (isBlank(request.getClientIp())) throw new IllegalArgumentException("clientIp 不能为空");
    }

    private List<String> normalizeList(List<String> values, boolean uppercase) {
        if (values == null) {
            return List.of();
        }
        return values.stream()
                .filter(value -> value != null && !value.isBlank())
                .map(String::trim)
                .map(value -> uppercase ? value.toUpperCase(Locale.ROOT) : value)
                .distinct()
                .toList();
    }

    private boolean allows(List<String> allowedValues, String value) {
        return allowedValues == null || allowedValues.isEmpty() || allowedValues.contains(value);
    }

    private boolean hasRequiredRole(List<String> requiredRoles, List<String> userRoles) {
        if (requiredRoles == null || requiredRoles.isEmpty()) {
            return true;
        }
        Set<String> roleSet = new HashSet<>(userRoles);
        return requiredRoles.stream().anyMatch(roleSet::contains);
    }

    private boolean pathMatches(String pattern, String path) {
        // Keep path matching intentionally small: exact routes and "/**" suffix routes cover the gateway policy idea.
        if (pattern.endsWith("/**")) {
            String prefix = pattern.substring(0, pattern.length() - 3);
            return path.equals(prefix) || path.startsWith(prefix + "/");
        }
        return pattern.equals(path);
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/gateway/PolicyRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/gateway/PolicyRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class PolicyRepository {
    private final Map<String, RouteAuthPolicy> policies = new ConcurrentHashMap<>();

    public RouteAuthPolicy save(RouteAuthPolicy policy) {
        policies.put(policy.getPolicyId(), policy);
        return policy;
    }

    public Optional<RouteAuthPolicy> findById(String policyId) {
        return Optional.ofNullable(policies.get(policyId));
    }

    public List<RouteAuthPolicy> findAll() {
        return new ArrayList<>(policies.values());
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
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

1. GatewayAuthPolicyController：接收 HTTP 请求并转换成 Java 方法调用
2. GatewayAuthPolicyService：执行案例的核心业务规则
3. PolicyRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/gateway-auth`：模块说明
- `POST /api/gateway-auth/policies`：创建或替换策略
- `GET /api/gateway-auth/policies`：查询策略列表
- `POST /api/gateway-auth/evaluate`：评估一次访问请求

## 调用验证

```bash
curl -X POST "http://localhost:8137/api/gateway-auth/policies" \
  -H "Content-Type: application/json" \
  -d '{"policyId":"policy-order-admin","routeId":"order-admin","pathPattern":"/api/orders/**","allowedMethods":["GET","POST"],"requiredRoles":["ORDER_ADMIN"],"ipAllowlist":["10.0.0.1"],"priority":10,"enabled":true}'
```

```bash
curl -X POST "http://localhost:8137/api/gateway-auth/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"path":"/api/orders/100","method":"GET","roles":["ORDER_ADMIN"],"clientIp":"10.0.0.1"}'
```

```bash
curl -X POST "http://localhost:8137/api/gateway-auth/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"path":"/api/orders/100","method":"GET","roles":["ORDER_VIEWER"],"clientIp":"10.0.0.1"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 网关过滤器：在转发到后端服务前执行策略评估
- 策略存储：数据库、配置中心或规则平台
- 路径匹配：使用 Spring Cloud Gateway、Nginx 或 API 网关内置路由谓词
- 身份来源：从已验证 JWT、Session 或内部鉴权上下文提取角色
- IP 判断：结合可信代理头和 CIDR-aware 匹配
- 审计：记录拒绝请求、命中策略和原因码

## 生产差距

该示例用于隔离学习 网关认证策略 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 57-SpringBoot-gateway-auth-policy test
```

## 要点总结

1. 路由权限策略
2. 路径模式匹配
3. HTTP 方法约束
4. 角色约束
5. IP allowlist

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
