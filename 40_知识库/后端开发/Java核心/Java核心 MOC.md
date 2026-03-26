---
title: Java 核心 MOC
date: 2026-03-26
tags:
  - Java
  - MOC
---

# Java 核心 MOC

Java 核心知识体系索引。

## 知识图谱

```mermaid
graph TD
    A[Java 核心] --> B[集合框架]
    A --> C[泛型]
    A --> D[IO/NIO]
    A --> E[反射]
    A --> F[Stream API]
    
    B --> B1[List]
    B --> B2[Set]
    B --> B3[Map]
    B --> B4[Queue]
    
    C --> C1[泛型类]
    C --> C2[泛型方法]
    C --> C3[通配符]
    C --> C4[类型擦除]
    
    D --> D1[字节流]
    D --> D2[字符流]
    D --> D3[NIO Files]
    D --> D4[序列化]
    
    E --> E1[Class 对象]
    E --> E2[Field/Method]
    E --> E3[动态代理]
    E --> E4[注解反射]
    
    F --> F1[中间操作]
    F --> F2[终端操作]
    F --> F3[Collector]
    F --> F4[并行流]
```

## 核心笔记

| 主题 | 说明 | 链接 |
|------|------|------|
| 集合框架 | List/Set/Map/Queue 数据结构 | [[Java 集合框架]] |
| 泛型 | 类型安全、PECS 原则 | [[Java 泛型]] |
| IO 与 NIO | 字节流、字符流、文件操作 | [[Java IO与NIO]] |
| 反射 | 动态代理、注解处理 | [[Java 反射]] |
| Stream API | 函数式数据处理 | [[Java Stream API]] |

## 学习路径

### 入门阶段

1. [[Java 集合框架]] - 掌握常用集合的选择和使用
2. [[Java 泛型]] - 理解类型安全和通配符
3. [[Java Stream API]] - 学习函数式数据处理

### 进阶阶段

4. [[Java IO与NIO]] - 文件操作和网络 IO
5. [[Java 反射]] - 框架开发基础

## 快速参考

### 集合选择指南

| 需求 | 选择 |
|------|------|
| 索引访问 | ArrayList |
| 频繁增删 | LinkedList |
| 去重 | HashSet |
| 排序 | TreeSet |
| 键值对 | HashMap |
| 线程安全 | ConcurrentHashMap |

### Stream 操作速查

| 操作类型 | 常用方法 |
|---------|---------|
| 中间操作 | filter, map, flatMap, sorted, distinct, limit, skip |
| 终端操作 | collect, forEach, reduce, count, min, max, anyMatch |
| 收集器 | toList, toSet, toMap, groupingBy, partitioningBy, joining |

### IO 选择指南

| 场景 | 选择 |
|------|------|
| 文本文件 | BufferedReader/Writer |
| 二进制文件 | BufferedInputStream/OutputStream |
| 简单读写 | Files.readString/writeString |
| 随机访问 | RandomAccessFile |

---

> [!info] 相关链接
> - [[后端开发 MOC]]
