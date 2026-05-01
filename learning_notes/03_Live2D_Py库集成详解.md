# Live2D-Py 库集成详解

## 库简介

**live2d-py** 是一个基于 Python C++ API 对 Live2D Native SDK (C++) 进行封装的库，提供了在 Python 环境中直接加载和操作 Live2D 模型的能力。

### 主要特性

- ✅ 支持 Live2D Cubism 3.0+ 模型（`.model3.json`）
- ✅ 支持 Live2D Cubism 2.1 模型（`.model.json`）
- ✅ 支持 PyQt5 / PySide2 / PySide6 等 UI 框架
- ✅ 支持动作播放和回调函数
- ✅ 支持口型同步（需要音频处理）
- ✅ 跨平台支持（Windows、Linux、MacOS）

## 安装方式

### 通过 pip 安装（推荐）

```bash
pip install live2d-py
```

### 安装特定版本

```bash
pip install live2d-py==0.6.1
```

### 检查安装

```python
import live2d.v3 as live2d
print(live2d)
# 应该输出 <module 'live2d.v3'>
```

## 核心 API

### 初始化函数

#### `live2d.init()`

初始化 Live2D SDK。**必须在创建任何 Live2D 对象之前调用。**

```python
import live2d.v3 as live2d

live2d.init()  # 初始化 SDK
print("Live2D SDK 初始化成功")
```

#### `live2d.glInit()`

初始化 OpenGL 相关功能。**必须在 OpenGL 上下文中调用。**

```python
from PyQt5.QtWidgets import QOpenGLWidget

class MyWidget(QOpenGLWidget):
    def initializeGL(self):
        self.makeCurrent()
        live2d.glInit()  # 初始化 OpenGL
```

#### `live2d.setGLProperties()` (已废弃)

在某些版本中用于设置 OpenGL 属性，但新版本中已移除此函数。

### 模型操作

#### `live2d.LAppModel()`

创建 Live2D 模型实例。

```python
model = live2d.LAppModel()
print(f"模型实例: {model}")
```

#### `LoadModelJson(json_path: str) -> bool`

加载模型配置文件（`.model3.json`）。

```python
model_path = "./resources/models/hiyori.model3.json"
success = model.LoadModelJson(model_path)
print(f"模型加载{'成功' if success else '失败'}")
```

### 模型更新和绘制

#### `Update()`

更新模型状态，包括动画、物理演算等。**每帧调用一次。**

```python
def paintGL(self):
    model.Update()  # 更新模型状态
    model.Draw()    # 绘制模型
```

#### `Draw()`

绘制模型到当前 OpenGL 缓冲区。

```python
def paintGL(self):
    live2d.clearBuffer()  # 清除缓冲区
    model.Update()
    model.Draw()
```

### 参数控制

#### `SetParameterValue(name: str, value: float, weight: float = 1.0)`

设置模型参数值。

```python
# 设置头部 X 轴角度
model.SetParameterValue("ParamAngleX", 10.0)

# 设置眼球位置（权重为 0.5，表示部分影响）
model.SetParameterValue("ParamEyeBallX", 0.5, 0.5)

# 参数名称参考：
# - ParamAngleX: 头部 X 轴旋转
# - ParamAngleY: 头部 Y 轴旋转
# - ParamAngleZ: 头部 Z 轴旋转
# - ParamEyeBallX: 眼球 X 位置
# - ParamEyeBallY: 眼球 Y 位置
# - ParamBreath: 呼吸参数
```

#### `GetParameterValue(name: str) -> float`

获取模型参数的当前值。

```python
current_angle = model.GetParameterValue("ParamAngleX")
print(f"当前头部角度: {current_angle}")
```

### 动作系统

#### `StartMotion(group: str, no: int, priority: int, ...)`

播放指定动作。

```python
# 播放 Tap 动作组的第 0 个动作
model.StartMotion("Tap", 0, live2d.MotionPriority.FORCE.value)
```

#### `StartRandomMotion(group: str, priority: int, ...)`

随机播放指定动作组中的一个动作。

```python
# 随机播放 Tap 动作组
model.StartRandomMotion("Tap", live2d.MotionPriority.FORCE.value)
```

#### 动作优先级

```python
live2d.MotionPriority.NONE.value      # 无优先级
live2d.MotionPriority.IDLE.value     # 待机优先级（最低）
live2d.MotionPriority.NORMAL.value   # 普通优先级
live2d.MotionPriority.FORCE.value    # 强制优先级（最高）
```

### 交互功能

#### `Drag(x: float, y: float)`

拖拽视线跟随。

```python
def mouseMoveEvent(self, event):
    model.Drag(event.pos().x(), event.pos().y())
```

#### `Touch(x: float, y: float)`

处理点击事件，触发动作。

```python
def mousePressEvent(self, event):
    model.Touch(event.pos().x(), event.pos().y())
```

#### `HitTest(name: str, x: float, y: float) -> bool`

检测点击位置是否在指定区域。

```python
# 检测是否点击了"身体"区域
hit = model.HitTest("Body", event.pos().x(), event.pos().y())
if hit:
    print("点击了身体区域")
```

### 渲染控制

#### `clearBuffer()`

清除当前 OpenGL 缓冲区。

```python
def paintGL(self):
    live2d.clearBuffer()  # 清除上一帧
    model.Update()
    model.Draw()
```

#### `Resize(width: int, height: int)`

调整模型大小以适应窗口。

