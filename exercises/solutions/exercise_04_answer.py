"""
练习 04: 实现拖拽移动功能 - 答案

答案说明：
展示了如何实现窗口拖拽功能，包括：
1. 记录拖拽开始位置
2. 检测拖拽状态
3. 更新窗口位置
4. 区分拖拽和点击
"""

import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class DraggableWidget(QOpenGLWidget):
    """
    可拖拽的桌宠窗口

    实现思路：
    1. mousePressEvent: 记录鼠标按下位置
    2. mouseMoveEvent: 计算移动距离，更新窗口位置
    3. mouseReleaseEvent: 检测是否为点击（移动距离很小）
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None

        # 拖拽状态
        self._is_dragging = False
        self._drag_start_pos = None
        self._window_start_pos = None

        # 点击检测阈值（小于这个距离认为是点击）
        self._click_threshold = 5

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 04: 拖拽移动 [答案]")
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

        开始拖拽：记录初始位置
        """
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.pos()
            self._window_start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件

        执行拖拽：计算移动距离，更新窗口位置
        """
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            # 计算鼠标移动距离
            current_pos = event.pos()
            delta = current_pos - self._drag_start_pos

            # 计算新窗口位置
            new_pos = self._window_start_pos + delta
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件

        结束拖拽：检测是否为点击
        """
        if event.button() == Qt.LeftButton:
            if self._is_dragging:
                # 计算移动距离
                release_pos = event.pos()
                delta = release_pos - self._drag_start_pos
                distance = (delta.x() ** 2 + delta.y() ** 2) ** 0.5

                # 判断是拖拽还是点击
                if distance < self._click_threshold:
                    print("[交互] 检测到点击")
                else:
                    print(f"[交互] 拖拽移动，距离: {distance:.1f}")

            # 重置拖拽状态
            self._is_dragging = False
            self._drag_start_pos = None
            self._window_start_pos = None
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
    print("练习 04: 拖拽移动 [答案]")
    print("功能：按住左键拖动窗口")
    print("改进：可以区分拖拽和点击")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
