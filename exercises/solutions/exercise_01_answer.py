"""
练习 01: 添加新的表情 - 答案

练习目标：
学习如何为 Live2D 模型添加自定义表情。

答案说明：
1. 在 Expression 枚举中添加 SURPRISED
2. 在 EXPRESSION_CONFIGS 中添加参数配置
3. 在右键菜单中添加选项和处理逻辑
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
    SURPRISED = "surprised"  # 添加惊讶表情


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
    Expression.SURPRISED: {  # 惊讶表情配置
        "ParamEyeLOpen": 1.0,     # 睁大眼睛
        "ParamEyeROpen": 1.0,
        "ParamEyeLSmile": 0.0,    # 不笑
        "ParamEyeRSmile": 0.0,
        "ParamMouthForm": 0.0,    # 嘴巴呈 O 型
        "ParamMouthOpenY": 0.8,   # 张大嘴
        "ParamBrowLForm": 0.8,    # 眉毛上扬
        "ParamBrowRForm": 0.8,
        "ParamCheek": 0.0,        # 不脸红
    },
}


class ExpressionWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.live2d_model = None
        self.current_expression = Expression.HAPPY
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("练习 01: 添加新表情 [答案]")
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
        action_happy = expression_menu.addAction("开心 😊")
        action_serious = expression_menu.addAction("认真 🤔")
        action_sleepy = expression_menu.addAction("犯困 😪")
        action_surprised = expression_menu.addAction("惊讶 😲")  # 新增

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == action_happy:
            self.current_expression = Expression.HAPPY
        elif action == action_serious:
            self.current_expression = Expression.SERIOUS
        elif action == action_sleepy:
            self.current_expression = Expression.SLEEPY
        elif action == action_surprised:  # 新增处理
            self.current_expression = Expression.SURPRISED

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
    print("练习 01: 添加新表情 [答案]")
    print("新增：惊讶表情 (SURPRISED)")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
