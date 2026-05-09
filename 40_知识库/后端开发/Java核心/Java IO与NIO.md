---
title: Java IO 与 NIO
date: 2026-03-26
tags:
  - Java
  - IO
  - NIO
  - 文件操作
---
# Java IO 与 NIO

Java IO 分为两大体系：
- **IO 流**：java.io 包，字节流和字符流
- **NIO**：java.nio 包，非阻塞 IO、文件通道、Path API

## IO 流分类

```
                 InputStream（字节输入流）
                /         |          \
      FileInputStream  ByteArrayInputStream  BufferedInputStream
      
                 OutputStream（字节输出流）
                /         |          \
     FileOutputStream  ByteArrayOutputStream  BufferedOutputStream
     
                 Reader（字符输入流）
                /         |          \
            FileReader  InputStreamReader  BufferedReader
            
                 Writer（字符输出流）
                /         |          \
            FileWriter  OutputStreamWriter  BufferedWriter
```

## 选择指南

| 场景 | 推荐选择 |
|------|---------|
| 文本文件 | Reader/Writer（字符流） |
| 二进制文件（图片、视频等） | InputStream/OutputStream（字节流） |
| 大文件复制 | FileChannel 或 BufferedInputStream |
| 文件属性操作 | Files 工具类（NIO） |

## 字节流

### 什么时候用字节流？

处理二进制数据（图片、视频、压缩包等）或不需要考虑编码的场景。

### 基本用法

```java
// 写入字节
try (FileOutputStream fos = new FileOutputStream("file.dat")) {
    byte[] data = "Hello".getBytes(StandardCharsets.UTF_8);
    fos.write(data);
}

// 读取字节（批量读取，推荐）
try (FileInputStream fis = new FileInputStream("file.dat")) {
    byte[] buffer = new byte[1024];
    int bytesRead = fis.read(buffer);
    String content = new String(buffer, 0, bytesRead, StandardCharsets.UTF_8);
}
```

### 内存中的字节流

```java
// ByteArrayInputStream：将字节数组当作输入源
byte[] source = "数据".getBytes(StandardCharsets.UTF_8);
try (ByteArrayInputStream bais = new ByteArrayInputStream(source)) {
    byte[] buffer = new byte[1024];
    int len = bais.read(buffer);
}

// ByteArrayOutputStream：写入内存
try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
    baos.write("第一行".getBytes());
    baos.write("第二行".getBytes());
    byte[] result = baos.toByteArray();
}
```

## 字符流

### 什么时候用字符流？

处理文本文件，自动处理编码转换，避免乱码问题。

### 基本用法

```java
// 写入（推荐指定编码）
try (OutputStreamWriter writer = new OutputStreamWriter(
        new FileOutputStream("file.txt"), StandardCharsets.UTF_8)) {
    writer.write("你好，世界！\n");
}

// 读取（推荐指定编码）
try (InputStreamReader reader = new InputStreamReader(
        new FileInputStream("file.txt"), StandardCharsets.UTF_8)) {
    char[] buffer = new char[1024];
    int charsRead = reader.read(buffer);
}
```

## 缓冲流

> [!tip] 性能优化
> 缓冲流减少磁盘 IO 次数，比非缓冲流快 10-100 倍

```java
// BufferedWriter
try (BufferedWriter writer = new BufferedWriter(new FileWriter("file.txt"))) {
    writer.write("第一行");
    writer.newLine();  // 跨平台的换行符
    writer.write("第二行");
}

// BufferedReader
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}

// 一行代码读取所有行
List<String> lines = Files.readAllLines(Path.of("file.txt"), StandardCharsets.UTF_8);
```

### 复制文件示例

```java
try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream(source));
     BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(target))) {
    
    byte[] buffer = new byte[8192];  // 8KB 缓冲区
    int bytesRead;
    while ((bytesRead = bis.read(buffer)) != -1) {
        bos.write(buffer, 0, bytesRead);
    }
}
```

## NIO 文件操作

### Path API

```java
Path path = Paths.get("dir", "file.txt");

path.getFileName();      // 文件名
path.getParent();        // 父目录
path.getRoot();          // 根目录
path.toAbsolutePath();   // 绝对路径
```

