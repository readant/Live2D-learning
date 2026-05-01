"""
练习 04: 实现拖拽移动功能

练习目标：
学习如何让桌宠窗口可以被拖拽移动。

练习要求：
1. 实现窗口拖拽功能，让用户可以移动桌宠位置
2. 使用鼠标按下、移动、松开来实现拖拽
3. 确保拖拽时不会误触发其他点击事件

提示：
- 重写 mousePressEvent, mouseMoveEvent, mouseReleaseEvent
- 使用 self.pos() 获取窗口当前位置
- 使用 event.globalPos() 获取鼠标全局位置
- 使用 self.move(x, y) 移动窗口

思考问题：
- 如何区分拖拽和点击？
- 拖拽时需要考虑边界限制吗？

答案参考：solutions/exercise_04_answer.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class DraggableWidget(QOpenGLWidget):
    """
    可拖拽的桌宠窗口

    TODO: 实现拖拽功能
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None

        # TODO: 添加拖拽状态变量
        # self._is_dragging = False
        # self._drag_start_pos = None

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 04: 拖拽移动")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        self.makeCurrent()
        live2d.init()
        live2d.glInit()
        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)
        self.startTimer(33)

    def paintGL(self):
        live2d.clearBuffer()
        if self.live2d_model:
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mousePressEvent(self, event):
        """
        鼠标按下事件

        TODO: 实现以下功能
        1. 记录拖拽开始位置
        2. 设置拖拽状态为 True
        """
        if event.button() == Qt.LeftButton:
            # TODO: 实现拖拽开始
            pass
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件

        TODO: 实现以下功能
        1. 检查是否在拖拽状态
        2. 计算鼠标移动距离
        3. 更新窗口位置
        """
        # TODO: 实现拖拽移动
        pass

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件

        TODO: 实现以下功能
        1. 检查释放的是左键
        2. 重置拖拽状态
        3. 检测是否为点击（移动距离很小）
        """
        if event.button() == Qt.LeftButton:
            # TODO: 实现点击检测和状态重置
            pass
        super().mouseReleaseEvent(event)

    def timerEvent(self, event):
        self.update()

    def closeEvent(self, event):
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = DraggableWidget()
    widget.show()

    print("=" * 50)
    print("练习 04: 拖拽移动")
    print("目标：实现窗口拖拽功能")
    print("提示：按住左键拖动窗口")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
