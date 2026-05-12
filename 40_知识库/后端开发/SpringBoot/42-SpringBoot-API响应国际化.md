---
title: SpringBoot API响应国际化
date: 2026-05-11
tags:
  - springboot
  - java
  - 国际化
module: 42-SpringBoot-api-response-i18n
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot API响应国际化

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/42-SpringBoot-api-response-i18n`

## 核心思路

本模块演示 API 响应消息国际化：错误码保持稳定，`message` 和字段校验消息根据 `Accept-Language` 返回中文或英文。

## 能力点

- `Accept-Language` 解析请求语言
- `MessageSource` 管理中英文消息
- 稳定错误码与本地化消息分离
- Bean Validation 字段错误国际化
- 业务异常消息国际化

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot API响应国际化 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ApiResponseI18nController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ApiResponseI18nController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/i18n")
public class ApiResponseI18nController {

    private final I18nMessageService messageService;
    private final I18nUserService userService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ApiResponseI18nController(I18nMessageService messageService, I18nUserService userService) {
        this.messageService = messageService;
        this.userService = userService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "42-SpringBoot-api-response-i18n");
        data.put("desc", messageService.message("module.desc"));
        data.put("apis", new String[]{"POST /api/i18n/users"});
        return ApiResult.of(ErrorCode.SUCCESS.getCode(), messageService.message(ErrorCode.SUCCESS), data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/users")
    public ApiResult<UserCreatedResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        return ApiResult.of(
                ErrorCode.SUCCESS.getCode(),
                messageService.message(ErrorCode.SUCCESS),
                userService.createUser(request)
        );
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/i18n/I18nMessageService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/i18n/I18nMessageService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class I18nMessageService {

    private final MessageSource messageSource;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public I18nMessageService(MessageSource messageSource) {
        this.messageSource = messageSource;
    }

    public String message(ErrorCode errorCode) {
        return message(errorCode, LocaleContextHolder.getLocale());
    }

    public String message(ErrorCode errorCode, Locale locale) {
        return message(errorCode.getMessageKey(), locale);
    }

    public String message(String key) {
        return message(key, LocaleContextHolder.getLocale());
    }

    public String message(String key, Locale locale) {
        return messageSource.getMessage(key, null, locale);
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/I18nUserService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/I18nUserService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class I18nUserService {

    public UserCreatedResponse createUser(CreateUserRequest request) {
        if ("admin".equalsIgnoreCase(request.getUsername())) {
            throw new BusinessException(ErrorCode.USER_DUPLICATE);
        }
        return new UserCreatedResponse(request.getUsername(), request.getEmail(), request.getAge(), "CREATED");
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/LocaleConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/LocaleConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class LocaleConfig {

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public MessageSource messageSource() {
        ResourceBundleMessageSource messageSource = new ResourceBundleMessageSource();
        messageSource.setBasename("messages");
        messageSource.setDefaultEncoding(StandardCharsets.UTF_8.name());
        messageSource.setDefaultLocale(Locale.SIMPLIFIED_CHINESE);
        return messageSource;
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public LocaleResolver localeResolver() {
        AcceptHeaderLocaleResolver resolver = new AcceptHeaderLocaleResolver();
        resolver.setDefaultLocale(Locale.SIMPLIFIED_CHINESE);
        resolver.setSupportedLocales(List.of(Locale.SIMPLIFIED_CHINESE, Locale.US));
        return resolver;
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. LocaleConfig：启动时注册配置、Bean 或扩展点
2. ApiResponseI18nController：接收 HTTP 请求并转换成 Java 方法调用
3. I18nMessageService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/i18n`：模块说明
- `POST /api/i18n/users`：创建用户，演示校验错误和业务错误国际化

## 调用验证

默认中文：

```bash
curl "http://localhost:8122/api/i18n"
```

英文：

```bash
curl "http://localhost:8122/api/i18n" \
  -H "Accept-Language: en-US"
```

英文校验错误：

```bash
curl -X POST "http://localhost:8122/api/i18n/users" \
  -H "Accept-Language: en-US" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 生产差距

该示例用于隔离学习 API响应国际化 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 42-SpringBoot-api-response-i18n test
```

## 要点总结

1. `Accept-Language` 解析请求语言
2. `MessageSource` 管理中英文消息
3. 稳定错误码与本地化消息分离
4. Bean Validation 字段错误国际化
5. 业务异常消息国际化

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
