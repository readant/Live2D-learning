"""
示例 01: 最简单的 PyQt5 窗口 - 答案版本

这个示例展示如何创建一个最基本的 PyQt5 窗口。
适合作为学习 PyQt5 的起点。

学习要点：
- QApplication 的创建和事件循环
- QWidget 的基本使用
- 窗口属性设置（标题、大小）
- 程序入口写法

运行方式：
    python solutions/01_basic_window_answer.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget


def main():
    """
    主函数：创建并显示窗口

    步骤：
    1. 创建 QApplication 实例（每个 PyQt5 程序只需要一个）
    2. 创建 QWidget 作为主窗口
    3. 设置窗口属性（标题、大小、位置）
    4. 调用 show() 显示窗口
    5. 进入 app.exec_() 事件循环
    """
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("示例 01: 最简单的窗口")
    window.setGeometry(100, 100, 400, 300)

    window.show()

    print("窗口已显示，关闭窗口退出程序")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
