---
title: SpringBoot 文件上传
date: 2026-04-20
tags:
  - springboot
  - java
  - 文件上传
module: 07-SpringBoot-file-upload
area: [[后端开发]]
created: 2026-04-20
---
# SpringBoot 文件上传

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/07-SpringBoot-file-upload`

## 项目结构

```
07-SpringBoot-file-upload/
└── src/main/java/com/cloud/
    ├── config/WebConfig.java            # 静态资源映射
    ├── service/FileStorageService.java  # 文件存储核心
    ├── controller/FileUploadController.java
    ├── vo/FileInfoVO.java
    ├── common/ApiResult.java
    └── exception/GlobalExceptionHandler.java
```

## 配置

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB        # 单个文件最大
      max-request-size: 50MB     # 单次请求最大

file:
  upload-dir: uploads
  public-path: /uploads/
  max-size-bytes: 10485760
  allowed-extensions: jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,txt
```

| 配置 | 说明 |
|------|------|
| `max-file-size` | Spring 层：单文件大小限制 |
| `max-request-size` | Spring 层：请求总大小限制 |
| `max-size-bytes` | 业务层：自定义大小校验 |
| `allowed-extensions` | 业务层：白名单扩展名 |

## 静态资源映射 — WebConfig

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path absoluteUploadDir = Paths.get(uploadDir).toAbsolutePath().normalize();
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:" + absoluteUploadDir + "/");
    }
}
```

- URL `/uploads/**` → 映射到本地文件系统 `uploads/` 目录
- `file:` 前缀表示文件系统路径（非 classpath）

## 文件存储核心 — FileStorageService

### 存储路径设计

```
uploads/
└── 2026/04/20/                    # 按日期分目录
    └── 20260420150030_a1b2c3d4.jpg # 时间戳 + UUID + 扩展名
```

### 单文件上传

```java
public FileInfoVO store(MultipartFile file) {
    validateFile(file);                        // 校验

    String dateDir = LocalDate.now().format(DATE_DIR_FORMAT);   // yyyy/MM/dd
    String storedFilename = timestamp + "_" + uuid8 + "." + ext;
    Path targetFile = rootPath.resolve(dateDir).resolve(storedFilename);

    Files.createDirectories(targetDir);
    file.transferTo(targetFile);               // 落盘

    return FileInfoVO.builder()
            .originalFilename(originalFilename)
            .storedFilename(storedFilename)
            .relativePath(dateDir + "/" + storedFilename)
            .url(publicPath + relativePath)
            .size(file.getSize())
            .contentType(file.getContentType())
            .build();
}
```

### 文件校验

```java
private void validateFile(MultipartFile file) {
    if (file == null || file.isEmpty()) throw ...;          // 空文件
    if (file.getSize() > maxFileSize) throw ...;            // 大小超限
    if (!allowedExtensions.contains(extension)) throw ...;  // 扩展名白名单
}
```

### 安全删除 — 路径穿越防护

```java
public void delete(String relativePath) {
    Path targetFile = rootPath.resolve(relativePath).normalize();
    if (!targetFile.startsWith(rootPath)) {
        throw new IllegalArgumentException("文件路径不合法");  // 防 ../ 穿越
    }
    Files.delete(targetFile);
}
```

> [!important] 路径穿越攻击
> 恶意请求 `relativePath=../../../etc/passwd` 可删除系统文件。
> `normalize()` 解析 `..`，`startsWith(rootPath)` 确保不超出上传目录。

### 多文件上传

```java
public List<FileInfoVO> store(MultipartFile[] files) {
    return List.of(files).stream().map(this::store).toList();
}
```

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 文件上传 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/FileUploadController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/FileUploadController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/files")
public class FileUploadController {

    private final FileStorageService fileStorageService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public FileUploadController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> index() {
        Map<String, Object> apiList = new LinkedHashMap<>();
        apiList.put("module", "07-SpringBoot-file-upload");
        apiList.put("description", "演示 Spring Boot 单文件上传、多文件上传、静态访问和文件删除");
        apiList.put("apis", List.of(
                "GET /api/files",
                "POST /api/files/upload",
                "POST /api/files/uploads",
                "DELETE /api/files?relativePath=2026/04/09/demo.txt",
                "GET /uploads/**"
        ));
        return ApiResult.success(apiList);
    }

    // 单文件上传适合先理解 MultipartFile 的基本能力。
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/upload")
    public ApiResult<FileInfoVO> upload(@RequestParam("file") MultipartFile file) {
        return ApiResult.success(fileStorageService.store(file));
    }

    // 多文件上传本质上就是对文件数组逐个执行相同的校验与落盘逻辑。
    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/uploads")
    public ApiResult<List<FileInfoVO>> uploadBatch(@RequestParam("files") MultipartFile[] files) {
        return ApiResult.success(fileStorageService.store(files));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @DeleteMapping
    public ApiResult<Void> delete(@RequestParam String relativePath) {
        fileStorageService.delete(relativePath);
        return ApiResult.success();
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/FileStorageService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/FileStorageService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class FileStorageService {
    private static final DateTimeFormatter DATE_DIR_FORMAT = DateTimeFormatter.ofPattern("yyyy/MM/dd");
    private static final DateTimeFormatter FILE_NAME_TIME_FORMAT = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

    private final Path rootPath;
    private final String publicPath;
    private final List<String> allowedExtensions;
    private final long maxFileSize;

    @Autowired
    public FileStorageService(@Value("${file.upload-dir}") String uploadDir,
                              @Value("${file.public-path}") String publicPath,
                              @Value("${file.allowed-extensions}") String allowedExtensions,
                              @Value("${file.max-size-bytes:10485760}") long maxFileSize) {
        this(uploadDir, publicPath, parseAllowedExtensions(allowedExtensions), maxFileSize);
    }

    public FileStorageService(String uploadDir,
                              String publicPath,
                              List<String> allowedExtensions,
                              long maxFileSize) {
        this.rootPath = Paths.get(uploadDir).toAbsolutePath().normalize();
        this.publicPath = normalizePublicPath(publicPath);
        this.allowedExtensions = allowedExtensions.stream()
                .map(ext -> ext.toLowerCase(Locale.ROOT))
                .toList();
        this.maxFileSize = maxFileSize;
    }

    public FileInfoVO store(MultipartFile file) {
        validateFile(file);

        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        String extension = getExtension(originalFilename);
        String dateDir = LocalDate.now().format(DATE_DIR_FORMAT);
        String storedFilename = LocalDateTime.now().format(FILE_NAME_TIME_FORMAT) + "_"
                + UUID.randomUUID().toString().replace("-", "").substring(0, 8) + "." + extension;
        Path targetDir = rootPath.resolve(dateDir).normalize();
        Path targetFile = targetDir.resolve(storedFilename).normalize();

        try {
            Files.createDirectories(targetDir);
            file.transferTo(targetFile);
        } catch (IOException e) {
            throw new IllegalStateException("文件保存失败", e);
        }

        String relativePath = dateDir + "/" + storedFilename;
        return FileInfoVO.builder()
                .originalFilename(originalFilename)
                .storedFilename(storedFilename)
                .relativePath(relativePath)
                .url(publicPath + relativePath)
                .size(file.getSize())
                .contentType(file.getContentType())
                .build();
    }

    public List<FileInfoVO> store(MultipartFile[] files) {
        if (files == null || files.length == 0) {
            throw new IllegalArgumentException("上传文件不能为空");
        }
        return List.of(files).stream().map(this::store).toList();
    }

    public void delete(String relativePath) {
        if (!StringUtils.hasText(relativePath)) {
            throw new IllegalArgumentException("文件路径不能为空");
        }

        // 只允许删除上传根目录下的文件，避免通过 ../ 访问任意系统路径。
        Path targetFile = rootPath.resolve(relativePath).normalize();
        if (!targetFile.startsWith(rootPath)) {
            throw new IllegalArgumentException("文件路径不合法");
        }
        if (!Files.exists(targetFile) || Files.isDirectory(targetFile)) {
            throw new IllegalArgumentException("文件不存在");
        }

        try {
            Files.delete(targetFile);
        } catch (IOException e) {
            throw new IllegalStateException("文件删除失败", e);
        }
    }

    public Path getRootPath() {
        return rootPath;
    }

    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("上传文件不能为空");
        }
        if (!StringUtils.hasText(file.getOriginalFilename())) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        if (file.getSize() > maxFileSize) {
            throw new IllegalArgumentException("文件大小超出限制");
        }

        String extension = getExtension(file.getOriginalFilename());
        if (!allowedExtensions.contains(extension)) {
            throw new IllegalArgumentException("文件类型不支持");
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 配置类：Spring 如何注册基础设施

源码位置：`src/main/java/com/cloud/config/WebConfig.java`

配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。

```java
// 文件：com/cloud/config/WebConfig.java
// 学习重点：配置类负责把基础设施对象注册到 Spring 容器，后续请求或启动流程才会用到它们。
// @Configuration 表示这里会声明或注册 Spring 基础设施。
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path absoluteUploadDir = Paths.get(uploadDir).toAbsolutePath().normalize();
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:" + absoluteUploadDir + "/");
    }
}
```

关键点拆解：

- 配置类的重点不是业务规则，而是“把谁注册到容器、在什么条件下注册”。
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

    @ExceptionHandler(IllegalArgumentException.class)
    public ApiResult<Void> handleIllegalArgument(IllegalArgumentException e) {
        return ApiResult.fail(400, e.getMessage());
    }

    @ExceptionHandler(IllegalStateException.class)
    public ApiResult<Void> handleIllegalState(IllegalStateException e) {
        return ApiResult.fail(500, e.getMessage());
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ApiResult<Void> handleMaxUploadSizeExceeded(MaxUploadSizeExceededException e) {
        return ApiResult.fail(400, "上传文件超过大小限制");
    }

    @ExceptionHandler(Exception.class)
    public ApiResult<Void> handleException(Exception e) {
        return ApiResult.fail(500, e.getMessage());
    }
}
```

关键点拆解：

- 先看这个类暴露了哪些 public 方法，再看它依赖了哪些对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

## 运行时调用链

1. WebConfig：启动时注册配置、Bean 或扩展点
2. FileUploadController：接收 HTTP 请求并转换成 Java 方法调用
3. FileStorageService：执行案例的核心业务规则

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/files/upload` | 单文件上传 |
| POST | `/api/files/uploads` | 多文件上传 |
| DELETE | `/api/files?relativePath=...` | 删除文件 |
| GET | `/uploads/**` | 静态资源访问 |

## 生产差距

这个示例适合帮助初学者理解 文件上传 的核心机制，但生产项目不能只停留在“能跑通”。真实落地时至少要补齐：统一鉴权、参数边界校验、异常响应、结构化日志、监控指标、自动化测试、配置隔离和容量评估。

如果模块涉及数据库、缓存、消息、网关、认证或外部服务，还要进一步考虑连接池、超时、重试、幂等、事务边界、数据一致性和故障告警。学习时可以先记住主流程，再用这些生产差距反向检查自己是否真正理解了案例。

## 要点总结

1. **MultipartFile**：Spring 封装的上传文件对象，`transferTo()` 直接落盘
2. **日期分目录**：`yyyy/MM/dd` 避免单目录文件过多
3. **文件名策略**：时间戳 + UUID 防重名，保留原始扩展名
4. **扩展名白名单**：防止上传 .jsp/.exe 等危险文件
5. **路径穿越防护**：`normalize()` + `startsWith(rootPath)`
6. **静态资源映射**：`addResourceHandlers` 将 URL 映射到文件系统

## 实践流程

```mermaid
flowchart LR
  A[接收 MultipartFile] --> B[校验大小和类型]
  B --> C[生成安全文件名]
  C --> D[写入隔离目录或对象存储]
  D --> E[返回访问地址和元数据]
```

## 实践检查清单

- 是否限制文件大小、扩展名和 MIME 类型。
- 文件名是否重新生成，避免使用用户原始路径。
- 存储目录是否和应用代码目录隔离。
- 删除、下载和预览是否做权限校验。
- 是否记录上传人、文件大小、hash 和存储路径。

## 案例

用户上传头像时，服务端先校验图片类型和大小，再生成 UUID 文件名保存到日期目录，数据库只记录相对路径和元数据，访问时通过受控 URL 返回。

## 常见误区

- 只校验扩展名，不校验内容类型和大小。
- 使用原始文件名落盘，造成覆盖或路径风险。
- 上传目录可执行脚本，导致远程代码执行风险。
