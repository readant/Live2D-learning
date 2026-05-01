# Live2D Learning Repository

该仓库专门设计为组织和探索Live2D学习实践的综合资源。虽然最初的主要应用重点是桌面宠物开发，但需要注意的是，其范围不仅限于桌面宠物创建。这是一个易于访问、对初学者友好的学习仓库，提供从Live2D基础概念到高级实现技术的完整学习路径，适合所有技能水平的学习者。

## 功能特性

基于 PyQt5 和 Live2D 的桌面宠物程序，支持鼠标交互、动作触发和表情切换。

- **鼠标跟随**：头部和眼球跟随鼠标移动
- **呼吸动画**：自动播放的待机呼吸微动
- **点击交互**：单击、双击、三击触发不同动作
- **表情切换**：开心、认真、犯困三种表情
- **右键菜单**：快捷操作和动作测试

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

## 模型说明

本项目使用 Live2D Cubism 4.0 模型 "Hiyori"（非商业授权）。

模型来源：[Live2D Cubism Samples](https://www.live2d.com/download/cubism-model.html)

## 学习笔记

项目包含详细的学习笔记，供参考：

- 01_项目概述.md
- 02_技术架构详解.md
- 03_Live2D_Py库集成详解.md
- 04_常见问题与解决方案.md
- 05_代码结构与规范.md
- 06_交互系统详解.md

## 许可证

本项目仅供学习交流使用。Live2D 模型遵循其各自的许可证协议。

## 致谢

- [Live2D Cubism](https://www.live2d.com/) - 2D 动画技术
- [live2d-py](https://github.com/Arkueid/live2d-py) - Python 绑定
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
