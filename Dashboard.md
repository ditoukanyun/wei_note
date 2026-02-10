---
cssclass: dashboard
---

# 🎯 我的知识库仪表盘

> 📅 {{date:YYYY年MM月DD日 dddd}} | 🕐 {{time:HH:mm}}

---

## 🔥 当前活跃项目

```dataview
table status as "状态", target_date as "截止日期", category as "分类"
from "00_Projects"
where status = "进行中"
sort target_date asc
```

**快速添加**：[[Templates/项目模板|➕ 新建项目]]

---

## ✅ 今日待办

### 紧急重要
- [ ] 

### 重要不紧急
- [ ] 

### 今日习惯
- [ ] 📚 阅读 30 分钟
- [ ] 🏃 运动
- [ ] 📝 每日复盘
- [ ] 💧 喝水 8 杯

**今日复盘**：[[01_Areas/生活管理/每日复盘/{{date:YYYY-MM-DD}} 复盘|📝 开始记录]]

---

## 📚 正在学习

### 前端开发
```dataview
list status
from "01_Areas/技术学习/前端开发"
where status = "学习中"
sort file.mtime desc
limit 5
```

### 后端开发
```dataview
list status
from "01_Areas/技术学习/后端开发"
where status = "学习中"
sort file.mtime desc
limit 5
```

**快速添加**：[[Templates/技术笔记模板|➕ 新建学习笔记]]

---

## 📖 最近阅读

```dataview
table author as "作者", rating as "评分", status as "状态"
from "02_Resources/学习资源/书籍"
sort file.mtime desc
limit 5
```

---

## 🆕 最近更新

```dataview
table file.mtime as "修改时间"
from ""
sort file.mtime desc
limit 10
```

---

## 🗺️ 内容地图 (MOC)

### 工作相关
- [[01_Areas/职业发展/工作管理|工作管理]]
- [[01_Areas/职业发展/技术成长路径|技术成长路径]]
- [[00_Projects/工作项目/|工作项目]]

### 学习相关
- [[01_Areas/技术学习/前端开发/前端开发 MOC|🎨 前端开发]]
- [[01_Areas/技术学习/后端开发/后端开发 MOC|⚙️ 后端开发]]
- [[01_Areas/技术学习/通用技能/通用技能 MOC|🔧 通用技能]]

### 生活相关
- [[01_Areas/生活管理/健康管理|健康管理]]
- [[01_Areas/生活管理/财务规划|财务规划]]
- [[01_Areas/兴趣探索/阅读|阅读]]

---

## 📊 本周统计

| 指标 | 本周 | 上周 |
|------|------|------|
| 完成项目 | | |
| 新增笔记 | | |
| 学习时长 | | |
| 阅读页数 | | |

---

## 🎯 本周重点

1. 
2. 
3. 

---

## 💡 灵感收集

> 随时记录突然出现的想法和灵感

- 

---

## 🔗 快速链接

| 类别 | 链接 |
|------|------|
| **项目** | [[00_Projects\|全部项目]] |
| **领域** | [[01_Areas\|全部领域]] |
| **资源** | [[02_Resources\|全部资源]] |
| **归档** | [[03_Archives\|归档]] |
| **模板** | [[Templates\|全部模板]] |

---

## 🛠️ 系统维护

- [ ] 检查过期项目
- [ ] 整理待处理资源
- [ ] 更新链接图谱
- [ ] 备份知识库

---

> 💡 **提示**：将此页面设为 Obsidian 的启动页，方便每次打开都能快速进入状态。