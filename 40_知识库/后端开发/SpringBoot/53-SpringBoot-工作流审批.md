---
title: SpringBoot 工作流审批
date: 2026-05-11
tags:
  - springboot
  - java
  - 工作流
module: 53-SpringBoot-workflow-approval
area: [[后端开发]]
created: 2026-05-11
---
# SpringBoot 工作流审批

> 源码：`/Users/chenwei/Documents/code/java/learn-springboot/53-SpringBoot-workflow-approval`

## 核心思路

本模块演示顺序审批流原型：定义审批步骤，提交审批实例，按当前处理人逐级通过或驳回，并保留审计时间线。

## 能力点

- 审批流定义
- 有序审批步骤
- 审批实例提交
- 当前处理人
- 通过/驳回
- 终态控制
- 审计时间线

## 初学者学习路线

- 先把这个案例当成“最小可运行样例”，目标是理解 SpringBoot 工作流审批 的主流程。
- 先运行 README 里的启动命令和 curl，再带着现象回到代码里找入口。
- 每读一个类都问三件事：它由谁调用、它依赖谁、它改变了什么状态。

## 代码导读

下面的代码片段来自案例源码，并额外补了中文教学注释。阅读时先看注释理解职责，再回到完整源码核对细节。

### 接口入口：Controller 如何接收请求

源码位置：`src/main/java/com/cloud/controller/WorkflowApprovalController.java`

Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。

```java
// 文件：com/cloud/controller/WorkflowApprovalController.java
// 学习重点：Controller 是 HTTP 世界和 Java 代码世界之间的边界：路径、请求参数、返回值都在这里集中出现。
// @RestController 表示这个类的返回值会直接写到 HTTP 响应体里，常用于 JSON API。
@RestController
// 类级别路径是这一组接口的共同前缀。
@RequestMapping("/api/workflows")
public class WorkflowApprovalController {

    private final WorkflowApprovalService service;

    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WorkflowApprovalController(WorkflowApprovalService service) {
        this.service = service;
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping
    public ApiResult<Map<String, Object>> moduleInfo() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("module", "53-SpringBoot-workflow-approval");
        data.put("desc", "顺序审批流定义、实例提交、通过/驳回、当前处理人和审计时间线");
        data.put("apis", new String[]{
                "GET /api/workflows",
                "POST /api/workflows/definitions",
                "GET /api/workflows/definitions",
                "POST /api/workflows/instances",
                "GET /api/workflows/instances",
                "GET /api/workflows/instances/{instanceId}",
                "POST /api/workflows/instances/{instanceId}/approve",
                "POST /api/workflows/instances/{instanceId}/reject"
        });
        return ApiResult.success(data);
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/definitions")
    public ApiResult<WorkflowDefinition> createDefinition(@RequestBody CreateWorkflowDefinitionRequest request) {
        return ApiResult.success(service.createDefinition(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/definitions")
    public ApiResult<List<WorkflowDefinition>> definitions() {
        return ApiResult.success(service.definitions());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/instances")
    public ApiResult<ApprovalInstance> start(@RequestBody StartApprovalRequest request) {
        return ApiResult.success(service.start(request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/instances")
    public ApiResult<List<ApprovalInstance>> instances() {
        return ApiResult.success(service.instances());
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @GetMapping("/instances/{instanceId}")
    public ApiResult<ApprovalInstance> instance(@PathVariable String instanceId) {
        return ApiResult.success(service.findInstance(instanceId));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/instances/{instanceId}/approve")
    public ApiResult<ApprovalInstance> approve(@PathVariable String instanceId, @RequestBody ApprovalActionRequest request) {
        return ApiResult.success(service.approve(instanceId, request));
    }

    // 方法级别映射说明具体 HTTP 动词和子路径。
    @PostMapping("/instances/{instanceId}/reject")
    public ApiResult<ApprovalInstance> reject(@PathVariable String instanceId, @RequestBody ApprovalActionRequest request) {
        return ApiResult.success(service.reject(instanceId, request));
    }
}
```

关键点拆解：

- 先把 README 里的 curl 路径和这里的 `@RequestMapping` / `@GetMapping` / `@PostMapping` 对上。
- Controller 不应该堆复杂业务逻辑；看到它调用 Service，就说明职责分层是清楚的。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 业务核心：Service 如何组织规则

源码位置：`src/main/java/com/cloud/service/WorkflowApprovalService.java`

Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。

