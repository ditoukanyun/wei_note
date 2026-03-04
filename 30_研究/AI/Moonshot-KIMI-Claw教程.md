---
title: Moonshot推出KIMI Claw工具，5分钟搭建股市盯盘助手
source: https://www.huxiu.com/article/4838633.html
date: 2026-03-04
tags: [KIMI, Moonshot, OpenClaw, AI, 股市, 教程]
---

# Moonshot推出KIMI Claw工具，5分钟搭建股市盯盘助手

> 原文链接：https://www.huxiu.com/article/4838633.html  
> 采集时间：2026-03-04

---

我之前写过几篇OpenClaw的保姆级教程，阅读量加起来可能有几十万了，在评论区收到最多的反馈就是：门槛太高，坑太多，出了问题太难解决！

其实，国内大模型和云厂商跟进很快！想快速体验到用聊天软件指挥一个能干活儿的OpenClaw的最佳方案，绝对不是自己手动一步一步搭建，而是去选一个可以"一键部署"的地方，实现真正意义的"5分钟就能体验"。

今天给大家推荐的是**Moonshot的KIMI Claw**。为什么首先推荐Moonshot？因为你订阅KIMI Allegretto版本及以上会员相当于白领了一只龙虾嘛！毕竟自己找一台Spot Server部署龙虾一个月都得大几十¥了...

具体场景嘛，刚好最近在测几个前微软同事的创业项目**QVeris**，就干脆搞了个**KIMI Claw + QVeris + 飞书 = 股市盯盘助手**。

---

## 创建KIMI Claw

1. 访问 https://www.kimi.com/membership/pricing
2. 切换到连续包月选择 **¥199/月 的Allegretto 版本**，点击"订阅"
3. 进入 https://www.kimi.com/bot 点击"创建"
4. 等待1分钟（有时可能会遇上插件升级，再等待1分钟）
5. 建议先打开设置项看看有啥
6. 给Kimi Claw起个名字
7. 在对话的第一个session完成bootstrap

**自带终端**，本质上和Openclaw没啥区别。可以直接 `openclaw onboard`；所以，如果你会独立部署OpenClaw的话，玩转Kimi Claw应该不成问题。

不过，如果玩不转命令行，也没关系，你直接问KIMI Claw怎么配置也行。

---

## 把KIMI Claw接入飞书

1. 登录飞书开放平台 https://open.feishu.cn/app
2. 创建企业自建应用
3. 点击"添加机器人"
4. 对机器人进行配置，填入名称
5. "权限管理" --> "批量导入/导出权限"
6. 点击"下一步" -> "申请开通" -> "确认"
7. 点击"创建版本"，填入应用信息
8. 点击"保存" -> "确认发布"
9. 点击"凭证与基础信息"
10. **将APP ID和App Secret告诉KIMI Claw**

**注意：** KIMI Claw可能会尝试"重启自己"失败。此时可以：
- 打开KIMI Claw的终端，输入 `openclaw gateway restart`
- 或者在KIMI Claw的设置中选择重启KIMI Claw

11. 回到飞书开放平台"事件与回调"，选择"长连接"
12. 添加 `im.message.receive_v1`
13. 点击"创建版本"，然后确认发布
14. 切换到飞书，找到"开发者小助手"，点击"打开应用"
15. 然后就可以和KIMI Claw在飞书上开心地玩耍啦

---

## 打通QVeris

**QVeris是啥？**  
可以把QVeris理解成API的OpenRouter，一个API KEY打通成千上万个不同服务和工具的API。创始人都是前微软ARD的硬核团队。

1. 访问 https://qveris.ai/
2. 采用Google/Github登录
3. 登录之后，会获得5000+个点数，够玩很久了
4. 回到首页，把页面底部那句话复制给KIMI Claw

如果安装失败了，就直接把QVeris的Github塞给KIMI Claw，并告知QVeris的base url是 `https://qveris.ai/api/v1/search`

---

## KIMI Claw + QVeris打造贴身金融小助手

### 查询特定股票
由于直接让KIMI Claw创建的飞书多维表格有权限问题，因此，自己创建一个飞书多维表发给KIMI Claw。KIMI Claw会把这支股票的数据都写入到这个多维表格中。

打开多维表格，使用AI引导新建仪表盘。

示例数据：
- 小米集团过去4个季度的营收、同比增长率、净利润同比增长等
- 分析当日的涨停股龙虎榜及资金偏好和趋势
- 写入飞书多维表格，创建仪表板
- 符合特定要求的股票列表

### 创建定时任务
让KIMI Claw自动获取涨停股数据、分析、写入多维表格。

---

## 更多可能场景

金融场景也仅是KIMI Claw可以支持的无数可能场景之一，结合KIMI K2.5强大的原生多模态能力，可以开的脑洞无限多：

1. 搭网页？
2. 做插件？
3. 待办追踪？
4. 搞个CLI工具？
5. AI绘画收藏官？
6. etc...

具体做什么，就交给你自己思考啦！
