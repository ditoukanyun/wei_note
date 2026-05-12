---
title: SpringBoot 应用生命周期事件
date: 2026-05-11
tags:
  - springboot
  - java
  - 生命周期
module: 66-SpringBoot-application-lifecycle-events
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 应用生命周期事件

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/66-SpringBoot-application-lifecycle-events`

## 核心思路

本模块演示 Spring Boot 应用启动生命周期中的关键扩展点：`ApplicationRunner`、`ApplicationReadyEvent`、生命周期事件记录、显式排序时间线和事件摘要。

## 能力点

- `ApplicationRunner`
- `ApplicationListener<ApplicationReadyEvent>`
- 启动生命周期审计
- 生命周期事件去重
- 时间线排序
- 事件类型统计
- MockMvc API 测试

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 应用生命周期事件 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/LifecycleAuditController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/LifecycleAuditController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/lifecycle")
public class LifecycleAuditController {
    private final LifecycleAuditService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public LifecycleAuditController(LifecycleAuditService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "66-SpringBoot-application-lifecycle-events");
        data.put("desc", "ApplicationRunner 与 ApplicationReadyEvent 的启动生命周期审计");
        data.put("apis", new String[]{
                "GET /api/lifecycle",
                "POST /api/lifecycle/events",
                "GET /api/lifecycle/timeline",
                "GET /api/lifecycle/summary"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/events")
    public ApiResult<LifecycleEventRecord> record(@RequestBody LifecycleRecordRequest request) {
        return ApiResult.success(service.record(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/timeline")
    public ApiResult<List<LifecycleEventRecord>> timeline() {
        return ApiResult.success(service.timeline());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/summary")
    public ApiResult<LifecycleSummary> summary() {
        return ApiResult.success(service.summary());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/LifecycleAuditService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/LifecycleAuditService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class LifecycleAuditService {
    private final LifecycleAuditRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public LifecycleAuditService(LifecycleAuditRepository repository) {
        this.repository = repository;
    }

    public LifecycleEventRecord record(LifecycleRecordRequest request) {
        validate(request);
        if (repository.find(request.getEventId()).isPresent()) {
            throw new IllegalArgumentException("eventId 已存在");
        }
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(new LifecycleEventRecord(request.getEventId(), request.getEventType(), request.getSource(),
                request.getOrderNo(), request.getMessage(), request.getOccurredAt()));
    }

    public List<LifecycleEventRecord> timeline() {
        return repository.events().stream()
                .sorted(Comparator.comparingInt(LifecycleEventRecord::getOrderNo)
                        .thenComparing(LifecycleEventRecord::getOccurredAt)
                        .thenComparing(LifecycleEventRecord::getEventId))
                .toList();
    }

    public LifecycleSummary summary() {
        Map<LifecycleEventType, Long> counts = repository.events().stream()
                .collect(Collectors.groupingBy(LifecycleEventRecord::getEventType, Collectors.counting()));
        return new LifecycleSummary(repository.events().size(), counts);
    }

    public LifecycleEventRecord latest(LifecycleEventType eventType) {
        if (eventType == null) throw new IllegalArgumentException("eventType 不能为空");
        return repository.events().stream()
                .filter(event -> event.getEventType() == eventType)
                .max(Comparator.comparing(LifecycleEventRecord::getOccurredAt)
                        .thenComparingInt(LifecycleEventRecord::getOrderNo))
                .orElseThrow(() -> new NoSuchElementException("生命周期事件不存在: " + eventType));
    }

    private void validate(LifecycleRecordRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getEventId())) throw new IllegalArgumentException("eventId 不能为空");
        if (request.getEventType() == null) throw new IllegalArgumentException("eventType 不能为空");
        if (isBlank(request.getSource())) throw new IllegalArgumentException("source 不能为空");
        if (request.getOrderNo() < 0) throw new IllegalArgumentException("orderNo 不能小于 0");
        if (isBlank(request.getMessage())) throw new IllegalArgumentException("message 不能为空");
        if (request.getOccurredAt() == null) throw new IllegalArgumentException("occurredAt 不能为空");
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/lifecycle/LifecycleAuditRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/lifecycle/LifecycleAuditRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class LifecycleAuditRepository {
    private final Map<String, LifecycleEventRecord> events = new LinkedHashMap<>();

    public LifecycleEventRecord save(LifecycleEventRecord event) {
        events.put(event.getEventId(), event);
        return event;
    }

    public Optional<LifecycleEventRecord> find(String eventId) {
        return Optional.ofNullable(events.get(eventId));
    }

    public List<LifecycleEventRecord> events() {
        return new ArrayList<>(events.values());
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 监听器：Spring 事件如何被消费

源码位置：`src/main/java/com/cloud/lifecycle/ApplicationReadyLifecycleListener.java`

这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。

```java
// 文件：com/cloud/lifecycle/ApplicationReadyLifecycleListener.java
// 学习重点：这是案例链路中的关键类，读它可以把 README 的概念落到具体代码。
@Component
public class ApplicationReadyLifecycleListener implements ApplicationListener<ApplicationReadyEvent> {
    private final LifecycleAuditService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ApplicationReadyLifecycleListener(LifecycleAuditService service) {
        this.service = service;
    }

    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        // ApplicationReadyEvent is published after runners complete and the application is ready to serve traffic.
        service.record(new LifecycleRecordRequest("application-ready", LifecycleEventType.APPLICATION_READY,
                "ApplicationReadyEvent", 90, "Application is ready", LocalDateTime.now()));
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. LifecycleAuditController：接收 HTTP 请求并转换成 Java 方法调用
2. LifecycleAuditService：执行案例的核心业务规则
3. LifecycleAuditRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/lifecycle`：模块说明
- `POST /api/lifecycle/events`：手动记录一个生命周期事件
- `GET /api/lifecycle/timeline`：查看有序事件时间线
- `GET /api/lifecycle/summary`：查看事件类型统计

## 调用验证

```bash
curl "http://localhost:8146/api/lifecycle"
```

```bash
curl -X POST "http://localhost:8146/api/lifecycle/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "custom-1",
    "eventType": "CUSTOM",
    "source": "curl",
    "orderNo": 100,
    "message": "manual checkpoint",
    "occurredAt": "2026-05-08T10:30:00"
  }'
```

```bash
curl "http://localhost:8146/api/lifecycle/timeline"
```

```bash
curl "http://localhost:8146/api/lifecycle/summary"
```

## 生产映射

生产系统可以把本模块扩展为：

- 启动审计表
- runner 和 listener 执行顺序诊断
- 应用 ready 前后的检查点记录
- 启动异常排查辅助接口
- 与 actuator readiness/liveness 的联动状态说明

## 生产差距

该示例用于隔离学习 应用生命周期事件 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 66-SpringBoot-application-lifecycle-events test
```

测试覆盖：

- 服务层事件记录、排序、统计、重复拒绝、最新事件查询
- API 层模块信息、事件写入、时间线和摘要

## 要点总结

1. `ApplicationRunner`
2. `ApplicationListener<ApplicationReadyEvent>`
3. 启动生命周期审计
4. 生命周期事件去重
5. 时间线排序

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
