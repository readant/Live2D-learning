"""
示例 06: 完整桌宠实现

这个示例展示了如何将所有功能组合在一起，创建一个完整的桌面宠物程序。

学习要点：
- 模块组合
- 系统架构设计
- 代码组织
- 功能集成

这个示例整合了：
- 02_live2d_rendering: Live2D 模型渲染
- 03_mouse_tracking: 鼠标追踪注视
- 04_animation: 呼吸、眨眼、挥手动画
- 05_expression: 表情切换

运行方式：
    python 06_complete.py
"""

import sys
import time
from enum import Enum
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMenu
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


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

    def update_mouse_position(self, x, y):
        import math
        dx = x - self.target_center[0]
        dy = y - self.target_center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            max_distance = 400
            normalized_distance = min(distance / max_distance, 1.0)
            self.relative_angle_x = (dx / distance) * normalized_distance
            self.relative_angle_y = (dy / distance) * normalized_distance
        else:
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_gaze_angles(self):
        angle_x = self.relative_angle_x * self.max_gaze_angle
        angle_y = self.relative_angle_y * self.max_gaze_angle
        eye_x = self.relative_angle_x * 1.0
        eye_y = self.relative_angle_y * 1.0
        return angle_x, angle_y, eye_x, eye_y


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
        import math
        self.breath_timer += delta_time
        breath_cycle = 3.0
        breath_progress = (self.breath_timer % breath_cycle) / breath_cycle
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
        import math
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
        self.live2d_model = None
        self.mouse_tracker = MouseTracker(
            (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2)
        )
        self.animation_controller = None
        self.current_expression = Expression.HAPPY
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("示例 06: 完整桌宠")
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
        self.animation_controller = AnimationController(self.live2d_model)
        self.startTimer(33)

    def paintGL(self):
        live2d.clearBuffer()
        if self.live2d_model:
            delta_time = 1.0 / settings.FPS
            self.animation_controller.update(delta_time)

            angles = self.mouse_tracker.get_gaze_angles()
            self.live2d_model.SetParameterValue("ParamAngleX", angles[0])
            self.live2d_model.SetParameterValue("ParamAngleY", angles[1])
            self.live2d_model.SetParameterValue("ParamEyeBallX", angles[2])
            self.live2d_model.SetParameterValue("ParamEyeBallY", angles[3])

            self._apply_expression(self.current_expression)
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def _apply_expression(self, expression):
        config = EXPRESSION_CONFIGS.get(expression, {})
        for param_name, value in config.items():
            self.live2d_model.SetParameterValue(param_name, value)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.update_mouse_position(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.animation_controller.trigger_wave()
            expressions = list(Expression)
            current_index = expressions.index(self.current_expression)
            next_index = (current_index + 1) % len(expressions)
            self.current_expression = expressions[next_index]
        super().mousePressEvent(event)

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

    def closeEvent(self, event):
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet = DesktopPetWidget()
    pet.show()

    print("=" * 50)
    print("完整桌宠示例")
    print("功能：")
    print("  - 移动鼠标：头部/眼球跟随")
    print("  - 左键点击：挥手 + 切换表情")
    print("  - 右键菜单：选择表情/退出")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
