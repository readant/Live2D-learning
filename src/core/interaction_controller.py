"""
交互控制器模块
管理桌宠的所有交互逻辑，包括点击、双击、拖拽等
支持动作优先级、冷却时间等机制
"""

import time
from enum import Enum
from typing import Callable, Optional, Dict, List
from dataclasses import dataclass


class ClickType(Enum):
    """点击类型枚举"""
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    LONG = 4


class HitArea(Enum):
    """命中区域枚举"""
    HEAD = "Head"
    BODY = "Body"
    OTHER = "Other"


@dataclass
class MotionInfo:
    """动作信息"""
    name: str
    priority: int
    callback: Optional[Callable] = None


class InteractionController:
    """
    交互控制器
    统一管理桌宠的所有交互行为
    支持：单击/双击/三击识别、动作优先级、冷却时间、命中区域检测
    """

    def __init__(self, live2d_model=None):
        """
        初始化交互控制器
        
        Args:
            live2d_model: Live2D 模型实例（可选，可稍后通过 set_model 设置）
        """
        # Live2D 模型实例
        self._model = live2d_model
        
        # ========== 点击检测状态 ==========
        # 上次点击的时间戳（用于检测双击/三击）
        self._last_click_time = 0
        # 连续点击次数
        self._click_count = 0
        # 点击位置历史（暂时未使用）
        self._click_positions: List[tuple] = []
        # 双击的最大时间间隔（秒）
        self._double_click_interval = 0.3
        # 三击的最大时间间隔（秒）
        self._triple_click_interval = 0.5
        # 上次点击的命中区域
        self._last_click_area = HitArea.OTHER
        
        # ========== 动作管理 ==========
        # 动作回调函数字典
        self._motion_callbacks: Dict[str, Callable] = {}
        # 当前正在播放的动作列表
        self._current_playing_motions: List[str] = []
        # 动作优先级配置（数字越小优先级越高）
        self._motion_priorities: Dict[str, int] = {
            "Idle": 0,        # 待机动作，优先级最低
            "Tap": 2,         # 点击头部
            "Tap@Body": 2,    # 点击身体
            "Flick": 2,       # 挥手
            "Flick@Body": 2,  # 从身体挥手
            "FlickDown": 2,   # 向下挥手
        }
        
        # ========== 交互控制 ==========
        # 是否启用交互
        self._interaction_enabled = True
        # 冷却时间计时器（记录每个动作上次触发的时间）
        self._cooldown_timers: Dict[str, float] = {}
        # 动作冷却时间配置（秒）
        self._cooldowns: Dict[str, float] = {
            "Tap": 1.0,
            "Tap@Body": 1.0,
            "Flick": 0.5,
            "Flick@Body": 0.5,
            "FlickDown": 0.5,
        }

    def set_model(self, model):
        """
        设置 Live2D 模型实例
        
        Args:
            model: Live2D 模型实例
        """
        self._model = model

    def set_motion_callback(self, motion_name: str, callback: Callable):
        """
        设置动作播放回调函数
        
        Args:
            motion_name: 动作名称
            callback: 回调函数
        """
        self._motion_callbacks[motion_name] = callback

    def register_motion_priority(self, motion_name: str, priority: int):
        """
        注册动作优先级
        
        Args:
            motion_name: 动作名称
            priority: 优先级（数字越小优先级越高）
        """
        self._motion_priorities[motion_name] = priority

    def enable_interaction(self):
        """启用交互"""
        self._interaction_enabled = True

    def disable_interaction(self):
        """禁用交互"""
        self._interaction_enabled = False

    def process_click(self, x: float, y: float, click_count: int = 1) -> bool:
        """
        处理点击事件
        
        Args:
            x: 点击的 X 坐标
            y: 点击的 Y 坐标
            click_count: 点击次数（1=单击, 2=双击, 3=三击）
            
        Returns:
            是否成功触发动作
        """
        if not self._interaction_enabled or not self._model:
            return False

        # 检测点击命中的区域
        hit_area = self._detect_hit_area(x, y)
        
        # 根据点击次数分发到不同的处理函数
        if click_count == 1:
            return self._handle_single_click(hit_area, x, y)
        elif click_count == 2:
            return self._handle_double_click(hit_area, x, y)
        elif click_count >= 3:
            return self._handle_triple_click(hit_area, x, y)
        
        return False

    def _detect_hit_area(self, x: float, y: float) -> HitArea:
        """
        检测点击区域
        
        基于窗口尺寸划分区域：
        - 头部：上半部分（y < 40%）
        - 身体：下半部分（y >= 40%）
        
        Args:
            x: 点击的 X 坐标
            y: 点击的 Y 坐标
            
        Returns:
            命中区域（HitArea.HEAD 或 HitArea.BODY）
        """
        from config import settings
        
        # 计算 Y 坐标的相对百分比
        window_height = settings.WINDOW_HEIGHT
        relative_y = (y / window_height) * 100
        
        # 上 40% 为头部区域，下 60% 为身体区域
        if relative_y < 40:
            return HitArea.HEAD
        else:
            return HitArea.BODY

    def _handle_single_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """
        处理单击
        
        Args:
            hit_area: 命中区域
            x: 点击 X 坐标
            y: 点击 Y 坐标
            
        Returns:
            是否成功触发动作
        """
        current_time = time.time()
        
        # ========== 连续点击检测算法 ==========
        # 如果距离上次点击超过双击间隔，重置点击计数为 1
        # 否则，增加点击计数（用于后续检测双击/三击）
        if current_time - self._last_click_time > self._double_click_interval:
            self._click_count = 1
        else:
            self._click_count += 1
        
        # 更新最后点击时间和区域
        self._last_click_time = current_time
        self._last_click_area = hit_area
        
        # 根据命中区域触发不同的动作
        if hit_area == HitArea.BODY:
            return self._trigger_motion("Tap@Body")
        else:
            return self._trigger_motion("Tap")

    def _handle_double_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """
        处理双击
        
        Args:
            hit_area: 命中区域
            x: 点击 X 坐标
            y: 点击 Y 坐标
            
        Returns:
            是否成功触发动作
        """
        if hit_area == HitArea.BODY:
            return self._trigger_motion("Flick@Body")
        else:
            return self._trigger_motion("Flick")

    def _handle_triple_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """
        处理三击
        
        Args:
            hit_area: 命中区域
            x: 点击 X 坐标
            y: 点击 Y 坐标
            
        Returns:
            是否成功触发动作
        """
        return self._trigger_motion("FlickDown")

    def _trigger_motion(self, motion_name: str, force: bool = False) -> bool:
        """
        触发动作
        
        Args:
            motion_name: 动作名称
            force: 是否强制播放（忽略冷却时间）
            
        Returns:
            是否成功触发
        """
        if not self._model:
            return False

        # ========== 冷却时间检查 ==========
        # 如果不是强制播放，且动作仍在冷却中，则跳过
        if not force and self._is_in_cooldown(motion_name):
            print(f"[交互] {motion_name} 动作冷却中，跳过")
            return False

        # 获取动作优先级
        priority = self._motion_priorities.get(motion_name, 1)
        
        try:
            # 调用 Live2D SDK 播放动作
            self._model.StartRandomMotion(motion_name, priority)
            
            # 设置冷却时间
            self._set_cooldown(motion_name)
            # 记录正在播放的动作
            self._current_playing_motions.append(motion_name)
            
            print(f"[交互] 触发动作: {motion_name} (优先级: {priority})")
            
            # 执行动作回调（如果有）
            if motion_name in self._motion_callbacks:
                callback = self._motion_callbacks[motion_name]
                if callback:
                    callback(motion_name)
            
            return True
            
        except Exception as e:
            print(f"[交互] 触发动作失败: {motion_name}, 错误: {e}")
            return False

    def _is_in_cooldown(self, motion_name: str) -> bool:
        """
        检查动作是否在冷却中
        
        Args:
            motion_name: 动作名称
            
        Returns:
            是否在冷却中
        """
        # 如果动作没有配置冷却时间，直接返回 False
        if motion_name not in self._cooldowns:
            return False
        
        # 如果动作没有冷却计时器记录，直接返回 False
        if motion_name not in self._cooldown_timers:
            return False
        
        # ========== 冷却时间计算 ==========
        # 计算距离上次触发的时间，如果小于配置的冷却时间，则仍在冷却中
        elapsed = time.time() - self._cooldown_timers[motion_name]
        return elapsed < self._cooldowns[motion_name]

    def _set_cooldown(self, motion_name: str):
        """
        设置动作冷却（记录当前时间）
        
        Args:
            motion_name: 动作名称
        """
        if motion_name in self._cooldowns:
            self._cooldown_timers[motion_name] = time.time()

    def on_motion_finished(self, motion_name: str):
        """
        动作播放完成回调
        
        Args:
            motion_name: 动作名称
        """
        if motion_name in self._current_playing_motions:
            self._current_playing_motions.remove(motion_name)
        print(f"[交互] 动作完成: {motion_name}")

    def is_motion_playing(self, motion_name: str = None) -> bool:
        """
        检查是否有动作正在播放
        
        Args:
            motion_name: 如果为 None，检查是否有任何动作在播放
                        如果指定了名称，检查该动作是否在播放
            
        Returns:
            是否有动作正在播放
        """
        if motion_name is None:
            return len(self._current_playing_motions) > 0
        return motion_name in self._current_playing_motions

    def stop_all_motions(self):
        """停止所有动作"""
        self._current_playing_motions.clear()
        print("[交互] 停止所有动作")

    def get_available_motions(self) -> List[str]:
        """
        获取所有可用的动作列表
        
        Returns:
            动作名称列表
        """
        return list(self._motion_priorities.keys())

    def trigger_idle(self):
        """
        触发待机动作
        
        Returns:
            是否成功触发
        """
        return self._trigger_motion("Idle")

    def process_drag(self, x: float, y: float):
        """
        处理拖拽（视线跟随）
        
        Args:
            x: 鼠标 X 坐标
            y: 鼠标 Y 坐标
        """
        if not self._interaction_enabled or not self._model:
            return
        
        try:
            self._model.Drag(x, y)
        except Exception as e:
            pass

    def process_touch(self, x: float, y: float):
        """
        处理触摸事件
        
        Args:
            x: 触摸点 X 坐标
            y: 触摸点 Y 坐标
        """
        if not self._interaction_enabled or not self._model:
            return
        
        try:
            self._model.Touch(x, y)
        except Exception as e:
            pass

    def set_cooldown(self, motion_name: str, seconds: float):
        """
        设置动作冷却时间
        
        Args:
            motion_name: 动作名称
            seconds: 冷却时间（秒）
        """
        self._cooldowns[motion_name] = seconds

    def get_cooldown_remaining(self, motion_name: str) -> float:
        """
        获取动作剩余冷却时间
        
        Args:
            motion_name: 动作名称
            
        Returns:
            剩余冷却时间（秒），如果不在冷却中则返回 0
        """
        if not self._is_in_cooldown(motion_name):
            return 0
        
        # 计算剩余冷却时间
        elapsed = time.time() - self._cooldown_timers[motion_name]
        return max(0, self._cooldowns[motion_name] - elapsed)