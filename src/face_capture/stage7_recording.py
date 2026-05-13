"""
阶段 7：动作录制与导出

功能：录制面部捕捉数据并导出为 Live2D motion3.json 格式

学习目标：
- 理解 motion3.json 文件格式
- 掌握动作录制方法
- 学习如何导出自定义动作

motion3.json 格式说明：
- Version: 版本号
- Meta: 元信息（作者、创建时间等）
- Duration: 动作持续时间（毫秒）
- Fps: 帧率
- Curves: 曲线数据（参数动画）
- UserData: 用户数据（标记点）
"""

import json
import time
import numpy as np
from datetime import datetime


class MotionRecorder:
    """动作录制器"""
    
    def __init__(self, fps=30):
        """
        初始化动作录制器
        :param fps: 录制帧率
        """
        self.fps = fps
        self.frame_interval = 1.0 / fps
        
        # 录制状态
        self.is_recording = False
        self.start_time = 0.0
        self.last_frame_time = 0.0
        
        # 录制数据
        self.frames = []
        self.meta = {
            'author': 'FaceCapture System',
            'version': '1.0',
            'created': '',
            'comment': 'Recorded from face capture'
        }
    
    def start_recording(self):
        """开始录制"""
        self.is_recording = True
        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.frames = []
        self.meta['created'] = datetime.now().isoformat()
        
        print("🎬 开始录制...")
    
    def stop_recording(self):
        """停止录制"""
        self.is_recording = False
        print(f"✅ 录制结束，共录制 {len(self.frames)} 帧")
    
    def record_frame(self, parameters, timestamp=None):
        """
        录制一帧数据
        :param parameters: 当前帧的参数字典
        :param timestamp: 可选的时间戳（秒）
        """
        if not self.is_recording:
            return
        
        if timestamp is None:
            timestamp = time.time() - self.start_time
        
        # 检查是否需要录制当前帧（基于帧率）
        if timestamp - self.last_frame_time >= self.frame_interval:
            frame_data = {
                'time': timestamp,
                'parameters': parameters.copy()
            }
            self.frames.append(frame_data)
            self.last_frame_time = timestamp
    
    def get_frame_count(self):
        """获取录制帧数"""
        return len(self.frames)
    
    def get_duration(self):
        """获取录制时长（秒）"""
        if len(self.frames) == 0:
            return 0.0
        return self.frames[-1]['time']
    
    def export_to_motion3(self, filepath):
        """
        导出为 motion3.json 格式
        :param filepath: 输出文件路径
        """
        if len(self.frames) == 0:
            print("⚠️ 没有录制数据")
            return False
        
        # 构建 motion3.json 结构
        motion_data = self._build_motion3_data()
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(motion_data, f, indent=2, ensure_ascii=False)
        
        print(f"📤 动作数据已导出到 {filepath}")
        return True
    
    def _build_motion3_data(self):
        """构建 motion3.json 数据结构"""
        # 获取所有参数名
        all_params = set()
        for frame in self.frames:
            all_params.update(frame['parameters'].keys())
        
        # 为每个参数创建曲线
        curves = []
        for param_name in sorted(all_params):
            curve = self._create_curve(param_name)
            if curve:
                curves.append(curve)
        
        # 计算持续时间（毫秒）
        duration_ms = int(self.get_duration() * 1000)
        
        motion_data = {
            'Version': '3.0',
            'Meta': self.meta,
            'Duration': duration_ms,
            'Fps': self.fps,
            'Curves': curves,
            'UserData': []
        }
        
        return motion_data
    
    def _create_curve(self, param_name):
        """
        为单个参数创建曲线数据
        :param param_name: 参数名
        :return: 曲线数据字典
        """
        # 收集该参数的所有关键帧
        keyframes = []
        
        for frame in self.frames:
            if param_name in frame['parameters']:
                time_ms = int(frame['time'] * 1000)
                value = frame['parameters'][param_name]
                
                # 简化处理：使用线性插值
                keyframes.append({
                    'Time': time_ms,
                    'Value': value,
                    'Easing': 'Linear'
                })
        
        if len(keyframes) == 0:
            return None
        
        return {
            'Target': param_name,
            'Id': 0,  # 参数ID，通常由 Live2D Editor 分配
            'KeyFrames': keyframes
        }
    
    def export_to_csv(self, filepath):
        """
        导出为 CSV 格式（便于调试和分析）
        :param filepath: 输出文件路径
        """
        if len(self.frames) == 0:
            print("⚠️ 没有录制数据")
            return False
        
        # 获取所有参数名
        all_params = set()
        for frame in self.frames:
            all_params.update(frame['parameters'].keys())
        
        params_list = sorted(all_params)
        
        # 写入 CSV
        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入表头
            header = ['Time'] + params_list
            f.write(','.join(header) + '\n')
            
            # 写入数据
            for frame in self.frames:
                row = [str(frame['time'])]
                for param in params_list:
                    row.append(str(frame['parameters'].get(param, '')))
                f.write(','.join(row) + '\n')
        
        print(f"📤 CSV 数据已导出到 {filepath}")
        return True
    
    def clear(self):
        """清除录制数据"""
        self.frames = []
        self.start_time = 0.0
        self.last_frame_time = 0.0
    
    def get_statistics(self):
        """获取录制统计信息"""
        return {
            'frame_count': len(self.frames),
            'duration': self.get_duration(),
            'fps': self.fps,
            'parameter_count': len(self._get_all_parameters()),
            'parameters': self._get_all_parameters()
        }
    
    def _get_all_parameters(self):
        """获取所有录制的参数名"""
        params = set()
        for frame in self.frames:
            params.update(frame['parameters'].keys())
        return sorted(list(params))


