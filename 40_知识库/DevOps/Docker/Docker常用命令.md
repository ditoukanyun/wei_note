---
type: wiki
created: 2026-03-16
tags: [docker, devops, 容器化]
area: "[[DevOps]]"
---
# Docker 常用命令

## 镜像管理

```bash
# 搜索镜像
docker search <image_name>

# 拉取镜像
docker pull <image_name>:<tag>
docker pull redis:7-alpine      # 拉取 Redis 7 alpine 版本

# 查看本地镜像
docker images

# 删除镜像
docker rmi <image_id>
docker rmi $(docker images -q)  # 删除所有镜像

# 构建镜像
docker build -t <name>:<tag> .

# 导出/导入镜像
docker save -o <file>.tar <image>
docker load -i <file>.tar
```

## 容器管理

```bash
# 运行容器
docker run [options] <image>
  -d, --detach          # 后台运行
  -p, --publish         # 端口映射 host:container
  -v, --volume          # 挂载卷 host:container
  -e, --env             # 环境变量
  --name                # 容器名称
  --restart             # 重启策略 (always, on-failure)
  --network             # 网络模式

# 查看容器
docker ps               # 运行中的容器
docker ps -a            # 所有容器
docker ps -q            # 只显示 ID

# 容器操作
docker start <container>
docker stop <container>
docker restart <container>
docker rm <container>           # 删除容器
docker rm -f <container>        # 强制删除运行中的容器
docker rm $(docker ps -aq)      # 删除所有容器

# 查看日志
docker logs <container>
docker logs -f <container>      # 实时跟踪
docker logs --tail 100 <container>

# 进入容器
docker exec -it <container> bash
docker exec -it <container> sh  # alpine 用 sh

# 查看容器详情
docker inspect <container>
docker stats                     # 实时资源使用
```

## 网络管理

```bash
# 创建网络
docker network create <network_name>
docker network create --driver bridge mynet

# 查看网络
docker network ls

# 连接容器到网络
docker network connect <network> <container>

# 断开网络
docker network disconnect <network> <container>
```

## 数据卷

```bash
# 创建卷
docker volume create <volume_name>

# 查看卷
docker volume ls

# 查看卷详情
docker volume inspect <volume_name>

# 删除卷
docker volume rm <volume_name>
```

## Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 构建并启动
docker-compose up -d --build
```

---

## 相关阅读

- [[Docker启动Redis]]
- [[Docker启动Nginx]]
- [[Docker启动MySQL]]
- [[Docker启动PostgreSQL]]

## 实践检查清单

- 操作容器前先确认当前环境、容器名和镜像版本，避免误删生产资源。
- 删除容器和数据卷前确认数据是否已经备份。
- 排查问题时优先看 `docker ps`、`docker logs`、`docker inspect` 和 `docker stats`。
- 多容器项目优先使用 Compose 固化命令，减少手工步骤漂移。
- 常用命令可以沉淀到项目 README 或脚本中，但不要把危险清理命令设为默认动作。

## 案例

本地调试后端服务连接 Redis 时，先用 `docker ps` 确认 Redis 容器运行，再用 `docker logs redis` 查看启动错误，最后用 `docker inspect` 检查端口映射和网络。这样比反复重启应用更快定位问题。

## 常见误区

- 把容器当虚拟机长期手工修改，导致镜像和运行态不一致。
- 不理解数据卷，删除容器后误以为数据一定还在。
- 使用 `latest` 镜像标签，重建环境时得到不可预期版本。
