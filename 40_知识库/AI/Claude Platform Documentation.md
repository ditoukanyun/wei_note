---
type: resource
area: "[[AI]]"
tags: [Claude, 文档]
created: 2026-05-08
---
# Claude Platform Documentation
Claude Platform Documentation 是 Claude 平台官方文档入口，用于查阅模型、API、工具和平台能力说明。

## 相关概念
- [[Claude-Platform-Managed-Agents]]
- [[Claude Code 配置详解]]

## 查阅流程

```mermaid
flowchart LR
  A[明确问题类型] --> B[定位模型、API 或工具章节]
  B --> C[查看限制和示例]
  C --> D[本地最小验证]
  D --> E[沉淀配置笔记]
```

## 实践检查清单

- 是否优先查官方文档中的模型、API、限制和计费说明。
- 示例代码是否在本地最小化验证过。
- 平台能力是否和当前云环境、区域、权限匹配。
- 文档更新后是否同步修订本地配置笔记。
- 是否记录关键链接和适用日期。

## 案例

配置 Claude 托管 Agent 前，应先查模型可用区域、认证方式和工具调用限制，再更新 [[Claude-Platform-Managed-Agents]] 中的部署说明。

## 常见误区

- 只看二手教程，忽略官方限制已经变化。
- 没记录文档日期，后续排查不知道依据是否过期。
- 把平台文档当教程，不做本地验证。
