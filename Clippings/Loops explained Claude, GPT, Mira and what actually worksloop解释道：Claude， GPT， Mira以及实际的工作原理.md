---
title: "Loops explained: Claude, GPT, Mira and what actually worksloop解释道：Claude， GPT， Mira以及实际的工作原理"
source: "https://x.com/AnatoliKopadze/status/2068328135611822149"
author:
  - "[[@AnatoliKopadze]]"
published: 2026-06-20
created: 2026-06-22
description: "AI has been in everyone's hands for years. Most people who use it every day still use it the slowest way there is: type a request, wait, fix..."
tags:
  - "clippings"
---
![图像](https://pbs.twimg.com/media/HLQR6x3WgAAoX0v?format=jpg&name=large)

AI has been in everyone's hands for years. Most people who use it every day still use it the slowest way there is: type a request, wait, fix it, ask again, all by hand.人工智能已经在每个人手中很多年了。大多数每天使用它的人仍然以最慢的方式使用它：输入一个请求，等待，修复它，再次请求，所有这些都是手工的。

Not because the faster way is complicated, because nobody showed them what it looks like.不是因为更快的方法复杂，而是因为没有人给他们展示它的样子。

The faster way is a loop, and right now it is the one thing the best AI engineers in the world care about. This article fixes the part nobody explained. By the end you will understand loops better than almost anyone on your timeline: what they are, how they actually work under the hood, when they are worth it and when they are a trap, how to build a basic one yourself in Claude or ChatGPT, the simple ones worth running in your own life.更快的方法是循环，现在这是世界上最好的人工智能工程师关心的一件事。这篇文章修复了没人解释的部分。 到最后，你将比你的时间表上的几乎任何人都更了解循环：它们是什么，它们实际上是如何在引擎盖下工作的，它们何时值得使用，何时是陷阱，如何在Claude或ChatGPT中构建一个基本的循环，简单的值得在你自己的生活中运行。

Before we get into it, follow me on X and join my Telegram channel I just created where I post more AI content every day. Both are free.在我们开始之前，请在X上关注我，并加入我刚刚创建的Telegram频道，我每天都会在那里发布更多人工智能内容。两者都是免费的。

X - [https://x.com/AnatoliKopadze](https://x.com/AnatoliKopadze)

Telegram - [https://t.me/kopadzemp](https://t.me/kopadzemp)

## How most people use AI?大多数人是如何使用人工智能的？

Look closely at the one-request-at-a-time habit, because it is the whole problem. Every step runs through you. You decide what to ask, you judge the answer, you decide what comes next. The AI never moves unless you push it, and the moment you stop, it stops.仔细看看一次一个请求的习惯，因为这是整个问题。每一步都要经过你。你决定问什么，你判断答案，你决定接下来要做什么。除非你推动它，否则AI永远不会移动，当你停下来的时候，它也会停止。

This is fine, but it has a ceiling. You are the engine. The AI is only the tool in your hand, and a tool does nothing on its own.这很好，但它有一个上限。你是引擎。人工智能只是你手中的工具，而工具本身并不能做任何事情。

There is another way to work, and it is the reason the best engineers in the world are changing how they build. Instead of walking the AI through every step, you give it the goal once and let it run the steps itself. It plans, does the work, checks its own result, fixes what is weak, and repeats until the goal is met. You step out. The work keeps going.还有另一种工作方式，这就是为什么世界上最好的工程师正在改变他们的建造方式。比起引导AI完成每一步，你只需要给它设定一次目标，然后让它自己执行每一步。它计划，完成工作，检查自己的结果，修复弱点，然后重复，直到达到目标。你走出去。工作还在继续。

> 6月8日
> 
> 这是你的月度提醒：你不应该再提示编码代理了。 你应该设计循环来提示你的代理。

<video preload="none" tabindex="-1" playsinline="" aria-label="嵌入式视频" poster="https://pbs.twimg.com/amplify_video_thumb/2068028099128643584/img/WqoEwyrbdk15hRD7.jpg" style="width: 100%; height: 100%; position: absolute; background-color: black; top: 0%; left: 0%; transform: rotate(0deg) scale(1.005);"><source type="video/mp4" src="blob:https://x.com/608abcb2-ab8a-41cc-b277-a388ec3aef17"></video>

0:01 / 0:08

Two of the most respected engineers, saying the same thing in different words. Most people read lines like these and quietly had no idea what they meant in practice. So let's break it down properly.两位最受尊敬的工程师，用不同的语言说同样的事情。大多数人读到这样的句子，却不知道它们实际上是什么意思。让我们把它分解一下。

## What a loop is? 什么是循环？

A prompt is a single instruction. A loop is a goal the AI keeps working toward until it gets there. Think of it as a recursive goal: you define a purpose, and the AI iterates until it is complete.提示符是一条指令。循环是AI不断努力的目标，直到达到目标为止。可以把它看作一个递归目标：你定义一个目的，AI迭代直到它完成。

A prompt gives you one answer and then waits for you to decide what is next. A loop runs the full cycle on its own:提示给你一个答案，然后等待你决定下一步是什么。一个循环自己运行完整的循环：

```text
DISCOVER  →  work out what needs doing
PLAN      →  decide how to do it
EXECUTE   →  do the work
VERIFY    →  check it against the goal
ITERATE   →  not there yet? feed the result back in and repeat
```

Three of these five do all the real work, and they are where people get loops wrong.这五种方法中的三种完成了所有的实际工作，而这正是人们犯循环错误的地方。

**Verify is the heart of the loop.验证是这个循环的核心。** Without a real check on the result, you do not have a loop, you have the agent agreeing with itself on repeat. The check is what turns repetition into progress. It can be a hard test ("does the code pass"), a measurable condition ("is the number above X"), or a rubric the model scores against. No gate means the agent grades its own homework, and the model that did the work is far too generous a grader.如果没有对结果进行真正的检查，你就没有一个循环，你让代理重复地同意自己。检查将重复转化为进步。它可以是一个困难的测试（“代码是否通过了”），一个可测量的条件（“是x上面的数字”），或者一个模型评分的标准。没有门意味着智能体给自己的作业打分，而完成作业的模型对评分者来说太慷慨了。

**State is what makes the loop learn.状态是让循环学习的东西。** Each pass, the AI has to remember what it already tried, or it repeats the same mistake forever. A real loop keeps a small record on the side: what is done, what failed, what is next. Tomorrow's run resumes instead of starting from zero. This is also exactly where it starts getting expensive, which we will get to.每次通过，AI都必须记住它已经尝试过的内容，否则它就会永远重复同样的错误。真正的循环会在旁边保存一个小记录：做了什么，失败了什么，下一步是什么。明天的比赛会继续，而不是从零开始。这也是它开始变得昂贵的地方，我们会讲到的。

**A stop condition is what keeps it sane.停止条件使它保持理智。** A loop with no exit runs until it succeeds, breaks, or drains your account. Every serious loop has two ways to stop: success, and a hard limit ("after 8 tries, stop and report"). Skip this and you have built a machine that can run all night for nothing.一个没有出口的循环会一直运行，直到它成功、中断或耗尽你的账户。每个严重循环都有两种停止方式：成功和硬限制（“尝试8次后，停止并报告”）。跳过这一步，你就制造了一台可以免费运行一整晚的机器。

A prompt hands the AI an instruction. A loop hands the AI a job, a way to know when the job is done, and a rule for when to give up.提示符会给AI一个指令。循环将交给AI一项任务，一种知道任务何时完成的方法，以及何时放弃的规则。

## Do you even need one?你真的需要吗？

Most articles sell you the loop before they tell you when it is a mistake. Here is the test the serious people actually use. A loop is worth building only when all four of these are true:大多数文章在告诉你这是一个错误之前就向你推销了这个循环。这是严肃人士实际使用的测试。只有当这四个条件都满足时，循环才值得构建：

- **The task repeats, at least weekly.这个任务至少每周重复一次。** Less than that and the setup cost never pays itself back. A one-off is still better served by one good prompt.低于这个数字，设置成本就永远无法收回。一次性的事情最好有一个好的提示。
- **Something can automatically reject bad output.有些东西可以自动拒绝不良输出。** A test, a type check, a build, a linter, a hard rule. If nothing can fail the work for you, the loop just spins.一个测试，一个类型检查，一个构建，一个检查，一个硬规则。如果没有什么能让你的工作失败，那么这个循环就会旋转。
- **The agent can actually do the work itself,代理可以自己完成工作，** end to end, not hand half of it back to you.首尾相连，不把一半还给你。
- **"Done" is objective, not a judgment call.“完成”是客观的，而不是主观的。** If quality is a matter of taste, a human still wins.如果质量是品味的问题，人类仍然是赢家。

Miss one box, keep it as a manual prompt. The honest version of this whole topic: loop engineering is real, and most people do not need the heavy version yet. **What everyone can use is the light version, which we will get to.** But you should know where the line is.漏掉一个盒子，保留它作为手动提示。这个话题的真实版本是：循环工程是真实存在的，大多数人还不需要这个沉重的版本。每个人都能使用的是轻量级版本，我们会讲到的。但你应该知道底线在哪里。

## The version built for code为代码构建的版本

Loops took off in software first, because code is the easiest thing in the world to verify. A test passes or it fails. There is no arguing with it, so the AI always knows whether it is finished.循环首先在软件中流行起来，因为代码是世界上最容易验证的东西。测试通过或失败。这是毋庸置疑的，所以AI总是知道它是否完成了。

A coding loop is given a goal and a strict way to check it:一个编码循环有一个目标和严格的检查方法：

```text
▸ LOOP SPEC
GOAL: every test in /tests/auth passes, lint is clean, no type errors.

EACH ITERATION:
  1. run the test suite and read every failure
  2. pick the single highest-impact failure
  3. write the smallest change that fixes it
  4. re-run the tests, lint, and type checker

VERIFY: green tests + zero lint warnings + zero type errors
STOP WHEN: verify passes, OR 8 iterations reached
ON STOP: summarize what changed and what still fails
```

Under the hood, a real loop is assembled from five building blocks. Claude Code and Codex now ship all five.在引擎盖下，一个真正的循环是由五个构建模块组装而成的。Claude Code和Codex现在提供所有五种。

**1\. The automation (the heartbeat)1. 自动化（心跳）**

This is the trigger that makes it a loop and not a one-off you ran once. You define a prompt, a cadence, and a goal, and it runs on schedule without you starting it. In Claude Code, /loop re-runs a prompt on an interval, /goal keeps a session going until a condition you wrote is actually true, hooks fire commands at points in the agent's lifecycle, and pushing it to a cron job or GitHub Actions keeps it running after you close the laptop. Findings come to you. You are not the one going around checking.这是一个触发器，使它成为一个循环，而不是你运行一次的一次性。你定义了一个提示、一个节奏和一个目标，它就会按计划运行，而不需要你启动它。在Claude Code中，/loop以间隔重新运行提示，/goal保持会话运行，直到您编写的条件实际为真，在代理生命周期中的点上钩子触发命令，并将其推送到cron作业或GitHub Actions，使其在关闭笔记本电脑后继续运行。你会发现。你又不是那个到处检查的人。

**2\. The skill (reusable instructions)2. 技能（可重用指令）**

Instead of pasting a wall of instructions into every run, you save them once as a file the loop reads every time: the rules, the patterns to follow, and a hard list of what it must never touch. Now the automation just calls the skill by name, and the recurring job stays maintainable instead of rotting inside a schedule nobody updates.您不必在每次运行时都粘贴一大堆指令，而是将它们保存为循环每次读取的文件：规则、要遵循的模式以及绝不能触及的内容的硬列表。现在，自动化只是通过名称调用技能，重复出现的工作保持可维护，而不是在没有人更新的时间表中腐烂。

**3\. Sub-agents (keep the maker away from the checker)3. 子代理（使制造商远离检查者）**

The single most useful structural trick in a loop is splitting the agent that does the work from the agent that checks it. The model that wrote the code is too nice grading its own homework. A second agent, with different instructions and sometimes a stronger model on higher effort, catches the things the first one talked itself into. Your writer can be fast and cheap, your reviewer slow and strict. That separation is most of the quality.循环中最有用的结构技巧是将执行工作的代理与检查工作的代理分开。编写代码的模型对自己的作业评分太好了。第二个智能体，有不同的指令，有时是更强大的模型，更努力，捕捉到第一个智能体说服自己的东西。你的作者可以是快速和廉价的，你的审稿人是缓慢和严格的。这种分离是最重要的品质。

**4\. Connectors (so it acts, not suggests)4. 连接器（因此它起作用，而不是建议）**

This is the difference between an agent that says "here is the fix" and a loop that opens the pull request, links the ticket, and pings the channel once the build is green, by itself. Connectors are what let the loop act inside your real environment instead of just describing what it would do if it could.这就是说“这是修复”的代理与打开拉取请求、链接票证并在构建绿色后ping通道的循环之间的区别。连接器让循环在您的真实环境中发挥作用，而不是仅仅描述它可能会做什么。

**5\. The verifier (the gate)5. 验证者（门）**

The test, type check, or build that automatically rejects bad work. This is the one block that decides whether the loop helps you or just spends your money. Everything else is plumbing. This is the part that makes it real.自动拒绝不良工作的测试、类型检查或构建。这是决定循环是帮助你还是只是花你的钱的一个块。其他的都是管道。这是让它变得真实的部分。

Stack those together and you get what big teams now run at scale: fleets of agents looping on the same job, dozens or thousands at once. One engineer used a loop like this to rewrite an entire codebase from one programming language to another in about six days, work that would have taken close to a year by hand. It is a genuine change in how serious software gets built. And it comes with a catch the demos never show.把这些加在一起，你就得到了现在大团队规模运行的东西：一群代理同时循环执行同一项任务，几十个或几千个。一位工程师使用这样的循环在六天内将整个代码库从一种编程语言重写为另一种编程语言，而手工完成这项工作可能需要近一年的时间。这是严肃软件构建方式的真正改变。它附带了一个从未展示过的陷阱。

## The cost nobody mentions 没有人提到成本

Loops run on tokens, and tokens are money. The problem is not that each step costs something. The problem is how the cost compounds.循环运行在代币上，而代币就是货币。问题不在于每一步都有成本。问题是成本是如何增加的。

Every time the loop goes around, the agent re-reads its context: the goal, the code, the last result, what failed. That whole pile is sent through the model again on every iteration, and it grows each pass. A loop that runs ten times does not cost ten prompts. It costs ten prompts that each keep getting bigger. The maker-and-checker trick that lifts quality also doubles the bill, because now two models read the work instead of one.每次循环进行时，代理都会重新读取其上下文：目标、代码、最后的结果、失败的内容。整个堆在每次迭代时都会再次通过模型，并且每次迭代都会增长。一个循环运行10次并不需要10次提示。它需要十个提示符，每个提示符不断变大。提高质量的“制造者和检查者”的把戏也使费用翻了一倍，因为现在有两个模特来阅读作品，而不是一个。

```text
▸ ROUGH COST OF ONE LOOP
single agent, one medium task:      ~50,000 – 200,000 tokens
context re-sent every iteration:    grows each pass
a fleet of agents in parallel:      multiply all of the above
```

The metric that actually matters, and almost nobody tracks, is cost per accepted change. Not tokens spent or loops run. If the loop gives you ten results and you toss six, you are doing the review work it was meant to save. Below a 50% accept rate, it costs more than it gives back.真正重要的度量，几乎没有人跟踪，是每个可接受的更改的成本。不使用令牌或运行循环。如果循环给你10个结果，而你丢弃了6个，那么你就是在做审查工作。如果接受率低于50%，则成本大于回报。

Loops also fail quietly. Engineer Geoffrey Huntley calls it the "Ralph Wiggum loop": the agent decides it is done too early, exits on a half-finished job, and the loop keeps running and spending while producing nothing. Without a hard gate that can fail the work, loops do not crash, they bill you in silence.循环也会悄然失效。工程师杰弗里·亨特利将其称为“拉尔夫·维格姆循环”：代理认为它完成得太早，在完成一半的工作时退出，循环继续运行，在没有产出的情况下消费。如果没有一个可以使工作失败的硬门，循环就不会崩溃，它们会无声地向你收费。

That is why the heavy version belongs to teams with the budget and guardrails to run it: iteration caps, token budgets, cheap models on the boring steps, monitoring. If that is not you, you are not missing out, the core idea works at a fraction of the cost and none of the setup.

## The order that actually works

If you do build one, the order matters more than the tools. The people who ship loops that survive in production all do it the same way:

```text
1. Get ONE manual run reliable first.
2. Turn that into a skill (save the instructions).
3. Wrap the skill in a loop (add the gate + stop condition).
4. THEN put it on a schedule.
```

Skipping ahead, scheduling something you have not made reliable by hand, is exactly how loops blow up while you sleep. Prove it once, harden it, then automate it.

## Build a basic loop yourself (any LLM)

You do not need a coding agent to feel how this works. You can run a simple loop by hand inside any LLM right now, with nothing but a prompt. The trick is to give the model all three loop parts at once: a goal, strict success criteria, and a protocol that forces it to check itself before it is allowed to stop.

```text
▸ SELF-CHECKING LOOP  (paste into Claude or ChatGPT)
You will work in a loop until the task meets the bar.

TASK:
[describe exactly what you want produced]

SUCCESS CRITERIA (be strict, no soft passes):
- [criterion 1]
- [criterion 2]
- [criterion 3]

LOOP PROTOCOL, repeat every turn:
1. PLAN   - state the single next step.
2. DO     - produce or improve the work.
3. VERIFY - score the result 1-10 on each criterion.
            Be brutally honest. List exactly what is still weak.
4. DECIDE - if every criterion is 8+, print "FINAL" and stop.
            Otherwise print "ITERATING" and go again, fixing
            the weakest point first.

RULES:
- Never call it done until every criterion is 8 or higher.
- Each pass must fix the weakest score from the last VERIFY.
- Do not ask me questions. Make a sensible assumption, note it,
  and keep going.

Begin. Run the loop until FINAL.
```

Watch what happens. The model drafts, grades its own work against your criteria, finds the weak spot, and rewrites, over and over, until it actually clears the bar instead of handing you the first thing that looked close. That is a loop. You just built one with a paragraph.

But notice what is still missing, because it is the whole point of what comes next. You are the trigger. You opened the chat, you pasted the prompt, you are sitting there watching it iterate. Close the tab and it is gone. There is no schedule. There is no "do this every morning," no "wake up when an email arrives." It cannot reach out to you, because it only exists while you are looking at it.

To get a loop that runs on its own, on a schedule, triggered by real events, without you babysitting it, you normally have to step into the heavy world from earlier: tools, hosting, code, gates, and a bill.

That makes sense when you are tackling genuinely heavy tasks. But for 99% of everyday ones, there is already a ready, dead-simple solution.

## The same idea, for your actual life

Strip away the code and the cost, and what is left is one simple, genuinely useful concept: a task that runs itself, on a schedule or the moment something happens, with no need for you to remember it or be there. You do not need to be an engineer for that. You just need loops built for life instead of for codebases.

There is a free option where you create one by describing it in plain words. No code, no hosting, no keys, no tab to keep open, no build order to get wrong.

It is called Mira, and it lives inside Telegram, the app you probably already have open. You message it like a friend, and the loops it runs are called Skills. Every Skill quietly has the same parts a real loop needs, a trigger, an action, a way to run by itself, except you never wire any of them together. You just say what you want.

```text
▸ SKILL
"Every weekday at 7am, check my Gmail and Google Calendar.
Send me a short brief: my 3 most important meetings, anything
urgent in the inbox, and one thing I said I'd follow up on but
haven't. Keep it under 120 words."
```

That is a real loop. A time trigger, a multi-step action across two connected apps, running on its own and coming to you. You wrote it as one message.

## What Mira can actually do

Here is the part that makes it click. Mira is not a smarter chatbot. The difference from ChatGPT is simple: ChatGPT answers, Mira acts. You do not ask it to write the email, you tell it to send the email. You do not get a draft ticket, you get a real one in Linear with the owner assigned. It does the thing, in the background, and it remembers you between every conversation.

It connects to 500+ apps through Composio (Notion, Gmail, Google Calendar, GitHub, Figma, Stripe and hundreds more), it has long-term memory that holds across sessions and group chats, and it is model-agnostic, running GPT, Claude, Gemini depending on the task. Here is what that turns into.

**For work** This is where the loops idea pays off without a single line of code.

```text
▸ SKILLS
"An hour before each meeting, remind me with the context and
decisions from our last conversation with that person."

"When I forward a message here, turn it into a Linear ticket
with the right priority and assign the owner."

"Every Friday at 4pm, collect the team's task status and metrics
and post a clean weekly digest in our chat."

"Summarize everything I missed in this group chat while I was
away, in 5 bullets."
```

It catches you up on a 200-message thread in seconds, files the ticket while you keep talking, and walks into meetings already briefed. In group chats it remembers the team's decisions and tasks, not just yours.

**For creators** This is the part most people underrate. Mira makes content end to end, inside the chat.

```text
▸ SKILLS
"I'll send a voice note with a raw idea. Turn it into a finished
post with a caption and hashtags."

"Take this one idea and write versions for X, Instagram, LinkedIn,
Email, and a newsletter, each in the right format."

"Generate 3 image options for this post."

"Turn this image into a short video for my Telegram channel."
```

Voice note in, finished post out in about thirty seconds. One brief becomes six platform-native versions. It generates images and video right in the chat, edits photos, swaps backgrounds, builds mascots and avatars, even lip-syncs and animates them. The whole content pipeline lives in one window.

**For voice** Mira treats voice as a first-class input, which matters more than it sounds.

```text
▸ SKILLS
"Transcribe my voice messages into clean text."
"Read this article back to me as audio."
"Summarize the voice notes in this group chat into key points."
```

It transcribes your voice messages, reads text back to you, understands voice notes inside group chats and summarizes the discussion, and works as a hands-free voice assistant when you cannot type.

**For your life** The same engine, pointed at everything else.

```text
▸ SKILLS
"Every evening at 7, ask if I trained today. Keep a streak and
don't let me quietly skip more than one day."

"Every night, ask me 3 questions about my day, remember the
answers, and once a week tell me what changed."

"Track my calories from a photo of my plate."

"Watch this flight route and buy when the price drops to my number."

"Every morning, give me a no-clickbait news digest on my topics."
```

A coach that holds you to a streak. A journal that actually remembers you and becomes a check-in companion over time. Calorie tracking from a photo, no separate app. Language practice built from your own mistakes. A flight watcher that buys when the price is right. A daily digest with the clickbait stripped out.

## How to start in two minutes

Open Telegram. Go to [Mira](https://t.me/mira?start=social_x_200626_howtostart). Send it a message. Free access works immediately. Try one of these first:

```text
@mira, plan my week
@mira, summarize this chat
@mira, remind me to review PRs every Monday at 9am
@mira, write a post about [topic] for X and Instagram
```

Any example in this article becomes a running loop the moment you type it.

## What this actually means for you

Loops are not a trend. They are a shift in who does the work. The AI stops waiting for you to push it through every step and starts running the whole job on its own. That said, this isn't something to chase or force into places it doesn't belong. More often than not, you will just burn money for nothing. My take: start by using what's already there for free, and only once you actually feel that it isn't enough should you start thinking about what you truly need.

If you want to stay up to date with everything happening in AI, follow me on X and Telegram: X - [https://x.com/AnatoliKopadze](https://x.com/AnatoliKopadze) Telegram - [https://t.me/kopadzemp](https://t.me/kopadzemp)