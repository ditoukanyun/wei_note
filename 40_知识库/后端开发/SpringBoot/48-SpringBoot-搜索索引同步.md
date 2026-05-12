---
title: SpringBoot 搜索索引同步
date: 2026-05-11
tags:
  - springboot
  - java
  - 搜索
module: 48-SpringBoot-search-index-sync
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 搜索索引同步

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/48-SpringBoot-search-index-sync`

## 核心思路

本模块演示搜索索引同步和查询流程：把业务文档同步到内存索引，支持关键词检索、分类/状态过滤、排序和高亮式摘要。

## 能力点

- 文档 upsert
- 全量重建索引
- 关键词检索
- category/status 过滤
- 价格和相关度排序
- `<em>` 摘要片段

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 搜索索引同步 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/SearchIndexController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/SearchIndexController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/search")
public class SearchIndexController {

    private final SearchIndexService searchIndexService;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SearchIndexController(SearchIndexService searchIndexService) {
        this.searchIndexService = searchIndexService;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "48-SpringBoot-search-index-sync");
        data.put("desc", "搜索索引同步、关键词检索、过滤排序和结果摘要");
        data.put("apis", new String[]{
                "GET /api/search",
                "POST /api/search/documents",
                "POST /api/search/rebuild",
                "GET /api/search/query",
                "GET /api/search/stats"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/documents")
    public ApiResult<IndexStats> sync(@RequestBody IndexSyncRequest request) {
        return ApiResult.success(searchIndexService.sync(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/rebuild")
    public ApiResult<IndexStats> rebuild(@RequestBody IndexSyncRequest request) {
        return ApiResult.success(searchIndexService.rebuild(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/query")
    public ApiResult<SearchResponse> query(@RequestParam(required = false) String keyword,
                                           @RequestParam(required = false) String category,
                                           @RequestParam(required = false) String status,
                                           @RequestParam(required = false) String sort) {
        return ApiResult.success(searchIndexService.search(keyword, category, status, sort));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/stats")
    public ApiResult<IndexStats> stats() {
        return ApiResult.success(searchIndexService.stats());
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/SearchIndexService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/SearchIndexService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class SearchIndexService {

    private final SearchIndexRepository repository;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public SearchIndexService(SearchIndexRepository repository) {
        this.repository = repository;
    }

    public IndexStats sync(IndexSyncRequest request) {
        List<SearchDocument> documents = normalizedDocuments(request);
        repository.upsertAll(documents);
        return stats();
    }

    public IndexStats rebuild(IndexSyncRequest request) {
        List<SearchDocument> documents = normalizedDocuments(request);
        repository.rebuild(documents);
        return stats();
    }

    public SearchResponse search(String keyword, String category, String status, String sort) {
        String sortMode = sort == null || sort.isBlank() ? "scoreDesc" : sort;
        Comparator<SearchResultItem> comparator = comparator(sortMode);
        String normalizedKeyword = normalize(keyword);
        List<SearchResultItem> items = repository.findAll().stream()
                .filter(document -> matchesFilter(document.getCategory(), category))
                .filter(document -> matchesFilter(document.getStatus(), status))
                .map(document -> toResult(document, normalizedKeyword))
                .filter(item -> normalizedKeyword.isBlank() || item.getScore() > 0)
                .sorted(comparator)
                .toList();
        return new SearchResponse(items.size(), items);
    }

    public IndexStats stats() {
        List<SearchDocument> documents = repository.findAll();
        List<String> categories = documents.stream()
                .map(SearchDocument::getCategory)
                .filter(Objects::nonNull)
                .distinct()
                .sorted()
                .toList();
        return new IndexStats(documents.size(), categories, repository.getLastSyncAt());
    }

    private List<SearchDocument> normalizedDocuments(IndexSyncRequest request) {
        List<SearchDocument> documents = request == null ? List.of() : request.getDocuments();
        for (SearchDocument document : documents) {
            if (document.getDocumentId() == null || document.getDocumentId().isBlank()) {
                throw new IllegalArgumentException("documentId 不能为空");
            }
        }
        return documents;
    }

    private boolean matchesFilter(String actual, String expected) {
        return expected == null || expected.isBlank() || expected.equals(actual);
    }

    private SearchResultItem toResult(SearchDocument document, String keyword) {
        int score = score(document, keyword);
        return new SearchResultItem(
                document.getDocumentId(),
                value(document.getTitle()),
                value(document.getCategory()),
                value(document.getStatus()),
                document.getPrice() == null ? BigDecimal.ZERO : document.getPrice(),
                score,
                snippet(document.getContent(), keyword)
        );
    }

    private int score(SearchDocument document, String keyword) {
        if (keyword.isBlank()) {
            return 1;
        }
        int score = 0;
        if (normalize(document.getTitle()).contains(keyword)) {
            score += 3;
        }
        if (normalize(document.getContent()).contains(keyword)) {
            score += 1;
        }
        for (String tag : document.getTags()) {
            if (normalize(tag).contains(keyword)) {
                score += 1;
            }
        }
        return score;
    }

    private String snippet(String content, String keyword) {
        String safeContent = value(content);
        if (keyword.isBlank()) {
            return safeContent;
        }
        String lowerContent = safeContent.toLowerCase(Locale.ROOT);
        int index = lowerContent.indexOf(keyword);
        if (index < 0) {
            return safeContent;
        }
        String matched = safeContent.substring(index, index + keyword.length());
        return safeContent.substring(0, index) + "<em>" + matched + "</em>" + safeContent.substring(index + keyword.length());
    }
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/search/SearchIndexRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/search/SearchIndexRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class SearchIndexRepository {

    private final ConcurrentMap<String, SearchDocument> documents = new ConcurrentHashMap<>();
    private volatile Instant lastSyncAt;

    public void upsertAll(List<SearchDocument> newDocuments) {
        for (SearchDocument document : newDocuments) {
            documents.put(document.getDocumentId(), document);
        }
        lastSyncAt = Instant.now();
    }

    public void rebuild(List<SearchDocument> newDocuments) {
        documents.clear();
        upsertAll(newDocuments);
    }

    public List<SearchDocument> findAll() {
        return new ArrayList<>(documents.values());
    }

    public Instant getLastSyncAt() {
        return lastSyncAt;
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

1. SearchIndexController：接收 HTTP 请求并转换成 Java 方法调用
2. SearchIndexService：执行案例的核心业务规则
3. SearchIndexRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/search`：模块说明
- `POST /api/search/documents`：增量同步文档
- `POST /api/search/rebuild`：全量重建索引
- `GET /api/search/query`：搜索查询
- `GET /api/search/stats`：索引统计

## 调用验证

```bash
curl -X POST "http://localhost:8128/api/search/documents" \
  -H "Content-Type: application/json" \
  -d '{"documents":[{"documentId":"p1","title":"Spring Search","content":"Spring Boot search index sync","category":"guide","tags":["spring","search"],"status":"PUBLISHED","price":19.90,"updatedAt":"2026-04-30T00:00:00Z"}]}'
```

```bash
curl "http://localhost:8128/api/search/query?keyword=spring&category=guide&status=PUBLISHED"
```

## 生产映射

本模块使用内存索引模拟搜索引擎。生产环境通常映射为：

- `POST /documents`：业务变更事件消费后写入 ES/OpenSearch
- `POST /rebuild`：全量重建索引任务
- `GET /query`：映射为 bool query、filter、sort、highlight
- `GET /stats`：映射为索引文档数、分片状态、同步水位

## 生产差距

该示例用于隔离学习 搜索索引同步 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 48-SpringBoot-search-index-sync test
```

## 要点总结

1. 文档 upsert
2. 全量重建索引
3. 关键词检索
4. category/status 过滤
5. 价格和相关度排序

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
