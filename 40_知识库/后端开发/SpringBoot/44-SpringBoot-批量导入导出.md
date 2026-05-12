---
title: SpringBoot 批量导入导出
date: 2026-05-11
tags:
  - springboot
  - java
  - 批处理
module: 44-SpringBoot-batch-import-export
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 批量导入导出

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/44-SpringBoot-batch-import-export`

## 核心思路

本模块演示批量导入和导出元数据原型：提交 JSON 行数据后创建导入任务，后台异步处理并记录进度、成功数量、失败数量和逐行失败明细；导出接口基于已导入客户生成虚拟 CSV 文件元数据。

## 能力点

- 批量导入任务创建
- 异步任务进度查询
- 行级校验和失败明细
- 部分成功导入
- 导出文件元数据生成

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 批量导入导出 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/BatchImportExportController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/BatchImportExportController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/batch")
public class BatchImportExportController {

    private final BatchImportExportService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public BatchImportExportController(BatchImportExportService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "44-SpringBoot-batch-import-export");
        data.put("desc", "批量导入、行级校验失败明细、异步任务进度和导出元数据");
        data.put("apis", new String[]{
                "GET /api/batch",
                "POST /api/batch/imports",
                "GET /api/batch/imports/{taskId}",
                "POST /api/batch/exports",
                "GET /api/batch/exports/{exportId}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/imports")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public ApiResult<ImportTask> startImport(@RequestBody List<CustomerImportRow> rows) {
        return ApiResult.success(service.startImport(rows));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/imports/{taskId}")
    public ApiResult<ImportTask> importTask(@PathVariable String taskId) {
        return ApiResult.success(service.findImportTask(taskId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/exports")
    public ApiResult<ExportFileMetadata> createExport() {
        return ApiResult.success(service.createExport());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/exports/{exportId}")
    public ApiResult<ExportFileMetadata> export(@PathVariable String exportId) {
        return ApiResult.success(service.findExport(exportId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/BatchImportExportService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/BatchImportExportService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class BatchImportExportService {

    private static final DateTimeFormatter FILE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

    private final BatchJobRepository repository;
    private final Executor taskExecutor;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public BatchImportExportService(Executor taskExecutor) {
        this(new BatchJobRepository(), taskExecutor);
    }

    @Autowired
    public BatchImportExportService(BatchJobRepository repository, @Qualifier("batchTaskExecutor") Executor taskExecutor) {
        this.repository = repository;
        this.taskExecutor = taskExecutor;
    }

    public ImportTask startImport(List<CustomerImportRow> rows) {
        if (rows == null || rows.isEmpty()) {
            throw new IllegalArgumentException("导入数据不能为空");
        }

        ImportTask task = new ImportTask(UUID.randomUUID().toString(), rows.size());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveImportTask(task);
        taskExecutor.execute(() -> processImport(task, rows));
        return task;
    }

    public ImportTask findImportTask(String taskId) {
        return repository.findImportTask(taskId)
                .orElseThrow(() -> new NoSuchElementException("导入任务不存在: " + taskId));
    }

    public ExportFileMetadata createExport() {
        List<ImportedCustomer> customers = repository.customers();
        String exportId = UUID.randomUUID().toString();
        String fileName = "customers-" + LocalDateTime.now().format(FILE_TIME_FORMATTER) + ".csv";
        long sizeBytes = renderCsv(customers).getBytes(StandardCharsets.UTF_8).length;
        ExportFileMetadata metadata = new ExportFileMetadata(
                exportId,
                fileName,
                "text/csv",
                customers.size(),
                sizeBytes,
                "READY",
                LocalDateTime.now(),
                "/api/batch/exports/" + exportId + "/download"
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveExport(metadata);
        return metadata;
    }

    public ExportFileMetadata findExport(String exportId) {
        return repository.findExport(exportId)
                .orElseThrow(() -> new NoSuchElementException("导出文件不存在: " + exportId));
    }

    private void processImport(ImportTask task, List<CustomerImportRow> rows) {
        try {
            task.markRunning();
            for (CustomerImportRow row : rows) {
                List<ImportFailure> failures = validate(row);
                if (failures.isEmpty()) {
                    repository.addCustomer(toCustomer(row));
                    task.recordSuccess();
                } else {
                    task.recordFailure(failures);
                }
            }
            task.markCompleted();
        } catch (RuntimeException exception) {
            task.markFailed(exception.getMessage());
        }
    }

    private List<ImportFailure> validate(CustomerImportRow row) {
        List<ImportFailure> failures = new ArrayList<>();
        if (row.getName() == null || row.getName().isBlank()) {
            failures.add(new ImportFailure(row.getRowNumber(), "name", row.getName(), "客户姓名不能为空"));
        }
        if (row.getMobile() == null || !row.getMobile().matches("^1\\d{10}$")) {
            failures.add(new ImportFailure(row.getRowNumber(), "mobile", row.getMobile(), "手机号必须是 1 开头的 11 位数字"));
        }
        if (!"NORMAL".equals(row.getMemberLevel()) && !"VIP".equals(row.getMemberLevel())) {
            failures.add(new ImportFailure(row.getRowNumber(), "memberLevel", row.getMemberLevel(), "会员等级必须是 NORMAL 或 VIP"));
        }
        BigDecimal balance = row.getBalance();
        if (balance == null || balance.compareTo(BigDecimal.ZERO) < 0) {
            failures.add(new ImportFailure(row.getRowNumber(), "balance", String.valueOf(balance), "余额必须大于等于 0"));
        }
        return failures;
    }

    private ImportedCustomer toCustomer(CustomerImportRow row) {
        return new ImportedCustomer(
                UUID.randomUUID().toString(),
                row.getName().trim(),
                row.getMobile(),
                row.getMemberLevel(),
                row.getBalance(),
                LocalDateTime.now()
        );
    }

    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/AsyncConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/AsyncConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class AsyncConfig {

    // @Bean 的返回对象会进入 Spring 容器，之后可以被其他类注入使用。
    @Bean
    public Executor batchTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setThreadNamePrefix("batch-import-");
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(2);
        executor.setQueueCapacity(20);
        executor.initialize();
        return executor;
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/batch/BatchJobRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/batch/BatchJobRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class BatchJobRepository {

    private final ConcurrentMap<String, ImportTask> importTasks = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, ExportFileMetadata> exports = new ConcurrentHashMap<>();
    private final CopyOnWriteArrayList<ImportedCustomer> customers = new CopyOnWriteArrayList<>();

    public void saveImportTask(ImportTask task) {
        importTasks.put(task.getTaskId(), task);
    }

    public Optional<ImportTask> findImportTask(String taskId) {
        return Optional.ofNullable(importTasks.get(taskId));
    }

    public void addCustomer(ImportedCustomer customer) {
        customers.add(customer);
    }

    public List<ImportedCustomer> customers() {
        return new ArrayList<>(customers);
    }

    public void saveExport(ExportFileMetadata metadata) {
        exports.put(metadata.getExportId(), metadata);
    }

    public Optional<ExportFileMetadata> findExport(String exportId) {
        return Optional.ofNullable(exports.get(exportId));
    }
}
```

