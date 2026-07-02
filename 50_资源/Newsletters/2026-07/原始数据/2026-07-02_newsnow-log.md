# 2026-07-02 抓取说明

- 时间: 2026/07/02 09:11:04 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结果: 48 个成功返回、3 个空结果、10 个非零失败、5 个超时、0 个无效 JSON。
- 本轮变化: 与 2026-07-01 相比，成功源增加 2 个；恢复可用：`freebuf`、`github`、`github-trending-today`；转为缺失：`kuaishou`。

## 成功返回的 source

- 综合/资讯: `baidu`、`zhihu`、`weibo`、`tencent-hot`、`toutiao`、`thepaper`、`ifeng`、`cankaoxiaoxi`、`sputniknewscn`
- 财经/产业: `36kr`、`36kr-quick`、`36kr-renqi`、`cls-depth`、`cls-hot`、`gelonghui`、`wallstreetcn`、`wallstreetcn-hot`、`wallstreetcn-news`、`wallstreetcn-quick`、`jin10`、`xueqiu`、`xueqiu-hotstock`
- 科技/开发者: `ithome`、`juejin`、`nowcoder`、`solidot`、`sspai`、`ghxi`、`github`、`github-trending-today`、`freebuf`、`pcbeta-windows`、`pcbeta-windows11`
- 平台/社区热度: `bilibili`、`bilibili-hot-search`、`bilibili-hot-video`、`bilibili-ranking`、`chongbuluo`、`chongbuluo-hot`、`chongbuluo-latest`、`coolapk`、`douban`、`douyin`、`hupu`、`iqiyi-hot-ranklist`、`qqvideo-tv-hotsearch`、`smzdm`、`tieba`

## 返回空结果的 source

- `fastbull`
- `fastbull-express`
- `fastbull-news`

## 失败或超时的 source

- `cls`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `cls-telegraph`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"cls-telegraph\": [GET] \"https://www.cls.cn/nodeapi/updateTelegraphList?appName=CailianpressWeb&os=web&sv=7.7.5&sign=9c11221af4f6b47b253098a8b9957b8f\": 404 Not Found","code":"FETCH_ERROR"}
- `hackernews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"hackernews\": [GET] \"https://news.ycombinator.com\": <no response> Unable to connect. Is the computer able to access the url?","code":"FETCH_ERROR"}
- `kaopu`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"kaopu\": [GET] \"https://kaopustorage.blob.core.windows.net/news-prod/news_list_hans_0.json\": <no response> Was there a typo in the url or port?","...
- `kuaishou`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"kuaishou\": undefined is not an object (evaluating 'data.defaultClient.ROOT_QUERY['visionHotRank({\"page\":\"home\"})'].id')","code":"FETCH_ERROR"}
- `linuxdo`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `linuxdo-hot`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `linuxdo-latest`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `mktnews`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> The socket connection was closed unexpectedly. For more inform...
- `mktnews-flash`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"mktnews-flash\": [GET] \"https://api.mktnews.net/api/flash?type=0&limit=50\": <no response> The socket connection was closed unexpectedly. For more ...
- `producthunt`
  - 状态: `nonzero`
  - 信息: 缺少 `PRODUCTHUNT_API_TOKEN`
- `steam`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `v2ex`
  - 状态: `timeout`
  - 信息: Timed out after 15000ms
- `v2ex-share`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"v2ex-share\": [GET] \"https://www.v2ex.com/feed/programmer.json\": <no response> Unable to connect. Is the computer able to access the url?","code":...
- `zaobao`
  - 状态: `nonzero`
  - 信息: {"error":"Fetch failed for \"zaobao\": [GET] \"https://www.zaochenbao.com/realtime/\": <no response> The socket connection was closed unexpectedly. For more information, pass `v...

## 重试与补救

- 直接按单个 source 执行 `npx newsnow <source> --limit 5 --json --pretty`，保持“单源失败跳过、不阻塞全量轮询”的策略。
- 对 `hackernews`、`kaopu`、`linuxdo`、`linuxdo-hot`、`linuxdo-latest`、`mktnews`、`mktnews-flash`、`steam`、`v2ex`、`v2ex-share`、`zaobao` 做了第二轮窄重试，单源超时上调到 15 秒。
- 本轮继续保持“失败跳过、不阻塞成稿”的策略，没有因为个别 source 失败而收缩成少量固定来源。
- 详细结果见 `/Users/chenwei/Documents/wei_note/50_资源/Newsletters/2026-07/原始数据/2026-07-02_newsnow-summary.json`。
