---
type: wiki
area: "[[AI]]"
tags: [Obsidian, Claude Code]
created: 2026-05-08
---
# Obsidian + Claude Code 工作流
Obsidian + Claude Code 工作流是用本地知识库承载任务、项目、研究和自动化整理的协作方式。

## 相关概念
- [[Claude Code 配置详解]]
- [[通用技能 MOC]]

## 工作流程

```mermaid
flowchart LR
  A[Obsidian 捕获想法] --> B[Claude Code 整理和补全]
  B --> C[写入项目或知识库]
  C --> D[建立 wikilink]
  D --> E[复盘和归档]
```

## 实践检查清单

- 收件箱内容是否及时处理为项目、研究或原子笔记。
- Claude Code 修改前是否明确目标目录和笔记格式。
- 生成内容是否使用中文、frontmatter 和 wikilink。
- 重要项目是否在日记中记录进展。
- 完成后是否运行链接和格式校验。

## 案例

看到一篇 AI 工程文章后，先放入 Obsidian 收件箱，再让 Claude Code 拆成“评测集”“工具调用安全”“成本监控”等知识点，并链接到相关项目。

## 常见误区

- 只让 AI 扩写内容，不做结构归类和链接。
- 笔记没有来源和上下文，后续无法复用。
- 自动整理后不检查断链和重复概念。
