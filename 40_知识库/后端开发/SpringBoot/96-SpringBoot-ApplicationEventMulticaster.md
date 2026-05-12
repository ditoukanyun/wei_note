---
title: SpringBoot ApplicationEventMulticaster
date: 2026-05-11
tags:
  - springboot
  - java
module: 96-SpringBoot-event-multicaster
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot ApplicationEventMulticaster

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/96-SpringBoot-event-multicaster`

## 核心思路

本模块演示 Spring 的应用事件广播链路：`ApplicationEventPublisher` 发布事件后，应用上下文把事件交给名为 `applicationEventMulticaster` 的 `ApplicationEventMulticaster`，再由 `SimpleApplicationEventMulticaster` 解析并调用匹配的 listener。

## 能力点

- `ApplicationEventPublisher`
- `ApplicationEventMulticaster`
- `SimpleApplicationEventMulticaster`
- named `applicationEventMulticaster` bean
- `ApplicationListener<T>`
- listener generic type filtering
- `Ordered` listener execution order
- synchronous listener delivery
- ApplicationContextRunner 验证广播器和 listener 选择
- MockMvc 验证完整应用上下文中的发布接口

## 关键实现

命名广播器：

```java
@Bean(name = AbstractApplicationContext.APPLICATION_EVENT_MULTICASTER_BEAN_NAME)
public ApplicationEventMulticaster applicationEventMulticaster() {
    return new SimpleApplicationEventMulticaster();
}
```

同步发布：

```java
eventPublisher.publishEvent(new OrderAuditEvent(this, orderId));
```

没有配置 `TaskExecutor` 时，`SimpleApplicationEventMulticaster` 会在发布线程里直接调用 listener。本模块把线程名记录到 `AuditEventRecord`，用于测试这个同步路径。

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot ApplicationEventMulticaster 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/EventMulticasterController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/EventMulticasterController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/event-multicaster")
public class EventMulticasterController {
    private final AuditEventPublishService publishService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public EventMulticasterController(AuditEventPublishService publishService) {
        this.publishService = publishService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        return ApiResult.success(Map.of(
                "module", "96-SpringBoot-event-multicaster",
                "topic", "Spring ApplicationEventMulticaster and synchronous listener dispatch",
                "apis", List.of(
                        "GET /api/event-multicaster",
                        "POST /api/event-multicaster/order-events?orderId=O-100",
                        "POST /api/event-multicaster/inventory-events?skuId=SKU-9",
                        "GET /api/event-multicaster/records"
                )
        ));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/order-events")
    public ApiResult<List<AuditEventRecord>> publishOrder(@RequestParam(defaultValue = "O-100") String orderId) {
        return ApiResult.success(publishService.publishOrder(orderId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/inventory-events")
    public ApiResult<List<AuditEventRecord>> publishInventory(@RequestParam(defaultValue = "SKU-9") String skuId) {
        return ApiResult.success(publishService.publishInventory(skuId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/records")
    public ApiResult<List<AuditEventRecord>> records() {
        return ApiResult.success(publishService.records());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/event/AuditEventPublishService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/event/AuditEventPublishService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
public class AuditEventPublishService {
    private final ApplicationEventPublisher eventPublisher;
    private final AuditEventStore store;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public AuditEventPublishService(ApplicationEventPublisher eventPublisher, AuditEventStore store) {
        this.eventPublisher = eventPublisher;
        this.store = store;
    }

    public List<AuditEventRecord> publishOrder(String orderId) {
        store.clear();
        eventPublisher.publishEvent(new OrderAuditEvent(this, orderId));
        return records();
    }

    public List<AuditEventRecord> publishInventory(String skuId) {
        store.clear();
        eventPublisher.publishEvent(new InventoryAuditEvent(this, skuId));
        return records();
    }

    public List<AuditEventRecord> records() {
        return store.all();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/event/AllAuditEventsListener.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/event/AllAuditEventsListener.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class AllAuditEventsListener implements ApplicationListener<DemoAuditEvent>, Ordered {
    private final AuditEventStore store;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public AllAuditEventsListener(AuditEventStore store) {
        this.store = store;
    }

    @Override
    public void onApplicationEvent(DemoAuditEvent event) {
        store.record(event.eventType(), "all-audit-events-listener", event.aggregateId());
    }

    @Override
    public int getOrder() {
        return 20;
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/event/InventoryAuditListener.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/event/InventoryAuditListener.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
public class InventoryAuditListener implements ApplicationListener<InventoryAuditEvent>, Ordered {
    private final AuditEventStore store;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InventoryAuditListener(AuditEventStore store) {
        this.store = store;
    }

    @Override
    public void onApplicationEvent(InventoryAuditEvent event) {
        store.record(event.eventType(), "inventory-audit-listener", event.aggregateId());
    }

    @Override
    public int getOrder() {
        return 10;
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

- `GET /api/event-multicaster`：模块说明
- `POST /api/event-multicaster/order-events?orderId=O-100`：发布订单审计事件
- `POST /api/event-multicaster/inventory-events?skuId=SKU-9`：发布库存审计事件
- `GET /api/event-multicaster/records`：查看当前 listener 调用记录

## 调用验证

```bash
curl "http://localhost:8176/api/event-multicaster"
```

```bash
curl -X POST "http://localhost:8176/api/event-multicaster/order-events?orderId=O-100"
```

订单事件核心响应：

```json
[
  {
    "sequence": 1,
    "eventType": "order",
    "listenerName": "order-audit-listener",
    "aggregateId": "O-100"
  },
  {
    "sequence": 2,
    "eventType": "order",
    "listenerName": "all-audit-events-listener",
    "aggregateId": "O-100"
  }
]
```

## 生产映射

Spring 应用事件适合进程内解耦，不等同于可靠消息队列。适合使用的场景：

- 同一应用内的轻量领域事件；
- 启动、刷新、配置变更等框架事件扩展；
- 需要按类型筛选 listener 的内部通知；
- 排查 listener 是否被触发、触发顺序和执行线程。

如果事件必须跨进程、需要重试、持久化或削峰，应使用消息队列或 outbox，而不是直接依赖应用事件。

## 生产差距

该示例用于隔离学习 ApplicationEventMulticaster 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 96-SpringBoot-event-multicaster test
```

测试覆盖：

- named `applicationEventMulticaster` 是 `SimpleApplicationEventMulticaster`
- 订单事件只触发订单 listener 和基类 listener
- 库存事件只触发库存 listener 和基类 listener
- 没有 task executor 时 listener 运行在发布线程
- MockMvc 验证 metadata、订单事件和库存事件接口

## 要点总结

1. `ApplicationEventPublisher`
2. `ApplicationEventMulticaster`
3. `SimpleApplicationEventMulticaster`
4. named `applicationEventMulticaster` bean
5. `ApplicationListener<T>`

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
