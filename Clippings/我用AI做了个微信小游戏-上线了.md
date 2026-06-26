---
title: "我用AI做了个微信小游戏-上线了"
source: "https://juejin.cn/post/7641048219231010862"
author:
  - "[[前端阿彬]]"
published: 2026-05-18
created: 2026-05-20
description: "真实的 AI 开发微信小游戏全流程记录：技术栈、prompt、踩坑清单、成本明细全公开。文末有彩蛋。"
tags:
  - "clippings"
---
![分享图.jpg](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/650c2b541c584b5fac054600961bf2b0~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5YmN56uv6Zi_5b2s:q75.awebp?rk3s=f64ab15b&x-expires=1779702094&x-signature=dAoyt3a7dC1FpLatkY8vZNBO%2B2o%3D)

## 前言

- **总周期** ：2 个月业余时间（每天通勤 + 周末，平均每天 1.5h）。
- **总成本** ：≈ 微信认证 30，腾讯云oss服务 9.9一年 + 流量计费。
- **技术栈** ： `pixi.js@6 + matter-js + vite + Supabase` ，输出微信小游戏单文件 CJS。
- **AI 工具** ：Claude Code 写代码 / gpt + gemini + 豆包出图 / Claude 写文案 / ElevenLabs、pixabay 音效。
- **产品状态** ：已上线微信小游戏「 **开心点连连看** 」，无限关卡、好友榜、每日挑战、主题系统、成就系统。
- **本文给到** ：完整技术栈选型、踩过的 19 个微信小游戏深坑、我抄了 6 个月才稳定的 Claude Code prompt 工作流、真实成本清单。

> 👀 文末有 3 个开放问题，欢迎在评论区开杠，我会一条一条回。

---

## 一、为什么是「微信小游戏」而不是 H5 / App？

去年底身边陆陆续续有同事被优化，我也开始焦虑。看了一圈"普通人副业方向"，我列了一张表：

| 候选 | 我的判断 |
| --- | --- |
| 写公众号 | 太卷，起号周期 6 个月起 |
| 接外包 | 没技能、没渠道 |
| 摆摊 / 实体 | 重资产、占时间 |
| 做独立 App | 上架太重，iOS 还要 99 美金 |
| **微信小游戏** | 0 上架成本、有 12 亿流量入口、单人单干刚好 |

但真正促使我选小游戏的，是另一个判断：

> **小游戏的「代码 + 美术」体量，刚好卡在 AI 能稳定 cover 的尺寸里。**

太大的项目（比如 SaaS）AI 容易上下文丢失、改坏老逻辑；太小的项目（比如静态页）又不像「正经产品」。 **5000-10000 行、单仓库、单端、无后端依赖** ——这是 2026 年 AI 编程最甜的区间。

---

## 二、技术栈选型：为什么是 PixiJS 6 + Matter.js + Vite？

我让 Claude 给我列了 3 套技术栈对比，最后选的这套：

| 维度 | 选型 | 理由 |
| --- | --- | --- |
| 渲染引擎 | **pixi.js@6** （不是 7+） | 微信小游戏的 WebGL 环境只支持 GLSL 100，pixi 7+ 的某些内置 shader 升级到了 300，会报错 |
| 物理引擎 | **matter-js** | 重力下落机制要用；轻量、文档全、AI 熟悉 |
| 构建 | **vite + rollup** | 必须输出 **CJS 单文件** （微信不支持 ESM、不支持动态 import） |
| 状态 | **mobx** | 一个 `observable` 跑全场，足够 |
| 后端 | **Supabase** （免费额度） | 排行榜 / 同步存档，0 元起步 |
| 适配层 | `@iro/wechat-adapter` + `@pixi/unsafe-eval` | DOM shim + 替换 `new Function` 用的 shader 编译 |
| 触摸 | `@iro/interaction` | 替换 pixi 默认的 DOM 交互插件 |

**Vite 关键配置** （这一段直接抄走能用）：

