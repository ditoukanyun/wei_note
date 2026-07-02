# 2026-06-29 抓取说明

- 时间: 2026/06/29 09:10:56 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 46 个成功返回、4 个空结果、11 个非零失败、5 个超时。
- 本轮变化: `github` 与 `github-trending-today` 今日恢复可用；`nowcoder` 今日转为连接失败；`bilibili-ranking` 返回 API `code -352`；`steam` 本轮未恢复。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `github`、`github-trending-today`、`ithome`、`juejin`、`solidot`、`sspai`、`ghxi`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`coolapk`、`douban`、`douyin`、`hupu`、`iqiyi-hot-ranklist`、`kuaishou`、`qqvideo-tv-hotsearch`、`smzdm`、`tieba`

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`
- `freebuf`

## 失败或超时的 source

- `bilibili-ranking`
  - 状态: `nonzero`
  - 信息: Bilibili 排行榜接口返回异常 `code -352`
- `cls`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `hackernews`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `kaopu`
  - 状态: `nonzero`
  - 信息: Azure Blob 源站无响应
- `linuxdo`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `linuxdo-hot`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `linuxdo-latest`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `mktnews`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `nowcoder`
  - 状态: `nonzero`
  - 信息: 源站无法连接
- `producthunt`
  - 状态: `nonzero`
  - 信息: 缺少 `PRODUCTHUNT_API_TOKEN`
- `steam`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `v2ex`
  - 状态: `nonzero`
  - 信息: `feed/share.json` 无法连接
- `v2ex-share`
  - 状态: `nonzero`
  - 信息: `feed/ideas.json` 无法连接
- `zaobao`
  - 状态: `nonzero`
  - 信息: 站点连接被提前关闭

## 重试与补救

- 对 `hackernews`、`kaopu`、`linuxdo*`、`mktnews*`、`steam`、`v2ex*`、`zaobao` 做了第二轮窄重试，单源超时上调到 15 秒。
- `github` 与 `github-trending-today` 今天直接恢复可用，开发者社区部分不再只依赖资讯站；`nowcoder` 今日失败，因此社区求职/讨论视角由 `github`、`juejin`、`solidot`、`sspai`、`ghxi` 和 `pcbeta*` 补位。
- 其余失败源均按“单源失败跳过、不阻塞全量轮询”的策略保留失败记录，不缩减其余可用来源的覆盖面。
- 详细结果见 `50_资源/Newsletters/2026-06/原始数据/2026-06-29_newsnow-summary.json`。
