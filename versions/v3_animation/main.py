"""
版本 3: 添加动画系统

在版本 2 的基础上添加动画功能。
实现呼吸动画、眨眼动画和挥手动画。

新增内容：
- AnimationController 类：管理所有动画
- 呼吸动画：使用正弦波实现
- 眨眼动画：使用状态机实现
- 挥手动画：点击触发

学习这个版本的收获：
- 理解定时器驱动动画的原理
- 学会使用正弦波实现平滑动画
- 掌握状态机的设计方法
"""

import sys
import math
import time
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

MODEL_PATH = "./resources/models/Hiyori.model3.json"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
FPS = 30


class MouseTracker:
    """鼠标追踪器"""
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


class AnimationController:
    """动画控制器：管理呼吸、眨眼、挥手动画"""
    def __init__(self, model=None):
        self.model = model
        self.breath_timer = 0.0
        self.blink_timer = 0.0
        self.wave_timer = 0.0
        self.is_waving = False
        self.wave_duration = 2.0
        self.blink_interval = 3.0
        self.is_blinking = False
        self.blink_duration = 0.1

    def update(self, delta_time):
        self._update_breath(delta_time)
        self._update_blink(delta_time)
        self._update_wave(delta_time)

    def _update_breath(self, delta_time):
        self.breath_timer += delta_time
        breath_progress = (self.breath_timer % 3.0) / 3.0
        breath_value = (math.sin(breath_progress * 2 * math.pi) + 1) / 2
        if self.model:
            self.model.SetParameterValue("ParamBreath", breath_value)

    def _update_blink(self, delta_time):
        if not self.is_blinking:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.is_blinking = True
                self.blink_timer = 0.0
        else:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_duration:
                self.is_blinking = False
                self.blink_timer = 0.0
        if self.model:
            if self.is_blinking:
                self.model.SetParameterValue("ParamEyeLOpen", 0.0)
                self.model.SetParameterValue("ParamEyeROpen", 0.0)
            else:
                self.model.SetParameterValue("ParamEyeLOpen", 1.0)
                self.model.SetParameterValue("ParamEyeROpen", 1.0)

    def _update_wave(self, delta_time):
        if self.is_waving:
            self.wave_timer += delta_time
            if self.wave_timer < self.wave_duration:
                progress = self.wave_timer / self.wave_duration
                arm_value = -30 - 20 * (1 - abs(2 * progress - 1))
                self.model.SetParameterValue("ParamArmLA", arm_value)
                self.model.SetParameterValue("ParamArmRA", arm_value)
            else:
                self.is_waving = False
                self.wave_timer = 0.0
                self.model.SetParameterValue("ParamArmLA", 0.0)
                self.model.SetParameterValue("ParamArmRA", 0.0)

    def trigger_wave(self):
        if not self.is_waving:
            self.is_waving = True
            self.wave_timer = 0.0


class AnimationWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("版本 3: 添加动画")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.live2d_model = None
        self.mouse_tracker = MouseTracker((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.animation_controller = None

    def initializeGL(self):
        self.makeCurrent()
        live2d.init()
        live2d.glInit()
        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(MODEL_PATH)
        self.animation_controller = AnimationController(self.live2d_model)
        self.startTimer(1000 // FPS)

    def paintGL(self):
        live2d.clearBuffer()
        if self.live2d_model:
            delta_time = 1.0 / FPS
            self.animation_controller.update(delta_time)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.animation_controller.trigger_wave()
        super().mousePressEvent(event)

    def timerEvent(self, event):
        self.update()


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    widget = AnimationWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
