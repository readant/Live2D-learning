"""
示例 01: 最简单的 PyQt5 窗口

这个示例展示如何创建一个最基本的 PyQt5 窗口。
适合作为学习 PyQt5 的起点。

学习要点：
- QApplication 的创建和事件循环
- QWidget 的基本使用
- 窗口属性设置（标题、大小）
- 程序入口写法

运行方式：
    python 01_basic_window.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget


def main():
    """
    主函数：创建并显示窗口
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
