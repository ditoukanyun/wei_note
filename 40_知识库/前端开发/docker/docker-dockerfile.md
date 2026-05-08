---
type: wiki
area: "[[前端开发]]"
tags:
  - Docker
  - Dockerfile
created: 2026-05-08
---
# docker-dockerfile

Dockerfile 是构建 Docker 镜像的声明文件，描述基础镜像、依赖安装、文件复制、构建命令和启动命令。

## 要点

- 多阶段构建可减少最终镜像体积。
- 依赖安装层应尽量利用缓存。
- 不要把密钥写进镜像。

## 相关概念

- [[Docker]]
- [[docker-镜像]]
