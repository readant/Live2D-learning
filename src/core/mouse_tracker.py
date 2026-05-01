"""
鼠标追踪模块
实时追踪鼠标位置，计算与模型的相对角度
"""

import math
from typing import Tuple
from PyQt5.QtCore import QPoint


class MouseTracker:
    """鼠标追踪器，计算注视角度"""

    def __init__(self, target_center: Tuple[int, int]):
        self.target_center = target_center
        self.mouse_pos = QPoint(0, 0)
        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0

    def update_target_center(self, x: int, y: int) -> None:
        self.target_center = (x, y)

    def update_mouse_position(self, x: int, y: int) -> None:
        self.mouse_pos = QPoint(x, y)
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

    def get_gaze_angles(self) -> Tuple[float, float, float, float]:
        head_x = self.relative_angle_y * 15
        head_y = self.relative_angle_x * 20
        eye_x = self.relative_angle_x * 0.8
        eye_y = self.relative_angle_y * 0.6
        return head_x, head_y, eye_x, eye_y

    def reset(self) -> None:
        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0
