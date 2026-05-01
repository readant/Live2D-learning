"""
版本 1: 基础渲染

这个版本展示了创建 Live2D 桌宠的最小代码。
只包含最基础的窗口和模型渲染，没有任何交互功能。

学习这个版本的收获：
- 如何初始化 PyQt5 应用
- 如何创建 QOpenGLWidget
- 如何初始化 Live2D SDK
- 如何加载和渲染模型
"""

import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt
import live2d.v3 as live2d

MODEL_PATH = "./resources/models/Hiyori.model3.json"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500


class BasicWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("版本 1: 基础渲染")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.live2d_model = None

    def initializeGL(self):
        self.makeCurrent()
        live2d.init()
        live2d.glInit()
        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(MODEL_PATH)

    def paintGL(self):
        live2d.clearBuffer()
        if self.live2d_model:
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    widget = BasicWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
