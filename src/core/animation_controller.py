"""
动画控制器模块
管理眨眼、呼吸、挥手等动画状态
"""

import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.live2d.model import Live2DModelInterface


class AnimationController:
    """动画控制器"""

    def __init__(self, model: "Live2DModelInterface"):
        self.model = model

        self.breath_value = 0.5
        self.breath_direction = 1

        self.blink_timer = 0.0
        self.blink_interval = random.uniform(2.0, 5.0)
        self.is_blinking = False

        self.is_waving = False
        self.wave_timer = 0.0

        self.blink_min_interval = 2.0
        self.blink_max_interval = 5.0
        self.blink_duration = 0.3
        self.breath_speed = 1.5
        self.wave_duration = 2.0

    def update(self, delta_time: float) -> None:
        current_time = time.time()
        self._update_breath(delta_time)
        self._update_blink(current_time)
        self._update_wave(delta_time)

    def _update_breath(self, delta_time: float) -> None:
        self.breath_value += self.breath_direction * delta_time * self.breath_speed
        if self.breath_value > 1.0:
            self.breath_value = 1.0
            self.breath_direction = -1
        elif self.breath_value < 0.0:
            self.breath_value = 0.0
            self.breath_direction = 1
        self.model.set_parameter("ParamBreath", self.breath_value)

    def _update_blink(self, current_time: float) -> None:
        if not self.is_blinking:
            if current_time - self.blink_timer > self.blink_interval:
                self.is_blinking = True
                self.blink_timer = current_time
        else:
            elapsed = current_time - self.blink_timer
            if elapsed < 0.1:
                val = elapsed * 10
            elif elapsed < 0.2:
                val = 1.0
            elif elapsed < self.blink_duration:
                val = 1.0 - (elapsed - 0.2) * 10
            else:
                val = 0.0
                self.is_blinking = False
                self.blink_timer = current_time
                self.blink_interval = random.uniform(self.blink_min_interval, self.blink_max_interval)

            self.model.set_parameter("ParamEyeLOpen", val)
            self.model.set_parameter("ParamEyeROpen", val)

    def _update_wave(self, delta_time: float) -> None:
        if self.is_waving:
            self.wave_timer += delta_time
            if self.wave_timer > self.wave_duration:
                self.is_waving = False
                self.wave_timer = 0.0

    def trigger_wave(self) -> bool:
        if not self.is_waving:
            self.is_waving = True
            self.wave_timer = 0.0
            return True
        return False

    def is_waving(self) -> bool:
        return self.is_waving

    def reset(self) -> None:
        self.breath_value = 0.5
        self.breath_direction = 1
        self.is_blinking = False
        self.is_waving = False
        self.wave_timer = 0.0
