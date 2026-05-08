---
title: "3 个命令 7 个步骤，学会 git worktree 并行开发"
source: "https://juejin.cn/post/7633718886635356210"
author:
  - "[[双越AI_club]]"
published: 2026-04-29
created: 2026-05-07
description: "大家好，我是双越。wangEditor 作者，前百度 滴滴 资深前端工程师，慕课网金牌讲师，PMP，前端面试派 作者。本文介绍 git worktree 的概念和应用，AI 编程+并行开发，会用到～大家好，我是双越。wangEditorhttps://www.wangeditor.com/ 作者，前百度 滴滴 资深前端"
tags:
  - "clippings"
---
大家好，我是双越。 [wangEditor](https://link.juejin.cn/?target=https%3A%2F%2Fwww.wangeditor.com%2F "https://www.wangeditor.com/") 作者，前百度 滴滴 资深前端工程师，慕课网金牌讲师，PMP， [前端面试派](https://link.juejin.cn/?target=https%3A%2F%2Fwww.mianshipai.com%2F "https://www.mianshipai.com/") 作者。

我正致力于两个项目的开发和升级，感兴趣的可以私信我，加入项目小组。

- [【划水AI】](https://link.juejin.cn/?target=https%3A%2F%2Fwww.huashuiai.com%2F "https://www.huashuiai.com/") Node 全栈 AIGC 知识库，包括 AI 写作、多人协同编辑。复杂业务，真实上线。
- [【智语】](https://link.juejin.cn/?target=https%3A%2F%2Fzhitalk.chat%2F "https://zhitalk.chat/") AI Agent 智能体项目。一个智能面试官，可以优化简历、模拟面试、解答题目等。

## 开始

> 你可以一边修复 bug ，同时一边开发新功能，反正两个目录互不影响。

在过去的传统开发模式中，大多数程序员使用 `git branch` 就已经足够：

这种方式简单直接，在 **单任务开发** 场景下非常高效。

但现在情况变了。

随着 AI 编程工具（如 ChatGPT、Claude Code、Copilot）的普及，开发模式正在发生变化：

- 同时开发多个功能
- 多个 AI 对话并行执行任务
- 长时间等待模型响应
- 需要频繁切换上下文

👉 这时候，传统的 `git branch` 就开始显得不够用了。

于是，一个很多人没用过的工具开始进入视野： **git worktree**

很多程序员甚至从没听说过它，但它其实早就内置在 Git 中。

本文将从实战角度，带你彻底理解并掌握它。

## Git branch 的不足

我们先看一个真实开发场景：你正在开发功能 A，突然被要求紧急修复 bug1。

### 传统做法

当前在 `feature-a` 分支，开发到一半儿了。得先缓存当前代码，再切换到 `bugfix-1` 分支。

```
体验AI代码助手 代码解读复制代码git stash
git checkout -b bugfix-1
```

或者直接提交当前修改，然后切换到 `bugfix-1` 分支。

```sql
体验AI代码助手 代码解读复制代码git commit -m "WIP"
git checkout -b bugfix-1
```

### 存在的问题

#### 1\. 上下文被打断

- stash 容易忘内容
- commit 会污染历史

#### 2\. 切换成本高

频繁的 `stash` 和 `pop` ，容易冲突、出错

```
体验AI代码助手 代码解读复制代码git checkout feature-A
git stash pop
```

#### 3\. 无法并行开发

你同一时间只能处理一个分支：

- 不能一边开发 A，一边修 bug
- 不能同时跑多个 AI 任务

### 本质原因

branch 是“逻辑切换”，不是“物理隔离”。

### worktree 的价值

👉 它解决的是： **让你可以“同时在多个分支开发”，而不是来回切换**

## worktree 的基本使用

### 核心概念

- branch：代码版本线（逻辑）
- worktree：工作目录（物理）

👉 一个仓库可以有多个 worktree

### add 命令

创建一个新的 worktree 并同时创建一个新分支（惯例）

```
体验AI代码助手 代码解读复制代码git worktree add ../project-A -b feature-A
```

PS. 一个分支不能同时在多个 worktree 打开，git 会提示 `fatal: 'feature-A' is already checked out at '/Users/xxx/xxx/project-A'`

### list 命令

列出当前所有的 worktree 目录

```
体验AI代码助手 代码解读复制代码git worktree list
```

### remove 命令

删除一个 worktree：

```arduino
体验AI代码助手 代码解读复制代码git worktree remove ../project-A
```

### 表面现象

你会看到三个同级别的文件夹，其中 `/project` 就是原始项目的文件夹。看起来像多个独立项目。

```bash
体验AI代码助手 代码解读复制代码/project
/project-A
/project-bugfix
```

### 本质

多个目录，共享同一个 Git 仓库 —— 这很重要。

不是执行了三次 `git clone` 创建的三个独立仓库，不是！

### 多目录如何实现共享同一个 git 内容

主仓库的 `.git` 目录，管理着所有 git 数据。这个程序员都知道。

```bash
体验AI代码助手 代码解读复制代码/project/.git/
```

新建的 worktree 仓库中，有一个 `.git` 文件。注意，这是一个 **文件** ，不是目录。

```bash
体验AI代码助手 代码解读复制代码/project-A/.git
```

内容类似如下，连接到主仓库的 git 目录中

```javascript
体验AI代码助手 代码解读复制代码gitdir: /project/.git/worktrees/project-A
```

主仓库里多了如下内容，用于绑定 worktree 的状态信息

```bash
体验AI代码助手 代码解读复制代码/project/.git/worktrees/project-A/
```

这是 git 专门设计的，并不是操作系统的 symlink 软链接。

## 举例说明（完整流程）

### 场景

这是一个实际的开发场景：

- 从 main 开始
- 开发 A 功能
- 中途修 bug1
- bug 合并回 main
- 继续开发 A
- A 合并回 main

### Step 1：初始化

从 main 分支开始

```
体验AI代码助手 代码解读复制代码git checkout main
git pull
```

### Step 2：开始开发 A

新建一个 worktree `project-A` 同时新建一个 `feature-A` 分支

```
体验AI代码助手 代码解读复制代码git worktree add ../project-A -b feature-A
```

### Step 3：出现 bug

此时你不需要 `git stash` 或 `git commit`

你直接新建一个 worktree ，同时基于 `main` 分支新建一个 `bugfix-1` 分支即可。不影响当前分支。

```
体验AI代码助手 代码解读复制代码git worktree add ../project-bugfix -b bugfix-1 main
```

### Step 4：修复 bug

在新的 worktree 修复 bug ，提交代码。正常开发流程。

```bash
体验AI代码助手 代码解读复制代码cd ../project-bugfix
git add .
git commit -m "fix: bug1"
```

### Step 5：合并 bug 代码

在任何一个 worktree ，将 `bugfix-1` 分支的代码合并到 `main` 分支。或者提交 PR 合并都可以。

```bash
体验AI代码助手 代码解读复制代码cd ../project
git checkout main
git pull
git merge bugfix-1
git push
```

合并以后，就可以删掉这个 worktree 和分支

```arduino
体验AI代码助手 代码解读复制代码git worktree remove ../project-bugfix
git branch -D bugfix-1
```

### Step 6：回到 A 功能

回到 A 功能的 worktree 目录，同步最新的 `main` 分支代码

```bash
体验AI代码助手 代码解读复制代码cd ../project-A
git fetch
git rebase origin/main
```

然后继续开发 A 功能的代码。中间如果再有 bug 修复，还是参照上文的步骤。

甚至，你可以一边修复 bug ，同时一边开发 A 功能，反正两个目录互不影响。

### Step 7：完成 A 并合并

等待 A 功能开发完了，提交代码，合并到 `main` 分支。

```sql
体验AI代码助手 代码解读复制代码git add .
git commit -m "feat: A done"

cd ../project
git checkout main
git pull

git merge feature-A
git push
```

最后删掉 worktree 和分支

```
体验AI代码助手 代码解读复制代码git worktree remove ../project-A
git branch -D feature-A
```

以上就是 git worktree 的基础使用，亲自操作一边，肯定已经学会了。

## 非 git 管理的文件

以上讨论的都是 git 管理的文件，还有写文件和目录不是 git 管理的，例如 `.env` 和 `node_modules`

注意，这些文件 git 不管理，worktree 当然也就不会管理它们，需要你自己手动处理。

### .env

像 `.env` 这种单个文件，推荐使用软链接，直接链接到主仓库的原始文件

```bash
体验AI代码助手 代码解读复制代码ln -s ../project/.env ../project-A/.env
```

### node\_modules

node\_modules 目录的内容太多，而且可能还有版本一致性问题，推荐重复安装。  
即新建一个 worktree 之后，在新目录下重新安装。

这里推荐使用 pnpm 安装 `pnpm install` ，它的优势：

## 最后

学会 worktree，你将获得：

- 真正的并行开发能力
- 更好的 AI 编程体验
- 更清晰的开发上下文隔离

最后，worktree 不是替代 branch，而是让 branch 发挥最大价值。