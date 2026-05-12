---
title: SpringBoot 优惠券与促销
date: 2026-05-11
tags:
  - springboot
  - java
  - 促销
module: 61-SpringBoot-coupon-promotion
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 优惠券与促销

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/61-SpringBoot-coupon-promotion`

## 核心思路

本模块演示优惠券促销的核心链路：创建优惠券模板，向用户发券，按订单金额和有效期试算优惠，并在订单创建时核销优惠券。

## 能力点

- 优惠券模板
- 用户券发放
- 库存扣减
- 固定金额优惠
- 百分比优惠
- 最低订单金额门槛
- 有效期校验
- 核销幂等

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 优惠券与促销 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/CouponPromotionController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/CouponPromotionController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/coupons")
public class CouponPromotionController {
    private final CouponPromotionService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CouponPromotionController(CouponPromotionService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "61-SpringBoot-coupon-promotion");
        data.put("desc", "优惠券模板、发券、试算、核销和幂等兑换");
        data.put("apis", new String[]{
                "GET /api/coupons",
                "POST /api/coupons/templates",
                "GET /api/coupons/templates",
                "POST /api/coupons/issue",
                "POST /api/coupons/evaluate",
                "POST /api/coupons/redeem",
                "GET /api/coupons/users/{userId}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/templates")
    public ApiResult<CouponTemplate> saveTemplate(@RequestBody CouponTemplate template) {
        return ApiResult.success(service.saveTemplate(template));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/templates")
    public ApiResult<List<CouponTemplate>> templates() {
        return ApiResult.success(service.templates());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/issue")
    public ApiResult<UserCoupon> issueCoupon(@RequestBody IssueCouponRequest request) {
        return ApiResult.success(service.issueCoupon(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/evaluate")
    public ApiResult<CouponEvaluation> evaluate(@RequestBody EvaluationRequest request) {
        return ApiResult.success(service.evaluate(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/redeem")
    public ApiResult<CouponEvaluation> redeem(@RequestBody EvaluationRequest request) {
        return ApiResult.success(service.redeem(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/users/{userId}")
    public ApiResult<List<UserCoupon>> userCoupons(@PathVariable String userId) {
        return ApiResult.success(service.userCoupons(userId));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/CouponPromotionService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/CouponPromotionService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class CouponPromotionService {
    private final CouponRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public CouponPromotionService(CouponRepository repository) {
        this.repository = repository;
    }

    public CouponTemplate saveTemplate(CouponTemplate template) {
        validateTemplate(template);
        template.setDiscountValue(money(template.getDiscountValue()));
        template.setMinOrderAmount(money(template.getMinOrderAmount()));
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveTemplate(template);
    }

    public UserCoupon issueCoupon(IssueCouponRequest request) {
        if (request == null) throw new IllegalArgumentException("request 不能为空");
        if (isBlank(request.getTemplateId())) throw new IllegalArgumentException("templateId 不能为空");
        if (isBlank(request.getUserId())) throw new IllegalArgumentException("userId 不能为空");
        CouponTemplate template = findTemplate(request.getTemplateId());
        if (template.getIssuedCount() >= template.getTotalStock()) {
            throw new IllegalArgumentException("优惠券库存不足");
        }
        template.setIssuedCount(template.getIssuedCount() + 1);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveTemplate(template);
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        return repository.saveUserCoupon(new UserCoupon(UUID.randomUUID().toString(), template.getTemplateId(),
                request.getUserId(), UserCouponStatus.UNUSED, null));
    }

    public CouponEvaluation evaluate(EvaluationRequest request) {
        validateEvaluation(request);
        UserCoupon coupon = findUserCoupon(request.getUserCouponId());
        CouponTemplate template = findTemplate(coupon.getTemplateId());
        BigDecimal orderAmount = money(request.getOrderAmount());
        if (!coupon.getUserId().equals(request.getUserId())) {
            return deny("USER_NOT_MATCH", "优惠券不属于当前用户", orderAmount, coupon);
        }
        if (coupon.getStatus() == UserCouponStatus.USED) {
            return deny("COUPON_USED", "优惠券已使用", orderAmount, coupon);
        }
        return evaluateUnused(template, coupon, request, "ELIGIBLE");
    }

    public CouponEvaluation redeem(EvaluationRequest request) {
        validateEvaluation(request);
        UserCoupon coupon = findUserCoupon(request.getUserCouponId());
        CouponTemplate template = findTemplate(coupon.getTemplateId());
        if (coupon.getStatus() == UserCouponStatus.USED) {
            if (request.getOrderNo().equals(coupon.getUsedOrderNo())) {
                // Same coupon + same order is treated as idempotent success for retry-safe order creation.
                return success("IDEMPOTENT_REDEEMED", "重复核销请求已幂等返回", template, coupon, money(request.getOrderAmount()));
            }
            return deny("COUPON_USED", "优惠券已使用", money(request.getOrderAmount()), coupon);
        }
        CouponEvaluation evaluation = evaluateUnused(template, coupon, request, "ELIGIBLE");
        if (evaluation.isEligible()) {
            coupon.setStatus(UserCouponStatus.USED);
            coupon.setUsedOrderNo(request.getOrderNo());
            // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
            repository.saveUserCoupon(coupon);
            evaluation.setUserCoupon(coupon);
        }
        return evaluation;
    }

    public List<CouponTemplate> templates() {
        return repository.templates().stream().sorted(Comparator.comparing(CouponTemplate::getTemplateId)).toList();
    }

    public List<UserCoupon> userCoupons(String userId) {
        if (isBlank(userId)) throw new IllegalArgumentException("userId 不能为空");
        return repository.userCoupons().stream()
                .filter(coupon -> coupon.getUserId().equals(userId))
                .sorted(Comparator.comparing(UserCoupon::getTemplateId).thenComparing(UserCoupon::getUserCouponId))
                .toList();
    }

    private CouponEvaluation evaluateUnused(CouponTemplate template, UserCoupon coupon, EvaluationRequest request, String successReason) {
        BigDecimal orderAmount = money(request.getOrderAmount());
        if (request.getOrderDate().isBefore(template.getValidFrom())) {
            return deny("COUPON_NOT_STARTED", "优惠券未到可用日期", orderAmount, coupon);
        }
        if (request.getOrderDate().isAfter(template.getValidTo())) {
            return deny("COUPON_EXPIRED", "优惠券已过期", orderAmount, coupon);
        }
        if (orderAmount.compareTo(template.getMinOrderAmount()) < 0) {
            return deny("MIN_ORDER_NOT_MET", "订单金额未达到使用门槛", orderAmount, coupon);
        }
        return success(successReason, "优惠券可用", template, coupon, orderAmount);
    }

    private CouponEvaluation success(String reasonCode, String message, CouponTemplate template, UserCoupon coupon, BigDecimal orderAmount) {
        BigDecimal discount = calculateDiscount(template, orderAmount);
        return new CouponEvaluation(true, reasonCode, message, discount, money(orderAmount.subtract(discount)), coupon);
    }

    private CouponEvaluation deny(String reasonCode, String message, BigDecimal orderAmount, UserCoupon coupon) {
        return new CouponEvaluation(false, reasonCode, message, money(BigDecimal.ZERO), orderAmount, coupon);
    }

    private BigDecimal calculateDiscount(CouponTemplate template, BigDecimal orderAmount) {
        // FIXED_AMOUNT caps at order amount; PERCENT_OFF uses discountValue as a discount ratio, such as 0.20.
        BigDecimal discount = template.getDiscountType() == DiscountType.FIXED_AMOUNT
                ? template.getDiscountValue().min(orderAmount)
                : orderAmount.multiply(template.getDiscountValue());
        return money(discount.min(orderAmount));
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/coupon/CouponRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/coupon/CouponRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class CouponRepository {
    private final Map<String, CouponTemplate> templates = new ConcurrentHashMap<>();
    private final Map<String, UserCoupon> userCoupons = new ConcurrentHashMap<>();

    public CouponTemplate saveTemplate(CouponTemplate template) {
        templates.put(template.getTemplateId(), template);
        return template;
    }

    public Optional<CouponTemplate> findTemplate(String templateId) {
        return Optional.ofNullable(templates.get(templateId));
    }

    public List<CouponTemplate> templates() {
        return new ArrayList<>(templates.values());
    }

    public UserCoupon saveUserCoupon(UserCoupon coupon) {
        userCoupons.put(coupon.getUserCouponId(), coupon);
        return coupon;
    }

    public Optional<UserCoupon> findUserCoupon(String userCouponId) {
        return Optional.ofNullable(userCoupons.get(userCouponId));
    }

    public List<UserCoupon> userCoupons() {
        return new ArrayList<>(userCoupons.values());
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

1. CouponPromotionController：接收 HTTP 请求并转换成 Java 方法调用
2. CouponPromotionService：执行案例的核心业务规则
3. CouponRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/coupons`：模块说明
- `POST /api/coupons/templates`：创建或替换优惠券模板
- `GET /api/coupons/templates`：查询优惠券模板
- `POST /api/coupons/issue`：向用户发券
- `POST /api/coupons/evaluate`：试算优惠券
- `POST /api/coupons/redeem`：核销优惠券
- `GET /api/coupons/users/{userId}`：查询用户券

