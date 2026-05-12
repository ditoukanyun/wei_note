---
title: SpringBoot 分布式锁与定时任务
date: 2026-05-11
tags:
  - springboot
  - java
  - 分布式锁
module: 46-SpringBoot-distributed-lock-job
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 分布式锁与定时任务

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/46-SpringBoot-distributed-lock-job`

## 核心思路

本模块演示用分布式锁保护定时任务：多个实例同时尝试执行同一个任务时，只有抢到锁的实例真正执行，其他实例记录为跳过；任务结束后必须用 owner token 校验所有权再释放锁。

## 能力点

- `SET NX` 风格抢锁
- TTL 自动过期
- owner token 所有权校验
- 多实例重复执行防护
- 任务执行与跳过历史记录

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 分布式锁与定时任务 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/DistributedLockJobController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/DistributedLockJobController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/locks")
public class DistributedLockJobController {

    private final LockedJobService jobService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DistributedLockJobController(LockedJobService jobService) {
        this.jobService = jobService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "46-SpringBoot-distributed-lock-job");
        data.put("desc", "分布式锁保护定时任务、多实例防重复执行和锁所有权安全释放");
        data.put("apis", new String[]{
                "GET /api/locks",
                "POST /api/locks/jobs/trigger",
                "GET /api/locks/jobs/history",
                "GET /api/locks/current"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/jobs/trigger")
    public ApiResult<JobRunRecord> trigger(@RequestBody(required = false) TriggerJobRequest request) {
        TriggerJobRequest resolved = request == null ? new TriggerJobRequest() : request;
        return ApiResult.success(jobService.trigger(resolved.getJobName(), resolved.getInstanceId()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/jobs/history")
    public ApiResult<List<JobRunRecord>> history() {
        return ApiResult.success(jobService.history());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/current")
    public ApiResult<List<LockEntry>> currentLocks() {
        return ApiResult.success(jobService.currentLocks());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/DistributedLockService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/DistributedLockService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class DistributedLockService {

    private final DistributedLockRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public DistributedLockService(DistributedLockRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public DistributedLockService(DistributedLockRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public synchronized LockAcquireResult tryAcquire(String lockName, String ownerInstance, Duration ttl) {
        Instant now = clock.instant();
        LockEntry current = repository.get(lockName);
        if (current != null && !current.isExpired(now)) {
            return new LockAcquireResult(
                    lockName,
                    false,
                    current.getOwnerToken(),
                    current.getOwnerInstance(),
                    current.getExpiresAt(),
                    "lock is held by another owner"
            );
        }

        String ownerToken = UUID.randomUUID().toString();
        Instant expiresAt = now.plus(ttl);
        LockEntry entry = new LockEntry(lockName, ownerToken, ownerInstance, now, expiresAt);
        repository.put(lockName, entry);
        return new LockAcquireResult(lockName, true, ownerToken, ownerInstance, expiresAt, "lock acquired");
    }

    public synchronized boolean release(String lockName, String ownerToken) {
        return repository.removeIfOwner(lockName, ownerToken);
    }

    public List<LockEntry> currentLocks() {
        Instant now = clock.instant();
        return repository.findAll().stream()
                .filter(lock -> !lock.isExpired(now))
                .toList();
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/LockedJobService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/LockedJobService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class LockedJobService {

    private static final String DEFAULT_JOB_NAME = "daily-report";
    private static final String DEFAULT_INSTANCE_ID = "api-instance";

    private final DistributedLockService lockService;
    private final Duration lockTtl;
    private final CopyOnWriteArrayList<JobRunRecord> history = new CopyOnWriteArrayList<>();

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public LockedJobService(DistributedLockService lockService) {
        this(lockService, Duration.ofSeconds(30));
    }

    public LockedJobService(DistributedLockService lockService, Duration lockTtl) {
        this.lockService = lockService;
        this.lockTtl = lockTtl;
    }

    public JobRunRecord trigger(String jobName, String instanceId) {
        String resolvedJobName = defaultIfBlank(jobName, DEFAULT_JOB_NAME);
        String resolvedInstanceId = defaultIfBlank(instanceId, DEFAULT_INSTANCE_ID);
        String lockName = "job:" + resolvedJobName;
        Instant startedAt = Instant.now();
        LockAcquireResult acquireResult = lockService.tryAcquire(lockName, resolvedInstanceId, lockTtl);
        if (!acquireResult.isAcquired()) {
            JobRunRecord skipped = new JobRunRecord(
                    UUID.randomUUID().toString(),
                    resolvedJobName,
                    resolvedInstanceId,
                    JobRunStatus.SKIPPED,
                    null,
                    startedAt,
                    Instant.now(),
                    acquireResult.getMessage()
            );
            history.add(skipped);
            return skipped;
        }

        try {
            sleepBriefly();
            JobRunRecord success = new JobRunRecord(
                    UUID.randomUUID().toString(),
                    resolvedJobName,
                    resolvedInstanceId,
                    JobRunStatus.SUCCESS,
                    acquireResult.getOwnerToken(),
                    startedAt,
                    Instant.now(),
                    "job executed with distributed lock"
            );
            history.add(success);
            return success;
        } finally {
            lockService.release(lockName, acquireResult.getOwnerToken());
        }
    }

    public List<JobRunRecord> history() {
        return new ArrayList<>(history);
    }

    public List<LockEntry> currentLocks() {
        return lockService.currentLocks();
    }

    private String defaultIfBlank(String value, String defaultValue) {
        return value == null || value.isBlank() ? defaultValue : value;
    }

    private void sleepBriefly() {
        try {
            Thread.sleep(50);
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
        }
    }
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/lock/DistributedLockRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/lock/DistributedLockRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class DistributedLockRepository {

    private final ConcurrentMap<String, LockEntry> locks = new ConcurrentHashMap<>();

    public LockEntry get(String lockName) {
        return locks.get(lockName);
    }

    public void put(String lockName, LockEntry entry) {
        locks.put(lockName, entry);
    }

    public boolean removeIfOwner(String lockName, String ownerToken) {
        LockEntry current = locks.get(lockName);
        if (current == null || !current.getOwnerToken().equals(ownerToken)) {
            return false;
        }
        return locks.remove(lockName, current);
    }

    public List<LockEntry> findAll() {
        return new ArrayList<>(locks.values());
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. DistributedLockJobController：接收 HTTP 请求并转换成 Java 方法调用
2. DistributedLockService：执行案例的核心业务规则
3. DistributedLockRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。
- 忽略幂等、重试、超时和补偿，导致失败后状态不一致。

## API 接口

- `GET /api/locks`：模块说明
- `POST /api/locks/jobs/trigger`：手动触发受锁保护的任务
- `GET /api/locks/jobs/history`：查看执行与跳过历史
- `GET /api/locks/current`：查看当前未过期锁

## 调用验证

```bash
curl -X POST "http://localhost:8126/api/locks/jobs/trigger" \
  -H "Content-Type: application/json" \
  -d '{"jobName":"daily-report","instanceId":"node-a"}'
```

## 生产映射

本模块使用内存仓储模拟 Redis 语义。生产环境通常映射为：

- 加锁：`SET lockName ownerToken NX PX ttlMillis`
- 释放：Lua 脚本先比较 `GET lockName` 是否等于 `ownerToken`，相等才 `DEL lockName`
- 目的：避免实例 A 的锁过期后被实例 B 获得，实例 A 又误删实例 B 的锁

## 生产差距

该示例用于隔离学习 分布式锁与定时任务 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 46-SpringBoot-distributed-lock-job test
```

## 要点总结

1. `SET NX` 风格抢锁
2. TTL 自动过期
3. owner token 所有权校验
4. 多实例重复执行防护
5. 任务执行与跳过历史记录

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
