---
created: 2026-02-25
type: concept
category: AI/Agents
tags: [AI, Agent, OpenClaw, plugin, extension]
aliases: [技能, 插件, 能力模块]
area: [[AI]]
---
# Skills

**定义**: Skills（技能）是 AI Agent 的能力扩展模块，定义了 Agent 可以执行的具体任务集合。类似于软件中的"插件"或"应用"。

## Skill 的组成

一个典型的 Skill 包含：

```yaml
name: "邮件管理"
description: "管理 Gmail 邮件的 Skill"
version: "1.0.0"

triggers:
  - "检查邮件"
  - "发送邮件"
  - "邮件摘要"

actions:
  - name: check_inbox
    description: "检查收件箱"
  - name: send_email
    description: "发送邮件"
  - name: summarize_emails
    description: "总结邮件内容"
```

## Skill 的分类

### 按功能分类
| 类别 | 示例 Skills |
|------|-------------|
| **通讯** | email-manager, slack-bot, whatsapp-integration |
| **生产力** | calendar, todo-list, file-organizer |
| **信息** | web-search, rss-reader, news-aggregator |
| **自动化** | cron-jobs, webhook-handler, browser-control |
| **集成** | github-integration, notion-api, linear-api |

### 按来源分类
| 来源 | 说明 |
|------|------|
| **官方** | OpenClaw 团队维护的核心 Skills |
| **社区** | 第三方开发者在 Clawhub 上发布的 Skills |
| **自定义** | 用户自己编写的私有 Skills |

## Skill 的生命周期

```
发现 → 安装 → 配置 → 使用 → 更新 → 卸载
```

### 管理命令（以 OpenClaw 为例）

```bash
# 搜索 Skills
openclaw skills search email

# 查看详情
openclaw skills info @openclaw/email-manager

# 安装 Skill
openclaw skills install @openclaw/email-manager

# 更新 Skill
openclaw skills update @openclaw/email-manager

# 卸载 Skill
openclaw skills uninstall @openclaw/email-manager

# 列出已安装
openclaw skills list

# 重新加载（开发时使用）
openclaw skills reload
```

## 自定义 Skill 开发

Skill 可以使用 YAML 或 Markdown 定义：

```yaml
# ~/.openclaw/skills/my-custom-skill.yaml
name: "天气助手"
description: "查询天气信息"
version: "1.0.0"

triggers:
  - "天气"
  - "今天天气如何"
  - "查天气"

steps:
  - action: extract_location
    from: "{{user_message}}"
    
  - action: api_call
    url: "https://api.weather.com/v1/current?city={{location}}"
    
  - action: format_response
    template: "{{city}}今天{{weather}}，温度{{temperature}}度"
```

## Skill 设计最佳实践

1. **单一职责**: 每个 Skill 只做一件事，做好一件事
2. **明确触发词**: 使用清晰、不易混淆的触发词
3. **错误处理**: 优雅处理 API 失败、超时等情况
4. **权限最小化**: 只请求必要的权限
5. **文档完整**: 提供清晰的安装和使用说明

## 相关概念

- [[AI Agent]] - Skills 是 Agent 的能力模块
- [[Gateway]] - Gateway 接收的输入触发 Skills
- [[API]] - Skills 通常调用外部 API 完成任务

---

*参考: [[OpenClaw]] 使用 Skills 系统扩展功能*

## 实践检查清单

- Skill 是否有清晰的触发场景，避免和其他 Skill 抢同一类请求。
- 输入参数是否有结构化约束，减少模型误提取。
- 外部 API、文件系统或账号权限是否遵循最小权限。
- 失败时是否返回可解释错误，而不是静默失败。
- 更新 Skill 后是否用典型用户请求做回归验证。

## 案例

邮件管理 Skill 可以只负责“读取、筛选、归档邮件”，而不要同时承担日程规划、客户画像和项目管理。跨领域需求应拆给不同 Skill，再由 Agent 编排。

## 常见误区

- Skill 描述过宽，模型不知道什么时候该调用。
- 把多个无关能力塞进同一个 Skill，后续调试和权限控制困难。
- 只写成功路径，没有处理鉴权失效、API 超时和空结果。
