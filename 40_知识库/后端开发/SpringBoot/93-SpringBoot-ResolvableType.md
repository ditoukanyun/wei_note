---
title: SpringBoot ResolvableType
date: 2026-05-11
tags:
  - springboot
  - java
module: 93-SpringBoot-resolvable-type
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ResolvableType

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/93-SpringBoot-resolvable-type`

## 核心思路

本模块演示 Spring 的 `ResolvableType`：从 `EventHandler<T>` 的具体实现类反推出泛型参数类型。这个模式在 Spring 源码里很常见，例如 converter、listener、serializer、handler registry 等框架组件都需要从用户实现类推断支持的领域类型。

## 能力点

- `ResolvableType`
- generic interface resolution
- `forClass(genericInterface, implementationClass)`
- `getGeneric(0)`
- ordered handler catalog
- ApplicationContextRunner 验证泛型解析
- MockMvc 验证完整应用上下文中的 catalog 输出

## 关键实现

```java
Class<?> eventType = ResolvableType.forClass(EventHandler.class, handler.getClass())
        .getGeneric(0)
        .resolve();
```

示例映射：

| handler | resolved event type |
| --- | --- |
| `UserCreatedEventHandler` | `UserCreatedEvent` |
| `InvoicePaidEventHandler` | `InvoicePaidEvent` |

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ResolvableType 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/resolvable/EventHandlerConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/resolvable/EventHandlerConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration(proxyBeanMethods = false)
public class EventHandlerConfig {
    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    EventHandler<UserCreatedEvent> userCreatedEventHandler() {
        return new UserCreatedEventHandler();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    EventHandler<InvoicePaidEvent> invoicePaidEventHandler() {
        return new InvoicePaidEventHandler();
    }

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    EventHandlerCatalog eventHandlerCatalog(List<EventHandler<?>> handlers) {
        return new EventHandlerCatalog(handlers);
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ResolvableTypeController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ResolvableTypeController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/resolvable-type")
public class ResolvableTypeController {
    private final EventHandlerCatalog eventHandlerCatalog;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ResolvableTypeController(EventHandlerCatalog eventHandlerCatalog) {
        this.eventHandlerCatalog = eventHandlerCatalog;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "93-SpringBoot-resolvable-type",
                "topic", "Spring ResolvableType generic interface resolution",
                "apis", List.of(
                        "GET /api/resolvable-type",
                        "GET /api/resolvable-type/handlers"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/handlers")
    public ApiResult<List<HandlerDescriptor>> handlers() {
        return ApiResult.success(eventHandlerCatalog.descriptors());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：EventHandler

源码位置：`src/main/java/com/cloud/resolvable/EventHandler.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/resolvable/EventHandler.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public interface EventHandler<T extends DomainEvent> extends Ordered {
    String handlerName();

    String handle(T event);
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 关键类：EventHandlerCatalog

源码位置：`src/main/java/com/cloud/resolvable/EventHandlerCatalog.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/resolvable/EventHandlerCatalog.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class EventHandlerCatalog {
    private final List<EventHandler<?>> handlers;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public EventHandlerCatalog(List<EventHandler<?>> handlers) {
        this.handlers = List.copyOf(handlers);
    }

    public Class<?> resolveEventType(EventHandler<?> handler) {
        // This mirrors Spring framework code that adapts generic user components by resolving their SPI type.
        Class<?> eventType = ResolvableType.forClass(EventHandler.class, handler.getClass())
                .getGeneric(0)
                .resolve();
        if (eventType == null) {
            throw new IllegalArgumentException("Cannot resolve event type for " + handler.getClass().getName());
        }
        return eventType;
    }

    public List<HandlerDescriptor> descriptors() {
        return handlers.stream()
                .sorted(Comparator.comparingInt(EventHandler::getOrder))
                .map(handler -> {
                    Class<?> eventType = resolveEventType(handler);
                    return new HandlerDescriptor(
                            handler.handlerName(),
                            eventType.getSimpleName(),
                            eventName(eventType)
                    );
                })
                .toList();
    }

    private String eventName(Class<?> eventType) {
        if (eventType.equals(UserCreatedEvent.class)) {
            return new UserCreatedEvent("sample-user").eventName();
        }
        if (eventType.equals(InvoicePaidEvent.class)) {
            return new InvoicePaidEvent("sample-invoice").eventName();
        }
        throw new IllegalArgumentException("Unsupported event type " + eventType.getName());
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

- `GET /api/resolvable-type`：模块说明
- `GET /api/resolvable-type/handlers`：返回 handler 与解析出的事件类型

## 调用验证

```bash
curl "http://localhost:8173/api/resolvable-type"
```

```bash
curl "http://localhost:8173/api/resolvable-type/handlers"
```

`/handlers` 核心响应：

```json
[
  {
    "handlerName": "user-created-handler",
    "eventType": "UserCreatedEvent",
    "eventName": "user-created"
  },
  {
    "handlerName": "invoice-paid-handler",
    "eventType": "InvoicePaidEvent",
    "eventName": "invoice-paid"
  }
]
```

## 生产映射

`ResolvableType` 适合框架层读取用户实现类的泛型声明。相比自己解析 `java.lang.reflect.Type`，它对 Spring 常见场景更友好，也更贴近 Spring 源码中的类型推断方式。

适合使用这个模式的场景：

- 事件处理器自动注册
- 泛型 converter 或 adapter catalog
- 根据 handler 泛型推断支持的消息类型
- 避免用字符串手写类型元数据
- 阅读 Spring event、conversion、binding 相关源码

如果类型信息是业务配置的一部分，显式配置可能比泛型推断更清晰。

## 生产差距

该示例用于隔离学习 ResolvableType 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 93-SpringBoot-resolvable-type test
```

测试覆盖：

- `UserCreatedEventHandler` 解析为 `UserCreatedEvent`
- `InvoicePaidEventHandler` 解析为 `InvoicePaidEvent`
- catalog 输出顺序稳定
- MockMvc 验证 metadata 和 handlers 接口

## 要点总结

1. `ResolvableType`
2. generic interface resolution
3. `forClass(genericInterface, implementationClass)`
4. `getGeneric(0)`
5. ordered handler catalog

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
