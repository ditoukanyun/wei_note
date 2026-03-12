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

## HTTPS 配置（Let's Encrypt）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d blog.moss.cn -d admin.moss.cn
```

---

*创建于 2026-03-12*
