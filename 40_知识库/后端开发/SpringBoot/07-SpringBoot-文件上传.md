---
title: SpringBoot 文件上传
date: 2026-04-20
tags:
  - springboot
  - java
  - 文件上传
module: 07-SpringBoot-file-upload
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

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/files/upload` | 单文件上传 |
| POST | `/api/files/uploads` | 多文件上传 |
| DELETE | `/api/files?relativePath=...` | 删除文件 |
| GET | `/uploads/**` | 静态资源访问 |

## 要点总结

1. **MultipartFile**：Spring 封装的上传文件对象，`transferTo()` 直接落盘
2. **日期分目录**：`yyyy/MM/dd` 避免单目录文件过多
3. **文件名策略**：时间戳 + UUID 防重名，保留原始扩展名
4. **扩展名白名单**：防止上传 .jsp/.exe 等危险文件
5. **路径穿越防护**：`normalize()` + `startsWith(rootPath)`
6. **静态资源映射**：`addResourceHandlers` 将 URL 映射到文件系统
