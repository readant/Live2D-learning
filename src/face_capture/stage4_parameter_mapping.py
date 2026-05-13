"""
阶段 4：Live2D 参数映射

功能：将面部捕捉数据映射到 Live2D 参数

学习目标：
- 理解 Live2D 参数系统
- 掌握参数映射方法
- 学习如何驱动 Live2D 模型

Live2D 参数说明：
- ParamAngleX: 头部左右旋转 (-30° ~ 30°)
- ParamAngleY: 头部上下旋转 (-30° ~ 30°)
- ParamAngleZ: 头部倾斜 (-15° ~ 15°)
- ParamBodyAngleX: 身体左右旋转 (-10° ~ 10°)
- ParamEyeBallX: 左眼水平移动 (-1 ~ 1)
- ParamEyeBallY: 左眼垂直移动 (-1 ~ 1)
- ParamEyeBallX_2: 右眼水平移动 (-1 ~ 1)
- ParamEyeBallY_2: 右眼垂直移动 (-1 ~ 1)
- ParamMouthOpenY: 嘴巴张开程度 (0 ~ 1)
- ParamMouthForm: 嘴巴形状 (-1 ~ 1)
- ParamEyeblowL: 左眉毛高度 (-1 ~ 1)
- ParamEyeblowR: 右眉毛高度 (-1 ~ 1)
"""

import numpy as np


