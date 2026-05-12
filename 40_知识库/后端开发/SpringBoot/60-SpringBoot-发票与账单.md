---
title: SpringBoot 发票与账单
date: 2026-05-11
tags:
  - springboot
  - java
  - 计费
module: 60-SpringBoot-invoice-billing
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 发票与账单

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/60-SpringBoot-invoice-billing`

## 核心思路

本模块演示发票申请与状态流转原型：从可开票明细创建发票申请，按类别聚合发票行，计算总金额，并支持开票、付款和作废。

## 能力点

- 发票申请
- 可开票明细
- 明细聚合
- 金额合计
- 开票
- 作废
- 付款状态
- 发票事件时间线

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 发票与账单 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/InvoiceBillingController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/InvoiceBillingController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/invoices")
public class InvoiceBillingController {
    private final InvoiceBillingService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InvoiceBillingController(InvoiceBillingService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "60-SpringBoot-invoice-billing");
        data.put("desc", "发票申请、明细聚合、开票、作废和付款状态");
        data.put("apis", new String[]{
                "GET /api/invoices",
                "POST /api/invoices/applications",
                "POST /api/invoices/{invoiceId}/issue",
                "POST /api/invoices/{invoiceId}/void",
                "POST /api/invoices/{invoiceId}/paid",
                "GET /api/invoices/{invoiceId}",
                "GET /api/invoices/{invoiceId}/events",
                "GET /api/invoices/applications"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/applications")
    public ApiResult<InvoiceApplication> applyInvoice(@RequestBody ApplyInvoiceRequest request) {
        return ApiResult.success(service.applyInvoice(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{invoiceId}/issue")
    public ApiResult<InvoiceApplication> issue(@PathVariable String invoiceId,
                                               @RequestBody IssueInvoiceRequest request) {
        return ApiResult.success(service.issue(invoiceId, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{invoiceId}/void")
    public ApiResult<InvoiceApplication> voidInvoice(@PathVariable String invoiceId,
                                                     @RequestBody VoidInvoiceRequest request) {
        return ApiResult.success(service.voidInvoice(invoiceId, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/{invoiceId}/paid")
    public ApiResult<InvoiceApplication> markPaid(@PathVariable String invoiceId,
                                                  @RequestBody OperatorRequest request) {
        return ApiResult.success(service.markPaid(invoiceId, request.getOperator()));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/{invoiceId}")
    public ApiResult<InvoiceApplication> detail(@PathVariable String invoiceId) {
        return ApiResult.success(service.detail(invoiceId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/{invoiceId}/events")
    public ApiResult<List<InvoiceEvent>> events(@PathVariable String invoiceId) {
        return ApiResult.success(service.events(invoiceId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/applications")
    public ApiResult<List<InvoiceApplication>> invoices() {
        return ApiResult.success(service.invoices());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/InvoiceBillingService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/InvoiceBillingService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class InvoiceBillingService {
    private final InvoiceRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InvoiceBillingService(InvoiceRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public InvoiceBillingService(InvoiceRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public InvoiceApplication applyInvoice(ApplyInvoiceRequest request) {
        validateApply(request);
        List<BillableItem> items = request.getItems().stream()
                .map(this::normalizeItem)
                .toList();
        List<InvoiceLine> lines = aggregateLines(items);
        BigDecimal totalAmount = lines.stream()
                .map(InvoiceLine::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .setScale(2, RoundingMode.HALF_UP);

        InvoiceApplication invoice = new InvoiceApplication();
        invoice.setInvoiceId(UUID.randomUUID().toString());
        invoice.setTenantId(request.getTenantId());
        invoice.setBuyerName(request.getBuyerName());
        invoice.setStatus(InvoiceStatus.APPLIED);
        invoice.setTotalAmount(totalAmount);
        invoice.setAppliedAt(clock.instant());
        invoice.setItems(items);
        invoice.setLines(lines);
        appendEvent(invoice, "APPLIED", "发票申请已创建", request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(invoice);
    }

    public InvoiceApplication issue(String invoiceId, IssueInvoiceRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getInvoiceNo())) throw new IllegalArgumentException("invoiceNo 不能为空");
        validateOperator(request.getOperator());
        InvoiceApplication invoice = find(invoiceId);
        ensureStatus(invoice, InvoiceStatus.APPLIED, "只有已申请发票可以开票");
        invoice.setInvoiceNo(request.getInvoiceNo());
        invoice.setStatus(InvoiceStatus.ISSUED);
        appendEvent(invoice, "ISSUED", "发票已开具: " + request.getInvoiceNo(), request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(invoice);
    }

    public InvoiceApplication markPaid(String invoiceId, String operator) {
        validateOperator(operator);
        InvoiceApplication invoice = find(invoiceId);
        ensureStatus(invoice, InvoiceStatus.ISSUED, "只有已开具发票可以标记付款");
        invoice.setStatus(InvoiceStatus.PAID);
        appendEvent(invoice, "PAID", "发票已付款", operator);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(invoice);
    }

    public InvoiceApplication voidInvoice(String invoiceId, VoidInvoiceRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getReason())) throw new IllegalArgumentException("reason 不能为空");
        validateOperator(request.getOperator());
        InvoiceApplication invoice = find(invoiceId);
        if (invoice.getStatus() == InvoiceStatus.PAID) {
            throw new IllegalArgumentException("已付款发票不能作废");
        }
        if (invoice.getStatus() == InvoiceStatus.VOIDED) {
            throw new IllegalArgumentException("终态发票不能继续操作");
        }
        invoice.setStatus(InvoiceStatus.VOIDED);
        appendEvent(invoice, "VOIDED", request.getReason(), request.getOperator());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.save(invoice);
    }

    public InvoiceApplication detail(String invoiceId) {
        return find(invoiceId);
    }

    public List<InvoiceEvent> events(String invoiceId) {
        return find(invoiceId).getEvents();
    }

    public List<InvoiceApplication> invoices() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(InvoiceApplication::getTenantId).thenComparing(InvoiceApplication::getBuyerName))
                .toList();
    }

    private List<InvoiceLine> aggregateLines(List<BillableItem> items) {
        // Invoice applications usually show summarized lines, while source billable items remain traceable.
        return items.stream()
                .collect(Collectors.groupingBy(BillableItem::getCategory, TreeMap::new, Collectors.toList()))
                .entrySet().stream()
                .map(entry -> new InvoiceLine(entry.getKey(), entry.getValue().size(),
                        entry.getValue().stream().map(BillableItem::getAmount)
                                .reduce(BigDecimal.ZERO, BigDecimal::add)
                                .setScale(2, RoundingMode.HALF_UP)))
                .toList();
    }

    private BillableItem normalizeItem(BillableItem item) {
        return new BillableItem(item.getItemNo().trim(), item.getCategory().trim(), item.getDescription().trim(),
                item.getAmount().setScale(2, RoundingMode.HALF_UP));
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/invoice/InvoiceRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/invoice/InvoiceRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class InvoiceRepository {
    private final Map<String, InvoiceApplication> invoices = new ConcurrentHashMap<>();

    public InvoiceApplication save(InvoiceApplication invoice) {
        invoices.put(invoice.getInvoiceId(), invoice);
        return invoice;
    }

    public Optional<InvoiceApplication> findById(String invoiceId) {
        return Optional.ofNullable(invoices.get(invoiceId));
    }

    public List<InvoiceApplication> findAll() {
        return new ArrayList<>(invoices.values());
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

1. InvoiceBillingController：接收 HTTP 请求并转换成 Java 方法调用
2. InvoiceBillingService：执行案例的核心业务规则
3. InvoiceRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/invoices`：模块说明
- `POST /api/invoices/applications`：创建发票申请
- `POST /api/invoices/{invoiceId}/issue`：开票
- `POST /api/invoices/{invoiceId}/void`：作废
- `POST /api/invoices/{invoiceId}/paid`：标记付款
- `GET /api/invoices/{invoiceId}`：查询发票详情
- `GET /api/invoices/{invoiceId}/events`：查询发票事件
- `GET /api/invoices/applications`：查询发票申请列表

