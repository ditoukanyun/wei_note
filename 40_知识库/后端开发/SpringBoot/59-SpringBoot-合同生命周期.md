---
title: SpringBoot 合同生命周期
date: 2026-05-11
tags:
  - springboot
  - java
  - 合同
  - 生命周期
module: 59-SpringBoot-contract-lifecycle
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 合同生命周期

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/59-SpringBoot-contract-lifecycle`

## 核心思路

本模块演示合同生命周期管理原型：创建合同草稿，更新版本化条款，提交签署，记录客户方和公司方签署，双方签署后生效，并支持到期扫描和主动终止。

## 能力点

- 合同草稿
- 条款版本
- 提交签署
- 双方签署
- 合同生效
- 到期处理
- 主动终止
- 时间线事件

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 合同生命周期 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ContractLifecycleController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ContractLifecycleController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/contracts")
public class ContractLifecycleController {
    private final ContractLifecycleService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ContractLifecycleController(ContractLifecycleService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "59-SpringBoot-contract-lifecycle");
        data.put("desc", "合同草稿、提交、签署、生效、到期、终止和时间线");
        data.put("apis", new String[]{
                "GET /api/contracts",
                "POST /api/contracts/drafts",
                "POST /api/contracts/{contractId}/terms",
                "POST /api/contracts/{contractId}/submit",
                "POST /api/contracts/{contractId}/sign/customer",
                "POST /api/contracts/{contractId}/sign/company",
                "POST /api/contracts/{contractId}/activate",
                "POST /api/contracts/{contractId}/terminate",
                "POST /api/contracts/expire-due",
                "GET /api/contracts/{contractId}",
                "GET /api/contracts/{contractId}/events"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/drafts")
    public ApiResult<ContractAgreement> createDraft(@RequestBody CreateContractRequest request) {
        return ApiResult.success(service.createDraft(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/terms")
    public ApiResult<ContractAgreement> updateTerms(@PathVariable String contractId,
                                                    @RequestBody UpdateTermsRequest request) {
        return ApiResult.success(service.updateTerms(contractId, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/submit")
    public ApiResult<ContractAgreement> submit(@PathVariable String contractId,
                                               @RequestBody OperatorRequest request) {
        return ApiResult.success(service.submit(contractId, request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/sign/customer")
    public ApiResult<ContractAgreement> signCustomer(@PathVariable String contractId,
                                                     @RequestBody OperatorRequest request) {
        return ApiResult.success(service.signCustomer(contractId, request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/sign/company")
    public ApiResult<ContractAgreement> signCompany(@PathVariable String contractId,
                                                    @RequestBody OperatorRequest request) {
        return ApiResult.success(service.signCompany(contractId, request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/activate")
    public ApiResult<ContractAgreement> activate(@PathVariable String contractId,
                                                 @RequestBody OperatorRequest request) {
        return ApiResult.success(service.activate(contractId, request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{contractId}/terminate")
    public ApiResult<ContractAgreement> terminate(@PathVariable String contractId,
                                                  @RequestBody TerminateContractRequest request) {
        return ApiResult.success(service.terminate(contractId, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/expire-due")
    public ApiResult<List<ContractAgreement>> expireDue(@RequestBody ExpireDueContractsRequest request) {
        return ApiResult.success(service.expireDue(request.getCurrentDate(), request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/{contractId}")
    public ApiResult<ContractAgreement> detail(@PathVariable String contractId) {
        return ApiResult.success(service.detail(contractId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/{contractId}/events")
    public ApiResult<List<ContractEvent>> events(@PathVariable String contractId) {
        return ApiResult.success(service.events(contractId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ContractLifecycleService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ContractLifecycleService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ContractLifecycleService {
    private final ContractRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ContractLifecycleService(ContractRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public ContractLifecycleService(ContractRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public ContractAgreement createDraft(CreateContractRequest request) {
        validateCreate(request);
        ContractAgreement contract = new ContractAgreement();
        contract.setContractId(UUID.randomUUID().toString());
        contract.setContractNo(request.getContractNo());
        contract.setTitle(request.getTitle());
        contract.setTenantId(request.getTenantId());
        contract.setCounterparty(request.getCounterparty());
        contract.setVersion(1);
        contract.setStatus(ContractStatus.DRAFT);
        contract.setEffectiveDate(request.getEffectiveDate());
        contract.setExpireDate(request.getExpireDate());
        contract.getTerms().add(new ContractTerm(1, request.getTermContent()));
        appendEvent(contract, "DRAFT_CREATED", "合同草稿已创建", request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement updateTerms(String contractId, UpdateTermsRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getTermContent())) throw new IllegalArgumentException("termContent 不能为空");
        if (isBlank(request.getOperator())) throw new IllegalArgumentException("operator 不能为空");
        ContractAgreement contract = find(contractId);
        ensureStatus(contract, ContractStatus.DRAFT, "只有草稿合同可以更新条款");
        int nextVersion = contract.getVersion() + 1;
        contract.setVersion(nextVersion);
        contract.getTerms().add(new ContractTerm(nextVersion, request.getTermContent()));
        appendEvent(contract, "TERMS_UPDATED", "合同条款更新到版本 " + nextVersion, request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement submit(String contractId, String operator) {
        validateOperator(operator);
        ContractAgreement contract = find(contractId);
        ensureStatus(contract, ContractStatus.DRAFT, "只有草稿合同可以提交");
        contract.setStatus(ContractStatus.SUBMITTED);
        appendEvent(contract, "SUBMITTED", "合同已提交签署", operator);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement signCustomer(String contractId, String operator) {
        validateOperator(operator);
        ContractAgreement contract = find(contractId);
        ensureSignable(contract);
        contract.setCustomerSigned(true);
        refreshSignatureStatus(contract);
        appendEvent(contract, "CUSTOMER_SIGNED", "客户方已签署", operator);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement signCompany(String contractId, String operator) {
        validateOperator(operator);
        ContractAgreement contract = find(contractId);
        ensureSignable(contract);
        contract.setCompanySigned(true);
        refreshSignatureStatus(contract);
        appendEvent(contract, "COMPANY_SIGNED", "公司方已签署", operator);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement activate(String contractId, String operator) {
        validateOperator(operator);
        ContractAgreement contract = find(contractId);
        if (contract.getStatus() != ContractStatus.FULLY_SIGNED) {
            throw new IllegalArgumentException("合同必须双方签署后才能生效");
        }
        contract.setStatus(ContractStatus.ACTIVE);
        appendEvent(contract, "ACTIVATED", "合同已生效", operator);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public ContractAgreement terminate(String contractId, TerminateContractRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getReason())) throw new IllegalArgumentException("reason 不能为空");
        validateOperator(request.getOperator());
        ContractAgreement contract = find(contractId);
        ensureStatus(contract, ContractStatus.ACTIVE, "只有生效合同可以终止");
        contract.setStatus(ContractStatus.TERMINATED);
        appendEvent(contract, "TERMINATED", request.getReason(), request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(contract);
    }

    public List<ContractAgreement> expireDue(LocalDate currentDate, String operator) {
        if (currentDate == null) throw new IllegalArgumentException("currentDate 不能为空");
        validateOperator(operator);
        return repository.findAll().stream()
                .filter(contract -> contract.getStatus() == ContractStatus.ACTIVE)
                .filter(contract -> !contract.getExpireDate().isAfter(currentDate))
                .map(contract -> {
                    contract.setStatus(ContractStatus.EXPIRED);
                    appendEvent(contract, "EXPIRED", "合同已到期", operator);
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/contract/ContractRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/contract/ContractRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class ContractRepository {
    private final Map<String, ContractAgreement> contracts = new ConcurrentHashMap<>();

    public ContractAgreement save(ContractAgreement contract) {
        contracts.put(contract.getContractId(), contract);
        return contract;
    }

    public Optional<ContractAgreement> findById(String contractId) {
        return Optional.ofNullable(contracts.get(contractId));
    }

    public List<ContractAgreement> findAll() {
        return new ArrayList<>(contracts.values());
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

1. ContractLifecycleController：接收 HTTP 请求并转换成 Java 方法调用
2. ContractLifecycleService：执行案例的核心业务规则
3. ContractRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/contracts`：模块说明
- `POST /api/contracts/drafts`：创建合同草稿
- `POST /api/contracts/{contractId}/terms`：更新草稿条款
- `POST /api/contracts/{contractId}/submit`：提交签署
- `POST /api/contracts/{contractId}/sign/customer`：客户方签署
- `POST /api/contracts/{contractId}/sign/company`：公司方签署
- `POST /api/contracts/{contractId}/activate`：合同生效
- `POST /api/contracts/{contractId}/terminate`：合同终止
- `POST /api/contracts/expire-due`：到期合同扫描
- `GET /api/contracts/{contractId}`：查询合同详情
- `GET /api/contracts/{contractId}/events`：查询合同时间线

