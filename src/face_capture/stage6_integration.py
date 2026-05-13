"""
阶段 6：完整系统集成与优化

功能：将所有模块整合为完整的面部捕捉系统

学习目标：
- 理解系统架构设计
- 掌握模块集成方法
- 学习性能优化策略

系统架构：
┌─────────────────┐
│   摄像头输入     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  MediaPipe检测  │  ← stage1_mediapipe.py
└────────┬────────┘
         ↓
┌─────────────────┐
│  特征点提取     │  ← stage2_landmarks.py
└────────┬────────┘
         ↓
┌─────────────────┐
│  头部姿态估计   │  ← stage3_head_pose.py
└────────┬────────┘
         ↓
┌─────────────────┐
│  参数映射       │  ← stage4_parameter_mapping.py
└────────┬────────┘
         ↓
┌─────────────────┐
│  平滑滤波       │  ← stage5_smoothing.py
└────────┬────────┘
         ↓
┌─────────────────┐
│  Live2D渲染    │  ← live2d-py
└─────────────────┘
"""

import cv2
import numpy as np
import time

from .stage1_mediapipe import FaceMeshDetector
from .stage2_landmarks import FacialLandmarks
from .stage3_head_pose import HeadPoseEstimator
from .stage4_parameter_mapping import ParameterMapper
from .stage5_smoothing import MultiStageSmoother, VelocityLimiter
from .visualization import FaceCaptureVisualizer


class FaceCaptureSystem:
    """完整的面部捕捉系统"""
    
    def __init__(self, show_debug=True, smoothing_enabled=True):
        """
        初始化面部捕捉系统
        :param show_debug: 是否显示调试信息
        :param smoothing_enabled: 是否启用平滑滤波
        """
        # 核心组件
        self.detector = FaceMeshDetector()
        self.feature_extractor = FacialLandmarks()
        self.pose_estimator = HeadPoseEstimator()
        self.parameter_mapper = ParameterMapper()
        self.smoother = MultiStageSmoother()
        self.velocity_limiter = VelocityLimiter(max_velocity=30)
        self.visualizer = FaceCaptureVisualizer()
        
        # 配置
        self.show_debug = show_debug
        self.smoothing_enabled = smoothing_enabled
        
        # 状态
        self.running = False
        self.frame_count = 0
        self.fps = 0
        self.start_time = time.time()
        
        # Live2D 模型（延迟加载）
        self.live2d_model = None
        
        # 缓存数据
        self.last_parameters = {}
    
    def start(self):
        """启动系统"""
        self.running = True
        self.frame_count = 0
        self.start_time = time.time()
        print("🎯 面部捕捉系统已启动")
    
    def stop(self):
        """停止系统"""
        self.running = False
        print("✅ 面部捕捉系统已停止")
    
    def process_frame(self, frame):
        """
        处理单帧图像
        :param frame: BGR 格式图像
        :return: 处理后的图像、Live2D 参数
        """
        if not self.running:
            return frame, {}
        
        # 镜像翻转（自拍模式）
        frame = cv2.flip(frame, 1)
        frame_shape = frame.shape
        
        # 1. 人脸检测
        results = self.detector.process_frame(frame)
        
        # 2. 获取关键点
        landmarks = self.detector.get_landmarks_array(results)
        
        # 3. 提取特征
        features = self.feature_extractor.extract_all_features(landmarks)
        
        # 4. 估计姿态
        pose = self.pose_estimator.estimate(landmarks, frame_shape)
        
        # 5. 参数映射
        parameters = self.parameter_mapper.map_all_features(
            pose=pose,
            eye_features=features.get('eyes'),
            mouth_features=features.get('mouth'),
            brow_features=features.get('eyebrows')
        )
        
        # 6. 平滑滤波
        if self.smoothing_enabled and parameters:
            parameters = self.smoother.smooth(parameters)
            parameters = self.velocity_limiter.limit(parameters)
        
        # 7. 更新缓存
        self.last_parameters = parameters
        
        # 8. 可视化（调试模式）
        if self.show_debug:
            frame = self._draw_debug_info(frame, pose, parameters, features)
        
        # 9. 更新 FPS
        self._update_fps()
        
        return frame, parameters
    
    def _draw_debug_info(self, frame, pose, parameters, features):
        """
        绘制调试信息
        :param frame: 原始图像
        :param pose: 姿态估计结果
        :param parameters: Live2D 参数
        :param features: 面部特征
        :return: 绘制后的图像
        """
        # 绘制关键点
        frame = self.detector.draw_landmarks(frame, pose)
        
        # 绘制姿态信息
        if pose and pose.get('success', False):
            frame = self.pose_estimator.draw_axis(frame, pose)
            frame = self.pose_estimator.draw_pose_info(frame, pose)
        
        # 绘制特征值
        y_offset = 30
        if features.get('eyes'):
            cv2.putText(frame, 
                       f"Eye Open: {features['eyes']['avg_open']:.2f}",
                       (10, frame.shape[0] - y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if features.get('mouth'):
            cv2.putText(frame, 
                       f"Mouth: {features['mouth']['open']:.2f} | Smile: {features['mouth']['smile']:.2f}",
                       (10, frame.shape[0] - y_offset - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 绘制参数条
        if parameters:
            # 只显示几个关键参数
            key_params = {k: v for k, v in parameters.items() if k in 
                         ['ParamAngleX', 'ParamAngleY', 'ParamAngleZ', 'ParamMouthOpenY']}
            frame = self.visualizer.draw_parameter_bars(frame, key_params, 
                                                      (frame.shape[1] - 200, 10),
                                                      width=150, height=15)
        
        # 绘制 FPS
        frame = self.visualizer.draw_fps(frame, self.fps)
        
        return frame
    
    def _update_fps(self):
        """更新帧率计算"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
    
    def set_live2d_model(self, model):
        """
        设置 Live2D 模型
        :param model: Live2D 模型对象
        """
        self.live2d_model = model
    
    def apply_to_model(self):
        """将参数应用到 Live2D 模型"""
        if self.live2d_model and self.last_parameters:
            self.parameter_mapper.apply_parameters_to_model(
                self.live2d_model, 
                self.last_parameters
            )
    
    def get_parameters(self):
        """获取当前参数"""
        return self.last_parameters.copy()
    
    def reset(self):
        """重置系统状态"""
        self.smoother.reset()
        self.velocity_limiter.reset()
        self.last_parameters = {}
        self.frame_count = 0
        self.fps = 0


def demo():
    """演示函数：完整面部捕捉系统"""
    print("🎯 完整面部捕捉系统演示")
    print("📋 按 'q' 退出")
    print("📋 按 's' 切换平滑模式")
    
    # 初始化系统
    system = FaceCaptureSystem(show_debug=True, smoothing_enabled=True)
    system.start()
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # 处理帧
        frame, parameters = system.process_frame(frame)
        
        # 显示结果
        cv2.imshow("Face Capture System", frame)
        
        # 打印参数（每10帧打印一次）
        if system.frame_count % 10 == 0 and parameters:
            print(f"\rFPS: {system.fps:.1f} | Params: {len(parameters)}", end='')
        
        # 处理键盘输入
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            system.smoothing_enabled = not system.smoothing_enabled
            status = "ON" if system.smoothing_enabled else "OFF"
            print(f"\n🔄 平滑模式: {status}")
    
    # 清理
    system.stop()
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ 演示结束")


if __name__ == "__main__":
    demo()