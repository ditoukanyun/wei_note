# Nginx 多前端项目部署指南

## 概述

一台 Nginx 服务器可以托管多个前端项目，常见有两种方式：
- **子域名区分**（推荐）：`blog.moss.cn`、`admin.moss.cn`
- **路径区分**：`moss.cn/blog/`、`moss.cn/admin/`

---

## 方案一：子域名区分（推荐）

### 原理

```
用户访问          Nginx 判断            返回对应项目
─────────        ───────────           ───────────
blog.moss.cn  →  server_name 匹配  →  /var/www/blog/
app.moss.cn   →  server_name 匹配  →  /var/www/app/
```

### DNS 配置

| 记录类型 | 主机记录 | 记录值 |
|---------|---------|--------|
| A | `blog` | 118.145.223.121 |
| A | `admin` | 118.145.223.121 |

### Nginx 配置

```nginx
# blog.moss.cn
server {
    listen 80;
    server_name blog.moss.cn;
    
    root /var/www/blog/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}

# admin.moss.cn
server {
    listen 80;
    server_name admin.moss.cn;
    
    root /var/www/admin/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 后台API代理
    location /api/ {
        proxy_pass http://localhost:8080/;
    }
}
```

### 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/blog.moss.cn /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/admin.moss.cn /etc/nginx/sites-enabled/

# 检查并重载
sudo nginx -t
sudo nginx -s reload
```

---

## 方案二：路径区分

### 前端需要做的处理

#### 1. 构建时设置 base 路径

**Vite:**
```js
// vite.config.js
export default {
  base: '/app/',  // ← 关键
}
```

**Webpack:**
```js
module.exports = {
  publicPath: '/app/',
}
```

#### 2. 前端路由配置

**Vue Router:**
```js
const router = createRouter({
  history: createWebHistory('/app/'),
  routes: [...]
})
```

**React Router:**
```js
<BrowserRouter basename="/app">
  <Routes>...</Routes>
</BrowserRouter>
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    location /app/ {
        alias /var/www/app/dist/;
        try_files $uri $uri/ /app/index.html;
    }
    
    location /admin/ {
        alias /var/www/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }
}
```

**关键点：**
- 用 `alias` 而不是 `root`
- `try_files` 回退到对应项目的 `index.html`

---

## 本地开发模拟域名

### 修改 hosts 文件

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Mac/Linux:** `/etc/hosts`

```hosts
127.0.0.1  blog.local
127.0.0.1  admin.local
127.0.0.1  api.local
```

### 本地 Nginx 配置

```nginx
server {
    listen 80;
    server_name blog.local;
    root /Users/用户名/projects/blog/dist;
    index index.html;
}
```

### 刷新 DNS 缓存

```bash
# Windows
ipconfig /flushdns

# Mac
sudo killall -HUP mDNSResponder
```

---

## 方案对比

| 方案 | URL 示例 | 前端配置 | 适用场景 |
|-----|---------|---------|---------|
| **子域名** | `blog.moss.cn` | 无需额外配置 ✅ | 正式环境、独立项目 |
| 路径区分 | `moss.cn/blog/` | 需要设置 base | 快速测试、简单部署 |
| 不同端口 | `moss.cn:3000` | 无需配置 | 开发调试 |

---

## 常见问题

| 问题 | 原因 | 解决 |
|-----|------|------|
| 页面空白 | 资源 404 | 检查 `base` / `publicPath` |
| 刷新 404 | 路由问题 | `try_files` 配置 |
| 图片不显示 | 绝对路径问题 | 用相对路径或带 base |

---

## 反向代理与负载均衡

### 反向代理 (Reverse Proxy)

**作用：** 用户请求先到 Nginx，Nginx 再转发到后端服务器，用户不知道真正的服务器是谁。

```
用户请求 → Nginx（反向代理）→ 后端服务器 → 返回给用户
```

**基础配置：**
```nginx
server {
    listen 80;
    server_name api.moss.cn;
    
    location / {
        proxy_pass http://localhost:8080;
        
        # 转发真实 IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

### 负载均衡 (Load Balancer)

**作用：** 将流量分摊到多台服务器，避免单点过载。

```
                    ┌─→ 服务器 A
用户请求 → Nginx ──┼─→ 服务器 B
                    └─→ 服务器 C
```

**配置示例：**
```nginx
# 定义后端服务器组
upstream backend {
    server 192.168.1.10:8080 weight=5;
    server 192.168.1.11:8080 weight=3;
    server 192.168.1.12:8080 backup;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
    }
}
```

### 负载均衡算法

| 算法 | 说明 | 配置 |
|-----|------|------|
| 轮询 | 依次分配（默认） | 无需配置 |
| 权重 | 按权重比例分配 | `weight=5` |
| IP 哈希 | 同 IP 访问同一台 | `ip_hash;` |
| 最少连接 | 分配给连接最少的服务器 | `least_conn;` |

### 实际应用场景

**前后端分离：**
```nginx
server {
    listen 80;
    server_name moss.cn;
    
    # 前端
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8080/;
    }
}
```

**微服务网关：**
```nginx
upstream user-service {
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
}

upstream order-service {
    server 10.0.2.10:8080;
    server 10.0.2.11:8080;
}

server {
    location /user/ {
        proxy_pass http://user-service/;
    }
    
    location /order/ {
        proxy_pass http://order-service/;
    }
}
```

### 反向代理 vs 负载均衡

| 特性 | 反向代理 | 负载均衡 |
|-----|---------|---------|
| 核心作用 | 隐藏后端服务器 | 分摊流量压力 |
| 服务器数量 | 通常 1 台 | 多台 |
| 主要目的 | 安全、统一入口 | 性能、高可用 |
| 关系 | 基础功能 | 反向代理的扩展 |

---

## HTTPS 配置（Let's Encrypt）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d blog.moss.cn -d admin.moss.cn
```

---

*创建于 2026-03-12*