```java
// 文件：com/cloud/service/WorkflowApprovalService.java
// 学习重点：Service 承载业务规则，初学者要重点看它如何校验输入、调用依赖、返回结果。
// @Service 表示这是业务层 Bean，会被 Spring 自动扫描并注入。
@Service
public class WorkflowApprovalService {

    private final WorkflowRepository repository;
    private final Clock clock;

    @Autowired
    // 构造器注入：依赖从 Spring 容器传入，代码更容易测试，也避免隐藏依赖。
    public WorkflowApprovalService(WorkflowRepository repository) {
        this(repository, Clock.systemUTC());
    }

    public WorkflowApprovalService(WorkflowRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public WorkflowDefinition createDefinition(CreateWorkflowDefinitionRequest request) {
        validateDefinition(request);
        List<ApprovalStep> sortedSteps = request.getSteps().stream()
                .sorted(Comparator.comparingInt(ApprovalStep::getStepOrder))
                .toList();
        WorkflowDefinition definition = new WorkflowDefinition(
                UUID.randomUUID().toString(),
                request.getName(),
                request.isEnabled(),
                sortedSteps,
                clock.instant()
        );
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveDefinition(definition);
        return definition;
    }

    public List<WorkflowDefinition> definitions() {
        return repository.definitions().stream()
                .sorted(Comparator.comparing(WorkflowDefinition::getCreatedAt))
                .toList();
    }

    public ApprovalInstance start(StartApprovalRequest request) {
        validateStart(request);
        WorkflowDefinition definition = findDefinition(request.getDefinitionId());
        if (!definition.isEnabled()) {
            throw new IllegalArgumentException("审批流未启用");
        }
        ApprovalStep firstStep = definition.getSteps().get(0);
        ApprovalInstance instance = new ApprovalInstance(
                UUID.randomUUID().toString(),
                definition.getDefinitionId(),
                request.getBusinessKey(),
                request.getApplicant(),
                request.getTitle(),
                ApprovalStatus.PENDING,
                firstStep.getStepId(),
                firstStep.getAssignee(),
                new ArrayList<>(),
                clock.instant(),
                null
        );
        instance.getTimeline().add(new ApprovalAction("SUBMIT", request.getApplicant(), request.getTitle(), null, clock.instant()));
        // save 表示状态发生变化，学习时要追踪保存前做了哪些校验。
        repository.saveInstance(instance);
        return instance;
    }

    public ApprovalInstance approve(String instanceId, ApprovalActionRequest request) {
        ApprovalInstance instance = findInstance(instanceId);
        validateAction(instance, request);
        instance.getTimeline().add(new ApprovalAction("APPROVE", request.getActor(), request.getComment(), instance.getCurrentStepId(), clock.instant()));

        WorkflowDefinition definition = findDefinition(instance.getDefinitionId());
        int currentIndex = indexOfCurrentStep(definition, instance);
        if (currentIndex == definition.getSteps().size() - 1) {
            instance.setStatus(ApprovalStatus.APPROVED);
            instance.setCurrentStepId(null);
            instance.setCurrentAssignee(null);
            instance.setEndedAt(clock.instant());
            return instance;
        }

        ApprovalStep nextStep = definition.getSteps().get(currentIndex + 1);
        instance.setCurrentStepId(nextStep.getStepId());
        instance.setCurrentAssignee(nextStep.getAssignee());
        return instance;
    }

    public ApprovalInstance reject(String instanceId, ApprovalActionRequest request) {
        ApprovalInstance instance = findInstance(instanceId);
        validateAction(instance, request);
        instance.getTimeline().add(new ApprovalAction("REJECT", request.getActor(), request.getComment(), instance.getCurrentStepId(), clock.instant()));
        instance.setStatus(ApprovalStatus.REJECTED);
        instance.setCurrentStepId(null);
        instance.setCurrentAssignee(null);
        instance.setEndedAt(clock.instant());
        return instance;
    }

    public ApprovalInstance findInstance(String instanceId) {
        return repository.findInstance(instanceId)
                .orElseThrow(() -> new NoSuchElementException("审批实例不存在: " + instanceId));
    }

    public List<ApprovalInstance> instances() {
        return repository.instances().stream()
                .sorted(Comparator.comparing(ApprovalInstance::getCreatedAt))
                .toList();
    }
    // ... 省略其余辅助代码，完整实现以源码为准。
}
```

关键点拆解：

- Service 的 public 方法通常就是一个用例，例如创建、查询、刷新、投递、同步。
- 先看输入校验，再看调用了哪些依赖，最后看返回对象。
- 读完代码后，回到“生产差距”检查：安全、异常、监控、容量、测试是否都补齐。

### 数据访问：示例如何保存和查询数据

源码位置：`src/main/java/com/cloud/workflow/WorkflowRepository.java`

