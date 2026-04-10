# UI/UX Pro Max Skill

**来源**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill  
**记录时间**: 2026-04-09

---

## 简介

一个为 AI 助手提供设计智能的 Skill，用于构建跨多平台的专业 UI/UX。

---

## 核心功能

### v2.0 旗舰功能：设计系统生成器
AI 驱动的推理引擎，分析项目需求并在数秒内生成完整的设计系统。

**输出示例：**
- 推荐设计模式（Pattern）
- 风格建议（67 种 UI 风格）
- 配色方案（161 种调色板）
- 字体搭配（57 种字体组合）
- 效果与动画
- 反模式警告
- 交付前检查清单

---

## 工作流程

```
用户请求 → 多域搜索 → 推理引擎 → 完整设计系统输出
```

1. **多域并行搜索**（5 个维度）
   - 产品类型匹配（161 分类）
   - 风格推荐（67 种风格）
   - 配色选择（161 种调色板）
   - 落地页模式（24 种）
   - 字体搭配（57 种组合）

2. **推理引擎**
   - 匹配产品 → UI 分类规则
   - 应用风格优先级（BM25 排序）
   - 过滤行业反模式
   - 处理决策规则（JSON 条件）

3. **完整设计系统输出**
   - 模式 + 风格 + 颜色 + 字体 + 效果
   - 需避免的反模式
   - 交付前检查清单

---

## 支持的 UI 风格（部分）

| # | 风格 | 适用场景 |
|---|------|---------|
| 1 | Minimalism & Swiss Style | 企业应用、仪表盘、文档 |
| 2 | Neumorphism | 健康/养生应用、冥想平台 |
| 3 | Glassmorphism | 现代 SaaS、金融仪表盘 |
| 4 | Brutalism | 设计作品集、艺术项目 |
| 5 | 3D & Hyperrealism | 游戏、产品展示、沉浸式 |
| 6 | Dark Mode (OLED) | 夜间模式应用、编程平台 |
| 7 | Claymorphism | 教育应用、儿童应用 |
| 8 | Bento Box Grid | 仪表盘、产品页面、作品集 |
| 9 | AI-Native UI | AI 产品、聊天机器人、Copilot |
| 10 | Spatial UI (VisionOS) | 空间计算应用、VR/AR |

---

## 落地页风格（8 种）

1. **Hero-Centric Design** - 视觉识别强的产品
2. **Conversion-Optimized** - 潜在客户生成、销售页面
3. **Feature-Rich Showcase** - SaaS、复杂产品
4. **Minimal & Direct** - 简单产品、应用
5. **Social Proof-Focused** - 服务、B2C 产品
6. **Interactive Product Demo** - 软件、工具
7. **Trust & Authority** - B2B、企业、咨询
8. **Storytelling-Driven** - 品牌、代理、非营利组织

---

## 技术栈支持

- **Web**: HTML + Tailwind, React, Next.js, shadcn/ui, Vue, Nuxt.js, Svelte, Astro
- **Mobile**: SwiftUI, Jetpack Compose, React Native, Flutter
- **其他**: Angular, Laravel

---

## 安装方式

### Claude Code
```bash
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

### CLI 安装
```bash
npm install -g uipro-cli
uipro init --ai claude  # 或其他 AI 助手
```

---

## 使用示例

自然语言即可触发：
- "Build a landing page for my SaaS product"
- "Create a dashboard for healthcare analytics"
- "Design a portfolio website with dark mode"
- "Make a mobile app UI for e-commerce"

---

## 项目链接

- **GitHub**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **官网**: https://uupm.cc
- **NPM CLI**: https://www.npmjs.com/package/uipro-cli

---

## 相关项目

- [NextLevelBuilder.io](https://nextlevelbuilder.io)
- [GoClaw.sh](https://goclaw.sh)
- [ClaudeKit.cc](https://claudekit.cc)
- [TOSE.sh](https://tose.sh)