```ts
代码解读复制代码// vite.config.ts
build: {
  lib: {
    formats: ['cjs'],           // 必须 CJS，不能 ESM
    fileName: () => 'game.js'   // 固定输出
  },
  rollupOptions: {
    output: { inlineDynamicImports: true } // 必须内联所有动态 import
  }
}
// 插件里必须替换 process.env.NODE_ENV
replace({ 'process.env.NODE_ENV': JSON.stringify('production') })
```

**入口必须延迟两帧** （不延迟会直接崩，这是我第一周踩的最大的坑）：

```ts
代码解读复制代码// src/app.ts
function deferInit() {
  if (typeof requestAnimationFrame !== 'undefined') {
    requestAnimationFrame(() => requestAnimationFrame(init))
  } else {
    setTimeout(init, 50)
  }
}
setTimeout(deferInit, 0)
```

原因是：微信小游戏在 `game.js` 顶层执行时， `__wxConfig.useWebWorker` 还没赋值，这时候你访问 `wx.getSystemInfoSync()` 或者 `canvas` 就会报错。 **这条不写在任何官方文档里** ，是我让 Claude 帮我读 `@iro/wechat-adapter` 源码读出来的。

---

## 三、19 个微信小游戏的深坑（这是本文最干的部分）

下面这张表是我整整 6 个月维护的 `AGENTS.md` （专门给 AI 看的注意事项），现在打包送给你：

| # | 坑 | 解法 |
| --- | --- | --- |
| 1 | 入口同步代码访问 `wx` / `canvas` 会崩 | 延迟 2 帧 + `setTimeout(50)` 兜底 |
| 2 | 没有 DOM / window / document | `@iro/wechat-adapter` 必须第一行 import |
| 3 | 微信禁止 `eval` / `new Function` | `@pixi/unsafe-eval` 替换 PIXI 内部 shader 编译 |
| 4 | 默认 interaction 用 `addEventListener` | `@iro/interaction` 替换，注册成 RendererPlugin |
| 5 | 触摸坐标直传，不要再做 DOM 偏移 | `mapPositionToPoint = (p,x,y) => p.set(x,y)` |
| 6 | `canvas` 是全局变量，不是 DOM 查询 | `new PIXI.Renderer({ view: canvas })` |
| 7 | accessibility 插件会操作 DOM 报错 | `renderer.plugins.accessibility.destroy()` |
| 8 | Shader 只能 GLSL 100，不能 300 | 自定义 shader 不写版本号；TilingSprite 需手动替换 |
| 9 | 必须 CJS 单文件 + 内联动态 import | vite 配置见上文 |
| 10 | `process.env.NODE_ENV` 运行时不存在 | rollup-plugin-replace 注入 |
| 11 | 不能用 `new Audio()` / `AudioContext` | `wx.createInnerAudioContext` |
| 12 | TS 中 Container 没有 `interactive` 字段 | 用 `(x as any).interactive = true` 断言 |
| 13 | 用 `pointerdown` ，不要用 `click` | touch 不触发 click |
| 14 | 排行榜要走开放数据域（独立沙箱） | `dist/context/` 独立 build，主域 postMessage |
| 15 | 开放数据域不能跑 ES5 编译 | `project.config.json` 的 `babelSetting.ignore` 加 `"context/**"` |
| 16 | 不能用 `fetch` / `localStorage` | `wx.request` / `wx.setStorage` |
| 17 | `wx.getSystemInfoSync()` 不要重复调用 | 启动时取一次，导出常量 `windowWidth/windowHeight/safeAreaTopPx` |
| 18 | 高度不能写死 1334 | `designLayoutH = round(750 * windowHeight / windowWidth)` |
| 19 | AnimatedSprite 在纹理未就绪时设宽高会爆炸 | 监听 `baseTexture.once('loaded')` 后再 `scale.set` |

这张表是我 **真金白银** 踩出来的——尤其是第 8、15、19 条，每条都让我卡了不止一天。

> 💡 看到这里你可能想问：「这些 AI 能自己想到吗？」
> 
> 答案是： **不能** 。这就是为什么我下面要讲 prompt 工作流。

---

## 四、我用了 6 个月才稳定的 Claude Code 工作流

这是本文第二干的部分。直接给你三段我每个项目都用的「prompt 资产」。

