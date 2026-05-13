"""
可视化工具模块

功能：提供面部捕捉数据的可视化功能

学习目标：
- 理解可视化在调试中的作用
- 掌握多种可视化方法
- 学习如何调试面部捕捉系统

可视化类型：
1. 关键点绘制
2. 姿态坐标轴
3. 参数实时图表
4. 调试信息面板
"""

import cv2
import numpy as np


class FaceCaptureVisualizer:
    """面部捕捉可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        # 颜色配置
        self.colors = {
            'landmark': (0, 255, 0),      # 绿色
            'contour': (0, 255, 255),     # 黄色
            'eye': (255, 0, 0),           # 红色
            'mouth': (0, 0, 255),         # 蓝色
            'axis_x': (0, 0, 255),        # 红色
            'axis_y': (0, 255, 0),        # 绿色
            'axis_z': (255, 0, 0),        # 蓝色
            'text': (255, 255, 255),      # 白色
            'success': (0, 255, 0),       # 绿色
            'warning': (0, 255, 255),     # 黄色
            'error': (255, 0, 0)          # 红色
        }
    
    def draw_landmarks(self, frame, landmarks, frame_shape):
        """
        绘制关键点
        :param frame: 原始图像
        :param landmarks: 关键点数组 (N, 2) 或 (N, 3)
        :param frame_shape: 图像形状
        :return: 绘制后的图像
        """
        if landmarks is None:
            return frame
        
        height, width = frame_shape[:2]
        
        for i, landmark in enumerate(landmarks):
            # 转换为像素坐标
            x = int(landmark[0] * width)
            y = int(landmark[1] * height)
            
            # 绘制关键点
            cv2.circle(frame, (x, y), 2, self.colors['landmark'], -1)
            
            # 为特殊点添加标签
            if i == 0:  # 下巴
                cv2.putText(frame, 'Chin', (x+5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
            elif i == 33:  # 鼻尖
                cv2.putText(frame, 'Nose', (x+5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
            elif i == 133:  # 左眼外侧角
                cv2.putText(frame, 'LE', (x+5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
            elif i == 362:  # 右眼外侧角
                cv2.putText(frame, 'RE', (x+5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
        
        return frame
    
    def draw_pose_axis(self, frame, pose, camera_matrix, dist_coeffs):
        """
        绘制姿态坐标轴
        :param frame: 原始图像
        :param pose: 姿态估计结果
        :param camera_matrix: 相机内参
        :param dist_coeffs: 畸变系数
        :return: 绘制后的图像
        """
        if pose is None or not pose.get('success', False):
            return frame
        
        axis_length = 50
        axis_points_3d = np.float32([
            [axis_length, 0, 0],
            [0, axis_length, 0],
            [0, 0, axis_length]
        ])
        
        axis_points_2d, _ = cv2.projectPoints(
            axis_points_3d,
            pose['rotation_vector'],
            pose['translation_vector'],
            camera_matrix,
            dist_coeffs
        )
        
        nose_tip_2d, _ = cv2.projectPoints(
            np.float32([[0, 0, 0]]),
            pose['rotation_vector'],
            pose['translation_vector'],
            camera_matrix,
            dist_coeffs
        )
        
        origin = tuple(nose_tip_2d[0][0].astype(int))
        
        cv2.line(frame, origin, tuple(axis_points_2d[0][0].astype(int)), 
                 self.colors['axis_x'], 3)
        cv2.line(frame, origin, tuple(axis_points_2d[1][0].astype(int)), 
                 self.colors['axis_y'], 3)
        cv2.line(frame, origin, tuple(axis_points_2d[2][0].astype(int)), 
                 self.colors['axis_z'], 3)
        
        cv2.putText(frame, 'X', tuple(axis_points_2d[0][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['axis_x'], 2)
        cv2.putText(frame, 'Y', tuple(axis_points_2d[1][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['axis_y'], 2)
        cv2.putText(frame, 'Z', tuple(axis_points_2d[2][0].astype(int)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['axis_z'], 2)
        
        return frame
    
    def draw_info_panel(self, frame, info_dict, position=(10, 10)):
        """
        绘制信息面板
        :param frame: 原始图像
        :param info_dict: 信息字典
        :param position: 起始位置
        :return: 绘制后的图像
        """
        x, y = position
        line_height = 25
        font_size = 0.6
        
        for i, (key, value) in enumerate(info_dict.items()):
            text = f"{key}: {value}"
            cv2.putText(frame, text, (x, y + i * line_height), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size, 
                       self.colors['text'], 1)
        
        return frame
    
    def draw_parameter_bars(self, frame, parameters, position=(10, 10), width=100, height=20):
        """
        绘制参数条形图
        :param frame: 原始图像
        :param parameters: 参数字典
        :param position: 起始位置
        :param width: 条形图宽度
        :param height: 条形图高度
        :return: 绘制后的图像
        """
        x, y = position
        gap = 5
        
        for i, (param_name, value) in enumerate(parameters.items()):
            # 计算条形图位置
            bar_x = x
            bar_y = y + i * (height + gap)
            
            # 归一化值到 0-1
            normalized_value = self._normalize_value(param_name, value)
            
            # 绘制背景
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + width, bar_y + height), 
                         (50, 50, 50), -1)
            
            # 绘制条形
            bar_width = int(width * normalized_value)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + height), 
                         self.colors['success'], -1)
            
            # 绘制参数名和值
            text = f"{param_name}: {value:.2f}"
            cv2.putText(frame, text, (bar_x + width + 5, bar_y + height - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
        
        return frame
    
    def _normalize_value(self, param_name, value):
        """
        将参数值归一化到 0-1 范围
        :param param_name: 参数名
        :param value: 参数值
        :return: 归一化后的值
        """
        # Live2D 参数的典型范围
        ranges = {
            'ParamAngleX': (-30, 30),
            'ParamAngleY': (-20, 20),
            'ParamAngleZ': (-15, 15),
            'ParamBodyAngleX': (-10, 10),
            'ParamEyeBallX': (-1, 1),
            'ParamEyeBallY': (-1, 1),
            'ParamMouthOpenY': (0, 1),
            'ParamMouthForm': (-1, 1),
            'ParamEyeblowL': (-1, 1),
            'ParamEyeblowR': (-1, 1),
        }
        
        if param_name in ranges:
            min_val, max_val = ranges[param_name]
            return (value - min_val) / (max_val - min_val)
        else:
            return max(0, min(1, (value + 1) / 2))  # 默认处理
    
    def draw_fps(self, frame, fps, position=(10, 30)):
        """
        绘制 FPS
        :param frame: 原始图像
        :param fps: 帧率
        :param position: 位置
        :return: 绘制后的图像
        """
        color = self.colors['success'] if fps >= 25 else self.colors['warning']
        cv2.putText(frame, f"FPS: {int(fps)}", position, 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return frame
    
    def draw_status_indicator(self, frame, status, position=(frame.shape[1]-100, 30)):
        """
        绘制状态指示器
        :param frame: 原始图像
        :param status: 状态 ('success', 'warning', 'error')
        :param position: 位置
        :return: 绘制后的图像
        """
        colors = {
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }
        
        color = colors.get(status, self.colors['error'])
        cv2.circle(frame, position, 10, color, -1)
        cv2.putText(frame, status, (position[0]+15, position[1]+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['text'], 1)
        
        return frame


class DebugVisualizer:
    """调试可视化器（用于开发调试）"""
    
    def __init__(self):
        """初始化调试可视化器"""
        self.visualizer = FaceCaptureVisualizer()
        self.debug_data = {}
    
    def update_debug_data(self, key, value):
        """
        更新调试数据
        :param key: 数据键
        :param value: 数据值
        """
        self.debug_data[key] = value
    
    def draw_debug_panel(self, frame):
        """
        绘制调试面板
        :param frame: 原始图像
        :return: 绘制后的图像
        """
        # 绘制信息面板
        info_dict = {}
        for key, value in self.debug_data.items():
            if isinstance(value, float):
                info_dict[key] = f"{value:.2f}"
            elif isinstance(value, np.ndarray):
                info_dict[key] = f"array({value.shape})"
            else:
                info_dict[key] = str(value)
        
        frame = self.visualizer.draw_info_panel(frame, info_dict, (10, 10))
        
        return frame
    
    def draw_face_mesh(self, frame, landmarks, frame_shape):
        """
        绘制面部网格
        :param frame: 原始图像
        :param landmarks: 关键点数组
        :param frame_shape: 图像形状
        :return: 绘制后的图像
        """
        if landmarks is None:
            return frame
        
        height, width = frame_shape[:2]
        
        # 绘制面部轮廓连接
        contour_indices = [0, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 16]
        for i in range(len(contour_indices)-1):
            idx1 = contour_indices[i]
            idx2 = contour_indices[i+1]
            if idx1 < len(landmarks) and idx2 < len(landmarks):
                x1, y1 = int(landmarks[idx1, 0] * width), int(landmarks[idx1, 1] * height)
                x2, y2 = int(landmarks[idx2, 0] * width), int(landmarks[idx2, 1] * height)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        
        # 绘制眼睛区域
        eye_indices = [36, 37, 38, 39, 40, 41, 36, 42, 43, 44, 45, 46, 47, 42]
        for i in range(len(eye_indices)-1):
            idx1 = eye_indices[i]
            idx2 = eye_indices[i+1]
            if idx1 < len(landmarks) and idx2 < len(landmarks):
                x1, y1 = int(landmarks[idx1, 0] * width), int(landmarks[idx1, 1] * height)
                x2, y2 = int(landmarks[idx2, 0] * width), int(landmarks[idx2, 1] * height)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # 绘制嘴巴区域
        mouth_indices = list(range(48, 68)) + [48]
        for i in range(len(mouth_indices)-1):
            idx1 = mouth_indices[i]
            idx2 = mouth_indices[i+1]
            if idx1 < len(landmarks) and idx2 < len(landmarks):
                x1, y1 = int(landmarks[idx1, 0] * width), int(landmarks[idx1, 1] * height)
                x2, y2 = int(landmarks[idx2, 0] * width), int(landmarks[idx2, 1] * height)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        return frame


def demo():
    """演示函数：可视化工具"""
    print("🎯 可视化工具演示")
    
    # 创建可视化器
    visualizer = FaceCaptureVisualizer()
    
    # 创建示例图像
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 绘制示例信息
    info = {
        'Status': 'Running',
        'Faces Detected': 1,
        'FPS': 30,
        'Landmarks': 468
    }
    frame = visualizer.draw_info_panel(frame, info)
    
    # 绘制示例参数条
    params = {
        'ParamAngleX': 15.5,
        'ParamAngleY': -8.3,
        'ParamMouthOpenY': 0.6
    }
    frame = visualizer.draw_parameter_bars(frame, params, (10, 100))
    
    # 绘制 FPS
    frame = visualizer.draw_fps(frame, 30)
    
    # 绘制状态指示器
    frame = visualizer.draw_status_indicator(frame, 'success')
    
    # 保存图像
    cv2.imwrite('visualization_demo.png', frame)
    print("✅ 可视化演示完成，图像已保存为 visualization_demo.png")


if __name__ == "__main__":
    demo()