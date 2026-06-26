# 2026-06-15 抓取说明

- 时间: 2026/06/15 09:09 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: 25 个来源成功返回，2 个来源返回空数组，8 个来源失败或挂起；广覆盖策略今天继续有效，综合热点、时政、财经、科技和开发者社区都已覆盖到位。

## 成功抓取并纳入整理稿正文的 source

- `baidu`
- `zhihu`
- `weibo`
- `tencent-hot`
- `toutiao`
- `thepaper`
- `ifeng`
- `cankaoxiaoxi`
- `sputniknewscn`
- `36kr`
- `gelonghui`
- `wallstreetcn-news`
- `wallstreetcn-quick`
- `jin10`
- `xueqiu-hotstock`
- `ithome`
- `juejin`
- `solidot`
- `sspai`
- `nowcoder`
- `bilibili-hot-search`
- `douyin`
- `tieba`
- `kuaishou`

## 成功抓取但仅作侧写的 source

- `coolapk`
  - 以机型颜值、生活吐槽和社区闲聊为主，新闻信号明显偏弱。

## 返回空结果的 source

- `fastbull-news`
- `freebuf`

## 失败或挂起的 source

- `zaobao`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `cls`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `cls-telegraph`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `mktnews-flash`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `github-trending-today`
  - 首轮脚本抓取 10 秒超时
  - 使用 `tty=true` 单独补测后仍持续无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `hackernews`
  - 首轮脚本抓取 10 秒超时
  - 处理: 不再等待，直接跳过
- `linuxdo-hot`
  - 首轮脚本抓取 10 秒超时
  - 使用 `tty=true` 单独补测后仍持续无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `v2ex`
  - 返回 `FETCH_ERROR`
  - 失败信息: `Unable to connect`

## 抓取细节

- 直接按单个 source 执行 `npx newsnow <source> --limit 5 --json --pretty` 仍然是今天成功率最高的方式。
- `sspai` 在首轮脚本窗口内超时，但随后单独直拉成功，说明今天仍存在个别源“脚本超时、直拉可用”的现象。
- `kuaishou` 作为补充平台热榜单独补抓成功，帮助把短视频平台侧的社会议题和大众情绪补全。
- 今天的综合平台几乎都把“美伊达成和平协议”“霍尔木兹海峡开放预期”和世界杯比赛结果推到前排，舆论集中度高于日常状态。
- 财经面最强信号是油价跳水、黄金白银走强、亚太股市上行，以及围绕半导体材料、机器人融资和太空算力的产业线索。
- 开发者面没有拿到 `github-trending-today`、`hackernews`、`linuxdo-hot` 和 `v2ex`，但 `掘金`、`IT之家`、`Solidot`、`少数派`、`牛客` 仍足以补出今天的技术与职业讨论结构。

## 代表 headlines

- `baidu`: 美伊达成和平协议；荷兰 2 比 2 日本；地下管网焕新
- `zhihu`: 德国 7 比 1 库拉索；微信收费假设讨论；荷兰 2 比 2 日本
- `weibo`: 荷兰 2 比 2 日本；国乒单打全军覆没；报志愿概念梳理
- `tencent-hot`: 特朗普称美伊协议已完成；德国 7 比 1 库拉索；伊朗浓缩铀库存处理
- `toutiao`: 日本 2 比 2 绝平荷兰；美伊达成和平协议；上交会成交项目破 600
- `thepaper`: 黄大炜去世；泌阳货车偏航评论；世界技能奥林匹克倒计时
- `ifeng`: 美伊谈判与霍尔木兹海峡；备忘录细节；金价上涨和油价暴跌
- `cankaoxiaoxi`: 意大利移民示威；G7 峰会巡逻车队事故；瑞士公投
- `sputniknewscn`: 特朗普与伊朗协议；内塔尼亚胡寻求紧急会晤；对伊资产与重建计划
- `36kr`: 印度 IPO；日经 225 大涨；融资余额回落；机器人融资
- `gelonghui`: 停牌公告；TMP 产能；泰国产能规划；机器人概念澄清
- `wallstreetcn-news`: 钼代钨；中国股市上升窗口；油价大跌与日韩股市走强；SpaceX 太空算力
- `wallstreetcn-quick`: 亚太指数上行；原油期货大跌；A50 期货走高
- `jin10`: 日内瓦签字仪式预期；中印尼卫星网络协调；金银高开
- `xueqiu-hotstock`: 巨化股份、赛力斯、东山精密、信维通信、南方海力士
- `ithome`: 华为耳夹耳机；英特尔新处理器；2K 400Hz 显示器；旅居房车
- `juejin`: 前端出路讨论；Fable 5 提示词；Claude Code 相关内容；Bun 多线程
- `solidot`: 本田思域攻击面；软骨再生；印度工人与 AI 机器人；果糖饱腹信号
- `sspai`: WWDC26 回顾；Liquid Glass；Apple 设计奖
- `nowcoder`: 面试扣分习惯；前端开发面经；美团裁应届生；暑期实习经验
- `bilibili-hot-search`: 凡人修仙传；荷兰 2 比 2 日本；T1 vs GEN；德国 7 比 1 库拉索
- `douyin`: 美伊达成和平协议；荷兰 2 比 2 日本；中国经济“六张网”；德国 7 比 1 库拉索
- `tieba`: 停战话题；日本绝平荷兰；德国大胜；BLG/T1 电竞讨论
- `kuaishou`: 美伊达成和平协议；器官捐献；铁路货运；陕西山西震感

## 本轮观察

- 美伊协议与霍尔木兹海峡预期是今天最强的政经交叉信号，同时牵动综合平台、国际新闻站点和市场快讯。
- 世界杯比赛结果继续强势占据大众流量入口，压缩了一般社会新闻的可见度。
- 科技与开发者面没有出现单一压倒性产品发布，更多是 Apple 生态更新、AI 编码工具、前端职业焦虑和求职内容并行发酵。
