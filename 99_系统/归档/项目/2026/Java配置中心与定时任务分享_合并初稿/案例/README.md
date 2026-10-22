# Java 配置中心与定时任务 Docker 案例

一个真实接入 Nacos、ZooKeeper、PostgreSQL 和 ElasticJob 的 Spring Boot 演示。两个开发实例执行三个区域分片，测试观察实例使用独立配置与数据库。

## 启动

在当前目录执行：

```bash
docker compose up -d --build
```

打开 http://localhost:8081/，等待三个实例连接完成。宿主机只需 Docker + Compose v2，Java 与 Maven 都在构建容器中。

首次拉取和构建需要联网，建议 Docker 至少分配 4 GB 内存。默认端口为 8081、8082、8083、8848；冲突时复制 `.env.example` 为 `.env` 后调整。

## 演示顺序

1. 点击“重置演示数据与配置”，等待开发 `false / 100`、测试 `false / 7`。
2. 发布开发配置 `true / 20`，比较启动标识，验证动态刷新。
3. 触发任务：11 笔成功、1005 失败，业务流水 11。
4. 恢复模拟依赖，再次触发：12 笔成功，业务流水 12。
5. 额外触发：流水仍为 12，已完成订单的尝试次数不变。

页面是本案例的中文教学控制台，配置操作走 Nacos API，任务触发走真实 ElasticJob API。Nacos 原生控制台在 http://localhost:8848/nacos/。未打包 ElasticJob 官方 UI。

## 自动验证

```bash
docker compose run --rm verify
```

验证会重置演示数据与配置，覆盖真实动态刷新、环境隔离、双实例分片、失败补偿、重跑、非法配置和批量大小，成功后恢复初始状态。

Docker 构建过程中会运行 7 项 Java 测试。若需要单独运行 Java 测试，仍无需安装宿主机 Maven：

```bash
docker run --rm -v "${PWD}:/workspace" -w /workspace maven:3.9.9-eclipse-temurin-17 mvn -B -ntp test
```

这条命令使用 macOS / Linux 或 PowerShell 的路径变量语法；Compose 的启动与验证命令不依赖该卷挂载写法。

## 固定版本

| 组件 | 版本 |
| --- | --- |
| Java | 17 |
| Maven 构建镜像 | 3.9.9-eclipse-temurin-17 |
| Spring Boot | 3.5.7 |
| Nacos 服务端 / Java 客户端 | 2.5.1 |
| ElasticJob Lite | 3.0.4 |
| ZooKeeper | 3.9.3 |
| PostgreSQL | 16.6-alpine |
| 初始化与验证容器 | Python 3.12-alpine |

这些是教学案例固定的依赖，不代表团队必须采用的升级目标。未强制指定 CPU 架构，构建时使用目标电脑匹配的镜像。

## 关键目录

```text
案例/
├── compose.yaml                    容器编排、端口与依赖顺序
├── Dockerfile                      容器内测试、构建、运行
├── pom.xml                         固定依赖版本
├── infra/初始化数据库.sql           创建独立开发与测试数据库
├── scripts/初始化配置.py            创建两个 Nacos 命名空间与初始配置
├── scripts/验证演示.py              真实服务端到端验证
└── src/
    ├── main/java/cn/orbit/share/    配置监听、Job、业务处理、演示 API
    ├── main/resources/             应用配置、数据库结构、中文页面
    └── test/java/cn/orbit/share/    校验、事务、幂等与分片范围测试
```

## 停止

```bash
docker compose down
```

数据保存在本案例的命名卷中。`docker compose down -v` 会清空本案例配置与数据库，供完全重建时使用。

完整彩排、备用命令、故障排查和离线迁移步骤见上级目录的《演示操作手册》。