## 调用验证

```bash
curl -X POST "http://localhost:8140/api/invoices/applications" \
  -H "Content-Type: application/json" \
  -d '{"tenantId":"tenant-a","buyerName":"示例客户","operator":"finance","items":[{"itemNo":"ITEM-1","category":"SERVICE","description":"服务费","amount":100.00},{"itemNo":"ITEM-2","category":"SERVICE","description":"实施费","amount":50.00},{"itemNo":"ITEM-3","category":"STORAGE","description":"存储费","amount":20.00}]}'
```

```bash
curl -X POST "http://localhost:8140/api/invoices/{invoiceId}/issue" \
  -H "Content-Type: application/json" \
  -d '{"invoiceNo":"INV-2026-001","operator":"finance"}'
```

```bash
curl -X POST "http://localhost:8140/api/invoices/{invoiceId}/paid" \
  -H "Content-Type: application/json" \
  -d '{"operator":"finance"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 发票申请表：租户、购买方、状态、发票号、总金额
- 发票明细表：类别、数量、金额
- 可开票来源表：账单、订单、服务费、存储费等来源关联
- 税控/电子票平台：开票、作废、回调
- 财务事件表：申请、开票、付款、作废审计
- 下游系统：总账、结算、对账和税务申报

## 生产差距

该示例用于隔离学习 发票与账单 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 60-SpringBoot-invoice-billing test
```

## 要点总结

1. 发票申请
2. 可开票明细
3. 明细聚合
4. 金额合计
5. 开票

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
