---
title: Markdown 速查表
type: wiki
created: 2025-02-11
tags: [markdown, reference, cheat-sheet]
---

# Markdown 速查表

## 基础语法

### 标题
```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

### 段落和换行
```markdown
这是同一段落中的文本。

这是另一个段落（用空行分隔）。
这是强制换行（在行尾加两个空格）  
新行开始
```

### 强调
```markdown
*斜体* 或 _斜体_
**粗体** 或 __粗体__
***粗斜体*** 或 ___粗斜体___
~~删除线~~
==高亮== (部分平台支持)
```

### 列表

**无序列表**
```markdown
- 项目 1
- 项目 2
  - 子项目 2.1
  - 子项目 2.2
* 也可以用星号
+ 或加号
```

**有序列表**
```markdown
1. 第一项
2. 第二项
   1. 子项 2.1
   2. 子项 2.2
3. 第三项
```

**任务列表**
```markdown
- [x] 已完成任务
- [ ] 未完成任务
- [ ] 另一个任务
```

---

## 链接和图片

### 链接
```markdown
[链接文字](https://example.com)
[链接文字](https://example.com "悬停标题")
[相对路径](./other-file.md)
[锚点链接](#标题名称)
```

**参考式链接**
```markdown
[链接文字][ref]
[ref]: https://example.com "标题"
```

### 图片
```markdown
![替代文字](https://example.com/image.png)
![替代文字](./local-image.jpg "图片标题")
![替代文字][img-ref]
[img-ref]: ./image.png "标题"
```

---

## 代码

### 行内代码
```markdown
使用 `code` 标签表示行内代码
使用 `` ` `` 来显示反引号
```

### 代码块
````markdown
```python
def hello():
    print("Hello, World!")
```

```javascript
console.log("Hello");
```

```
无语言标识的代码块
```
````

---

## 引用和分隔线

### 引用
```markdown
> 这是引用文本
> 多行引用

> 嵌套引用
>> 第二层引用
>>> 第三层引用
```

### 分隔线
```markdown
---
***
___
```

---

## 表格

```markdown
| 表头 1 | 表头 2 | 表头 3 |
|--------|--------|--------|
| 单元格 | 单元格 | 单元格 |
| 左对齐 | 居中   | 右对齐 |
| 数据   | 数据   | 数据   |

对齐方式:
| 左对齐 | 居中对齐 | 右对齐 |
|:-------|:--------:|-------:|
| 内容   |  内容    |  内容  |
```

---

## 高级语法

### 脚注
```markdown
这里有一个脚注[^1]

[^1]: 这是脚注内容
```

### 定义列表
```markdown
术语 1
:   定义 1

术语 2
:   定义 2a
:   定义 2b
```

### HTML 嵌入
```markdown
<details>
<summary>点击展开</summary>

隐藏的内容

</details>
```

---

## Obsidian 特有语法

### 双向链接
```markdown
[[笔记名称]]
[[笔记名称|显示文字]]
[[笔记名称#标题]]
[[笔记名称#标题|显示文字]]
[[笔记名称#^块ID]]
```

### 嵌入
```markdown
![[笔记名称]]
![[笔记名称#标题]]
![[图片.png]]
```

### 标注（Callouts）
```markdown
> [!note] 标题
> 内容

> [!tip] 提示
> 提示内容

> [!warning] 警告
> 警告内容

> [!danger] 危险
> 危险内容

> [!info] 信息
> 信息内容

> [!todo] 待办
> 待办内容
```

### 标签
```markdown
#tag
#tag/subtag
```

---

## 数学公式

### 行内公式
```markdown
$E = mc^2$
```

### 块级公式
```markdown
$$
\sum_{i=1}^{n} x_i = x_1 + x_2 + \cdots + x_n
$$
```

---

## 特殊字符转义

```markdown
\* 星号
\_ 下划线
\` 反引号
\# 井号
\[ \] 方括号
\( \) 圆括号
\{ \} 花括号
\> 大于号
\< 小于号
\. 句号
\! 感叹号
\| 竖线
\\ 反斜杠
```

---

## Emoji

```markdown
:smile: :heart: :thumbsup: :rocket:
```

常用 Emoji:
- :white_check_mark: `:white_check_mark:` 完成
- :x: `:x:` 错误
- :warning: `:warning:` 警告
- :bulb: `:bulb:` 想法
- :book: `:book:` 文档
- :link: `:link:` 链接
- :star: `:star:` 收藏

---

## 快速参考卡片

| 元素 | Markdown 语法 |
|------|--------------|
| 标题 | `# H1` `## H2` `### H3` |
| 粗体 | `**bold**` |
| 斜体 | `*italic*` |
| 引用 | `> quote` |
| 链接 | `[title](url)` |
| 图片 | `![alt](url)` |
| 代码 | `` `code` `` |
| 代码块 | ` ```code``` ` |
| 无序列表 | `- item` |
| 有序列表 | `1. item` |
| 任务列表 | `- [x] task` |
| 表格 | `\| \| \|` |
| 分隔线 | `---` |
| 脚注 | `[^1]` |
| 删除线 | `~~text~~` |