```python
def resizeGL(self, w, h):
    model.Resize(w, h)
```

## PyQt5 集成示例

### 基础集成

```python
import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt
import live2d.v3 as live2d

class Live2DWidget(QOpenGLWidget):
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.model = None

    def initializeGL(self):
        self.makeCurrent()
        live2d.init()
        live2d.glInit()
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.startTimer(33)  # 30 FPS

    def resizeGL(self, w, h):
        if self.model:
            self.model.Resize(w, h)

    def paintGL(self):
        live2d.clearBuffer()
        self.model.Update()
        self.model.Draw()

    def timerEvent(self, event):
        self.update()

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    
    widget = Live2DWidget("./model.model3.json")
    widget.show()
    
    sys.exit(app.exec_())
```

### 完整桌宠示例

参考项目源码：`src/ui/desktop_pet_widget.py`

关键点：
1. 使用 `QOpenGLWidget` 作为渲染容器
2. 在 `initializeGL()` 中初始化 live2d-py
3. 在 `paintGL()` 中更新和绘制模型
4. 通过 `mouseMoveEvent` 和 `mousePressEvent` 处理交互
5. 使用 `QTimer` 定时器驱动渲染循环

## 模型文件结构

### Cubism 3.0+ 模型（.model3.json）

```json
{
  "Version": 3,
  "FileReferences": {
    "Moc": "hiyori.moc3",
    "Textures": [
      "hiyori.4096/texture_00.png"
    ],
    "Physics": "hiyori.physics3.json",
    "Motions": {
      "Idle": [
        "motion/hiyori_m01.motion3.json"
      ],
      "Tap": [
        "motion/hiyori_m06.motion3.json"
      ]
    }
  }
}
```

### 关键文件说明

| 文件类型 | 说明 | 必需 |
|---------|------|-----|
| `.moc3` | 模型数据文件 | ✅ |
| `.model3.json` | 模型配置文件 | ✅ |
| `texture_*.png` | 纹理图集 | ✅ |
| `.physics3.json` | 物理演算配置 | ❌ |
| `*.motion3.json` | 动作文件 | ❌ |

## 参数系统详解

### 常用参数

| 参数名 | 说明 | 范围 | 示例 |
|-------|------|------|------|
| ParamAngleX | 头部 X 轴旋转 | -30 ~ 30 | 视线左右移动 |
| ParamAngleY | 头部 Y 轴旋转 | -30 ~ 30 | 视线上下移动 |
| ParamAngleZ | 头部 Z 轴旋转 | -30 ~ 30 | 头部倾斜 |
| ParamEyeBallX | 眼球 X 位置 | -1 ~ 1 | 眼球左右转动 |
| ParamEyeBallY | 眼球 Y 位置 | -1 ~ 1 | 眼球上下转动 |
| ParamBreath | 呼吸 | 0 ~ 1 | 身体起伏 |
| ParamBodyAngleX | 身体 X 轴旋转 | -10 ~ 10 | 身体左右倾斜 |

### 表情参数

| 参数名 | 说明 | 开心值 | 认真值 | 犯困值 |
|-------|------|--------|--------|--------|
| ParamEyeLOpen | 左眼睁开度 | 0.8~1.0 | 0.6~0.8 | 0.1~0.3 |
| ParamEyeROpen | 右眼睁开度 | 0.8~1.0 | 0.6~0.8 | 0.1~0.3 |
| ParamMouthOpenY | 嘴巴张开度 | 0.0~0.2 | 0.0~0.1 | 0.3~0.5 |

## 常见问题排查

### 1. OpenGL 上下文未正确设置

**错误**：`AttributeError: module 'live2d.v3' has no attribute 'glInit'`

**原因**：在非 OpenGL 上下文中调用了 `glInit()`

**解决**：
```python
def initializeGL(self):
    self.makeCurrent()  # 确保在正确的上下文中
    live2d.glInit()
```

### 2. 模型文件路径错误

**错误**：`模型加载失败` 或 `文件未找到`

**解决**：
- 使用绝对路径而非相对路径
- 检查工作目录是否正确
- 确保所有引用文件（.moc3, textures）存在

### 3. 共享 OpenGL 上下文问题

**错误**：多窗口时出现白色渲染

**解决**：
```python
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
```

### 4. 内存泄漏

**注意**：频繁创建和销毁模型可能导致内存泄漏

**解决**：
- 复用模型实例
- 在程序结束时调用 `live2d.dispose()`（如果有）

## 性能优化

### 1. 合理的帧率

```python
# 30 FPS 足够，60 FPS 可能导致性能问题
self.startTimer(33)  # 约 30 FPS
```

### 2. 避免频繁的参数设置

```python
# 不推荐：每帧设置多个参数
for i in range(10):
    model.SetParameterValue(f"Param{i}", value)

# 推荐：批量设置
model.SetParameterValue("ParamAngleX", angle_x)
model.SetParameterValue("ParamAngleY", angle_y)
```

### 3. 使用动作而非手动参数控制

Live2D SDK 的内置动作系统已经优化，直接使用动作可以获得更好的性能。

## 下一步学习

1. **动作编辑**：学习创建和编辑 Live2D 动作文件
2. **物理演算**：深入理解物理配置文件的编写
3. **口型同步**：实现音频驱动的口型动画
4. **换装系统**：实现模型换装功能
5. **Live2D Cubism Editor**：学习使用官方编辑器自定义模型