关键点拆解：

- 示例里的 Repository 多半是内存实现；真实项目要替换成数据库、缓存或外部服务。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. AsyncConfig：启动时注册配置、Bean 或扩展点
2. BatchImportExportController：接收 HTTP 请求并转换成 Java 方法调用
3. BatchImportExportService：执行案例的核心业务规则
4. BatchJobRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/batch`：模块说明和接口列表
- `POST /api/batch/imports`：创建导入任务
- `GET /api/batch/imports/{taskId}`：查询导入任务进度
- `POST /api/batch/exports`：创建导出元数据
- `GET /api/batch/exports/{exportId}`：查询导出元数据

## 调用验证

创建导入任务：

```bash
curl -X POST "http://localhost:8124/api/batch/imports" \
  -H "Content-Type: application/json" \
  -d '[
    {"rowNumber":1,"name":"Alice","mobile":"13800138000","memberLevel":"VIP","balance":99.50},
    {"rowNumber":2,"name":"","mobile":"13900139000","memberLevel":"NORMAL","balance":10},
    {"rowNumber":3,"name":"Bob","mobile":"bad-mobile","memberLevel":"GOLD","balance":1}
  ]'
```

用返回的 `taskId` 查询进度：

```bash
curl "http://localhost:8124/api/batch/imports/{taskId}"
```

创建导出元数据：

```bash
curl -X POST "http://localhost:8124/api/batch/exports"
```

## 生产差距

该示例用于隔离学习 批量导入导出 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 44-SpringBoot-batch-import-export test
```

## 要点总结

1. 批量导入任务创建
2. 异步任务进度查询
3. 行级校验和失败明细
4. 部分成功导入
5. 导出文件元数据生成

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
