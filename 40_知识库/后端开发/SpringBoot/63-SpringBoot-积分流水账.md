---
title: SpringBoot 积分流水账
date: 2026-05-11
tags:
  - springboot
  - java
  - 积分
module: 63-SpringBoot-points-ledger
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 积分流水账

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/63-SpringBoot-points-ledger`

## 核心思路

本模块演示积分系统的核心账本模型：用户获得积分、兑换积分、积分过期、流水冲正，并通过不可变流水计算账户余额。

## 能力点

- 积分账户
- 获得积分
- 兑换积分
- 积分过期
- 流水冲正
- 余额计算
- `transactionRef` 幂等
- 追加式积分流水

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 积分流水账 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/PointsLedgerController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/PointsLedgerController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/points")
public class PointsLedgerController {
    private final PointsLedgerService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public PointsLedgerController(PointsLedgerService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "63-SpringBoot-points-ledger");
        data.put("desc", "积分账户、获得、兑换、过期、冲正流水与余额计算");
        data.put("apis", new String[]{
                "GET /api/points",
                "POST /api/points/earn",
                "POST /api/points/redeem",
                "POST /api/points/expire",
                "POST /api/points/reverse",
                "GET /api/points/accounts/{userId}",
                "GET /api/points/accounts/{userId}/ledger"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/earn")
    public ApiResult<PointsLedgerEntry> earn(@RequestBody PointsCommand command) {
        return ApiResult.success(service.earn(command));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/redeem")
    public ApiResult<PointsLedgerEntry> redeem(@RequestBody PointsCommand command) {
        return ApiResult.success(service.redeem(command));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/expire")
    public ApiResult<PointsLedgerEntry> expire(@RequestBody PointsCommand command) {
        return ApiResult.success(service.expire(command));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/reverse")
    public ApiResult<PointsLedgerEntry> reverse(@RequestBody ReversePointsRequest request) {
        return ApiResult.success(service.reverse(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/accounts/{userId}")
    public ApiResult<PointsAccount> account(@PathVariable String userId) {
        return ApiResult.success(service.account(userId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/accounts/{userId}/ledger")
    public ApiResult<List<PointsLedgerEntry>> ledger(@PathVariable String userId) {
        return ApiResult.success(service.ledger(userId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/PointsLedgerService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/PointsLedgerService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class PointsLedgerService {
    private final PointsLedgerRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public PointsLedgerService(PointsLedgerRepository repository) {
        this.repository = repository;
    }

    public PointsLedgerEntry earn(PointsCommand command) {
        validateCommand(command);
        return appendWithIdempotency(command, PointsEntryType.EARN, command.getPoints(), null);
    }

    public PointsLedgerEntry redeem(PointsCommand command) {
        validateCommand(command);
        return repository.findByTransactionRef(command.getTransactionRef())
                .orElseGet(() -> {
                    if (balance(command.getUserId()) < command.getPoints()) {
                        throw new IllegalArgumentException("积分余额不足");
                    }
                    return append(command, PointsEntryType.REDEEM, -command.getPoints(), null);
                });
    }

    public PointsLedgerEntry expire(PointsCommand command) {
        validateCommand(command);
        return repository.findByTransactionRef(command.getTransactionRef())
                .orElseGet(() -> {
                    int expired = Math.min(command.getPoints(), balance(command.getUserId()));
                    return append(command, PointsEntryType.EXPIRE, -expired, null);
                });
    }

    public PointsLedgerEntry reverse(ReversePointsRequest request) {
        validateReverse(request);
        return repository.findByTransactionRef(request.getTransactionRef())
                .orElseGet(() -> {
                    PointsLedgerEntry original = repository.findEntry(request.getOriginalEntryId())
                            .orElseThrow(() -> new NoSuchElementException("原积分流水不存在: " + request.getOriginalEntryId()));
                    if (!original.getUserId().equals(request.getUserId())) {
                        throw new IllegalArgumentException("原积分流水不属于当前用户");
                    }
                    if (original.getEntryType() == PointsEntryType.REVERSE) {
                        throw new IllegalArgumentException("冲正流水不能再次冲正");
                    }
                    if (isReversed(original.getEntryId())) {
                        throw new IllegalArgumentException("原积分流水已冲正");
                    }
                    int reversePoints = -original.getPoints();
                    if (reversePoints < 0 && balance(request.getUserId()) < Math.abs(reversePoints)) {
                        throw new IllegalArgumentException("冲正后积分余额不能为负");
                    }
                    // Historical entries stay immutable; reversal is represented as a compensating ledger entry.
                    return append(new PointsCommand(request.getUserId(), Math.abs(reversePoints), request.getTransactionRef(),
                            request.getReason(), request.getOccurredAt()), PointsEntryType.REVERSE, reversePoints,
                            original.getEntryId());
                });
    }

    public PointsAccount account(String userId) {
        if (isBlank(userId)) throw new IllegalArgumentException("userId 不能为空");
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        PointsAccount account = repository.findAccount(userId).orElseGet(() -> repository.saveAccount(new PointsAccount(userId, 0)));
        account.setBalance(balance(userId));
        return account;
    }

    public List<PointsLedgerEntry> ledger(String userId) {
        if (isBlank(userId)) throw new IllegalArgumentException("userId 不能为空");
        return repository.entries().stream()
                .filter(entry -> entry.getUserId().equals(userId))
                .toList();
    }

    private PointsLedgerEntry appendWithIdempotency(PointsCommand command, PointsEntryType type, int signedPoints, String relatedEntryId) {
        // transactionRef is the idempotency key; repeated business callbacks return the original ledger entry.
        return repository.findByTransactionRef(command.getTransactionRef())
                .orElseGet(() -> append(command, type, signedPoints, relatedEntryId));
    }

    private PointsLedgerEntry append(PointsCommand command, PointsEntryType type, int signedPoints, String relatedEntryId) {
        ensureAccount(command.getUserId());
        PointsLedgerEntry entry = new PointsLedgerEntry(UUID.randomUUID().toString(), command.getUserId(), type, signedPoints,
                command.getTransactionRef(), relatedEntryId, command.getReason(), command.getOccurredAt());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveEntry(entry);
        account(command.getUserId());
        return entry;
    }

    private PointsAccount ensureAccount(String userId) {
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.findAccount(userId).orElseGet(() -> repository.saveAccount(new PointsAccount(userId, 0)));
    }

    private int balance(String userId) {
        return repository.entries().stream()
                .filter(entry -> entry.getUserId().equals(userId))
                .mapToInt(PointsLedgerEntry::getPoints)
                .sum();
    }

    private boolean isReversed(String entryId) {
        return repository.entries().stream()
                .anyMatch(entry -> entry.getEntryType() == PointsEntryType.REVERSE && entryId.equals(entry.getRelatedEntryId()));
    }

    private void validateCommand(PointsCommand command) {
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/points/PointsLedgerRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/points/PointsLedgerRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class PointsLedgerRepository {
    private final Map<String, PointsAccount> accounts = new LinkedHashMap<>();
    private final Map<String, PointsLedgerEntry> entries = new LinkedHashMap<>();
    private final Map<String, String> transactionIndex = new LinkedHashMap<>();

    public PointsAccount saveAccount(PointsAccount account) {
        accounts.put(account.getUserId(), account);
        return account;
    }

    public Optional<PointsAccount> findAccount(String userId) {
        return Optional.ofNullable(accounts.get(userId));
    }

    public PointsLedgerEntry saveEntry(PointsLedgerEntry entry) {
        entries.put(entry.getEntryId(), entry);
        transactionIndex.put(entry.getTransactionRef(), entry.getEntryId());
        return entry;
    }

    public Optional<PointsLedgerEntry> findEntry(String entryId) {
        return Optional.ofNullable(entries.get(entryId));
    }

    public Optional<PointsLedgerEntry> findByTransactionRef(String transactionRef) {
        String entryId = transactionIndex.get(transactionRef);
        return entryId == null ? Optional.empty() : findEntry(entryId);
    }

    public List<PointsLedgerEntry> entries() {
        return new ArrayList<>(entries.values());
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
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

1. PointsLedgerController：接收 HTTP 请求并转换成 Java 方法调用
2. PointsLedgerService：执行案例的核心业务规则
3. PointsLedgerRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/points`：模块说明
- `POST /api/points/earn`：获得积分
- `POST /api/points/redeem`：兑换积分
- `POST /api/points/expire`：积分过期
- `POST /api/points/reverse`：冲正流水
- `GET /api/points/accounts/{userId}`：查询积分账户
- `GET /api/points/accounts/{userId}/ledger`：查询积分流水

