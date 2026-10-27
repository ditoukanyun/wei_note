# 2026-10-27 抓取说明

- 时间: 2026/10/27 08:00:48 CST
- 入口命令: `/Users/wei/.nvm/versions/node/v24.22.0/bin/newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 41 个成功返回、5 个空结果、15 个非零失败、4 个超时、0 个无效 JSON、1 个缺环境变量跳过。
- 抓取方式: 6 路并发，同站源串行（如 `bilibili*`、`linuxdo*`）。
- 本轮变化: 与 2026-10-26 相比，成功源减少 1 个；恢复可用：`freebuf`；转为缺失：`steam`、`solidot`。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`
- 科技/开发者: `ithome`、`juejin`、`nowcoder`、`sspai`、`ghxi`、`freebuf`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`coolapk`、`douban`、`douyin`、`hupu`、`iqiyi-hot-ranklist`、`kuaishou`、`qqvideo-tv-hotsearch`、`smzdm`、`tieba`

## 返回空结果的 source

- `fastbull-express`
- `fastbull`
- `fastbull-news`
- `pcbeta-windows`
- `pcbeta-windows11`

## 失败或超时的 source

- `bilibili-ranking`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"bilibili-ranking\": Bilibili ranking API returned unexpected response: {\"code\":-352,\"message\":\"-352\",\"ttl\":1}","code":"FETCH_ERROR"}
- `cls`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls-telegraph\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `hackernews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"hackernews\": [GET] \"https://news.ycombinator.com\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?","code"...
- `linuxdo`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo\": [GET] \"https://linux.do/latest.rss\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?","code":"FE...
- `linuxdo-hot`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo-hot\": [GET] \"https://linux.do/top/daily.rss\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?","co...
- `linuxdo-latest`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo-latest\": [GET] \"https://linux.do/latest.rss\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?","co...
- `mktnews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> ECONNRESET: The socket connection was closed unexpectedly. For...
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews-flash\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> ECONNRESET: The socket connection was closed unexpectedl...
- `kaopu`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"kaopu\": [GET] \"https://kaopustorage.blob.core.windows.net/news-prod/news_list_hans_0.json\": 409 Public access is not permitted on this storage ac...
- `v2ex`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"v2ex\": [GET] \"https://www.v2ex.com/feed/create.json\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?","co...
- `v2ex-share`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"v2ex-share\": [GET] \"https://www.v2ex.com/feed/ideas.json\": <no response> ECONNREFUSED: Unable to connect. Is the computer able to access the url?...
- `xueqiu-hotstock`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"xueqiu-hotstock\": [GET] \"https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=30&_type=10&type=10\": 400 ","code":"FETCH_ERROR"}
- `xueqiu`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"xueqiu\": [GET] \"https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=30&_type=10&type=10\": 400 ","code":"FETCH_ERROR"}
- `zaobao`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"zaobao\": [GET] \"https://www.zaochenbao.com/realtime/\": <no response> ECONNRESET: The socket connection was closed unexpectedly. For more informat...
- `solidot`
  - 状态: `timeout`
  - 信息: Timed out after 10000ms
- `github`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `github-trending-today`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `steam`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms

## 缺环境变量跳过的 source

- `producthunt`: 缺少环境变量: PRODUCTHUNT_API_TOKEN

## 重试与补救

- 直接按单个 source 执行 `newsnow <source> --limit 5 --json --pretty`，保持“单源失败跳过、不阻塞全量轮询”的策略。
- 对 `hackernews`、`linuxdo`、`linuxdo-hot`、`linuxdo-latest`、`mktnews`、`mktnews-flash`、`kaopu`、`v2ex`、`v2ex-share`、`zaobao`、`github`、`github-trending-today`、`steam` 做了第二轮窄重试，单源超时上调到 15 秒。
- 本轮继续保持“失败跳过、不阻塞成稿”的策略，没有因为个别 source 失败而收缩成少量固定来源。
- 详细结果见 `/Volumes/zhitai/code/github/wei_note/50_资源/Newsletters/2026-10/原始数据/2026-10-27_newsnow-summary.json`。
