# 2026-06-09 抓取说明

- 时间: 2026/06/09 09:07 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: `newsnow` 的 source 抓取今天依然可用，但执行方式很敏感；小批次直接拉取成功，并发批量、stdout 重定向和子进程包装会普遍触发 `<no response>`。

## 成功抓取并纳入整理稿的 source

- `baidu`
- `thepaper`
- `ifeng`
- `36kr`
- `wallstreetcn-news`
- `ithome`
- `github-trending-today`
- `solidot`
- `sspai`

## 失败或未纳入的 source

- `cls-telegraph`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `hackernews`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response>`
  - 2026-06-09 09:06 CST 以 25 秒显式超时包装补测，仍未恢复

## 本轮观察

- 百度热搜从纯高考现场转向高考余波与产业热词并行，`电子布价格涨幅达100%` 等算力供应链话题冲入前排。
- 澎湃与凤凰网分别代表国内高层外事与国际安全局势两条主线。
- 产业与开发者侧的共同主题是 agent、skills、数据中心和知识库工具链，而不是新的大模型发布。

## 执行经验

- 直接在 shell 中执行 `npx newsnow <source> --limit 5 --json --pretty` 的成功率最高。
- 在本环境里，使用并发批量、stdout 重定向、`tee` 或 Node 子进程包装时，会让本来可用的 source 普遍退化成 `FETCH_ERROR / <no response>`。
- `Solidot` 首条仍是旧课程推广，不适合作为当日快照，已从正文剔除。
- 少数派热门位本轮偏生活方式和装备内容，正文只保留 3 条与工具工作流更相关的条目。
