---
title: SpringBoot 请求签名与重放防护
date: 2026-05-11
tags:
  - springboot
  - java
  - 签名
module: 40-SpringBoot-request-signature-replay
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 请求签名与重放防护

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/40-SpringBoot-request-signature-replay`

## 核心思路

本模块演示机器到机器接口常见的 HMAC 请求签名与防重放机制。客户端按固定规则生成签名，服务端在拦截器中校验 appId、timestamp、nonce 和 signature。

## 能力点

- `X-App-Id` 标识调用方
- `X-Timestamp` 控制 5 分钟时间窗
- `X-Nonce` 保证一次性请求
- `X-Signature` 使用 HMAC-SHA256 生成
- Spring MVC `HandlerInterceptor` 保护业务接口

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 请求签名与重放防护 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/RequestSignatureController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/RequestSignatureController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/signature")
public class RequestSignatureController {

    private final SignatureService signatureService;
    private final SignedOrderService signedOrderService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public RequestSignatureController(SignatureService signatureService, SignedOrderService signedOrderService) {
        this.signatureService = signatureService;
        this.signedOrderService = signedOrderService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "40-SpringBoot-request-signature-replay");
        data.put("desc", "HMAC 请求签名、timestamp 时间窗校验、nonce 防重放");
        data.put("headers", new String[]{"X-App-Id", "X-Timestamp", "X-Nonce", "X-Signature"});
        data.put("apis", new String[]{
                "GET /api/signature/demo-signature",
                "GET /api/signature/orders/{orderId}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/demo-signature")
    public ApiResult<DemoSignatureResponse> demoSignature(
            @RequestParam(defaultValue = "demo-app") String appId,
            @RequestParam String method,
            @RequestParam String path,
            @RequestParam String timestamp,
            @RequestParam String nonce
    ) {
        String signature = signatureService.signForApp(appId, method, path, timestamp, nonce);
        return ApiResult.success(new DemoSignatureResponse(
                appId,
                signatureService.canonical(method, path, timestamp, nonce),
                signature
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/orders/{orderId}")
    public ApiResult<SignedOrder> order(@PathVariable String orderId) {
        return ApiResult.success(signedOrderService.findById(orderId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/SignatureService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/SignatureService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class SignatureService {

    private static final Duration ALLOWED_SKEW = Duration.ofMinutes(5);

    private final InMemoryAppCredentialRepository credentialRepository;
    private final InMemoryNonceStore nonceStore;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SignatureService(InMemoryAppCredentialRepository credentialRepository, InMemoryNonceStore nonceStore) {
        this(credentialRepository, nonceStore, Clock.systemUTC());
    }

    public SignatureService(InMemoryAppCredentialRepository credentialRepository, InMemoryNonceStore nonceStore, Clock clock) {
        this.credentialRepository = credentialRepository;
        this.nonceStore = nonceStore;
        this.clock = clock;
    }

    public String sign(String method, String path, String timestamp, String nonce, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            byte[] digest = mac.doFinal(canonical(method, path, timestamp, nonce).getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(digest);
        } catch (Exception ex) {
            throw new IllegalStateException("签名生成失败", ex);
        }
    }

    public String signForApp(String appId, String method, String path, String timestamp, String nonce) {
        AppCredential credential = credentialRepository.findByAppId(appId)
                .orElseThrow(() -> new SignatureException(401, "未知 appId"));
        return sign(method, path, timestamp, nonce, credential.getSecret());
    }

    public String canonical(String method, String path, String timestamp, String nonce) {
        return method.toUpperCase() + "\n" + path + "\n" + timestamp + "\n" + nonce;
    }

    public SignatureValidationResult validate(SignatureRequest request) {
        requireText(request.getAppId(), "X-App-Id 不能为空");
        requireText(request.getTimestamp(), "X-Timestamp 不能为空");
        requireText(request.getNonce(), "X-Nonce 不能为空");
        requireText(request.getSignature(), "X-Signature 不能为空");

        AppCredential credential = credentialRepository.findByAppId(request.getAppId())
                .orElseThrow(() -> new SignatureException(401, "未知 appId"));

        validateTimestamp(request.getTimestamp());

        String expected = sign(
                request.getMethod(),
                request.getPath(),
                request.getTimestamp(),
                request.getNonce(),
                credential.getSecret()
        );
        if (!MessageDigest.isEqual(
                expected.getBytes(StandardCharsets.UTF_8),
                request.getSignature().getBytes(StandardCharsets.UTF_8)
        )) {
            throw new SignatureException(401, "signature 不匹配");
        }

        if (!nonceStore.consume(request.getAppId(), request.getNonce())) {
            throw new SignatureException(401, "nonce 已被使用");
        }
        return new SignatureValidationResult(request.getAppId(), request.getMethod().toUpperCase(), request.getPath());
    }

    private void validateTimestamp(String timestamp) {
        long requestTime;
        try {
            requestTime = Long.parseLong(timestamp);
        } catch (NumberFormatException ex) {
            throw new SignatureException(401, "timestamp 格式错误");
        }
        long delta = Math.abs(clock.millis() - requestTime);
        if (delta > ALLOWED_SKEW.toMillis()) {
            throw new SignatureException(401, "timestamp 已过期");
        }
    }

    private void requireText(String value, String message) {
        if (!StringUtils.hasText(value)) {
            throw new SignatureException(401, message);
        }
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/SignedOrderService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/SignedOrderService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class SignedOrderService {

    private final Map<String, SignedOrder> orders = new LinkedHashMap<>();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SignedOrderService() {
        orders.put("1001", new SignedOrder("1001", "签名接口课程", new BigDecimal("129.90"), "PAID"));
        orders.put("1002", new SignedOrder("1002", "防重放实践", new BigDecimal("99.00"), "CREATED"));
    }

    public SignedOrder findById(String orderId) {
        SignedOrder order = orders.get(orderId);
        if (order == null) {
            throw new NoSuchElementException("订单不存在: " + orderId);
        }
        return order;
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 请求拦截：进入 Controller 前做什么

源码位置：`src/main/java/com/cloud/web/SignatureAuthInterceptor.java`

拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。

```java
// 文件：com/cloud/web/SignatureAuthInterceptor.java
// 学习重点：拦截器运行在 Controller 前后，适合做鉴权、租户、日志、上下文清理。
@Component
public class SignatureAuthInterceptor implements HandlerInterceptor {

