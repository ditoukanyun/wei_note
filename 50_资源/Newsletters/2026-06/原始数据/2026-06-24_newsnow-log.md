# 2026-06-24 抓取说明

- 时间: 2026/6/24 09:05:26 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 47 个成功返回、4 个空结果、0 个无效 JSON、13 个非零失败、2 个超时。
- 本轮变化: `github`、`github-trending-today` 今日转为超时，`kaopu` 由 2026-06-23 的成功源改为抓取失败；成功源比 2026-06-23 少 3 个，继续保持“失败跳过、不缩源”的覆盖策略。

## 成功返回的 source

- 综合/资讯: `baidu`、`weibo`、`zhihu`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `ithome`、`juejin`、`solidot`、`sspai`、`ghxi`、`nowcoder`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`bilibili-ranking`、`douyin`、`douban`、`tieba`、`kuaishou`、`qqvideo-tv-hotsearch`、`hupu`、`steam`、`coolapk`、`smzdm`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`iqiyi-hot-ranklist`

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`
- `freebuf`

## 失败或超时的 source

- `cls`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls-telegraph\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `github`
  - 状态: `timeout`
  - 信息: spawnSync npx ETIMEDOUT
- `github-trending-today`
  - 状态: `timeout`
  - 信息: spawnSync npx ETIMEDOUT
- `hackernews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"hackernews\": [GET] \"https://news.ycombinator.com\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `kaopu`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"kaopu\": [GET] \"https://kaopustorage.blob.core.windows.net/news-prod/news_list_hans_0.json\": <no response> Was there a typo in the url or port?","code":"FETCH_ERROR"}
- `linuxdo`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo\": [GET] \"https://linux.do/latest.rss\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `linuxdo-hot`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo-hot\": [GET] \"https://linux.do/top/daily.rss\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `linuxdo-latest`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"linuxdo-latest\": [GET] \"https://linux.do/latest.rss\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `mktnews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> The socket connection was closed unexpectedly. For more information, pass `verbose: true` in the second argument to fetch()","code":"FETCH_ERROR"}
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews-flash\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> The socket connection was closed unexpectedly. For more information, pass `verbose: true` in the second argument to fetch()","code":"FETCH_ERROR"}
- `producthunt`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"producthunt\": PRODUCTHUNT_API_TOKEN is not set","code":"FETCH_ERROR"}
- `v2ex`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"v2ex\": [GET] \"https://www.v2ex.com/feed/programmer.json\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `v2ex-share`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"v2ex-share\": [GET] \"https://www.v2ex.com/feed/programmer.json\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `zaobao`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"zaobao\": [GET] \"https://www.zaochenbao.com/realtime/\": <no response> The socket connection was closed unexpectedly. For more information, pass `verbose: true` in the second argument to fetch()","code":"FETCH_ERROR"}

## 抓取细节

- 直接按单个 source 执行 `npx newsnow <source> --limit 5 --json --pretty`，今天依旧是成功率最高的方式。
- 每个 source 设置 10 秒超时，继续执行“单源失败跳过、不阻塞全量轮询”的策略。
- 详细结果见 `50_资源/Newsletters/2026-06/原始数据/2026-06-24_newsnow-summary.json`。
