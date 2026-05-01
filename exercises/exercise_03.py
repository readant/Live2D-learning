"""
练习 03: 添加新的点击动作

练习目标：
学习如何触发 Live2D 模型的不同动作。

练习要求：
1. 修改代码，使点击时播放不同的动作
2. 尝试播放 "Tap" 动作组的其他动作
3. 了解动作优先级的概念
4. 尝试使用 StartRandomMotion 和 StartMotion 的区别

提示：
- 使用 self.live2d_model.StartRandomMotion("Tap", priority) 随机播放 Tap 动作组
- 使用 self.live2d_model.StartMotion("Tap", index, priority) 播放指定动作
- 动作索引从 0 开始
- 查看模型文件了解有哪些动作组和动作

相关 API:
- StartRandomMotion(group, priority)
- StartMotion(group, index, priority)

答案参考：solutions/exercise_03_answer.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMenu
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class MotionWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 03: 添加新动作")
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

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_tap = menu.addAction("播放 Tap 动作")
        action_idle = menu.addAction("播放 Idle 动作")
        menu.addSeparator()
        action_info = menu.addAction("查看可用动作")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_tap:
            # TODO: 播放 Tap 动作
            # 提示：使用 StartRandomMotion("Tap", live2d.MotionPriority.FORCE.value)
            pass

        elif action == action_idle:
            # TODO: 播放 Idle 动作
            pass

        elif action == action_info:
            print("提示：查看 resources/models/Hiyori.model3.json 文件了解可用动作")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # TODO: 点击时播放动作
            # 提示：尝试不同的动作组
            pass
        super().mousePressEvent(event)

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

    widget = MotionWidget()
    widget.show()

    print("=" * 50)
    print("练习 03: 添加新动作")
    print("目标：学习如何触发 Live2D 动作")
    print("提示：右键菜单或点击窗口测试动作")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