Repository 隐藏存储细节，让 Service 不必关心数据怎么存。

```java
// 文件：com/cloud/workflow/WorkflowRepository.java
// 学习重点：Repository 隐藏存储细节，让 Service 不必关心数据怎么存。
// @Repository 表示数据访问层 Bean，真实项目通常连接数据库或外部存储。
@Repository
public class WorkflowRepository {

    private final Map<String, WorkflowDefinition> definitions = new LinkedHashMap<>();
    private final Map<String, ApprovalInstance> instances = new LinkedHashMap<>();

    public void saveDefinition(WorkflowDefinition definition) {
        definitions.put(definition.getDefinitionId(), definition);
    }

    public Optional<WorkflowDefinition> findDefinition(String definitionId) {
        return Optional.ofNullable(definitions.get(definitionId));
    }

    public List<WorkflowDefinition> definitions() {
        return new ArrayList<>(definitions.values());
    }

    public void saveInstance(ApprovalInstance instance) {
        instances.put(instance.getInstanceId(), instance);
    }

    public Optional<ApprovalInstance> findInstance(String instanceId) {
        return Optional.ofNullable(instances.get(instanceId));
    }

    public List<ApprovalInstance> instances() {
        return new ArrayList<>(instances.values());
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

1. WorkflowApprovalController：接收 HTTP 请求并转换成 Java 方法调用
2. WorkflowApprovalService：执行案例的核心业务规则
3. WorkflowRepository：保存或查询示例数据

## 初学者常见误区

- 只把接口跑通，却没有回到代码理解 Controller、Service、Repository 的分工。
- 把内存 Map、模拟客户端、固定配置当成生产实现。
- 只看 happy path，忽略参数错误、外部系统失败、并发和重复请求。

## API 接口

- `GET /api/workflows`：模块说明
- `POST /api/workflows/definitions`：创建审批流定义
- `GET /api/workflows/definitions`：查询审批流定义
- `POST /api/workflows/instances`：提交审批实例
- `GET /api/workflows/instances`：查询审批实例
- `GET /api/workflows/instances/{instanceId}`：查询单个审批实例
- `POST /api/workflows/instances/{instanceId}/approve`：通过当前步骤
- `POST /api/workflows/instances/{instanceId}/reject`：驳回当前步骤

## 调用验证

创建审批流：

```bash
curl -X POST "http://localhost:8133/api/workflows/definitions" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"expense-approval",
    "enabled":true,
    "steps":[
      {"stepId":"manager","name":"Manager approval","assignee":"alice","stepOrder":1},
      {"stepId":"finance","name":"Finance approval","assignee":"bob","stepOrder":2}
    ]
  }'
```

提交审批：

```bash
curl -X POST "http://localhost:8133/api/workflows/instances" \
  -H "Content-Type: application/json" \
  -d '{"definitionId":"{definitionId}","businessKey":"EXP-1001","applicant":"chenwei","title":"expense 1001"}'
```

通过当前步骤：

```bash
curl -X POST "http://localhost:8133/api/workflows/instances/{instanceId}/approve" \
  -H "Content-Type: application/json" \
  -d '{"actor":"alice","comment":"manager ok"}'
```

驳回当前步骤：

```bash
curl -X POST "http://localhost:8133/api/workflows/instances/{instanceId}/reject" \
  -H "Content-Type: application/json" \
  -d '{"actor":"alice","comment":"missing invoice"}'
```

## 生产映射

本模块使用内存仓储和顺序状态机。生产环境通常替换为：

- 流程引擎：Flowable、Activiti、Camunda
- 数据存储：流程定义表、实例表、任务表、审批日志表
- 身份体系：用户、角色、部门、岗位、代理人
- 任务中心：待办、已办、抄送、催办
- 表单：业务单据表 + 表单快照
- 通知：审批节点变化触发消息中心

## 生产差距

该示例用于隔离学习 工作流审批 的核心机制，生产落地时还需要补齐鉴权、异常路径、监控指标、审计日志、容量边界和自动化测试。若涉及外部系统，还应明确超时、重试、幂等、回滚和告警策略。

## 测试

```bash
mvn -pl 53-SpringBoot-workflow-approval test
```

## 要点总结

1. 审批流定义
2. 有序审批步骤
3. 审批实例提交
4. 当前处理人
5. 通过/驳回

## 复盘问题

- 这个模块解决的核心问题是什么？
- 示例实现中哪些部分只是教学简化？
- 如果放到真实项目，需要补哪些监控、权限、容量和异常处理？
- 它和 [[SpringBoot MOC]] 中哪些主题可以互相链接？
