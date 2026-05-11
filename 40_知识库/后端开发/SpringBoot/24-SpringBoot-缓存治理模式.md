---
title: SpringBoot 缓存治理模式
date: 2026-04-28
tags:
  - springboot
  - java
  - redis
  - 缓存
  - 高并发
module: 24-SpringBoot-cache-patterns
area: [[后端开发]]
created: 2026-04-28
---
# SpringBoot 缓存治理模式

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/24-SpringBoot-cache-patterns`

## 核心思路

本模块演示缓存治理中的四类典型问题：[[缓存穿透]]、[[缓存击穿]]、[[缓存雪崩]]、[[热点 Key]]。示例用内存 Map 模拟缓存，但治理模式同样适用于 [[Redis]]。

## 项目结构

```text
src/main/java/com/cloud/
├── controller/CachePatternsController.java
├── service/
│   ├── CachePatternsService.java     (缓存治理核心)
│   └── InMemoryProductStore.java     (模拟数据库)
├── model/
│   ├── Product.java
│   ├── CachedProduct.java            (缓存包装对象)
│   └── CacheMetrics.java             (缓存指标)
├── common/ApiResult.java
└── exception/GlobalExceptionHandler.java
```

## 四类缓存问题

| 问题 | 现象 | 本模块方案 |
|------|------|------------|
| [[缓存穿透]] | 查询不存在数据，缓存永远 miss，请求持续打到数据库 | 存在性判断 + 空值缓存 |
| [[缓存击穿]] | 热点 key 过期瞬间，大量请求同时重建缓存 | 互斥锁 + 双重检查 |
| [[缓存雪崩]] | 大量 key 同时过期，数据库压力陡增 | TTL 抖动 |
| [[热点 Key]] | 单个高频 key 访问量极大，重建成本高 | 逻辑过期 + 异步刷新 |

## 关键配置

```yaml
demo:
  cache:
    base-ttl-seconds: 30
    ttl-jitter-seconds: 10
    null-ttl-seconds: 10
    hot-logical-expire-seconds: 30
    lock-wait-ms: 50
```

| 配置 | 说明 |
|------|------|
| `base-ttl-seconds` | 普通缓存基础 TTL |
| `ttl-jitter-seconds` | TTL 随机抖动秒数 |
| `null-ttl-seconds` | 空值缓存 TTL |
| `hot-logical-expire-seconds` | 热点 key 逻辑过期时间 |
| `lock-wait-ms` | 缓存重建锁等待时间 |

## 核心代码解析

### 普通查询：缓存穿透 + 击穿防护

```java
public Optional<Product> getProduct(Long id) {
    CacheReadResult cached = readCache(id, now, true);
    if (cached.hit()) {
        return cached.product();
    }

    metrics.incCacheMiss();
    if (!productStore.exists(id)) {
        cacheNullValue(id, now);
        return Optional.empty();
    }
    return loadWithMutex(id, false);
}
```

查询不存在商品时写入短 TTL 的空值缓存，避免同一个不存在 ID 反复打到数据库。

### 互斥重建：防止缓存击穿

```java
ReentrantLock lock = rebuildLocks.computeIfAbsent(id, key -> new ReentrantLock());
if (!lock.tryLock()) {
    metrics.incBreakdownLockWait();
    sleepSafely(lockWaitMs);
    CacheReadResult retryRead = readCache(id, System.currentTimeMillis(), true);
    if (retryRead.hit()) {
        return retryRead.product();
    }
    lock.lock();
}
```

> [!important] 双重检查
> 线程拿锁后再次读缓存，避免前一个线程已经完成重建后，后续线程重复查询数据库。

### TTL 抖动：缓解缓存雪崩

```java
private static long withJitter(long base, long jitter) {
    long random = ThreadLocalRandom.current().nextLong(jitter + 1);
    return Math.max(1, base + random);
}
```

普通缓存过期时间不是固定值，而是 `base + random(0, jitter)`，让 key 的过期点分散开。

### 热点 Key：逻辑过期 + 异步刷新

```java
if (cached.isLogicalExpired(now)) {
    triggerHotRefresh(id);
}
return Optional.of(cached.getProduct());
```

热点 key 逻辑过期后，当前请求仍返回旧值，同时触发后台线程刷新缓存。这是 [[Stale-While-Revalidate]] 思路。

```java
private void triggerHotRefresh(Long id) {
    if (!hotRefreshInProgress.add(id)) {
        return;
    }
    refreshExecutor.submit(() -> {
        try {
            Optional<Product> refreshed = loadFromStore(id);
            if (refreshed.isPresent()) {
                cacheHotValue(id, refreshed.get(), now);
            }
        } finally {
            hotRefreshInProgress.remove(id);
        }
    });
}
```

`hotRefreshInProgress` 保证同一热点 key 同一时间只有一个刷新任务。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cache-patterns` | 模块信息 |
| GET | `/api/cache-patterns/product/{id}` | 普通缓存查询 |
| GET | `/api/cache-patterns/hot/{id}` | 热点 key 查询 |
| POST | `/api/cache-patterns/hot/{id}/mark` | 标记热点 key |
| DELETE | `/api/cache-patterns/cache` | 清空缓存 |
| GET | `/api/cache-patterns/metrics` | 查看缓存指标 |

## 调用验证

```bash
mvn -pl 24-SpringBoot-cache-patterns spring-boot:run

curl "http://localhost:8104/api/cache-patterns/product/1"
curl "http://localhost:8104/api/cache-patterns/product/99999"
curl -X POST "http://localhost:8104/api/cache-patterns/hot/2/mark"
curl "http://localhost:8104/api/cache-patterns/hot/2"
curl "http://localhost:8104/api/cache-patterns/metrics"
```

## 要点总结

1. [[缓存穿透]] 用空值缓存或布隆过滤器降低无效查询压力
2. [[缓存击穿]] 用互斥锁让同一个 key 只有一个线程重建缓存
3. [[缓存雪崩]] 用 TTL 抖动让大量 key 的过期时间分散
4. [[热点 Key]] 用逻辑过期和异步刷新优先保证读请求稳定
5. 空值缓存 TTL 要短，避免数据库刚写入新数据后长时间读不到

## 实践流程

```mermaid
flowchart LR
  A[识别缓存风险] --> B[选择空值、互斥锁或 TTL 抖动]
  B --> C[实现缓存读写]
  C --> D[记录命中率和重建次数]
  D --> E[压测和复盘]
```

## 实践检查清单

- 是否区分穿透、击穿、雪崩和热点 Key。
- 空值缓存是否设置短 TTL。
- 缓存重建是否有互斥和超时保护。
- 热点 Key 是否支持逻辑过期和异步刷新。
- 是否监控命中率、重建耗时和下游数据库压力。

## 案例

商品详情页遇到热点商品时，可以返回逻辑未过期的旧缓存，同时后台异步刷新。用户看到的是稍旧但可用的数据，数据库也不会被瞬时流量击穿。

## 常见误区

- 所有 Key 使用相同 TTL，导致集中失效。
- 缓存未命中时所有请求同时查数据库。
- 空值缓存 TTL 太长，新数据写入后仍长期查不到。
