# ElasticJob 独立 Docker 案例

两个任务实例，通过 ZooKeeper 协调三个区域分片，处理共享 PostgreSQL 中的 12 笔待补偿订单。本案例不连接配置中心。

```bash
docker compose up -d --build
```

打开 http://localhost:8091/。重置订单后首次触发得到 11 成功、1 失败；恢复模拟依赖并重跑后得到 12 成功；额外重跑不会增加业务流水。

```bash
docker compose run --rm verify
docker compose down
```

验证会重置演示订单。构建执行 4 项测试，覆盖并发幂等、失败恢复、事务回滚和分片范围；真实环境验证覆盖两实例与三个分片。

固定版本：Java 17、Spring Boot 3.5.7、ElasticJob 3.0.4、ZooKeeper 3.9.3、PostgreSQL 16.6-alpine；Maven 构建镜像为 3.9.9，验证容器为 Python 3.12-alpine。

源码入口：`JobInfrastructure.java` 注册任务，`CompensationJob.java` 适配上下文，`CompensationService.java` 分批执行，`OrderProcessor.java` 负责单笔事务与幂等。

运行参数来自本地 `application.yaml`，`TaskSettings.java` 读取它们。本篇不演示运行时动态配置刷新。

页面是本案例的教学控制台，通过真实 ElasticJob API 触发。未打包官方 ElasticJob UI。

Compose 项目名为 `java-job-share`，默认端口 8091 / 8092。操作与离线迁移见上级目录《ElasticJob演示手册》。
