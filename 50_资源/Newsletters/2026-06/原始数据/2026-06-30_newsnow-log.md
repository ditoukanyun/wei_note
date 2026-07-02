# 2026-06-30 抓取说明

- 时间: 2026/06/30 09:06:44 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 50 个成功返回且有内容、3 个空结果、10 个非零失败、3 个超时。
- 本轮变化: `bilibili-ranking`、`freebuf`、`nowcoder`、`steam` 恢复可用；今天没有出现“昨日成功、今日失败”的 source。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `freebuf`、`github`、`github-trending-today`、`ithome`、`juejin`、`nowcoder`、`solidot`、`sspai`、`ghxi`、`steam`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`bilibili-ranking`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`coolapk`、`douban`、`douyin`、`hupu`、`iqiyi-hot-ranklist`、`kuaishou`、`qqvideo-tv-hotsearch`、`smzdm`、`tieba`

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`

## 失败或超时的 source

- `cls`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: 财联社电报接口返回 `404 Not Found`
- `hackernews`
  - 状态: `nonzero`
  - 信息: `news.ycombinator.com` 无响应
- `kaopu`
  - 状态: `nonzero`
  - 信息: Azure Blob 源站无响应
- `linuxdo`
  - 状态: `timeout`
  - 信息: 15 秒重试后仍超时
- `linuxdo-hot`
  - 状态: `timeout`
  - 信息: 15 秒重试后仍超时
- `linuxdo-latest`
  - 状态: `timeout`
  - 信息: 15 秒重试后仍超时
- `mktnews`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: 接口连接被提前关闭
- `producthunt`
  - 状态: `nonzero`
  - 信息: 缺少 `PRODUCTHUNT_API_TOKEN`
- `v2ex`
  - 状态: `nonzero`
  - 信息: `feed/programmer.json` 无法连接
- `v2ex-share`
  - 状态: `nonzero`
  - 信息: `feed/programmer.json` 无法连接
- `zaobao`
  - 状态: `nonzero`
  - 信息: 站点连接被提前关闭

## 重试与补救

- 对 `hackernews`、`kaopu`、`linuxdo*`、`mktnews*`、`steam`、`v2ex*`、`zaobao` 做了第二轮窄重试，单源超时上调到 15 秒。
- `steam` 本轮重试后恢复；`linuxdo*` 仍超时，`mktnews*` 仍是 socket closed，`v2ex*` 仍无法连接。
- `bilibili-ranking`、`freebuf`、`nowcoder` 在不减少其他来源覆盖面的前提下恢复成功，今天的平台热视频、安全与求职社区视角比 2026-06-29 更完整。
- 详细结果见 `50_资源/Newsletters/2026-06/原始数据/2026-06-30_newsnow-summary.json`。
