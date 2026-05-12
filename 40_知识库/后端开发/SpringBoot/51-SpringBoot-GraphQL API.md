---
title: SpringBoot GraphQL API
date: 2026-05-11
tags:
  - springboot
  - java
  - graphql
module: 51-SpringBoot-graphql-api
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot GraphQL API

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/51-SpringBoot-graphql-api`

## 核心思路

本模块演示 Spring for GraphQL：显式 schema、resolver、查询聚合、mutation 校验，以及用批量加载统计说明 N+1 问题的规避思路。

## 能力点

- GraphQL schema
- `@QueryMapping`
- `@MutationMapping`
- 查询过滤
- 聚合查询
- mutation 入参校验
- 批量加载原型

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot GraphQL API 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ShopGraphqlController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ShopGraphqlController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
@Controller
public class ShopGraphqlController {

    private final GraphqlDemoService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ShopGraphqlController(GraphqlDemoService service) {
        this.service = service;
    }

    @QueryMapping
    public List<Product> products(@Argument String category) {
        return service.products(category);
    }

    @QueryMapping
    public List<Customer> customers(@Argument String level) {
        return service.customers(level);
    }

    @QueryMapping
    public List<ShopOrder> orders(@Argument String status) {
        return service.orders(status);
    }

    @QueryMapping
    public ShopOrder order(@Argument String id) {
        return service.order(id);
    }

    @QueryMapping
    public OrderSummaryConnection orderSummaries(@Argument String status) {
        return service.orderSummaries(status);
    }

    @MutationMapping
    public ShopOrder createOrder(@Argument CreateOrderInput input) {
        return service.createOrder(input);
    }

    @MutationMapping
    public ShopOrder updateOrderStatus(@Argument UpdateOrderStatusInput input) {
        return service.updateOrderStatus(input);
    }

    @GraphQlExceptionHandler
    public GraphQLError handleRuntimeException(RuntimeException exception) {
        return GraphqlErrorBuilder.newError()
                .message(exception.getMessage())
                .build();
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/GraphqlDemoService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/GraphqlDemoService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class GraphqlDemoService {

    private static final Set<String> SUPPORTED_STATUSES = Set.of("CREATED", "PAID", "SHIPPED", "CANCELLED");

    private final Map<String, Product> products = new LinkedHashMap<>();
    private final Map<String, Customer> customers = new LinkedHashMap<>();
    private final Map<String, ShopOrder> orders = new LinkedHashMap<>();
    private int nextOrderNumber = 1003;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public GraphqlDemoService() {
        products.put("P100", new Product("P100", "Phone", "ELECTRONICS", 799.0));
        products.put("P200", new Product("P200", "Headphones", "ELECTRONICS", 199.0));
        products.put("P300", new Product("P300", "Book", "BOOK", 39.0));

        customers.put("C100", new Customer("C100", "Alice", "VIP"));
        customers.put("C200", new Customer("C200", "Bob", "NORMAL"));

        orders.put("O1001", new ShopOrder("O1001", "C100", List.of("P100", "P200"), "PAID", 998.0));
        orders.put("O1002", new ShopOrder("O1002", "C200", List.of("P300"), "CREATED", 39.0));
    }

    public List<Product> products(String category) {
        return products.values().stream()
                .filter(product -> isBlank(category) || product.getCategory().equals(category))
                .toList();
    }

    public List<Customer> customers(String level) {
        return customers.values().stream()
                .filter(customer -> isBlank(level) || customer.getLevel().equals(level))
                .toList();
    }

    public List<ShopOrder> orders(String status) {
        return orders.values().stream()
                .filter(order -> isBlank(status) || order.getStatus().equals(status))
                .toList();
    }

    public ShopOrder order(String id) {
        return orders.get(id);
    }

    public ShopOrder createOrder(CreateOrderInput input) {
        validateCreateOrder(input);
        List<Product> selectedProducts = input.getProductIds().stream()
                .map(this::findProduct)
                .toList();
        double totalAmount = selectedProducts.stream()
                .mapToDouble(Product::getPrice)
                .sum();
        ShopOrder order = new ShopOrder("O" + nextOrderNumber++, input.getCustomerId(), input.getProductIds(), "CREATED", totalAmount);
        orders.put(order.getId(), order);
        return order;
    }

    public ShopOrder updateOrderStatus(UpdateOrderStatusInput input) {
        if (input == null || isBlank(input.getOrderId())) {
            throw new IllegalArgumentException("orderId 不能为空");
        }
        if (isBlank(input.getStatus())) {
            throw new IllegalArgumentException("status 不能为空");
        }
        if (!SUPPORTED_STATUSES.contains(input.getStatus())) {
            throw new IllegalArgumentException("订单状态不支持: " + input.getStatus());
        }
        ShopOrder order = orders.get(input.getOrderId());
        if (order == null) {
            throw new NoSuchElementException("订单不存在: " + input.getOrderId());
        }
        order.setStatus(input.getStatus());
        return order;
    }

    public OrderSummaryConnection orderSummaries(String status) {
        List<ShopOrder> selectedOrders = orders(status);
        Set<String> customerIds = new LinkedHashSet<>();
        Set<String> productIds = new LinkedHashSet<>();
        selectedOrders.forEach(order -> {
            customerIds.add(order.getCustomerId());
            productIds.addAll(order.getProductIds());
        });

        AtomicInteger batchLookupCount = new AtomicInteger();
        Map<String, Customer> customerMap = batchCustomers(customerIds, batchLookupCount);
        Map<String, Product> productMap = batchProducts(productIds, batchLookupCount);

        List<OrderSummary> summaries = selectedOrders.stream()
                .map(order -> new OrderSummary(
                        order.getId(),
                        customerMap.get(order.getCustomerId()).getName(),
                        order.getStatus(),
                        order.getProductIds().stream()
                                .map(productId -> productMap.get(productId).getName())
                                .toList(),
                        order.getTotalAmount()
                ))
                .toList();
        return new OrderSummaryConnection(summaries, batchLookupCount.get());
    }

    private Map<String, Customer> batchCustomers(Collection<String> customerIds, AtomicInteger batchLookupCount) {
        batchLookupCount.incrementAndGet();
        Map<String, Customer> result = new LinkedHashMap<>();
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

- 从 README 的接口或测试名称开始，先定位入口类。
- 找 Controller、Runner、Listener 或 AutoConfiguration 作为第一阅读点。
- 沿着构造器注入的依赖继续进入 Service、Repository 或扩展点类。

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## 调用验证

查询商品：

```bash
curl -X POST "http://localhost:8131/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { products(category: \"ELECTRONICS\") { id name category price } }"}'
```

创建订单：

```bash
curl -X POST "http://localhost:8131/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { createOrder(input: {customerId: \"C100\", productIds: [\"P100\", \"P300\"]}) { id customerId status totalAmount } }"}'
```

查询聚合摘要：

```bash
curl -X POST "http://localhost:8131/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { orderSummaries(status: \"CREATED\") { batchLookupCount summaries { id customerName itemNames totalAmount } } }"}'
```

## 生产映射

本模块使用内存数据和手写批量查询。生产环境通常替换为：

- 数据源：MySQL/PostgreSQL + JPA/MyBatis
- N+1 处理：GraphQL Java DataLoader
- 校验：Bean Validation + 业务校验
- 错误：统一 GraphQL error extensions，例如 code、traceId
- 安全：字段级权限、query depth/complexity 限制、persisted queries
- 可观测：resolver 耗时、错误率、慢查询日志

## 生产差距

该示例用于隔离学习 GraphQL API 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 51-SpringBoot-graphql-api test
```

## 要点总结

1. GraphQL schema
2. `@QueryMapping`
3. `@MutationMapping`
4. 查询过滤
5. 聚合查询

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
