"""
版本 5: 完整桌宠

这是最终的完整版本，整合了所有功能。
包括：渲染、交互、动画、表情、拖拽移动。

这个版本可以直接作为桌宠使用。

学习这个版本的收获：
- 理解完整项目的架构设计
- 掌握模块化开发方法
- 了解如何整合多个功能
"""

import sys
import math
import time
from enum import Enum
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMenu
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

MODEL_PATH = "./resources/models/Hiyori.model3.json"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
FPS = 30


class Expression(Enum):
    HAPPY = "happy"
    SERIOUS = "serious"
    SLEEPY = "sleepy"


EXPRESSION_CONFIGS = {
    Expression.HAPPY: {
        "ParamEyeLSmile": 0.8,
        "ParamEyeRSmile": 0.8,
        "ParamMouthForm": 0.5,
        "ParamMouthOpenY": 0.3,
        "ParamCheek": 0.6,
    },
    Expression.SERIOUS: {
        "ParamEyeLSmile": -0.4,
        "ParamEyeRSmile": -0.4,
        "ParamBrowLForm": 0.7,
        "ParamBrowRForm": 0.7,
        "ParamMouthForm": -0.4,
        "ParamMouthOpenY": 0.0,
        "ParamCheek": 0.0,
    },
    Expression.SLEEPY: {
        "ParamEyeLOpen": 0.2,
        "ParamEyeROpen": 0.2,
        "ParamMouthOpenY": 0.5,
        "ParamCheek": 0.1,
    },
}


class MouseTracker:
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


class DesktopPetWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("版本 5: 完整桌宠")
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
        self.current_expression = Expression.HAPPY

        self._is_dragging = False
        self._drag_start_pos = None
        self._window_start_pos = None
        self._click_threshold = 5

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
            self._apply_expression(self.current_expression)
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

    def _apply_expression(self, expression):
        config = EXPRESSION_CONFIGS.get(expression, {})
        for param_name, value in config.items():
            self.live2d_model.SetParameterValue(param_name, value)

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            current_pos = event.pos()
            delta = current_pos - self._drag_start_pos
            new_pos = self._window_start_pos + delta
            self.move(new_pos)
        else:
            self.mouse_tracker.update(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.pos()
            self._window_start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_dragging:
                release_pos = event.pos()
                delta = release_pos - self._drag_start_pos
                distance = (delta.x() ** 2 + delta.y() ** 2) ** 0.5
                if distance < self._click_threshold:
                    self.animation_controller.trigger_wave()
                    expressions = list(Expression)
                    current_index = expressions.index(self.current_expression)
                    next_index = (current_index + 1) % len(expressions)
                    self.current_expression = expressions[next_index]
            self._is_dragging = False
            self._drag_start_pos = None
            self._window_start_pos = None
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        expression_menu = menu.addMenu("切换表情")
        action_happy = expression_menu.addAction("开心")
        action_serious = expression_menu.addAction("认真")
        action_sleepy = expression_menu.addAction("犯困")
        menu.addSeparator()
        action_exit = menu.addAction("退出")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_happy:
            self.current_expression = Expression.HAPPY
        elif action == action_serious:
            self.current_expression = Expression.SERIOUS
        elif action == action_sleepy:
            self.current_expression = Expression.SLEEPY
        elif action == action_exit:
            self.close()

    def timerEvent(self, event):
        self.update()


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = DesktopPetWidget()
    widget.show()

    print("=" * 50)
    print("版本 5: 完整桌宠")
    print("功能：")
    print("  - 拖拽移动")
    print("  - 鼠标注视")
    print("  - 呼吸/眨眼动画")
    print("  - 点击挥手/切换表情")
    print("  - 右键菜单")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
