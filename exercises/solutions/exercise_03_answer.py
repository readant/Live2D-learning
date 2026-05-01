"""
练习 03: 添加新的点击动作 - 答案

答案说明：
展示了如何触发 Live2D 模型的不同动作。
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
        self.setWindowTitle("练习 03: 添加新动作 [答案]")
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

    def _play_motion(self, group: str, index: int = -1):
        """
        播放动作

        Args:
            group: 动作组名称（如 "Tap", "Idle", "Flick"）
            index: 动作索引，-1 表示随机播放
        """
        if not self.live2d_model:
            return

        priority = live2d.MotionPriority.FORCE.value

        if index == -1:
            self.live2d_model.StartRandomMotion(group, priority)
            print(f"[动作] 随机播放 {group} 组动作")
        else:
            self.live2d_model.StartMotion(group, index, priority)
            print(f"[动作] 播放 {group} 组第 {index} 个动作")

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        tap_menu = menu.addMenu("Tap 动作")
        action_tap_random = tap_menu.addAction("随机 Tap")
        action_tap_0 = tap_menu.addAction("Tap 动作 0")
        action_tap_1 = tap_menu.addAction("Tap 动作 1")

        idle_menu = menu.addMenu("Idle 动作")
        action_idle_random = idle_menu.addAction("随机 Idle")
        action_idle_0 = idle_menu.addAction("Idle 动作 0")

        flick_menu = menu.addMenu("Flick 动作")
        action_flick_random = flick_menu.addAction("随机 Flick")

        menu.addSeparator()
        action_info = menu.addAction("查看模型动作配置")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_tap_random:
            self._play_motion("Tap", -1)
        elif action == action_tap_0:
            self._play_motion("Tap", 0)
        elif action == action_tap_1:
            self._play_motion("Tap", 1)
        elif action == action_idle_random:
            self._play_motion("Idle", -1)
        elif action == action_idle_0:
            self._play_motion("Idle", 0)
        elif action == action_flick_random:
            self._play_motion("Flick", -1)
        elif action == action_info:
            print("提示：查看 resources/models/Hiyori.model3.json 文件")
            print("了解模型支持的动作组和动作")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 点击播放 Tap 动作
            self._play_motion("Tap", -1)
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
    print("练习 03: 添加新动作 [答案]")
    print("动作 API:")
    print("  - StartRandomMotion(group, priority): 随机播放")
    print("  - StartMotion(group, index, priority): 播放指定动作")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
