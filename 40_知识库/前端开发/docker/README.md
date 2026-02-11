---
title: "Docker"
date: 2024-01-15
tags: [docker, 容器化, 前端开发]
category: 知识库/前端开发/docker
status: active
aliases: [容器技术, Docker技术]
---

# Docker

> Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流行的 Linux 或 Windows 机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口。

## 概述

Docker 通过容器化技术解决了"在我机器上能运行"的问题，使得应用部署更加一致和可靠。

## 核心概念

- **镜像 (Image)** - 只读模板，包含运行应用所需的代码、库、环境变量和配置文件
- **容器 (Container)** - 镜像的运行实例，可以被创建、启动、停止、删除
- **仓库 (Repository)** - 存储和分发镜像的地方（如 Docker Hub）
- **Dockerfile** - 定义镜像构建步骤的文本文件

## 核心主题

### 基础入门
- [[docker-基础|Docker 基础]] - 安装、基本命令、常用操作
- [[docker-镜像|镜像管理]] - 镜像的搜索、下载、构建、发布
- [[docker-容器|容器操作]] - 容器的创建、启动、停止、删除

### 进阶主题
- [[docker-数据卷|数据卷]] - 容器数据持久化
- [[docker-网络|网络配置]] - 容器网络与通信
- [[docker-dockerfile|Dockerfile 构建]] - 自定义镜像构建
- [[docker-compose|Docker Compose]] - 多容器编排
- [[docker-swarm|Swarm 集群]] - 容器集群管理

## 实践案例
- [[docker-nginx|使用 Nginx]]
- [[docker-portainer|Portainer 可视化管理]]
- [[docker-redis集群|Redis 集群配置]]

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)

## 相关笔记
- [[前端开发]] - 父级领域
- [[容器化技术]] - 相关技术

## 最近更新
- [[docker-基础]] - CentOS 安装指南
- [[docker-redis集群]] - 集群配置步骤
