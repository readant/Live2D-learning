"""
练习 02: 修改鼠标跟随灵敏度 - 答案

答案说明：
提供了几组不同的参数配置供选择，并解释了每个参数的影响。

调整建议：
- max_gaze_angle = 20: 更保守的跟随，适合需要克制的场景
- max_gaze_angle = 40: 更夸张的跟随，适合可爱的场景
- max_distance = 200: 更灵敏，距离较近就开始跟随
- max_distance = 500: 更迟钝，需要移动更远才开始跟随
"""

import sys
import math
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
import live2d.v3 as live2d

from config import settings


class MouseTracker:
    """
    鼠标追踪器

    参数调整指南：
    1. max_gaze_angle: 最大注视角度
       - 值越大，头部转动角度越大
       - 推荐范围：20-50
       - 太大可能导致不自然

    2. max_distance: 最大有效距离
       - 值越小，越灵敏（靠近中心就开始跟随）
       - 推荐范围：200-500
       - 需要根据窗口大小调整

    3. gaze_smoothing: 平滑系数（当前未使用）
       - 值越小，移动越平滑
       - 可以用于实现缓动效果
    """

    def __init__(self, target_center=(200, 250)):
        self.target_center = target_center
        self.mouse_pos = QPoint(0, 0)

        # ========== 推荐配置 ==========
        # 配置 A: 默认配置
        # self.max_gaze_angle = 30
        # self.max_distance = 400

        # 配置 B: 高灵敏度
        # self.max_gaze_angle = 45
        # self.max_distance = 300

        # 配置 C: 低灵敏度
        # self.max_gaze_angle = 20
        # self.max_distance = 500

        # 选择一个配置：
        self.max_gaze_angle = 45      # 尝试 40-50
        self.max_distance = 300        # 尝试 200-400

        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0

    def update_mouse_position(self, x: int, y: int) -> None:
        """更新鼠标位置并计算角度"""
        self.mouse_pos = QPoint(x, y)

        dx = x - self.target_center[0]
        dy = y - self.target_center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            normalized_distance = min(distance / self.max_distance, 1.0)
            self.relative_angle_x = (dx / distance) * normalized_distance
            self.relative_angle_y = (dy / distance) * normalized_distance
        else:
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_gaze_angles(self):
        """获取注视角度"""
        angle_x = self.relative_angle_x * self.max_gaze_angle
        angle_y = self.relative_angle_y * self.max_gaze_angle
        eye_x = self.relative_angle_x * 1.0
        eye_y = self.relative_angle_y * 1.0
        return angle_x, angle_y, eye_x, eye_y


class MouseTrackingWidget(QOpenGLWidget):
    """鼠标追踪窗口"""

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.mouse_tracker = MouseTracker(
            (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2)
        )
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 02: 修改鼠标跟随灵敏度 [答案]")
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

            angles = self.mouse_tracker.get_gaze_angles()
            self.live2d_model.SetParameterValue("ParamAngleX", angles[0])
            self.live2d_model.SetParameterValue("ParamAngleY", angles[1])
            self.live2d_model.SetParameterValue("ParamEyeBallX", angles[2])
            self.live2d_model.SetParameterValue("ParamEyeBallY", angles[3])

            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.update_mouse_position(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)

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

    widget = MouseTrackingWidget()
    widget.show()

    print("=" * 50)
    print("练习 02: 修改鼠标跟随灵敏度 [答案]")
    print("当前参数：")
    print("  - max_gaze_angle: 45")
    print("  - max_distance: 300")
    print("提示：尝试不同的配置，找到最适合的效果")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
