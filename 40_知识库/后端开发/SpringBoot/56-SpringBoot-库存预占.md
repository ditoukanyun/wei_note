---
title: SpringBoot 库存预占
date: 2026-05-11
tags:
  - springboot
  - java
  - 库存
module: 56-SpringBoot-inventory-reservation
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 库存预占

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/56-SpringBoot-inventory-reservation`

## 核心思路

本模块演示库存预占原型：维护 SKU 可用库存、预占库存和已售库存，支持下单预占、支付确认扣减、主动释放、超时过期释放，并在预占阶段防止超卖。

## 能力点

- SKU 入库
- 库存预占
- 确认扣减
- 主动释放
- 超时过期
- 防超卖校验
- 预占单终态保护

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 库存预占 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/InventoryReservationController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/InventoryReservationController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/inventory")
public class InventoryReservationController {
    private final InventoryReservationService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InventoryReservationController(InventoryReservationService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "56-SpringBoot-inventory-reservation");
        data.put("desc", "库存预占、释放、过期、确认扣减和防超卖");
        data.put("apis", new String[]{
                "GET /api/inventory",
                "POST /api/inventory/skus",
                "GET /api/inventory/skus",
                "POST /api/inventory/reservations",
                "POST /api/inventory/reservations/{reservationId}/confirm",
                "POST /api/inventory/reservations/{reservationId}/release",
                "POST /api/inventory/reservations/expire-due",
                "GET /api/inventory/reservations"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/skus")
    public ApiResult<SkuInventory> restock(@RequestBody RestockRequest request) {
        return ApiResult.success(service.restock(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/skus")
    public ApiResult<List<SkuInventory>> inventories() {
        return ApiResult.success(service.inventories());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/reservations")
    public ApiResult<InventoryReservation> reserve(@RequestBody ReserveStockRequest request) {
        return ApiResult.success(service.reserve(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/reservations/{reservationId}/confirm")
    public ApiResult<InventoryReservation> confirm(@PathVariable String reservationId) {
        return ApiResult.success(service.confirm(reservationId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/reservations/{reservationId}/release")
    public ApiResult<InventoryReservation> release(@PathVariable String reservationId) {
        return ApiResult.success(service.release(reservationId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/reservations/expire-due")
    public ApiResult<List<InventoryReservation>> expireDue() {
        return ApiResult.success(service.expireDue());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/reservations")
    public ApiResult<List<InventoryReservation>> reservations() {
        return ApiResult.success(service.reservations());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/InventoryReservationService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/InventoryReservationService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class InventoryReservationService {
    private final InventoryRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public InventoryReservationService(InventoryRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public InventoryReservationService(InventoryRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public SkuInventory restock(RestockRequest request) {
        if (request == null || isBlank(request.getSkuId())) throw new IllegalArgumentException("skuId 不能为空");
        if (request.getQuantity() <= 0) throw new IllegalArgumentException("quantity 必须大于 0");
        SkuInventory inventory = repository.findInventory(request.getSkuId())
                .orElseGet(() -> new SkuInventory(request.getSkuId(), request.getSkuName(), 0, 0, 0));
        if (!isBlank(request.getSkuName())) {
            inventory.setSkuName(request.getSkuName());
        }
        inventory.restock(request.getQuantity());
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveInventory(inventory);
        return inventory;
    }

    public InventoryReservation reserve(ReserveStockRequest request) {
        if (request == null || isBlank(request.getSkuId())) throw new IllegalArgumentException("skuId 不能为空");
        if (isBlank(request.getOrderNo())) throw new IllegalArgumentException("orderNo 不能为空");
        if (request.getQuantity() <= 0) throw new IllegalArgumentException("quantity 必须大于 0");
        SkuInventory inventory = findInventory(request.getSkuId());
        if (inventory.getAvailableQuantity() < request.getQuantity()) {
            throw new IllegalArgumentException("可用库存不足");
        }
        inventory.reserve(request.getQuantity());
        Instant now = clock.instant();
        InventoryReservation reservation = new InventoryReservation(UUID.randomUUID().toString(), request.getSkuId(), request.getOrderNo(),
                request.getQuantity(), InventoryReservationStatus.RESERVED, now, now.plusSeconds(request.getTtlSeconds() <= 0 ? 900 : request.getTtlSeconds()), null);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveReservation(reservation);
        return reservation;
    }

    public InventoryReservation confirm(String reservationId) {
        InventoryReservation reservation = findReservation(reservationId);
        ensureReserved(reservation);
        findInventory(reservation.getSkuId()).confirm(reservation.getQuantity());
        reservation.setStatus(InventoryReservationStatus.CONFIRMED);
        reservation.setFinishedAt(clock.instant());
        return reservation;
    }

    public InventoryReservation release(String reservationId) {
        InventoryReservation reservation = findReservation(reservationId);
        ensureReserved(reservation);
        findInventory(reservation.getSkuId()).returnReserved(reservation.getQuantity());
        reservation.setStatus(InventoryReservationStatus.RELEASED);
        reservation.setFinishedAt(clock.instant());
        return reservation;
    }

    public List<InventoryReservation> expireDue() {
        Instant now = clock.instant();
        return repository.reservations().stream()
                .filter(reservation -> reservation.getStatus() == InventoryReservationStatus.RESERVED)
                .filter(reservation -> !reservation.getExpireAt().isAfter(now))
                .map(reservation -> {
                    findInventory(reservation.getSkuId()).returnReserved(reservation.getQuantity());
                    reservation.setStatus(InventoryReservationStatus.EXPIRED);
                    reservation.setFinishedAt(now);
                    return reservation;
                })
                .toList();
    }

    public List<SkuInventory> inventories() {
        return repository.inventories().stream().sorted(Comparator.comparing(SkuInventory::getSkuId)).toList();
    }

    public List<InventoryReservation> reservations() {
        return repository.reservations().stream().sorted(Comparator.comparing(InventoryReservation::getReservedAt)).toList();
    }

    private SkuInventory findInventory(String skuId) {
        return repository.findInventory(skuId).orElseThrow(() -> new NoSuchElementException("SKU 不存在: " + skuId));
    }

    private InventoryReservation findReservation(String reservationId) {
        return repository.findReservation(reservationId).orElseThrow(() -> new NoSuchElementException("预占单不存在: " + reservationId));
    }

    private void ensureReserved(InventoryReservation reservation) {
        if (reservation.getStatus() != InventoryReservationStatus.RESERVED) {
            throw new IllegalArgumentException("预占单已结束");
        }
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

源码位置：`src/main/java/com/cloud/inventory/InventoryRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/inventory/InventoryRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class InventoryRepository {
    private final Map<String, SkuInventory> inventories = new LinkedHashMap<>();
    private final Map<String, InventoryReservation> reservations = new LinkedHashMap<>();

    public void saveInventory(SkuInventory inventory) {
        inventories.put(inventory.getSkuId(), inventory);
    }

    public Optional<SkuInventory> findInventory(String skuId) {
        return Optional.ofNullable(inventories.get(skuId));
    }

    public List<SkuInventory> inventories() {
        return new ArrayList<>(inventories.values());
    }

    public void saveReservation(InventoryReservation reservation) {
        reservations.put(reservation.getReservationId(), reservation);
    }

    public Optional<InventoryReservation> findReservation(String reservationId) {
        return Optional.ofNullable(reservations.get(reservationId));
    }

    public List<InventoryReservation> reservations() {
        return new ArrayList<>(reservations.values());
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

1. InventoryReservationController：接收 HTTP 请求并转换成 Java 方法调用
2. InventoryReservationService：执行案例的核心业务规则
3. InventoryRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/inventory`：模块说明
- `POST /api/inventory/skus`：SKU 入库
- `GET /api/inventory/skus`：查询 SKU 库存列表
- `POST /api/inventory/reservations`：创建库存预占单
- `POST /api/inventory/reservations/{reservationId}/confirm`：确认扣减
- `POST /api/inventory/reservations/{reservationId}/release`：释放预占库存
- `POST /api/inventory/reservations/expire-due`：释放已到期预占单
- `GET /api/inventory/reservations`：查询预占单列表

## 调用验证

```bash
curl -X POST "http://localhost:8136/api/inventory/skus" \
  -H "Content-Type: application/json" \
  -d '{"skuId":"SKU-100","skuName":"测试商品","quantity":100}'
```

```bash
curl -X POST "http://localhost:8136/api/inventory/reservations" \
  -H "Content-Type: application/json" \
  -d '{"skuId":"SKU-100","orderNo":"O100","quantity":2,"ttlSeconds":900}'
```

```bash
curl -X POST "http://localhost:8136/api/inventory/reservations/{reservationId}/confirm"
```

```bash
curl -X POST "http://localhost:8136/api/inventory/reservations/expire-due"
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 库存表：可用、预占、已售、冻结等库存字段
- 预占单表：订单号、SKU、数量、过期时间、状态、版本号
- 并发控制：数据库乐观锁、行锁或 Redis Lua 原子扣减
- 过期处理：延迟消息、定时补偿任务或 Redis ZSet 扫描
- 幂等：订单号与业务动作幂等键
- 对账补偿：订单状态、支付状态和库存状态定期校验

## 生产差距

该示例用于隔离学习 库存预占 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 56-SpringBoot-inventory-reservation test
```

## 要点总结

1. SKU 入库
2. 库存预占
3. 确认扣减
4. 主动释放
5. 超时过期

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
