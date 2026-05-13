"""
阶段 2：面部特征点提取与可视化

功能：将 468 个关键点按面部区域分组，提取有用特征

学习目标：
- 理解 468 个关键点的分布和含义
- 掌握关键点分组方法
- 学习从关键点中提取面部特征

关键点分组：
- 下巴轮廓 (0-16)
- 左眼眉 (17-21)
- 右眼眉 (22-26)
- 左眼 (36-45)
- 右眼 (42-47)
- 鼻子 (27-35)
- 嘴巴外围 (48-60)
- 嘴巴内部 (61-67)
- 虹膜关键点 (468个中的高精度点)
"""

import cv2
import numpy as np


class FacialLandmarks:
    """面部特征点处理器"""
    
    # MediaPipe Face Mesh 关键点索引定义
    # 参考：https://solutions.mediapipe.dev/face_mesh
    CHIN = list(range(0, 17))  # 下巴轮廓
    LEFT_EYEBROW = list(range(17, 22))  # 左眉毛
    RIGHT_EYEBROW = list(range(22, 27))  # 右眉毛
    NOSE = list(range(27, 36))  # 鼻子
    LEFT_EYE = list(range(36, 42))  # 左眼轮廓
    RIGHT_EYE = list(range(42, 48))  # 右眼轮廓
    MOUTH_OUTER = list(range(48, 61))  # 嘴巴外围
    MOUTH_INNER = list(range(61, 68))  # 嘴巴内部
    
    # 虹膜关键点（高精度模式下可用）
    LEFT_IRIS = [468, 469, 470, 471, 472]
    RIGHT_IRIS = [473, 474, 475, 476, 477]
    
    # 面部特征关键点（用于姿态估计）
    FACE_POINTS = [
        1,   # 下巴尖
        33,  # 鼻尖
        133, # 左眼外侧角
        362, # 右眼外侧角
        263, # 右眼内侧角
        159, # 左眼内侧角
        57,  # 左嘴角
        287  # 右嘴角
    ]
    
    def __init__(self):
        """初始化特征点处理器"""
        pass
    
    def get_region(self, landmarks, region):
        """
        获取指定区域的关键点
        :param landmarks: (468, 3) 的关键点数组
        :param region: 区域索引列表（如 CHIN, LEFT_EYE 等）
        :return: 该区域的关键点数组
        """
        if landmarks is None:
            return None
        return landmarks[region]
    
    def get_chin(self, landmarks):
        """获取下巴轮廓关键点"""
        return self.get_region(landmarks, self.CHIN)
    
    def get_left_eyebrow(self, landmarks):
        """获取左眉毛关键点"""
        return self.get_region(landmarks, self.LEFT_EYEBROW)
    
    def get_right_eyebrow(self, landmarks):
        """获取右眉毛关键点"""
        return self.get_region(landmarks, self.RIGHT_EYEBROW)
    
    def get_nose(self, landmarks):
        """获取鼻子关键点"""
        return self.get_region(landmarks, self.NOSE)
    
    def get_left_eye(self, landmarks):
        """获取左眼关键点"""
        return self.get_region(landmarks, self.LEFT_EYE)
    
    def get_right_eye(self, landmarks):
        """获取右眼关键点"""
        return self.get_region(landmarks, self.RIGHT_EYE)
    
    def get_mouth_outer(self, landmarks):
        """获取嘴巴外围关键点"""
        return self.get_region(landmarks, self.MOUTH_OUTER)
    
    def get_mouth_inner(self, landmarks):
        """获取嘴巴内部关键点"""
        return self.get_region(landmarks, self.MOUTH_INNER)
    
    def extract_eye_features(self, landmarks):
        """
        提取眼睛相关特征
        :param landmarks: 关键点数组
        :return: 眼睛特征字典
        """
        if landmarks is None:
            return None
        
        left_eye = self.get_left_eye(landmarks)
        right_eye = self.get_right_eye(landmarks)
        
        # 计算眼睛开合程度
        # 垂直方向距离 / 水平方向距离
        left_eye_open = self._calculate_eye_openness(left_eye)
        right_eye_open = self._calculate_eye_openness(right_eye)
        
        # 计算眼睛中心位置
        left_eye_center = np.mean(left_eye[:, :2], axis=0)
        right_eye_center = np.mean(right_eye[:, :2], axis=0)
        
        return {
            'left_open': left_eye_open,
            'right_open': right_eye_open,
            'avg_open': (left_eye_open + right_eye_open) / 2,
            'left_center': left_eye_center,
            'right_center': right_eye_center,
            'eye_distance': np.linalg.norm(left_eye_center - right_eye_center)
        }
    
    def _calculate_eye_openness(self, eye_landmarks):
        """
        计算单只眼睛的开合程度
        :param eye_landmarks: 眼睛区域的关键点
        :return: 开合程度 (0-1)，1 表示完全睁开
        """
        if eye_landmarks is None or len(eye_landmarks) == 0:
            return 0.5  # 默认值
        
        # 眼睛关键点索引（相对于眼睛区域）
        # 0: 左眼外角 / 右眼外角
        # 1: 左眼上眼睑上缘 / 右眼上眼睑上缘
        # 2: 左眼上眼睑下缘 / 右眼上眼睑下缘
        # 3: 左眼内角 / 右眼内角
        # 4: 左眼下方眼睑下缘 / 右眼下方眼睑下缘
        # 5: 左眼下方眼睑上缘 / 右眼下方眼睑上缘
        
        # 计算垂直方向距离（上下眼睑距离）
        # 点 1 到点 4 的距离，点 2 到点 5 的距离
        vertical_dist1 = np.linalg.norm(eye_landmarks[1, :2] - eye_landmarks[4, :2])
        vertical_dist2 = np.linalg.norm(eye_landmarks[2, :2] - eye_landmarks[5, :2])
        avg_vertical = (vertical_dist1 + vertical_dist2) / 2
        
        # 计算水平方向距离（内外眼角距离）
        horizontal_dist = np.linalg.norm(eye_landmarks[0, :2] - eye_landmarks[3, :2])
        
        if horizontal_dist == 0:
            return 0.5
        
        # 开合程度 = 垂直距离 / 水平距离
        # 归一化到 0-1 范围
        openness = avg_vertical / horizontal_dist
        
        # 正常眼睛开合范围大约在 0.2-0.4 之间，进行归一化
        min_open = 0.15
        max_open = 0.45
        openness = (openness - min_open) / (max_open - min_open)
        openness = np.clip(openness, 0, 1)
        
        return openness
    
    def extract_mouth_features(self, landmarks):
        """
        提取嘴巴相关特征
        :param landmarks: 关键点数组
        :return: 嘴巴特征字典
        """
        if landmarks is None:
            return None
        
        mouth_outer = self.get_mouth_outer(landmarks)
        mouth_inner = self.get_mouth_inner(landmarks)
        
        # 计算嘴巴张开程度
        mouth_open = self._calculate_mouth_openness(mouth_outer, mouth_inner)
        
        # 计算嘴角上扬程度（微笑检测）
        smile = self._calculate_smile(mouth_outer)
        
        # 计算嘴巴宽度
        mouth_width = self._calculate_mouth_width(mouth_outer)
        
        return {
            'open': mouth_open,
            'smile': smile,
            'width': mouth_width
        }
    
    def _calculate_mouth_openness(self, mouth_outer, mouth_inner):
        """
        计算嘴巴张开程度
        :param mouth_outer: 嘴巴外围关键点
        :param mouth_inner: 嘴巴内部关键点
        :return: 张开程度 (0-1)
        """
        if mouth_outer is None or mouth_inner is None:
            return 0.0
        
        # 嘴巴中心点（上唇中心点和下唇中心点）
        upper_lip_center = mouth_outer[12]  # 上唇中央
        lower_lip_center = mouth_outer[18]  # 下唇中央
        
        # 计算垂直距离
        vertical_dist = np.linalg.norm(upper_lip_center[:2] - lower_lip_center[:2])
        
        # 计算嘴巴宽度（嘴角距离）
        left_corner = mouth_outer[0]   # 左嘴角
        right_corner = mouth_outer[6]  # 右嘴角
        width = np.linalg.norm(left_corner[:2] - right_corner[:2])
        
        if width == 0:
            return 0.0
        
        # 张开程度 = 垂直距离 / 宽度
        openness = vertical_dist / width
        
        # 归一化到 0-1
        max_open = 0.8  # 最大张开程度
        openness = min(openness / max_open, 1.0)
        
        return openness
    
    def _calculate_smile(self, mouth_outer):
        """
        计算微笑程度
        :param mouth_outer: 嘴巴外围关键点
        :return: 微笑程度 (0-1)
        """
        if mouth_outer is None:
            return 0.0
        
        # 获取关键点
        left_corner = mouth_outer[0]   # 左嘴角
        right_corner = mouth_outer[6]  # 右嘴角
        upper_center = mouth_outer[12] # 上唇中央
        lower_center = mouth_outer[18] # 下唇中央
        
        # 计算嘴角相对于嘴唇中心的垂直位置
        # 微笑时嘴角会上扬
        mouth_center_y = (upper_center[1] + lower_center[1]) / 2
        
        # 计算嘴角上扬程度
        left_corner_y_diff = mouth_center_y - left_corner[1]
        right_corner_y_diff = mouth_center_y - right_corner[1]
        
        # 计算嘴巴宽度
        width = np.linalg.norm(left_corner[:2] - right_corner[:2])
        
        if width == 0:
            return 0.0
        
        # 微笑程度 = 嘴角上扬距离 / 嘴巴宽度
        avg_y_diff = (left_corner_y_diff + right_corner_y_diff) / 2
        smile = avg_y_diff / width
        
        # 归一化到 0-1
        smile = max(0, smile * 5)  # 放大系数
        smile = min(smile, 1.0)
        
        return smile
    
    def _calculate_mouth_width(self, mouth_outer):
        """
        计算嘴巴宽度
        :param mouth_outer: 嘴巴外围关键点
        :return: 归一化的嘴巴宽度
        """
        if mouth_outer is None:
            return 0.5
        
        left_corner = mouth_outer[0]   # 左嘴角
        right_corner = mouth_outer[6]  # 右嘴角
        
        return np.linalg.norm(left_corner[:2] - right_corner[:2])
    
    def extract_eyebrow_features(self, landmarks):
        """
        提取眉毛相关特征
        :param landmarks: 关键点数组
        :return: 眉毛特征字典
        """
        if landmarks is None:
            return None
        
        left_brow = self.get_left_eyebrow(landmarks)
        right_brow = self.get_right_eyebrow(landmarks)
        
        # 计算眉毛高度（相对于眼睛）
        # 这里简化处理，只计算眉毛中心位置
        left_brow_center = np.mean(left_brow[:, :2], axis=0)
        right_brow_center = np.mean(right_brow[:, :2], axis=0)
        
        # 计算眉毛倾斜程度
        left_brow_tilt = self._calculate_brow_tilt(left_brow)
        right_brow_tilt = self._calculate_brow_tilt(right_brow)
        
        return {
            'left_center': left_brow_center,
            'right_center': right_brow_center,
            'left_tilt': left_brow_tilt,
            'right_tilt': right_brow_tilt,
            'avg_tilt': (left_brow_tilt + right_brow_tilt) / 2
        }
    
    def _calculate_brow_tilt(self, brow):
        """
        计算眉毛倾斜程度
        :param brow: 眉毛关键点
        :return: 倾斜角度（弧度）
        """
        if brow is None or len(brow) < 2:
            return 0.0
        
        # 使用眉毛的第一个和最后一个点计算倾斜
        start = brow[0][:2]
        end = brow[-1][:2]
        
        # 计算角度
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        if dx == 0:
            return 0.0
        
        return np.arctan2(dy, dx)
    
    def extract_all_features(self, landmarks):
        """
        提取所有面部特征
        :param landmarks: 关键点数组
        :return: 包含所有特征的字典
        """
        if landmarks is None:
            return None
        
        return {
            'eyes': self.extract_eye_features(landmarks),
            'mouth': self.extract_mouth_features(landmarks),
            'eyebrows': self.extract_eyebrow_features(landmarks),
            'nose_tip': landmarks[33, :2] if len(landmarks) > 33 else None,
            'chin': landmarks[0, :2] if len(landmarks) > 0 else None
        }


def demo():
    """演示函数：面部特征点提取"""
    print("🎯 面部特征点提取演示")
    print("📋 按 'q' 退出")
    
    # 导入阶段1的检测器
    from .stage1_mediapipe import FaceMeshDetector
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 初始化检测器和特征提取器
    detector = FaceMeshDetector()
    feature_extractor = FacialLandmarks()
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        results = detector.process_frame(frame)
        
        # 获取关键点数组
        landmarks = detector.get_landmarks_array(results)
        
        if landmarks is not None:
            # 提取特征
            features = feature_extractor.extract_all_features(landmarks)
            
            # 在图像上显示特征值
            if features['eyes']:
                cv2.putText(frame, f"Eye Open: {features['eyes']['avg_open']:.2f}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            if features['mouth']:
                cv2.putText(frame, f"Mouth Open: {features['mouth']['open']:.2f}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Smile: {features['mouth']['smile']:.2f}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # 绘制关键点
        frame = detector.draw_landmarks(frame, results)
        
        cv2.imshow("Facial Features Demo", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 程序结束")


if __name__ == "__main__":
    demo()