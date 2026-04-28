---
title: SpringBoot Feature Flag 与灰度发布
date: 2026-04-28
tags:
  - springboot
  - java
  - feature-flag
  - 灰度发布
  - 稳定哈希
module: 35-SpringBoot-feature-flag-gray-release
---
# SpringBoot Feature Flag 与灰度发布

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/35-SpringBoot-feature-flag-gray-release`

## 核心思路

本模块演示 [[Feature Flag]] 与 [[灰度发布]]：通过运行时配置控制功能是否开放，支持全局开关、白名单优先命中、稳定哈希百分比灰度，并在业务接口中根据 flag 选择新旧路径。

## 项目结构

```text
src/main/java/com/cloud/
├── controller/FeatureFlagController.java
├── service/
│   ├── FeatureFlagService.java       (配置更新、评估和业务示例)
│   └── FeatureFlagEvaluator.java     (命中规则计算)
├── repository/InMemoryFeatureFlagRepository.java
├── model/
│   ├── FeatureFlagConfig.java
│   ├── FeatureFlagUpdateRequest.java
│   ├── FeatureFlagEvaluation.java
│   └── CheckoutResponse.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## Feature Flag 配置模型

```java
public class FeatureFlagConfig {
    private String key;
    private boolean enabled;
    private int rolloutPercent;
    private Set<String> allowlist;
    private Instant updatedAt;
}
```

| 字段 | 含义 |
|------|------|
| `key` | 功能开关标识，例如 `new-checkout` |
| `enabled` | 全局是否启用 |
| `rolloutPercent` | 百分比灰度比例，范围 0-100 |
| `allowlist` | 白名单用户集合，优先于百分比灰度 |
| `updatedAt` | 更新时间 |

## 更新与校验

```java
public FeatureFlagConfig update(String key, FeatureFlagUpdateRequest request) {
    validateKey(key);
    if (request.getRolloutPercent() < 0 || request.getRolloutPercent() > 100) {
        throw new IllegalArgumentException("rolloutPercent 必须在 0 到 100 之间");
    }
    return repository.save(new FeatureFlagConfig(
            key,
            request.isEnabled(),
            request.getRolloutPercent(),
            request.getAllowlist() == null ? new LinkedHashSet<>() : new LinkedHashSet<>(request.getAllowlist()),
            Instant.now()
    ));
}
```

`rolloutPercent` 必须限制在 0 到 100，白名单为空时使用空集合，避免后续评估时空指针。

## 评估规则

```java
public FeatureFlagEvaluation evaluate(FeatureFlagConfig config, String userId) {
    int bucket = bucket(config.getKey(), userId);
    if (!config.isEnabled()) {
        return result(config, userId, false, "DISABLED", bucket);
    }
    if (config.getAllowlist().contains(userId)) {
        return result(config, userId, true, "ALLOWLIST", bucket);
    }
    if (config.getRolloutPercent() >= 100) {
        return result(config, userId, true, "FULL_ROLLOUT", bucket);
    }
    if (config.getRolloutPercent() <= 0) {
        return result(config, userId, false, "NOT_IN_ROLLOUT", bucket);
    }
    boolean enabled = bucket < config.getRolloutPercent();
    return result(config, userId, enabled, enabled ? "PERCENTAGE_ROLLOUT" : "NOT_IN_ROLLOUT", bucket);
}
```

优先级：

1. 全局关闭：直接不命中
2. 白名单：优先命中
3. 100%：全量命中
4. 0%：非白名单不命中
5. 百分比灰度：通过稳定 hash bucket 判断

## 稳定哈希分桶

```java
private int bucket(String key, String userId) {
    CRC32 crc32 = new CRC32();
    crc32.update((key + ":" + userId).getBytes(StandardCharsets.UTF_8));
    return (int) (crc32.getValue() % 100);
}
```

同一个 `key + userId` 会得到稳定 bucket，因此同一用户在灰度比例不变时不会一会儿进新版、一会儿回旧版。

> [!important] 灰度稳定性
> 百分比灰度必须使用稳定分桶，而不是每次随机。随机会导致用户体验抖动，也会让问题排查变困难。

## 业务接口选择新旧路径

```java
public CheckoutResponse checkout(String userId) {
    FeatureFlagEvaluation evaluation = evaluate("new-checkout", userId);
    return new CheckoutResponse(
            userId,
            evaluation.isEnabled() ? "NEW_CHECKOUT" : "LEGACY_CHECKOUT",
            evaluation.isEnabled(),
            evaluation.getReason(),
            evaluation.getBucket()
    );
}
```

业务接口不直接读取配置细节，只依赖评估结果选择新旧路径，并把命中原因和 bucket 返回，方便调试。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/flags` | 模块说明 |
| PUT | `/api/flags/{key}` | 更新 flag 配置 |
| GET | `/api/flags/{key}` | 查询 flag 配置 |
| GET | `/api/flags/{key}/evaluate?userId=1001` | 评估用户是否命中 |
| GET | `/api/flags/checkout?userId=1001` | 结账业务示例 |

## 调用验证

```bash
mvn -pl 35-SpringBoot-feature-flag-gray-release spring-boot:run

curl -X PUT "http://localhost:8115/api/flags/new-checkout" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"rolloutPercent":0,"allowlist":["1001"]}'

curl "http://localhost:8115/api/flags/new-checkout/evaluate?userId=1001"
curl "http://localhost:8115/api/flags/checkout?userId=2001"
```

## 要点总结

1. [[Feature Flag]] 让功能发布和代码部署解耦
2. 灰度发布应支持全局开关、白名单和百分比分桶
3. 白名单通常优先于百分比灰度，便于内部测试或定向开放
4. 稳定哈希保证同一用户命中结果一致
5. 业务响应中暴露 reason 和 bucket，有助于灰度排查
