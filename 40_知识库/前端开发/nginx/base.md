# nginx 基础

## Docker 启动 Nginx

### 快速启动

```bash
# 最简单的方式
docker run -d --name nginx -p 80:80 nginx:alpine

# 指定端口
docker run -d --name nginx -p 8888:80 nginx:alpine
```

### 带配置挂载

```bash
docker run --name nginx -d -p 8888:80 \
  -v /Users/chenwei/Documents/docker/nginx/html:/usr/share/nginx/html \
  -v /Users/chenwei/Documents/docker/nginx/conf.d:/etc/nginx/conf.d \
  nginx:alpine
```

### 完整配置启动

```bash
# 创建本地目录
mkdir -p ~/docker/nginx/{html,conf.d,logs,ssl}

# 启动容器
docker run -d --name nginx \
  -p 80:80 \
  -p 443:443 \
  -v ~/docker/nginx/html:/usr/share/nginx/html \
  -v ~/docker/nginx/conf.d:/etc/nginx/conf.d \
  -v ~/docker/nginx/nginx.conf:/etc/nginx/nginx.conf \
  -v ~/docker/nginx/logs:/var/log/nginx \
  -v ~/docker/nginx/ssl:/etc/nginx/ssl \
  --restart unless-stopped \
  nginx:alpine
```

### 参数说明

| 参数                                      | 说明           |
| ----------------------------------------- | -------------- |
| `-p 80:80`                                | HTTP 端口映射  |
| `-p 443:443`                              | HTTPS 端口映射 |
| `-v .../html:/usr/share/nginx/html`       | 静态文件目录   |
| `-v .../conf.d:/etc/nginx/conf.d`         | 站点配置目录   |
| `-v .../nginx.conf:/etc/nginx/nginx.conf` | 主配置文件     |
| `-v .../logs:/var/log/nginx`              | 日志目录       |
| `-v .../ssl:/etc/nginx/ssl`               | SSL 证书目录   |

### 常用操作

```bash
# 测试配置语法
docker exec nginx nginx -t

# 重载配置（不重启）
docker exec nginx nginx -s reload

# 查看日志
docker logs -f nginx
tail -f ~/docker/nginx/logs/access.log

# 进入容器
docker exec -it nginx sh

# 查看版本
docker exec nginx nginx -v
```

### Docker Compose 方式

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./html:/usr/share/nginx/html
      - ./conf.d:/etc/nginx/conf.d
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./logs:/var/log/nginx
      - ./ssl:/etc/nginx/ssl
```

```bash
# 启动
docker-compose up -d

# 重载配置
docker-compose exec nginx nginx -s reload
```

---

## 配置语法

```sh
location /{
  alias lib/;# 别名,重定向路径
  autoindex on;# 开启静态目录索引
  set $limit_rate 1k;# 限速
}

log_format main 'xxx' # main命名日志
access_log path main；# 日志记录位置
listen 127.0.0.1:8080;# 只允许本机8080地址

# 上游服务集合
upstream name{
  server 127.0.0.1:8080;# 上游服务器
}
server{
  location /{
    proxy_set_header Host $host;# 设置代理请求头（代理源head）
    proxy_pass http://name;# 代理到name上游
  }
}
```

https://nginx.org/en/docs/http/ngx_http_proxy_module.html

```sh
http {
  proxy_cache_path /tmp/cache levels=1:2 keys_zone=cachename:10m max_size=10g inactive=60m use_temp_path=off;
}
缓存
location /{
  proxy_cache cachename;
  proxy_cache_key $host$args;
  proxy_cache_valid 200 304 1d;缓存请求
}

```

goaccess 日志查看工具