## 调用验证

```bash
curl -X POST "http://localhost:8141/api/coupons/templates" \
  -H "Content-Type: application/json" \
  -d '{"templateId":"T-100-30","name":"满100减30","discountType":"FIXED_AMOUNT","discountValue":30.00,"minOrderAmount":100.00,"totalStock":10,"issuedCount":0,"validFrom":"2026-05-01","validTo":"2026-05-31"}'
```

```bash
curl -X POST "http://localhost:8141/api/coupons/issue" \
  -H "Content-Type: application/json" \
  -d '{"templateId":"T-100-30","userId":"user-a"}'
```

```bash
curl -X POST "http://localhost:8141/api/coupons/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userCouponId":"替换为发券返回的 userCouponId","userId":"user-a","orderNo":"O-1","orderAmount":120.00,"orderDate":"2026-05-08"}'
```

```bash
curl -X POST "http://localhost:8141/api/coupons/redeem" \
  -H "Content-Type: application/json" \
  -d '{"userCouponId":"替换为发券返回的 userCouponId","userId":"user-a","orderNo":"O-1","orderAmount":120.00,"orderDate":"2026-05-08"}'
```

## 生产映射

本模块使用内存仓储。生产环境通常替换为：

- 优惠券模板表：折扣类型、门槛、库存、有效期、状态
- 用户券表：用户、模板、状态、领取时间、使用订单
- 核销流水表：订单号、用户券、优惠金额、幂等键
- 促销试算服务：订单创建前预估应付金额
- 订单事务：创建订单、锁定/核销优惠券、写核销流水在同一事务边界内完成
- 风控/限购：限制领取频次、黑名单、渠道规则

## 生产差距

该示例用于隔离学习 优惠券与促销 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 61-SpringBoot-coupon-promotion test
```

## 要点总结

1. 优惠券模板
2. 用户券发放
3. 库存扣减
4. 固定金额优惠
5. 百分比优惠

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
