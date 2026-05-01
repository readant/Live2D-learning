"""
Live2D模型接口模块
封装Live2D Cubism SDK的Python接口
使用 live2d-py 库实现
"""

import os
from typing import Dict, Tuple, Optional, Callable
import sys

try:
    import live2d.v3 as live2d
    LIVE2D_AVAILABLE = True
except ImportError:
    LIVE2D_AVAILABLE = False
    print("[Live2D] 警告: live2d-py 库未安装，使用模拟模式")


class Live2DModelInterface:
    """
    Live2D模型接口类
    封装Live2D模型的基本操作
    使用 live2d-py 库实现
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.initialized = False
        self._model = None
        self._fallback_mode = not LIVE2D_AVAILABLE

        if LIVE2D_AVAILABLE:
            self.parameters = {}
            self.parameter_ranges = {}
        else:
            self.parameters: Dict[str, float] = {}
            self.parameter_ranges: Dict[str, Tuple[float, float]] = {
                "ParamAngleX": (-30, 30),
                "ParamAngleY": (-30, 30),
                "ParamAngleZ": (-30, 30),
                "ParamEyeBallX": (-1, 1),
                "ParamEyeBallY": (-1, 1),
                "ParamBreath": (0, 1),
                "ParamMouthOpenY": (0, 1),
                "ParamEyeLOpen": (0, 1),
                "ParamEyeROpen": (0, 1),
                "ParamBodyAngleX": (-10, 10),
            }
            self._init_parameters()

    def _init_parameters(self) -> None:
        for param, (min_val, max_val) in self.parameter_ranges.items():
            self.parameters[param] = (min_val + max_val) / 2

    def load(self) -> bool:
        if self._fallback_mode:
            print(f"[Live2D] 模拟模式 - 正在加载模型: {self.model_path}")
            self.initialized = True
            return True

        try:
            print(f"[Live2D] 正在加载模型: {self.model_path}")

            if not os.path.exists(self.model_path):
                print(f"[Live2D] 错误: 模型文件不存在: {self.model_path}")
                self._fallback_mode = True
                self._init_parameters()
                self.initialized = True
                return True

            live2d.init()
            self._model = live2d.LAppModel()
            success = self._model.LoadModelJson(self.model_path)

            if success:
                self.initialized = True
                print(f"[Live2D] 模型加载成功")
            else:
                print(f"[Live2D] 模型加载失败")
                self._fallback_mode = True
                self._init_parameters()
                self.initialized = True

            return success
        except Exception as e:
            print(f"[Live2D] 加载模型时出错: {e}")
            self._fallback_mode = True
            self._init_parameters()
            self.initialized = True
            return True

    def resize(self, width: int, height: int) -> None:
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Resize(width, height)

    def set_parameter(self, name: str, value: float, weight: float = 1.0) -> None:
        if self._fallback_mode:
            if name not in self.parameters:
                return

            min_val, max_val = self.parameter_ranges[name]
            clamped_value = max(min_val, min(max_val, value))

            if weight < 1.0:
                current = self.parameters[name]
                self.parameters[name] = current + (clamped_value - current) * weight
            else:
                self.parameters[name] = clamped_value
        else:
            if self._model is not None:
                self._model.SetParameterValue(name, value, weight)

    def get_parameter(self, name: str) -> float:
        if self._fallback_mode:
            return self.parameters.get(name, 0.0)
        else:
            return 0.0

    def reset_parameters(self) -> None:
        if self._fallback_mode:
            self._init_parameters()

    def drag(self, x: float, y: float) -> None:
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Drag(x, y)

    def start_motion(self, group: str, no: int = 0, priority: int = 3,
                      start_callback: Optional[Callable[[str, int], None]] = None,
                      finish_callback: Optional[Callable[[], None]] = None) -> None:
        if self._fallback_mode:
            print(f"[Live2D] 模拟播放动作: {group}-{no}")
            return
        if self._model is not None:
            self._model.StartMotion(group, no, priority, start_callback, finish_callback)

    def start_random_motion(self, group: str, priority: int = 3,
                           start_callback: Optional[Callable[[str, int], None]] = None,
                           finish_callback: Optional[Callable[[], None]] = None) -> None:
        if self._fallback_mode:
            print(f"[Live2D] 模拟随机播放动作: {group}")
            return
        if self._model is not None:
            self._model.StartRandomMotion(group, priority, start_callback, finish_callback)

    def hit_test(self, hit_area_name: str, x: float, y: float) -> Optional[str]:
        if self._fallback_mode:
            return None
        if self._model is not None:
            return self._model.HitTest(hit_area_name, x, y)
        return None

    def update(self, delta_time: float) -> None:
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Update()

    def draw(self) -> None:
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Draw()

    def is_loaded(self) -> bool:
        return self.initialized

    def get_raw_model(self):
        return self._model
