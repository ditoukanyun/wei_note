---
title: "Loops: What Every AI Engineer Needs to Know in 2026循环：2026年每个人工智能工程师需要知道的事情"
source: "https://x.com/sairahul1/status/2064277888216555684"
author:
  - "[[@sairahul1]]"
published: 2026-06-09
created: 2026-06-11
description: "Peter Steinberger, creator of OpenClaw, who now works with OpenAI.Peter Steinberger， OpenClaw的创始人，现在在OpenAI工作。Yesterday he posted this:昨天他发帖..."
tags:
  - "clippings"
---
![图像](https://pbs.twimg.com/media/HKTN8h6bQAAyMyQ?format=jpg&name=large)

![图像](https://pbs.twimg.com/media/HKTAqe3aMAE9yag?format=jpg&name=large)

Peter Steinberger, creator of OpenClaw, who now works with OpenAI.Peter Steinberger， OpenClaw的创始人，现在在OpenAI工作。

Yesterday he posted this:昨天他发帖说：

> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."您不应该再提示编码代理了。你应该设计循环来提示你的代理。

Then Boris Cherny, head of Claude Code at Anthropic, said the same thing differently:然后，Anthropic的Claude Code负责人Boris Cherny用不同的方式说了同样的话：

> "I don't prompt Claude anymore. I have loops running that prompt Claude and figure out what to do. My job is to write loops."我不再提示克劳德了。我有循环运行这个提示，克劳德，并找出该怎么做。我的工作是编写循环。

Two of the most senior AI engineers alive. Same message.两位最资深的人工智能工程师。同样的信息。

Most people read it and thought: what does that actually mean?大多数人读了之后会想：这到底是什么意思？

I went deep on it.我深入研究了一下。

Here is everything — broken down simply.这是对所有事情的简单分析。

No jargon. Just the mental model you need.没有术语。这正是你需要的心智模式。

Save this. It will change how you think about AI.保存这个。它将改变你对人工智能的看法。

## BUT FIRST: THE REASON MOST PEOPLE NEVER BUILD LOOPS但首先：大多数人从不建立循环的原因

> Loops sound great. Then you see the bill.循环听起来很棒。然后你看到账单。

![图像](https://pbs.twimg.com/media/HKW9OcNboAA4Iql?format=jpg&name=large)

Here is what nobody tells you upfront.这是没人会事先告诉你的。

A single agent loop on a medium coding task: 50,000–200,000 tokens.中等编码任务上的单个代理循环：50,000–200,000令牌。

A fleet loop with an orchestrator and 3 specialists: 500,000–2,000,000 tokens.一个由一个编排者和3个专家组成的舰队循环：500,000–2,000,000令牌。

A loop running on a schedule every morning: millions of tokens per week.每天早上按照时间表运行的循环：每周数百万代币。

At standard API pricing, a week of serious loop engineering costs more than most people's entire monthly AI budget.

This is why Peter Steinberger's replies were full of people saying: 这就是为什么Peter Steinberger的回复中满是这样的人：

> "Easy for you to say — you have unlimited OpenAI access."你说得很容易，你有无限的OpenAI访问权限。

They are not wrong. 他们没有错。

Loop engineering on a normal budget breaks fast.

Every retry costs. Every self-correction costs. Every subagent costs. Every verification pass costs.

The open loop that explores freely? Burns tokens at a rate that makes your eyes water.自由探索的开环？烧代币的速度快到让你流泪。

This is the hidden blocker nobody talks about.这就是没人谈论的隐藏障碍。

Loops are not hard to design.循环并不难设计。

They are hard to afford.他们很难负担得起。

That is exactly what Chinese LLMs solve.这正是中国法学硕士要解决的问题。

Models like **DeepSeek, Kimi, and MiniMax** make agent loops economically viable.像DeepSeek、Kimi和MiniMax这样的模型使得智能体循环在经济上可行。

The biggest problem with autonomous agents is not intelligence.自主代理最大的问题不是智能。

It is **token burn**. 这是象征性的燃烧。

Loops consume tokens fast.循环消耗令牌的速度很快。

A single run can easily burn **50K–200K tokens**.一次运行可以轻松地消耗50K&ndash；200K代币。

Run multiple agents, schedule loops daily, or work on large codebases — and costs spiral quickly.运行多个代理，每天安排循环，或者在大型代码库上工作，成本就会迅速上升。

This is where **DeepSeek changes the equation**.这就是DeepSeek改变等式的地方。

DeepSeek V4 is currently one of the **cheapest frontier-level models for running loops at scale**.DeepSeek V4是目前用于大规模运行循环的最便宜的前沿级模型之一。

What you get: 你会得到什么：

→ **1M context window** — built for large projects and long-running workflows → **384K max output** — handles bigger generations without breaking → **DeepSeek V4 Flash + Pro models** → **Extremely low token pricing** → **Tool calls + JSON output** for agent workflows → **High concurrency** (up to 2500 requests on Flash)

Why the **1M context window** matters:

Loops need memory.

A coding loop working on a large project needs to keep:

— previous runs — current errors — architecture docs — test results — codebase context

all in memory at the same time.

Most models lose context midway.

Your loop starts forgetting what happened earlier.

DeepSeek holds significantly more context, so long-running loops stay coherent.

And because pricing is so low:

**Loops stop breaking the bank.**

## PART 1: THE OLD WAY VS THE NEW WAY

**For the last two years, we prompted agents one task at a time.**

![图像](https://pbs.twimg.com/media/HKTISKSboAA2OUN?format=jpg&name=large)

You type a prompt. The agent responds. You review it. You fix what is wrong. You prompt again. You are the loop.

That is starting to change.

Instead of asking an agent to build a landing page and then driving every step yourself, you set up a loop that handles discovery, planning, the work, checking, and iterating — until the goal is met.

The difference:

**Old way (prompting):**

You → Prompt → Agent → Output → You review → You fix → Repeat

**New way (looping):**

You set the goal → Loop runs → Agent discovers → Plans → Executes → Verifies → Iterates → Done

You are not prompting each step anymore.

The agent repeats the cycle for you.

A prompt gives the agent instructions.

A loop gives the agent a job.

## PART 2: WHAT LOOP ENGINEERING ACTUALLY IS

![图像](https://pbs.twimg.com/media/HKTIO2caMAEvMoS?format=jpg&name=large)

Loop Engineering is the practice of designing repeatable feedback

cycles that guide AI agents from attempt to verified outcome —

without constant human intervention.

Looping is a setup you build.

Almost any agent harness can run it.

It just depends on how you wire it up.

At its simplest, one agent works on itself:

→ Researches

→ Drafts

→ Checks the draft against a goal

→ Fixes what is weak

→ Runs that cycle again until the work clears the requirements

Every loop — no matter how simple or complex — moves through

the same 5 stages:

DISCOVER → PLAN → EXECUTE → VERIFY → ITERATE

Pass verification → ship.

Fail verification → loop again.

That is the whole idea.

Everything else in this article is just how you build that cycle properly.

## PART 3: ONE AGENT VS A FLEET

**There are two scales of looping:**

![图像](https://pbs.twimg.com/media/HKTIW_laoAAenV9?format=jpg&name=large)

**SINGLE-AGENT LOOP**

One agent runs the whole cycle on its own.

Think of it like a person redoing their own draft.

It discovers what is needed, plans the work, executes, verifies quality, and iterates if something is wrong.

Good for:

→ Focused tasks

→ Simple goals

→ Limited scope

One brain. One loop. Self-improving.

━━━

**FLEET LOOP**

The bigger version is a fleet looping.

You give an orchestrator agent a goal.

It breaks the goal into pieces.

Hands each piece to a specialist agent.

Those specialists hand smaller jobs to their own subagents.

The whole tree keeps looping through discovery, planning, execution, and verification — until the goal is met.

Think of it like a whole team running a project end-to-end.

The structure:

→ Orchestrator owns the goal

→ Specialists own the steps

→ Subagents do the narrow work

→ Eval gates make sure it is not slop

Example: "Build a productivity app"

> Orchestrator (owns the mission) ↓ ↓ ↓ Research Engineering QA Specialist Specialist Specialist ↓ ↓ ↓ Web Code Writer Test Writer Researcher + Debugger + Bug Tracker

Every agent in the tree runs the same 5-stage loop.

Discover → Plan → Execute → Verify → Iterate.

The important thing:

A single-agent loop is like a person redoing their own draft.

A fleet loop is a whole team running a project end-to-end.

## PART 4: OPEN LOOPS VS CLOSED LOOPS

**This is the most important practical distinction in 2026:**

![图像](https://pbs.twimg.com/media/HKTIaMEbEAAiGoa?format=jpg&name=large)

Not all loops are equal.

There are two types.

**OPEN LOOPING**

Exploratory. Wide space to move in.

You give the agent a goal and let it roam.

It can try different paths, discover things, build something you did not fully spec out.

This is the exciting end. It is what Peter Steinberger and others are doing at OpenAI.

The catch?

It burns an insane amount of tokens.

For the 90% of people without unlimited API budgets, open looping is not practical yet.

Pointed at projects with loose standards, it turns into a slop machine.

Fast. Messy. Expensive.

**CLOSED LOOPING**

Bounded. A human designs the end-to-end path first.

→ Clear goal

→ Defined steps

→ An evaluation at each step

→ A point where it stops or hands back to you

The agents still loop — but inside a framework you built.

It gets better every run because each pass feeds the next.

It runs on a normal budget because the path is tight.

The standard keeps it honest.

Without a quality gate: AI drifts.

With a quality gate: AI improves.

For most real work today, closed looping is the one that pays off.

**Which one should you use?**

Start with closed loops.

Build a tight system that works reliably.

Then open it up once you have the quality gates.

## PART 5: THE 6 BUILDING BLOCKS OF EVERY GOOD LOOP

**Every loop that holds together has these 6 things:**

![图像](https://pbs.twimg.com/media/HKV1afKbcAAzTGw?format=jpg&name=large)

Now the practical part.

A loop has 5 stages conceptually.

But what do you actually build to make it run?

6 things. Both Claude Code and Codex ship all of them now.

Here they are — and what each one is really doing inside the loop.

**1\. AUTOMATIONS**

This is what triggers DISCOVER and kicks the loop into motion.

The heartbeat of the loop.

An automation is what makes a loop an actual loop — and not just one run you did once.

You define a prompt, a cadence, and a goal.

The loop runs on schedule. Findings come to you. You are not the one going around checking.

→ /loop re-runs on a cadence

→ /goal keeps going until a condition you wrote is actually true

Give it: "all tests in test/auth pass and lint is clean."

Walk away.

**2\. WORKTREES**

This is what lets multiple EXECUTE stages run in parallel without breaking each other.

Parallel agents without chaos.

The second you run more than one agent, files start colliding.

Two agents writing the same file is the same problem as two engineers committing to the same lines without talking.

A git worktree gives each agent its own isolated working directory on its own branch — same repo history, zero collisions.

One agent's edits literally cannot touch the other's checkout.

**3\. SKILLS**

This is what makes DISCOVER faster — the agent already knows your project before it starts.

Stop explaining your project from zero every run.

A skill is a folder with a SKILL.md inside — project conventions, build steps, the "we don't do it this way because of that incident."

Written once. Read every loop.

Without skills: the loop re-derives your whole project from zero every cycle.

With skills: it compounds. The agent knows your project before it starts.

→ VISION.md — what success looks like

→ ARCHITECTURE.md — the tech stack and folder structure

→ RULES.md — what the agent is never allowed to do

**4\. PLUGINS AND CONNECTORS**

This is what makes EXECUTE real — the loop acts in your actual environment, not just your filesystem.

A loop that can only see the filesystem is a tiny loop.

Connectors (built on MCP) let the agent read your issue tracker, query a database, hit a staging API, drop a message in Slack.

This is the difference between an agent that says "here is the fix" and a loop that opens the PR, links the Linear ticket, and pings the channel once CI is green — by itself.

**5\. SUBAGENTS**

This is what makes VERIFY honest — the checker is never the same agent as the maker.

Keep the maker away from the checker.

The model that wrote the code is too nice grading its own homework.

A second agent with different instructions — sometimes a different model — catches the stuff the first one talked itself into.

The split that works:

→ One agent explores

→ One agent implements

→ One agent verifies against the spec

This is also what /goal does under the hood.

A fresh model decides if the loop is done — not the one that did the work.

**6\. MEMORY**

This is what makes the loop persistent — DISCOVER on run 47 knows everything runs 1 through 46 already tried.

The spine of the whole loop.

A markdown file. A Linear board. Anything that lives outside the single conversation.

The model forgets everything between runs.

The repo does not.

The memory file holds: what got tried, what passed, what is still open.

Tomorrow morning the loop picks up where today stopped.

It sounds too simple to matter.

Every long-running loop depends on it.

## PART 6: REAL LOOP EXAMPLES

**What loops look like in practice:**

![图像](https://pbs.twimg.com/media/HKV0CkPboAADGHg?format=jpg&name=large)

**The Coding Loop**

```plaintext
Read VISION.md + ARCHITECTURE.md
↓
Plan the next change
↓
Edit the code
↓
Run tests automatically
↓
If tests fail → read error → fix → retest
↓
If tests pass → summarize changes
↓
Stop
```

No human in the middle.

The agent writes, tests, fixes, and verifies on its own.

━━━

**The Research Loop**

```plaintext
Define research question
↓
Search for sources
↓
Summarize findings
↓
Verify claims against sources
↓
Compare conflicting information
↓
Synthesize final answer
↓
Stop when confidence threshold met
```

━━━

**The Content Loop**

```plaintext
Topic + audience + goal defined
↓
Draft created
↓
Critique agent reviews draft
↓
Rewrite based on critique
↓
Score against success criteria
↓
If score passes → publish
↓
If score fails → rewrite again
```

━━━

**The Sales Outreach Loop**

```plaintext
ICP (Ideal Customer Profile) defined
↓
Find leads matching profile
↓
Enrich with company data
↓
Qualify against criteria
↓
Personalize message
↓
Quality review
↓
Send or escalate to human
```

Every loop has the same skeleton:

Goal → Action → Check → Fix → Repeat until done.

## PART 7: PROMPT ENGINEER VS LOOP ENGINEER

**The skill gap opening up in 2026:**

![图像](https://pbs.twimg.com/media/HKTKaUab0AAIlU7?format=jpg&name=large)

**Prompt Engineer**

→ Craft better instructions

→ Linguistic skill

→ Better prompt

→ better single output

→ Still reviews output manually after every run

→ You are the feedback loop

**Loop Engineer**

→ Design better feedback cycles

→ Software engineering skill

→ Better loop

→ reliable verified outcomes

→ System runs, checks, and self-corrects

→ The system is the feedback loop

Prompt Engineer -> "Write me a function"

Loop Engineer -> "Write → test → fix until green"

Writes better prompts Writes VISION.md Reviews output manually Tests review automatically Runs agent once Builds repeating system Pays per single output Pays for verified outcome

The tools are the same.

The mindset is completely different.

Prompt engineers ask AI for output.

Loop engineers design systems that produce verified outcomes.

The highest-paid AI engineers in 2026 are not writing better English sentences.

They are writing the logic that governs how agents discover, plan, check their own work, and know when they are done.

![图像](https://pbs.twimg.com/media/HKTKkvLbwAAKXPq?format=jpg&name=large)

## CLOSING

That is Loop Engineering.

Let me recap everything:

**The shift:**

→ For two years we prompted agents one task at a time → Now we design loops that run the whole cycle

**The 6 things you actually build:**

→ Automations — the heartbeat, triggers discovery

→ Worktrees — parallel agents without collisions

→ Skills — project knowledge that compounds every run

→ Plugins and connectors — loop acts in your real tools

→ Subagents — maker and checker are never the same agent

→ Memory — loop never forgets between runs

**Two scales:**

→ Single agent: one brain, self-improving

→ Fleet: orchestrator + specialists + subagents — every agent runs the same loop

**Two types:**

→ Open loop: exploratory, powerful, expensive, needs unlimited budget

→ Closed loop: bounded, reliable, affordable, the one that pays off today

**The 5 parts of every good loop:**

→ Goal — define what done means precisely

→ Context — VISION.md, ARCHITECTURE.md, RULES.md

→ Action — only what the agent actually needs

→ Feedback — tests, type checks, linters, structured errors

→ Stop condition — when the loop knows it's finished

**The cost problem:**

→ Loops burn tokens fast

→ $20 on DeepSeek goes dramatically further than most frontier models

→ That removes the last real blocker

**The big shift:**

→ Prompt engineers ask AI for output

→ Loop engineers design systems that produce verified outcomes

Peter Steinberger said it right:

Stop prompting your agents.

Start designing loops.

Because one reliable loop is worth a thousand perfect prompts.

One more thing nobody says out loud.

Two people can build the exact same loop and get completely opposite results.

One uses it to move faster on work they understand deeply.

The other uses it to avoid understanding the work at all.

The loop does not know the difference.

You do.

That is what makes loop design harder than prompt engineering — not easier.

Boris Cherny's point is not that the work got easier.

It is that the leverage point moved.

Build the loop.

But build it like someone who intends to stay the engineer — not just the person who presses go.

Because one reliable loop is worth a thousand perfect prompts.

And with 1.7 billion tokens for $20, you can finally afford to build one.

If this helped:

→ Repost to share with your network

→ Follow [@sairahul1](https://x.com/@sairahul1) for more breakdowns like this

→ Bookmark this — the 5-part framework is worth revisiting

I write about AI, building products, and systems that run while you sleep.