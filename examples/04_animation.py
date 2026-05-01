"""
示例 04: 动画系统

这个示例展示如何实现呼吸动画、眨眼动画等基础动画效果。

学习要点：
- 定时器驱动动画
- 正弦波动画算法
- 随机事件处理
- 动画状态管理

运行方式：
    python 04_animation.py
"""

import sys
import math
import time
import random
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class AnimationController:
    """
    动画控制器

    负责管理所有自动画效果：
    - 呼吸动画：身体轻微上下起伏
    - 眨眼动画：随机眨眼效果
    - 挥手动画：点击触发的大幅度挥手

    设计思路：
    - 使用正弦波实现平滑的呼吸效果
    - 使用定时器检测眨眼时机
    - 挥手使用三角形波实现快速上升-缓慢复位
    """

    def __init__(self, model=None):
        self.model = model

        self.last_time = time.time()
        self.breath_timer = 0.0
        self.blink_timer = 0.0
        self.wave_timer = 0.0

        self.is_waving = False
        self.wave_duration = 2.0

        self.blink_interval = 3.0
        self.is_blinking = False
        self.blink_duration = 0.1

    def update(self, delta_time: float) -> None:
        """
        更新所有动画状态

        Args:
            delta_time: 距离上一帧的时间（秒）
        """
        self._update_breath(delta_time)
        self._update_blink(delta_time)
        self._update_wave(delta_time)

    def _update_breath(self, delta_time: float) -> None:
        """更新呼吸动画"""
        self.breath_timer += delta_time

        breath_cycle = 3.0
        breath_progress = (self.breath_timer % breath_cycle) / breath_cycle
        breath_value = (math.sin(breath_progress * 2 * math.pi) + 1) / 2

        if self.model:
            self.model.SetParameterValue("ParamBreath", breath_value)

    def _update_blink(self, delta_time: float) -> None:
        """更新眨眼动画"""
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

    def _update_wave(self, delta_time: float) -> None:
        """更新挥手动画"""
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

    def trigger_wave(self) -> None:
        """触发挥手动画"""
        if not self.is_waving:
            self.is_waving = True
            self.wave_timer = 0.0


class AnimationWidget(QOpenGLWidget):
    """
    带动画系统的 Live2D 窗口
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.animation_controller = None
        self._init_ui()

    def _init_ui(self):
        """初始化窗口"""
        self.setWindowTitle("示例 04: 动画系统")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        """初始化"""
        self.makeCurrent()
        live2d.init()
        live2d.glInit()

        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)

        self.animation_controller = AnimationController(self.live2d_model)
        self.startTimer(33)

    def paintGL(self):
        """渲染"""
        live2d.clearBuffer()

        if self.live2d_model:
            delta_time = 1.0 / settings.FPS
            self.animation_controller.update(delta_time)

            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mousePressEvent(self, event):
        """点击触发挥手"""
        if event.button() == Qt.LeftButton:
            self.animation_controller.trigger_wave()
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

    widget = AnimationWidget()
    widget.show()

    print("=" * 50)
    print("动画系统示例")
    print("- 自动呼吸动画")
    print("- 随机眨眼动画")
    print("- 点击触发挥手动画")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