class MotionPlayer:
    """动作播放器"""
    
    def __init__(self):
        """初始化动作播放器"""
        self.motion_data = None
        self.current_time = 0.0
        self.is_playing = False
        self.start_time = 0.0
        
        # 缓存的参数曲线
        self.curves = {}
    
    def load_motion(self, filepath):
        """
        加载 motion3.json 文件
        :param filepath: 文件路径
        :return: 是否加载成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.motion_data = json.load(f)
            
            # 解析曲线数据
            self._parse_curves()
            print(f"📥 已加载动作文件: {filepath}")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def _parse_curves(self):
        """解析曲线数据"""
        if self.motion_data is None:
            return
        
        self.curves = {}
        for curve in self.motion_data.get('Curves', []):
            target = curve['Target']
            keyframes = curve['KeyFrames']
            
            # 将关键帧按时间排序
            keyframes.sort(key=lambda kf: kf['Time'])
            self.curves[target] = keyframes
    
    def play(self):
        """开始播放"""
        if self.motion_data is None:
            print("⚠️ 没有加载动作数据")
            return
        
        self.is_playing = True
        self.current_time = 0.0
        self.start_time = time.time()
        print("▶️ 开始播放")
    
    def pause(self):
        """暂停播放"""
        self.is_playing = False
        print("⏸️ 播放暂停")
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.current_time = 0.0
        print("⏹️ 播放停止")
    
    def update(self):
        """
        更新播放状态，获取当前帧参数
        :return: 当前帧的参数字典
        """
        if not self.is_playing or self.motion_data is None:
            return {}
        
        # 计算当前时间（毫秒）
        self.current_time = (time.time() - self.start_time) * 1000
        
        # 检查是否播放完毕
        duration = self.motion_data.get('Duration', 0)
        if self.current_time >= duration:
            self.stop()
            return {}
        
        # 插值计算每个参数的值
        parameters = {}
        for param_name, keyframes in self.curves.items():
            parameters[param_name] = self._interpolate(keyframes, self.current_time)
        
        return parameters
    
    def _interpolate(self, keyframes, time_ms):
        """
        在关键帧之间插值
        :param keyframes: 关键帧列表
        :param time_ms: 当前时间（毫秒）
        :return: 插值后的值
        """
        if len(keyframes) == 0:
            return 0.0
        
        if len(keyframes) == 1:
            return keyframes[0]['Value']
        
        # 找到当前时间所在的关键帧区间
        for i in range(len(keyframes) - 1):
            t0 = keyframes[i]['Time']
            t1 = keyframes[i+1]['Time']
            
            if t0 <= time_ms <= t1:
                # 线性插值
                v0 = keyframes[i]['Value']
                v1 = keyframes[i+1]['Value']
                
                alpha = (time_ms - t0) / (t1 - t0)
                return v0 + alpha * (v1 - v0)
        
        # 如果时间超出范围，返回最后一个值
        return keyframes[-1]['Value']
    
    def get_progress(self):
        """获取播放进度（0-1）"""
        if self.motion_data is None:
            return 0.0
        
        duration = self.motion_data.get('Duration', 1)
        return min(self.current_time / duration, 1.0)
    
    def get_duration(self):
        """获取动作时长（毫秒）"""
        if self.motion_data is None:
            return 0
        return self.motion_data.get('Duration', 0)


def demo():
    """演示函数：动作录制与播放"""
    print("🎯 动作录制与导出演示")
    
    # 创建录制器
    recorder = MotionRecorder(fps=30)
    
    # 模拟录制数据
    print("\n📝 模拟录制数据...")
    recorder.start_recording()
    
    # 模拟 2 秒的面部捕捉数据
    duration = 2.0
    num_frames = int(duration * recorder.fps)
    
    for i in range(num_frames):
        t = i / recorder.fps
        
        # 模拟参数变化
        params = {
            'ParamAngleX': 10 * np.sin(2 * np.pi * t),
            'ParamAngleY': 5 * np.cos(2 * np.pi * t),
            'ParamAngleZ': 3 * np.sin(4 * np.pi * t),
            'ParamMouthOpenY': 0.3 + 0.2 * np.sin(3 * np.pi * t),
            'ParamMouthForm': 0.5 * np.cos(2 * np.pi * t)
        }
        
        recorder.record_frame(params, t)
    
    recorder.stop_recording()
    
    # 显示统计信息
    stats = recorder.get_statistics()
    print("\n📊 录制统计:")
    print(f"  帧数: {stats['frame_count']}")
    print(f"  时长: {stats['duration']:.2f} 秒")
    print(f"  帧率: {stats['fps']} FPS")
    print(f"  参数数量: {stats['parameter_count']}")
    print(f"  参数列表: {stats['parameters']}")
    
    # 导出为 motion3.json
    recorder.export_to_motion3('demo_motion.motion3.json')
    
    # 导出为 CSV
    recorder.export_to_csv('demo_motion.csv')
    
    # 测试加载和播放
    print("\n🔄 测试加载和播放...")
    player = MotionPlayer()
    if player.load_motion('demo_motion.motion3.json'):
        player.play()
        
        # 模拟播放几帧
        for _ in range(30):
            params = player.update()
            if params:
                print(f"\r播放进度: {player.get_progress():.1%} | Params: {len(params)}", end='')
                time.sleep(1/30)
        
        player.stop()
        print("\n✅ 演示完成")


if __name__ == "__main__":
    demo()