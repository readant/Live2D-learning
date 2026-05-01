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
    """
    主程序入口函数
    初始化 Qt 应用程序，创建并显示桌面宠物窗口
    """
    # ========== Qt 应用程序配置 ==========
    # 启用 OpenGL 上下文共享（Live2D 需要）
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    
    # 创建 Qt 应用程序实例
    app = QApplication(sys.argv)
    # 关闭最后一个窗口时不退出应用程序（桌宠需要保持运行）
    app.setQuitOnLastWindowClosed(False)
    # 设置应用程序名称
    app.setApplicationName("Live2D桌宠")

    # ========== 创建并显示桌面宠物窗口 ==========
    pet = DesktopPetWidget()
    pet.show()

    # ========== 打印启动信息 ==========
    print("=" * 50)
    print("Live2D桌面宠物已启动")
    print("功能说明：")
    print("  - 移动鼠标：头部/眼球跟随")
    print("  - 左键点击：触发挥手和表情切换")
    print("  - 右键菜单：手动选择表情/退出")
    print("=" * 50)

    # ========== 进入 Qt 事件循环 ==========
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
