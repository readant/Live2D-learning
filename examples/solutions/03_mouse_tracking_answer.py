"""
示例 03: 鼠标追踪实现 - 答案版本

这个示例展示如何实现鼠标追踪功能，让 Live2D 模型跟随鼠标移动。

学习要点：
- 鼠标位置追踪
- 视线角度计算
- 模型参数控制
- 坐标转换

运行方式：
    python solutions/03_mouse_tracking_answer.py
"""

import sys
import math
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
import live2d.v3 as live2d

from config import settings


class MouseTracker:
    """
    鼠标追踪器

    负责追踪鼠标位置，计算模型应该注视的角度。

    设计模式：
    这是一个独立于 UI 的类，体现了模块化设计思想。
    它不依赖 PyQt5，可以很容易地移植到其他框架。

    算法原理：
    1. 记录鼠标在屏幕上的位置
    2. 计算鼠标相对于模型中心的偏移
    3. 根据偏移量计算头部和眼球应该转动的角度
    4. 应用平滑处理，避免突然的角度变化
    """

    def __init__(self, target_center=(200, 250)):
        """
        初始化鼠标追踪器

        Args:
            target_center: 模型中心点的坐标 (x, y)
                         这个点作为"视线目标"的参考点

        设计考量：
        - 使用元组而不是 QPoint，保持类的独立性
        - 默认值 (200, 250) 适合 400x500 的窗口
        """
        self.target_center = target_center
        self.mouse_pos = QPoint(0, 0)

        self.max_gaze_angle = 30
        self.gaze_smoothing = 0.15

        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0

    def update_mouse_position(self, x: int, y: int) -> None:
        """
        更新鼠标位置并计算相对角度

        这是核心方法，实现视线追踪的算法。

        算法步骤：
        1. 记录当前位置
        2. 计算与中心点的偏移量 (dx, dy)
        3. 计算距离
        4. 如果距离大于 0（不在中心点）：
           - 归一化距离，防止角度过大
           - 计算单位向量（方向）
           - 结合方向和距离得到相对角度
        5. 如果在中心点，角度归零

        Args:
            x: 鼠标 X 坐标
            y: 鼠标 Y 坐标
        """
        self.mouse_pos = QPoint(x, y)

        dx = x - self.target_center[0]
        dy = y - self.target_center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            max_distance = 400
            normalized_distance = min(distance / max_distance, 1.0)

            self.relative_angle_x = (dx / distance) * normalized_distance
            self.relative_angle_y = (dy / distance) * normalized_distance
        else:
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_gaze_angles(self):
        """
        获取注视角度

        将归一化的相对角度转换为实际的模型参数值。

        Live2D 参数说明：
        - ParamAngleX/Y: 头部旋转角度，范围通常是 -30 ~ 30
        - ParamEyeBallX/Y: 眼球位置，范围通常是 -1 ~ 1

        Returns:
            tuple: (头部X角度, 头部Y角度, 眼球X角度, 眼球Y角度)
        """
        angle_x = self.relative_angle_x * self.max_gaze_angle
        angle_y = self.relative_angle_y * self.max_gaze_angle

        eye_x = self.relative_angle_x * 1.0
        eye_y = self.relative_angle_y * 1.0

        return angle_x, angle_y, eye_x, eye_y


class MouseTrackingWidget(QOpenGLWidget):
    """
    带有鼠标追踪功能的 Live2D 窗口

    这个类组合了 MouseTracker 和 Live2D 模型，
    负责 UI 交互和渲染协调。
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.mouse_tracker = MouseTracker(
            (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2)
        )
        self._init_ui()

    def _init_ui(self):
        """初始化窗口属性"""
        self.setWindowTitle("示例 03: 鼠标追踪")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        """
        初始化 OpenGL 和 Live2D

        步骤：
        1. makeCurrent() - 获取 OpenGL 上下文
        2. live2d.init() - 初始化 Live2D SDK
        3. live2d.glInit() - 初始化 OpenGL 功能
        4. 创建并加载模型
        5. 启动定时器
        """
        self.makeCurrent()
        live2d.init()
        live2d.glInit()

        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)

        self.startTimer(33)

    def paintGL(self):
        """
        渲染回调

        渲染流程：
        1. 清空缓冲区
        2. 更新模型状态
        3. 应用注视角度参数
        4. 绘制模型

        关键点：
        - 每帧都要调用 SetParameterValue 更新参数
        - 参数会在下一帧生效
        """
        live2d.clearBuffer()

        if self.live2d_model:
            self.live2d_model.Update()

            angles = self.mouse_tracker.get_gaze_angles()
            self.live2d_model.SetParameterValue("ParamAngleX", angles[0])
            self.live2d_model.SetParameterValue("ParamAngleY", angles[1])
            self.live2d_model.SetParameterValue("ParamEyeBallX", angles[2])
            self.live2d_model.SetParameterValue("ParamEyeBallY", angles[3])

            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        """窗口大小改变时调整模型"""
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件

        关键点：
        - event.pos() 获取鼠标在窗口内的相对位置
        - 传递给 MouseTracker 进行处理
        - 调用 super() 确保正常的事件传播

        注意：
        - 需要启用鼠标追踪属性：setMouseTracking(True)
        - 否则只有按下鼠标时才会触发
        """
        self.mouse_tracker.update_mouse_position(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)

    def timerEvent(self, event):
        """定时器事件，触发重绘"""
        self.update()

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    """
    主函数

    关键点：
    - AA_ShareOpenGLContexts 对于 Live2D 渲染是必需的
    - setQuitOnLastWindowClosed(False) 确保桌宠可以持续运行
    """
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = MouseTrackingWidget()
    widget.show()

    print("=" * 50)
    print("鼠标追踪示例")
    print("移动鼠标，Live2D 模型会跟随注视")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
