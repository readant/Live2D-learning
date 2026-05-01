"""
鼠标追踪模块
实时追踪鼠标位置，计算与模型的相对角度
实现眼睛和头部跟随鼠标移动的效果
"""

import math
from typing import Tuple
from PyQt5.QtCore import QPoint


class MouseTracker:
    """
    鼠标追踪器类
    计算鼠标相对于模型中心的位置，并转换为头部和眼球的角度
    实现模型注视鼠标的效果
    """

    def __init__(self, target_center: Tuple[int, int]):
        """
        初始化鼠标追踪器
        
        Args:
            target_center: 模型中心点的坐标 (x, y)
        """
        self.target_center = target_center  # 模型中心点坐标
        self.mouse_pos = QPoint(0, 0)       # 当前鼠标位置
        self.relative_angle_x = 0.0         # X轴相对角度 (-1.0 ~ 1.0)
        self.relative_angle_y = 0.0         # Y轴相对角度 (-1.0 ~ 1.0)

    def update_target_center(self, x: int, y: int) -> None:
        """
        更新模型中心点坐标
        
        Args:
            x: 新的中心点 X 坐标
            y: 新的中心点 Y 坐标
        """
        self.target_center = (x, y)

    def update_mouse_position(self, x: int, y: int) -> None:
        """
        更新鼠标位置并计算相对角度
        
        Args:
            x: 鼠标 X 坐标
            y: 鼠标 Y 坐标
        """
        self.mouse_pos = QPoint(x, y)
        
        # 计算鼠标相对于模型中心的偏移
        dx = x - self.target_center[0]  # X轴偏移
        dy = y - self.target_center[1]  # Y轴偏移
        
        # 计算鼠标到中心的距离
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # ========== 角度计算算法 ==========
            # 1. dx/distance 和 dy/distance: 计算单位向量（方向）
            # 2. normalized_distance: 距离归一化（0.0 ~ 1.0），防止角度过大
            # 3. 相乘后得到最终的相对角度 (-1.0 ~ 1.0)
            # ===================================
            
            max_distance = 400  # 最大有效距离（超过这个距离角度不再增加）
            normalized_distance = min(distance / max_distance, 1.0)  # 归一化距离
            
            # 计算相对角度（结合方向和距离）
            self.relative_angle_x = (dx / distance) * normalized_distance
            self.relative_angle_y = (dy / distance) * normalized_distance
        else:
            # 鼠标在中心位置，角度归零
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_gaze_angles(self) -> Tuple[float, float, float, float]:
        """
        获取注视角度
        
        Returns:
            Tuple[float, float, float, float]: 
                (头部X角度, 头部Y角度, 眼球X角度, 眼球Y角度)
        """
        # 头部跟随（系数越大，跟随越明显）
        head_x = self.relative_angle_y * 15  # 头部X轴角度（前后倾斜）
        head_y = self.relative_angle_x * 20  # 头部Y轴角度（左右转动）
        
        # 眼球跟随（系数比头部小，更自然）
        eye_x = self.relative_angle_x * 0.8  # 眼球X轴
        eye_y = self.relative_angle_y * 0.6  # 眼球Y轴
        
        return head_x, head_y, eye_x, eye_y

    def reset(self) -> None:
        """重置角度到中心位置"""
        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0
