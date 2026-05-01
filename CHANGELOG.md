# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2024-05-01

### Added

- **项目基础结构**
  - 模块化项目架构 (config/src/ui)
  - 基于 PyQt5 的无标题栏窗口实现
  - OpenGL 渲染支持

- **核心功能**
  - 鼠标追踪实现头部/眼球跟随
  - 呼吸动画控制器
  - 交互控制器 (单击/双击/三击检测)
  - 动作优先级与冷却系统
  - 表情切换 (开心/认真/犯困)
  - 右键菜单系统

- **文档**
  - 项目概述
  - 技术架构详解
  - Live2D_Py 库集成详解
  - 常见问题与解决方案
  - 代码结构与规范
  - 交互系统详解

### Dependencies

- PyQt5 >= 5.15.0
- numpy >= 1.20.0
- live2d-py >= 0.6.1
- PyOpenGL >= 3.1.0

### Model

- Live2D Cubism 4.0 Model "Hiyori" (non-commercial license)