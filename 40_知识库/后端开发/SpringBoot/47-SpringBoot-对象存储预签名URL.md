---
title: SpringBoot 对象存储预签名URL
date: 2026-05-11
tags:
  - springboot
  - java
  - 对象存储
module: 47-SpringBoot-object-storage-presigned-url
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 对象存储预签名URL

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/47-SpringBoot-object-storage-presigned-url`

## 核心思路

本模块演示对象存储的预签名上传/下载流程：服务端先生成带过期时间和约束条件的上传链接，客户端再使用 token 上传内容；下载时服务端生成带 HMAC 签名和过期时间的下载链接，读取时校验签名与有效期。

## 能力点

- 对象元数据管理
- 预签名上传 URL
- 上传 contentType 和 size 校验
- 预签名下载 URL
- HMAC SHA-256 签名校验
- 过期时间校验

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 对象存储预签名URL 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/ObjectStorageController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/ObjectStorageController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/storage")
public class ObjectStorageController {

    private final ObjectStorageService storageService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ObjectStorageController(ObjectStorageService storageService) {
        this.storageService = storageService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "47-SpringBoot-object-storage-presigned-url");
        data.put("desc", "对象存储元数据、预签名上传下载、过期时间与 HMAC 签名校验");
        data.put("apis", new String[]{
                "GET /api/storage",
                "POST /api/storage/upload-urls",
                "PUT /api/storage/uploads/{token}",
                "GET /api/storage/objects",
                "POST /api/storage/download-urls",
                "GET /api/storage/downloads/{bucket}/{objectKey}"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/upload-urls")
    public ApiResult<PresignedUploadUrl> createUploadUrl(@RequestBody CreateUploadUrlRequest request) {
        return ApiResult.success(storageService.createUploadUrl(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PutMapping("/uploads/{token}")
    public ApiResult<StoredObject> upload(@PathVariable String token, @RequestBody UploadPayload payload) {
        return ApiResult.success(storageService.upload(token, payload));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/objects")
    public ApiResult<List<StoredObject>> objects() {
        return ApiResult.success(storageService.listObjects());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/download-urls")
    public ApiResult<PresignedDownloadUrl> createDownloadUrl(@RequestBody CreateDownloadUrlRequest request) {
        return ApiResult.success(storageService.createDownloadUrl(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/downloads/{bucket}/{objectKey}")
    public ApiResult<StoredObject> download(@PathVariable String bucket,
                                            @PathVariable String objectKey,
                                            @RequestParam String expires,
                                            @RequestParam String signature) {
        return ApiResult.success(storageService.download(bucket, objectKey, parseExpires(expires), signature));
    }

    private long parseExpires(String expires) {
        try {
            return Long.parseLong(expires);
        } catch (NumberFormatException ignored) {
            return Instant.parse(expires).toEpochMilli();
        }
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/ObjectStorageService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/ObjectStorageService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class ObjectStorageService {

    private final ObjectStorageRepository repository;
    private final Clock clock;
    private final String secret;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public ObjectStorageService(ObjectStorageRepository repository) {
        this(repository, Clock.systemUTC(), "learn-springboot-storage-secret");
    }

    public ObjectStorageService(ObjectStorageRepository repository, Clock clock, String secret) {
        this.repository = repository;
        this.clock = clock;
        this.secret = secret;
    }

    public PresignedUploadUrl createUploadUrl(CreateUploadUrlRequest request) {
        validateUploadRequest(request);
        String token = UUID.randomUUID().toString();
        Instant expiresAt = clock.instant().plusSeconds(normalizeTtl(request.getTtlSeconds()));
        PresignedUploadUrl uploadUrl = new PresignedUploadUrl(
                token,
                "/api/storage/uploads/" + token,
                expiresAt,
                request.getBucket(),
                request.getObjectKey(),
                request.getContentType(),
                request.getSizeBytes()
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveUploadUrl(uploadUrl);
        return uploadUrl;
    }

    public StoredObject upload(String token, UploadPayload payload) {
        PresignedUploadUrl uploadUrl = repository.findUploadUrl(token)
                .orElseThrow(() -> new NoSuchElementException("预签名上传 token 不存在: " + token));
        if (!uploadUrl.getExpiresAt().isAfter(clock.instant())) {
            throw new IllegalArgumentException("预签名上传链接已过期");
        }
        if (payload == null || !uploadUrl.getContentType().equals(payload.getContentType())) {
            throw new IllegalArgumentException("上传 contentType 与预签名不一致");
        }
        String content = payload.getContent() == null ? "" : payload.getContent();
        long sizeBytes = content.getBytes(StandardCharsets.UTF_8).length;
        if (sizeBytes != uploadUrl.getSizeBytes()) {
            throw new IllegalArgumentException("上传大小与预签名不一致");
        }
        StoredObject object = new StoredObject(
                uploadUrl.getBucket(),
                uploadUrl.getObjectKey(),
                uploadUrl.getContentType(),
                sizeBytes,
                etag(content),
                content,
                clock.instant()
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveObject(object);
        return object;
    }

    public List<StoredObject> listObjects() {
        return repository.listObjects();
    }

    public PresignedDownloadUrl createDownloadUrl(CreateDownloadUrlRequest request) {
        validateDownloadRequest(request);
        findObjectOrThrow(request.getBucket(), request.getObjectKey());
        Instant expiresAt = clock.instant().plusSeconds(normalizeTtl(request.getTtlSeconds()));
        long expiresMillis = expiresAt.toEpochMilli();
        String signature = sign(request.getBucket(), request.getObjectKey(), expiresMillis);
        String downloadUrl = "/api/storage/downloads/" + request.getBucket() + "/" + request.getObjectKey()
                + "?expires=" + expiresMillis + "&signature=" + signature;
        return new PresignedDownloadUrl(downloadUrl, expiresAt, request.getBucket(), request.getObjectKey(), signature);
    }

    public StoredObject download(String bucket, String objectKey, long expiresMillis, String signature) {
        if (Instant.ofEpochMilli(expiresMillis).isBefore(clock.instant())) {
            throw new IllegalArgumentException("预签名下载链接已过期");
        }
        String expected = sign(bucket, objectKey, expiresMillis);
        if (!expected.equals(signature)) {
            throw new IllegalArgumentException("下载签名无效");
        }
        return findObjectOrThrow(bucket, objectKey);
    }

    private StoredObject findObjectOrThrow(String bucket, String objectKey) {
        return repository.findObject(bucket, objectKey)
                .orElseThrow(() -> new NoSuchElementException("对象不存在: " + bucket + "/" + objectKey));
    }

    private void validateUploadRequest(CreateUploadUrlRequest request) {
        if (request == null || isBlank(request.getBucket())) {
            throw new IllegalArgumentException("bucket 不能为空");
        }
        if (isBlank(request.getObjectKey())) {
            throw new IllegalArgumentException("objectKey 不能为空");
        }
        if (isBlank(request.getContentType())) {
            throw new IllegalArgumentException("contentType 不能为空");
        }
        if (request.getSizeBytes() <= 0) {
            throw new IllegalArgumentException("sizeBytes 必须大于 0");
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/storage/ObjectStorageRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/storage/ObjectStorageRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class ObjectStorageRepository {

    private final ConcurrentMap<String, PresignedUploadUrl> uploadUrls = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, StoredObject> objects = new ConcurrentHashMap<>();

    public void saveUploadUrl(PresignedUploadUrl uploadUrl) {
        uploadUrls.put(uploadUrl.getUploadToken(), uploadUrl);
    }

    public Optional<PresignedUploadUrl> findUploadUrl(String uploadToken) {
        return Optional.ofNullable(uploadUrls.get(uploadToken));
    }

    public void saveObject(StoredObject object) {
        objects.put(objectId(object.getBucket(), object.getObjectKey()), object);
    }

    public Optional<StoredObject> findObject(String bucket, String objectKey) {
        return Optional.ofNullable(objects.get(objectId(bucket, objectKey)));
    }

    public List<StoredObject> listObjects() {
        return new ArrayList<>(objects.values());
    }

    private String objectId(String bucket, String objectKey) {
        return bucket + "/" + objectKey;
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

    @ExceptionHandler(NoSuchElementException.class)
    public ResponseEntity<ApiResult<Void>> handleNotFound(NoSuchElementException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResult.fail(404, exception.getMessage()));
    }

    @ExceptionHandler({IllegalArgumentException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiResult<Void>> handleBadRequest(Exception exception) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResult.fail(400, exception.getMessage()));
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. ObjectStorageController：接收 HTTP 请求并转换成 Java 方法调用
2. ObjectStorageService：执行案例的核心业务规则
3. ObjectStorageRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/storage`：模块说明
- `POST /api/storage/upload-urls`：创建预签名上传 URL
- `PUT /api/storage/uploads/{token}`：使用 token 上传内容
- `GET /api/storage/objects`：查询对象列表
- `POST /api/storage/download-urls`：创建预签名下载 URL
- `GET /api/storage/downloads/{bucket}/{objectKey}`：带签名下载对象

