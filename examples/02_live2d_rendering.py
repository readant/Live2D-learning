"""
示例 02: Live2D 基础渲染

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
    python 02_live2d_rendering.py
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
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self._init_ui()

    def _init_ui(self):
        """初始化窗口属性"""
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
        初始化 OpenGL 上下文

        重要：
        - 这个方法在 OpenGL 上下文首次激活时调用
        - 必须先调用 makeCurrent() 确保在正确的上下文中
        - live2d.glInit() 必须在 OpenGL 上下文中调用
        """
        self.makeCurrent()
        live2d.init()
        live2d.glInit()

        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)
        print(f"[Live2D] 模型加载成功: {settings.MODEL_PATH}")

    def paintGL(self):
        """
        渲染回调

        每帧被调用（约 60 次/秒）
        负责清空缓冲区、更新模型、绘制模型
        """
        live2d.clearBuffer()
        if self.live2d_model:
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        """窗口大小改变时调用"""
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    """
    主函数：创建并显示 Live2D 渲染窗口
    """
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = Live2DRenderingWidget()
    widget.show()

    QTimer.singleShot(16, lambda: widget.update())

    print("=" * 50)
    print("Live2D 基础渲染示例")
    print("提示：这是一个无边框、始终置顶的窗口")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
