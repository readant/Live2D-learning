"""
Live2D渲染器模块
负责模型渲染和动画控制
"""

from typing import TYPE_CHECKING
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import QRect, Qt

if TYPE_CHECKING:
    from src.live2d.model import Live2DModelInterface


class Live2DRenderer:
    """
    Live2D渲染器类
    负责模型渲染和动画控制
    """

    def __init__(self, model: "Live2DModelInterface"):
        self.model = model
        self.canvas_width = 400
        self.canvas_height = 500
        self._frame_count = 0

    def render(self, painter: QPainter) -> None:
        self._frame_count += 1
        params = self.model.parameters

        painter.setRenderHint(QPainter.Antialiasing)

        breath_offset = params.get("ParamBreath", 0.5) * 5
        base_y = self.canvas_height // 2

        painter.setBrush(QColor(255, 200, 200))
        painter.setPen(QColor(200, 150, 150))
        body_rect = QRect(
            self.canvas_width // 2 - 80,
            base_y - 50 + int(breath_offset),
            160,
            120
        )
        painter.drawEllipse(body_rect)

        head_y = base_y - 120 + int(breath_offset)
        head_x = self.canvas_width // 2 + int(params.get("ParamAngleX", 0) * 2)
        painter.setBrush(QColor(255, 220, 220))
        painter.setPen(QColor(220, 180, 180))
        painter.drawEllipse(QRect(head_x - 60, head_y - 60, 120, 120))

        painter.setBrush(QColor(180, 140, 200))
        painter.setPen(Qt.NoPen)
        for i in range(3):
            offset_x = (i - 1) * 25
            painter.drawEllipse(QRect(head_x + offset_x - 15, head_y - 85 + i * 5, 30, 40))

        eye_offset_x = int(params.get("ParamEyeBallX", 0) * 10)
        eye_offset_y = int(params.get("ParamEyeBallY", 0) * 8)
        painter.setBrush(QColor(50, 50, 50))
        painter.drawEllipse(QRect(head_x - 30 + eye_offset_x, head_y - 10 + eye_offset_y, 20, 25))
        painter.drawEllipse(QRect(head_x + 10 + eye_offset_x, head_y - 10 + eye_offset_y, 20, 25))

        mouth_open = int(params.get("ParamMouthOpenY", 0) * 10)
        painter.setBrush(QColor(200, 80, 80))
        painter.drawEllipse(QRect(head_x - 15, head_y + 30, 30, 15 + mouth_open))

        painter.setBrush(QColor(255, 150, 150, 100))
        painter.drawEllipse(QRect(head_x - 50, head_y + 5, 25, 15))
        painter.drawEllipse(QRect(head_x + 25, head_y + 5, 25, 15))

        painter.setFont(QFont("微软雅黑", 10))
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(10, 30, f"帧: {self._frame_count}")

    def update_render_size(self, width: int, height: int) -> None:
        self.canvas_width = width
        self.canvas_height = height

    def get_frame_count(self) -> int:
        return self._frame_count
