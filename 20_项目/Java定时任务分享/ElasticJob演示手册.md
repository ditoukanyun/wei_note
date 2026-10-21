---
type: reference
created: 2026-10-21
area: "[[后端开发]]"
tags: [ElasticJob, Docker, 演示]
---
# ElasticJob 演示手册

## 与详稿的时间衔接

本手册支持 [[ElasticJob分享讲稿]] 的第 06 节，约 6 分钟完成三轮结果验证。框架职责、分片计算、事务时间线在详稿其他章节展开；不靠安装、等待或临时故障实验补足时长。

每一轮先预测，再操作，等本轮记录结束后核对订单、尝试次数和流水。讲清“提交触发请求”“产生分片调用”“实际处理订单”三个层次，不能只快速连点按钮。

## 启动与验证

在本篇的 `案例/` 目录执行：

```bash
docker compose up -d --build
docker compose run --rm verify
```

宿主机仅需 Docker 与 Compose v2，首次构建需要联网。建议为 Docker 分配至少 3 GB 内存。本案例只启动 PostgreSQL、ZooKeeper 和两个 Java 应用，不连接配置中心。

| 入口 | 默认地址 |
| --- | --- |
| 任务演示台 | http://localhost:8091/ |
| 任务实例乙 | http://localhost:8092/api/runtime |

构建运行 4 项业务测试。验证容器检查两个实例分片、失败补偿和额外重跑幂等，成功后恢复初始订单。

## 会前准备

```bash
docker compose ps -a
docker compose logs --tail 80 app-a app-b
```

等待两个实例就绪，确认 PostgreSQL 与 ZooKeeper healthy。代码只注册一套 ElasticJob 调度，默认 Cron 为北京时间每天零点，现场通过页面手动触发。

## 现场顺序

### 1. 重置演示订单

点击“重置演示订单”：12 笔待补偿、流水 0，针对 1005 的模拟故障开启。

用前端轮询开场：“两个页面各有自己的定时器；后端两个实例同样需要考虑怎样分担业务。”

### 2. 第一次触发

点击“触发一次任务”，等运行分片回到 0。

预期：

- 0、1、2 三个分片按华东、华南、华北分工。
- 两个实例参与执行，具体分配以现场为准。
- 11 笔成功，1005 待补偿，业务流水 11。
- 1005 的错误为模拟下游超时。

框架分片状态显示“空闲，等待调度”时，说明当前未执行；业务是否成功以订单和分片执行记录为准。

### 3. 恢复后重跑

点击“恢复模拟依赖”，再触发一次。

预期：12 笔成功、流水 12；1005 尝试次数为 2，其他订单为 1。

话术：“就像重新执行按钮，再次进入同一处理路径，实际处理范围由待补偿状态决定。”

### 4. 额外触发

再次触发，流水仍为 12，订单状态与尝试次数保持原值。

接着讲前端按钮防重复与后端幂等的边界，并展示独立事务类 `OrderProcessor.java`。

## 备用命令

```bash
curl http://localhost:8091/api/shards
curl http://localhost:8091/api/summary
curl http://localhost:8091/api/orders
curl -X POST http://localhost:8091/api/jobs/trigger -H 'Content-Type: application/json' -d '{}'
curl -X POST http://localhost:8091/api/demo/failure -H 'Content-Type: application/json' -d '{"enabled":false}'
curl -X POST http://localhost:8091/api/demo/reset -H 'Content-Type: application/json' -d '{}'
```

Windows PowerShell 使用 `curl.exe`。重置会清空本案例的流水与执行记录，仅在无分片运行时操作。

## 可选：只留一个实例

待任务结束后停止实例乙：

```bash
docker compose stop app-b
```

等待注册中心感知，下一次触发观察剩余实例承担全部分片。恢复：

```bash
docker compose start app-b
```

本例未开启 failover，该操作用于观察后续调度的重新分配，不用于证明执行中分片立即故障转移。

## 停止与重建

```bash
docker compose down
```

数据卷保留。需要完全初始化时可执行 `docker compose down -v`，它会删除本案例的订单与注册中心数据。端口冲突时复制 `.env.example` 为 `.env` 调整外部端口。

## 离线迁移

在与公司电脑同架构的联网环境构建后：

```bash
docker image save -o job-share-images.tar java-job-share-demo:1.0.0 zookeeper:3.9.3 postgres:16.6-alpine python:3.12-alpine
```

复制本篇源码与镜像文件到公司电脑：

```bash
docker image load -i job-share-images.tar
docker compose up -d --no-build --pull never
```

源码包不包含镜像，导出的镜像需要与公司电脑 CPU 架构匹配。
