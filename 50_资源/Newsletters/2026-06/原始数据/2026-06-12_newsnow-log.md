# 2026-06-12 抓取说明

- 时间: 2026/06/12 09:12 CST
- 入口命令: `npx newsnow`
- 裸命令结果: 返回 CLI 用法说明，不直接输出新闻。
- `npx newsnow list --json --pretty` 结果: 共识别 66 个 source。
- 本轮结论: 31 个来源成功返回，2 个来源返回空数组，9 个来源失败或挂起；广覆盖策略今天仍有效，并将综合热点、时政、财经、科技和开发者社区同时拉齐。

## 成功抓取并纳入整理稿正文的 source

- `baidu`
- `zhihu`
- `weibo`
- `tencent-hot`
- `toutiao`
- `thepaper`
- `ifeng`
- `cankaoxiaoxi`
- `sputniknewscn`
- `36kr`
- `gelonghui`
- `wallstreetcn-news`
- `wallstreetcn-quick`
- `jin10`
- `xueqiu-hotstock`
- `ithome`
- `juejin`
- `solidot`
- `sspai`
- `nowcoder`
- `bilibili-hot-search`
- `douyin`
- `tieba`

## 成功抓取但仅作侧写的 source

- `36kr-quick`
  - 与 `36kr` 当日前排内容高度重合，保留原始 JSON，不在正文重复展开。
- `coolapk`
  - 以高考后换机、WiFi 7 和生活讨论为主，适合作为数码社区情绪样本。
- `chongbuluo-hot`
  - 以会员、闲聊和求助帖为主，新闻信号较弱。
- `chongbuluo-latest`
  - 以社区求助与信用卡讨论为主，新闻信号较弱。
- `ghxi`
  - 以 Windows 镜像和工具分发为主，更偏工具资源站热度。
- `pcbeta-windows`
  - 以壁纸、工具和装机问题为主。
- `pcbeta-windows11`
  - 以 Win11 升级、镜像和工具为主。
- `douban`
  - 当日主要是作品与文艺话题，不纳入主新闻整理。

## 返回空结果的 source

- `fastbull-news`
- `freebuf`

## 失败或挂起的 source

- `cls`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `cls-telegraph`
  - 返回 `FETCH_ERROR`
  - 失败信息: `404 Not Found`
- `zaobao`
  - 返回 `FETCH_ERROR`
  - 失败信息: `<no response> The socket connection was closed unexpectedly`
- `github-trending-today`
  - 首次直拉 30 秒无输出
  - 使用 `tty=true` 单独补测后仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `linuxdo-hot`
  - 首次直拉 30 秒无输出
  - 使用 `tty=true` 单独补测后仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `hackernews`
  - 使用 `tty=true` 单独补测 7 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `v2ex`
  - 使用 `tty=true` 单独补测 7 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `v2ex-share`
  - 使用 `tty=true` 单独补测 7 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿
- `linuxdo-latest`
  - 使用 `tty=true` 单独补测 7 秒仍无输出
  - 处理: `Ctrl-C` 终止，不阻塞成稿

## 抓取细节

- 直接在 shell 中执行 `npx newsnow <source> --limit 5 --json --pretty` 的成功率仍最高。
- 世界杯开幕式与揭幕战全面挤占综合平台热榜，社会面热点集中度明显高于前一天。
- 美伊协议与中东风险、对菲制裁、英国国防和骚乱、电商与票务平台监管，共同构成今天的政经叙事主轴。
- 财经线继续集中在 AI 基建、光模块、半导体材料、黄金白银与大宗商品波动，以及 SpaceX IPO 和亚太股市风险偏好修复。
- 科技与开发者线继续向 AI 工作流、Vision Pro、企业引入 Copilot/ChatGPT、Agent 学习与求职内容集中。

## 代表 headlines

- `baidu`: 世界杯开幕式；世界杯揭幕战；高考报志愿
- `zhihu`: 对菲制裁；世界杯揭幕战复盘；特斯拉 FSD 山路实测
- `weibo`: 世界杯开幕式；LABUBU 和马宁；文化遗产进生活
- `tencent-hot`: 美伊协议反复；揭幕战三红牌；英国国防大臣辞职
- `toutiao`: 墨西哥 2:0 南非；矿难问责链；菲防长旧闻再发酵
- `thepaper`: 钉钉换帅；抢票平台被约谈；对菲制裁；电商补贴整治
- `ifeng`: 特朗普对伊表态反转；伊朗港口爆炸；协议进入最后定稿
- `cankaoxiaoxi`: 万斯批评内塔尼亚胡；台积电或涨价；美国精英“苏伊士时刻”
- `sputniknewscn`: G20 邀请；美伊协议框架；药明康德起诉美国防部
- `36kr`: 阿里竞购朴朴；PTFE 与算力材料；光模块壳体量产
- `gelonghui`: 全氟醚材料；玻璃基板链条；科伦药业回款
- `wallstreetcn-news`: 朴朴竞购；CME 7x24 黄金原油；SpaceX IPO
- `jin10`: 多晶硅走强；涉企侵权自律公约；港股早报；马斯克/星链中东话题
- `xueqiu-hotstock`: 美光、闪迪、鼎龙股份、中船特气、英伟达
- `ithome`: 钉钉工时争议；Vision Pro；SK 海力士引入 Copilot/ChatGPT
- `juejin`: 跨平台 AI 自动化框架；Codex Skill；具身智能 Agent
- `solidot`: NVIDIA DLI；科技巨头借债；Fedora 可疑 AI 智能体
- `sspai`: Apple 设计奖；内容消费；Obsidian/AI 工作流余热
- `nowcoder`: Agent 学习指南；Agent 岗求职；AI skill 找工作
- `bilibili-hot-search`: 揭幕战；CS 电竞；穆里尼奥回归；五角大楼封锁
- `douyin`: 揭幕战；开幕式；通信技术试验卫星二十五号发射
- `tieba`: 揭幕战；世界杯开幕；C 罗；游戏圈与社会化热议

## 本轮观察

- 世界杯开幕是今天最强的公共流量入口，几乎压过了其他社会热点。
- 对菲制裁和美伊谈判反复让国际政治信号更强，综合平台和新闻站点都在同步放大。
- 财经与产业继续把 AI 叙事落到算力材料、期货交易时段、企业并购与资本市场风险偏好上。
- 开发者社区没有拿到 `github-trending-today` 与 `hackernews`，但 `掘金`、`Solidot`、`牛客`、`IT之家`、`少数派` 足以补出今天的技术面结构。
