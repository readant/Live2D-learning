"""
Live2D模型接口模块
封装Live2D Cubism SDK的Python接口
使用 live2d-py 库实现
支持真实渲染和模拟渲染两种模式
"""

import os
from typing import Dict, Tuple, Optional, Callable
import sys

# ========== 库可用性检测 ==========
# 尝试导入 live2d-py 库，如果失败则使用模拟模式
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
    支持降级到模拟模式，确保程序在缺少依赖时仍能运行
    """

    def __init__(self, model_path: str):
        """
        初始化模型接口
        
        Args:
            model_path: Live2D 模型文件路径（.model3.json）
        """
        # 模型文件路径
        self.model_path = model_path
        # 模型是否已初始化
        self.initialized = False
        # 真实模型实例（live2d-py 的 LAppModel）
        self._model = None
        # 是否使用模拟模式（当 live2d-py 不可用时）
        self._fallback_mode = not LIVE2D_AVAILABLE

        # 根据是否有 live2d-py 库初始化不同的参数存储
        if LIVE2D_AVAILABLE:
            self.parameters = {}
            self.parameter_ranges = {}
        else:
            # ========== 模拟模式参数配置 ==========
            # 模拟模式下预定义常用的 Live2D 参数及其范围
            self.parameters: Dict[str, float] = {}
            self.parameter_ranges: Dict[str, Tuple[float, float]] = {
                "ParamAngleX": (-30, 30),      # 头部 X 轴旋转（左右摇头）
                "ParamAngleY": (-30, 30),      # 头部 Y 轴旋转（上下点头）
                "ParamAngleZ": (-30, 30),      # 头部 Z 轴旋转（歪头）
                "ParamEyeBallX": (-1, 1),      # 眼球 X 轴移动（左右看）
                "ParamEyeBallY": (-1, 1),      # 眼球 Y 轴移动（上下看）
                "ParamBreath": (0, 1),         # 呼吸参数
                "ParamMouthOpenY": (0, 1),     # 嘴巴开合
                "ParamEyeLOpen": (0, 1),       # 左眼开合
                "ParamEyeROpen": (0, 1),       # 右眼开合
                "ParamBodyAngleX": (-10, 10),  # 身体 X 轴旋转
            }
            self._init_parameters()

    def _init_parameters(self) -> None:
        """
        初始化模拟模式的参数
        将所有参数设置为范围的中间值
        """
        for param, (min_val, max_val) in self.parameter_ranges.items():
            self.parameters[param] = (min_val + max_val) / 2

    def load(self) -> bool:
        """
        加载 Live2D 模型
        
        Returns:
            是否成功加载真实模型（模拟模式始终返回 True）
        """
        if self._fallback_mode:
            print(f"[Live2D] 模拟模式 - 正在加载模型: {self.model_path}")
            self.initialized = True
            return True

        try:
            print(f"[Live2D] 正在加载模型: {self.model_path}")

            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                print(f"[Live2D] 错误: 模型文件不存在: {self.model_path}")
                self._fallback_mode = True
                self._init_parameters()
                self.initialized = True
                return True

            # 初始化 live2d-py 库并加载模型
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
        """
        调整模型渲染尺寸
        
        Args:
            width: 宽度（像素）
            height: 高度（像素）
        """
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Resize(width, height)

    def set_parameter(self, name: str, value: float, weight: float = 1.0) -> None:
        """
        设置模型参数值
        
        Args:
            name: 参数名称（如 "ParamAngleX"）
            value: 参数值
            weight: 权重（0.0~1.0），用于平滑过渡，1.0 表示立即设置
        """
        if self._fallback_mode:
            # 模拟模式下手动处理参数
            if name not in self.parameters:
                return

            # ========== 参数值限制 ==========
            # 确保参数值在允许的范围内
            min_val, max_val = self.parameter_ranges[name]
            clamped_value = max(min_val, min(max_val, value))

            # ========== 权重平滑算法 ==========
            # 如果权重小于 1.0，使用平滑过渡：
            # 新值 = 当前值 + (目标值 - 当前值) * 权重
            if weight < 1.0:
                current = self.parameters[name]
                self.parameters[name] = current + (clamped_value - current) * weight
            else:
                self.parameters[name] = clamped_value
        else:
            # 真实模式直接调用 SDK
            if self._model is not None:
                self._model.SetParameterValue(name, value, weight)

    def get_parameter(self, name: str) -> float:
        """
        获取模型参数值
        
        Args:
            name: 参数名称
            
        Returns:
            参数值（模拟模式返回存储值，真实模式暂时返回 0.0）
        """
        if self._fallback_mode:
            return self.parameters.get(name, 0.0)
        else:
            return 0.0

    def reset_parameters(self) -> None:
        """
        重置所有参数到初始值
        """
        if self._fallback_mode:
            self._init_parameters()

    def drag(self, x: float, y: float) -> None:
        """
        处理拖拽（视线跟随）
        
        Args:
            x: 鼠标 X 坐标
            y: 鼠标 Y 坐标
        """
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Drag(x, y)

    def start_motion(self, group: str, no: int = 0, priority: int = 3,
                      start_callback: Optional[Callable[[str, int], None]] = None,
                      finish_callback: Optional[Callable[[], None]] = None) -> None:
        """
        播放指定的动作
        
        Args:
            group: 动作组名称
            no: 动作编号（从 0 开始）
            priority: 优先级（数字越小优先级越高）
            start_callback: 动作开始时的回调
            finish_callback: 动作结束时的回调
        """
        if self._fallback_mode:
            print(f"[Live2D] 模拟播放动作: {group}-{no}")
            return
        if self._model is not None:
            self._model.StartMotion(group, no, priority, start_callback, finish_callback)

    def start_random_motion(self, group: str, priority: int = 3,
                           start_callback: Optional[Callable[[str, int], None]] = None,
                           finish_callback: Optional[Callable[[], None]] = None) -> None:
        """
        随机播放动作组中的一个动作
        
        Args:
            group: 动作组名称
            priority: 优先级（数字越小优先级越高）
            start_callback: 动作开始时的回调
            finish_callback: 动作结束时的回调
        """
        if self._fallback_mode:
            print(f"[Live2D] 模拟随机播放动作: {group}")
            return
        if self._model is not None:
            self._model.StartRandomMotion(group, priority, start_callback, finish_callback)

    def hit_test(self, hit_area_name: str, x: float, y: float) -> Optional[str]:
        """
        碰撞检测（检测点击是否在指定区域）
        
        Args:
            hit_area_name: 碰撞区域名称
            x: 点击 X 坐标
            y: 点击 Y 坐标
            
        Returns:
            碰撞区域名称，如果未命中则返回 None
        """
        if self._fallback_mode:
            return None
        if self._model is not None:
            return self._model.HitTest(hit_area_name, x, y)
        return None

    def update(self, delta_time: float) -> None:
        """
        更新模型状态（每帧调用）
        
        Args:
            delta_time: 距离上一帧的时间差（秒）
        """
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Update()

    def draw(self) -> None:
        """
        绘制模型（每帧调用）
        """
        if self._fallback_mode:
            return
        if self._model is not None:
            self._model.Draw()

    def is_loaded(self) -> bool:
        """
        检查模型是否已加载
        
        Returns:
            是否已加载
        """
        return self.initialized

    def get_raw_model(self):
        """
        获取原始模型实例（live2d-py 的 LAppModel）
        
        Returns:
            原始模型实例
        """
        return self._model
