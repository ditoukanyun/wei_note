---
type: wiki
area: "[[前端开发]]"
tags:
  - 前端开发
  - JavaScript
  - 原型链
created: 2026-05-08
---
# Prototype

## 定义

Prototype 是 JavaScript 对象继承机制的核心概念。函数对象的 `prototype` 属性用于给通过 `new` 创建的实例提供共享方法，普通对象的内部原型用于沿着原型链查找属性。

## 要点

- `Constructor.prototype` 是实例共享方法和属性的挂载位置。
- 实例对象通过内部原型连接到构造函数的 `prototype`。
- 属性查找会先查对象自身，再沿原型链向上查找。
- `Object.create(proto)` 可以直接创建以 `proto` 为原型的对象。
- 不应随意修改内置对象原型，容易造成全局污染和兼容性问题。

## 示例

`arr.map` 并不是每个数组实例单独拥有的方法，而是来自 `Array.prototype.map`。

## 相关概念

- [[原型链]]
- [[JavaScript]]
- [[函数式编程]]
