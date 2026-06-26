# 2026-06-10 抓取说明

- 时间: 2026/06/10 09:16 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: 按“多渠道优先”重跑后，16 个来源成功返回，覆盖综合热点、社交热榜、时政、财经、市场情绪、科技与开发者社区。

## 成功抓取并纳入整理稿的 source

- `baidu`
- `zhihu`
- `weibo`
- `tencent-hot`
- `toutiao`
- `thepaper`
- `ifeng`
- `36kr`
- `wallstreetcn-news`
- `jin10`
- `xueqiu-hotstock`
- `ithome`
- `juejin`
- `github-trending-today`
- `solidot`
- `sspai`

## 失败或未纳入的 source

- `cls`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `zaobao`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response>`
- `v2ex`
  - 直接调用超过 50 秒无输出
  - 处理: 手动终止，不阻塞成稿
- `linuxdo-hot`
  - 与 `v2ex` 同组调用时持续挂起，未返回结果
  - 处理: 随组终止，不阻塞成稿
- `hackernews`
  - 沿用 2026-06-10 09:03-09:04 CST 的补测结论
  - 结果: 持续等待超过 60 秒仍无输出，本轮未再阻塞重试

## 新增覆盖来源

- 热榜与舆论面: `zhihu`、`weibo`、`tencent-hot`、`toutiao`
- 财经与市场面: `jin10`、`xueqiu-hotstock`
- 开发者社区面: `juejin`

## 代表 headlines

- `baidu`: 美军称对伊朗发动“自卫性”打击；中国首颗时间胶囊落地四川；“鹅腿阿姨”原材料争议
- `zhihu`: 乘用车销量前十无燃油车；Claude Fable 5；Siri AI 引发资本市场冷反应
- `weibo`: 高考后知后觉情绪；朝方欢送仪式热度；“鹅腿阿姨卖鸭腿”舆情
- `tencent-hot`: 美军报复性打击伊朗；中方对韩严正交涉；储蓄国债发售
- `toutiao`: 运营商“杀熟”；反腐重案；外交部对韩交涉
- `thepaper`: 对朝访问收尾；高考结束查分；乘用车“增重”问题
- `ifeng`: 伊朗战争动态；阿里巴巴等中企涉军清单；稀土出口话题
- `36kr`: 数据中心一体化；DDR5 RCD 芯片；股市与煤焦后市
- `wallstreetcn-news`: 锂矿定价权；燃油车退出月销前十；霍尔木兹海峡风险
- `jin10`: 伊朗 20 个目标被打击；日本国债收益率；黄金与白银走弱
- `xueqiu-hotstock`: 美光、英伟达、Lumentum、闪迪、应用光电
- `ithome`: iOS 27 地图 AI；手机直连卫星；轨道 AI 计算测试
- `juejin`: 千问 3.6 调用教程；跨平台 AI 自动化框架；JavaScript 原型机制
- `github-trending-today`: `last30days-skill`、`turbovec`、`supervision`、`opencv`、`tolaria`
- `solidot`: 全固态电池争议；iPhone 与美国生育率；Falcon 9 第一级 35 次发射
- `sspai`: 2026 Apple 设计奖；Obsidian 与 AI 辅助工作流

## 本轮观察

- 广覆盖策略有效恢复了掘金和多平台热榜视角，新闻面不再局限于少量固定源。
- 社交热榜噪音显著高于新闻站与专业站，但能更好反映平台情绪与议题分化。
- 财经与市场面在今天高度聚焦美伊冲突外溢、贵金属波动、资源定价权和半导体链条。
- 科技与开发者面继续围绕 AI 产品化、跨平台自动化、skills、Apple AI 与卫星通信展开。
- `Solidot` 首条活动推广类条目已从正文剔除；`少数派` 生活方式内容未全部纳入。
