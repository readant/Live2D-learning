# Live2D 学习仓库

面向国内自学者的专业学习仓库，提供完整的 Live2D 学习路径、实例代码和实践项目。

## 项目特点

- **本土化资源**：推荐国内可访问的学习平台和工具镜像
- **循序渐进**：从零基础到高级应用的完整学习路径
- **中文友好**：使用简洁易懂的语言解释复杂概念
- **实战驱动**：丰富的示例代码和练习项目
- **持续更新**：反映国内技术发展和教育环境的最新动态

## 功能特性

基于 PyQt5 和 Live2D 的桌面宠物程序：

- 🖱️ **鼠标跟随**：头部和眼球跟随鼠标移动
- 💨 **呼吸动画**：自动播放的待机呼吸微动
- 👋 **点击交互**：单击、双击、三击触发不同动作
- 😊 **表情切换**：开心、认真、犯困三种表情
- 🎯 **右键菜单**：快捷操作和动作测试

## 学习路径

```
├── examples/          # 示例代码（带详细注释）
├── exercises/         # 实践练习（含答案）
├── versions/          # 版本演进（从 v1 到 v5）
├── learning_notes/    # 学习笔记
└── config/            # 配置文件
```

### 示例代码 (examples/)

| 示例 | 内容 | 难度 |
|------|------|------|
| 01_basic_window | PyQt5 基础窗口 | ⭐☆☆☆☆ |
| 02_live2d_rendering | Live2D 模型渲染 | ⭐⭐☆☆☆ |
| 03_mouse_tracking | 鼠标追踪实现 | ⭐⭐⭐☆☆ |
| 04_animation | 动画系统 | ⭐⭐⭐☆☆ |
| 05_expression | 表情切换 | ⭐⭐⭐⭐☆ |
| 06_complete | 完整桌宠 | ⭐⭐⭐⭐⭐ |

### 实践练习 (exercises/)

| 练习 | 内容 | 难度 |
|------|------|------|
| 01 | 添加新表情 | ⭐⭐☆☆☆ |
| 02 | 修改鼠标跟随灵敏度 | ⭐☆☆☆☆ |
| 03 | 添加新动作 | ⭐⭐⭐☆☆ |
| 04 | 实现拖拽移动 | ⭐⭐⭐⭐☆ |

### 版本演进 (versions/)

| 版本 | 内容 | 新增功能 |
|------|------|----------|
| v1 | 基础渲染 | 模型加载、渲染循环 |
| v2 | 添加交互 | 鼠标追踪、视线跟随 |
| v3 | 添加动画 | 呼吸、眨眼、挥手 |
| v4 | 添加表情 | 表情切换、右键菜单 |
| v5 | 完整桌宠 | 拖拽移动、整合所有功能 |

## 项目结构

```
Live2D-learning/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py         # 项目设置
├── src/                    # 源代码
│   ├── core/               # 核心功能
│   │   ├── animation_controller.py   # 动画控制器
│   │   ├── interaction_controller.py # 交互控制器
│   │   └── mouse_tracker.py         # 鼠标追踪
│   ├── live2d/             # Live2D 相关
│   │   ├── expression.py   # 表情配置
│   │   ├── model.py        # 模型接口
│   │   └── renderer.py     # 渲染器
│   └── ui/                # UI 模块
│       └── desktop_pet_widget.py    # 主窗口
├── examples/               # 示例代码
├── exercises/             # 实践练习
├── versions/              # 版本演进
├── resources/              # 资源文件
│   └── models/            # Live2D 模型
├── learning_notes/        # 学习笔记
├── main.py               # 程序入口
└── requirements.txt      # 依赖清单
```

## 快速开始

### 环境要求

- Python 3.10+
- PyQt5 5.15+
- live2d-py 0.6.1+
- numpy
- PyOpenGL

### 国内镜像安装（推荐）

使用国内镜像源加速依赖安装：

