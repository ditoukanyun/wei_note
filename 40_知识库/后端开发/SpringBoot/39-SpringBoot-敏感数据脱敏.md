---
title: SpringBoot 敏感数据脱敏
date: 2026-05-11
tags:
  - springboot
  - java
  - 脱敏
module: 39-SpringBoot-sensitive-data-mask
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 敏感数据脱敏

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/39-SpringBoot-sensitive-data-mask`

## 核心思路

本模块演示在 Spring Boot 响应序列化阶段做敏感数据脱敏：服务层保留原始客户资料，Controller 返回对象时由 Jackson 根据字段注解统一输出脱敏值。

## 能力点

- `@SensitiveField` 标记敏感字段
- `SensitiveType` 区分姓名、手机号、邮箱、身份证、银行卡
- `BeanSerializerModifier` 包装 Jackson 字段写入逻辑
- 服务层原始值不被修改，只在 JSON 响应中脱敏

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 敏感数据脱敏 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/SensitiveDataMaskController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/SensitiveDataMaskController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/mask")
public class SensitiveDataMaskController {

    private final CustomerProfileService customerProfileService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SensitiveDataMaskController(CustomerProfileService customerProfileService) {
        this.customerProfileService = customerProfileService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "39-SpringBoot-sensitive-data-mask");
        data.put("desc", "响应序列化阶段的敏感数据脱敏示例");
        data.put("apis", new String[]{
                "GET /api/mask/customers/{id}",
                "GET /api/mask/customers/{id}/raw-check"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/customers/{id}")
    public ApiResult<CustomerProfile> customer(@PathVariable Long id) {
        return ApiResult.success(customerProfileService.findById(id));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/customers/{id}/raw-check")
    public ApiResult<RawCheckResponse> rawCheck(@PathVariable Long id) {
        return ApiResult.success(customerProfileService.rawCheck(id));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/CustomerProfileService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/CustomerProfileService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class CustomerProfileService {

    private final Map<Long, CustomerProfile> customers = new LinkedHashMap<>();

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CustomerProfileService() {
        customers.put(1L, new CustomerProfile(
                1L,
                "张三",
                "13812345678",
                "alice@example.com",
                "330102199001017890",
                "6222000000001234"
        ));
        customers.put(2L, new CustomerProfile(
                2L,
                "李四",
                "13900001111",
                "bob@example.com",
                "110101199909091234",
                "6225888800005678"
        ));
    }

    public CustomerProfile findById(Long id) {
        CustomerProfile profile = customers.get(id);
        if (profile == null) {
            throw new NoSuchElementException("客户不存在: " + id);
        }
        return profile;
    }

    public RawCheckResponse rawCheck(Long id) {
        CustomerProfile profile = findById(id);
        return new RawCheckResponse(profile.getPhone(), true);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/SensitiveMaskingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/SensitiveMaskingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class SensitiveMaskingService {

    public String mask(String value, SensitiveType type) {
        if (value == null || value.isEmpty()) {
            return value;
        }
        return switch (type) {
            case NAME -> maskName(value);
            case PHONE -> maskPhone(value);
            case EMAIL -> maskEmail(value);
            case ID_CARD -> maskIdCard(value);
            case BANK_CARD -> maskBankCard(value);
        };
    }

    private String maskName(String value) {
        if (value.length() == 1) {
            return "*";
        }
        return value.charAt(0) + "*";
    }

    private String maskPhone(String value) {
        if (value.length() < 7) {
            return "*".repeat(value.length());
        }
        return value.substring(0, 3) + "****" + value.substring(value.length() - 4);
    }

    private String maskEmail(String value) {
        int atIndex = value.indexOf('@');
        if (atIndex <= 0) {
            return "*".repeat(value.length());
        }
        String account = value.substring(0, atIndex);
        String domain = value.substring(atIndex);
        if (account.length() == 1) {
            return "*" + domain;
        }
        return account.charAt(0) + "***" + account.charAt(account.length() - 1) + domain;
    }

    private String maskIdCard(String value) {
        if (value.length() < 7) {
            return "*".repeat(value.length());
        }
        return value.substring(0, 3) + "************" + value.substring(value.length() - 4);
    }

    private String maskBankCard(String value) {
        String digits = value.replace(" ", "");
        if (digits.length() < 8) {
            return "*".repeat(digits.length());
        }
        return digits.substring(0, 4) + " **** **** " + digits.substring(digits.length() - 4);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/JacksonMaskingConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/JacksonMaskingConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class JacksonMaskingConfig {

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public Jackson2ObjectMapperBuilderCustomizer sensitiveDataMaskingCustomizer(SensitiveMaskingService maskingService) {
        return builder -> {
            SimpleModule module = new SimpleModule();
            module.setSerializerModifier(new SensitiveDataSerializerModifier(maskingService));
            builder.modules(module);
        };
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. JacksonMaskingConfig：启动时注册配置、Bean 或扩展点
2. SensitiveDataMaskController：接收 HTTP 请求并转换成 Java 方法调用
3. CustomerProfileService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/mask`：模块说明
- `GET /api/mask/customers/{id}`：查询客户资料，响应自动脱敏
- `GET /api/mask/customers/{id}/raw-check`：验证服务层仍可读取原始手机号

## 调用验证

```bash
curl "http://localhost:8119/api/mask/customers/1"
```

响应中的 `name`、`phone`、`email`、`idCard`、`bankCard` 会被脱敏。

```bash
curl "http://localhost:8119/api/mask/customers/1/raw-check"
```

该接口返回服务层读取到的原始手机号，用于对比“存储/业务处理原值，响应输出脱敏”的边界。

## 生产差距

该示例用于隔离学习 敏感数据脱敏 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 39-SpringBoot-sensitive-data-mask test
```

## 要点总结

1. `@SensitiveField` 标记敏感字段
2. `SensitiveType` 区分姓名、手机号、邮箱、身份证、银行卡
3. `BeanSerializerModifier` 包装 Jackson 字段写入逻辑
4. 服务层原始值不被修改，只在 JSON 响应中脱敏

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
