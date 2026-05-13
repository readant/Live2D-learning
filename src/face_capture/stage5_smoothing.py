"""
阶段 5：平滑滤波与抖动抑制

功能：对捕捉数据进行平滑处理，减少抖动

学习目标：
- 理解平滑滤波原理
- 掌握多种滤波算法
- 学习如何平衡响应速度和平滑效果

常用滤波算法：
1. 移动平均滤波 (Moving Average)
2. 指数加权移动平均 (EWMA)
3. 卡尔曼滤波 (Kalman Filter)
4. 贝塞尔曲线平滑

关键参数：
- 滤波窗口大小（影响平滑程度和延迟）
- 平滑系数（影响响应速度）
- 阈值处理（处理异常值）
"""

import numpy as np
from collections import deque


class Smoother:
    """数据平滑器"""
    
    def __init__(self, method='ewma', window_size=10, alpha=0.3):
        """
        初始化平滑器
        :param method: 滤波方法 ('moving_average', 'ewma', 'kalman')
        :param window_size: 移动平均窗口大小
        :param alpha: EWMA 平滑系数 (0-1)，越小越平滑
        """
        self.method = method
        self.window_size = window_size
        self.alpha = alpha
        
        # 存储历史数据
        self.history = {}
        
        # 卡尔曼滤波状态（每个参数独立）
        self.kalman_states = {}
    
    def smooth(self, parameters):
        """
        对参数进行平滑处理
        :param parameters: 参数字典
        :return: 平滑后的参数字典
        """
        if parameters is None or len(parameters) == 0:
            return parameters
        
        smoothed = {}
        
        for param_name, value in parameters.items():
            # 初始化历史记录
            if param_name not in self.history:
                self._init_param_history(param_name, value)
            
            # 根据方法进行平滑
            if self.method == 'moving_average':
                smoothed[param_name] = self._moving_average(param_name, value)
            elif self.method == 'ewma':
                smoothed[param_name] = self._ewma(param_name, value)
            elif self.method == 'kalman':
                smoothed[param_name] = self._kalman_filter(param_name, value)
            else:
                smoothed[param_name] = value
        
        return smoothed
    
    def _init_param_history(self, param_name, initial_value):
        """
        初始化参数历史记录
        :param param_name: 参数名
        :param initial_value: 初始值
        """
        if self.method == 'moving_average':
            self.history[param_name] = deque([initial_value], maxlen=self.window_size)
        elif self.method == 'ewma':
            self.history[param_name] = initial_value
        elif self.method == 'kalman':
            # 卡尔曼滤波状态：[估计值, 估计误差, 过程噪声, 测量噪声]
            self.kalman_states[param_name] = {
                'x': initial_value,      # 状态估计
                'p': 1.0,              # 估计误差协方差
                'q': 0.01,             # 过程噪声协方差
                'r': 0.1               # 测量噪声协方差
            }
            self.history[param_name] = initial_value
    
    def _moving_average(self, param_name, value):
        """
        移动平均滤波
        :param param_name: 参数名
        :param value: 当前值
        :return: 平滑后的值
        """
        history = self.history[param_name]
        history.append(value)
        
        # 计算平均值
        return sum(history) / len(history)
    
    def _ewma(self, param_name, value):
        """
        指数加权移动平均滤波
        :param param_name: 参数名
        :param value: 当前值
        :return: 平滑后的值
        """
        prev_value = self.history[param_name]
        
        # EWMA 公式: S_t = alpha * X_t + (1 - alpha) * S_{t-1}
        smoothed_value = self.alpha * value + (1 - self.alpha) * prev_value
        
        # 更新历史
        self.history[param_name] = smoothed_value
        
        return smoothed_value
    
    def _kalman_filter(self, param_name, value):
        """
        简化卡尔曼滤波
        :param param_name: 参数名
        :param value: 当前值（测量值）
        :return: 滤波后的值
        """
        state = self.kalman_states[param_name]
        
        # 预测步骤
        # x_pred = x_prev
        # p_pred = p_prev + q
        x_pred = state['x']
        p_pred = state['p'] + state['q']
        
        # 更新步骤
        # k = p_pred / (p_pred + r)
        # x = x_pred + k * (z - x_pred)
        # p = (1 - k) * p_pred
        k = p_pred / (p_pred + state['r'])
        x = x_pred + k * (value - x_pred)
        p = (1 - k) * p_pred
        
        # 更新状态
        state['x'] = x
        state['p'] = p
        
        # 更新历史
        self.history[param_name] = x
        
        return x
    
    def reset(self):
        """重置所有历史数据"""
        self.history = {}
        self.kalman_states = {}
    
    def reset_param(self, param_name):
        """重置指定参数的历史数据"""
        if param_name in self.history:
            del self.history[param_name]
        if param_name in self.kalman_states:
            del self.kalman_states[param_name]