```bash
# 使用清华镜像安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 运行程序

```bash
python main.py
```

## 交互说明

| 操作 | 效果 |
|------|------|
| 移动鼠标 | 头部/眼球跟随 |
| 单击头部 | 触发挥手动作 + 切换表情 |
| 单击身体 | 触发身体点击动作 |
| 双击 | 触发滑动动作 |
| 三击 | 触发下滑动作 |
| 右键菜单 | 选择表情、测试动作、退出 |

## 学习建议

### 初学者
1. 从 `examples/01_basic_window.py` 开始
2. 逐步阅读每个示例，理解核心概念
3. 完成 `exercises/` 中的练习

### 进阶学习
1. 查看 `versions/v1_basic` 到 `versions/v5_complete` 的演进
2. 理解每个版本新增的功能
3. 尝试修改代码，观察效果

### 推荐学习顺序

```
1. 阅读 learning_notes/00_学习路径指南.md
2. 阅读 learning_notes/09_国内工具配置指南.md（配置开发环境）
3. 运行 examples/ 了解各个功能
4. 完成 exercises/ 练习巩固
5. 阅读 versions/ 理解代码演进
6. 阅读 learning_notes/ 其他笔记深入学习
```

## 学习笔记

项目包含详细的学习笔记：

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | 学习路径指南.md | 从入门到进阶的完整学习路线 |
| 01 | 项目概述.md | 项目简介和技术栈 |
| 02 | 技术架构详解.md | 系统架构和核心模块 |
| 03 | Live2D_Py库集成详解.md | SDK API 和 PyQt5 集成 |
| 04 | 常见问题与解决方案.md | 错误处理和调试技巧 |
| 05 | 代码结构与规范.md | 编码规范和最佳实践 |
| 06 | 交互系统详解.md | 交互逻辑和动作管理 |
| 07 | 工具和资源汇总.md | 开发工具和学习资源 |
| 08 | 实践练习指南.md | 练习指导和答案 |
| 09 | 国内工具配置指南.md | 国内镜像和工具配置 |
| 10 | 学习笔记模板.md | 笔记记录模板 |

## 国内学习资源推荐

### 视频平台
- **Bilibili**：搜索「Live2D 教程」「PyQt5 入门」
- **抖音/快手**：搜索相关技术短视频

### 技术社区
- **掘金**：高质量技术文章和教程
- **CSDN**：全面的技术博客
- **知乎**：技术问答和经验分享

### 在线课程
- **B站大学**：免费视频课程
- **慕课网**：系统的编程课程
- **力扣**：算法练习平台

### 国内镜像
- **清华 PyPI 镜像**：`https://pypi.tuna.tsinghua.edu.cn/simple`
- **阿里 PyPI 镜像**：`https://mirrors.aliyun.com/pypi/simple/`
- **中科大 PyPI 镜像**：`https://pypi.mirrors.ustc.edu.cn/simple/`

## 学习交流

### 国内社区
- **QQ 群**：搜索「Live2D 学习」「Python 交流」相关群
- **微信群**：通过技术公众号加入
- **Discord（需特殊网络）**：Live2D 官方社区

## 模型说明

本项目使用 Live2D Cubism 4.0 模型 "Hiyori"（非商业授权）。

模型来源：[Live2D Cubism Samples](https://www.live2d.com/download/cubism-model.html)

## 许可证

本项目仅供学习交流使用。Live2D 模型遵循其各自的许可证协议。

## 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2024-01 | 初始版本发布 |
| 2024-XX | 添加国内资源推荐 |
| 2024-XX | 更新学习笔记模板 |

## 贡献指南

欢迎国内学习者一起完善这个学习仓库：

1. Fork 本仓库
2. 添加或修改学习笔记
3. 提交 Pull Request
4. 等待审核

## 致谢

- [Live2D Cubism](https://www.live2d.com/) - 2D 动画技术
- [live2d-py](https://github.com/EasyLive2D/live2d-py) - Python 绑定
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- 国内开源社区的技术分享