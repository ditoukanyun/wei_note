---
title: Java 反射
date: 2026-03-26
tags:
  - Java
  - 反射
  - 动态代理
  - 注解
---

# Java 反射

反射是 Java 的核心特性，允许程序在运行时检查和操作类、方法、字段等。

## 反射的核心价值

| 应用场景 | 说明 |
|---------|------|
| **框架开发** | Spring、Hibernate 等框架的核心技术 |
| **动态代理** | AOP、RPC 远程调用的基础 |
| **工具开发** | 测试框架、序列化工具等 |
| **解耦** | 通过配置创建对象，避免硬编码依赖 |

## 获取 Class 对象

```java
// 方式一：类名.class（编译时已知类型，最常用）
Class<String> clazz1 = String.class;

// 方式二：对象.getClass()（运行时获取）
Class<? extends String> clazz2 = "hello".getClass();

// 方式三：Class.forName()（通过全限定名，适合配置驱动）
Class<?> clazz3 = Class.forName("java.lang.String");
```

### 基本类型和数组

```java
Class<Integer> intClass = int.class;        // 基本类型
Class<Integer> integerClass = Integer.class; // 包装类型
Class<int[]> intArrayClass = int[].class;    // 数组类型
```

## 字段反射

### 获取字段

```java
Class<User> clazz = User.class;

// 获取所有 public 字段（包括继承的）
Field[] publicFields = clazz.getFields();

// 获取所有声明的字段（包括 private，不包括继承的）
Field[] allFields = clazz.getDeclaredFields();

// 获取指定字段
Field nameField = clazz.getDeclaredField("name");
```

### 读取和修改字段值

```java
User user = new User("张三", 30);

Field nameField = User.class.getDeclaredField("name");
nameField.setAccessible(true);  // 访问私有字段必须先设置

// 读取
Object value = nameField.get(user);

// 修改
nameField.set(user, "李四");
```

## 方法反射

### 获取方法

```java
// 获取所有 public 方法（包括继承的）
Method[] publicMethods = clazz.getMethods();

// 获取所有声明的方法（包括 private）
Method[] allMethods = clazz.getDeclaredMethods();

// 获取指定方法
Method setName = clazz.getMethod("setName", String.class);
```

### 调用方法

```java
User user = new User();

// 调用 public 方法
Method setName = User.class.getMethod("setName", String.class);
setName.invoke(user, "张三");

// 调用私有方法
Method privateMethod = User.class.getDeclaredMethod("privateMethod");
privateMethod.setAccessible(true);
privateMethod.invoke(user);

// 调用静态方法
Method staticMethod = User.class.getMethod("staticMethod");
staticMethod.invoke(null);  // 静态方法传入 null
```

## 构造器反射

```java
// 获取构造器
Constructor<User> constructor = User.class.getConstructor(String.class, int.class);

// 创建对象
User user = constructor.newInstance("张三", 30);

// 无参构造器快捷方式
User user = User.class.getDeclaredConstructor().newInstance();

// 调用私有构造器（单例模式的破坏点）
Constructor<User> privateConstructor = User.class.getDeclaredConstructor(String.class);
privateConstructor.setAccessible(true);
User user = privateConstructor.newInstance("李四");
```

## 动态代理

> [!important] 动态代理的核心应用
> - AOP（面向切面编程）
> - RPC 远程调用
> - 数据库连接池
> - 事务管理

### 创建动态代理

```java
// 目标对象
UserService target = new UserServiceImpl();

// 创建代理对象
UserService proxy = (UserService) Proxy.newProxyInstance(
    target.getClass().getClassLoader(),
    target.getClass().getInterfaces(),
    new InvocationHandler() {
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            // 前置处理
            System.out.println("调用方法: " + method.getName());
            
            // 调用目标方法
            Object result = method.invoke(target, args);
            
            // 后置处理
            System.out.println("返回结果: " + result);
            
            return result;
        }
    }
);

// 调用代理方法
proxy.doSomething();
```

### 日志代理示例

```java
class LoggingInvocationHandler implements InvocationHandler {
    private final Object target;
    
    public LoggingInvocationHandler(Object target) {
        this.target = target;
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        long start = System.nanoTime();
        Object result = method.invoke(target, args);
        long elapsed = System.nanoTime() - start;
        
        System.out.println(method.getName() + " 耗时: " + elapsed / 1_000_000 + "ms");
        return result;
    }
}
```

## 注解反射

```java
// 类上的注解
if (clazz.isAnnotationPresent(MyService.class)) {
    MyService annotation = clazz.getAnnotation(MyService.class);
    String value = annotation.value();
}

// 方法上的注解
Method method = clazz.getMethod("doSomething");
if (method.isAnnotationPresent(MyTransactional.class)) {
    MyTransactional tx = method.getAnnotation(MyTransactional.class);
    boolean readOnly = tx.readOnly();
}

// 字段上的注解
Field field = clazz.getDeclaredField("dependency");
if (field.isAnnotationPresent(MyAutowired.class)) {
    MyAutowired autowired = field.getAnnotation(MyAutowired.class);
    boolean required = autowired.required();
}
```

## 数组反射

```java
// 判断是否是数组
int[] array = {1, 2, 3};
boolean isArray = array.getClass().isArray();

// 获取组件类型
Class<?> componentType = array.getClass().getComponentType();

// 动态创建数组
String[] strArray = (String[]) Array.newInstance(String.class, 5);

// 动态设置和获取元素
Array.set(strArray, 0, "Hello");
Object value = Array.get(strArray, 0);
```

## 反射最佳实践

### 1. 缓存反射结果

```java
// 反射操作很慢，应该缓存 Class、Method、Field 对象
private static final Method CACHED_METHOD;

static {
    try {
        CACHED_METHOD = TargetClass.class.getMethod("methodName");
    } catch (NoSuchMethodException e) {
        throw new RuntimeException(e);
    }
}
```

### 2. 谨慎使用 setAccessible

```java
// 它会破坏封装性，可能导致安全问题
// 只在必要时使用
field.setAccessible(true);
```

### 3. 区分 getXxx 和 getDeclaredXxx

| 方法 | 范围 | 继承 |
|------|------|------|
| `getFields()` | public | 包括继承 |
| `getDeclaredFields()` | 所有 | 不包括继承 |

### 4. 反射的替代方案

| 方案 | 适用场景 |
|------|---------|
| MethodHandle | Java 7+，更快更安全 |
| VarHandle | Java 9+，访问字段 |
| Lambda | 简单方法调用 |
| 代码生成 | 高性能需求（ASM、ByteBuddy） |

## 性能警告

> [!warning] 反射比直接调用慢 10-100 倍
> 但以下场景可以接受：
> - 初始化阶段（如框架启动）
> - 低频操作（如配置加载）
> - 没有其他选择时（如框架开发）

---

> [!info] 相关链接
> - [[Java 泛型]]
> - [[Java Stream API]]
> - [[Spring 框架]]
