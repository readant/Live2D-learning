"""
Live2D 桌面宠物项目配置
包含所有全局配置项，便于统一管理和调整
"""

# ========== 模型配置 ==========
# Live2D 模型文件的路径
MODEL_PATH = "./resources/models/Hiyori.model3.json"

# ========== 窗口配置 ==========
# 窗口宽度（像素）
WINDOW_WIDTH = 400
# 窗口高度（像素）
WINDOW_HEIGHT = 500
# 窗口标题
WINDOW_TITLE = "Live2D 桌宠"

# ========== 渲染配置 ==========
# 帧率（每秒帧数），决定动画流畅度
FPS = 60
# 帧间隔（毫秒），由 FPS 计算得出，用于定时器
FRAME_INTERVAL = 1000 // FPS

# ========== 表情配置（已废弃，使用 Expression 枚举） ==========
# 这些常量保留用于兼容性，新项目建议使用 src/live2d/expression.py 中的 Expression 枚举
EXPRESSION_HAPPY = "happy"
EXPRESSION_SERIOUS = "serious"
EXPRESSION_SLEEPY = "sleepy"

# ========== 眨眼动画配置 ==========
# 眨眼的最小间隔时间（秒）
BLINK_MIN_INTERVAL = 2.0
# 眨眼的最大间隔时间（秒）
BLINK_MAX_INTERVAL = 5.0
# 眨眼动画的持续时间（秒），控制眼睛闭合的快慢
BLINK_DURATION = 0.3

# ========== 呼吸动画配置 ==========
# 呼吸动画的速度，值越大呼吸越快
BREATH_SPEED = 1.5
# 挥手动画的持续时间（秒）
WAVE_DURATION = 2.0
