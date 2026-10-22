# 配置中心独立 Docker 案例

本例演示订单列表开关与每页数量的动态刷新、多实例同步和环境隔离。使用 Nacos 原生 Java SDK，不依赖数据库、ZooKeeper 或 ElasticJob。

```bash
docker compose up -d --build
```

打开 http://localhost:8081/。初始开发配置为关闭 / 100，测试为关闭 / 7。发布开发开启 / 3 后，列表返回 3 笔，两个开发实例启动标识不变，测试环境保持原值。

```bash
docker compose run --rm verify
docker compose down
```

验证脚本会重置本例配置。构建运行 3 项配置测试，端到端验证覆盖业务响应、非法值保留旧快照、环境隔离和未重启。

固定依赖：Java 17、Spring Boot 3.5.7、Nacos 服务端与客户端 2.5.1；构建镜像 Maven 3.9.9，辅助容器 Python 3.12-alpine。

代码入口：`NacosConfigClient.java` 订阅配置，`ConfigStore.java` 校验与替换快照，`ConfigController.java` 发布和使用配置。Compose 项目名为 `java-config-share`，与定时任务分享的网络、镜像和数据卷独立。

详细操作、端口修改与离线迁移见上级目录《配置中心演示手册》。

扩展实验见上级目录《配置中心扩展实验与实践》：停止 Nacos 后观察内存配置，再验证同一容器与全新 `app-cold` 探针的启动。探针属于 `experiments` profile，不映射宿主机端口，默认不运行。当前 SDK 接口不回退读取磁盘快照，不能将缓存文件存在等同于支持离线启动。
