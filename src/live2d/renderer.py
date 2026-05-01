"""
Live2D渲染器模块
负责模拟模式下的模型渲染和动画控制
注意：此渲染器仅用于 live2d-py 库不可用时的备用方案
"""

from typing import TYPE_CHECKING
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import QRect, Qt

if TYPE_CHECKING:
    from src.live2d.model import Live2DModelInterface


class Live2DRenderer:
    """
    Live2D渲染器类（备用模拟版本）
    当 live2d-py 库不可用时，使用简单的椭圆模拟渲染
    """

    def __init__(self, model: "Live2DModelInterface"):
        """
        初始化渲染器
        
        Args:
            model: Live2D 模型接口
        """
        self.model = model  # 模型实例
        self.canvas_width = 400  # 画布宽度
        self.canvas_height = 500  # 画布高度
        self._frame_count = 0  # 帧计数器

    def render(self, painter: QPainter) -> None:
        """
        渲染模型（模拟版本）
        使用简单的椭圆组合模拟 Live2D 模型效果
        
        Args:
            painter: QPainter 绘图对象
        """
        self._frame_count += 1
        params = self.model.parameters

        # 开启抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)

        # ========== 计算动画参数 ==========
        breath_offset = params.get("ParamBreath", 0.5) * 5  # 呼吸偏移
        base_y = self.canvas_height // 2  # 基准Y坐标

        # ========== 绘制身体 ==========
        painter.setBrush(QColor(255, 200, 200))  # 填充色（浅粉色）
        painter.setPen(QColor(200, 150, 150))  # 描边色
        body_rect = QRect(
            self.canvas_width // 2 - 80,  # 左上角X
            base_y - 50 + int(breath_offset),  # 左上角Y（随呼吸变化）
            160,  # 宽度
            120  # 高度
        )
        painter.drawEllipse(body_rect)  # 画椭圆（身体）

        # ========== 绘制头部 ==========
        head_y = base_y - 120 + int(breath_offset)  # 头部Y坐标（随呼吸变化）
        head_x = self.canvas_width // 2 + int(params.get("ParamAngleX", 0) * 2)  # 头部X坐标（随旋转变化）
        painter.setBrush(QColor(255, 220, 220))  # 填充色
        painter.setPen(QColor(220, 180, 180))  # 描边色
        painter.drawEllipse(QRect(head_x - 60, head_y - 60, 120, 120))  # 画椭圆（头部）

        # ========== 绘制头发 ==========
        painter.setBrush(QColor(180, 140, 200))  # 头发颜色（紫色）
        painter.setPen(Qt.NoPen)  # 不描边
        for i in range(3):
            offset_x = (i - 1) * 25  # 3个头发椭圆的X偏移
            painter.drawEllipse(QRect(
                head_x + offset_x - 15,
                head_y - 85 + i * 5,
                30,
                40
            ))

        # ========== 绘制眼睛 ==========
        eye_offset_x = int(params.get("ParamEyeBallX", 0) * 10)  # 眼球X偏移
        eye_offset_y = int(params.get("ParamEyeBallY", 0) * 8)  # 眼球Y偏移
        painter.setBrush(QColor(50, 50, 50))  # 眼睛颜色（深色）
        # 左眼
        painter.drawEllipse(QRect(
            head_x - 30 + eye_offset_x,
            head_y - 10 + eye_offset_y,
            20,
            25
        ))
        # 右眼
        painter.drawEllipse(QRect(
            head_x + 10 + eye_offset_x,
            head_y - 10 + eye_offset_y,
            20,
            25
        ))

        # ========== 绘制嘴巴 ==========
        mouth_open = int(params.get("ParamMouthOpenY", 0) * 10)  # 嘴巴开合程度
        painter.setBrush(QColor(200, 80, 80))  # 嘴巴颜色（红色）
        painter.drawEllipse(QRect(
            head_x - 15,
            head_y + 30,
            30,
            15 + mouth_open
        ))

        # ========== 绘制腮红 ==========
        painter.setBrush(QColor(255, 150, 150, 100))  # 腮红颜色（半透明粉色）
        painter.drawEllipse(QRect(head_x - 50, head_y + 5, 25, 15))  # 左腮红
        painter.drawEllipse(QRect(head_x + 25, head_y + 5, 25, 15))  # 右腮红

        # ========== 绘制调试信息 ==========
        painter.setFont(QFont("微软雅黑", 10))
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(10, 30, f"帧: {self._frame_count}")

    def update_render_size(self, width: int, height: int) -> None:
        """
        更新渲染尺寸
        
        Args:
            width: 新宽度
            height: 新高度
        """
        self.canvas_width = width
        self.canvas_height = height

    def get_frame_count(self) -> int:
        """
        获取当前渲染帧数
        
        Returns:
            帧计数
        """
        return self._frame_count
