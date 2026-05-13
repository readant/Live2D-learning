"""
阶段 1：基础环境搭建与 MediaPipe 集成

功能：实时摄像头捕获 + MediaPipe Face Mesh 468 点检测

学习目标：
- 掌握 MediaPipe Face Mesh 的基本使用
- 理解人脸关键点检测流程
- 学习实时图像处理和可视化
"""

import cv2
import mediapipe as mp
import numpy as np

class FaceMeshDetector:
    """人脸关键点检测器"""
    
    def __init__(self, static_image_mode=False, max_num_faces=1):
        """
        初始化检测器
        :param static_image_mode: 是否为静态图像模式（视频流设为 False）
        :param max_num_faces: 最大检测人脸数量
        """
        # 初始化 MediaPipe Face Mesh 组件
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=True,  # 启用高精度关键点（眼睛区域更精细）
            min_detection_confidence=0.5,  # 检测置信度阈值
            min_tracking_confidence=0.5    # 追踪置信度阈值
        )
        
        # 绘图工具配置
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 关键点绘制样式（绿色小点）
        self.landmark_spec = self.mp_drawing.DrawingSpec(
            color=(0, 255, 0),    # 绿色
            thickness=1, 
            circle_radius=1
        )
        
        # 连接线绘制样式（绿色细线条）
        self.connection_spec = self.mp_drawing.DrawingSpec(
            color=(0, 255, 0),
            thickness=1,
            circle_radius=1
        )
    
    def process_frame(self, frame):
        """
        处理单帧图像，检测人脸关键点
        :param frame: BGR 格式图像（OpenCV 默认格式）
        :return: MediaPipe 检测结果对象
        """
        # MediaPipe 需要 RGB 格式，进行格式转换
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False  # 禁用写入以提高性能
        
        # 执行人脸关键点检测
        results = self.face_mesh.process(rgb_frame)
        
        return results
    
    def draw_landmarks(self, frame, results):
        """
        在图像上绘制检测到的关键点和连接线
        :param frame: 原始 BGR 图像
        :param results: process_frame 返回的检测结果
        :return: 绘制后的图像
        """
        frame.flags.writeable = True  # 重新启用写入
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 绘制面部网格（所有关键点连接）
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.connection_spec
                )
                
                # 绘制面部轮廓（黄色）
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(0, 255, 255),  # 黄色
                        thickness=2, 
                        circle_radius=1
                    )
                )
                
                # 绘制左眼轮廓（红色）
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_LEFT_EYE,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(255, 0, 0),  # 红色
                        thickness=2, 
                        circle_radius=1
                    )
                )
                
                # 绘制右眼轮廓（红色）
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_RIGHT_EYE,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(255, 0, 0),
                        thickness=2, 
                        circle_radius=1
                    )
                )
                
                # 绘制嘴巴轮廓（蓝色）
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_LIPS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(0, 0, 255),  # 蓝色
                        thickness=2, 
                        circle_radius=1
                    )
                )
        
        return frame
    
    def get_landmarks_array(self, results):
        """
        将关键点转换为 NumPy 数组格式
        :param results: 检测结果
        :return: (468, 3) 的 NumPy 数组，每行包含 x, y, z 坐标
        """
        if not results.multi_face_landmarks:
            return None
        
        # 获取第一张人脸的关键点
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = []
        
        for landmark in face_landmarks.landmark:
            # x, y 是归一化坐标（0-1），z 是深度信息
            landmarks.append([landmark.x, landmark.y, landmark.z])
        
        return np.array(landmarks, dtype=np.float32)

def main():
    """主函数：实时人脸捕捉演示"""
    print("🎯 人脸捕捉演示程序")
    print("📋 按 'q' 退出")
    print("📋 按 's' 保存当前帧")
    
    # 初始化摄像头（0 为默认摄像头，可尝试 1、2 等其他索引）
    cap = cv2.VideoCapture(0)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("❌ 无法打开摄像头，请检查设备连接")
        return
    
    # 设置摄像头分辨率（根据设备能力调整）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 初始化人脸检测器
    detector = FaceMeshDetector()
    
    # FPS 计算相关变量
    frame_count = 0
    fps = 0
    start_time = cv2.getTickCount()
    save_count = 0
    
    while True:
        # 读取一帧图像
        success, frame = cap.read()
        if not success:
            print("❌ 无法读取帧，可能摄像头已断开")
            break
        
        # 镜像翻转（自拍模式更自然）
        frame = cv2.flip(frame, 1)
        
        # 检测人脸关键点
        results = detector.process_frame(frame)
        
        # 在图像上绘制关键点
        frame = detector.draw_landmarks(frame, results)
        
        # 计算并显示 FPS
        frame_count += 1
        if frame_count % 10 == 0:
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            fps = frame_count / elapsed_time
            frame_count = 0
            start_time = cv2.getTickCount()
        
        # 在图像左上角显示 FPS
        cv2.putText(
            frame, 
            f"FPS: {int(fps)}", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0),  # 绿色文字
            2             # 线条粗细
        )
        
        # 显示提示信息
        cv2.putText(
            frame, 
            "q:退出 | s:保存", 
            (10, 460), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            (255, 255, 255), 
            1
        )
        
        # 显示结果窗口
        cv2.imshow("Face Mesh Demo", frame)
        
        # 处理键盘输入
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # 按 q 退出
            break
        elif key == ord('s'):
            # 按 s 保存当前帧
            save_path = f"face_capture_{save_count:03d}.jpg"
            cv2.imwrite(save_path, frame)
            print(f"📸 已保存: {save_path}")
            save_count += 1
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 程序正常结束")

if __name__ == "__main__":
    main()