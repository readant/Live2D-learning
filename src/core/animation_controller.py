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
    """
    动画控制器类
    负责管理 Live2D 模型的各种自动动画效果：
    - 呼吸动画
    - 眨眼动画
    - 挥手动画
    """

    def __init__(self, model: "Live2DModelInterface"):
        """
        初始化动画控制器
        
        Args:
            model: Live2D 模型接口对象
        """
        self.model = model

        # ========== 呼吸动画参数 ==========
        self.breath_value = 0.5  # 当前呼吸值 (0.0 ~ 1.0)
        self.breath_direction = 1  # 呼吸方向 (1=吸气, -1=呼气)

        # ========== 眨眼动画参数 ==========
        self.blink_timer = 0.0  # 眨眼计时器
        self.blink_interval = random.uniform(2.0, 5.0)  # 两次眨眼的间隔时间（随机 2~5 秒）
        self.is_blinking = False  # 是否正在眨眼

        # ========== 挥手动画参数 ==========
        self.is_waving = False  # 是否正在挥手
        self.wave_timer = 0.0  # 挥手计时器

        # ========== 可调整的动画设置 ==========
        self.blink_min_interval = 2.0  # 眨眼最小间隔（秒）
        self.blink_max_interval = 5.0  # 眨眼最大间隔（秒）
        self.blink_duration = 0.3  # 每次眨眼持续时间（秒）
        self.breath_speed = 1.5  # 呼吸速度（值越大呼吸越快）
        self.wave_duration = 2.0  # 挥手动作持续时间（秒）

    def update(self, delta_time: float) -> None:
        """
        更新所有动画（每帧调用）
        
        Args:
            delta_time: 距离上一帧的时间差（秒）
        """
        current_time = time.time()
        self._update_breath(delta_time)  # 更新呼吸
        self._update_blink(current_time)  # 更新眨眼
        self._update_wave(delta_time)  # 更新挥手

    def _update_breath(self, delta_time: float) -> None:
        """
        更新呼吸动画
        实现胸部的轻微起伏效果
        
        Args:
            delta_time: 距离上一帧的时间差（秒）
        """
        # 根据呼吸方向和速度更新呼吸值
        self.breath_value += self.breath_direction * delta_time * self.breath_speed
        
        # 当呼吸值达到边界时，反向呼吸
        if self.breath_value > 1.0:
            self.breath_value = 1.0  # 吸气最大值
            self.breath_direction = -1  # 改为呼气
        elif self.breath_value < 0.0:
            self.breath_value = 0.0  # 呼气最小值
            self.breath_direction = 1  # 改为吸气
        
        # 应用到模型的呼吸参数
        self.model.set_parameter("ParamBreath", self.breath_value)

    def _update_blink(self, current_time: float) -> None:
        """
        更新眨眼动画
        实现自然的闭眼-睁眼过程
        
        Args:
            current_time: 当前时间戳
        """
        # 如果没有在眨眼，检查是否到了该眨眼的时候
        if not self.is_blinking:
            if current_time - self.blink_timer > self.blink_interval:
                # 开始眨眼
                self.is_blinking = True
                self.blink_timer = current_time
        else:
            # 正在眨眼，计算当前眼睛的开闭程度
            elapsed = current_time - self.blink_timer  # 眨眼开始后经过的时间
            
            if elapsed < 0.1:
                # 阶段1: 0~0.1秒，眼睛逐渐闭上（从0到1）
                val = elapsed * 10
            elif elapsed < 0.2:
                # 阶段2: 0.1~0.2秒，眼睛完全闭上
                val = 1.0
            elif elapsed < self.blink_duration:
                # 阶段3: 0.2~0.3秒，眼睛逐渐睁开（从1到0）
                val = 1.0 - (elapsed - 0.2) * 10
            else:
                # 阶段4: 眨眼结束，恢复正常
                val = 0.0
                self.is_blinking = False
                self.blink_timer = current_time
                # 设置下一次眨眼的随机间隔
                self.blink_interval = random.uniform(self.blink_min_interval, self.blink_max_interval)

            # 应用到左右眼参数
            self.model.set_parameter("ParamEyeLOpen", val)
            self.model.set_parameter("ParamEyeROpen", val)

    def _update_wave(self, delta_time: float) -> None:
        """
        更新挥手动画
        实现手臂的大幅度挥动效果
        
        Args:
            delta_time: 距离上一帧的时间差（秒）
        """
        if self.is_waving:
            self.wave_timer += delta_time  # 增加计时器
            
            # 计算挥手动画（只在持续时间内执行）
            if self.wave_timer < self.wave_duration:
                # ========== 挥手动画算法 ==========
                # 使用三角形波实现先快速上升，再缓慢复位的效果
                # 2 * t / duration - 1: 将时间归一化为 -1 到 1 的范围
                # abs(): 取绝对值，变成 1 到 0 再到 1 的三角形
                # 1 - abs(): 变成 0 到 1 再到 0 的上升-下降曲线
                # -30 是手臂抬起的最大值，-20 是额外的幅度
                # =================================
                
                progress = self.wave_timer / self.wave_duration  # 动画进度 (0.0 ~ 1.0)
                arm_value = -30 - 20 * (1 - abs(2 * progress - 1))
                
                # 同时控制左右臂
                self.model.set_parameter("ParamArmLA", arm_value)
                self.model.set_parameter("ParamArmRA", arm_value)
            else:
                # 挥手结束，复位状态
                self.is_waving = False
                self.wave_timer = 0.0
                # 把手臂参数复位到 0（默认位置）
                self.model.set_parameter("ParamArmLA", 0.0)
                self.model.set_parameter("ParamArmRA", 0.0)

    def trigger_wave(self) -> bool:
        """
        触发挥手动画
        
        Returns:
            bool: 是否成功触发（如果已经在挥手则返回 False）
        """
        if not self.is_waving:
            self.is_waving = True
            self.wave_timer = 0.0
            return True
        return False

    def is_waving(self) -> bool:
        """
        检查是否正在挥手
        
        Returns:
            bool: 是否正在挥手
        """
        return self.is_waving

    def reset(self) -> None:
        """
        重置所有动画状态
        """
        self.breath_value = 0.5
        self.breath_direction = 1
        self.is_blinking = False
        self.is_waving = False
        self.wave_timer = 0.0
