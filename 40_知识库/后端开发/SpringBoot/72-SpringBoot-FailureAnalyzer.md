---
title: SpringBoot FailureAnalyzer
date: 2026-05-11
tags:
  - springboot
  - java
module: 72-SpringBoot-failure-analyzer
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot FailureAnalyzer

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/72-SpringBoot-failure-analyzer`

## 核心思路

本模块演示 Spring Boot 启动失败诊断机制：业务代码抛出一个有语义的启动异常，`FailureAnalyzer` 把异常转换成可读的失败说明和修复动作。

## 能力点

- `FailureAnalyzer`
- `AbstractFailureAnalyzer`
- `FailureAnalysis`
- `META-INF/spring.factories`
- 启动 fail-fast 校验
- typed exception 携带诊断上下文
- MockMvc 模拟失败分析结果

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot FailureAnalyzer 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/FailureAnalyzerController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/FailureAnalyzerController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/failure-analyzer")
public class FailureAnalyzerController {
    private final TenantStartupProperties properties;
    private final TenantStartupValidator validator;
    private final MissingTenantConfigurationFailureAnalyzer analyzer = new MissingTenantConfigurationFailureAnalyzer();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public FailureAnalyzerController(TenantStartupProperties properties, TenantStartupValidator validator) {
        this.properties = properties;
        this.validator = validator;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "72-SpringBoot-failure-analyzer",
                "apis", List.of(
                        "GET /api/failure-analyzer",
                        "GET /api/failure-analyzer/properties",
                        "POST /api/failure-analyzer/validate",
                        "POST /api/failure-analyzer/analyze"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/properties")
    public ApiResult<TenantStartupProperties> properties() {
        return ApiResult.success(properties);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/validate")
    public ApiResult<Map<String, Object>> validateCurrentProperties() {
        try {
            validator.validate(properties);
            return ApiResult.success(Map.of("valid", true));
        } catch (MissingTenantConfigurationException exception) {
            return ApiResult.success(Map.of(
                    "valid", false,
                    "error", exception.getMessage()
            ));
        }
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/analyze")
    public ApiResult<Map<String, Object>> analyze(@RequestParam(defaultValue = "true") boolean failFast,
                                                  @RequestParam(required = false) String tenantId,
                                                  @RequestParam(defaultValue = TenantStartupProperties.DEFAULT_SUPPORT_URL)
                                                  String supportUrl) {
        TenantStartupProperties request = new TenantStartupProperties();
        request.setFailFast(failFast);
        request.setTenantId(tenantId);
        request.setSupportUrl(supportUrl);

        try {
            validator.validate(request);
            return ApiResult.success(Map.of("valid", true));
        } catch (MissingTenantConfigurationException exception) {
            FailureAnalysis analysis = analyzer.analyze(exception);
            return ApiResult.success(Map.of(
                    "valid", false,
                    "exception", exception.getClass().getSimpleName(),
                    "description", analysis.getDescription(),
                    "action", analysis.getAction()
            ));
        }
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/diagnostics/MissingTenantConfigurationFailureAnalyzer.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/diagnostics/MissingTenantConfigurationFailureAnalyzer.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
public class MissingTenantConfigurationFailureAnalyzer
        extends AbstractFailureAnalyzer<MissingTenantConfigurationException> {
    @Override
    protected FailureAnalysis analyze(Throwable rootFailure, MissingTenantConfigurationException cause) {
        String description = "Tenant startup validation failed because required property "
                + cause.getPropertyName() + " is missing.";
        String action = "Set " + cause.getPropertyName()
                + " when demo.tenant.fail-fast=true. Runbook: " + cause.getSupportUrl();
        return new FailureAnalysis(description, action, cause);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/diagnostics/TenantStartupConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/diagnostics/TenantStartupConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
@EnableConfigurationProperties(TenantStartupProperties.class)
public class TenantStartupConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public TenantStartupValidator tenantStartupValidator() {
        return new TenantStartupValidator();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public ApplicationRunner tenantStartupValidationRunner(TenantStartupProperties properties,
                                                          TenantStartupValidator validator) {
        // Default fail-fast is false so the learning module starts normally; tests and APIs opt into failure analysis.
        return args -> validator.validate(properties);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置绑定：application.yml 如何进入 Java 对象

源码位置：`src/main/java/com/cloud/diagnostics/TenantStartupProperties.java`

Properties 类把配置文件里的字符串变成类型安全的 Java 字段。

```java
// 文件：com/cloud/diagnostics/TenantStartupProperties.java
// 学习重点：Properties 类把配置文件里的字符串变成类型安全的 Java 字段。
@Data
// 把 application.yml/properties 中同前缀的配置绑定到这个对象。
@ConfigurationProperties(prefix = "demo.tenant")
public class TenantStartupProperties {
    public static final String TENANT_ID_PROPERTY = "demo.tenant.tenant-id";
    public static final String DEFAULT_SUPPORT_URL = "https://internal.example.com/runbooks/tenant-config";

    private boolean failFast = false;
    private String tenantId;
    private String supportUrl = DEFAULT_SUPPORT_URL;
}
```

关键点拆解：

- 配置字段最好有默认值和边界校验，否则线上配置错误会变成隐蔽故障。
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

- `GET /api/failure-analyzer`：模块说明
- `GET /api/failure-analyzer/properties`：当前租户启动配置
- `POST /api/failure-analyzer/validate`：校验当前配置
- `POST /api/failure-analyzer/analyze`：模拟缺失 tenant id 的失败分析

## 调用验证

```bash
curl "http://localhost:8152/api/failure-analyzer"
```

```bash
curl "http://localhost:8152/api/failure-analyzer/properties"
```

```bash
curl -X POST "http://localhost:8152/api/failure-analyzer/validate"
```

```bash
curl -X POST "http://localhost:8152/api/failure-analyzer/analyze?failFast=true"
```

返回的 `description` 会说明缺失 `demo.tenant.tenant-id`，`action` 会给出配置建议和 runbook 地址。

## 生产映射

生产系统可以把这个模式用于：

- 缺少数据库、消息队列、租户或外部服务关键配置时快速失败
- 把长堆栈转换成面向运维和开发的明确修复动作
- 给启动失败绑定 runbook、配置项名和排障上下文
- 避免用户只看到底层 `IllegalStateException` 或绑定异常

## 生产差距

该示例用于隔离学习 FailureAnalyzer 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 72-SpringBoot-failure-analyzer test
```

测试覆盖：

- fail-fast 关闭时缺少 tenant id 也能通过
- fail-fast 开启且 tenant id 存在时通过
- fail-fast 开启且 tenant id 为空时抛出 typed exception
- analyzer 输出 description、action 和 cause
- `spring.factories` 注册内容
- Web API 的元信息、属性、校验和模拟分析

## 要点总结

1. `FailureAnalyzer`
2. `AbstractFailureAnalyzer`
3. `FailureAnalysis`
4. `META-INF/spring.factories`
5. 启动 fail-fast 校验

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
