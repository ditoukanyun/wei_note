---
type: wiki
created: 2026-03-16
tags: [redis, docker, 缓存, 数据库]
area: "[[后端开发]]"
---

# Docker 启动 Redis

## 快速启动

```bash
# 最简单的方式
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 带密码
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine \
  --requirepass yourpassword
```

## 完整配置启动

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  -v redis_conf:/usr/local/etc/redis \
  --restart unless-stopped \
  redis:7-alpine \
  redis-server /usr/local/etc/redis/redis.conf
```

### 参数说明

| 参数                                 | 说明                  |
| ------------------------------------ | --------------------- |
| `-d`                                 | 后台运行              |
| `--name redis`                       | 容器名称              |
| `-p 6379:6379`                       | 端口映射（主机:容器） |
| `-v redis_data:/data`                | 数据持久化卷          |
| `-v redis_conf:/usr/local/etc/redis` | 配置文件目录          |
| `--restart unless-stopped`           | 自动重启策略          |

## 配置文件方式

### 1. 创建配置文件

```bash
# 创建本地配置目录
mkdir -p ~/docker/redis/conf

# 创建配置文件
cat > ~/docker/redis/conf/redis.conf << 'EOF'
# 网络配置
bind 0.0.0.0
port 6379

# 密码（生产环境必须设置）
requirepass your_strong_password

# 持久化配置
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000

# 内存配置
maxmemory 256mb
maxmemory-policy allkeys-lru

# 日志
loglevel notice

# 禁用危险命令
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
EOF
```

### 2. 使用配置启动

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v ~/docker/redis/data:/data \
  -v ~/docker/redis/conf:/usr/local/etc/redis \
  --restart unless-stopped \
  redis:7-alpine \
  redis-server /usr/local/etc/redis/redis.conf
```

## Redis CLI 连接

```bash
# 进入容器内的 redis-cli
docker exec -it redis redis-cli

# 带密码连接
docker exec -it redis redis-cli -a yourpassword

# 从宿主机连接（需要安装 redis-cli）
redis-cli -h 127.0.0.1 -p 6379 -a yourpassword
```

## 常用操作

```bash
# 查看日志
docker logs -f redis

# 查看容器内 Redis 信息
docker exec -it redis redis-cli info

# 测试连接
docker exec -it redis redis-cli ping

# 查看内存使用
docker exec -it redis redis-cli info memory

# 查看持久化状态
docker exec -it redis redis-cli info persistence
```

## Docker Compose 方式

```yaml
# docker-compose.yml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./conf/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis_data:
```

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看日志
docker-compose logs -f redis
```

## Redis Sentinel 高可用

```yaml
# docker-compose.yml (Sentinel 模式)
version: "3.8"

services:
  redis-master:
    image: redis:7-alpine
    container_name: redis-master
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  redis-slave:
    image: redis:7-alpine
    container_name: redis-slave
    ports:
      - "6380:6379"
    command: redis-server --slaveof redis-master 6379 --appendonly yes
    depends_on:
      - redis-master

  redis-sentinel:
    image: redis:7-alpine
    container_name: redis-sentinel
    ports:
      - "26379:26379"
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-slave
```

## Redis Cluster 集群

```bash
# 创建集群网络
docker network create redis-cluster

# 启动 6 个节点（3主3从）
for port in $(seq 7000 7005); do
  docker run -d --name redis-${port} \
    --net redis-cluster \
    -p ${port}:${port} \
    redis:7-alpine \
    redis-server \
    --port ${port} \
    --cluster-enabled yes \
    --cluster-config-file nodes.conf \
    --cluster-node-timeout 5000 \
    --appendonly yes
done

# 创建集群
docker exec -it redis-7000 redis-cli --cluster create \
  172.18.0.2:7000 172.18.0.3:7001 172.18.0.4:7002 \
  172.18.0.5:7003 172.18.0.6:7004 172.18.0.7:7005 \
  --cluster-replicas 1
```

## 清理命令

```bash
# 停止并删除容器
docker stop redis && docker rm redis

# 删除数据卷（谨慎使用）
docker volume rm redis_data

# 完全清理
docker stop redis && docker rm redis && docker volume rm redis_data
```

---

## 相关阅读

- [[Docker常用命令]]
- [[Redis数据类型]]
- [[Redis持久化机制]]
