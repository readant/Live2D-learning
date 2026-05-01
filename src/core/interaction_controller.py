"""
交互控制器模块
管理桌宠的所有交互逻辑，包括点击、双击、拖拽等
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
    """

    def __init__(self, live2d_model=None):
        self._model = live2d_model
        
        self._last_click_time = 0
        self._click_count = 0
        self._click_positions: List[tuple] = []
        self._double_click_interval = 0.3
        self._triple_click_interval = 0.5
        self._last_click_area = HitArea.OTHER
        
        self._motion_callbacks: Dict[str, Callable] = {}
        self._current_playing_motions: List[str] = []
        self._motion_priorities: Dict[str, int] = {
            "Idle": 0,
            "Tap": 2,
            "Tap@Body": 2,
            "Flick": 2,
            "Flick@Body": 2,
            "FlickDown": 2,
        }
        
        self._interaction_enabled = True
        self._cooldown_timers: Dict[str, float] = {}
        self._cooldowns: Dict[str, float] = {
            "Tap": 1.0,
            "Tap@Body": 1.0,
            "Flick": 0.5,
            "Flick@Body": 0.5,
            "FlickDown": 0.5,
        }

    def set_model(self, model):
        """设置 Live2D 模型实例"""
        self._model = model

    def set_motion_callback(self, motion_name: str, callback: Callable):
        """设置动作播放回调函数"""
        self._motion_callbacks[motion_name] = callback

    def register_motion_priority(self, motion_name: str, priority: int):
        """注册动作优先级"""
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

        hit_area = self._detect_hit_area(x, y)
        
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
        """
        from config import settings
        
        window_height = settings.WINDOW_HEIGHT
        relative_y = (y / window_height) * 100
        
        if relative_y < 40:
            return HitArea.HEAD
        else:
            return HitArea.BODY

    def _handle_single_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """处理单击"""
        current_time = time.time()
        
        if current_time - self._last_click_time > self._double_click_interval:
            self._click_count = 1
        else:
            self._click_count += 1
        
        self._last_click_time = current_time
        self._last_click_area = hit_area
        
        if hit_area == HitArea.BODY:
            return self._trigger_motion("Tap@Body")
        else:
            return self._trigger_motion("Tap")

    def _handle_double_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """处理双击"""
        if hit_area == HitArea.BODY:
            return self._trigger_motion("Flick@Body")
        else:
            return self._trigger_motion("Flick")

    def _handle_triple_click(self, hit_area: HitArea, x: float, y: float) -> bool:
        """处理三击"""
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

        if not force and self._is_in_cooldown(motion_name):
            print(f"[交互] {motion_name} 动作冷却中，跳过")
            return False

        priority = self._motion_priorities.get(motion_name, 1)
        
        try:
            self._model.StartRandomMotion(motion_name, priority)
            
            self._set_cooldown(motion_name)
            self._current_playing_motions.append(motion_name)
            
            print(f"[交互] 触发动作: {motion_name} (优先级: {priority})")
            
            if motion_name in self._motion_callbacks:
                callback = self._motion_callbacks[motion_name]
                if callback:
                    callback(motion_name)
            
            return True
            
        except Exception as e:
            print(f"[交互] 触发动作失败: {motion_name}, 错误: {e}")
            return False

    def _is_in_cooldown(self, motion_name: str) -> bool:
        """检查动作是否在冷却中"""
        if motion_name not in self._cooldowns:
            return False
        
        if motion_name not in self._cooldown_timers:
            return False
        
        elapsed = time.time() - self._cooldown_timers[motion_name]
        return elapsed < self._cooldowns[motion_name]

    def _set_cooldown(self, motion_name: str):
        """设置动作冷却"""
        if motion_name in self._cooldowns:
            self._cooldown_timers[motion_name] = time.time()

    def on_motion_finished(self, motion_name: str):
        """动作播放完成回调"""
        if motion_name in self._current_playing_motions:
            self._current_playing_motions.remove(motion_name)
        print(f"[交互] 动作完成: {motion_name}")

    def is_motion_playing(self, motion_name: str = None) -> bool:
        """
        检查是否有动作正在播放
        
        Args:
            motion_name: 如果为 None，检查是否有任何动作在播放
        """
        if motion_name is None:
            return len(self._current_playing_motions) > 0
        return motion_name in self._current_playing_motions

    def stop_all_motions(self):
        """停止所有动作"""
        self._current_playing_motions.clear()
        print("[交互] 停止所有动作")

    def get_available_motions(self) -> List[str]:
        """获取所有可用的动作列表"""
        return list(self._motion_priorities.keys())

    def trigger_idle(self):
        """触发待机动作"""
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
        
        Returns:
            剩余冷却时间（秒），如果不在冷却中则返回 0
        """
        if not self._is_in_cooldown(motion_name):
            return 0
        
        elapsed = time.time() - self._cooldown_timers[motion_name]
        return max(0, self._cooldowns[motion_name] - elapsed)