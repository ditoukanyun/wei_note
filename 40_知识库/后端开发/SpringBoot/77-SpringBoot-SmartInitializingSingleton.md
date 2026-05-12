---
title: SpringBoot SmartInitializingSingleton
date: 2026-05-11
tags:
  - springboot
  - java
module: 77-SpringBoot-smart-initializing-singleton
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot SmartInitializingSingleton

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/77-SpringBoot-smart-initializing-singleton`

## 核心思路

本模块演示 `SmartInitializingSingleton`：所有普通单例 Bean 实例化完成后，再执行一次统一的生命周期回调。

## 能力点

- `SmartInitializingSingleton`
- `afterSingletonsInstantiated`
- 多个策略 Bean 的统一收集
- 单例全部就绪后的不可变快照
- MockMvc 验证最终 registry 状态

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot SmartInitializingSingleton 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/SmartInitializingSingletonController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/SmartInitializingSingletonController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/smart-initializing-singleton")
public class SmartInitializingSingletonController {
    private final NotificationStrategyRegistry registry;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SmartInitializingSingletonController(NotificationStrategyRegistry registry) {
        this.registry = registry;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "77-SpringBoot-smart-initializing-singleton",
                "apis", List.of(
                        "GET /api/smart-initializing-singleton",
                        "GET /api/smart-initializing-singleton/registry"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/registry")
    public ApiResult<Map<String, Object>> registry() {
        return ApiResult.success(Map.of(
                "initialized", registry.isInitialized(),
                "strategyCount", registry.getStrategyCount(),
                "channels", registry.getChannels()
        ));
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

- `GET /api/smart-initializing-singleton`：模块说明
- `GET /api/smart-initializing-singleton/registry`：返回策略 registry 快照

## 调用验证

```bash
curl "http://localhost:8157/api/smart-initializing-singleton"
```

```bash
curl "http://localhost:8157/api/smart-initializing-singleton/registry"
```

## 生产映射

生产系统可以用这个模式：

- 校验插件、策略、处理器是否全部注册完成
- 把多个 Bean 聚合成不可变路由表
- 在依赖注入完成后预热内存 registry
- 避免在每次请求中重复扫描 Bean 集合

如果要处理单个 Bean 初始化前后，用 `BeanPostProcessor`；如果要等全部普通单例都就绪后再统一处理，用 `SmartInitializingSingleton`。

## 生产差距

该示例用于隔离学习 SmartInitializingSingleton 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 77-SpringBoot-smart-initializing-singleton test
```

测试覆盖：

- 直接使用 `DefaultListableBeanFactory` 验证 `preInstantiateSingletons` 触发生命周期回调
- 验证 registry 收集 `email`、`sms` 两个策略
- 验证 channel 快照不可变
- MockMvc 验证最终 registry 状态进入 controller

## 要点总结

1. `SmartInitializingSingleton`
2. `afterSingletonsInstantiated`
3. 多个策略 Bean 的统一收集
4. 单例全部就绪后的不可变快照
5. MockMvc 验证最终 registry 状态

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
