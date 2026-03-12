# Docker 常用命令

## Nginx

### 本地启动 Nginx（基础版）

```bash
docker run --name nginx -d -p 8888:80 -v /Users/chenwei/Document/docker/nginx/html:/usr/share/nginx/html nginx
```

### 本地启动 Nginx（带配置挂载）

```bash
docker run --name nginx -d -p 8888:80 \
  -v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html \
  -v /Users/chenwei/Documents/docker/nginx/conf.d:/etc/nginx/conf.d \
  nginx
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--name nginx` | 容器命名为 nginx |
| `-d` | 后台运行（detached 模式） |
| `-p 8888:80` | 主机 8888 端口映射到容器 80 端口 |
| `-v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html` | 挂载本地 html 目录到容器 |
| `-v /Users/chenwei/Documents/docker/nginx/conf.d:/etc/nginx/conf.d` | 挂载本地配置目录到容器 |
| `nginx` | 使用的镜像名称 |

---

*记录时间: 2026-03-11*
