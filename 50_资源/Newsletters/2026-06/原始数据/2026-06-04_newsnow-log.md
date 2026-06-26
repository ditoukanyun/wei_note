# 2026-06-04 抓取说明

- 时间: 2026/06/04 09:06 CST
- 入口命令: `npx newsnow`
- 结果: 裸命令只返回 CLI 用法；按 source 抓取时，已验证的 10 个稳定源全部返回 `<no response>`。

## 失败的 source

- `baidu`
- `thepaper`
- `ifeng`
- `36kr`
- `wallstreetcn`
- `ithome`
- `juejin`
- `github-trending-today`
- `solidot`
- `sspai`

## 本轮补救口径

- 整理稿改用官网页面补采。
- 实际纳入来源: 百度热搜、凤凰网、36氪、IT之家、GitHub Trending、Solidot、少数派。
- 本轮未纳入: `澎湃新闻`、`华尔街见闻`、`掘金`。

## 未纳入原因

- `澎湃新闻`: 首页可打开，但抽到的文章详情页日期明显滞后，不适合当作 2026-06-04 的当日快照。
- `华尔街见闻`: live 页在当前抓取链路下未能稳定抽出正文列表。
- `掘金`: 热榜页依赖前端接口，本轮未稳定抓取到可核验结果。
