"""
阶段 3：头部姿态估计（PnP算法）

功能：使用 Perspective-n-Point 算法估计头部的三维姿态

学习目标：
- 理解 PnP 算法原理
- 掌握头部姿态估计方法
- 学习将 2D 关键点映射到 3D 姿态

核心概念：
- PnP (Perspective-n-Point): 从 2D 图像点估计 3D 姿态
- 欧拉角: 俯仰角(pitch)、偏航角(yaw)、翻滚角(roll)
- 相机内参: 焦距、主点坐标

坐标系：
- 世界坐标系: 以人脸中心为原点
- 图像坐标系: 以图像左上角为原点
- 相机坐标系: 以相机光心为原点
"""

import cv2
import numpy as np


class HeadPoseEstimator:
    """头部姿态估计器"""
    
    def __init__(self, camera_matrix=None, dist_coeffs=None):
        """
        初始化姿态估计器
        :param camera_matrix: 相机内参矩阵 (3x3)
        :param dist_coeffs: 畸变系数
        """
        # 默认相机内参（假设 640x480 分辨率）
        if camera_matrix is None:
            self.camera_matrix = np.array([
                [640, 0, 320],    # fx, 0, cx
                [0, 640, 240],    # 0, fy, cy
                [0, 0, 1]         # 0, 0, 1
            ], dtype=np.float32)
        else:
            self.camera_matrix = camera_matrix
        
        # 默认畸变系数（假设无畸变）
        if dist_coeffs is None:
            self.dist_coeffs = np.zeros((4, 1), dtype=np.float32)
        else:
            self.dist_coeffs = dist_coeffs
        
        # 3D 面部模型关键点（单位：毫米）
        # 基于通用人脸模型定义
        self.model_points = np.array([
            [0.0, 0.0, 0.0],             # 鼻尖 (33)
            [0.0, -330.0, -65.0],        # 下巴 (1)
            [-225.0, 170.0, -135.0],     # 左眼外侧角 (133)
            [225.0, 170.0, -135.0],      # 右眼外侧角 (362)
            [-150.0, -150.0, -125.0],    # 左嘴角 (57)
            [150.0, -150.0, -125.0],     # 右嘴角 (287)
            [0.0, 250.0, -50.0],         # 额头中心点
            [0.0, -180.0, -100.0],       # 嘴唇中心点
        ], dtype=np.float32)
    
    def estimate(self, landmarks_2d, frame_shape):
        """
        估计头部姿态
        :param landmarks_2d: (N, 2) 的 2D 关键点数组（归一化坐标）
        :param frame_shape: 图像形状 (height, width)
        :return: 包含姿态信息的字典
        """
        if landmarks_2d is None:
            return None
        
        height, width = frame_shape[:2]
        
        # 选择用于姿态估计的关键点索引
        # 对应 model_points 的顺序
        landmark_indices = [33, 1, 133, 362, 57, 287, 10, 13]
        
        # 获取对应的 2D 关键点并转换为像素坐标
        image_points = []
        for idx in landmark_indices:
            if idx < len(landmarks_2d):
                x = landmarks_2d[idx, 0] * width
                y = landmarks_2d[idx, 1] * height
                image_points.append([x, y])
        
        image_points = np.array(image_points, dtype=np.float32)
        
        # 确保有足够的点进行估计
        if len(image_points) < 4:
            return None
        
        try:
            # 使用 SOLVEPNP_ITERATIVE 方法求解 PnP
            # 其他选项: SOLVEPNP_P3P, SOLVEPNP_EPNP
            success, rotation_vec, translation_vec = cv2.solvePnP(
                self.model_points,
                image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return None
            
            # 将旋转向量转换为旋转矩阵
            rotation_matrix, _ = cv2.Rodrigues(rotation_vec)
            
            # 将旋转矩阵转换为欧拉角（弧度）
            # 返回顺序: pitch, yaw, roll
            euler_angles = self._rotation_matrix_to_euler(rotation_matrix)
            
            # 计算头部在图像中的位置
            head_position = self._calculate_head_position(landmarks_2d, frame_shape)
            
            return {
                'rotation_vector': rotation_vec,      # 旋转向量 (3x1)
                'rotation_matrix': rotation_matrix,    # 旋转矩阵 (3x3)
                'translation_vector': translation_vec, # 平移向量 (3x1)
                'euler_angles': euler_angles,          # 欧拉角 (pitch, yaw, roll)
                'head_position': head_position,        # 头部位置 (x, y, size)
                'success': True
            }
        
        except Exception as e:
            print(f"姿态估计失败: {e}")
            return None
    
    def _rotation_matrix_to_euler(self, rotation_matrix):
        """
        将旋转矩阵转换为欧拉角
        :param rotation_matrix: 3x3 旋转矩阵
        :return: (pitch, yaw, roll) 欧拉角（弧度）
        """
        # 参考: https://www.learnopencv.com/rotation-matrix-to-euler-angles/
        
        # 提取欧拉角
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        
        singular = sy < 1e-6
        
        if not singular:
            # 正常情况
            roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            pitch = np.arctan2(-rotation_matrix[2, 0], sy)
            yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            # 奇异情况（万向锁）
            roll = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            pitch = np.arctan2(-rotation_matrix[2, 0], sy)
            yaw = 0.0
        
        return np.array([pitch, yaw, roll])
    
    def _calculate_head_position(self, landmarks, frame_shape):
        """
        计算头部在图像中的位置和大小
        :param landmarks: 关键点数组
        :param frame_shape: 图像形状
        :return: 包含位置和大小的字典
        """
        if landmarks is None:
            return None
        
        height, width = frame_shape[:2]
        
        # 使用面部轮廓关键点计算头部边界
        chin = landmarks[0]    # 下巴
        forehead = landmarks[10] # 额头
        left_cheek = landmarks[234] # 左脸颊
        right_cheek = landmarks[454] # 右脸颊
        
        # 转换为像素坐标
        points = np.array([
            [chin[0] * width, chin[1] * height],
            [forehead[0] * width, forehead[1] * height],
            [left_cheek[0] * width, left_cheek[1] * height],
            [right_cheek[0] * width, right_cheek[1] * height]
        ])
        
        # 计算边界框
        min_x = np.min(points[:, 0])
        max_x = np.max(points[:, 0])
        min_y = np.min(points[:, 1])
        max_y = np.max(points[:, 1])
        
        # 计算中心点
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # 计算头部大小（边界框对角线长度）
        size = np.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2)
        
        return {
            'x': center_x / width,      # 归一化 x 坐标
            'y': center_y / height,     # 归一化 y 坐标
            'size': size / min(width, height),  # 归一化大小
            'bbox': (min_x, min_y, max_x - min_x, max_y - min_y)
        }
    
    def draw_axis(self, frame, pose):
        """
        在图像上绘制姿态坐标轴
        :param frame: 原始图像
        :param pose: 姿态估计结果
        :return: 绘制后的图像
        """
        if pose is None or not pose.get('success', False):
            return frame
        
        height, width = frame.shape[:2]
        
        # 定义坐标轴端点（在 3D 空间中）
        axis_length = 100  # 轴长度
        axis_points_3d = np.float32([
            [axis_length, 0, 0],    # X 轴（红色）
            [0, axis_length, 0],    # Y 轴（绿色）
            [0, 0, axis_length]     # Z 轴（蓝色）
        ])
        
        # 将 3D 点投影到 2D 图像平面
        axis_points_2d, _ = cv2.projectPoints(
            axis_points_3d,
            pose['rotation_vector'],
            pose['translation_vector'],
            self.camera_matrix,
            self.dist_coeffs
        )
        
        # 获取鼻尖位置作为坐标轴原点
        nose_tip_2d, _ = cv2.projectPoints(
            np.float32([[0, 0, 0]]),
            pose['rotation_vector'],
            pose['translation_vector'],
            self.camera_matrix,
            self.dist_coeffs
        )
        
        origin = tuple(nose_tip_2d[0][0].astype(int))
        
        # 绘制坐标轴
        cv2.line(frame, origin, tuple(axis_points_2d[0][0].astype(int)), (0, 0, 255), 3)  # X
        cv2.line(frame, origin, tuple(axis_points_2d[1][0].astype(int)), (0, 255, 0), 3)  # Y
        cv2.line(frame, origin, tuple(axis_points_2d[2][0].astype(int)), (255, 0, 0), 3)  # Z
        
        # 添加标签
        cv2.putText(frame, 'X', tuple(axis_points_2d[0][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, 'Y', tuple(axis_points_2d[1][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, 'Z', tuple(axis_points_2d[2][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        return frame
    
    def draw_pose_info(self, frame, pose):
        """
        在图像上绘制姿态信息
        :param frame: 原始图像
        :param pose: 姿态估计结果
        :return: 绘制后的图像
        """
        if pose is None or not pose.get('success', False):
            return frame
        
        euler_angles = pose['euler_angles']
        
        # 将弧度转换为角度
        pitch_deg = np.degrees(euler_angles[0])
        yaw_deg = np.degrees(euler_angles[1])
        roll_deg = np.degrees(euler_angles[2])
        
        # 在图像上显示角度信息
        info_text = [
            f"Pitch: {pitch_deg:+.1f}°",
            f"Yaw: {yaw_deg:+.1f}°",
            f"Roll: {roll_deg:+.1f}°"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + i * 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame


def demo():
    """演示函数：头部姿态估计"""
    print("🎯 头部姿态估计演示")
    print("📋 按 'q' 退出")
    
    from .stage1_mediapipe import FaceMeshDetector
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    detector = FaceMeshDetector()
    pose_estimator = HeadPoseEstimator()
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        results = detector.process_frame(frame)
        
        landmarks = detector.get_landmarks_array(results)
        
        if landmarks is not None:
            # 估计头部姿态
            pose = pose_estimator.estimate(landmarks, frame.shape)
            
            if pose:
                # 绘制坐标轴
                frame = pose_estimator.draw_axis(frame, pose)
                
                # 绘制姿态信息
                frame = pose_estimator.draw_pose_info(frame, pose)
        
        # 绘制关键点
        frame = detector.draw_landmarks(frame, results)
        
        cv2.imshow("Head Pose Estimation", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 程序结束")


if __name__ == "__main__":
    demo()