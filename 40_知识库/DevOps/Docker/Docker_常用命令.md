# Docker 常用命令

## Nacos

### 单机模式启动

```bash
docker run --name nacos \
  -e MODE=standalone \
  -e NACOS_AUTH_TOKEN="SecretKey012345678901234567890123456789012345678901234567890123456789" \
  -e NACOS_AUTH_IDENTITY_KEY="serverIdentity" \
  -e NACOS_AUTH_IDENTITY_VALUE="security" \
  -p 8080:8080 \
  -p 8848:8848 \
  -p 9848:9848 \
  -d nacos/nacos-server:latest
```

**端口说明：**
- `8080` - Nacos 控制台备用端口
- `8848` - Nacos 主端口（HTTP API、控制台）
- `9848` - gRPC 端口（2.x 版本新增，用于长连接）

**环境变量说明：**
- `MODE=standalone` - 单机模式
- `NACOS_AUTH_TOKEN` - 认证 Token
- `NACOS_AUTH_IDENTITY_KEY/VALUE` - 身份认证配置

---

## Nginx

### 基础启动

```bash
docker run --name nginx -d -p 8888:80 \
  -v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html \
  nginx
```

### 挂载配置文件启动（推荐）

```bash
docker run --name nginx -d -p 8888:80 \
  -v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html \
  -v /Users/chenwei/Documents/docker/nginx/conf.d:/etc/nginx/conf.d \
  nginx
```

**参数说明：**
- `-p 8888:80` - 将主机 8888 端口映射到容器 80 端口
- `-v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html` - 挂载静态文件目录
- `-v /Users/chenwei/Documents/docker/nginx/conf.d:/etc/nginx/conf.d` - 挂载配置文件目录
- `-d` - 后台运行
- `--name nginx` - 指定容器名称

**注意事项：**
- 挂载的本地目录需要提前创建，否则可能报错
- 配置文件修改后需要执行 `docker restart nginx` 生效
- 查看日志：`docker logs nginx`
- 进入容器：`docker exec -it nginx bash`

---

## MySQL

### 基础启动（带数据卷挂载）

```bash
docker run --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -p 3306:3306 \
  -v /Users/chenwei/Documents/docker/mysql/data:/var/lib/mysql \
  -d mysql:latest
```

### 完整启动（推荐）

```bash
docker run --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=mydb \
  -p 3306:3306 \
  -v /Users/chenwei/Documents/docker/mysql/data:/var/lib/mysql \
  -d mysql:latest
```

**参数说明：**
- `-e MYSQL_ROOT_PASSWORD=123456` - 设置 root 密码为 123456
- `-e MYSQL_DATABASE=mydb` - 初始化时创建数据库 mydb（可选）
- `-p 3306:3306` - 映射 MySQL 默认端口
- `-v /Users/chenwei/Documents/docker/mysql/data:/var/lib/mysql` - 挂载数据目录，持久化存储

**常用操作：**
```bash
# 进入 MySQL 容器
docker exec -it mysql bash

# 登录 MySQL（容器内）
mysql -u root -p

# 查看日志
docker logs mysql

# 停止并删除容器
docker stop mysql && docker rm mysql

# 备份数据
docker exec mysql mysqldump -u root -p123456 mydb > backup.sql

# 恢复数据
docker exec -i mysql mysql -u root -p123456 mydb < backup.sql
```

**注意事项：**
- 首次启动前需创建本地数据目录：`mkdir -p /Users/chenwei/Documents/docker/mysql/data`
- 如遇到权限问题，可添加 `--privileged` 参数
- 生产环境建议使用 Docker Compose 管理

---

## Redis

### 基础启动（带数据卷挂载）

```bash
docker run --name redis \
  -p 6379:6379 \
  -v /Users/chenwei/Documents/docker/redis/data:/data \
  -d redis:latest
```

### 开启持久化启动（推荐）

```bash
docker run --name redis \
  -p 6379:6379 \
  -v /Users/chenwei/Documents/docker/redis/data:/data \
  -v /Users/chenwei/Documents/docker/redis/redis.conf:/usr/local/etc/redis/redis.conf \
  -d redis:latest \
  redis-server /usr/local/etc/redis/redis.conf
```

**常用 redis.conf 配置：**
```conf
# 开启 AOF 持久化
appendonly yes
appendfsync everysec

# 设置密码（可选）
requirepass 123456

# 内存限制
maxmemory 256mb
maxmemory-policy allkeys-lru
```

**参数说明：**
- `-p 6379:6379` - 映射 Redis 默认端口
- `-v /Users/chenwei/Documents/docker/redis/data:/data` - 挂载数据目录，持久化存储
- `-v /Users/chenwei/Documents/docker/redis/redis.conf:/usr/local/etc/redis/redis.conf` - 挂载自定义配置文件
- `redis-server /usr/local/etc/redis/redis.conf` - 使用自定义配置启动

**常用操作：**
```bash
# 进入 Redis 容器
docker exec -it redis bash

# 连接 Redis（容器内）
redis-cli

# 连接 Redis（带密码）
redis-cli -a 123456

# 查看日志
docker logs redis

# 停止并删除容器
docker stop redis && docker rm redis

# 备份数据
docker exec redis redis-cli SAVE
cp /Users/chenwei/Documents/docker/redis/data/dump.rdb /backup/
```

**注意事项：**
- 首次启动前需创建本地数据目录：`mkdir -p /Users/chenwei/Documents/docker/redis/data`
- 默认开启 RDB 快照持久化，如需 AOF 需额外配置
- 生产环境建议设置密码并配置内存限制

---

*创建于 2026-03-06*
