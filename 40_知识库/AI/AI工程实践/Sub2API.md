---
area: "[[AI工程实践]]"
tags: [AI网关, 账号池, API中转, 订阅额度分发, Agent工具]
created: 2026-06-04
source:
  - https://github.com/Wei-Shaw/sub2api
  - https://raw.githubusercontent.com/Wei-Shaw/sub2api/main/README.md
  - https://raw.githubusercontent.com/Wei-Shaw/sub2api/main/deploy/README.md
---
# Sub2API

## 定义

Sub2API 是一个面向 AI 订阅额度分发的 API 网关平台。它的核心目标是把多个上游账号、API Key 或 OAuth 授权统一放入账号池，再给内部用户分发统一的 API Key，由平台负责鉴权、计费、限流、并发控制、粘性会话和请求转发。

相比 [[New API]]，Sub2API 更贴近“订阅账号池中转站”的场景。

## 主要作用

- 多账号管理：集中管理多个上游账号、API Key 或 OAuth 授权。
- API Key 分发：用户拿到的是 Sub2API 分发的 Key，而不是上游原始凭证。
- 账号池调度：根据分组、状态、并发、额度等选择上游账号。
- 粘性会话：让同一会话尽量绑定同一上游账号，适合 Claude Code、Codex、Gemini CLI 等 Agent 工具。
- 并发控制：支持用户级并发、账号级并发。
- 限流和用量控制：按请求数、token、余额或策略控制使用。
- 日志审计：记录调用、用量和失败情况，便于排查和治理。

## 账号池中转站架构

```text
用户 / Claude Code / Codex / Gemini CLI
  -> Sub2API API Key
  -> Sub2API
  -> 账号池调度层：分组、粘性会话、并发、限流、失败冷却
  -> 上游账号池：Claude / OpenAI / Gemini / Antigravity / API Key / OAuth
```

用户侧只配置 Sub2API 的 Base URL 和平台 Key。上游账号/API Key/OAuth 凭证只保存在 Sub2API 后台。

## 推荐分组方式

不要把所有账号混在一个池子里。建议按工具和协议分组：

- `claude-code-pool`
- `codex-pool`
- `gemini-cli-pool`
- `antigravity-pool`
- `test-pool`

分组的原因：

- 不同上游协议不同。
- 不同工具的上下文机制不同。
- 编程 Agent 场景通常需要粘性会话。
- 出问题时可以隔离某个池子，不影响全部用户。

## 海外服务器部署思路

适合个人或小团队快速使用：

```text
用户电脑 / Agent 客户端
  -> HTTPS 域名
  -> Nginx / Caddy
  -> Sub2API
  -> PostgreSQL / Redis
  -> 上游 AI 服务
```

服务器位置建议：

- 香港：国内访问快，但成本较高。
- 新加坡：综合稳定，适合国内团队。
- 日本：延迟低，价格适中。
- 美国西海岸：上游访问稳定，但国内访问可能慢。

最小配置：

```text
2C4G
40GB SSD
Ubuntu 22.04 / Debian 12
Docker + Docker Compose
域名 + HTTPS
```

## 企业内网自用部署思路

企业内网部署的关键不是公网暴露，而是让 Sub2API 服务器具备稳定、合规的上游访问能力。

推荐架构：

```text
员工电脑 / 内部工具
  -> 企业内网域名
  -> 内网 Nginx / 网关
  -> Sub2API
  -> 企业合规出口代理 / NAT / 专线
  -> OpenAI / Claude / Gemini 等上游
```

部署要点：

- Sub2API 部署在内网服务器或 DMZ。
- 员工通过办公网、VPN 或零信任网关访问。
- 不直接暴露公网。
- 出网通过企业批准的代理、NAT、专线或海外云出口。
- 上游原始账号/API Key 不下发给员工。
- 日志、用户、额度、Key 生命周期纳入企业治理。

如果企业内网无法稳定访问上游 AI 服务，可以采用：

```text
海外云部署 Sub2API
  + 公司 VPN / ZTNA 访问控制
  + 入口不公开暴露
```

这在使用体验上仍然是“企业内网自用”，但上游访问质量通常更好。

## Nginx 关键配置

Sub2API 的粘性会话可能依赖带下划线的 header。Nginx 默认可能丢弃这类 header，因此需要开启：

```nginx
underscores_in_headers on;
```

示例：

```nginx
underscores_in_headers on;

server {
    listen 80;
    server_name ai-gateway.corp.local;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

## 初始部署流程

```bash
mkdir -p /opt/sub2api
cd /opt/sub2api

curl -sSL https://raw.githubusercontent.com/Wei-Shaw/sub2api/main/deploy/docker-deploy.sh | bash

docker compose -f docker-compose.local.yml up -d
docker compose -f docker-compose.local.yml logs -f sub2api
```

企业内部自用建议先使用：

```bash
RUN_MODE=simple
TZ=Asia/Shanghai
```

如果需要多用户余额、充值、计费和 SaaS 化能力，再切换到标准模式。

## 关键配置建议

- 开启粘性会话。
- 设置单用户并发限制。
- 设置单账号并发限制。
- 设置请求频率限制。
- 设置 token 限制。
- 设置失败冷却。
- 按模型、工具和协议隔离账号池。
- 测试账号池与生产账号池分开。

建议初始值：

```text
单用户并发：1-3
单账号并发：1-2
失败冷却：5-10 分钟
```

## 风险和边界

- 只应接入自己或团队合法授权的账号、API Key、OAuth 额度。
- 不应把上游原始账号或原始 API Key 分发给普通用户。
- 需要确认上游服务条款、企业合规要求和数据安全要求。
- 订阅账号共享、额度转售、规避平台风控等行为可能导致账号封禁或服务中断。

## 与 New API 的区别

- [[New API]]：通用 LLM 网关，核心是渠道、模型聚合、计费和权限。
- Sub2API：订阅账号池网关，核心是账号池、粘性会话、并发控制和额度分发。

如果只是多模型 API 聚合，优先看 [[New API]]。  
如果要做 Claude Code、Codex、Gemini CLI 等工具的账号池中转，优先看 Sub2API。

## 参考资料

- [Wei-Shaw/sub2api](https://github.com/Wei-Shaw/sub2api)
- [Sub2API README](https://raw.githubusercontent.com/Wei-Shaw/sub2api/main/README.md)
- [Sub2API 部署说明](https://raw.githubusercontent.com/Wei-Shaw/sub2api/main/deploy/README.md)
