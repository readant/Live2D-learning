"""
练习 02: 修改鼠标跟随灵敏度

练习目标：
学习如何调整 Live2D 模型的鼠标跟随效果。

练习要求：
1. 修改 MouseTracker 类的参数，使头部跟随更灵敏
2. 调整最大注视角度（当前是 30 度）
3. 修改距离归一化的最大距离（当前是 400）
4. 尝试不同的数值，观察效果变化

调整建议：
- max_gaze_angle: 尝试 20、30、40、50
- max_distance: 尝试 200、300、400、500

思考问题：
- 角度太大会造成什么效果？
- 距离太近或太远会有什么影响？

答案参考：solutions/exercise_02_answer.py
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

    这个类负责追踪鼠标位置并计算注视角度。
    你需要修改这个类的参数来调整跟随效果。
    """

    def __init__(self, target_center=(200, 250)):
        self.target_center = target_center
        self.mouse_pos = QPoint(0, 0)

        # ========== 修改这些参数 ==========
        self.max_gaze_angle = 30      # 最大注视角度
        self.gaze_smoothing = 0.15    # 平滑系数（未使用）
        self.max_distance = 400       # 最大有效距离
        # ========== 参数结束 ==========

        self.relative_angle_x = 0.0
        self.relative_angle_y = 0.0

    def update_mouse_position(self, x: int, y: int) -> None:
        """更新鼠标位置并计算角度"""
        self.mouse_pos = QPoint(x, y)

        dx = x - self.target_center[0]
        dy = y - self.target_center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # 归一化距离
            normalized_distance = min(distance / self.max_distance, 1.0)

            # 计算相对角度
            self.relative_angle_x = (dx / distance) * normalized_distance
            self.relative_angle_y = (dy / distance) * normalized_distance
        else:
            self.relative_angle_x = 0.0
            self.relative_angle_y = 0.0

    def get_gaze_angles(self):
        """获取注视角度"""
        angle_x = self.relative_angle_x * self.max_gaze_angle
        angle_y = self.relative_angle_y * self.max_gaze_angle
        eye_x = self.relative_angle_x * 1.0
        eye_y = self.relative_angle_y * 1.0
        return angle_x, angle_y, eye_x, eye_y


class MouseTrackingWidget(QOpenGLWidget):
    """鼠标追踪窗口"""

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.mouse_tracker = MouseTracker(
            (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2)
        )
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 02: 修改鼠标跟随灵敏度")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        self.makeCurrent()
        live2d.init()
        live2d.glInit()
        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)
        self.startTimer(33)

    def paintGL(self):
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
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.update_mouse_position(event.pos().x(), event.pos().y())
        super().mouseMoveEvent(event)

    def timerEvent(self, event):
        self.update()

    def closeEvent(self, event):
        if self.live2d_model:
            self.live2d_model = None
        super().closeEvent(event)


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = MouseTrackingWidget()
    widget.show()

    print("=" * 50)
    print("练习 02: 修改鼠标跟随灵敏度")
    print("当前参数：")
    print("  - max_gaze_angle: 30")
    print("  - max_distance: 400")
    print("提示：修改 MouseTracker 类的参数，观察效果变化")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
