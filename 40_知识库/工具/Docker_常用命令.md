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

*创建于 2026-03-06*
