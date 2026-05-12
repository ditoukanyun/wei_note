---
title: SpringBoot 参数校验与错误码
date: 2026-05-11
tags:
  - springboot
  - java
  - 校验
module: 41-SpringBoot-validation-error-code
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 参数校验与错误码

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/41-SpringBoot-validation-error-code`

## 核心思路

本模块演示企业接口常见的统一参数校验、错误码和业务异常响应。

## 能力点

- Bean Validation 字段校验
- 统一字符串错误码
- 字段级错误明细
- 业务异常到 HTTP 状态码映射
- 全局异常处理器

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 参数校验与错误码 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ValidationDemoController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ValidationDemoController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/validation")
public class ValidationDemoController {

    private final ValidationDemoService validationDemoService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ValidationDemoController(ValidationDemoService validationDemoService) {
        this.validationDemoService = validationDemoService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "41-SpringBoot-validation-error-code");
        data.put("desc", "统一参数校验、错误码和业务异常响应");
        data.put("apis", new String[]{"POST /api/validation/users"});
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/users")
    public ApiResult<UserCreatedResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        return ApiResult.success(validationDemoService.createUser(request));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ValidationDemoService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ValidationDemoService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ValidationDemoService {

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

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResult<ValidationErrorResponse>> handleValidation(MethodArgumentNotValidException ex) {
        List<FieldErrorItem> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .map(error -> new FieldErrorItem(error.getField(), error.getCode(), error.getDefaultMessage()))
                .sorted(Comparator.comparing(FieldErrorItem::getField))
                .toList();
        ErrorCode errorCode = ErrorCode.VALIDATION_FAILED;
        return ResponseEntity.status(errorCode.getHttpStatus())
                .body(ApiResult.fail(errorCode, new ValidationErrorResponse(fieldErrors)));
    }

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResult<Void>> handleBusiness(BusinessException ex) {
        ErrorCode errorCode = ex.getErrorCode();
        return ResponseEntity.status(errorCode.getHttpStatus()).body(ApiResult.fail(errorCode));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResult<Void>> handleException(Exception ex) {
        log.error("Unhandled exception", ex);
        ErrorCode errorCode = ErrorCode.SYSTEM_ERROR;
        return ResponseEntity.status(errorCode.getHttpStatus()).body(ApiResult.fail(errorCode));
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：CreateUserRequest

源码位置：`src/main/java/com/cloud/model/CreateUserRequest.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/model/CreateUserRequest.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Data
public class CreateUserRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在 3 到 20 个字符之间")
    private String username;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于 18")
    @Max(value = 120, message = "年龄不能大于 120")
    private Integer age;
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

- `GET /api/validation`：模块说明
- `POST /api/validation/users`：创建用户并演示校验与业务错误

## 调用验证

```bash
curl -X POST "http://localhost:8121/api/validation/users" \
  -H "Content-Type: application/json" \
  -d '{}'
```

返回 `VALIDATION_FAILED`，并在 `data.fieldErrors` 中列出字段错误。

```bash
curl -X POST "http://localhost:8121/api/validation/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","age":30}'
```

返回 `USER_DUPLICATE`。

## 生产差距

该示例用于隔离学习 参数校验与错误码 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 41-SpringBoot-validation-error-code test
```

## 要点总结

1. Bean Validation 字段校验
2. 统一字符串错误码
3. 字段级错误明细
4. 业务异常到 HTTP 状态码映射
5. 全局异常处理器

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
