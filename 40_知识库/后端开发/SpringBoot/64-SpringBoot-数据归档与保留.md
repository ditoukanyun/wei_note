---
title: SpringBoot 数据归档与保留
date: 2026-05-11
tags:
  - springboot
  - java
  - 归档
module: 64-SpringBoot-data-archive-retention
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 数据归档与保留

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/64-SpringBoot-data-archive-retention`

## 核心思路

本模块演示数据生命周期治理的核心流程：配置保留策略，扫描可归档候选记录，执行归档，恢复已归档记录，并保留操作审计流水。

## 能力点

- 数据保留策略
- 业务记录管理
- 归档候选扫描
- 归档状态流转
- 归档恢复
- 操作审计日志
- 冷存储映射

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 数据归档与保留 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ArchiveRetentionController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ArchiveRetentionController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/archive")
public class ArchiveRetentionController {
    private final ArchiveRetentionService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ArchiveRetentionController(ArchiveRetentionService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "64-SpringBoot-data-archive-retention");
        data.put("desc", "数据保留策略、归档候选扫描、归档与恢复记录");
        data.put("apis", new String[]{
                "GET /api/archive",
                "POST /api/archive/policies",
                "GET /api/archive/policies",
                "POST /api/archive/records",
                "GET /api/archive/records",
                "POST /api/archive/scan",
                "POST /api/archive/archive",
                "POST /api/archive/restore",
                "GET /api/archive/operations"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/policies")
    public ApiResult<RetentionPolicy> savePolicy(@RequestBody RetentionPolicy policy) {
        return ApiResult.success(service.savePolicy(policy));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/policies")
    public ApiResult<List<RetentionPolicy>> policies() {
        return ApiResult.success(service.policies());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/records")
    public ApiResult<BusinessRecord> saveRecord(@RequestBody BusinessRecord record) {
        return ApiResult.success(service.saveRecord(record));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/records")
    public ApiResult<List<BusinessRecord>> records() {
        return ApiResult.success(service.records());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/scan")
    public ApiResult<ArchiveScanResult> scanCandidates(@RequestBody ArchiveScanRequest request) {
        return ApiResult.success(service.scanCandidates(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/archive")
    public ApiResult<BusinessRecord> archive(@RequestBody ArchiveRequest request) {
        return ApiResult.success(service.archive(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/restore")
    public ApiResult<BusinessRecord> restore(@RequestBody ArchiveRequest request) {
        return ApiResult.success(service.restore(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/operations")
    public ApiResult<List<ArchiveOperation>> operations() {
        return ApiResult.success(service.operations());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ArchiveRetentionService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ArchiveRetentionService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ArchiveRetentionService {
    private final ArchiveRetentionRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ArchiveRetentionService(ArchiveRetentionRepository repository) {
        this.repository = repository;
    }

    public RetentionPolicy savePolicy(RetentionPolicy policy) {
        validatePolicy(policy);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.savePolicy(policy);
    }

    public BusinessRecord saveRecord(BusinessRecord record) {
        validateRecord(record);
        if (record.getStatus() == null) {
            record.setStatus(RecordStatus.ACTIVE);
        }
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveRecord(record);
    }

    public ArchiveScanResult scanCandidates(ArchiveScanRequest request) {
        validateScan(request);
        List<BusinessRecord> candidates = repository.records().stream()
                .filter(record -> record.getDataType().equals(request.getDataType()))
                .filter(record -> isEligible(record, request.getScanDate()))
                .sorted(Comparator.comparing(BusinessRecord::getRecordId))
                .toList();
        return new ArchiveScanResult(request.getDataType(), request.getScanDate(), candidates);
    }

    public BusinessRecord archive(ArchiveRequest request) {
        validateOperationRequest(request);
        BusinessRecord record = findRecord(request.getRecordId());
        RetentionPolicy policy = activePolicy(record.getDataType());
        if (!isEligible(record, request.getOperatedAt().toLocalDate())) {
            throw new IllegalArgumentException("记录未达到归档条件");
        }
        record.setStatus(RecordStatus.ARCHIVED);
        record.setArchiveStore(policy.getArchiveStore());
        record.setArchivedAt(request.getOperatedAt());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveRecord(record);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveOperation(new ArchiveOperation(UUID.randomUUID().toString(), record.getRecordId(),
                ArchiveOperationType.ARCHIVE, request.getOperator(), request.getReason(), request.getOperatedAt()));
        return record;
    }

    public BusinessRecord restore(ArchiveRequest request) {
        validateOperationRequest(request);
        BusinessRecord record = findRecord(request.getRecordId());
        if (record.getStatus() != RecordStatus.ARCHIVED) {
            throw new IllegalArgumentException("只有已归档记录可以恢复");
        }
        // Restore returns the same logical record to active state; audit is kept in operations, not in payload.
        record.setStatus(RecordStatus.ACTIVE);
        record.setArchiveStore(null);
        record.setArchivedAt(null);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveRecord(record);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveOperation(new ArchiveOperation(UUID.randomUUID().toString(), record.getRecordId(),
                ArchiveOperationType.RESTORE, request.getOperator(), request.getReason(), request.getOperatedAt()));
        return record;
    }

    public List<RetentionPolicy> policies() {
        return repository.policies().stream().sorted(Comparator.comparing(RetentionPolicy::getPolicyId)).toList();
    }

    public List<BusinessRecord> records() {
        return repository.records().stream().sorted(Comparator.comparing(BusinessRecord::getRecordId)).toList();
    }

    public List<ArchiveOperation> operations() {
        return repository.operations();
    }

    private boolean isEligible(BusinessRecord record, java.time.LocalDate scanDate) {
        RetentionPolicy policy = repository.findPolicyByDataType(record.getDataType()).orElse(null);
        if (policy == null || !policy.isEnabled() || record.getStatus() != RecordStatus.ACTIVE) {
            return false;
        }
        // Candidate rule: createdAt + retentionDays <= scanDate.
        return !record.getCreatedAt().plusDays(policy.getRetentionDays()).isAfter(scanDate);
    }

    private RetentionPolicy activePolicy(String dataType) {
        RetentionPolicy policy = repository.findPolicyByDataType(dataType)
                .orElseThrow(() -> new NoSuchElementException("保留策略不存在: " + dataType));
        if (!policy.isEnabled()) throw new IllegalArgumentException("保留策略未启用");
        return policy;
    }

    private BusinessRecord findRecord(String recordId) {
        return repository.findRecord(recordId).orElseThrow(() -> new NoSuchElementException("业务记录不存在: " + recordId));
    }

    private void validatePolicy(RetentionPolicy policy) {
        if (policy == null) throw new IllegalArgumentException("policy 不能为空");
        if (isBlank(policy.getPolicyId())) throw new IllegalArgumentException("policyId 不能为空");
        if (isBlank(policy.getDataType())) throw new IllegalArgumentException("dataType 不能为空");
        if (policy.getRetentionDays() <= 0) throw new IllegalArgumentException("retentionDays 必须大于 0");
        if (isBlank(policy.getArchiveStore())) throw new IllegalArgumentException("archiveStore 不能为空");
    }

    private void validateRecord(BusinessRecord record) {
        if (record == null) throw new IllegalArgumentException("record 不能为空");
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/archive/ArchiveRetentionRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/archive/ArchiveRetentionRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class ArchiveRetentionRepository {
    private final Map<String, RetentionPolicy> policies = new LinkedHashMap<>();
    private final Map<String, BusinessRecord> records = new LinkedHashMap<>();
    private final Map<String, ArchiveOperation> operations = new LinkedHashMap<>();

    public RetentionPolicy savePolicy(RetentionPolicy policy) {
        policies.put(policy.getPolicyId(), policy);
        return policy;
    }

    public BusinessRecord saveRecord(BusinessRecord record) {
        records.put(record.getRecordId(), record);
        return record;
    }

    public ArchiveOperation saveOperation(ArchiveOperation operation) {
        operations.put(operation.getOperationId(), operation);
        return operation;
    }

    public Optional<RetentionPolicy> findPolicyByDataType(String dataType) {
        return policies.values().stream().filter(policy -> policy.getDataType().equals(dataType)).findFirst();
    }

    public Optional<BusinessRecord> findRecord(String recordId) {
        return Optional.ofNullable(records.get(recordId));
    }

    public List<RetentionPolicy> policies() {
        return new ArrayList<>(policies.values());
    }

    public List<BusinessRecord> records() {
        return new ArrayList<>(records.values());
    }

    public List<ArchiveOperation> operations() {
        return new ArrayList<>(operations.values());
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

1. ArchiveRetentionController：接收 HTTP 请求并转换成 Java 方法调用
2. ArchiveRetentionService：执行案例的核心业务规则
3. ArchiveRetentionRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/archive`：模块说明
- `POST /api/archive/policies`：创建或替换保留策略
- `GET /api/archive/policies`：查询保留策略
- `POST /api/archive/records`：创建或替换业务记录
- `GET /api/archive/records`：查询业务记录
- `POST /api/archive/scan`：扫描归档候选
- `POST /api/archive/archive`：归档记录
- `POST /api/archive/restore`：恢复记录
- `GET /api/archive/operations`：查询操作日志

