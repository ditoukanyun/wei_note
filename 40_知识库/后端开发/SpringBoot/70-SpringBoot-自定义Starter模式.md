---
title: SpringBoot 自定义Starter模式
date: 2026-05-11
tags:
  - springboot
  - java
  - starter
module: 70-SpringBoot-custom-starter-pattern
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 自定义Starter模式

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/70-SpringBoot-custom-starter-pattern`

## 核心思路

本模块演示 Spring Boot 3 自定义 starter 的核心结构：starter 代码放在应用扫描包之外，通过 `AutoConfiguration.imports` 导入自动配置，再用条件注解和用户 Bean 覆盖点完成可插拔装配。

## 能力点

- starter 风格包结构
- `AutoConfiguration.imports`
- `@AutoConfiguration`
- `@EnableConfigurationProperties`
- `@ConditionalOnProperty`
- `@ConditionalOnMissingBean`
- `ApplicationContextRunner` 自动配置测试
- 应用侧通过依赖注入消费 starter bean

## 结构与链路

应用代码在 `com.cloud` 包下：

- `com.cloud.Application`
- `com.cloud.controller.CustomStarterController`
- `com.cloud.common.ApiResult`

starter 风格代码在 `com.demo.audit` 包下，刻意放在 `com.cloud` 扫描路径之外：

- `AuditClient`：starter 暴露给业务方的接口
- `AuditCommand`：审计命令
- `AuditResult`：审计结果
- `DefaultAuditClient`：默认实现
- `AuditProperties`：`demo.audit` 配置绑定
- `AuditAutoConfiguration`：自动配置入口

这能证明 bean 不是靠应用包扫描注册，而是通过自动配置机制加载。

## 关键实现

Spring Boot 3 starter 使用如下文件注册自动配置类：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

文件内容：

```text
com.demo.audit.autoconfigure.AuditAutoConfiguration
```

`AuditAutoConfiguration` 负责：

- 绑定 `demo.audit.*` 到 `AuditProperties`
- `demo.audit.enabled=false` 时关闭默认 bean
- 缺少用户自定义 `AuditClient` 时创建 `DefaultAuditClient`

## 配置要点

Spring Boot 3 starter 使用如下文件注册自动配置类：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

文件内容：

```text
com.demo.audit.autoconfigure.AuditAutoConfiguration
```

`AuditAutoConfiguration` 负责：

- 绑定 `demo.audit.*` 到 `AuditProperties`
- `demo.audit.enabled=false` 时关闭默认 bean
- 缺少用户自定义 `AuditClient` 时创建 `DefaultAuditClient`

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 自定义Starter模式 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。
- starter/自动配置案例重点看条件注解、配置绑定和用户覆盖点。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 自动配置入口：Starter 如何装配 Bean

源码位置：`src/main/java/com/demo/audit/autoconfigure/AuditAutoConfiguration.java`

AutoConfiguration 是 starter 的核心，它决定“什么条件下自动创建哪些 Bean”。

```java
// 文件：com/demo/audit/autoconfigure/AuditAutoConfiguration.java
// 学习重点：AutoConfiguration 是 starter 的核心，它决定“什么条件下自动创建哪些 Bean”。
@AutoConfiguration
@EnableConfigurationProperties(AuditProperties.class)
// 通过配置开关控制这个 Bean 或配置类是否生效。
@ConditionalOnProperty(prefix = "demo.audit", name = "enabled", havingValue = "true", matchIfMissing = true)
public class AuditAutoConfiguration {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    // 只有容器里还没有同类型 Bean 时才创建默认实现，给业务方留下覆盖点。
    @ConditionalOnMissingBean
    public AuditClient auditClient(AuditProperties properties) {
        // @ConditionalOnMissingBean leaves the extension point open for applications to provide their own client.
        return new DefaultAuditClient(properties);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/CustomStarterController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/CustomStarterController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/custom-starter")
public class CustomStarterController {
    private final AuditClient auditClient;
    private final AuditProperties auditProperties;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CustomStarterController(AuditClient auditClient, AuditProperties auditProperties) {
        this.auditClient = auditClient;
        this.auditProperties = auditProperties;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "70-SpringBoot-custom-starter-pattern",
                "apis", List.of(
                        "GET /api/custom-starter",
                        "GET /api/custom-starter/properties",
                        "POST /api/custom-starter/audit"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/properties")
    public ApiResult<Map<String, Object>> properties() {
        return ApiResult.success(Map.of(
                "enabled", auditProperties.isEnabled(),
                "prefix", auditProperties.getPrefix(),
                "destination", auditProperties.getDestination()
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/audit")
    public ApiResult<AuditResult> audit(@RequestParam String actor,
                                        @RequestParam String action,
                                        @RequestParam String resourceId) {
        AuditResult result = auditClient.emit(new AuditCommand(actor, action, resourceId));
        return ApiResult.success(result);
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置绑定：application.yml 如何进入 Java 对象

源码位置：`src/main/java/com/demo/audit/autoconfigure/AuditProperties.java`

Properties 类把配置文件里的字符串变成类型安全的 Java 字段。

```java
// 文件：com/demo/audit/autoconfigure/AuditProperties.java
// 学习重点：Properties 类把配置文件里的字符串变成类型安全的 Java 字段。
@Data
// 把 application.yml/properties 中同前缀的配置绑定到这个对象。
@ConfigurationProperties(prefix = "demo.audit")
public class AuditProperties {
    private boolean enabled = true;
    private String prefix = "audit";
    private String destination = "memory";
}
```

关键点拆解：

- 配置字段最好有默认值和边界校验，否则线上配置错误会变成隐蔽故障。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：AuditClient

源码位置：`src/main/java/com/demo/audit/AuditClient.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/demo/audit/AuditClient.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public interface AuditClient {
    AuditResult emit(AuditCommand command);
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
- 把框架扩展点当普通业务代码使用，后续排查启动问题会很困难。

## API 接口

- `GET /api/custom-starter`：模块说明
- `GET /api/custom-starter/properties`：返回当前 starter 配置
- `POST /api/custom-starter/audit`：通过自动配置的 `AuditClient` 发射审计事件

## 调用验证

```bash
curl "http://localhost:8150/api/custom-starter"
```

```bash
curl "http://localhost:8150/api/custom-starter/properties"
```

```bash
curl -X POST "http://localhost:8150/api/custom-starter/audit?actor=u-100&action=CREATE_ORDER&resourceId=O-100"
```

示例响应中的 `auditId` 会以 `starter-audit-` 开头，说明配置属性已经绑定到默认客户端。

## 生产映射

生产 starter 通常会把本模块的 `AuditClient` 换成真实基础设施客户端，例如：

- 审计日志 SDK
- 消息投递客户端
- 企业统一追踪客户端
- 统一风控或合规模块

starter 保持默认可用，业务系统通过配置开关、属性绑定和用户 Bean 覆盖来调整行为。

## 生产差距

该示例用于隔离学习 自定义Starter模式 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 70-SpringBoot-custom-starter-pattern test
```

测试覆盖：

- 默认启用时创建 `AuditClient`
- `demo.audit.enabled=false` 时不创建默认客户端
- 用户自定义 `AuditClient` 覆盖默认实现
- `demo.audit.prefix` 和 `demo.audit.destination` 属性绑定
- MockMvc 验证应用接口能消费自动配置 bean

## 要点总结

1. starter 风格包结构
2. `AutoConfiguration.imports`
3. `@AutoConfiguration`
4. `@EnableConfigurationProperties`
5. `@ConditionalOnProperty`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
