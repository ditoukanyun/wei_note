---
title: SpringBoot API 版本管理
date: 2026-04-20
tags:
  - springboot
  - java
  - api版本
  - 灰度发布
  - 兼容性
module: 22-SpringBoot-api-versioning
---
# SpringBoot API 版本管理

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/22-SpringBoot-api-versioning`

## 核心思路

实现 API 多版本共存与灰度演进：URL 路径版本（`/v1`、`/v2`）、请求头版本（`X-API-Version`）、客户端标签路由（`X-Client-Tag`）、灰度百分比分流四种版本路由策略。

## 项目结构

```
src/main/java/com/cloud/
├── controller/ApiVersioningController.java
├── service/
│   ├── ApiVersionRoutingService.java     (版本路由)
│   ├── InMemoryUserProfileService.java   (用户数据)
│   └── UserViewAssembler.java            (视图组装)
├── model/UserProfile.java
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 依赖与配置

| 依赖 | 说明 |
|------|------|
| `spring-boot-starter-web` | Web 框架 |

```yaml
server:
  port: 8102

demo:
  api:
    gray-v2-percent: 20         # 灰度比例 0-100
    v1-sunset-date: 2026-12-31  # v1 废弃日期
```

## 核心代码解析

### ApiVersionRoutingService — 版本路由核心

```java
public String resolveVersion(String explicitVersion, String clientTag, String userId) {
    // 1. 显式版本（X-API-Version Header）
    String normalizedVersion = normalizeVersion(explicitVersion);
    if (normalizedVersion != null) return normalizedVersion;

    // 2. 客户端标签（beta → v2）
    if ("beta".equalsIgnoreCase(trimToNull(clientTag))) return "v2";

    // 3. 灰度百分比（userId hashCode 取模）
    int bucket = Math.floorMod(userId.hashCode(), 100);
    return bucket < grayV2Percent ? "v2" : "v1";
}
```

> [!important] 灰度分桶一致性
> `userId.hashCode() % 100` 保证同一用户始终路由到同一版本，避免用户看到版本闪烁。

### UserViewAssembler — 视图组装

```java
// v1：只返回基础字段
public Map<String, Object> toV1(UserProfile profile) {
    return Map.of("apiVersion", "v1", "userId", ..., "nickname", ...);
}

// v2：返回完整字段
public Map<String, Object> toV2(UserProfile profile) {
    return Map.of("apiVersion", "v2", "userId", ..., "nickname", ...,
        "membershipLevel", ..., "city", ..., "riskTags", ...);
}
```

### ApiVersioningController — 版本路由接口

```java
// URL 路径版本
@GetMapping("/v1/users/{userId}")
@GetMapping("/v2/users/{userId}")

// 兼容路由（自动版本解析）
@GetMapping("/users/{userId}")
public ApiResult<Map<String, Object>> getCompatibleUser(
        @PathVariable String userId,
        @RequestHeader(value = "X-API-Version", required = false) String explicitVersion,
        @RequestHeader(value = "X-Client-Tag", required = false) String clientTag) {
    String version = routingService.resolveVersion(explicitVersion, clientTag, userId);
    // 根据 version 选择 toV1 或 toV2
}

// v1 废弃标记
private void markV1Deprecated(HttpServletResponse response) {
    response.setHeader("Deprecation", "true");
    response.setHeader("Sunset", v1SunsetDate);
}
```

> [!tip] Deprecation + Sunset Header
> HTTP 标准草案定义：`Deprecation: true` 表示接口已废弃，`Sunset` 表示废弃日期，客户端可据此提前迁移。

## 版本路由策略

```mermaid
flowchart TD
    A[请求到达 /users/{userId}] --> B{X-API-Version Header?}
    B -->|有| C[使用显式版本]
    B -->|无| D{X-Client-Tag = beta?}
    D -->|是| E[路由到 v2]
    D -->|否| F{灰度百分比}
    F -->|userId % 100 < grayPercent| G[路由到 v2]
    F -->|其他| H[路由到 v1]

    C --> I{v1 / v2?}
    I -->|v1| J[toV1 + Deprecation Header]
    I -->|v2| K[toV2]

    style J fill:#ffd43b
    style K fill:#51cf66,color:#fff
```

### 路由优先级

| 优先级 | 策略 | 请求头 | 说明 |
|--------|------|--------|------|
| 1 | 显式版本 | `X-API-Version` | 客户端指定，最高优先 |
| 2 | 客户端标签 | `X-Client-Tag: beta` | beta 用户走 v2 |
| 3 | 灰度百分比 | 无 | userId 取模分流 |

## API 接口

| 方法 | 路径 | 版本 | 说明 |
|------|------|------|------|
| GET | `/api/versioning` | - | 模块信息 |
| GET | `/api/versioning/resolve` | - | 解析版本路由决策 |
| GET | `/api/v1/users/{userId}` | v1 | 用户信息 v1（已废弃） |
| GET | `/api/v2/users/{userId}` | v2 | 用户信息 v2 |
| GET | `/api/users/{userId}` | 自动 | 兼容路由 |

## API 版本管理方案对比

| 方案 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **URL 路径** | `/v1/users` | 直观、易缓存 | URL 膨胀 |
| 请求头 | `X-API-Version: v2` | URL 不变 | 不直观、需文档 |
| Content Negotiation | `Accept: application/vnd.api.v2+json` | RESTful | 复杂 |
| 参数 | `?version=2` | 简单 | 不规范 |

## 要点总结

1. **URL 路径版本**：最常见、最直观，`/v1` 和 `/v2` 可同时存在
2. **灰度发布**：userId 取模保证一致性，灰度比例可动态调整（0→100% 即全量）
3. **Deprecation / Sunset Header**：标准化废弃通知，客户端可自动检测
4. **UserViewAssembler**：同一数据模型，不同版本输出不同字段，向后兼容
5. **路由优先级**：显式版本 > 客户端标签 > 灰度百分比，层次清晰
