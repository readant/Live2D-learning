"""
示例 05: 表情切换系统

这个示例展示如何实现表情切换功能，让 Live2D 模型展现不同的表情。

学习要点：
- 表情参数配置
- 表情切换逻辑
- 参数权重和过渡
- 枚举类型的使用

运行方式：
    python 05_expression.py
"""

import sys
from enum import Enum
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMenu
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


class Expression(Enum):
    """表情枚举"""
    HAPPY = "happy"
    SERIOUS = "serious"
    SLEEPY = "sleepy"


EXPRESSION_CONFIGS = {
    Expression.HAPPY: {
        "ParamEyeLSmile": 0.8,
        "ParamEyeRSmile": 0.8,
        "ParamMouthForm": 0.5,
        "ParamMouthOpenY": 0.3,
        "ParamCheek": 0.6,
    },
    Expression.SERIOUS: {
        "ParamEyeLSmile": -0.4,
        "ParamEyeRSmile": -0.4,
        "ParamBrowLForm": 0.7,
        "ParamBrowRForm": 0.7,
        "ParamMouthForm": -0.4,
        "ParamMouthOpenY": 0.0,
        "ParamCheek": 0.0,
    },
    Expression.SLEEPY: {
        "ParamEyeLOpen": 0.2,
        "ParamEyeROpen": 0.2,
        "ParamMouthOpenY": 0.5,
        "ParamCheek": 0.1,
    },
}


class ExpressionWidget(QOpenGLWidget):
    """
    带表情切换功能的 Live2D 窗口
    """

    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.current_expression = Expression.HAPPY
        self._init_ui()

    def _init_ui(self):
        """初始化窗口"""
        self.setWindowTitle("示例 05: 表情切换")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

    def initializeGL(self):
        """初始化"""
        self.makeCurrent()
        live2d.init()
        live2d.glInit()

        self.live2d_model = live2d.LAppModel()
        self.live2d_model.LoadModelJson(settings.MODEL_PATH)

        self.startTimer(33)

    def paintGL(self):
        """渲染"""
        live2d.clearBuffer()

        if self.live2d_model:
            self._apply_expression(self.current_expression)
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def _apply_expression(self, expression: Expression):
        """应用表情参数"""
        config = EXPRESSION_CONFIGS.get(expression, {})
        for param_name, value in config.items():
            self.live2d_model.SetParameterValue(param_name, value)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)

        expression_menu = menu.addMenu("切换表情")
        action_happy = expression_menu.addAction("开心")
        action_serious = expression_menu.addAction("认真")
        action_sleepy = expression_menu.addAction("犯困")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_happy:
            self.current_expression = Expression.HAPPY
        elif action == action_serious:
            self.current_expression = Expression.SERIOUS
        elif action == action_sleepy:
            self.current_expression = Expression.SLEEPY

    def mousePressEvent(self, event):
        """点击切换表情"""
        if event.button() == Qt.LeftButton:
            expressions = list(Expression)
            current_index = expressions.index(self.current_expression)
            next_index = (current_index + 1) % len(expressions)
            self.current_expression = expressions[next_index]
            print(f"切换到: {self.current_expression.name}")
        super().mousePressEvent(event)

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

    widget = ExpressionWidget()
    widget.show()

    print("=" * 50)
    print("表情切换示例")
    print("- 左键点击：循环切换表情")
    print("- 右键菜单：选择特定表情")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