### Files 工具类

```java
Path path = Path.of("file.txt");

// 创建
Files.createFile(path);
Files.createDirectories(Path.of("dir/subdir"));

// 读写（最简单的方式）
Files.writeString(path, "内容", StandardCharsets.UTF_8);
String content = Files.readString(path, StandardCharsets.UTF_8);

// 逐行读取（适合大文件）
try (Stream<String> lines = Files.lines(path)) {
    lines.forEach(System.out::println);
}

// 文件属性
Files.exists(path);
Files.size(path);
Files.isDirectory(path);
Files.isRegularFile(path);

// 复制、移动、删除
Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING);
Files.move(source, target);
Files.delete(path);
```

### 遍历目录

```java
// 列出直接子项
try (Stream<Path> paths = Files.list(dir)) {
    paths.forEach(System.out::println);
}

// 递归遍历
Files.walkFileTree(dir, new SimpleFileVisitor<>() {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
        System.out.println("文件: " + file);
        return FileVisitResult.CONTINUE;
    }
});
```

## 对象序列化

### 实现序列化

```java
public class Person implements Serializable {
    private static final long serialVersionUID = 1L;  // 版本兼容
    
    private String name;
    private transient String password;  // 不参与序列化
    
    // ...
}
```

### 序列化与反序列化

```java
// 序列化
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("person.ser"))) {
    oos.writeObject(person);
}

// 反序列化
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("person.ser"))) {
    Person restored = (Person) ois.readObject();
}
```

> [!warning] 建议
> 推荐使用 JSON/Protobuf 替代 Java 原生序列化，更安全、跨语言。

## RandomAccessFile

可以随机读写文件任意位置，适合断点续传、文件分片、索引文件。

```java
try (RandomAccessFile raf = new RandomAccessFile("file.dat", "rw")) {
    // 写入
    raf.writeInt(12345);       // 4 bytes
    raf.writeDouble(3.14);     // 8 bytes
    
    // 随机读取
    raf.seek(0);               // 移动到开头
    int value = raf.readInt();
    
    raf.seek(4);               // 移动到 double 位置
    double d = raf.readDouble();
    
    // 追加
    raf.seek(raf.length());
    raf.writeUTF("追加内容");
}
```

## 最佳实践

### 1. 始终使用 try-with-resources

```java
// ✅ 自动关闭资源
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    // 使用 reader
}

// ❌ 手动关闭容易遗漏
BufferedReader reader = null;
try {
    reader = new BufferedReader(new FileReader("file.txt"));
    // ...
} finally {
    if (reader != null) reader.close();
}
```

### 2. 始终指定编码

```java
// ❌ 使用默认编码，可能乱码
new FileReader("file.txt")

// ✅ 明确指定编码
new InputStreamReader(new FileInputStream("file.txt"), StandardCharsets.UTF_8)
```

### 3. 选择正确的流

| 需求 | 选择 |
|------|------|
| 小文本文件 | Files.readString / Files.writeString |
| 大文本文件 | BufferedReader + Files.lines |
| 二进制文件 | BufferedInputStream / BufferedOutputStream |
| 对象持久化 | JSON 库（如 Jackson） |
| 随机访问 | RandomAccessFile |

---

> [!info] 相关链接
> - [[Java 集合框架]]
> - [[Java 反射]]

## 实践检查清单

- 文本读写是否显式指定字符编码。
- 文件、流、Channel 是否使用 try-with-resources 关闭。
- 大文件是否避免一次性读入内存。
- 阻塞 IO、NIO、异步 IO 的选择是否匹配并发模型。
- 序列化输入是否来自可信来源，避免反序列化安全风险。

## 案例

导入 2GB 日志文件时，不应使用 `Files.readAllLines` 一次性加载。更稳妥的方式是使用 `BufferedReader` 或 `Files.lines` 流式处理，并在每批处理后记录进度，方便失败恢复。

## 常见误区

- 使用系统默认编码，部署到不同系统后出现乱码。
- 手动关闭资源遗漏异常分支，导致文件句柄泄漏。
- 用 Java 原生序列化做跨服务协议，带来兼容性和安全问题。
