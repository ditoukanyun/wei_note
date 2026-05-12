---
title: SpringBoot Header Token 登录
date: 2026-04-20
tags:
  - springboot
  - java
  - token
  - 登录
module: 13-SpringBoot-header-token-login
area: [[后端开发]]
created: 2026-04-20
---
# SpringBoot Header Token 登录

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/13-SpringBoot-header-token-login`

## 核心思路

自定义 Token（UUID）存储在服务端内存中，客户端通过 `X-Auth-Token` 请求头携带，拦截器校验。

## Token 存储 — InMemoryTokenService

```java
@Service
public class InMemoryTokenService {
    private final Map<String, LoginUser> tokenStore = new ConcurrentHashMap<>();

    public String createToken(LoginUser loginUser) {
        String token = UUID.randomUUID().toString().replace("-", "");
        tokenStore.put(token, loginUser);
        return token;
    }

    public LoginUser getLoginUser(String token) { return tokenStore.get(token); }
    public void invalidate(String token) { tokenStore.remove(token); }
}
```

- `ConcurrentHashMap` 线程安全
- Token = UUID，无业务含义，不可逆

## 拦截器 — HeaderTokenInterceptor

```java
@Override
public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
    String token = request.getHeader("X-Auth-Token");
    LoginUser loginUser = tokenService.getLoginUser(token);
    if (loginUser == null) throw new UnauthenticatedException("未登录");
    request.setAttribute("loginUser", loginUser);  // 存入 request 供 Controller 使用
    return true;
}
```

- 与 JWT 不同：Token 本身不含用户信息，需查服务端
- 用户信息通过 `request.setAttribute` 传递（非 ThreadLocal）

## Session vs Header Token vs JWT 对比

| 维度 | Session | Header Token | JWT |
|------|---------|-------------|-----|
| Token 位置 | Cookie | 自定义 Header | Authorization Header |
| 用户信息 | 服务端 Session | 服务端内存 Map | Token 自带 |
| 注销 | `invalidate()` 立即生效 | `remove()` 立即生效 | 需黑名单 |
| 分布式 | 需 Session 共享 | 需 Redis 共享 | 天然支持 |
| Token 格式 | JSESSIONID | UUID | Base64 编码 JSON |

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Header Token 登录 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- 认证/上下文类案例要特别关注“在哪里写入、在哪里校验、在哪里清理”。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/HeaderTokenAuthController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/HeaderTokenAuthController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/header")
public class HeaderTokenAuthController {

    private final InMemoryAuthService authService;
    private final InMemoryTokenService tokenService;

    public HeaderTokenAuthController(InMemoryAuthService authService,
                                     InMemoryTokenService tokenService) {
        this.authService = authService;
        this.tokenService = tokenService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/login")
    public ApiResult<Map<String, Object>> login(@RequestParam String username,
                                                 @RequestParam String password) {
        try {
            LoginUser loginUser = authService.authenticate(username, password);
            String token = tokenService.createToken(loginUser);
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("token", token);
            data.put("tokenHeader", HeaderTokenInterceptor.TOKEN_HEADER);
            data.put("user", loginUser);
            return ApiResult.success(data);
        } catch (IllegalArgumentException ex) {
            throw new UnauthenticatedException(ex.getMessage());
        }
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/me")
    public ApiResult<LoginUser> currentUser(HttpServletRequest request) {
        Object value = request.getAttribute(HeaderTokenInterceptor.LOGIN_USER_ATTRIBUTE);
        if (value instanceof LoginUser loginUser) {
            return ApiResult.success(loginUser);
        }
        throw new UnauthenticatedException("未登录");
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/logout")
    public ApiResult<String> logout(HttpServletRequest request) {
        String token = request.getHeader(HeaderTokenInterceptor.TOKEN_HEADER);
        tokenService.invalidate(token);
        return ApiResult.success("ok");
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/public")
    public ApiResult<String> publicApi() {
        return ApiResult.success("这是一个无需登录即可访问的公共接口");
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/InMemoryTokenService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/InMemoryTokenService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class InMemoryTokenService {

    private final Map<String, LoginUser> tokenStore = new ConcurrentHashMap<>();

    public String createToken(LoginUser loginUser) {
        String token = UUID.randomUUID().toString().replace("-", "");
        tokenStore.put(token, loginUser);
        return token;
    }

    public LoginUser getLoginUser(String token) {
        if (token == null || token.isBlank()) {
            return null;
        }
        return tokenStore.get(token);
    }

    public void invalidate(String token) {
        if (token == null || token.isBlank()) {
            return;
        }
        tokenStore.remove(token);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/interceptor/HeaderTokenInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/interceptor/HeaderTokenInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class HeaderTokenInterceptor implements HandlerInterceptor {

    public static final String TOKEN_HEADER = "X-Auth-Token";
    public static final String LOGIN_USER_ATTRIBUTE = "loginUser";

    private final InMemoryTokenService tokenService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public HeaderTokenInterceptor(InMemoryTokenService tokenService) {
        this.tokenService = tokenService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        String token = request.getHeader(TOKEN_HEADER);
        LoginUser loginUser = tokenService.getLoginUser(token);
        if (loginUser == null) {
            throw new UnauthenticatedException("未登录");
        }

        request.setAttribute(LOGIN_USER_ATTRIBUTE, loginUser);
        return true;
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/InMemoryAuthService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/InMemoryAuthService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class InMemoryAuthService {

    private final Map<String, String> passwords = Map.of(
            "admin", "123456"
    );

    private final Map<String, String> displayNames = Map.of(
            "admin", "管理员"
    );

    public LoginUser authenticate(String username, String password) {
        if (username == null || !passwords.containsKey(username)) {
            throw new IllegalArgumentException("账号不存在");
        }
        if (password == null || !passwords.get(username).equals(password)) {
            throw new IllegalArgumentException("账号或密码错误");
        }
        return new LoginUser(username, displayNames.get(username));
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. HeaderTokenInterceptor：请求进入 Controller 前准备上下文或校验
2. HeaderTokenAuthController：接收 HTTP 请求并转换成 Java 方法调用
3. InMemoryTokenService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

| 方法 | 路径 | 需登录 | 说明 |
|------|------|--------|------|
| POST | `/api/header/login` | 否 | 登录，返回 token |
| GET | `/api/header/me` | 是 | 当前用户 |
| POST | `/api/header/logout` | 是 | 登出 |
| GET | `/api/header/public` | 否 | 公开接口 |

## 生产差距

这个示例适合帮助初学者理解 Header Token 登录 的核心机制，但生产项目不能只停留在“能跑通”。真实落地时至少要补齐：统一鉴权、参数边界校验、异常响应、结构化日志、监控指标、自动化测试、配置隔离和容量评估。

如果模块涉及数据库、缓存、消息、网关、认证或外部服务，还要进一步考虑连接池、超时、重试、幂等、事务边界、数据一致性和故障告警。学习时可以先记住主流程，再用这些生产差距反向检查自己是否真正理解了案例。

## 要点总结

1. **Header Token**：简单 Token 方案，服务端存 Map，客户端传 Header
2. **立即可注销**：删除 Map 中的 key 即可，比 JWT 更易控制
3. **不适合生产**：内存存储，重启丢失、不支持分布式（应换 Redis）
4. **与 Session 的区别**：不用 Cookie，前后端分离友好
5. **与 JWT 的区别**：Token 无业务信息，需查服务端，但注销更简单

## 实践检查清单

- Token 是否有过期时间、刷新策略和主动失效能力。
- Token 存储是否从内存替换为 Redis 等共享存储，以支持多实例。
- 拦截器是否放行登录、健康检查和公开接口。
- 失败响应是否统一返回 401，而不是在业务层散落判断。
- 日志是否避免输出完整 Token，只记录脱敏后的标识。

## 案例

后台管理系统使用 Header Token 登录时，登录接口返回随机 Token，前端存入内存或安全存储，请求时放到 `X-Auth-Token`。用户登出时服务端删除 Token，后续请求立即失效。

## 常见误区

- 只生成 Token 不设置过期时间，导致泄露后长期有效。
- 多实例部署仍使用本地 Map，用户请求打到另一台机器就变成未登录。
- 在日志、异常或浏览器地址中暴露 Token。
