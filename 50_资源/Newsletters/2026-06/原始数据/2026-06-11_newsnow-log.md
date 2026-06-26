# 2026-06-11 抓取说明

- 时间: 2026/06/11 09:09 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: 19 个来源成功返回，2 个来源返回空数组，6 个来源失败或挂起；广覆盖策略继续有效，并新增纳入 `cankaoxiaoxi`、`coolapk`、`nowcoder`。

## 成功抓取并纳入整理稿的 source

- `baidu`
- `zhihu`
- `weibo`
- `tencent-hot`
- `toutiao`
- `thepaper`
- `ifeng`
- `cankaoxiaoxi`
- `36kr`
- `wallstreetcn-news`
- `jin10`
- `xueqiu-hotstock`
- `ithome`
- `coolapk`
- `juejin`
- `github-trending-today`
- `solidot`
- `sspai`
- `nowcoder`

## 返回空结果但已补测的 source

- `freebuf`
- `fastbull-news`

## 失败或未纳入的 source

- `cls`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `zaobao`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `linuxdo-hot`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> Unable to connect`
- `mktnews-flash`
  - 返回 `FETCH_ERROR`
  - 失败信息: `The socket connection was closed unexpectedly`
- `hackernews`
  - 单独补测超过 5 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `v2ex`
  - 单独补测超过 5 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿

## 抓取细节

- `github-trending-today`
  - 首次非 TTY 调用持续挂起
  - 第二次使用 `tty=true` 单独补测成功并纳入成稿
- `solidot`
  - 首条仍为 NVIDIA DLI 课程活动
  - 处理: 从整理稿正文剔除，仅保留后续 4 条
- `sspai`
  - 热门位仍混有生活方式内容
  - 处理: 只保留设计奖与 Obsidian / AI 工作流两条
- `nowcoder`
  - 社区帖混有情绪向内容
  - 处理: 只保留 Agent 学习、求职与 AI 面经三条

## 新增覆盖来源

- 国际观察: `cankaoxiaoxi`
- 数码社区: `coolapk`
- 开发者求职社区: `nowcoder`

## 代表 headlines

- `baidu`: 美伊冲突最新进展；超1.1亿人获得个税退税；怀孕到生娃能领7笔钱
- `zhihu`: 美国 5 月 CPI 破 4%；世界杯版权保护声明；小米 SU7 电吸门安全争议
- `weibo`: 央视曝光色情漫画陷阱；广西兴安爆炸；霍尔木兹海峡关闭
- `tencent-hot`: 台湾岛东部海底地图；美伊加码军事施压；上海市副市长陈宇剑被查
- `toutiao`: 日菲与中国大陆动作；汽车出口增长；广西兴安爆炸
- `thepaper`: 山西应急管理系统干部被查；上海副市长被查；AI 回答带入门诊
- `ifeng`: 伊朗彻底关闭霍尔木兹；中方对欧方交涉；特朗普贸易争议
- `cankaoxiaoxi`: 欧洲复苏承压；OpenAI 在美申请 IPO；印巴水资源议题
- `36kr`: “人工智能+三品”；融资余额回落；美银称科技股遭大幅抛售
- `wallstreetcn-news`: AI 牛市错过原因；英伟达 Rubin 带动存储长协；数据中心停工传闻
- `jin10`: 多晶硅拉升；金银早盘波动；A50 和台股低开
- `xueqiu-hotstock`: 英伟达、超微电脑、美光、甲骨文、中船特气
- `ithome`: 育碧裁员；英特尔 Firefly；苹果 Siri AI 体验
- `coolapk`: 高考后换机与一加新机；抖音内容权重讨论
- `juejin`: 跨平台 AI 自动化框架；Agent Skills；LLM 原理入门
- `github-trending-today`: `agent-skills`、`pm-skills`、`tolaria`、`last30days-skill`、`maigret`
- `solidot`: 手机实名制；npm v12；双星系统与行星吞噬
- `sspai`: Apple 设计奖；Obsidian + AI 工作流
- `nowcoder`: Agent 学习指南；Agent 开发岗求职；字节 AI 面经

## 本轮观察

- 美伊冲突、霍尔木兹海峡、台湾周边海上动作、地方爆炸事故和反腐调查共同占据综合热榜前列。
- 财经面一边反映避险和波动，另一边继续押注 AI 基建、存储、半导体材料和算力供应链。
- 开发者面从单纯模型讨论继续转向 `skills`、Agent 工作流、知识库桌面工具和求职实战。
