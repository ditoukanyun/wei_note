---
type: learning-path
topic: Java
level: beginner-to-advanced
created: 2025-02-26
status: in-progress
---

# Java 学习路线

## 第一阶段：Java 基础（1-2 个月）

### 1. 环境搭建
- [[JDK 安装与配置]] - JDK 版本选择、环境变量设置
- [[IDE 选择]] - IntelliJ IDEA / Eclipse / VS Code
- [[第一个 Java 程序]] - Hello World 与编译运行

### 2. 核心语法
- [[Java 数据类型]] - 基本类型 vs 引用类型
- [[变量与常量]] - 作用域、命名规范
- [[运算符]] - 算术、逻辑、位运算
- [[控制流程]] - if/else、switch、循环结构
- [[数组]] - 一维、多维数组操作

### 3. 面向对象基础
- [[类与对象]] - 定义、实例化、内存模型
- [[封装]] - private/public、getter/setter
- [[继承]] - extends、super、方法重写
- [[多态]] - 向上转型、向下转型、动态绑定
- [[抽象类与接口]] - abstract、interface 区别
- [[包与访问修饰符]] - package、import、四种访问权限

### 4. 常用类库
- [[String 类]] - 不可变性、常用方法
- [[集合框架入门]] - List、Set、Map 基础
- [[异常处理]] - try/catch/finally、自定义异常
- [[IO 基础]] - File、字节流、字符流

**项目实践**：
- 学生管理系统（控制台版）
- 图书管理系统（面向对象练习）

---

## 第二阶段：Java 进阶（2-3 个月）

### 1. 集合框架深度
- [[ArrayList vs LinkedList]] - 底层实现、性能分析
- [[HashMap 原理]] - 哈希算法、扩容机制、红黑树
- [[ConcurrentHashMap]] - 并发安全实现
- [[其他集合]] - TreeSet、LinkedHashMap、PriorityQueue

### 2. 多线程与并发
- [[线程基础]] - Thread、Runnable、线程生命周期
- [[线程同步]] - synchronized、volatile
- [[锁机制]] - ReentrantLock、读写锁、StampedLock
- [[线程池]] - Executor 框架、核心参数、拒绝策略
- [[并发工具类]] - CountDownLatch、CyclicBarrier、Semaphore
- [[原子类]] - AtomicInteger、LongAdder
- [[并发容器]] - CopyOnWriteArrayList、BlockingQueue

### 3. JVM 基础
- [[JVM 内存模型]] - 堆、栈、方法区、程序计数器
- [[垃圾回收]] - GC 算法、G1、ZGC、Shenandoah
- [[类加载机制]] - 加载、验证、准备、解析、初始化
- [[JVM 调优入门]] - 常用参数、监控工具

### 4. 设计模式
- [[单例模式]] - 五种实现方式
- [[工厂模式]] - 简单工厂、工厂方法、抽象工厂
- [[代理模式]] - 静态代理、动态代理（JDK/CGLIB）
- [[观察者模式]] - 事件驱动编程
- [[其他常用模式]] - 策略、模板方法、装饰器

**项目实践**：
- 简易 Web 服务器（多线程）
- 生产者消费者模型
- 自定义 RPC 框架（入门级）

---

## 第三阶段：Java Web（2-3 个月）

### 1. Web 基础
- [[HTTP 协议]] - 请求方法、状态码、Header
- [[Servlet 规范]] - Servlet、Filter、Listener
- [[JSP 技术]] - 基础语法、EL 表达式、JSTL
- [[Tomcat 服务器]] - 部署、配置、原理

### 2. Spring 框架
- [[Spring Core]] - IoC、DI、Bean 生命周期
- [[Spring AOP]] - 切面、通知、切点表达式
- [[Spring MVC]] - 请求处理、参数绑定、视图解析
- [[Spring Boot]] - 自动配置、Starter、Actuator

### 3. 数据访问
- [[JDBC]] - 原生 API、连接池
- [[MyBatis]] - 映射配置、动态 SQL、插件
- [[Spring Data JPA]] - Repository、JPQL、分页
- [[数据库基础]] - SQL、索引、事务、锁

### 4. 常用中间件
- [[Redis]] - 数据类型、持久化、集群
- [[消息队列]] - RabbitMQ / Kafka 基础
- [[搜索引擎]] - Elasticsearch 入门

