---
title: SpringBoot 配置属性校验
date: 2026-05-11
tags:
  - springboot
  - java
  - 校验
  - 配置
module: 68-SpringBoot-configuration-properties-validation
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 配置属性校验

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/68-SpringBoot-configuration-properties-validation`

## 核心思路

本模块演示 Spring Boot 类型化配置的常见生产写法：`@ConfigurationProperties`、嵌套属性、Bean Validation、启动期失败诊断和安全配置展示。

## 能力点

- `@ConfigurationProperties`
- `@ConfigurationPropertiesScan`
- `@Validated`
- `@Valid`
- Bean Validation 注解
- 嵌套配置对象
- `ApplicationContextRunner`
- 配置快照脱敏

## 配置要点

配置前缀：`demo.payment`

```yaml
demo:
  payment:
    enabled: true
    merchant-id: M10086
    endpoint-url: https://pay.example.internal/api
    timeout-ms: 1500
    retry:
      max-attempts: 3
      backoff-ms: 200
    security:
      signing-key: demo-signing-key-2026
      allowed-currencies:
        - CNY
        - USD
```

核心规则：

- `merchantId` 不能为空
- `endpointUrl` 必须以 `https://` 开头
- `timeoutMs` 必须在 `100` 到 `10000` 之间
- `retry.maxAttempts` 必须在 `1` 到 `5` 之间
- `retry.backoffMs` 必须在 `50` 到 `5000` 之间
- `security.signingKey` 至少 16 位
- `security.allowedCurrencies` 至少包含一个 3 位大写币种码

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 配置属性校验 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ConfigValidationController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ConfigValidationController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/config-validation")
public class ConfigValidationController {
    private final PaymentConfigInspectionService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ConfigValidationController(PaymentConfigInspectionService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "68-SpringBoot-configuration-properties-validation");
        data.put("desc", "类型化配置、嵌套属性、Bean Validation 和失败诊断");
        data.put("apis", new String[]{
                "GET /api/config-validation",
                "GET /api/config-validation/properties",
                "GET /api/config-validation/rules"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/properties")
    public ApiResult<PaymentConfigSnapshot> properties() {
        return ApiResult.success(service.snapshot());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/rules")
    public ApiResult<List<String>> rules() {
        return ApiResult.success(service.validationRules());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/PaymentConfigInspectionService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/PaymentConfigInspectionService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class PaymentConfigInspectionService {
    private final PaymentGatewayProperties properties;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public PaymentConfigInspectionService(PaymentGatewayProperties properties) {
        this.properties = properties;
    }

    public PaymentConfigSnapshot snapshot() {
        return new PaymentConfigSnapshot(
                properties.isEnabled(),
                properties.getMerchantId(),
                properties.getEndpointUrl(),
                properties.getTimeoutMs(),
                properties.getRetry().getMaxAttempts(),
                properties.getRetry().getBackoffMs(),
                mask(properties.getSecurity().getSigningKey()),
                properties.getSecurity().getAllowedCurrencies()
        );
    }

    public List<String> validationRules() {
        return List.of(
                "merchantId must not be blank",
                "endpointUrl must start with https://",
                "timeoutMs must be between 100 and 10000",
                "retry.maxAttempts must be between 1 and 5",
                "retry.backoffMs must be between 50 and 5000",
                "security.signingKey must contain at least 16 characters",
                "security.allowedCurrencies must contain at least one ISO-style 3-letter code"
        );
    }

    private String mask(String value) {
        if (value == null || value.length() <= 8) {
            return "********";
        }
        return value.substring(0, 4) + "*".repeat(value.length() - 8) + value.substring(value.length() - 4);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/PaymentConfigSnapshot.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/PaymentConfigSnapshot.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentConfigSnapshot {
    private boolean enabled;
    private String merchantId;
    private String endpointUrl;
    private int timeoutMs;
    private int retryMaxAttempts;
    private int retryBackoffMs;
    private String signingKeyMasked;
    private List<String> allowedCurrencies;
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置绑定：application.yml 如何进入 Java 对象

源码位置：`src/main/java/com/cloud/config/PaymentGatewayProperties.java`

Properties 类把配置文件里的字符串变成类型安全的 Java 字段。

```java
// 文件：com/cloud/config/PaymentGatewayProperties.java
// 学习重点：Properties 类把配置文件里的字符串变成类型安全的 Java 字段。
@Data
@Validated
// 把 application.yml/properties 中同前缀的配置绑定到这个对象。
@ConfigurationProperties(prefix = "demo.payment")
public class PaymentGatewayProperties {
    private boolean enabled;

    @NotBlank(message = "merchantId 不能为空")
    private String merchantId;

    @NotBlank(message = "endpointUrl 不能为空")
    @Pattern(regexp = "^https://.+", message = "endpointUrl 必须使用 https")
    private String endpointUrl;

    @Min(value = 100, message = "timeoutMs 不能小于 100")
    @Max(value = 10000, message = "timeoutMs 不能大于 10000")
    private int timeoutMs;

    // @Valid is required so Bean Validation cascades into nested configuration objects during binding.
    @Valid
    private Retry retry = new Retry();

    @Valid
    private Security security = new Security();

    @Data
    public static class Retry {
        @Min(value = 1, message = "maxAttempts 不能小于 1")
        @Max(value = 5, message = "maxAttempts 不能大于 5")
        private int maxAttempts;

        @Min(value = 50, message = "backoffMs 不能小于 50")
        @Max(value = 5000, message = "backoffMs 不能大于 5000")
        private int backoffMs;
    }

    @Data
    public static class Security {
        @NotBlank(message = "signingKey 不能为空")
        @Size(min = 16, message = "signingKey 至少 16 位")
        private String signingKey;

        @NotEmpty(message = "allowedCurrencies 不能为空")
        private List<@Pattern(regexp = "^[A-Z]{3}$", message = "currency 必须是 3 位大写字母") String> allowedCurrencies =
                new ArrayList<>();
    }
}
```

关键点拆解：

- 配置字段最好有默认值和边界校验，否则线上配置错误会变成隐蔽故障。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. ConfigValidationController：启动时注册配置、Bean 或扩展点
2. ConfigValidationController：接收 HTTP 请求并转换成 Java 方法调用
3. PaymentConfigInspectionService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/config-validation`：模块说明
- `GET /api/config-validation/properties`：查看绑定后的安全配置快照
- `GET /api/config-validation/rules`：查看校验规则

## 调用验证

```bash
curl "http://localhost:8148/api/config-validation"
```

```bash
curl "http://localhost:8148/api/config-validation/properties"
```

```bash
curl "http://localhost:8148/api/config-validation/rules"
```

`properties` 接口只返回脱敏后的 `signingKeyMasked`，不会直接暴露原始签名 key。

## 生产映射

生产项目中推荐优先使用类型化配置，而不是散落的 `@Value`：

- 配置字段集中，便于审查
- 启动时快速失败，避免运行时才暴露错误配置
- 嵌套配置表达领域边界更清楚
- API 或诊断页面可以展示脱敏后的配置快照

## 生产差距

该示例用于隔离学习 配置属性校验 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 68-SpringBoot-configuration-properties-validation test
```

测试覆盖：

- 类型化配置绑定
- 非法配置启动失败
- 嵌套配置校验
- 安全配置脱敏
- 配置规则 API

## 要点总结

1. `@ConfigurationProperties`
2. `@ConfigurationPropertiesScan`
3. `@Validated`
4. `@Valid`
5. Bean Validation 注解

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
