---
type: wiki
area: "[[通用技能]]"
tags: [Git]
created: 2026-05-08
---
# Rebase

## 定义

Rebase 用于把一组提交移动到新的基底上，常用于整理本地提交历史和同步主分支。它会改写提交历史，因此更适合本地分支或明确约定的协作场景。

## 工作流程

```mermaid
flowchart LR
    A["feature: A-B-C"] --> B["main 新增 D-E"]
    B --> C["git rebase main"]
    C --> D["feature: D-E-A'-B'-C'"]
```

Rebase 会把 feature 分支上的提交重新应用到 main 最新提交之后，形成更线性的历史。

## 适用场景

- 本地 feature 分支同步主分支。
- 合并前整理多次零散提交。
- 保持提交历史线性，方便 Code Review。

## 风险与检查清单

- 不要随意 rebase 已被多人基于的共享分支。
- rebase 前确认工作区干净，避免混入未完成修改。
- 解决冲突后运行相关测试，再 `git rebase --continue`。
- 如果 rebase 后需要推送远端，优先使用 `--force-with-lease` 而不是普通强推。

## 案例

本地分支 `feature/a` 开发了 3 个提交，期间 `main` 合入了最新接口契约。此时可以：

```bash
git fetch origin
git rebase origin/main
```

解决冲突并测试通过后，分支历史会像是从最新 `main` 上继续开发。这样 PR 里更容易只看到 feature 自己的改动。

## 常见误区

- 在公共分支上 rebase 后强推，导致其他人的历史断裂。
- 遇到冲突时不了解上下文，机械选择当前分支版本。
- rebase 后不运行测试，遗漏语义冲突。

## 相关概念
- [[Git 基础]]
- [[冲突解决]]
- [[分支管理]]
