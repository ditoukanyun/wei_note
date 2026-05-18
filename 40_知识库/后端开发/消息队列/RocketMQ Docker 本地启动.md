---
type: wiki
area: "[[后端开发]]"
tags:
  - 后端开发
  - 消息队列
  - RocketMQ
  - Docker
created: 2026-05-15
---
# RocketMQ Docker 本地启动

## 适用场景

本笔记用于本地学习和调试 RocketMQ 5.x，启动组件包括：

- NameServer：路由注册中心，默认端口 `9876`。
- Broker：消息存储与投递服务，常用端口 `10909`、`10911`、`10912`。
- Proxy：RocketMQ 5.x Java 新客户端连接入口，常用端口 `8080`、`8081`。

> [!important]
> RocketMQ 5.x `rocketmq-client-java` 新客户端一般连接 Proxy，例如 `localhost:8081`。`9876` 是 NameServer 端口，主要给 Broker 和 `mqadmin` 使用。

## 启动命令

### 1. 创建 Docker 网络

```bash
docker network create rocketmq
```

RocketMQ 通常包含多个容器，把它们放到同一个 Docker 网络后，容器之间可以通过容器名通信。例如 Broker 可以通过 `rmqnamesrv:9876` 访问 NameServer。

### 2. 启动 NameServer

```bash
docker run -d \
  --name rmqnamesrv \
  -p 9876:9876 \
  --network rocketmq \
  apache/rocketmq:5.5.0 \
  sh mqnamesrv
```

查看日志：

```bash
docker logs -f rmqnamesrv
```

看到类似下面内容，说明 NameServer 已启动：

```text
The Name Server boot success
```

### 3. 启动 Broker 和 Proxy

```bash
docker run -d \
  --name rmqbroker \
  --network rocketmq \
  -p 10909:10909 \
  -p 10911:10911 \
  -p 10912:10912 \
  -p 8080:8080 \
  -p 8081:8081 \
  -e "NAMESRV_ADDR=rmqnamesrv:9876" \
  apache/rocketmq:5.5.0 \
  sh mqbroker --enable-proxy -c /home/rocketmq/rocketmq-5.5.0/conf/broker.conf
```

这条命令同时完成两件事：

- 启动 RocketMQ Broker，负责消息存储、投递和消费进度管理。
- 通过 `--enable-proxy` 同时启动 RocketMQ Proxy，给 RocketMQ 5.x 新客户端提供接入入口。

参数含义：

| 参数 | 作用 |
|---|---|
| `--name rmqbroker` | 容器名，后续可用 `docker logs rmqbroker`、`docker exec rmqbroker ...` 操作。 |
| `--network rocketmq` | 加入 `rocketmq` 网络，使 Broker 可以通过 `rmqnamesrv:9876` 访问 NameServer。 |
| `-p 10909:10909`、`-p 10911:10911`、`-p 10912:10912` | 暴露 Broker 相关端口，主要用于 Broker 通信、旧客户端或内部组件。 |
| `-p 8080:8080`、`-p 8081:8081` | 暴露 Proxy 端口，RocketMQ 5.x `rocketmq-client-java` 通常连接 `8081`。 |
| `-e "NAMESRV_ADDR=rmqnamesrv:9876"` | 告诉 Broker 和 Proxy 去哪里找 NameServer。 |
| `apache/rocketmq:5.5.0` | 使用 RocketMQ 5.5.0 Docker 镜像。 |
| `sh mqbroker --enable-proxy ...` | 启动 Broker，并开启 Proxy。 |

查看日志：

```bash
docker logs -f rmqbroker
```

看到类似下面内容，说明 Proxy 已启动：

```text
rocketmq-proxy startup successfully
```

## 初始化 Topic 和消费者组

RocketMQ 5.x 新客户端里，Topic 和 ConsumerGroup 建议提前创建。

### 创建 Topic

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin updateTopic -n rmqnamesrv:9876 -c DefaultCluster -t TestTopic'
```

查看 Topic 列表：

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin topicList -n rmqnamesrv:9876'
```

查看 Topic 状态：

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin topicStatus -n rmqnamesrv:9876 -t TestTopic'
```

### 创建消费者组

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin updateSubGroup -n rmqnamesrv:9876 -c DefaultCluster -g YourConsumerGroup'
```

如果消费者启动时报下面错误，通常就是消费者组未提前创建：

```text
No topic route info in name server for the topic: %RETRY%YourConsumerGroup
```

## Java 客户端连接配置

使用 `rocketmq-client-java` 5.x 时，客户端连接 Proxy：

```java
String endpoints = "localhost:8081";
String topic = "TestTopic";
String consumerGroup = "YourConsumerGroup";
```

不要把新客户端的 `endpoints` 配成 `localhost:9876`。`9876` 是 NameServer，不是 5.x Proxy 客户端入口。

本地 Docker 启动后的访问链路是：

```text
Java Producer / Consumer
        |
        | localhost:8081
        v
RocketMQ Proxy
        |
        v
RocketMQ Broker
        |
        v
NameServer: rmqnamesrv:9876
```

端口分工：

| 端口 | 组件 | 用途 |
|---|---|---|
| `9876` | NameServer | 路由注册中心，给 Broker、Proxy、`mqadmin` 使用。 |
| `10911` | Broker | Broker 主通信端口，常见于旧客户端或内部通信。 |
| `10909`、`10912` | Broker | Broker 相关通信端口。 |
| `8081` | Proxy | RocketMQ 5.x Java 新客户端的常用接入端口。 |
| `8080` | Proxy | Proxy 相关端口，部分接入方式或内部能力会使用。 |

因此，代码里写 `localhost:8081` 的原因是：Docker 命令把容器内 Proxy 的 `8081` 端口映射到了宿主机，Java 程序运行在宿主机上，需要通过这个端口访问 RocketMQ Proxy。

## 常用检查命令

查看容器：

```bash
docker ps
```

查看 Docker 网络：

```bash
docker network inspect rocketmq
```

查看 Broker 集群：

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin clusterList -n rmqnamesrv:9876'
```

查看消费者进度：

```bash
docker exec rmqbroker sh -lc '$ROCKETMQ_HOME/bin/mqadmin consumerProgress -n rmqnamesrv:9876 -g YourConsumerGroup'
```

## 停止和清理

停止容器：

```bash
docker stop rmqbroker rmqnamesrv
```

删除容器：

```bash
docker rm rmqbroker rmqnamesrv
```

删除网络：

```bash
docker network rm rocketmq
```

如果只是重启容器，不需要删除网络。

## 常见问题

### 容器名已存在

报错：

```text
Conflict. The container name "/rmqnamesrv" is already in use
```

处理：

```bash
docker rm -f rmqnamesrv
docker rm -f rmqbroker
```

### Consumer 没有输出

优先检查三件事：

- Producer 是否真的发送成功。
- Consumer 是否先启动，并且订阅的是同一个 `topic` 和 `tag`。
- `consumerGroup` 是否已经创建，消费位点是否已经移动到最新。

如果 Producer 先发完，Consumer 后启动，可能因为消费位点原因看不到旧消息。学习阶段可以换一个新的消费者组名重新测试。

## 相关概念

- [[消息队列]]
- [[消息队列总览：RabbitMQ、Kafka 与可靠消息]]
- [[消息可靠性：确认、重试与死信队列]]
