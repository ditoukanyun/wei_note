# 2026-06-05 抓取说明

- 时间: 2026/06/05 09:05 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 正常返回 CLI 用法
- `list` 结果: 可列出 66 个 source
- 代表源测试窗口: 2026/06/05 09:01-09:04 CST
- 结果: 10 个代表源全部返回 `FETCH_ERROR`，共同表现为对外 URL `<no response>`

## 失败的 source

- `baidu`
- `ifeng`
- `36kr`
- `wallstreetcn`
- `ithome`
- `juejin`
- `github-trending-today`
- `solidot`
- `sspai`
- `thepaper`

## 本轮补救口径

- 正式整理稿改用官网页面补采。
- 实际纳入来源: 百度热搜、凤凰网、36氪、IT之家、GitHub Trending、Solidot、少数派。
- 时间线提醒: `Solidot` 当前公开页最近更新停留在 2026-06-03；`少数派` 首页以 2026-06-04 内容为主。

## 未纳入说明

- `澎湃新闻`: 今日未做官网补采，避免与本轮网页补采口径混用。
- `华尔街见闻`: 今日未做官网补采，避免额外扩展来源范围。
- `掘金`: 今日未做官网补采，优先保留更稳定的综合与科技站点。
