---
title: HTML标签详解
date: 2026-02-10
tags:
  - HTML
  - 标签
  - 属性
aliases:
  - HTML标签
  - HTML元素
parent: "[[00-HTML-MOC|HTML知识地图]]"
---

# HTML标签详解

> [!abstract] 本章概要
> 本章详细介绍HTML中常用的标签及其属性，按功能分类整理。

## 一、文本标签

### 基础文本样式

| 标签 | 作用 | 语义 |
|------|------|------|
| `<b>` | 加粗 | 仅视觉加粗 |
| `<strong>` | 加粗 | **强调重要性** |
| `<i>` | 斜体 | 仅视觉斜体 |
| `<em>` | 斜体 | **强调文本** |
| `<u>` | 下划线 | 下划线文本 |
| `<s>` / `<del>` | 删除线 | 删除/修改的文本 |
| `<mark>` | 高亮 | 标注/突出显示 |
| `<sup>` | 上标 | 上标文本 |
| `<sub>` | 下标 | 下标文本 |

```html
<!-- 示例 -->
<p>这是<b>加粗</b>和<strong>强调</strong>文本</p>
<p>化学公式：H<sub>2</sub>O，数学公式：E=mc<sup>2</sup></p>
```

### 段落与格式

| 标签 | 作用 | 重要属性 |
|------|------|----------|
| `<p>` | 段落 | `align` - left/center/right |
| `<br />` | 换行 | 单边标签 |
| `<hr />` | 水平线 | color, width, size, noshade |
| `<pre>` | 预格式化 | **保留空格和换行** |

```html
<!-- pre标签示例 -->
<pre>
    这行会保留    空格
    和换行
</pre>
```

### 标题标签

```html
<h1>一级标题 - 页面主标题</h1>
<h2>二级标题 - 章节标题</h2>
<h3>三级标题 - 小节标题</h3>
<h4>四级标题</h4>
<h5>五级标题</h5>
<h6>六级标题</h6>
```

> [!tip] SEO建议
> - 一个页面只使用一个`<h1>`
> - 按层级使用标题，不要跳级

## 二、媒体标签

### 图片标签

```html
<img src="图片路径" 
     alt="替代文字" 
     title="提示文字"
     width="宽度"
     height="高度" />
```

**重要属性：**
- `src` - 图片资源路径（**必需**）
- `alt` - 图片无法显示时的替代文字
- `title` - 鼠标悬停时显示的文字

> [!warning] 图片尺寸
> 最好不要同时设置width和height，否则可能导致图片拉伸变形。

**支持的图片格式：**
- ✅ 可用：jpg/jpeg, png, gif, bmp, webp, svg
- ❌ 避免：psd, ai（设计源文件）

### 音频标签

```html
<audio controls loop autoplay>
    <source src="audio.mp3" type="audio/mpeg">
    <source src="audio.ogg" type="audio/ogg">
    您的浏览器不支持音频播放
</audio>
```

**属性说明：**
- `controls` - 显示播放控件
- `autoplay` - 自动播放
- `loop` - 循环播放

**支持格式：** MP3, Ogg Vorbis, Wav

### 视频标签

```html
<video controls width="640" height="360">
    <source src="video.mp4" type="video/mp4">
    <source src="video.webm" type="video/webm">
    <source src="video.ogg" type="video/ogg">
    您的浏览器不支持视频播放
</video>
```

**支持格式：** MP4, WebM, Ogg

## 三、链接标签

### 基础链接

```html
<a href="目标地址" 
   target="打开方式" 
   title="提示文字">
   链接文字
</a>
```

**target属性：**

| 值 | 说明 |
|----|------|
| `_self` | 默认，在当前窗口打开 |
| `_blank` | **在新窗口/标签页打开** |
| `_parent` | 在父框架中打开 |
| `_top` | 在整个窗口中打开 |
| `framename` | 在指定框架中打开 |

**空链接：**
```html
<!-- 方式1：JavaScript空链接 -->
<a href="javascript:void(0);">点击不跳转</a>

<!-- 方式2：#占位符（会跳转到页面顶部） -->
<a href="#">占位链接</a>
```

### 锚点链接

> [!info] 锚点用于页面内跳转

**定义锚点：**
```html
<a name="section1"></a>
<!-- 或 -->
<a id="section1"></a>
```

**跳转到锚点：**
```html
<!-- 同一页面 -->
<a href="#section1">跳转到第一节</a>

<!-- 不同页面 -->
<a href="page.html#section1">跳转到页面第一节</a>
```

## 四、列表标签

### 无序列表

```html
<ul type="disc">
    <li>项目一</li>
    <li>项目二</li>
    <li>项目三</li>
</ul>
```

**type属性值：**
- `disc` - 实心圆（默认）
- `circle` - 空心圆
- `square` - 实心方块