    private final SignatureService signatureService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SignatureAuthInterceptor(SignatureService signatureService) {
        this.signatureService = signatureService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String path = request.getRequestURI();
        String contextPath = request.getContextPath();
        if (contextPath != null && !contextPath.isEmpty() && path.startsWith(contextPath)) {
            path = path.substring(contextPath.length());
        }
        signatureService.validate(new SignatureRequest(
                request.getHeader("X-App-Id"),
                request.getMethod(),
                path,
                request.getHeader("X-Timestamp"),
                request.getHeader("X-Nonce"),
                request.getHeader("X-Signature")
        ));
        return true;
    }
}
```

关键点拆解：

- 前置处理负责准备上下文，后置处理负责清理资源；这两个动作要成对出现。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. SignatureAuthInterceptor：请求进入 Controller 前准备上下文或校验
2. RequestSignatureController：接收 HTTP 请求并转换成 Java 方法调用
3. SignatureService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/signature`：模块说明
- `GET /api/signature/demo-signature`：生成 demo 签名
- `GET /api/signature/orders/{orderId}`：受签名保护的订单查询

## 调用验证

```bash
curl "http://localhost:8120/api/signature/demo-signature?method=GET&path=/api/signature/orders/1001&timestamp=1714450000000&nonce=nonce-001&appId=demo-app"
```

调用受保护接口时带上签名头：

```bash
curl "http://localhost:8120/api/signature/orders/1001" \
  -H "X-App-Id: demo-app" \
  -H "X-Timestamp: <current-millis>" \
  -H "X-Nonce: <unique-nonce>" \
  -H "X-Signature: <base64-hmac>"
```

同一个 `appId + nonce` 只能使用一次，重复请求会返回 401。

## 生产差距

该示例用于隔离学习 请求签名与重放防护 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 40-SpringBoot-request-signature-replay test
```

## 要点总结

1. `X-App-Id` 标识调用方
2. `X-Timestamp` 控制 5 分钟时间窗
3. `X-Nonce` 保证一次性请求
4. `X-Signature` 使用 HMAC-SHA256 生成
5. Spring MVC `HandlerInterceptor` 保护业务接口

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
