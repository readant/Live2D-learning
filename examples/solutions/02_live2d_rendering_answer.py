"""
示例 02: Live2D 基础渲染 - 答案版本

这个示例展示如何在 PyQt5 中加载和渲染 Live2D 模型。
是学习 Live2D 集成的最基础代码。

学习要点：
- QOpenGLWidget 的使用
- live2d-py 库的初始化
- 模型的加载和渲染
- OpenGL 上下文管理

前置要求：
- 安装 live2d-py: pip install live2d-py
- 准备 Live2D 模型文件（.model3.json）

运行方式：
    python solutions/02_live2d_rendering_answer.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class Live2DRenderingWidget(QOpenGLWidget):
    """
    Live2D 渲染窗口组件

    使用 QOpenGLWidget 作为 Live2D 模型的渲染容器。
    QOpenGLWidget 提供了硬件加速的 OpenGL 渲染支持。

    重要方法说明：
    - initializeGL(): OpenGL 初始化，在上下文创建时调用一次
    - paintGL(): 渲染回调，每帧调用
    - resizeGL(): 窗口大小改变时调用
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self._init_ui()

    def _init_ui(self):
        """
        初始化窗口属性

        设置：
        - 无边框窗口 (FramelessWindowHint)
        - 始终置顶 (WindowStaysOnTopHint)
        - 工具窗口 (Tool) - 不显示在任务栏
        - 透明背景 (WA_TranslucentBackground)
        """
        self.setWindowTitle("示例 02: Live2D 基础渲染")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        """
        初始化 OpenGL 上下文和 Live2D 模型

        重要说明：
        1. makeCurrent() 必须首先调用，确保在正确的 OpenGL 上下文中操作
        2. live2d.init() 初始化 Live2D SDK
        3. live2d.glInit() 初始化 OpenGL 相关功能
        4. LAppModel() 创建模型实例
        5. LoadModelJson() 加载模型文件
        """
        self.makeCurrent()
        live2d.init()
        live2d.glInit()

        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)
        print(f"[Live2D] 模型加载成功: {settings.MODEL_PATH}")

        self.startTimer(33)

    def paintGL(self):
        """
        渲染回调 - 每帧调用

        渲染流程：
        1. clearBuffer() - 清空上一帧的缓冲区
        2. Update() - 更新模型的动画状态（物理演算、动作等）
        3. Draw() - 绘制模型到当前缓冲区

        这个方法会被 timer 定时调用，或者调用 update() 时触发
        """
        live2d.clearBuffer()
        if self.live2d_model:
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        """
        窗口大小改变时调用

        Args:
            w: 新的宽度
            h: 新的高度
        """
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def timerEvent(self, event):
        """
        定时器事件

        每隔 33ms（约 30 FPS）触发一次
        触发窗口重绘
        """
        self.update()

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    """
    主函数：创建并显示 Live2D 渲染窗口

    关键步骤：
    1. AA_ShareOpenGLContexts - 启用 OpenGL 上下文共享
       这对于 Live2D 渲染是必需的，避免上下文冲突
    2. setQuitOnLastWindowClosed(False) - 关闭窗口不退出程序
       对于桌宠应用很重要
    """
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = Live2DRenderingWidget()
    widget.show()

    print("=" * 50)
    print("Live2D 基础渲染示例")
    print("提示：这是一个无边框、始终置顶的窗口")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