class MultiStageSmoother:
    """多级平滑器（组合多种滤波方法）"""
    
    def __init__(self):
        """初始化多级平滑器"""
        # 第一级：异常值检测和裁剪
        self.outlier_threshold = 0.3  # 异常值阈值（与上次差值的最大比例）
        
        # 第二级：EWMA 滤波
        self.ewma_smoother = Smoother(method='ewma', alpha=0.2)
        
        # 第三级：卡尔曼滤波
        self.kalman_smoother = Smoother(method='kalman')
        
        # 存储上一帧的值用于异常检测
        self.prev_values = {}
    
    def smooth(self, parameters):
        """
        多级平滑处理
        :param parameters: 参数字典
        :return: 平滑后的参数字典
        """
        if parameters is None or len(parameters) == 0:
            return parameters
        
        # 第一级：异常值处理
        parameters = self._outlier_filter(parameters)
        
        # 第二级：EWMA 滤波
        parameters = self.ewma_smoother.smooth(parameters)
        
        # 第三级：卡尔曼滤波
        parameters = self.kalman_smoother.smooth(parameters)
        
        # 更新上一帧值
        self.prev_values.update(parameters)
        
        return parameters
    
    def _outlier_filter(self, parameters):
        """
        异常值检测和处理
        :param parameters: 参数字典
        :return: 处理后的参数字典
        """
        filtered = {}
        
        for param_name, value in parameters.items():
            if param_name in self.prev_values:
                prev_value = self.prev_values[param_name]
                
                # 计算变化量
                diff = abs(value - prev_value)
                
                # 获取参数的合理范围（用于计算比例）
                param_range = self._get_param_range(param_name)
                max_diff = param_range * self.outlier_threshold
                
                # 如果变化过大，限制变化量
                if diff > max_diff:
                    direction = 1 if value > prev_value else -1
                    filtered[param_name] = prev_value + direction * max_diff
                else:
                    filtered[param_name] = value
            else:
                filtered[param_name] = value
        
        return filtered
    
    def _get_param_range(self, param_name):
        """
        获取参数的合理范围
        :param param_name: 参数名
        :return: 参数范围
        """
        # 根据 Live2D 参数名返回典型范围
        ranges = {
            'ParamAngleX': 60,      # -30 ~ 30
            'ParamAngleY': 40,      # -20 ~ 20
            'ParamAngleZ': 30,      # -15 ~ 15
            'ParamBodyAngleX': 20,   # -10 ~ 10
            'ParamEyeBallX': 2,     # -1 ~ 1
            'ParamEyeBallY': 2,     # -1 ~ 1
            'ParamMouthOpenY': 1,   # 0 ~ 1
            'ParamMouthForm': 2,    # -1 ~ 1
            'ParamEyeblowL': 2,     # -1 ~ 1
            'ParamEyeblowR': 2,     # -1 ~ 1
        }
        
        return ranges.get(param_name, 1.0)
    
    def reset(self):
        """重置所有状态"""
        self.ewma_smoother.reset()
        self.kalman_smoother.reset()
        self.prev_values = {}


class VelocityLimiter:
    """速度限制器（防止参数变化过快）"""
    
    def __init__(self, max_velocity=10.0, delta_time=1/60):
        """
        初始化速度限制器
        :param max_velocity: 最大变化速度（每秒）
        :param delta_time: 时间间隔（秒）
        """
        self.max_velocity = max_velocity
        self.delta_time = delta_time
        self.prev_values = {}
    
    def limit(self, parameters):
        """
        限制参数变化速度
        :param parameters: 参数字典
        :return: 限速后的参数字典
        """
        if parameters is None or len(parameters) == 0:
            return parameters
        
        limited = {}
        max_change = self.max_velocity * self.delta_time
        
        for param_name, value in parameters.items():
            if param_name in self.prev_values:
                prev_value = self.prev_values[param_name]
                diff = value - prev_value
                
                # 限制变化量
                if abs(diff) > max_change:
                    direction = diff / abs(diff)
                    limited[param_name] = prev_value + direction * max_change
                else:
                    limited[param_name] = value
            else:
                limited[param_name] = value
            
            self.prev_values[param_name] = limited[param_name]
        
        return limited
    
    def reset(self):
        """重置状态"""
        self.prev_values = {}


def demo():
    """演示函数：平滑滤波效果"""
    print("🎯 平滑滤波演示")
    
    # 模拟带噪声的输入数据
    np.random.seed(42)
    time_steps = 50
    true_values = np.linspace(-30, 30, time_steps)
    noisy_values = true_values + np.random.normal(0, 5, time_steps)
    
    # 创建不同的平滑器
    smoothers = {
        'Original': None,
        'Moving Average (5)': Smoother(method='moving_average', window_size=5),
        'Moving Average (10)': Smoother(method='moving_average', window_size=10),
        'EWMA (0.2)': Smoother(method='ewma', alpha=0.2),
        'EWMA (0.5)': Smoother(method='ewma', alpha=0.5),
        'Kalman': Smoother(method='kalman'),
        'Multi-stage': MultiStageSmoother()
    }
    
    # 应用滤波
    results = {}
    for name, smoother in smoothers.items():
        results[name] = []
        for value in noisy_values:
            if smoother:
                result = smoother.smooth({'test': value})['test']
            else:
                result = value
            results[name].append(result)
    
    print("\n滤波结果对比（前10个值）:")
    print(f"{'Method':<20} {'Input':>8} {'Output':>8}")
    print("-" * 40)
    
    for i in range(10):
        for name, values in results.items():
            if i == 0:
                print(f"{name:<20} {noisy_values[i]:>8.2f} {values[i]:>8.2f}")
            else:
                print(f"{'':<20} {noisy_values[i]:>8.2f} {values[i]:>8.2f}")
        print()
    
    print("✅ 平滑滤波演示完成")
    
    # 绘制图表（需要 matplotlib）
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        plt.plot(true_values, label='True Value', linestyle='--', color='gray')
        plt.plot(noisy_values, label='Noisy Input', alpha=0.5, color='red')
        
        for name, values in results.items():
            if name != 'Original' and name != 'Moving Average (5)':
                plt.plot(values, label=name)
        
        plt.legend()
        plt.title('Smoothing Filter Comparison')
        plt.xlabel('Time Step')
        plt.ylabel('Value')
        plt.grid(True)
        plt.savefig('smoothing_demo.png')
        print("\n📊 图表已保存为 smoothing_demo.png")
        
    except ImportError:
        print("\n⚠️ 未安装 matplotlib，跳过图表绘制")


if __name__ == "__main__":
    demo()