## 调用验证

```bash
curl -X POST "http://localhost:8143/api/points/earn" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-a","points":100,"transactionRef":"TX-EARN-1","reason":"订单奖励","occurredAt":"2026-05-08T10:00:00"}'
```

```bash
curl -X POST "http://localhost:8143/api/points/redeem" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-a","points":40,"transactionRef":"TX-REDEEM-1","reason":"支付抵扣","occurredAt":"2026-05-08T10:00:00"}'
```

```bash
curl "http://localhost:8143/api/points/accounts/user-a"
```

```bash
curl -X POST "http://localhost:8143/api/points/reverse" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-a","originalEntryId":"替换为原流水 entryId","transactionRef":"TX-REVERSE-1","reason":"客服冲正","occurredAt":"2026-05-08T10:10:00"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 积分账户表：用户、当前余额、累计获得、累计消耗
- 积分流水表：流水类型、分值、业务引用、关联流水、发生时间
- `transactionRef` 唯一索引：保证订单、活动、退款回调幂等
- 余额快照表或账户余额字段：避免每次全量扫描流水
- 过期任务：按活动或积分批次定时过期
- 客服审计：记录冲正原因、操作人和原流水

## 生产差距

该示例用于隔离学习 积分流水账 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 63-SpringBoot-points-ledger test
```

## 要点总结

1. 积分账户
2. 获得积分
3. 兑换积分
4. 积分过期
5. 流水冲正

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
