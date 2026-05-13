"""
Live2D 面部捕捉桌宠系统 - 主入口文件

功能：将面部捕捉与 Live2D 模型相结合，实现实时面部驱动

学习路径：
阶段 1：基础环境搭建与 MediaPipe 集成
阶段 2：面部特征点提取与可视化
阶段 3：头部姿态估计（PnP算法）
阶段 4：Live2D 参数映射
阶段 5：平滑滤波与抖动抑制
阶段 6：完整系统集成
阶段 7：动作录制与导出

快捷键：
- q: 退出程序
- s: 切换平滑模式
- r: 开始/停止录制
- f: 切换全屏模式
"""

import sys
import cv2
import numpy as np

# 尝试导入面部捕捉模块
try:
    from src.face_capture import (
        FaceMeshDetector,
        FacialLandmarks,
        HeadPoseEstimator,
        ParameterMapper,
        MultiStageSmoother,
        VelocityLimiter,
        FaceCaptureVisualizer,
        FaceCaptureSystem,
        MotionRecorder
    )
    FACE_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 面部捕捉模块导入失败: {e}")
    FACE_CAPTURE_AVAILABLE = False

# 尝试导入 Live2D 模块
try:
    from src.live2d import Live2DModel, Live2DRenderer
    LIVE2D_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Live2D 模块导入失败: {e}")
    LIVE2D_AVAILABLE = False


class Application:
    """主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.running = False
        self.face_capture_system = None
        self.motion_recorder = None
        self.recording = False
        
        # 状态标志
        self.smoothing_enabled = True
        self.show_debug = True
        self.fullscreen = False
        
        # 摄像头
        self.cap = None
        
        # UI 窗口
        self.window_name = "Live2D Face Capture"
    
    def init_camera(self):
        """初始化摄像头"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ 无法打开摄像头")
            return False
        
        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return True
    
    def init_face_capture(self):
        """初始化面部捕捉系统"""
        if not FACE_CAPTURE_AVAILABLE:
            return False
        
        self.face_capture_system = FaceCaptureSystem(
            show_debug=self.show_debug,
            smoothing_enabled=self.smoothing_enabled
        )
        self.face_capture_system.start()
        return True
    
    def init_recorder(self):
        """初始化动作录制器"""
        self.motion_recorder = MotionRecorder(fps=30)
    
    def run(self):
        """运行应用"""
        print("🎯 Live2D 面部捕捉桌宠系统")
        print("📋 快捷键: q=退出, s=切换平滑, r=录制, f=全屏")
        
        # 初始化组件
        if not self.init_camera():
            return
        
        if not self.init_face_capture():
            print("⚠️ 面部捕捉不可用，仅显示摄像头画面")
        
        self.init_recorder()
        
        self.running = True
        
        while self.running:
            # 读取帧
            success, frame = self.cap.read()
            if not success:
                print("❌ 无法读取帧")
                break
            
            # 处理帧
            if self.face_capture_system:
                frame, parameters = self.face_capture_system.process_frame(frame)
                
                # 录制
                if self.recording and parameters:
                    self.motion_recorder.record_frame(parameters)
            
            # 显示
            cv2.imshow(self.window_name, frame)
            
            # 处理键盘输入
            key = cv2.waitKey(1) & 0xFF
            self.handle_keyboard(key)
        
        # 清理
        self.cleanup()
    
    def handle_keyboard(self, key):
        """处理键盘输入"""
        if key == ord('q'):
            # 退出
            self.running = False
        
        elif key == ord('s'):
            # 切换平滑模式
            if self.face_capture_system:
                self.face_capture_system.smoothing_enabled = not self.face_capture_system.smoothing_enabled
                status = "ON" if self.face_capture_system.smoothing_enabled else "OFF"
                print(f"\n🔄 平滑模式: {status}")
        
        elif key == ord('r'):
            # 开始/停止录制
            if self.motion_recorder:
                if not self.recording:
                    self.motion_recorder.start_recording()
                    self.recording = True
                else:
                    self.motion_recorder.stop_recording()
                    self.recording = False
                    # 导出录制数据
                    filename = f"motion_{int(time.time())}.motion3.json"
                    self.motion_recorder.export_to_motion3(filename)
        
        elif key == ord('f'):
            # 切换全屏
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            print(f"\n🔲 全屏模式: {'ON' if self.fullscreen else 'OFF'}")
    
    def cleanup(self):
        """清理资源"""
        print("\n✅ 正在清理资源...")
        
        if self.cap:
            self.cap.release()
        
        if self.face_capture_system:
            self.face_capture_system.stop()
        
        cv2.destroyAllWindows()
        print("✅ 程序结束")


def main():
    """主函数"""
    app = Application()
    app.run()


if __name__ == "__main__":
    import time
    main()