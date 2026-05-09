---
type: wiki
area: "[[通用技能]]"
tags: [Git]
created: 2026-05-08
---
# Git Flow
Git Flow 是以 develop、feature、release、hotfix 等长期分支组织开发和发布的分支模型。

## 分支结构

- main/master：生产发布历史。
- develop：日常集成分支。
- feature：功能开发分支。
- release：发布准备和修复分支。
- hotfix：生产紧急修复分支。

## 工作流程

```mermaid
flowchart TD
    A["feature 分支"] --> B["合入 develop"]
    B --> C["创建 release"]
    C --> D["测试和修复"]
    D --> E["合入 main 发布"]
    F["hotfix"] --> E
```

## 实践检查清单

- 团队是否真的需要长期 develop 和 release 分支。
- 发布周期是否较长且需要独立稳定分支。
- hotfix 是否能同时回合 main 和 develop。
- CI 是否覆盖各类分支。
- 是否和 [[Trunk Based]] 做过取舍比较。

## 案例

传统客户端或嵌入式项目发布周期长，可能适合 Git Flow；高频 Web 服务若有完善 CI 和 Feature Flag，通常更适合 Trunk Based。

## 适用边界

Git Flow 的优势是发布节奏清晰、稳定分支明确，适合版本周期较长、需要并行维护多个发布线的团队。代价是分支多、合并路径长、冲突和遗漏修复的风险更高。团队越小、发布越频繁，Git Flow 的流程成本越容易超过收益。

采用 Git Flow 时要把规则自动化：分支命名、合并方向、CI 触发、发布标签和 hotfix 回合都应写进脚本或流程模板。否则模型清楚但执行混乱，最终仍会出现修复丢失和分支漂移。

## 常见误区

- 小团队照搬 Git Flow，分支管理成本超过收益。
- hotfix 合回遗漏，导致修复在后续版本丢失。

## 相关概念
- [[分支管理]]
- [[Trunk Based]]