### 4.1 给 AI 配一份 CLAUDE.md（核心心法）

Claude Code 会自动读项目根目录的 `CLAUDE.md` 。这个文件不是给人看的，是 **给 AI 看的项目说明书** 。我的写法是：

```markdown
代码解读复制代码## 项目类型
微信小游戏（不是 H5），pixi.js@6 + matter-js + vite，单文件 CJS。

## 必读
AGENTS.md 是微信小游戏的非显式坑清单。改下面任一类代码前必读：
- 入口/初始化（§1-2）
- PIXI 集成（§3, 5-9）
- 构建配置（§8）
- 坐标系（§4, 10）
- 音频（§11）
- 交互（§12）
- 开放数据域（§13）
- 禁用 Web API（§15）

## 路径别名
~/* → src/*，@/* → 仓库根

## 约定
- UI 区域必须加中文注释（// 砖块区域、// 顶部菜单栏）
- 游戏逻辑变更必须同步更新 docs/需求文档.md
```

**关键点** ：把"AI 会犯什么错"写进去，而不是把"项目长什么样"写进去。后者它自己会读代码，前者它读不出来。

### 4.2 把"踩过的坑"沉淀成 AGENTS.md

每踩一个坑、修一个 bug，我都让 Claude 把这个坑总结成一节加进 `AGENTS.md` 。半年下来 19 节， **下次再叫它写新功能，它几乎不犯这些错了** 。

这才是 AI 编程真正的复利——不是 prompt 写得多花，而是 **知识被持续地外化到文件里** 。

### 4.3 写功能用「三段式」prompt

```
代码解读复制代码# 上下文
我要在 src/ui/ 下加一个「皮肤选择弹窗」，复用现有 makePanelBg / panelPad / bounceIn 的设计语言。
（参考 src/ui/pvp-modal.ts 的结构）

# 需求
1. 弹窗宽 PANEL_W = DESIGN_REF_W * 0.84
2. 横向 3 列网格，展示已解锁/未解锁两态
3. 点击未解锁项给 toast 提示
4. 选中后写入 src/game/llk-save.ts 的存档

# 约束
- 不准用 click，必须用 pointerdown
- 不准引入新依赖
- 不准改 src/core/，那是基础设施
- 改完之后把新增的资源路径加到 src/ui/home.ts 的 ASSET_URLS 里
```

**为什么有效** ：AI 最容易犯的不是写错代码，而是 **做多** ——给你顺手 refactor 一下不该动的地方。把"不准做什么"写出来比"要做什么"更重要。

---

## 五、真实成本明细（我没拿融资也没投广告）

| 项 | 金额 |
| --- | --- |
| Claude / Cursor 订阅 ¥200/月 × 6 | ¥1200 |
| Midjourney 订阅（中途换成即梦免费版） | ¥0 |
| 微信小游戏注册（个人主体） | ¥0 |
| 域名 / 服务器（Supabase 免费额度） | ¥0 |
| 美术外包 | ¥0（全部 AI 出图） |
| 音效 / BGM | ¥0（在线音效库 + ElevenLabs 试用） |
| **总计** | **≈ ¥1200** |

便宜过一次 Python 培训班。

---

## 六、AI 帮不了你的 4 件事（不吹 AI，反向干货）

写了这么多 AI 的好，必须诚实说说它 **真的不行** 的地方：

**1\. 产品决策它不会替你做。**

「第 1 关该不该难？」「死局要不要自动重排？」「弹窗按钮放左还是右？」——AI 给的是平均答案，平均答案是没记忆点的。

**2\. 长上下文里它会偷偷改坏老逻辑。**

一次给它太多目标，它会"顺手优化"你没让它改的地方。我现在的纪律是： **一次只让它做一件事，做完立刻 commit** 。

**3\. 美术风格一定要锁死参考图。**

不锁参考图，3 张图能给你 3 种画风。我后来的做法是： **固定 1 张主视觉，所有出图都把它作为 style reference 喂进去** 。

**4\. 上架审核它帮不了你。**

