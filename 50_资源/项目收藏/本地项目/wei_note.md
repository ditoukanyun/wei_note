# wei_note - 个人知识库

- **路径**: `/code/wei_note`
- **GitHub**: https://github.com/ditoukanyun/wei_note
- **标签**: #笔记 #知识库 #Obsidian #Quartz

## 简介
基于 Obsidian + Quartz 的个人知识库系统，使用 Markdown 格式管理笔记，自动构建静态博客。

## 目录结构

```
wei_note/
├── 10_日记/              # 每日日记（按年月组织）
│   ├── 2026年/
│   │   ├── 02月/
│   │   └── 03月/
│   └── 2026-04-07.md
├── 20_项目/              # 项目文档
├── 30_学习/              # 学习笔记
├── 40_工作/              # 工作相关
├── 50_资源/              # 资源收藏
│   ├── Newsletters/      # 每日新闻摘要
│   └── 项目收藏/         # GitHub 项目收藏
├── .agents/              # AI Agent 技能
├── .obsidian/            # Obsidian 配置
└── docs/                 # Quartz 博客配置
```

## 常用命令

```bash
cd /code/wei_note

# 拉取最新代码
git pull

# 提交更改
git add .
git commit -m "更新笔记"
git push

# 构建博客（在 quartz 目录）
cd docs/quartz
npm run build

# 启动本地预览
npm run serve
```

## 博客部署

- **构建工具**: Quartz (https://quartz.jzhao.xyz/)
- **部署方式**: 静态文件 + nginx
- **访问地址**: http://118.145.223.121

## 重要配置

| 文件 | 说明 |
|------|------|
| `docs/quartz/quartz.config.ts` | Quartz 主配置 |
| `docs/quartz/quartz.layout.ts` | 页面布局配置 |
| `.obsidian/app.json` | Obsidian 应用配置 |
| `.obsidian/graph.json` | 图谱视图配置 |

## 同步脚本

项目包含自动同步脚本，可自动：
1. 检查日记目录更新
2. 提交并推送到远程
3. 构建 Quartz 博客
4. 检查/启动 nginx

触发词: `同步笔记`, `推送日记`, `wei-note-sync`

## 注意事项

1. **日记路径**: 新日记按 `10_日记/2026年/04月/2026-04-07.md` 格式存放
2. **图片资源**: 放在 `sources/` 目录，使用相对路径引用
3. **Git 冲突**: 拉取前先提交本地更改，避免合并冲突
4. **自动构建**: 推送后会自动构建博客，约需 1-2 分钟

---

*记录时间: 2026-04-07*
