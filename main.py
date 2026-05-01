"""
Live2D桌面宠物主程序入口
基于PyQt5 + Live2D SDK实现
功能：头部/眼球跟随鼠标、随机呼吸、点击交互、表情切换
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from config import settings
from src.ui.desktop_pet_widget import DesktopPetWidget


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Live2D桌宠")

    pet = DesktopPetWidget()
    pet.show()

    print("=" * 50)
    print("Live2D桌面宠物已启动")
    print("功能说明：")
    print("  - 移动鼠标：头部/眼球跟随")
    print("  - 左键点击：触发挥手和表情切换")
    print("  - 右键菜单：手动选择表情/退出")
    print("=" * 50)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
