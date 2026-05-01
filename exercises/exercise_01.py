"""
练习 01: 添加新的表情

练习目标：
学习如何为 Live2D 模型添加自定义表情。

练习要求：
1. 添加一个新的表情 "惊讶" (SURPRISED)
2. 为这个表情定义合适的参数值
3. 在右键菜单中添加切换到这个表情的选项
4. 测试效果

提示：
- 参考 Expression.HAPPY 的参数配置
- SURPRISED 表情特点：睁大眼睛、张嘴、眉毛上扬
- 相关参数：
  * ParamEyeLOpen/ParamEyeROpen: 眼睛睁开程度 (0.0-1.0)
  * ParamMouthOpenY: 嘴巴张开程度 (0.0-1.0)
  * ParamBrowLForm/ParamBrowRForm: 眉毛形状

答案参考：solutions/exercise_01_answer.py
"""

import sys
from enum import Enum
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMenu
from PyQt5.QtCore import Qt, QTimer
import live2d.v3 as live2d

from config import settings


# ========== 在这里添加你的代码 ==========

class Expression(Enum):
    """表情枚举"""
    HAPPY = "happy"
    SERIOUS = "serious"
    SLEEPY = "sleepy"
    # TODO: 添加 SURPRISED 表情


EXPRESSION_CONFIGS = {
    # TODO: 添加 SURPRISED 表情的参数配置
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

# ========== 练习代码结束 ==========


class ExpressionWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.current_expression = Expression.HAPPY
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 01: 添加新表情")
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
            self._apply_expression(self.current_expression)
            self.live2d_model.Update()
            self.live2d_model.Draw()

    def resizeGL(self, w, h):
        if self.live2d_model:
            self.live2d_model.Resize(w, h)

    def _apply_expression(self, expression):
        config = EXPRESSION_CONFIGS.get(expression, {})
        for param_name, value in config.items():
            self.live2d_model.SetParameterValue(param_name, value)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        expression_menu = menu.addMenu("切换表情")
        action_happy = expression_menu.addAction("开心")
        action_serious = expression_menu.addAction("认真")
        action_sleepy = expression_menu.addAction("犯困")

        # TODO: 在这里添加"惊讶"选项

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_happy:
            self.current_expression = Expression.HAPPY
        elif action == action_serious:
            self.current_expression = Expression.SERIOUS
        elif action == action_sleepy:
            self.current_expression = Expression.SLEEPY
        # TODO: 添加 SURPRISED 的处理

    def mousePressEvent(self, event):
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
    print("练习 01: 添加新表情")
    print("目标：添加一个'惊讶'表情")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
