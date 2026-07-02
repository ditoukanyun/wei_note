# 2026-07-01 抓取说明

- 时间: 2026/07/01 09:10:29 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 46 个成功返回、4 个空结果、10 个非零失败、6 个超时、0 个无效 JSON。
- 本轮变化: `iqiyi-hot-ranklist` 今日恢复可用；`github`、`github-trending-today`、`steam` 由昨日成功转为今日超时；`freebuf` 由昨日有内容转为空结果，开发者社区视角更偏中文源。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `ithome`、`juejin`、`nowcoder`、`solidot`、`sspai`、`ghxi`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`bilibili-ranking`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`coolapk`、`douban`、`douyin`、`hupu`、`iqiyi-hot-ranklist`、`kuaishou`、`qqvideo-tv-hotsearch`、`smzdm`、`tieba`

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`
- `freebuf`

## 失败或超时的 source

- `cls`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `github`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `github-trending-today`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `hackernews`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `kaopu`
  - 状态: `nonzero`
  - 信息: Azure Blob 源站无响应
- `linuxdo`
  - 状态: `nonzero`
  - 信息: `latest.rss` 无法连接
- `linuxdo-hot`
  - 状态: `nonzero`
  - 信息: `top/daily.rss` 无法连接
- `linuxdo-latest`
  - 状态: `nonzero`
  - 信息: `latest.rss` 无法连接
- `mktnews`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `producthunt`
  - 状态: `nonzero`
  - 信息: 缺少 `PRODUCTHUNT_API_TOKEN`
- `steam`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `v2ex`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `v2ex-share`
  - 状态: `timeout`
  - 信息: 10 秒首轮与 15 秒重试均超时
- `zaobao`
  - 状态: `nonzero`
  - 信息: 站点连接被提前关闭

## 重试与补救

- 对 `github*`、`hackernews`、`kaopu`、`linuxdo*`、`mktnews*`、`steam`、`v2ex*`、`zaobao` 做了第二轮窄重试，单源超时上调到 15 秒。
- `iqiyi-hot-ranklist` 今日恢复，视频平台热度侧写比昨天完整；但 GitHub、Hacker News、V2EX 和 LinuxDo 同时缺失，全球开发者趋势视角明显弱于 2026-06-30。
- 本轮继续保持“失败跳过、不阻塞成稿”的策略，没有因为开发者源或海外源失败而收缩成少量固定来源。
- 详细结果见 `50_资源/Newsletters/2026-07/原始数据/2026-07-01_newsnow-summary.json`。
