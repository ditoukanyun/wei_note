---
title: SpringBoot CDC增量同步
date: 2026-05-11
tags:
  - springboot
  - java
  - cdc
module: 52-SpringBoot-cdc-incremental-sync
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot CDC增量同步

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/52-SpringBoot-cdc-incremental-sync`

## 核心思路

本模块演示 CDC 增量同步原型：源端变更写入 change log，消费者按 offset checkpoint 同步到读模型，使用 eventId 做幂等，并支持 rebuild 与 replay 控制。

## 能力点

- Change event model
- Offset checkpoint
- Idempotent consumer
- Incremental sync
- Tombstone delete
- Read model rebuild
- Replay from offset

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot CDC增量同步 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/CdcSyncController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/CdcSyncController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/cdc")
public class CdcSyncController {

    private final CdcSyncService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CdcSyncController(CdcSyncService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "52-SpringBoot-cdc-incremental-sync");
        data.put("desc", "CDC change log、offset checkpoint、幂等消费、读模型重建与 replay");
        data.put("apis", new String[]{
                "GET /api/cdc",
                "POST /api/cdc/source/products",
                "POST /api/cdc/source/products/{productId}/delete",
                "GET /api/cdc/source/events",
                "POST /api/cdc/sync/run",
                "POST /api/cdc/sync/rebuild",
                "POST /api/cdc/sync/replay?fromOffset=1",
                "GET /api/cdc/read-model/products",
                "GET /api/cdc/checkpoint"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/source/products")
    public ApiResult<ChangeEvent> upsertProduct(@RequestBody UpsertProductRequest request) {
        return ApiResult.success(service.upsertProduct(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/source/products/{productId}/delete")
    public ApiResult<ChangeEvent> deleteProduct(@PathVariable String productId) {
        return ApiResult.success(service.deleteProduct(productId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/source/events")
    public ApiResult<List<ChangeEvent>> events() {
        return ApiResult.success(service.events());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/sync/run")
    public ApiResult<SyncResult> runIncrementalSync() {
        return ApiResult.success(service.runIncrementalSync());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/sync/rebuild")
    public ApiResult<SyncResult> rebuild() {
        return ApiResult.success(service.rebuild());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/sync/replay")
    public ApiResult<SyncResult> replay(@RequestParam(defaultValue = "1") long fromOffset) {
        return ApiResult.success(service.replayFrom(fromOffset));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/read-model/products")
    public ApiResult<List<ProductSnapshot>> readModelProducts() {
        return ApiResult.success(service.readModelProducts());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/checkpoint")
    public ApiResult<SyncCheckpoint> checkpoint() {
        return ApiResult.success(service.checkpoint());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/CdcSyncService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/CdcSyncService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class CdcSyncService {

    private static final String PRODUCT_UPSERT = "PRODUCT_UPSERT";
    private static final String PRODUCT_DELETE = "PRODUCT_DELETE";

    private final ChangeEventLog eventLog;
    private final ProductReadModel readModel;
    private final Clock clock;
    private final SyncCheckpoint checkpoint = new SyncCheckpoint();

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CdcSyncService(ChangeEventLog eventLog, ProductReadModel readModel) {
        this(eventLog, readModel, Clock.systemUTC());
    }

    public CdcSyncService(ChangeEventLog eventLog, ProductReadModel readModel, Clock clock) {
        this.eventLog = eventLog;
        this.readModel = readModel;
        this.clock = clock;
    }

    public ChangeEvent upsertProduct(UpsertProductRequest request) {
        validateUpsert(request);
        return eventLog.append(
                UUID.randomUUID().toString(),
                PRODUCT_UPSERT,
                request.getProductId(),
                new ProductSnapshot(request.getProductId(), request.getName(), request.getStock(), false),
                clock.instant()
        );
    }

    public ChangeEvent deleteProduct(String productId) {
        if (isBlank(productId)) {
            throw new IllegalArgumentException("productId 不能为空");
        }
        return eventLog.append(
                UUID.randomUUID().toString(),
                PRODUCT_DELETE,
                productId,
                new ProductSnapshot(productId, null, 0, true),
                clock.instant()
        );
    }

    public SyncResult runIncrementalSync() {
        return process(eventLog.eventsAfter(checkpoint.getLastOffset()));
    }

    public SyncResult rebuild() {
        readModel.clear();
        checkpoint.reset();
        return process(eventLog.eventsFrom(1));
    }

    public SyncResult replayFrom(long fromOffset) {
        return process(eventLog.eventsFrom(fromOffset));
    }

    public List<ChangeEvent> events() {
        return eventLog.events();
    }

    public List<ProductSnapshot> readModelProducts() {
        return readModel.products();
    }

    public SyncCheckpoint checkpoint() {
        return checkpoint;
    }

    private SyncResult process(List<ChangeEvent> events) {
        int applied = 0;
        int skipped = 0;
        for (ChangeEvent event : events) {
            if (checkpoint.getProcessedEventIds().contains(event.getEventId())) {
                skipped++;
                checkpoint.setLastOffset(Math.max(checkpoint.getLastOffset(), event.getOffset()));
                continue;
            }
            apply(event);
            checkpoint.getProcessedEventIds().add(event.getEventId());
            checkpoint.setLastOffset(Math.max(checkpoint.getLastOffset(), event.getOffset()));
            applied++;
        }
        return new SyncResult(events.size(), applied, skipped, checkpoint.getLastOffset(), readModel.products().size());
    }

    private void apply(ChangeEvent event) {
        if (PRODUCT_UPSERT.equals(event.getEventType()) || PRODUCT_DELETE.equals(event.getEventType())) {
            readModel.apply(event.getPayload());
            return;
        }
        throw new IllegalArgumentException("不支持的事件类型: " + event.getEventType());
    }

    private void validateUpsert(UpsertProductRequest request) {
        if (request == null || isBlank(request.getProductId())) {
            throw new IllegalArgumentException("productId 不能为空");
        }
        if (isBlank(request.getName())) {
            throw new IllegalArgumentException("name 不能为空");
        }
        if (request.getStock() < 0) {
    // ... 省略其余辅助代码，完整实现以源码为准。
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

- `GET /api/cdc`：模块说明
- `POST /api/cdc/source/products`：写入源端商品变更
- `POST /api/cdc/source/products/{productId}/delete`：写入删除 tombstone 事件
- `GET /api/cdc/source/events`：查询 change log
- `POST /api/cdc/sync/run`：从 checkpoint 后增量消费
- `POST /api/cdc/sync/rebuild`：清空读模型并从头重建
- `POST /api/cdc/sync/replay?fromOffset=1`：从指定 offset replay
- `GET /api/cdc/read-model/products`：查询读模型
- `GET /api/cdc/checkpoint`：查询 checkpoint

## 调用验证

写入源端变更：

```bash
curl -X POST "http://localhost:8132/api/cdc/source/products" \
  -H "Content-Type: application/json" \
  -d '{"productId":"P100","name":"Phone","stock":10}'
```

执行增量同步：

```bash
curl -X POST "http://localhost:8132/api/cdc/sync/run"
```

查询读模型：

```bash
curl "http://localhost:8132/api/cdc/read-model/products"
```

重建读模型：

```bash
curl -X POST "http://localhost:8132/api/cdc/sync/rebuild"
```

从 offset replay：

```bash
curl -X POST "http://localhost:8132/api/cdc/sync/replay?fromOffset=1"
```

## 生产映射

本模块使用内存 change log 和读模型。生产环境通常替换为：

- 变更捕获：Debezium、Canal、数据库 binlog
- 事件传输：Kafka/RocketMQ/Pulsar
- checkpoint：consumer offset、数据库 checkpoint 表
- 幂等：eventId 去重表、业务唯一键、版本号
- 读模型：Elasticsearch、Redis、ClickHouse、PostgreSQL materialized view
- rebuild：全量快照 + 增量追平
- replay：按 offset/time range 重新投递，保留幂等保护

## 生产差距

该示例用于隔离学习 CDC增量同步 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 52-SpringBoot-cdc-incremental-sync test
```

## 要点总结

1. Change event model
2. Offset checkpoint
3. Idempotent consumer
4. Incremental sync
5. Tombstone delete

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