## 调用验证

创建上传 URL：

```bash
curl -X POST "http://localhost:8127/api/storage/upload-urls" \
  -H "Content-Type: application/json" \
  -d '{"bucket":"docs","objectKey":"invoice-1.txt","contentType":"text/plain","sizeBytes":5,"ttlSeconds":60}'
```

使用返回的 `uploadToken` 上传：

```bash
curl -X PUT "http://localhost:8127/api/storage/uploads/{uploadToken}" \
  -H "Content-Type: application/json" \
  -d '{"contentType":"text/plain","content":"hello"}'
```

## 生产映射

本模块使用内存仓储模拟 MinIO/S3：

- 上传签名：生产可替换为 S3/MinIO SDK 的 presigned PUT URL
- 下载签名：生产可替换为 S3/MinIO SDK 的 presigned GET URL
- 元数据：生产可存数据库或对象存储 metadata
- 内容：生产由对象存储保存，本模块为了学习和测试保存在内存中

## 生产差距

该示例用于隔离学习 对象存储预签名URL 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 47-SpringBoot-object-storage-presigned-url test
```

## 要点总结

1. 对象元数据管理
2. 预签名上传 URL
3. 上传 contentType 和 size 校验
4. 预签名下载 URL
5. HMAC SHA-256 签名校验

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