## 调用验证

```bash
curl -X POST "http://localhost:8144/api/archive/policies" \
  -H "Content-Type: application/json" \
  -d '{"policyId":"P-ORDER","dataType":"ORDER","retentionDays":30,"archiveStore":"cold-order","enabled":true}'
```

```bash
curl -X POST "http://localhost:8144/api/archive/records" \
  -H "Content-Type: application/json" \
  -d '{"recordId":"R-OLD","dataType":"ORDER","ownerId":"owner-a","payload":"{\"amount\":100}","createdAt":"2026-03-01","status":"ACTIVE"}'
```

```bash
curl -X POST "http://localhost:8144/api/archive/scan" \
  -H "Content-Type: application/json" \
  -d '{"dataType":"ORDER","scanDate":"2026-05-08"}'
```

```bash
curl -X POST "http://localhost:8144/api/archive/archive" \
  -H "Content-Type: application/json" \
  -d '{"recordId":"R-OLD","operator":"compliance","reason":"到期归档","operatedAt":"2026-05-08T10:00:00"}'
```

```bash
curl -X POST "http://localhost:8144/api/archive/restore" \
  -H "Content-Type: application/json" \
  -d '{"recordId":"R-OLD","operator":"auditor","reason":"审计复查","operatedAt":"2026-05-08T10:00:00"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 保留策略表：数据类型、保留天数、冷存储位置、启用状态
- 活跃数据表或分区：存放在线查询数据
- 归档元数据表：记录冷存储位置、归档时间、恢复状态
- 冷存储：对象存储、低频访问存储、归档库
- 审计流水表：归档、恢复、操作人、原因、时间
- 审批流程：恢复敏感数据前需要审批和授权

## 生产差距

该示例用于隔离学习 数据归档与保留 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 64-SpringBoot-data-archive-retention test
```

## 要点总结

1. 数据保留策略
2. 业务记录管理
3. 归档候选扫描
4. 归档状态流转
5. 归档恢复

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