## 调用验证

```bash
curl -X POST "http://localhost:8139/api/contracts/drafts" \
  -H "Content-Type: application/json" \
  -d '{"contractNo":"C-2026-001","title":"年度服务合同","tenantId":"tenant-a","counterparty":"示例客户","effectiveDate":"2026-05-01","expireDate":"2026-05-31","termContent":"第一版条款","operator":"sales"}'
```

```bash
curl -X POST "http://localhost:8139/api/contracts/{contractId}/submit" \
  -H "Content-Type: application/json" \
  -d '{"operator":"sales"}'
```

```bash
curl -X POST "http://localhost:8139/api/contracts/expire-due" \
  -H "Content-Type: application/json" \
  -d '{"currentDate":"2026-06-01","operator":"system"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 合同主表：合同编号、租户、相对方、状态、生效/到期日期
- 条款版本表：每次条款更新生成新版本
- 签署记录表：客户方、公司方签署结果和回调信息
- 合同事件表：状态变更审计时间线
- 电子签：对接第三方电子签平台
- 文件存储：合同 PDF、附件、签章文件
- 定时任务：扫描到期合同并生成审计记录

## 生产差距

该示例用于隔离学习 合同生命周期 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 59-SpringBoot-contract-lifecycle test
```

## 要点总结

1. 合同草稿
2. 条款版本
3. 提交签署
4. 双方签署
5. 合同生效

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
