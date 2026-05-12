---
title: SpringBoot Validation分组
date: 2026-05-11
tags:
  - springboot
  - java
  - 校验
module: 82-SpringBoot-validation-groups
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot Validation分组

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/82-SpringBoot-validation-groups`

## 核心思路

本模块演示 Bean Validation 分组校验：同一个请求 DTO 在 create 和 update 场景下使用不同规则。

## 能力点

- `spring-boot-starter-validation`
- `@Validated`
- Bean Validation groups
- `@Null`
- `@NotBlank`
- `@NotNull`
- `@Min`
- `MethodArgumentNotValidException` 错误响应

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot Validation分组 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ValidationGroupsController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ValidationGroupsController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/validation-groups")
public class ValidationGroupsController {
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "82-SpringBoot-validation-groups",
                "apis", List.of(
                        "GET /api/validation-groups",
                        "POST /api/validation-groups/orders",
                        "PUT /api/validation-groups/orders/{orderId}"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/orders")
    public ApiResult<OrderValidationResult> create(
            @Validated(ValidationGroups.Create.class) @RequestBody OrderRequest request) {
        // Create forbids client-provided orderId; the server owns identifier generation.
        return ApiResult.success(new OrderValidationResult("create", "generated", request.sku(), request.quantity()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PutMapping("/orders/{orderId}")
    public ApiResult<OrderValidationResult> update(
            @PathVariable String orderId,
            @Validated(ValidationGroups.Update.class) @RequestBody OrderRequest request) {
        return ApiResult.success(new OrderValidationResult("update", orderId, request.sku(), request.quantity()));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
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
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(BAD_REQUEST)
    public ApiResult<Map<String, Object>> handleValidation(MethodArgumentNotValidException exception) {
        List<Map<String, String>> errors = exception.getBindingResult().getFieldErrors().stream()
                .map(error -> Map.of("field", error.getField(), "message", error.getDefaultMessage()))
                .toList();
        return ApiResult.success(Map.of("validationErrors", errors));
    }

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

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/validation-groups`：模块说明
- `POST /api/validation-groups/orders`：Create 分组校验
- `PUT /api/validation-groups/orders/{orderId}`：Update 分组校验

## 调用验证

```bash
curl "http://localhost:8162/api/validation-groups"
```

```bash
curl -X POST "http://localhost:8162/api/validation-groups/orders" \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU-1","quantity":2}'
```

```bash
curl -X PUT "http://localhost:8162/api/validation-groups/orders/ORD-1" \
  -H "Content-Type: application/json" \
  -d '{"orderId":"ORD-1","sku":"SKU-1","quantity":2}'
```

## 生产映射

生产系统可以用这个模式：

- 同一个 DTO 在 create/update 中使用不同约束
- 防止客户端在 create 时传入服务端生成字段
- update 时强制要求业务主键
- 保持请求模型和校验意图靠近，减少控制器里的手写 if 判断

如果校验规则完全不同，拆 DTO 更清晰；如果只是少数字段在不同场景下约束不同，validation groups 更合适。

## 生产差距

该示例用于隔离学习 Validation分组 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 82-SpringBoot-validation-groups test
```

测试覆盖：

- Create 组拒绝客户端传入 `orderId`
- Update 组要求 `orderId`
- Create/Update 组共享字段校验
- MockMvc 验证 metadata、有效 create、有效 update、无效 create 的错误响应

## 要点总结

1. `spring-boot-starter-validation`
2. `@Validated`
3. Bean Validation groups
4. `@Null`
5. `@NotBlank`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
