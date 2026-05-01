"""
版本 2: 添加交互功能

在版本 1 的基础上添加鼠标追踪功能。
模型会跟随鼠标移动，实现视线注视效果。

新增内容：
- MouseTracker 类：追踪鼠标位置
- mouseMoveEvent：处理鼠标移动
- SetParameterValue：设置模型参数

学习这个版本的收获：
- 理解参数系统的作用
- 学会获取鼠标位置
- 实现视线跟随效果
"""

import sys
import math
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt
import live2d.v3 as live2d

MODEL_PATH = "./resources/models/Hiyori.model3.json"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500


class MouseTracker:
    """鼠标追踪器：计算注视角度"""
    def __init__(self, target_center=(200, 250)):
        self.target_center = target_center
        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0
        self.max_gaze_angle = 30

    def update(self, x, y):
        dx = x - self.target_center[0]
        dy = y - self.target_center[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            normalized = min(distance / 400, 1.0)
            self.relative_angle_x = (dx / distance) * normalized
            self.relative_angle_y = (dy / distance) * normalized
        else:
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_angles(self):
        return (
            self.relative_angle_x * self.max_gaze_angle,
            self.relative_angle_y * self.max_gaze_angle,
            self.relative_angle_x * 1.0,
            self.relative_angle_y * 1.0
        )


class InteractionWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("版本 2: 添加交互")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.live2d_model = None
        self.mouse_tracker = MouseTracker((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

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
            angles = self.mouse_tracker.get_angles()
            self.live2d_model.SetParameterValue("ParamAngleX", angles[0])
            self.live2d_model.SetParameterValue("ParamAngleY", angles[1])
            self.live2d_model.SetParameterValue("ParamEyeBallX", angles[2])
            self.live2d_model.SetParameterValue("ParamEyeBallY", angles[3])
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.update(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    widget = InteractionWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
