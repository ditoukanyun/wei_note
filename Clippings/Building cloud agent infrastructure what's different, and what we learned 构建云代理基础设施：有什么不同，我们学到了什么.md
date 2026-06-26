---
title: "Building cloud agent infrastructure: what's different, and what we learned 构建云代理基础设施：有什么不同，我们学到了什么"
source: "https://x.com/intuitiveml/status/2062699747224568212"
author:
  - "[[@intuitiveml]]"
published: 2026-06-05
created: 2026-06-07
description: "Most agent frameworks today assume a desktop. One user, one machine, one process. The agent runs while the laptop is open, writes to a local..."
tags:
  - "clippings"
---
![图像](https://pbs.twimg.com/media/HKAs9ukakAAOoou?format=jpg&name=large)

![图像](https://pbs.twimg.com/media/HKAtFFLbkAAtjb6?format=jpg&name=large)

Most agent frameworks today assume a desktop. One user, one machine, one process. The agent runs while the laptop is open, writes to a local filesystem, holds API keys in environment variables, and dies when the terminal closes. When something breaks, the user retries. When the agent needs a package, pip install drops it into the user's Python. State, secrets, and lifecycle all sit inside one trusted boundary.目前，大多数代理框架都假定有桌面。一个用户，一台机器，一个进程。代理在笔记本电脑打开时运行，向本地文件系统写入，在环境变量中保存API密钥，并在终端关闭时停止运行。当出现故障时，用户会重新尝试。当代理需要一个包时，pip install将它放入用户的Python中。状态、秘密和生命周期都位于一个可信边界内。

Cloud agent infrastructure has none of those luxuries.云代理基础设施没有这些奢侈。

The agent runs on a sandbox that boots fresh, on hardware shared with strangers, triggered by callers the user never meets: a schedule, an HTTP request, another agent. The user is usually asleep when the run happens. The code inside the sandbox may be adversarial. The filesystem has to survive deployments. Credentials cannot live where the agent lives. Every guarantee the desktop gives you for free — persistence, identity, network trust, retry — has to be rebuilt as an explicit system.代理运行在一个新启动的沙箱上，运行在与陌生人共享的硬件上，由用户从未遇到的调用者触发：调度、HTTP请求、另一个代理。当运行发生时，用户通常处于睡眠状态。沙箱中的代码可能是对抗性的。文件系统必须经受住部署的考验。凭据不能存在于代理所在的位置。桌面给你的所有免费保证——持久性、身份、网络信任、重试——都必须重新构建成一个明确的系统。

We spent the last few months tightening that layer at CREAO. Two lessons came out of it. If you have ever shipped a desktop agent and wondered what changes when it moves to the cloud, this is what changes.在过去的几个月里，我们在CREAO加强了这一层。我从中得到了两个教训。如果您曾经交付过一个桌面代理，并且想知道当它迁移到云端时会发生什么变化，那么这就是变化。

**Lesson 1: Separate what changes slowly from what changes fast第一课：区分变化慢的和变化快的**

![图像](https://pbs.twimg.com/media/HKAtREzaIAAMlrj?format=jpg&name=large)

On a desktop, the user's environment and the agent's runtime are the same thing, updated on the same cadence, by the same person. In the cloud, they are not.在桌面上，用户的环境和代理的运行时是一样的，由同一个人以相同的节奏更新。在云中，它们不是。

An agent app accumulates state on the platform's side. A stock analyst installs matplotlib, downloads market data, writes charting scripts. That environment is the agent's muscle memory. We freeze it into a sandbox snapshot the moment the user is happy with it, and we hold that snapshot frozen until the user edits the environment again. Every run boots from the same image. Same packages, same files, same versions. Monday's run behaves like Friday's, because nothing underneath has moved.代理应用会在平台端积累状态。股票分析师安装matplotlib，下载市场数据，编写图表脚本。那个环境就是代理的肌肉记忆。当用户对它感到满意时，我们将其冻结为沙盒快照，并保持该快照冻结，直到用户再次编辑环境。每次运行都是从同一个映像启动的。相同的包，相同的文件，相同的版本。周一的走势与周五的走势相似，因为底部没有任何变化。

This is the property that desktop frameworks cannot give you for free. A pip install six months ago resolves to different versions today. A cloud snapshot resolves to the same bytes forever. Reproducibility is something the platform owes the user, and a frozen snapshot is the cheapest way to deliver it.这是桌面框架无法免费提供的属性。六个月前的pip安装今天会解析为不同的版本。云快照永远解析为相同的字节。可重复性是平台欠用户的东西，而冻结快照是提供可重复性的最便宜的方式。

Then the coupling problem shows up.然后耦合问题就出现了。

The same image that freezes the user's environment also contains the runner code — the small harness library developed by us that manages the agent on each run. The user wants their environment to stay still. We want our runner to ship many times a day. One artifact, two opposite requirements.冻结用户环境的同一映像还包含运行程序代码&mdash；我们开发的用于在每次运行时管理代理的小harness库。用户希望他们的环境保持静止。我们希望我们的跑步者一天能发很多次货。一个工件，两个相反的需求。

Our first fix was blunt. On boot, check whether the runner inside the snapshot matches the version we just deployed. If it doesn't, throw the snapshot away and boot from a clean template. It worked, and nobody complained. The damage only hit the first run after a deployment.我们的第一个解决方案是直接的。在启动时，检查快照中的运行程序是否与我们刚刚部署的版本匹配。如果没有，扔掉快照，从一个干净的模板启动。它起作用了，没有人抱怨。损坏只发生在部署后的第一次运行中。

Unattended runs killed that cover. A cron job at 9am Monday should not lose its environment because we deployed at 8:55. The contract we were quietly violating — "your environment is frozen until you change it"无人值守的行动毁掉了掩护。星期一上午9点的cron作业不应该因为我们在8:55部署而失去它的环境。我们悄悄违反的合同“你的环境被冻结了，除非你改变它”。

The fix took us longer than it should have to see. The user's environment and the runner code change at completely different rates. The user edits their agent when they choose to. We deploy the platform many times a day. Treating them as one artifact forced a choice on every deployment: keep stale runner code, or destroy the frozen environment the user explicitly asked us to preserve.修复花了我们太多时间。用户的环境和运行程序代码以完全不同的速率变化。用户可以在自己选择的时候编辑他们的代理。我们每天多次部署这个平台。将它们视为一个工件，在每次部署时都必须做出选择：保留陈旧的运行程序代码，或者破坏用户明确要求我们保留的冻结环境。

The model we landed on borrows from how operating systems handle updates. The kernel changes. Your home directory does not. You do not wipe the disk to install a security patch.我们采用的模式借鉴了操作系统处理更新的方式。内核发生了变化。你的主目录没有。安装安全补丁时没有擦除磁盘。

We drew the same boundary. The sandbox boots from the user's frozen snapshot, untouched. Then we hot-swap only the runner. The sequence:我们画了同样的边界。沙箱从用户的冻结快照启动，不受影响。然后我们只热插拔跑步者。序列:

1. Stage the new runner in a temp directory inside the sandbox.在沙箱内的临时目录中运行新的运行程序。
2. Validate it with node --check so any syntax error is caught before we touch anything live.使用node——check验证它，以便在触及任何活动之前捕获任何语法错误。
3. Atomically swap it in: unlock the immutable flag on the old runner, copy the new one over, re-lock with chattr +i, then hide the chattr binary itself so sandbox code cannot reverse the lock.自动交换：解锁旧运行程序上的不可变标志，复制新运行程序，用chattr i重新锁定，然后隐藏chattr二进制本身，这样沙盒代码就无法反转锁定。
4. Purge V8's compile cache (/home/user/.cache/v8-compile-cache/\*) so the new file actually loads instead of running stale bytecode.清除V8的编译缓存（/home/user/.cache/ V8 -compile-cache/\*），以便实际加载新文件，而不是运行过时的字节码。
5. If any step fails, kill the sandbox and retry with a fresh one. No half-upgraded state ever runs an agent.如果任何步骤失败，终止沙箱并重试一个新的。没有任何半升级状态运行代理。

The whole swap takes about 300 milliseconds. We re-snapshot after a successful run only when the runner code was swapped, baking the updated code into the user's image so the next run skips the swap entirely. Platform deployments never discard the user's state; they fold the new runner into it. The user's packages, files, and customizations carry forward unchanged.整个交换过程大约需要300毫秒。在成功运行之后，只有当运行程序代码被交换时，我们才重新快照，将更新的代码放入用户的映像中，以便下一次运行完全跳过交换。平台部署从不丢弃用户的状态；他们把新来的赛跑运动员塞进去。用户的包、文件和自定义内容不会改变。

If you take one thing from this lesson, it is the diagnostic question. For anything you persist in a cloud platform, ask: who controls the cadence of change on this artifact? If the user and the platform both own it, you will eventually pay for the coupling. Split the artifact along the ownership boundary and let each side update on its own clock.如果你从这节课中得到一样东西，那就是诊断问题。对于您在云平台上坚持的任何内容，请问：谁控制该工件上的更改节奏？如果用户和平台都拥有它，那么您最终将为耦合付费。沿着所有权边界分割工件，并让每一方按照自己的时钟进行更新。

**Lesson 2: Keep secrets out of the execution boundary教训2：让秘密远离执行边界**

![图像](https://pbs.twimg.com/media/HKAtZiZakAAwOzu?format=jpg&name=large)

This is the lesson that separates cloud agent infrastructure from everything else.这是将云代理基础设施与其他一切区分开来的教训。

A desktop agent runs as the user. It uses the user's keys, on the user's machine, against the user's network. A cloud agent runs as nobody, on shared hardware, against the open internet, executing code an LLM wrote from a prompt that may have been adversarial. The security model has to assume the code inside the sandbox is already compromised, not hope against it.桌面代理作为用户运行。它使用用户的密钥，在用户的机器上，对抗用户的网络。云代理在共享硬件上以无人身份运行，对抗开放的互联网，执行LLM从可能是敌对的提示符编写的代码。安全模型必须假设沙箱内的代码已经被破坏，而不是寄希望于它。

The rule we hold is simple. No long-lived credential ever lives inside the sandbox.我们的原则很简单。沙箱中没有长期存在的凭证。

When an agent needs to call an authenticated service — Slack, GitHub, the user's own API — it does not hold the token. It sends a local HTTP request to an API bridge running outside the sandbox. The bridge attaches the OAuth token on the host side and forwards the call. The response comes back without the token ever entering the sandbox's memory or environment.当代理需要调用经过认证的服务& Slack， GitHub，用户自己的API &mdash时，它不持有令牌。它将本地HTTP请求发送到运行在沙箱外的API桥。桥接器在主机端附加OAuth令牌并转发调用。响应返回时，令牌从未进入沙箱的内存或环境。

The interesting part is how the bridge knows the sandbox is allowed to ask. Two checks, layered on purpose.有趣的部分是桥是如何知道沙盒被允许提问的。两张支票，故意分层。

First, IP allowlist. The bridge only accepts connections from the internal network range our sandbox hosts live on. A call from anywhere else — a developer laptop, a leaked URL, the public internet — is dropped at the network layer before any application code runs. This pins the bridge to one piece of physical infrastructure and makes it useless to anyone outside it.首先，IP allowlist。网桥只接受来自我们的沙箱主机所在的内部网络范围的连接。在任何应用程序代码运行之前，来自其他任何地方的调用——开发人员的笔记本电脑、泄露的URL、公共互联网——都会被丢弃在网络层。这将桥梁固定在一个物理基础设施上，使其对外部任何人都无用。

Second, a short-lived JWT minted per run. When a sandbox boots, the platform signs a token scoped to that specific run: which user, which app, which session, with an expiry that covers the run window and nothing more. The sandbox presents it on every bridge call. The bridge verifies the signature, checks the expiry, and only then resolves the user's stored credentials and attaches them server-side. If a sandbox is hijacked, the attacker inherits a token that dies with the run and only authorizes calls scoped to that one session. There is no master credential to steal.其次，每次运行生成一个短暂的JWT。当沙箱启动时，平台签署一个范围为特定运行的令牌：哪个用户，哪个应用程序，哪个会话，有效期覆盖运行窗口，仅此而已。沙盒会在每次桥接调用时呈现它。桥接器验证签名，检查过期，然后解析用户存储的凭据并将它们附加到服务器端。如果沙箱被劫持，攻击者将继承一个令牌，该令牌将随着运行而失效，并且只授权作用域为该会话的调用。没有主证书可以偷。

The same bridge carries billing deductions, logs, and metrics out, so it is the one interface that crosses the sandbox boundary in either direction. Everything else inside the sandbox is treated as compromised by default.同一桥接器携带账单扣除、日志和度量，因此它是在任何方向上跨越沙盒边界的一个接口。默认情况下，沙盒内的其他所有内容都被视为受损。

If a prompt injection convinces an agent to dump process.env to a webhook tomorrow, the attacker gets a short-lived JWT that only works from inside our network and expires with the run. That property is what lets us run untrusted user code on shared infrastructure without losing sleep.如果提示注入说服代理转储进程。攻击者会得到一个短暂的JWT，这个JWT只能在我们的网络中工作，并且会随着运行而过期。正是这个属性让我们在共享基础设施上运行不受信任的用户代码而不会失眠。

## The pattern underneath 下面的图案

Reliable, secure cloud agent infrastructure is not a novel system. It is a few properties held without exception:可靠、安全的云代理基础设施并不是一个新系统。它是一些毫无例外的属性：

- State lives in the sandbox, frozen until the user changes it.状态保存在沙盒中，在用户更改它之前一直处于冻结状态。
- Code is hot-swappable, independent of state.代码是热插拔的，独立于状态。
- Credentials live host-side, never inside the agent.凭据驻留在主机端，而不是在代理中。
- One execution pipeline serves every caller, whether the trigger is a human, a scheduler, or another piece of software.一个执行管道服务于每个调用者，无论触发器是人、调度程序还是其他软件。

That last property is the punchline of the whole design. One executeAgent function handles UI clicks, scheduled runs, and API calls. The billing system, the credit deduction logs, the observability signals — all identical regardless of whether a human clicked Run, a cron fired, or a script called the API. Adding a new trigger surface is a routing change, not an architecture change. The agent itself does not know or care who pulled the trigger.最后一个属性是整个设计的亮点。executeAgent函数处理UI单击、计划运行和API调用。计费系统、信用扣减日志、可观察性信号都是相同的，无论用户是单击了Run、触发了cron还是调用了调用API的脚本。添加新的触发器表面是路由更改，而不是架构更改。特工本身并不知道或关心是谁扣动了扳机。

That is what desktop frameworks cannot give you, and what makes the cloud version worth building. An agent on a laptop is bound to the laptop. An agent in the cloud is a function the rest of your stack can call. The user writes it once. The platform makes it survive deployments, run safely on shared hardware, and accept callers the user never anticipated.这是桌面框架无法提供的，也是云版本值得构建的原因。笔记本上的业务代表与笔记本绑定。云中的代理是堆栈的其余部分可以调用的函数。用户只写一次。该平台使其在部署中存活下来，在共享硬件上安全运行，并接受用户从未预料到的调用者。

An agent is a function with a natural language interface. Its implementation belongs to the user. Its trigger surface, its runtime, its security boundary belong to the platform. The discipline is to build the layers so each evolves on its own clock, and to spend the time finding the cracks between systems before someone else does.代理是一个具有自然语言接口的函数。它的实现属于用户。它的触发面、运行时、安全边界都属于平台。该原则是构建各个层，以便每个层都按照自己的时钟发展，并花时间在其他人之前找到系统之间的裂缝。

That is what makes the next surface cheap to ship, and safe to ship.这就是为什么下一个表面运输成本低、安全的原因。