备案、资质、隐私协议、用户协议、平台审核——这些得自己学。AI 顶多帮你写文案，不能帮你过审。

---

## 七、最让我意外的一个发现

做这个项目之前我以为 AI 编程是「我说一句、它写一段」。

做完之后我的看法变了：

> **AI 编程的本质，是把"项目里所有非显式的约束"全部外化成文档。**
> 
> 你的 `CLAUDE.md` 、 `AGENTS.md` 、需求文档、UI 规范——这些不是项目副产物， **它们才是 AI 时代的真正源代码** 。手写的 TS 代码反而成了"编译产物"。

这件事颠覆了我对"什么是工程"的理解。在 AI 之前，文档是给人看的，写多了浪费时间；AI 之后，文档是 **生产力** ，写得越好、AI 产出越稳。

我现在每开一个新项目，第一件事不是 `pnpm init` ，是 `touch CLAUDE.md AGENTS.md` 。

---

## 八、想试一下成品的话

游戏名叫「 **开心点连连看** 」——

微信里搜「开心点连连看」就能直接玩。

不用关注、不用授权、不用看广告，3 分钟一局，玩完顺手退也没人追你。

如果你玩了之后，觉得"这玩意儿一个人真的能做出来啊"，那就是我写这篇文章最大的收获。

---

## 九、给评论区的 3 个开放问题 👇

写到这里我自己也很多想不清楚的事， **真心想听听掘金各位的看法** ：

1. **你觉得 AI 编程的天花板，是"小型完整项目"还是"中大型项目的局部加速"？** 我的体感是前者已经稳了，后者还差不少。你呢？
2. **如果让你用 AI 做一个副业，你会选什么方向？** 我筛了一圈选了小游戏，但我猜评论区一定有更骚的方向。
3. **`CLAUDE.md` / `AGENTS.md` 这套"外化约束"的思路，你在自己的项目里用了吗？怎么用的？** 想互相抄一抄。

> 评论区留言我会 **一条一条回** ，前 50 条留言的同学，我把我这几个月攒下来的 prompt 模板包（含 pixi开发微信小游戏模版 + 出图 prompt 模板，当然还没完全整理好，我做个工具网站，自用的，会逐步往上更新内容）私信发给你 🦫🌿

---

## 十、彩蛋：本文目录索引（方便收藏）

