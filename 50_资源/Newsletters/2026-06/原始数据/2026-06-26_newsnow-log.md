# 2026-06-26 抓取说明

- 时间: 2026/06/26 09:17:09 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 48 个成功返回、4 个空结果、7 个非零失败、7 个超时。
- 本轮变化: `steam` 在重试轮恢复，`zhihu` 通过单独校验后纳入成稿；`github-trending-today` 今日可用，但 `github` 主源仍超时。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `ithome`、`juejin`、`github-trending-today`、`solidot`、`sspai`、`nowcoder`、`ghxi`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`bilibili-ranking`、`douyin`、`douban`、`tieba`、`kuaishou`、`hupu`、`qqvideo-tv-hotsearch`、`iqiyi-hot-ranklist`、`smzdm`、`coolapk`、`steam`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`

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
  - 信息: `spawnSync npx ETIMEDOUT`
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
  - 信息: 接口返回 `403 Forbidden`
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: 接口返回 `403 Forbidden`
- `producthunt`
  - 状态: `nonzero`
  - 信息: 缺少 `PRODUCTHUNT_API_TOKEN`
- `v2ex`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `v2ex-share`
  - 状态: `timeout`
  - 信息: `spawnSync npx ETIMEDOUT`
- `zaobao`
  - 状态: `nonzero`
  - 信息: 站点连接被提前关闭

## 重试与补救

- 对 `github`、`hackernews`、`kaopu`、`linuxdo*`、`mktnews*`、`steam`、`v2ex*`、`zaobao`、`zhihu` 做了第二轮窄重试，单源超时上调到 15 秒。
- `steam` 在重试轮恢复；`zhihu` 的直接抓取曾出现坏 JSON，最终通过 `python3 -m json.tool` 校验后成功写入原始文件。
- 其余失败源均按“单源失败跳过、不阻塞全量轮询”的策略保留失败记录，不缩减其余可用来源的覆盖面。
- 详细结果见 `50_资源/Newsletters/2026-06/原始数据/2026-06-26_newsnow-summary.json`。
