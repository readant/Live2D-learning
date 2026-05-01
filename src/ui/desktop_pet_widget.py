"""
桌面宠物主窗口模块
无标题栏、可拖动、始终置顶
使用 QOpenGLWidget 渲染 Live2D 模型
增强的交互系统：支持单击、双击、三击、不同区域点击
"""

import random
import time
from typing import Optional

from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QRegion, QPainterPath, QColor, QFont
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QOpenGLWidget

import live2d.v3 as live2d

from config import settings
from src.live2d.model import Live2DModelInterface
from src.live2d.renderer import Live2DRenderer
from src.live2d.expression import Expression, EXPRESSION_CONFIGS
from src.core.mouse_tracker import MouseTracker
from src.core.animation_controller import AnimationController
from src.core.interaction_controller import InteractionController, HitArea


class DesktopPetWidget(QOpenGLWidget):
    """
    桌面宠物主窗口
    使用 QOpenGLWidget 渲染 Live2D 模型
    增强的交互系统：
    - 单击身体：触发 Tap@Body 动作
    - 单击头部：触发 Tap 动作
    - 双击：触发 Flick 或 Flick@Body
    - 三击：触发 FlickDown
    """

    # 表情变化信号
    expression_changed = pyqtSignal(str)
    # 动作完成信号
    motion_finished = pyqtSignal(str)

    def __init__(self, parent: Optional[QOpenGLWidget] = None):
        """
        初始化桌面宠物窗口
        
        Args:
            parent: 父窗口（可选）
        """
        super().__init__(parent)
        # ========== 核心组件 ==========
        # Live2D 模型接口（模拟模式）
        self.model: Optional[Live2DModelInterface] = None
        # Live2D 真实模型实例
        self.live2d_model = None
        # 渲染器
        self.renderer: Optional[Live2DRenderer] = None
        # 鼠标追踪器（用于实现头部/眼球跟随）
        self.mouse_tracker: Optional[MouseTracker] = None
        # 动画控制器（呼吸、眨眼、挥手）
        self.animation_controller: Optional[AnimationController] = None
        # 交互控制器
        self.interaction_controller: Optional[InteractionController] = None

        # ========== 状态变量 ==========
        # 当前表情
        self.current_expression = Expression.HAPPY
        # 是否正在拖拽窗口
        self._dragging = False
        # 拖拽时的鼠标位置偏移
        self._drag_position = QPoint()
        # 帧计数器
        self._frame_count = 0
        
        # ========== 点击检测状态 ==========
        self._last_click_time = 0
        self._click_count = 0
        self._click_timer = None
        self._double_click_interval = 0.3
        self._triple_click_interval = 0.5
        
        # 初始化各个模块
        self._init_ui()
        self._init_live2d()
        self._init_timers()

    def _init_ui(self) -> None:
        """初始化 UI 配置"""
        # ========== 窗口标志设置 ==========
        # FramelessWindowHint: 无标题栏
        # WindowStaysOnTopHint: 始终置顶
        # Qt.Tool: 任务栏不显示图标
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置固定窗口大小
        self.setFixedSize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        # 移动到屏幕右下角
        self._move_to_bottom_right()
        # 启用鼠标追踪（即使不按下鼠标也能接收鼠标移动事件）
        self.setMouseTracking(True)

    def _move_to_bottom_right(self) -> None:
        """将窗口移动到屏幕右下角"""
        from PyQt5.QtWidgets import QApplication
        # 获取屏幕几何尺寸
        screen_geo = QApplication.desktop().screenGeometry()
        # 计算并移动到右下角（留出 20px 边距）
        self.move(screen_geo.width() - settings.WINDOW_WIDTH - 20,
                  screen_geo.height() - settings.WINDOW_HEIGHT - 20)

    def _init_live2d(self) -> None:
        """初始化 Live2D 相关组件"""
        # 创建模型接口
        self.model = Live2DModelInterface(settings.MODEL_PATH)
        
        # 创建渲染器
        self.renderer = Live2DRenderer(self.model)
        # 创建鼠标追踪器（目标点在窗口中心）
        self.mouse_tracker = MouseTracker((
            settings.WINDOW_WIDTH // 2,
            settings.WINDOW_HEIGHT // 2
        ))
        # 创建动画控制器
        self.animation_controller = AnimationController(self.model)
        # 创建交互控制器
        self.interaction_controller = InteractionController()

    def _init_timers(self) -> None:
        """初始化定时器（用于每帧更新）"""
        # 创建更新定时器
        self.update_timer = QTimer(self)
        # 连接超时信号到更新函数
        self.update_timer.timeout.connect(self._on_update)
        # 启动定时器（按配置的帧间隔）
        self.update_timer.start(settings.FRAME_INTERVAL)

    def initializeGL(self) -> None:
        """OpenGL 初始化（由 Qt 自动调用）"""
        self.makeCurrent()
        try:
            # 初始化 Live2D OpenGL 环境
            live2d.init()
            live2d.glInit()
            # 创建模型实例并加载
            self.live2d_model = live2d.LAppModel()
            self.live2d_model.LoadModelJson(settings.MODEL_PATH)
            
            # 更新模型接口的引用
            if self.model:
                self.model._model = self.live2d_model
                self.model.initialized = True
            
            # 设置交互控制器的模型
            if self.interaction_controller:
                self.interaction_controller.set_model(self.live2d_model)
            
            print("[Live2D] OpenGL 初始化成功，模型已加载")
        except Exception as e:
            print(f"[Live2D] OpenGL 初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def resizeGL(self, w: int, h: int) -> None:
        """
        OpenGL 窗口大小改变时调用
        
        Args:
            w: 新宽度
            h: 新高度
        """
        if self.live2d_model:
            try:
                self.live2d_model.Resize(w, h)
            except Exception as e:
                print(f"[Live2D] 调整大小时出错: {e}")

    def paintGL(self) -> None:
        """OpenGL 渲染（每帧调用）"""
        self._frame_count += 1
        try:
            if self.live2d_model:
                # 真实模式：使用 Live2D SDK 渲染
                live2d.clearBuffer()
                self.live2d_model.Update()
                self.live2d_model.Draw()
            else:
                # 模拟模式：使用 QPainter 绘制简单图形
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                self._fallback_render(painter)
        except Exception as e:
            print(f"[Live2D] 渲染时出错: {e}")
            # 出错时回退到模拟渲染
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            self._fallback_render(painter)

    def _fallback_render(self, painter):
        """
        模拟模式渲染（绘制简单的椭圆来模拟 Live2D 模型
        
        Args:
            painter: QPainter 对象
        """
        params = self.model.parameters if self.model else {}
        # 根据呼吸参数计算偏移量
        breath_offset = params.get("ParamBreath", 0.5) * 5
        base_y = settings.WINDOW_HEIGHT // 2
        # 绘制身体（粉色椭圆）
        painter.setBrush(QColor(255, 200, 200))
        painter.setPen(QColor(200, 150, 150))
        body_rect = QRect(
            settings.WINDOW_WIDTH // 2 - 80,
            base_y - 50 + int(breath_offset),
            160,
            120
        )
        painter.drawEllipse(body_rect)
        # 绘制头部（浅粉色椭圆）
        head_y = base_y - 120 + int(breath_offset)
        head_x = settings.WINDOW_WIDTH // 2 + int(params.get("ParamAngleX", 0) * 2)
        painter.setBrush(QColor(255, 220, 220))
        painter.setPen(QColor(220, 180, 180))
        painter.drawEllipse(QRect(head_x - 60, head_y - 60, 120, 120))
        # 绘制状态文字
        painter.setFont(QFont("微软雅黑", 10))
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(10, 30, f"帧: {self._frame_count} [模拟模式]")

    def _on_update(self) -> None:
        """每帧更新函数（由定时器调用）"""
        delta_time = 1.0 / settings.FPS

        # 更新动画控制器（呼吸、眨眼、挥手）
        if self.animation_controller:
            self.animation_controller.update(delta_time)

        # 更新鼠标追踪，设置头部/眼球参数
        if self.mouse_tracker:
            angles = self.mouse_tracker.get_gaze_angles()
            if self.live2d_model:
                try:
                    self.live2d_model.SetParameterValue("ParamAngleX", angles[0])
                    self.live2d_model.SetParameterValue("ParamAngleY", angles[1])
                    self.live2d_model.SetParameterValue("ParamEyeBallX", angles[2])
                    self.live2d_model.SetParameterValue("ParamEyeBallY", angles[3])
                except Exception as e:
                    pass
            elif self.model:
                self.model.set_parameter("ParamAngleX", angles[0])
                self.model.set_parameter("ParamAngleY", angles[1])
                self.model.set_parameter("ParamEyeBallX", angles[2])
                self.model.set_parameter("ParamEyeBallY", angles[3])

        # 应用当前表情
        self._apply_expression(self.current_expression)

        # 更新模型
        if self.model:
            self.model.update(delta_time)

        # 触发重绘
        self.update()

    def _apply_expression(self, expression: Expression) -> None:
        """
        应用表情参数
        
        Args:
            expression: 表情枚举
        """
        config = EXPRESSION_CONFIGS.get(expression)
        if not config:
            return
        # 遍历表情配置，设置每个参数
        for param, value in config.items():
            if self.live2d_model:
                try:
                    self.live2d_model.SetParameterValue(param, value)
                except Exception as e:
                    pass
            elif self.model:
                self.model.set_parameter(param, value)

    def _detect_hit_area(self, y: float) -> HitArea:
        """
        检测点击区域（头部/身体）
        
        Args:
            y: 点击 Y 坐标
            
        Returns:
            命中区域
        """
        window_height = settings.WINDOW_HEIGHT
        relative_y = (y / window_height) * 100
        
        if relative_y < 40:
            return HitArea.HEAD
        else:
            return HitArea.BODY

    def _handle_click(self, x: float, y: float) -> None:
        """
        处理点击事件（区分单击、双击、三击）
        
        Args:
            x: 点击 X 坐标
            y: 点击 Y 坐标
        """
        current_time = time.time()
        hit_area = self._detect_hit_area(y)
        
        # ========== 连续点击计数算法 ==========
        if current_time - self._last_click_time > self._double_click_interval:
            self._click_count = 1
        else:
            self._click_count += 1
        
        self._last_click_time = current_time
        
        # 同时调用交互控制器处理
        if self.interaction_controller and self.live2d_model:
            self.interaction_controller.process_click(x, y, self._click_count)
        
        # ========== 延迟判断单击/双击/三击 ==========
        # 使用 QTimer.singleShot 延迟判断，避免立即触发单击
        if self._click_count == 1:
            QTimer.singleShot(int(self._double_click_interval * 1000), 
                           lambda: self._process_click_action(x, y, 1, hit_area))
        elif self._click_count == 2:
            QTimer.singleShot(int(self._triple_click_interval * 1000), 
                           lambda: self._process_click_action(x, y, 2, hit_area))
        elif self._click_count >= 3:
            self._process_click_action(x, y, 3, hit_area)

    def _process_click_action(self, x: float, y: float, click_count: int, hit_area: HitArea) -> None:
        """
        处理点击动作（根据点击次数和区域）
        
        Args:
            x: 点击 X 坐标
            y: 点击 Y 坐标
            click_count: 点击次数
            hit_area: 命中区域
        """
        # 如果当前点击次数不等于目标次数，说明已经被后续点击覆盖了，直接返回
        if self._click_count != click_count:
            return
        
        print(f"[交互] 点击位置: ({x:.0f}, {y:.0f}), 命中区域: {hit_area.value}, 点击次数: {click_count}")
        
        # 根据点击次数执行不同动作
        if click_count == 1:
            if hit_area == HitArea.BODY:
                self._trigger_motion("Tap@Body")
            else:
                self._trigger_motion("Tap")
            # 单击时循环切换表情
            self._cycle_expression()
            
        elif click_count == 2:
            if hit_area == HitArea.BODY:
                self._trigger_motion("Flick@Body")
            else:
                self._trigger_motion("Flick")
                
        elif click_count >= 3:
            self._trigger_motion("FlickDown")

    def _trigger_motion(self, motion_name: str) -> None:
        """
        触发动作
        
        Args:
            motion_name: 动作名称
        """
        # 如果是挥手相关动作，同时触发我们的自定义大幅度挥手
        if "Flick" in motion_name:
            if self.animation_controller:
                self.animation_controller.trigger_wave()
        
        # 调用 Live2D SDK 播放动作
        if self.live2d_model:
            try:
                priority = self.interaction_controller._motion_priorities.get(motion_name, 2) if self.interaction_controller else 2
                self.live2d_model.StartRandomMotion(motion_name, priority)
                print(f"[交互] 触发动作: {motion_name} (优先级: {priority})")
            except Exception as e:
                print(f"[交互] 触发动作失败: {motion_name}, 错误: {e}")

    def mouseMoveEvent(self, event) -> None:
        """
        鼠标移动事件处理
        
        Args:
            event: 鼠标事件
        """
        # 如果正在拖拽窗口，移动窗口
        if self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
            return

        # 否则，处理视线跟随
        if self.live2d_model:
            try:
                self.live2d_model.Drag(event.pos().x(), event.pos().y())
            except Exception as e:
                pass
        elif self.mouse_tracker:
            # 计算鼠标相对于窗口的坐标
            local_x = event.globalX() - self.x()
            local_y = event.globalY() - self.y()
            self.mouse_tracker.update_mouse_position(local_x, local_y)

    def mousePressEvent(self, event) -> None:
        """
        鼠标按下事件处理
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            # 开始拖拽窗口
            self._dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # 处理点击
            self._handle_click(event.pos().x(), event.pos().y())
            
            # 通知 Live2D 模型触摸事件
            if self.live2d_model:
                try:
                    self.live2d_model.Touch(event.pos().x(), event.pos().y())
                except Exception as e:
                    pass
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """
        鼠标释放事件处理
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

    def _cycle_expression(self) -> None:
        """循环切换表情"""
        expressions = list(Expression)
        current_index = expressions.index(self.current_expression)
        # 计算下一个表情索引（循环）
        new_index = (current_index + 1) % len(expressions)
        self.current_expression = expressions[new_index]
        # 应用新表情
        self._apply_expression(self.current_expression)
        # 发送表情变化信号
        self.expression_changed.emit(self.current_expression.value)
        print(f"[交互] 切换表情: {self.current_expression.value}")

    def contextMenuEvent(self, event) -> None:
        """
        右键菜单事件处理
        
        Args:
            event: 鼠标事件
        """
        menu = QMenu(self)
        # 设置菜单样式（半透明白色背景，圆角边框）
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 240);
                border: 2px solid rgba(100, 100, 100, 100);
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                padding: 10px 30px;
                font-size: 14px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: rgba(100, 180, 255, 150);
            }
        """)

        # ========== 表情菜单 ==========
        expression_menu = menu.addMenu("🎭 切换表情")
        action_happy = expression_menu.addAction("😊 开心")
        action_serious = expression_menu.addAction("🤔 认真")
        action_sleepy = expression_menu.addAction("😪 犯困")

        # ========== 动作菜单 ==========
        motion_menu = menu.addMenu("🎬 动作测试")
        action_tap = motion_menu.addAction("👆 点击头部 (Tap)")
        action_tap_body = motion_menu.addAction("👆 点击身体 (Tap@Body)")
        action_flick = motion_menu.addAction("👋 挥手 (Flick)")
        action_flick_body = motion_menu.addAction("👋 从身体挥手 (Flick@Body)")
        action_flick_down = motion_menu.addAction("👇 向下挥手 (FlickDown)")
        action_idle = motion_menu.addAction("💤 待机 (Idle)")
        
        motion_menu.addSeparator()
        action_big_wave = motion_menu.addAction("✋✨ 大幅度挥手 (自定义)")

        menu.addSeparator()
        
        # ========== 信息菜单 ==========
        info_menu = menu.addMenu("ℹ️ 信息")
        action_status = info_menu.addAction(f"📊 帧率: {self._frame_count}")
        action_motions = info_menu.addAction("🎬 可用动作列表")
        
        menu.addSeparator()
        action_quit = menu.addAction("❌ 退出")

        # 显示菜单并获取用户选择的动作
        action = menu.exec_(self.mapToGlobal(event.pos()))

        # ========== 处理菜单选择 ==========
        if action == action_happy:
            self.current_expression = Expression.HAPPY
            self._apply_expression(Expression.HAPPY)
            print("[交互] 切换表情: 开心")
        elif action == action_serious:
            self.current_expression = Expression.SERIOUS
            self._apply_expression(Expression.SERIOUS)
            print("[交互] 切换表情: 认真")
        elif action == action_sleepy:
            self.current_expression = Expression.SLEEPY
            self._apply_expression(Expression.SLEEPY)
            print("[交互] 切换表情: 犯困")
        elif action == action_tap:
            self._trigger_motion("Tap")
        elif action == action_tap_body:
            self._trigger_motion("Tap@Body")
        elif action == action_flick:
            self._trigger_motion("Flick")
        elif action == action_flick_body:
            self._trigger_motion("Flick@Body")
        elif action == action_flick_down:
            self._trigger_motion("FlickDown")
        elif action == action_idle:
            self._trigger_motion("Idle")
        elif action == action_big_wave:
            if self.animation_controller:
                self.animation_controller.trigger_wave()
                print("[交互] 触发自定义大幅度挥手")
        elif action == action_motions:
            if self.interaction_controller:
                motions = self.interaction_controller.get_available_motions()
                print(f"[信息] 可用动作: {', '.join(motions)}")
        elif action == action_quit:
            from PyQt5.QtWidgets import QApplication
            QApplication.quit()

    def set_expression(self, expression: str) -> None:
        """
        设置表情（外部调用接口）
        
        Args:
            expression: 表情字符串
        """
        try:
            expr = Expression(expression)
            self.current_expression = expr
            self._apply_expression(expr)
        except ValueError:
            pass

    def get_expression(self) -> str:
        """
        获取当前表情
        
        Returns:
            表情字符串
        """
        return self.current_expression.value

    def trigger_motion(self, motion_name: str) -> bool:
        """
        外部调用触发动作
        
        Args:
            motion_name: 动作名称
            
        Returns:
            是否成功触发
        """
        if self.live2d_model:
            try:
                priority = self.interaction_controller._motion_priorities.get(motion_name, 2) if self.interaction_controller else 2
                self.live2d_model.StartRandomMotion(motion_name, priority)
                print(f"[交互] 触发动作: {motion_name}")
                return True
            except Exception as e:
                print(f"[交互] 触发动作失败: {motion_name}, 错误: {e}")
                return False
        return False
