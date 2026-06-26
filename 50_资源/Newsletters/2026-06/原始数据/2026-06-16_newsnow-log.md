# 2026-06-16 抓取说明

- 时间: 2026/06/16 09:07 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: 66 个 source 中，47 个成功返回、4 个空结果、8 个非零失败、7 个超时；今天的广覆盖策略明显优于“少量固定源”，综合热点、国际时政、财经产业、科技产品、开发者社区和平台热榜都拿到了可用数据。

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
- `36kr-renqi`
- `cls-depth`
- `cls-hot`
- `gelonghui`
- `wallstreetcn-hot`
- `wallstreetcn-news`
- `wallstreetcn-quick`
- `jin10`
- `xueqiu-hotstock`
- `ithome`
- `juejin`
- `solidot`
- `sspai`
- `bilibili-hot-search`
- `douyin`
- `tieba`
- `kuaishou`

## 成功抓取但仅作侧写的 source

- `36kr-quick`
  - 与 `36kr` 主 feed 高度重复。
- `bilibili`
  - 与 `bilibili-hot-search` 方向相近，重复较多。
- `bilibili-hot-video`
  - 更偏视频内容消费，不利于新闻摘要。
- `chongbuluo`
- `chongbuluo-hot`
- `chongbuluo-latest`
  - 以论坛互助、资源贴和生活讨论为主。
- `coolapk`
  - 社区闲聊和数码观点噪音偏高。
- `douban`
  - 返回内容多为影视人物与书影音条目，新闻结构弱。
- `ghxi`
  - 更适合作为软件下载和工具观察，不适合当日新闻正文。
- `hupu`
  - 主要是社区帖子而非事件新闻。
- `iqiyi-hot-ranklist`
  - 视频内容热度榜，不单独展开。
- `kaopu`
  - 泛资讯可读，但整体信号密度不如正文来源。
- `nowcoder`
  - 今日求职/情感帖占比高于可复用技术讨论。
- `pcbeta-windows`
- `pcbeta-windows11`
  - 以系统折腾、装机问题与外链搬运为主。
- `qqvideo-tv-hotsearch`
  - 娱乐热榜，不单独展开。
- `smzdm`
  - 偏消费内容与品牌讨论。
- `steam`
  - 今日仅反映游戏热度，不适合新闻正文。
- `wallstreetcn`
  - 与 `wallstreetcn-hot/news/quick` 重合较高。
- `xueqiu`
  - 与 `xueqiu-hotstock` 高度重合。

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`
- `freebuf`

## 失败或超时的 source

- `bilibili-ranking`
  - 返回 `FETCH_ERROR`
  - 失败信息: `Bilibili ranking API returned unexpected response: {"code":-352,"message":"-352","ttl":1}`
- `cls`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `cls-telegraph`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `github`
  - 10 秒超时后终止
- `github-trending-today`
  - 10 秒超时后终止
- `hackernews`
  - 返回 `FETCH_ERROR`
  - 失败信息: `Unable to connect`
- `linuxdo`
  - 10 秒超时后终止
- `linuxdo-hot`
  - 10 秒超时后终止
- `linuxdo-latest`
  - 10 秒超时后终止
- `mktnews`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `mktnews-flash`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `producthunt`
  - 返回 `FETCH_ERROR`
  - 失败信息: `PRODUCTHUNT_API_TOKEN is not set`
- `v2ex`
  - 10 秒超时后终止
- `v2ex-share`
  - 10 秒超时后终止
- `zaobao`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`

## 抓取细节

- 直接按单个 source 执行 `npx newsnow <source> --limit 5 --json --pretty`，今天依旧是成功率最高的方式。
- 这次不再只盯住少量稳定源，而是把 `list` 返回的 66 个 source 全量过一遍；结果比 6 月上旬更好，额外拿到了 `cls-depth`、`cls-hot`、`ghxi`、`pcbeta-*`、`steam`、`kaopu` 等补充面。
- `cls` 和 `cls-telegraph` 依旧 404，但 `cls-depth` 与 `cls-hot` 可用，说明财联社系 source 需要分开对待，不能因为一个 endpoint 失败就整组放弃。
- `github*`、`linuxdo*`、`v2ex*` 仍然是最不稳定的一组开发者社区来源；今天的开发者面主要由 `juejin`、`ithome`、`solidot`、`sspai` 补齐。
- 世界杯冷门和中东协议是今天最强的跨平台共识，市场面则同步映射为“油价跌、贵金属强、半导体股强、SpaceX热度延续”。