- [一、为什么是「微信小游戏」](#%E4%B8%80%E4%B8%BA%E4%BB%80%E4%B9%88%E6%98%AF%E5%BE%AE%E4%BF%A1%E5%B0%8F%E6%B8%B8%E6%88%8F%E8%80%8C%E4%B8%8D%E6%98%AF-h5--app "#%E4%B8%80%E4%B8%BA%E4%BB%80%E4%B9%88%E6%98%AF%E5%BE%AE%E4%BF%A1%E5%B0%8F%E6%B8%B8%E6%88%8F%E8%80%8C%E4%B8%8D%E6%98%AF-h5--app")
- [二、技术栈选型](#%E4%BA%8C%E6%8A%80%E6%9C%AF%E6%A0%88%E9%80%89%E5%9E%8B%E4%B8%BA%E4%BB%80%E4%B9%88%E6%98%AF-pixijs-6--matterjs--vite "#%E4%BA%8C%E6%8A%80%E6%9C%AF%E6%A0%88%E9%80%89%E5%9E%8B%E4%B8%BA%E4%BB%80%E4%B9%88%E6%98%AF-pixijs-6--matterjs--vite")
- [三、19 个微信小游戏深坑 ⭐](#%E4%B8%8919-%E4%B8%AA%E5%BE%AE%E4%BF%A1%E5%B0%8F%E6%B8%B8%E6%88%8F%E7%9A%84%E6%B7%B1%E5%9D%91%E8%BF%99%E6%98%AF%E6%9C%AC%E6%96%87%E6%9C%80%E5%B9%B2%E7%9A%84%E9%83%A8%E5%88%86 "#%E4%B8%8919-%E4%B8%AA%E5%BE%AE%E4%BF%A1%E5%B0%8F%E6%B8%B8%E6%88%8F%E7%9A%84%E6%B7%B1%E5%9D%91%E8%BF%99%E6%98%AF%E6%9C%AC%E6%96%87%E6%9C%80%E5%B9%B2%E7%9A%84%E9%83%A8%E5%88%86")
- [四、Claude Code 工作流 ⭐](#%E5%9B%9B%E6%88%91%E7%94%A8%E4%BA%86-6-%E4%B8%AA%E6%9C%88%E6%89%8D%E7%A8%B3%E5%AE%9A%E7%9A%84-claude-code-%E5%B7%A5%E4%BD%9C%E6%B5%81 "#%E5%9B%9B%E6%88%91%E7%94%A8%E4%BA%86-6-%E4%B8%AA%E6%9C%88%E6%89%8D%E7%A8%B3%E5%AE%9A%E7%9A%84-claude-code-%E5%B7%A5%E4%BD%9C%E6%B5%81")
- [五、真实成本明细](#%E4%BA%94%E7%9C%9F%E5%AE%9E%E6%88%90%E6%9C%AC%E6%98%8E%E7%BB%86%E6%88%91%E6%B2%A1%E6%8B%BF%E8%9E%8D%E8%B5%84%E4%B9%9F%E6%B2%A1%E6%8A%95%E5%B9%BF%E5%91%8A "#%E4%BA%94%E7%9C%9F%E5%AE%9E%E6%88%90%E6%9C%AC%E6%98%8E%E7%BB%86%E6%88%91%E6%B2%A1%E6%8B%BF%E8%9E%8D%E8%B5%84%E4%B9%9F%E6%B2%A1%E6%8A%95%E5%B9%BF%E5%91%8A")
- [六、AI 帮不了你的 4 件事](#%E5%85%ADai-%E5%B8%AE%E4%B8%8D%E4%BA%86%E4%BD%A0%E7%9A%84-4-%E4%BB%B6%E4%BA%8B%E4%B8%8D%E5%90%B9-ai%E5%8F%8D%E5%90%91%E5%B9%B2%E8%B4%A7 "#%E5%85%ADai-%E5%B8%AE%E4%B8%8D%E4%BA%86%E4%BD%A0%E7%9A%84-4-%E4%BB%B6%E4%BA%8B%E4%B8%8D%E5%90%B9-ai%E5%8F%8D%E5%90%91%E5%B9%B2%E8%B4%A7")
- [七、最让我意外的发现](#%E4%B8%83%E6%9C%80%E8%AE%A9%E6%88%91%E6%84%8F%E5%A4%96%E7%9A%84%E4%B8%80%E4%B8%AA%E5%8F%91%E7%8E%B0 "#%E4%B8%83%E6%9C%80%E8%AE%A9%E6%88%91%E6%84%8F%E5%A4%96%E7%9A%84%E4%B8%80%E4%B8%AA%E5%8F%91%E7%8E%B0")
- [八、试玩入口](#%E5%85%AB%E6%83%B3%E8%AF%95%E4%B8%80%E4%B8%8B%E6%88%90%E5%93%81%E7%9A%84%E8%AF%9D "#%E5%85%AB%E6%83%B3%E8%AF%95%E4%B8%80%E4%B8%8B%E6%88%90%E5%93%81%E7%9A%84%E8%AF%9D")
- [九、3 个开放问题 👇](#%E4%B9%9D%E7%BB%99%E8%AF%84%E8%AE%BA%E5%8C%BA%E7%9A%84-3-%E4%B8%AA%E5%BC%80%E6%94%BE%E9%97%AE%E9%A2%98- "#%E4%B9%9D%E7%BB%99%E8%AF%84%E8%AE%BA%E5%8C%BA%E7%9A%84-3-%E4%B8%AA%E5%BC%80%E6%94%BE%E9%97%AE%E9%A2%98-")

---

> 如果这篇文章帮到你， **点赞收藏 + 关注** 支持一下，让卡皮巴拉多一个粉丝 🦫
> 
> 下一篇预告：《我是怎么用 Supabase 给微信小游戏做了一套"零成本好友排行榜"》——感兴趣的同学评论区扣 1，我看人数定优先级。