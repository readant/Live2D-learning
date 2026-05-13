"""
面部捕捉模块 - Face Capture Module

该模块包含从摄像头面部捕捉到 Live2D 驱动的完整流程：
- MediaPipe 人脸关键点检测
- 头部姿态估计（PnP算法）
- 表情参数提取
- 平滑滤波处理
- Live2D 参数映射

学习路径：
阶段 1：基础环境搭建与 MediaPipe 集成
阶段 2：面部特征点提取与可视化
阶段 3：头部姿态估计（PnP算法）
阶段 4：Live2D 参数映射
阶段 5：平滑滤波与抖动抑制
阶段 6：完整系统集成
阶段 7：动作录制与导出
"""

from .stage1_mediapipe import FaceMeshDetector
from .stage2_landmarks import FacialLandmarks
from .stage3_head_pose import HeadPoseEstimator
from .stage4_parameter_mapping import ParameterMapper
from .stage5_smoothing import Smoother
from .visualization import FaceCaptureVisualizer

__all__ = [
    'FaceMeshDetector',
    'FacialLandmarks', 
    'HeadPoseEstimator',
    'ParameterMapper',
    'Smoother',
    'FaceCaptureVisualizer'
]