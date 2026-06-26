# 2026-06-08 抓取说明

- 时间: 2026/06/08 09:06 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: `newsnow` 的 source 抓取已明显恢复；与 2026-06-05 相比，不再是普遍性的 `<no response>`。

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
  - 在本环境连续等待约 60 秒后仍未返回结果
  - 本轮直接放弃，避免拖慢整理流程

## 本轮观察

- 国内公共热度以高考、地震和社会事件为主。
- 国际时政与宏观市场同时被伊朗、以色列、特朗普相关议题带动。
- 科技与开发者侧明显聚焦 AI 落地、工具链和实际工作流，而不是单纯模型发布。

## 整理口径

- 直接基于 `newsnow` 返回结果整理，不额外改写原始标题。
- `Solidot` 首条为旧活动推广，已从整理稿正文剔除。
- `华尔街见闻` 使用 `wallstreetcn-news` source；`财联社电报` 本轮未能使用。