### 有序列表

```html
<ol type="1" start="5">
    <li>项目五</li>
    <li>项目六</li>
    <li>项目七</li>
</ol>
```

**type属性值：**
- `1` - 数字（默认）
- `a` / `A` - 小写/大写字母
- `i` / `I` - 小写/大写罗马数字

**start属性：** 设置起始序号

### 定义列表

```html
<dl>
    <dt>HTML</dt>
    <dd>超文本标记语言</dd>
    
    <dt>CSS</dt>
    <dd>层叠样式表</dd>
</dl>
```

> [!note] 注意
> `dt` 和 `dd` 只能出现在 `dl` 标签内

## 五、表格标签

### 基础结构

```html
<table border="1">
    <caption>表格标题</caption>
    <tr>
        <th>表头1</th>
        <th>表头2</th>
    </tr>
    <tr>
        <td>数据1</td>
        <td>数据2</td>
    </tr>
</table>
```

### table属性

| 属性 | 说明 |
|------|------|
| `border` | 边框粗细（像素） |
| `width` / `height` | 宽高 |
| `align` | 表格水平对齐（left/center/right） |
| `cellpadding` | **单元格内边距** |
| `cellspacing` | **单元格间距** |
| `bgcolor` | 背景颜色 |
| `background` | 背景图片 |

### tr属性

| 属性 | 说明 |
|------|------|
| `align` | 水平对齐 |
| `valign` | 垂直对齐（top/middle/bottom） |
| `height` | 行高 |
| `bgcolor` | 背景颜色 |

### 单元格合并

```html
<!-- 跨列合并（横向） -->
<td colspan="2">合并两列</td>

<!-- 跨行合并（纵向） -->
<td rowspan="2">合并两行</td>
```

> [!tip] 合并后记得删除多余的单元格

## 六、表单标签

### form表单容器

```html
<form action="处理程序地址" method="post">
    <!-- 表单控件 -->
</form>
```

**method属性：**
- `get` - 数据附加在URL后（**不安全，有长度限制**）
- `post` - 数据放在请求体中（**相对安全，无长度限制**）

### input输入控件

| type值 | 作用 | 特殊属性 |
|--------|------|----------|
| `text` | 单行文本框 | - |
| `password` | 密码框 | - |
| `email` | 邮箱输入 | 自动验证格式 |
| `number` | 数字输入 | min, max, step |
| `radio` | **单选按钮** | name相同互斥 |
| `checkbox` | **多选按钮** | checked默认选中 |
| `file` | 文件上传 | multiple多选 |
| `hidden` | **隐藏域** | 提交但不显示 |
| `submit` | 提交按钮 | - |
| `reset` | 重置按钮 | - |
| `button` | 普通按钮 | 配合JS使用 |

```html
<!-- 单选按钮组 -->
<input type="radio" name="gender" value="male" checked> 男
<input type="radio" name="gender" value="female"> 女

<!-- 多选按钮组 -->
<input type="checkbox" name="hobby" value="reading"> 阅读
<input type="checkbox" name="hobby" value="sports"> 运动
```

### 其他表单控件

**下拉列表：**
```html
<select name="city">
    <option value="bj">北京</option>
    <option value="sh" selected>上海</option>
    <option value="gz">广州</option>
</select>
```

**文本域：**
```html
<textarea name="description" rows="4" cols="50">
多行文本内容
</textarea>
```

**按钮：**
```html
<button type="submit">提交</button>
<button type="reset">重置</button>
<button type="button">普通按钮</button>
```

### label标签

> [!important] label的for属性
> `for` 属性值与关联控件的 `id` 值一致，点击label会聚焦到对应控件

```html
<!-- 显式关联 -->
<label for="username">用户名：</label>
<input type="text" id="username" name="username">

<!-- 隐式关联 -->
<label>
    密码：
    <input type="password" name="password">
</label>
```

## 七、语义化标签（HTML5）

```html
<header>页头</header>
<nav>导航</nav>
<main>主要内容</main>
<article>文章</article>
<section>章节</section>
<aside>侧边栏</aside>
<footer>页脚</footer>
```

## 八、框架相关

### 浮动框架

```html
<iframe src="页面地址" 
        width="宽度" 
        height="高度"
        name="框架名">
</iframe>
```

> [!note] 使用a标签target跳转
> `<a href="url" target="框架名">` 可在iframe中打开页面

---

## 通用属性

所有HTML元素都支持的属性：

| 属性 | 说明 |
|------|------|
| `id` | 唯一标识（用于JS和CSS） |
| `class` | 类名（用于CSS样式） |
| `style` | 行内样式 |
| `title` | 鼠标悬停提示 |

---
*相关链接：[[00-HTML-MOC|返回知识地图]] | [[03-Meta标签详解|下一步：Meta标签]]*