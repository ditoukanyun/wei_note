---
type: wiki
area: "[[通用技能]]"
tags: [开发工具]
created: 2026-05-08
---
# JetBrains
JetBrains 是 IDE 工具系列，覆盖 IntelliJ IDEA、WebStorm、PyCharm 等开发环境。

## 相关概念
- [[VS Code 配置]]

## 使用场景

- Java、Kotlin、Spring 项目通常使用 IntelliJ IDEA 获得更完整的重构和调试体验。
- 前端项目可使用 WebStorm，重点利用 TypeScript、测试和重构能力。
- Python 项目可使用 PyCharm 管理解释器、虚拟环境和调试配置。

## 配置流程

```mermaid
flowchart LR
  A[打开项目] --> B[配置 SDK 和依赖]
  B --> C[配置代码风格]
  C --> D[配置运行和调试]
  D --> E[同步团队设置]
```

## 实践检查清单

- SDK、Node、Python 或 JDK 版本是否和项目一致。
- 代码格式化、导入排序和静态检查是否和 CI 对齐。
- Run Configuration 是否能一键启动本地服务和测试。
- 是否把个人本地路径和账号信息排除出版本控制。
- 是否善用重构、断点、数据库和 HTTP Client 等内置工具。

## 团队协作边界

JetBrains 的价值不只是编辑代码，还包括安全重构、调试、依赖导航、数据库查看和测试运行。团队应把代码风格、检查规则和运行配置尽量沉淀为项目配置，但个人主题、窗口布局、本地路径和账号信息不应提交。

大型 Java 或 Spring 项目中，IDE 对 Bean、调用链和重构的理解能显著降低维护成本。使用前要确保 JDK、构建工具和插件版本与项目一致，否则本地能跑不代表 CI 能过。

## 常见误区

- 只把 IDE 当编辑器，忽略重构和调试能力。
- 团队格式化规则不一致，提交产生大量无关 diff。
- 把 `.idea` 中的个人配置提交到仓库。
