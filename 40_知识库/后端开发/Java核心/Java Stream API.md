---
title: Java Stream API
date: 2026-03-26
tags:
  - Java
  - Stream
  - 函数式编程
  - Lambda
---

# Java Stream API

Stream API 是 Java 8 引入的函数式数据处理框架，以声明式方式处理集合数据，代码简洁、可读性强、易于并行化。

## Stream 处理流程

```
数据源 → 中间操作（链式调用）→ 终端操作

例如：
list.stream()           // 数据源
    .filter(...)        // 中间操作
    .map(...)           // 中间操作
    .sorted(...)        // 中间操作
    .collect(...);      // 终端操作
```

## Stream 特点

| 特点 | 说明 |
|------|------|
| **不存储数据** | 不是数据结构，只是数据的视图 |
| **惰性求值** | 中间操作不会立即执行，直到终端操作触发 |
| **一次性** | 每个 Stream 只能消费一次 |
| **可能无限** | 可以通过 iterate/generate 创建无限流 |

## 创建 Stream

```java
// 从集合
List<String> list = Arrays.asList("a", "b", "c");
Stream<String> stream1 = list.stream();
Stream<String> parallelStream = list.parallelStream();

// 从数组
String[] array = {"x", "y", "z"};
Stream<String> stream2 = Arrays.stream(array);

// 使用 Stream.of()
Stream<String> stream3 = Stream.of("1", "2", "3");

// 无限流 - iterate
Stream<Integer> iterate = Stream.iterate(0, n -> n + 1)
        .limit(5);  // 必须限制数量！

// 无限流 - generate
Stream<Double> random = Stream.generate(Math::random)
        .limit(3);
```

## 中间操作

### filter：过滤

```java
List<Integer> evens = numbers.stream()
        .filter(n -> n % 2 == 0)
        .collect(Collectors.toList());
```

### map：映射/转换

```java
List<String> squares = numbers.stream()
        .map(n -> n + "²=" + n * n)
        .collect(Collectors.toList());
```

### flatMap：扁平化映射

```java
List<List<Integer>> nested = Arrays.asList(
        Arrays.asList(1, 2),
        Arrays.asList(3, 4)
);

List<Integer> flattened = nested.stream()
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
// 结果：[1, 2, 3, 4]
```

### sorted：排序

```java
// 自然排序
list.stream().sorted()

// 自定义排序
persons.stream()
        .sorted(Comparator.comparing(Person::getAge).reversed())
```

### limit / skip

```java
// limit：限制数量
list.stream().limit(3)

// skip：跳过元素
list.stream().skip(5)

// 分页效果
list.stream()
        .skip((page - 1) * size)
        .limit(size)
```

## 终端操作

### forEach / count / min / max

```java
list.stream().forEach(System.out::println);

long count = list.stream().count();

Optional<Integer> min = list.stream().min(Integer::compareTo);
Optional<Integer> max = list.stream().max(Integer::compareTo);
```

### reduce：归约

```java
// 求和
int sum = numbers.stream().reduce(0, Integer::sum);

// 无初始值（返回 Optional）
Optional<Integer> sum = numbers.stream().reduce(Integer::sum);
```

### 匹配操作

```java
boolean anyMatch = list.stream().anyMatch(n -> n > 3);  // 任意匹配
boolean allMatch = list.stream().allMatch(n -> n > 0);  // 全部匹配
boolean noneMatch = list.stream().noneMatch(n -> n < 0); // 全不匹配
```

### 查找操作

```java
Optional<Integer> first = list.stream().findFirst();  // 第一个
Optional<Integer> any = list.stream().findAny();      // 任意一个（并行流）
```

## Collector 收集器

### 收集到集合

```java
List<String> list = stream.collect(Collectors.toList());
Set<String> set = stream.collect(Collectors.toSet());
LinkedList<String> linked = stream.collect(Collectors.toCollection(LinkedList::new));
```

### 收集到 Map

```java
Map<String, Integer> map = persons.stream()
        .collect(Collectors.toMap(
                Person::getName,
                Person::getAge,
                (existing, replacement) -> existing  // 键冲突处理
        ));
```

### 分组

```java
// 按年龄分组
Map<Integer, List<Person>> byAge = persons.stream()
        .collect(Collectors.groupingBy(Person::getAge));

// 分组后计数
Map<Integer, Long> countByAge = persons.stream()
        .collect(Collectors.groupingBy(
                Person::getAge,
                Collectors.counting()
        ));
```

### 分区

```java
// 按条件分为两组
Map<Boolean, List<Person>> partitioned = persons.stream()
        .collect(Collectors.partitioningBy(p -> p.getAge() >= 30));
```

### 连接字符串

```java
String joined = names.stream()
        .collect(Collectors.joining(", ", "[", "]"));
// 结果：[a, b, c]
```

### 聚合统计

```java
IntSummaryStatistics stats = persons.stream()
        .collect(Collectors.summarizingInt(Person::getAge));

stats.getCount();     // 数量
stats.getSum();       // 总和
stats.getMin();       // 最小值
stats.getMax();       // 最大值
stats.getAverage();   // 平均值
```

## 并行流

### 何时使用并行流？

| 条件 | 说明 |
|------|------|
| 数据量大 | 建议 > 10000 |
| 操作耗时 | CPU 密集型 |
| 无状态 | 操作无顺序依赖 |
| 易拆分 | ArrayList > LinkedList |

### 使用方式

```java
// 方式一：parallelStream()
list.parallelStream()

// 方式二：parallel()
list.stream().parallel()

// 检查是否并行
stream.isParallel()

// 切回串行
stream.sequential()
```

### 并行流陷阱

```java
// ❌ 错误：线程不安全
List<Integer> unsafe = new ArrayList<>();
list.parallelStream().forEach(unsafe::add);

// ✅ 正确：使用 collect
List<Integer> safe = list.parallelStream().collect(Collectors.toList());
```

## 原始类型流

```java
// IntStream、LongStream、DoubleStream 避免装箱拆箱开销

IntStream intStream = IntStream.range(1, 6);      // [1, 6)
IntStream closed = IntStream.rangeClosed(1, 5);   // [1, 5]

// 特有聚合方法
intStream.sum();
intStream.average();
intStream.max();

// 统计信息
IntSummaryStatistics stats = intStream.summaryStatistics();

// 装箱
Stream<Integer> boxed = intStream.boxed();

// 拆箱
IntStream unboxed = Stream.of(1, 2, 3).mapToInt(Integer::intValue);
```

## 最佳实践

### 1. 使用方法引用简化代码

```java
// ❌ 不推荐
list.stream().map(n -> n.toString())

// ✅ 推荐
list.stream().map(Object::toString)
```

### 2. 使用 Optional 避免 NPE

```java
Integer result = list.stream()
        .filter(n -> n > 100)
        .findFirst()
        .orElse(0);
```

### 3. 复杂流拆分为多个步骤

```java
// ✅ 推荐：中间变量增加可读性
Stream<Integer> filtered = numbers.stream().filter(n -> n > 3);
Stream<Integer> doubled = filtered.map(n -> n * 2);
List<Integer> result = doubled.collect(Collectors.toList());
```

### 4. 使用原始类型流避免装箱

```java
// ❌ 不推荐
int sum = numbers.stream().reduce(0, Integer::sum);

// ✅ 推荐
int sum = numbers.stream().mapToInt(Integer::intValue).sum();
```

---

> [!info] 相关链接
> - [[Java 集合框架]]
> - [[Java 泛型]]
> - [[Java Lambda 表达式]]