class ParameterMapper:
    """Live2D 参数映射器"""
    
    def __init__(self):
        """初始化参数映射器"""
        # 参数映射配置
        self.config = {
            # 头部旋转参数
            'angle_x': {
                'param_name': 'ParamAngleX',
                'min_input': -45,    # 输入最小值（度）
                'max_input': 45,     # 输入最大值（度）
                'min_output': -30,   # Live2D 参数最小值
                'max_output': 30,    # Live2D 参数最大值
                'curve': 'linear'    # 映射曲线类型
            },
            'angle_y': {
                'param_name': 'ParamAngleY',
                'min_input': -30,
                'max_input': 30,
                'min_output': -20,
                'max_output': 20,
                'curve': 'linear'
            },
            'angle_z': {
                'param_name': 'ParamAngleZ',
                'min_input': -20,
                'max_input': 20,
                'min_output': -15,
                'max_output': 15,
                'curve': 'linear'
            },
            # 身体旋转参数
            'body_angle_x': {
                'param_name': 'ParamBodyAngleX',
                'min_input': -15,
                'max_input': 15,
                'min_output': -10,
                'max_output': 10,
                'curve': 'linear'
            },
            # 眼球参数
            'eye_x': {
                'param_name': 'ParamEyeBallX',
                'min_input': -0.3,
                'max_input': 0.3,
                'min_output': -1,
                'max_output': 1,
                'curve': 'linear'
            },
            'eye_y': {
                'param_name': 'ParamEyeBallY',
                'min_input': -0.3,
                'max_input': 0.3,
                'min_output': -1,
                'max_output': 1,
                'curve': 'linear'
            },
            # 嘴巴参数
            'mouth_open': {
                'param_name': 'ParamMouthOpenY',
                'min_input': 0,
                'max_input': 1,
                'min_output': 0,
                'max_output': 1,
                'curve': 'ease_in'
            },
            'mouth_form': {
                'param_name': 'ParamMouthForm',
                'min_input': -1,
                'max_input': 1,
                'min_output': -1,
                'max_output': 1,
                'curve': 'linear'
            },
            # 眉毛参数
            'eyebrow_l': {
                'param_name': 'ParamEyeblowL',
                'min_input': -0.5,
                'max_input': 0.5,
                'min_output': -1,
                'max_output': 1,
                'curve': 'linear'
            },
            'eyebrow_r': {
                'param_name': 'ParamEyeblowR',
                'min_input': -0.5,
                'max_input': 0.5,
                'min_output': -1,
                'max_output': 1,
                'curve': 'linear'
            },
            # 表情参数
            'happy': {
                'param_name': 'ParamExpressionHappy',
                'min_input': 0,
                'max_input': 1,
                'min_output': 0,
                'max_output': 1,
                'curve': 'linear'
            },
            'sad': {
                'param_name': 'ParamExpressionSad',
                'min_input': 0,
                'max_input': 1,
                'min_output': 0,
                'max_output': 1,
                'curve': 'linear'
            },
            'angry': {
                'param_name': 'ParamExpressionAngry',
                'min_input': 0,
                'max_input': 1,
                'min_output': 0,
                'max_output': 1,
                'curve': 'linear'
            },
            'surprised': {
                'param_name': 'ParamExpressionSurprised',
                'min_input': 0,
                'max_input': 1,
                'min_output': 0,
                'max_output': 1,
                'curve': 'linear'
            }
        }
    
    def map_pose_to_parameters(self, pose):
        """
        将头部姿态映射到 Live2D 参数
        :param pose: 姿态估计结果
        :return: 参数字典
        """
        if pose is None or not pose.get('success', False):
            return {}
        
        parameters = {}
        euler_angles = pose['euler_angles']
        
        # 将弧度转换为角度
        pitch_deg = np.degrees(euler_angles[0])  # 俯仰角
        yaw_deg = np.degrees(euler_angles[1])    # 偏航角
        roll_deg = np.degrees(euler_angles[2])   # 翻滚角
        
        # 映射头部旋转参数
        parameters['ParamAngleX'] = self._map_value(
            yaw_deg, self.config['angle_x']
        )
        parameters['ParamAngleY'] = self._map_value(
            -pitch_deg, self.config['angle_y']  # 负号调整方向
        )
        parameters['ParamAngleZ'] = self._map_value(
            roll_deg, self.config['angle_z']
        )
        
        # 映射身体旋转（跟随头部，但幅度更小）
        parameters['ParamBodyAngleX'] = self._map_value(
            yaw_deg * 0.3, self.config['body_angle_x']  # 30% 幅度
        )
        
        return parameters
    
    def map_eye_features_to_parameters(self, eye_features):
        """
        将眼睛特征映射到 Live2D 参数
        :param eye_features: 眼睛特征字典
        :return: 参数字典
        """
        if eye_features is None:
            return {}
        
        parameters = {}
        
        # 映射眼睛开合程度
        eye_open = eye_features.get('avg_open', 0.5)
        parameters['ParamEyeOpen'] = eye_open
        
        # 映射眼球位置（基于眼睛中心的相对位置）
        if 'left_center' in eye_features and 'right_center' in eye_features:
            # 计算眼球移动（简化处理，使用归一化坐标）
            left_eye = eye_features['left_center']
            right_eye = eye_features['right_center']
            
            # 假设面部中心在 0.5, 0.5
            eye_center_x = (left_eye[0] + right_eye[0]) / 2
            eye_center_y = (left_eye[1] + right_eye[1]) / 2
            
            # 计算眼球偏移
            gaze_x = (eye_center_x - 0.5) * 2  # 归一化到 -1 ~ 1
            gaze_y = (eye_center_y - 0.5) * 2
            
            parameters['ParamEyeBallX'] = self._map_value(
                gaze_x, self.config['eye_x']
            )
            parameters['ParamEyeBallY'] = self._map_value(
                gaze_y, self.config['eye_y']
            )
            parameters['ParamEyeBallX_2'] = parameters['ParamEyeBallX']
            parameters['ParamEyeBallY_2'] = parameters['ParamEyeBallY']
        
        return parameters
    
    def map_mouth_features_to_parameters(self, mouth_features):
        """
        将嘴巴特征映射到 Live2D 参数
        :param mouth_features: 嘴巴特征字典
        :return: 参数字典
        """
        if mouth_features is None:
            return {}
        
        parameters = {}
        
        # 映射嘴巴张开程度
        mouth_open = mouth_features.get('open', 0.0)
        parameters['ParamMouthOpenY'] = self._map_value(
            mouth_open, self.config['mouth_open']
        )
        
        # 映射微笑到嘴巴形状
        smile = mouth_features.get('smile', 0.0)
        parameters['ParamMouthForm'] = self._map_value(
            smile, self.config['mouth_form']
        )
        
        return parameters
    
    def map_eyebrow_features_to_parameters(self, brow_features):
        """
        将眉毛特征映射到 Live2D 参数
        :param brow_features: 眉毛特征字典
        :return: 参数字典
        """
        if brow_features is None:
            return {}
        
        parameters = {}
        
        # 映射眉毛高度（基于倾斜角度）
        avg_tilt = brow_features.get('avg_tilt', 0.0)
        parameters['ParamEyeblowL'] = self._map_value(
            avg_tilt, self.config['eyebrow_l']
        )
        parameters['ParamEyeblowR'] = self._map_value(
            avg_tilt, self.config['eyebrow_r']
        )
        
        return parameters
    
    def map_all_features(self, pose=None, eye_features=None, 
                        mouth_features=None, brow_features=None):
        """
        映射所有特征到 Live2D 参数
        :param pose: 姿态估计结果
        :param eye_features: 眼睛特征
        :param mouth_features: 嘴巴特征
        :param brow_features: 眉毛特征
        :return: 完整的参数字典
        """
        parameters = {}
        
        # 合并所有参数
        parameters.update(self.map_pose_to_parameters(pose))
        parameters.update(self.map_eye_features_to_parameters(eye_features))
        parameters.update(self.map_mouth_features_to_parameters(mouth_features))
        parameters.update(self.map_eyebrow_features_to_parameters(brow_features))
        
        return parameters
    
    def _map_value(self, value, config):
        """
        将输入值映射到输出范围
        :param value: 输入值
        :param config: 映射配置
        :return: 映射后的输出值
        """
        min_in = config['min_input']
        max_in = config['max_input']
        min_out = config['min_output']
        max_out = config['max_output']
        curve_type = config['curve']
        
        # 裁剪输入值到输入范围
        value = np.clip(value, min_in, max_in)
        
        # 归一化到 0-1
        normalized = (value - min_in) / (max_in - min_in)
        
        # 应用曲线
        normalized = self._apply_curve(normalized, curve_type)
        
        # 映射到输出范围
        output = min_out + normalized * (max_out - min_out)
        
        return output
    
    def _apply_curve(self, value, curve_type):
        """
        应用映射曲线
        :param value: 归一化值 (0-1)
        :param curve_type: 曲线类型
        :return: 处理后的值
        """
        if curve_type == 'linear':
            return value
        elif curve_type == 'ease_in':
            # 缓入曲线（开始慢，后来快）
            return value ** 2
        elif curve_type == 'ease_out':
            # 缓出曲线（开始快，后来慢）
            return 1 - (1 - value) ** 2
        elif curve_type == 'ease_in_out':
            # 缓入缓出曲线
            if value < 0.5:
                return 2 * value ** 2
            else:
                return 1 - (-2 * value + 2) ** 2 / 2
        else:
            return value
    
    def apply_parameters_to_model(self, model, parameters):
        """
        将参数应用到 Live2D 模型
        :param model: Live2D 模型对象
        :param parameters: 参数字典
        """
        if model is None or parameters is None:
            return
        
        for param_name, value in parameters.items():
            model.SetParamFloat(param_name, value)
    
    def get_parameter_ranges(self):
        """
        获取所有参数的范围信息
        :return: 参数范围字典
        """
        ranges = {}
        for param_key, config in self.config.items():
            ranges[param_key] = {
                'param_name': config['param_name'],
                'min': config['min_output'],
                'max': config['max_output']
            }
        return ranges


