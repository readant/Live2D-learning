# Live2D Learning Repository

该仓库专门设计为组织和探索Live2D学习实践的综合资源。虽然最初的主要应用重点是桌面宠物开发，但需要注意的是，其范围不仅限于桌面宠物创建。这是一个易于访问、对初学者友好的学习仓库，提供从Live2D基础概念到高级实现技术的完整学习路径，适合所有技能水平的学习者。

## 功能特性

基于 PyQt5 和 Live2D 的桌面宠物程序，支持鼠标交互、动作触发和表情切换。

- **鼠标跟随**：头部和眼球跟随鼠标移动
- **呼吸动画**：自动播放的待机呼吸微动
- **点击交互**：单击、双击、三击触发不同动作
- **表情切换**：开心、认真、犯困三种表情
- **右键菜单**：快捷操作和动作测试

## 学习路径

```
├── examples/          # 大示例（带详细注释和答案）
├── exercises/         # 实践练习（4个练习 + 答案）
├── versions/          # 版本演进（从 v1 到 v5）
└── learning_notes/    # 学习笔记（8篇）
```

### 示例代码 (examples/)

6 个从简到繁的大示例，配有关键注释和答案版本：

| 示例 | 内容 | 难度 |
|------|------|------|
| 01_basic_window | PyQt5 基础窗口 | ⭐☆☆☆☆ |
| 02_live2d_rendering | Live2D 模型渲染 | ⭐⭐☆☆☆ |
| 03_mouse_tracking | 鼠标追踪实现 | ⭐⭐⭐☆☆ |
| 04_animation | 动画系统 | ⭐⭐⭐☆☆ |
| 05_expression | 表情切换 | ⭐⭐⭐⭐☆ |
| 06_complete | 完整桌宠 | ⭐⭐⭐⭐⭐ |

### 实践练习 (exercises/)

4 个动手练习，配有提示和完整答案：

| 练习 | 内容 | 难度 |
|------|------|------|
| 01 | 添加新表情 | ⭐⭐☆☆☆ |
| 02 | 修改鼠标跟随灵敏度 | ⭐☆☆☆☆ |
| 03 | 添加新动作 | ⭐⭐⭐☆☆ |
| 04 | 实现拖拽移动 | ⭐⭐⭐⭐☆ |

### 版本演进 (versions/)

5 个版本的代码演进，展示从零构建桌宠的过程：

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
├── examples/               # 大示例代码
│   ├── 01_basic_window.py
│   ├── 02_live2d_rendering.py
│   ├── ...
│   └── solutions/         # 示例答案
├── exercises/             # 实践练习
│   ├── exercise_01.py
│   ├── exercise_02.py
│   ├── ...
│   └── solutions/         # 练习答案
├── versions/              # 版本演进
│   ├── v1_basic/
│   ├── v2_interaction/
│   ├── v3_animation/
│   ├── v4_expression/
│   └── v5_complete/
├── resources/              # 资源文件
│   └── models/            # Live2D 模型
│       ├── Hiyori.model3.json
│       └── motion/        # 动作文件
├── learning_notes/        # 学习笔记
├── main.py               # 程序入口
└── requirements.txt      # 依赖清单
```

## 环境要求

- Python 3.10+
- PyQt5 5.15+
- live2d-py 0.6.1+
- numpy
- PyOpenGL

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

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
2. 运行 examples/ 了解各个功能
3. 完成 exercises/ 练习巩固
4. 阅读 versions/ 理解代码演进
5. 阅读 learning_notes/ 其他笔记深入学习
```

## 学习笔记

项目包含详细的学习笔记，供参考：

- 00_学习路径指南.md - 从入门到进阶的完整学习路线
- 01_项目概述.md - 项目简介和技术栈
- 02_技术架构详解.md - 系统架构和核心模块
- 03_Live2D_Py库集成详解.md - SDK API 和 PyQt5 集成
- 04_常见问题与解决方案.md - 错误处理和调试技巧
- 05_代码结构与规范.md - 编码规范和最佳实践
- 06_交互系统详解.md - 交互逻辑和动作管理
- 07_工具和资源汇总.md - 开发工具和学习资源
- 08_实践练习指南.md - 练习指导和答案

## 模型说明

本项目使用 Live2D Cubism 4.0 模型 "Hiyori"（非商业授权）。

模型来源：[Live2D Cubism Samples](https://www.live2d.com/download/cubism-model.html)

## 许可证

本项目仅供学习交流使用。Live2D 模型遵循其各自的许可证协议。

## 致谢

- [Live2D Cubism](https://www.live2d.com/) - 2D 动画技术
- [live2d-py](https://github.com/Arkueid/live2d-py) - Python 绑定
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
