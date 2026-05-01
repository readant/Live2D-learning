"""
示例 04: 动画系统 - 答案版本

这个示例展示如何实现呼吸动画、眨眼动画等基础动画效果。

学习要点：
- 定时器驱动动画
- 正弦波动画算法
- 随机事件处理
- 动画状态管理

运行方式：
    python solutions/04_animation_answer.py
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

    架构设计：
    这是一个独立于 UI 的类，体现模块化思想。
    它接收 model 参数，可以在任何时候绑定或更换模型。
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

        这是动画控制器的主方法，每帧调用一次。
        它按照固定顺序更新各个动画效果。

        Args:
            delta_time: 距离上一帧的时间（秒）
                      例如：如果 FPS 是 30，delta_time 就是 1/30 ≈ 0.033 秒
        """
        self._update_breath(delta_time)
        self._update_blink(delta_time)
        self._update_wave(delta_time)

    def _update_breath(self, delta_time: float) -> None:
        """
        更新呼吸动画

        算法：正弦波
        sin(x) 的值在 -1 到 1 之间变化
        (sin(x) + 1) / 2 将其映射到 0 到 1 之间

        呼吸周期：3 秒完成一次完整的呼吸
        breath_progress: 0.0 → 1.0 表示一个完整的呼吸周期
        """
        self.breath_timer += delta_time

        breath_cycle = 3.0
        breath_progress = (self.breath_timer % breath_cycle) / breath_cycle
        breath_value = (math.sin(breath_progress * 2 * math.pi) + 1) / 2

        if self.model:
            self.model.SetParameterValue("ParamBreath", breath_value)

    def _update_blink(self, delta_time: float) -> None:
        """
        更新眨眼动画

        状态机：
        - NOT_BLINKING: 累计时间，等待眨眼
        - BLINKING: 执行眨眼动作

        时间参数：
        - blink_interval: 眨眼间隔（3秒）
        - blink_duration: 眨眼持续时间（0.1秒）
        """
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
        """
        更新挥手动画

        算法：三角形波
        公式：-30 - 20 * (1 - abs(2 * progress - 1))

        动画曲线：
        - progress 从 0 到 1
        - abs(2 * progress - 1) 从 1 降到 0 再升到 1
        - 1 - abs(...) 从 0 升到 1 再降到 0
        - 最终值从 -30 升到 -50 再降回 -30

        这实现了：
        - 快速抬手（上升）
        - 缓慢放下（下降）
        """
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

    组合了：
    - Live2D 模型渲染
    - 动画控制器
    - 点击事件处理
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
        """
        渲染回调

        渲染流程：
        1. 清空缓冲区
        2. 计算时间差
        3. 更新所有动画状态
        4. 更新 Live2D 模型
        5. 绘制模型
        """
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
        """
        鼠标点击事件

        触发挥手动画
        """
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
