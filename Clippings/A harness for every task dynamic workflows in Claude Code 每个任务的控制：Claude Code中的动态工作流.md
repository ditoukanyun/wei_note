---
title: "A harness for every task: dynamic workflows in Claude Code 每个任务的控制：Claude Code中的动态工作流"
source: "https://x.com/trq212/status/2061907337154367865"
author:
  - "[[@trq212]]"
published: 2026-06-03
created: 2026-06-03
description: "Last week, we released dynamic workflows   动态工作流 in Claude Code. Claude can now write its own harness   利用 on the fly, custom-built for the ..."
tags:
  - "clippings"
---
![图像](https://pbs.twimg.com/media/HJ0q6o6aYAEM_ej?format=jpg&name=large)

Last week, we released [dynamic workflows 动态工作流](https://code.claude.com/docs/en/workflows) in Claude Code. Claude can now write its own [harness 利用](https://code.claude.com/docs/en/glossary#agentic-harness) on the fly, custom-built for the task at hand.上周，我们在Claude Code中发布了动态工作流。克劳德现在可以在飞行中编写自己的挽具，为手头的任务定制。

While the default Claude Code harness is built for coding, it is also useful for many other types of tasks because, as it turns out, many tasks resemble coding tasks. But there are certain classes of tasks where we have had to build custom harnesses on top of Claude Code to achieve peak performance such as [Research 研究](https://support.claude.com/en/articles/11088861-using-research-on-claude), [security analysis 安全分析](https://support.claude.com/en/articles/11932705-automated-security-reviews-in-claude-code), [agent teams 代理团队](https://code.claude.com/docs/en/agent-teams), or [Code Review 代码评审](https://code.claude.com/docs/en/code-review).虽然默认的Claude Code工具是为编码而构建的，但它对于许多其他类型的任务也很有用，因为事实证明，许多任务类似于编码任务。但是，在某些任务类别中，我们不得不在Claude Code之上构建自定义控制，以达到峰值性能，例如研究、安全分析、代理团队或代码审查。

Workflows allow you to dynamically create harnesses that enable Claude to solve all of those problems and more natively inside of Claude Code. You can also share and re-use these workflows with others.工作流允许您动态创建使Claude能够解决所有这些问题的线束，并且在Claude代码中更原生地解决这些问题。您还可以与其他人共享和重用这些工作流。

In this article, I’ll cover my initial workflows experiences and learnings so you can take full advantage. 在本文中，我将介绍我最初的工作流经验和学习，以便您可以充分利用。

That said, best practices are still developing! Dynamic workflows often use more tokens, so think carefully about when and how to use them. **Note**: this post is also 也就是说，最佳实践仍在发展中！动态工作流通常使用更多令牌，因此要仔细考虑何时以及如何使用它们。 注意：这篇文章也可以在克劳德博客上找到[available on the Claude Blog可以在克劳德博客上找到](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)

## Example prompts 例子提示

Before diving into the technical details, I’d like to start with some example prompts to get you thinking about the possibilities with workflows:在深入研究技术细节之前，我想从一些示例提示开始，让您思考工作流的可能性：

- "This test fails maybe 1 in 50 runs. Set up a workflow to reproduce it, form theories and adversarially test them in worktrees /goal don't stop until one theory works."这个测试可能在50次运行中失败1次。建立一个工作流程来复制它，形成理论并在工作树/目标中对抗性地测试它们，直到一个理论起作用为止。
- "Using a workflow, go through my last 50 sessions and mine them for corrections I keep making and turn the recurring ones into CLAUDE.md rules"使用工作流程，通过我最近的50次会议，挖掘他们的更正，我一直在做，并把反复出现的变成克劳德。md rules"
- “Use a workflow to dig through [#incidents #事件](https://x.com/search?q=%23incidents&src=hashtag_click) in Slack for the past six months and find recurring root causes where nobody has filed a ticket."&ldquo；使用工作流来挖掘过去六个月Slack中的事件，并找到没有人提交罚单的反复出现的根本原因。
- "Take my business plan and run a workflow where different agents tear it apart from an investor's, a customer's, and a competitor's perspective."“以我的商业计划为例，让不同的代理人从投资者、客户和竞争对手的角度来分析我的工作流程。”
- "Here's a folder of 80 resumes, use a workflow to rank them for the backend role and double-check the top ten. Interview me using the AskUserQuestion tool for a rubric."这是一个包含80份简历的文件夹，使用工作流对它们进行后端职位排名，并仔细检查前10名。使用AskUserQuestion工具对我进行采访。
- "I need a name for this CLI tool. Use a workflow to brainstorm a bunch of options and run a tournament to pick the top 3."我需要为这个CLI工具取一个名字。使用工作流程来集思广益，并举办一场比赛，选出前3名。
- "Use a workflow to rename our User model to Account everywhere."使用工作流将我们的User模型重命名为Account。
- “Go through my blog post draft and using a workflow verify every technical claim against the codebase, I don't want to ship anything wrong."浏览我的博客草稿，并使用工作流程验证代码库中的每个技术声明，我不想发布任何错误的内容。

## How dynamic workflows work动态工作流是如何工作的

Dynamic workflows execute a javascript file with a few special functions that help spawn and coordinate [subagents 子代理](https://code.claude.com/docs/en/sub-agents):动态工作流执行带有一些特殊功能的javascript文件，帮助生成和协调子代理：

![图像](https://pbs.twimg.com/media/HJ0t9PDbQAAYqh-?format=jpg&name=large)

Dynamic workflows also include standard JavaScript functions like JSON, Math, and Array, to help process data.动态工作流还包括JSON、Math和Array等标准JavaScript函数，以帮助处理数据。

It’s particularly useful to know that dynamic workflows can decide which models an agent uses and whether subagents are run in their own worktree, allowing Claude to choose the intelligence level and isolation needed.了解动态工作流可以决定代理使用哪些模型以及子代理是否在自己的工作树中运行，这一点特别有用，从而允许Claude选择所需的智能级别和隔离。

If a workflow is interrupted, for example by user action or quitting the terminal, resuming the session will allow the workflow to pick up where it left off.如果工作流被中断，例如由于用户操作或退出终端，恢复会话将允许工作流从中断的地方重新开始。

## Why dynamic workflows 为什么是动态工作流

When you ask the default Claude Code harness to do a task, it needs to both plan and execute in the same context window. For many coding tasks, this is highly effective, but it can sometimes break down over long-running, massively parallel and/or highly structured adversarial tasks.当您要求默认的Claude Code工具执行任务时，它需要在同一个上下文窗口中规划和执行。对于许多编码任务来说，这是非常有效的，但它有时会在长时间运行、大规模并行和/或高度结构化的对抗性任务中崩溃。

This is because the longer Claude works on a complex task in a single context window, the more it becomes susceptible to a few specific failure modes:这是因为Claude在单个上下文窗口中处理复杂任务的时间越长，它就越容易受到一些特定故障模式的影响：

- **Agentic laziness Agentic懒惰** refers to when Claude stops before finishing a particularly complex, multi-part task and declares the job done after partial progress, for example addressing 20 of the 50 items in a security review.指克劳德在完成一项特别复杂的多部分任务之前停下来，并在部分完成后宣布工作完成，例如处理安全审查中50项中的20项。
- **Self-preferential bias Self-preferential偏见**refers to Claude’s tendency to prefer its own results or findings, especially when asked to verify or judge them against a rubric.指克劳德倾向于自己的结果或发现，特别是当被要求根据一个标准来验证或判断它们时。
- **Goal drift 目标漂移**refers to the gradual loss of fidelity to the original objective across many turns, especially after compaction. Each summarization step is lossy, and details like edge-case requirements or "don't do X" constraints can get lost.指在许多回合中，特别是在压缩之后，对原始目标的保真度逐渐丧失。每个总结步骤都是有损的，像边缘情况需求或“不做x”约束这样的细节可能会丢失。

Creating a workflow helps combat these by orchestrating separate Claudes with their own context windows and focused, isolated goals.创建工作流可以通过编排具有自己的上下文窗口和集中的、孤立的目标的单独的claude来帮助解决这些问题。

## Dynamic vs static workflows动态与静态工作流

You may have previously created a static workflow using the Claude Agent SDK or claude -p to coordinate multiple instances of Claude Code together.您以前可能已经使用Claude Agent SDK或Claude -p创建了一个静态工作流来协调多个Claude Code实例。

But because static workflows need to work for all edge cases, they are usually more generic. With [Claude Opus 4.8 克劳德作品4.8](https://www.anthropic.com/news/claude-opus-4-8) and dynamic workflows, Claude is now intelligent enough to write a custom harness tailor-made for your use case.但是因为静态工作流需要适用于所有的边缘情况，所以它们通常更通用。有了Claude Opus 4.8和动态工作流，Claude现在足够智能，可以为你的用例编写定制的线束。

![图像](https://pbs.twimg.com/media/HJ1Dc3waUAA8Eeo?format=png&name=large)

# Helpful patterns when using dynamic workflows使用动态工作流时的有用模式

You can start using dynamic workflows just by asking Claude to make one, or by using the trigger word “ultracode” to ensure that Claude Code creates a workflow.你可以通过让Claude创建一个动态工作流来开始使用动态工作流，或者通过使用触发词ultrode&rdquo来确保Claude Code创建工作流。

But building a mental model for how dynamic workflows work will help you understand when to use them and how you might nudge Claude via prompts.但是，建立一个关于动态工作流如何工作的心智模型将帮助您了解何时使用它们以及如何通过提示来推动Claude。

There are a few common patterns that Claude might use and compose together when building workflows:在构建工作流时，Claude可能会使用和组合一些常见的模式：

![图像](https://pbs.twimg.com/media/HJ0u_2cbMAA3ufP?format=jpg&name=large)

**Classify-and-act**

Use a classifier agent to decide on the type of task, and then route to different agents or behavior based on the task. Or, use a classifier at the end to determine output.使用分类器代理来决定任务的类型，然后根据任务路由到不同的代理或行为。或者，在最后使用分类器来确定输出。

**Fan-out-and-synthesize**

Split up a task into many smaller steps, run an agent on each step and then synthesize those results. This is particularly useful for when there are a large number of smaller steps, or when each step benefits from its own clean context window so they don't interfere or cross-contaminate. The synthesize step is a barrier—it waits for all the fan-out agents, then merges their structured outputs into one result.将任务分成许多小步骤，在每个步骤上运行一个代理，然后综合这些结果。当有大量的小步骤时，或者当每个步骤都受益于自己的干净上下文窗口时，这一点特别有用，这样它们就不会相互干扰或交叉污染。合成步骤是一个障碍，它等待所有扇出代理，然后将它们的结构化输出合并为一个结果。

**Adversarial verification 敌对的验证**

For each spawned agent, run a separate spawned agent to adversarially verify its output against a rubric or criteria.对于每个生成代理，运行一个单独的生成代理，根据一个标题或标准对抗性地验证其输出。

**Generate-and-filter**

Generate a number of ideas on a topic and then filter them by a rubric or by verification, dedupe duplicates and return only the highest quality, tested ideas.在一个主题上产生一些想法，然后通过一个标题或验证来过滤它们，重复删除，只返回最高质量的，经过测试的想法。

**Tournament 比赛**

Instead of dividing the work, have agents compete on it. Spawn N agents that each attempt the same task using different approaches. Prompts or models then judge the results in a pairwise fashion using a judging agent until you have a winner.与其把工作分开，不如让代理人来竞争。刷出N个代理，每个代理使用不同的方法尝试相同的任务。然后，提示符或模型使用裁判代理以两两方式对结果进行评判，直到你选出获胜者。

**Loop until done 循环完成**

For tasks with an unknown amount of work, loop spawning agents until a stop condition is met (no new findings, or no more errors in the logs) instead of a fixed number of passes.对于工作量未知的任务，循环生成代理直到满足停止条件（没有新的发现，或者日志中没有更多错误），而不是固定次数的传递。

# Use cases 用例

Think creatively of when and how to ask Claude Code to make dynamic workflows. I’ve found that workflows are sometimes even more useful for non-technical work.创造性地思考何时以及如何要求Claude Code制作动态工作流程。我发现工作流有时对非技术工作甚至更有用。

![图像](https://pbs.twimg.com/media/HJ018ZjbcAA4nFm?format=png&name=large)

## Migrations and refactors 迁移和重构

[Bun](https://bun.com/) was rewritten from Zig to Rust using workflows. You can read more about how that was done in [Jarred’s X thread jared &rsquo；s X线程](https://x.com/jarredsumner/status/2060050578026189172).使用工作流将Bun从Zig重写为Rust。您可以在jared的X线程中阅读更多关于这是如何完成的。

The key is to break down the task into a series of steps that need to be operated on for example callsites, failing tests, modules, etc. Spin off a subagent for every fix in a worktree to make the fix, then have another agent adversarially review, and merge them. Consider telling the agent not to use resource intensive commands so that you can maximally parallelize without running out of resources on your machine.关键是将任务分解为一系列需要操作的步骤，例如调用站点、失败测试、模块等。为工作树中的每个修复都派生出一个子代理来进行修复，然后让另一个代理对抗性地检查，并合并它们。考虑告诉代理不要使用资源密集型命令，这样您就可以最大限度地并行化，而不会耗尽机器上的资源。

## Deep research 深入研究

We published a deep research skill (/deep-research) inside Claude Code that uses dynamic workflows. Specifically, it fans-out web searches, fetches sources, adversarially verifies their claims, and synthesizes a cited report.我们在Claude Code中发布了一个使用动态工作流的深度研究技能（/deep-research）。具体来说，它分散网络搜索，获取来源，对口验证他们的说法，并综合引用的报告。

But you may do this sort of research for more than just web searches. For example, asking Claude to compile a status report from context in Slack or to research how a feature works by exploring a codebase in-depth.但你可以做这类研究不仅仅是网络搜索。例如，让Claude从Slack的上下文中编译一份状态报告，或者通过深入探索代码库来研究一个功能是如何工作的。

## Deep verification 深验证

![图像](https://pbs.twimg.com/media/HJ0vMJ8acAAM9Uo?format=jpg&name=large)

On the other hand, if you have a report where you want to check and source every factual claim that it references you may want to generate a workflow which has one agent identify all of the factual claims and then spin off a subagent to check each one in-detail. You could also have a verification agent check the source subagent to make sure its source is high quality.另一方面，如果你有一个报告，你想要检查和来源它引用的每一个事实声明，你可能想要生成一个工作流，让一个代理识别所有的事实声明，然后派生出一个子代理来详细检查每一个。您还可以让验证代理检查源子代理，以确保其源是高质量的。

## Sorting 排序

![图像](https://pbs.twimg.com/media/HJ0wACFbMAAAvWl?format=jpg&name=large)

You may have a list of items that you want to sort by some qualitative measurement that you believe that Claude Code is good at evaluating, for example: support tickets sorted by severity of the bug. But if you try to sort 1000+ rows in one prompt, quality degrades and it won't fit in context. Instead run a tournament, a pipeline of pairwise-comparison agents (comparative judgment is more reliable than absolute scoring), or bucket-rank in parallel then merge. Each comparison is its own agent, so the deterministic loop holds the bracket and only the running order stays in context.您可能有一个项目列表，您希望通过一些您认为Claude Code擅长评估的定性度量对这些项目进行排序，例如：根据bug的严重程度对支持票据进行排序。但是，如果您尝试在一次提示中对1000行进行排序，则质量会降低，并且不适合上下文。取而代之的是举办一场锦标赛，一个由两两比较代理组成的管道（比较判断比绝对得分更可靠），或者并行排列，然后合并。每个比较都有自己的代理，因此确定性循环保留括号，只有运行顺序保留在上下文中。

## Memory and rule adherence记忆和规则遵守

![图像](https://pbs.twimg.com/media/HJ0wF76acAAyRMo?format=jpg&name=large)

If you have a particular set of rules that you find Claude misses or struggles with, even when put into the CLAUDE.mds, create a workflow with a list of rules that must be checked by verifier agents—one verifier per rule. Creating a skeptic persona subagent to review the rules to make sure they are in line will help avoid too many false positives.如果你有一个特定的规则，你发现克劳德错过或挣扎，即使把克劳德。创建一个带有规则列表的工作流，这些规则必须由验证者代理（每个规则有一个验证者）检查。创建一个持怀疑态度的角色子代理来审查规则，以确保它们是一致的，这将有助于避免太多的误报。

The reverse direction works too: mine your recent sessions and code review comments for corrections you keep making, cluster them with parallel agents, adversarially verify each candidate (would this rule have prevented a real mistake?), and then distill the survivors back into a [CLAUDE.md](http://claude.md/).相反的方向也可以：挖掘你最近的会话和代码审查评论，找出你一直在做的更正，将它们与并行代理聚类，对抗性地验证每个候选（这条规则是否可以防止真正的错误？），然后将幸存者提取回CLAUDE.md。

## Root-cause investigation 根源调查

Debugging works best when you come up with several independent hypotheses and test them, but if you’re only using one context window, Claude can run into self-preferential bias. A workflow can structurally prevent this by spinning up agents to generate hypotheses from disjoint evidence. For example, separate agents for logs, files, and data. Each hypothesis can then face a panel of verifiers and refuters.当您提出几个独立的假设并对它们进行测试时，调试效果最好，但如果您只使用一个上下文窗口，Claude可能会遇到自我偏好偏差。 工作流可以通过旋转代理从不一致的证据中生成假设，从结构上防止这种情况。例如，为日志、文件和数据使用单独的代理。然后，每个假设都要面对一组验证者和反驳者。

This isn't just for code. Workflows can be used for sales (why did sales drop in March?), data engineering (why did this pipeline fail?), or any post-mortem exercise.这不仅仅适用于代码。工作流可以用于销售（为什么3月份的销售额下降了？）、数据工程（为什么这个管道失败了？）或任何事后分析练习。

## Triaging at scale 大规模分诊

![图像](https://pbs.twimg.com/media/HJ0wNb8bUAA33h5?format=jpg&name=large)

Every team has a support queue, bug reports, or some other backlog that cannot be fully processed by humans.每个团队都有一个支持队列、错误报告或其他一些无法由人类完全处理的积压。

A triage workflow classifies each item, dedupes against what's already tracked, and takes action. This could mean attempting the fix or escalating to a human user.分类工作流程对每个项目进行分类，根据已经跟踪的内容进行重复，并采取行动。这可能意味着尝试修复或升级到人类用户。

A useful pattern for triage workflows is quarantine. This involves barring the agents that read untrusted public content from taking high-privilege actions, which are instead done by the agents in charge of acting on the information.分类工作流的一个有用模式是隔离。这包括禁止读取不受信任的公共内容的代理执行高权限操作，而由负责对信息执行操作的代理执行高权限操作。

Pair triage workflows with /loop to have Claude do this continuously.将分流工作流程与/loop配对，让Claude连续执行此操作。

## Exploration and taste 探索与品味

Workflows can be useful when exploring different approaches to a solution, especially when it is taste based, like design or naming, and would benefit from a rubric.在探索解决方案的不同方法时，工作流可能是有用的，特别是当它基于品味时，如设计或命名，并且将受益于标题。

Try asking Claude to explore a bunch of solutions, and give a review agent a rubric for what a good solution looks like. The task is complete when the review agent feels like it has met the criteria. Solutions can also be ordered or selected via a tournament based on the rubric.试着让克劳德探索一堆解决方案，并给一个审查代理人一个好的解决方案的标准。当审查代理觉得它符合标准时，任务就完成了。解决方案也可以通过基于规则的比赛来订购或选择。

## Evals

You can run lightweight evals for particular tasks by spinning off separate agents in a worktree and then spinning off comparison agents to compare and grade the specific outputs against a rubric. For example, evaluating and then refining a skill you’ve created against a particular criteria.您可以为特定任务运行轻量级的评估，方法是在工作树中分离单独的代理，然后分离比较代理，根据一个标题对特定的输出进行比较和分级。例如，根据特定的标准评估并改进你所创造的技能。

## Model and intelligence routing模型和智能路由

Create a classifier agent tuned to your tasks that decides which model to use. This can be helpful when your task will involve many tool calls and conducting research prior to execution can identify the best model for the job.创建一个针对任务进行调优的分类器代理，由其决定使用哪个模型。当您的任务将涉及许多工具调用时，这将非常有用，并且在执行之前进行研究可以确定工作的最佳模型。

For example, the best model for the task “explain how the auth module works” depends on how many files in the auth module there are and the shape of the codebase. A classifier agent can do this research and then route to Sonnet or Opus based on the expected complexity of the task.例如，解释验证模块如何工作的任务的最佳模型取决于验证模块中有多少文件以及代码库的形状。分类器代理可以完成这项研究，然后根据任务的预期复杂性路由到十四行诗或作品。

## When not to use dynamic workflows何时不使用动态工作流

Workflows are new. While there are many use cases where it will create outsized results, they are not needed for every task and may end up using significantly more tokens.工作流是新的。虽然在许多用例中，它会创建超大的结果，但并不是每个任务都需要它们，最终可能会使用更多的令牌。

It’s best to use workflows creatively to push Claude Code in ways that you haven’t previously. For regular coding tasks, try and ask yourself does it really need more compute? For example, most traditional coding tasks do not need a panel of 5 reviewers.最好是创造性地使用工作流，以您以前从未有过的方式来推动Claude Code。对于常规的编码任务，试着问问自己，它真的需要更多的计算吗？例如，大多数传统的编码任务不需要由5人组成的评审小组。

# Tips for building dynamic workflows构建动态工作流的技巧

**Prompting 促使**

Detailed prompting, using the specific techniques we described above, for dynamic workflows creates the best results.使用我们上面描述的特定技术，对动态工作流进行详细提示可以产生最佳结果。

Workflows are not just for large tasks. You can prompt the model to use a “quick workflow.” For example, you can create a quick adversarial review of an assumption.工作流不仅仅适用于大型任务。您可以提示模型使用快速工作流。例如，您可以创建一个假设的快速对抗性审查。

**Combine with /goal and /loop结合/goal和/loop**

When using workflows that can be repeated, for example triage, research, or verification, pair them with /loop to be run at regular intervals, and /goal to set a hard completion requirement.当使用可重复的工作流时，例如分类、研究或验证，将它们与/循环配对，以定期间隔运行，并/目标设置硬完成需求。

**Token usage budgets 令牌使用预算**

You can set explicit token usage budgets for dynamic workflows to limit how many tokens a task uses. You can prompt it with a budget like: “use 10k tokens,” which will set the cap.您可以为动态工作流设置显式令牌使用预算，以限制任务使用令牌的数量。您可以用这样的预算提示它：使用10k代币，这将设置上限。

**Saving and sharing dynamic workflows保存和共享动态工作流**

You can save workflows by pressing “s” in the workflow menu. You can check these into ~/.claude/workflows or distribute them via a skill.您可以通过在工作流菜单中按&ldquo； &rdquo；来保存工作流。您可以将这些签入~/。Claude /工作流或通过技能分发它们。

![图像](https://pbs.twimg.com/media/HJ0wWqbasAAcvgu?format=jpg&name=large)

To share them via a skill, put your JavaScript workflow files in the skill and folder and reference them in the [SKILL.MD 技能。医学博士](http://skill.md/). To allow for more flexibility, you may want to prompt Claude to think of the workflows in the skill as a template instead of a script that needs to be run verbatim.要通过技能共享它们，请将JavaScript工作流文件放在skill和文件夹中，并在skill . md中引用它们。为了获得更大的灵活性，您可能希望提示Claude将技能中的工作流视为模板，而不是需要逐字运行的脚本。

![图像](https://pbs.twimg.com/media/HJ0wbLFbIAAu2FH?format=jpg&name=large)

## A whole new world 一个全新的世界

Workflows are a helpful new way to extend Claude Code. I encourage you to think of this as a starting point, there's still much to discover in how to use them best. Let us know what you find.工作流是扩展Claude Code的一种有用的新方法。我鼓励你把这当作一个起点，在如何最好地使用它们方面，还有很多东西需要发现。让我们知道你发现了什么。

Thariq Shihipar and Sid Bidasaria ([@sidbid](https://x.com/@sidbid)) are members of technical staff at Anthropic, working on Claude Code.Thariq Shihipar和Sid Bidasaria （@sidbid）是Anthropic的技术人员，致力于《Claude Code》。