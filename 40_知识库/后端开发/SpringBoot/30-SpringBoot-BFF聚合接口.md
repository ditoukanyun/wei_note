---
title: SpringBoot BFF 聚合接口
date: 2026-04-28
tags:
  - springboot
  - java
  - bff
  - api聚合
  - 降级
module: 30-SpringBoot-bff-aggregation
area: [[后端开发]]
created: 2026-04-28
---
# SpringBoot BFF 聚合接口

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/30-SpringBoot-bff-aggregation`

## 核心思路

本模块演示 [[BFF]] / API 聚合层：一个商品详情接口并行聚合商品主数据、库存、促销和评论摘要；当部分下游失败或超时时，只降级对应 section，并在响应中暴露 `degradedSections`。

## 项目结构

```text
src/main/java/com/cloud/
├── controller/BffAggregationController.java
├── service/
│   ├── BffAggregationService.java            (聚合核心)
│   └── downstream/
│       ├── MockCatalogClient.java
│       ├── MockInventoryClient.java
│       ├── MockPromotionClient.java
│       └── MockReviewClient.java
├── model/
│   ├── ProductDetailView.java
│   ├── SectionResult.java
│   ├── InventorySummary.java
│   ├── PromotionSummary.java
│   ├── ReviewSummary.java
│   └── AggregationOptions.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 聚合响应模型

| Section | 来源 | 是否核心 | 降级策略 |
|---------|------|----------|----------|
| product | 商品主数据 | 是 | 不存在直接 404 |
| inventory | 库存 | 否 | section 级降级 |
| promotion | 促销 | 否 | 超时或失败时降级 |
| review | 评论摘要 | 否 | section 级降级 |

主数据是页面骨架，查不到商品时没有继续聚合的意义；库存、促销、评论是附加信息，失败时可以返回部分结果。

## 并行聚合流程

```java
ProductBrief product = catalogClient.findById(productId)
        .orElseThrow(() -> new ProductNotFoundException(productId));

CompletableFuture<SectionResult<InventorySummary>> inventoryFuture = section(
        () -> inventoryClient.query(productId, options)
);
CompletableFuture<SectionResult<PromotionSummary>> promotionFuture = section(
        () -> promotionClient.query(productId, options)
);
CompletableFuture<SectionResult<ReviewSummary>> reviewFuture = section(
        () -> reviewClient.query(productId, options)
);

SectionResult<InventorySummary> inventory = inventoryFuture.join();
SectionResult<PromotionSummary> promotion = promotionFuture.join();
SectionResult<ReviewSummary> review = reviewFuture.join();
```

`CompletableFuture` 让三个独立下游并行执行，整体耗时接近最慢 section，而不是三个接口耗时相加。

## Section 级超时与降级

```java
private <T> CompletableFuture<SectionResult<T>> section(Supplier<T> supplier) {
    return CompletableFuture.supplyAsync(() -> SectionResult.ok(supplier.get()), executorService)
            .completeOnTimeout(SectionResult.degraded("TIMEOUT"), sectionTimeoutMs, TimeUnit.MILLISECONDS)
            .exceptionally(ex -> SectionResult.degraded(reasonOf(ex)));
}
```

每个 section 独立超时、独立降级：

- 正常返回：`SectionResult.ok(data)`
- 超时返回：`SectionResult.degraded("TIMEOUT")`
- 异常返回：`SectionResult.degraded("DOWNSTREAM_ERROR")`

> [!important] BFF 降级粒度
> BFF 不应该因为评论接口失败就让整个商品详情失败。更合理的方式是保留核心数据，并标记哪个 section 降级。

## 降级 section 汇总

```java
private List<String> degradedSections(SectionResult<InventorySummary> inventory,
                                      SectionResult<PromotionSummary> promotion,
                                      SectionResult<ReviewSummary> review) {
    List<String> sections = new ArrayList<>();
    if (inventory.isDegraded()) sections.add("inventory");
    if (promotion.isDegraded()) sections.add("promotion");
    if (review.isDegraded()) sections.add("review");
    return sections;
}
```

聚合响应中同时返回：

- 每个 section 的数据或降级状态
- `degraded`：整体是否存在降级
- `degradedSections`：具体哪些 section 降级

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bff` | 模块说明 |
| GET | `/api/bff/products/{id}` | 聚合商品详情 |
| GET | `/api/bff/products/{id}?inventoryFail=true` | 库存 section 降级 |
| GET | `/api/bff/products/{id}?promotionDelayMs=800` | 促销 section 超时降级 |
| GET | `/api/bff/products/{id}?reviewFail=true` | 评论 section 降级 |
| GET | `/api/bff/products/99999` | 商品不存在返回 404 |

## 调用验证

```bash
mvn -pl 30-SpringBoot-bff-aggregation spring-boot:run

curl "http://localhost:8110/api/bff/products/1"
curl "http://localhost:8110/api/bff/products/1?inventoryFail=true"
curl "http://localhost:8110/api/bff/products/1?promotionDelayMs=800"
curl "http://localhost:8110/api/bff/products/99999"
```

## 要点总结

1. [[BFF]] 适合为特定前端页面聚合多个后端能力
2. 独立下游应并行调用，降低聚合接口总耗时
3. 核心数据失败可以整体失败，非核心 section 应尽量部分降级
4. 响应中要暴露 `degradedSections`，让前端知道哪些区域不完整
5. section 超时比全局超时更细，可以避免单个慢下游拖垮整个页面

## 实践流程

```mermaid
flowchart LR
  A[定义页面模型] --> B[并发调用下游]
  B --> C[按 section 合并结果]
  C --> D[标记降级状态]
  D --> E[返回前端可渲染结构]
```

## 实践检查清单

- 是否按页面区域定义 section，而不是暴露下游服务结构。
- 每个下游是否有独立超时、错误和降级策略。
- 核心数据和非核心数据是否区分失败语义。
- 聚合响应是否明确 `degraded` 和 `degradedSections`。
- 是否记录下游耗时，便于定位慢接口。

## 案例

商品详情 BFF 中，商品主信息失败应整体失败；评论、促销、库存提示失败可以降级为空或默认值，并提示前端对应区域不完整。

## 常见误区

- BFF 承载过多业务规则，演变成新单体。
- 一个非核心下游超时导致整页失败。
- 前端不知道哪些 section 降级，展示出误导性信息。