**项目实践**：
- 博客系统（Spring Boot + MyBatis + MySQL）
- 电商系统（包含用户、商品、订单模块）
- API 网关（Filter + 限流）

---

## 第四阶段：微服务与云原生（3-4 个月）

### 1. 微服务架构
- [[微服务设计原则]] - 服务拆分、数据一致性
- [[Spring Cloud]] - 
  - [[服务注册发现]] - Nacos / Eureka
  - [[配置中心]] - Nacos Config / Spring Cloud Config
  - [[服务网关]] - Gateway / Zuul
  - [[负载均衡]] - Ribbon / LoadBalancer
  - [[服务调用]] - OpenFeign
  - [[熔断限流]] - Sentinel / Hystrix
  - [[链路追踪]] - SkyWalking / Sleuth

### 2. 容器化与编排
- [[Docker]] - 镜像、容器、Dockerfile
- [[Kubernetes]] - Pod、Service、Deployment
- [[Helm]] - Chart 管理

### 3. DevOps 工具链
- [[Git]] - 分支策略、工作流
- [[Maven/Gradle]] - 构建、依赖管理
- [[CI/CD]] - Jenkins / GitLab CI / GitHub Actions
- [[监控告警]] - Prometheus + Grafana

### 4. 云原生进阶
- [[Service Mesh]] - Istio 概念
- [[Serverless]] - 函数计算

**项目实践**：
- 微服务电商平台（完整链路）
- 容器化部署实战
- CI/CD 流水线搭建

---

## 第五阶段：性能优化与架构设计（持续）

### 1. 性能优化
- [[JVM 深度调优]] - GC 日志分析、内存泄漏排查
- [[SQL 优化]] - 执行计划、索引优化、慢查询
- [[缓存策略]] - 本地缓存、分布式缓存、缓存一致性
- [[并发优化]] - 锁优化、无锁编程

### 2. 分布式系统
- [[分布式事务]] - 2PC、3PC、TCC、Saga
- [[分布式锁]] - Redis、ZooKeeper 实现
- [[分布式 ID]] - 雪花算法、Leaf
- [[分布式会话]] - Session 共享方案

### 3. 架构设计
- [[系统架构设计]] - 高可用、高并发、可扩展
- [[DDD 领域驱动设计]] - 实体、值对象、聚合、领域服务
- [[响应式编程]] - Reactor、WebFlux

### 4. 源码阅读
- [[Spring Framework 源码]]
- [[Spring Boot 源码]]
- [[JDK 源码]] - ArrayList、HashMap、ConcurrentHashMap

---

## 推荐学习资源

### 书籍
1. **入门**
   - 《Head First Java》
   - 《Java 核心技术 卷 I》
   
2. **进阶**
   - 《Effective Java》
   - 《Java 并发编程实战》
   - 《深入理解 Java 虚拟机》
   - 《Java 性能权威指南》

3. **框架**
   - 《Spring 实战》
   - 《Spring Boot 编程思想》
   - 《MyBatis 技术内幕》

### 在线资源
- [[官方文档]] - Oracle Java Docs、Spring 官方文档
- [[技术博客]] - 极客时间、掘金、InfoQ
- [[视频课程]] - 慕课网、B站、Coursera

### 实践平台
- [[LeetCode]] - 算法练习
- [[GitHub]] - 开源项目学习
- [[牛客网]] - 面试题库

---

## 学习建议

1. **不要只看不练** - 每学一个知识点都要写代码实践
2. **重视基础** - 框架会过时，基础永不过时
3. **阅读源码** - 优秀的开源项目是最佳教材
4. **参与社区** - GitHub、Stack Overflow、技术博客
5. **项目驱动** - 用项目检验学习成果
6. **持续学习** - Java 生态不断更新，保持好奇心

---

## 阶段检查清单

- [ ] 基础阶段：能独立完成控制台程序
- [ ] 进阶阶段：理解多线程和 JVM 原理
- [ ] Web 阶段：能开发完整 Web 应用
- [ ] 微服务阶段：能设计分布式系统
- [ ] 优化阶段：能进行性能调优和架构设计

---

> 💡 **提示**：点击 [[ ]] 中的链接可以跳转到对应的详细笔记。建议在学习过程中逐步完善每个主题的笔记。

> 📌 **参考**：[[后端开发技术栈]] | [[计算机基础]] | [[面试准备]]