def demo():
    """演示函数：参数映射"""
    print("🎯 参数映射演示")
    
    # 创建映射器
    mapper = ParameterMapper()
    
    # 测试姿态映射
    test_pose = {
        'success': True,
        'euler_angles': np.array([0.1, 0.2, 0.05])  # 弧度
    }
    
    pose_params = mapper.map_pose_to_parameters(test_pose)
    print("\n姿态参数映射结果:")
    for key, value in pose_params.items():
        print(f"  {key}: {value:.2f}")
    
    # 测试眼睛特征映射
    test_eye_features = {
        'avg_open': 0.8,
        'left_center': np.array([0.45, 0.45]),
        'right_center': np.array([0.55, 0.45])
    }
    
    eye_params = mapper.map_eye_features_to_parameters(test_eye_features)
    print("\n眼睛参数映射结果:")
    for key, value in eye_params.items():
        print(f"  {key}: {value:.2f}")
    
    # 测试嘴巴特征映射
    test_mouth_features = {
        'open': 0.5,
        'smile': 0.8
    }
    
    mouth_params = mapper.map_mouth_features_to_parameters(test_mouth_features)
    print("\n嘴巴参数映射结果:")
    for key, value in mouth_params.items():
        print(f"  {key}: {value:.2f}")
    
    print("\n✅ 参数映射演示完成")


if __name__ == "__main__":
    demo()