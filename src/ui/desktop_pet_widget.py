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

    expression_changed = pyqtSignal(str)
    motion_finished = pyqtSignal(str)

    def __init__(self, parent: Optional[QOpenGLWidget] = None):
        super().__init__(parent)
        self.model: Optional[Live2DModelInterface] = None
        self.live2d_model = None
        self.renderer: Optional[Live2DRenderer] = None
        self.mouse_tracker: Optional[MouseTracker] = None
        self.animation_controller: Optional[AnimationController] = None
        self.interaction_controller: Optional[InteractionController] = None

        self.current_expression = Expression.HAPPY
        self._dragging = False
        self._drag_position = QPoint()
        self._frame_count = 0
        
        self._last_click_time = 0
        self._click_count = 0
        self._click_timer = None
        self._double_click_interval = 0.3
        self._triple_click_interval = 0.5
        
        self._init_ui()
        self._init_live2d()
        self._init_timers()

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self._move_to_bottom_right()
        self.setMouseTracking(True)

    def _move_to_bottom_right(self) -> None:
        from PyQt5.QtWidgets import QApplication
        screen_geo = QApplication.desktop().screenGeometry()
        self.move(screen_geo.width() - settings.WINDOW_WIDTH - 20,
                  screen_geo.height() - settings.WINDOW_HEIGHT - 20)

    def _init_live2d(self) -> None:
        self.model = Live2DModelInterface(settings.MODEL_PATH)
        
        self.renderer = Live2DRenderer(self.model)
        self.mouse_tracker = MouseTracker((
            settings.WINDOW_WIDTH // 2,
            settings.WINDOW_HEIGHT // 2
        ))
        self.animation_controller = AnimationController(self.model)
        self.interaction_controller = InteractionController()

    def _init_timers(self) -> None:
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._on_update)
        self.update_timer.start(settings.FRAME_INTERVAL)

    def initializeGL(self) -> None:
        self.makeCurrent()
        try:
            live2d.init()
            live2d.glInit()
            self.live2d_model = live2d.LAppModel()
            self.live2d_model.LoadModelJson(settings.MODEL_PATH)
            
            if self.model:
                self.model._model = self.live2d_model
                self.model.initialized = True
            
            if self.interaction_controller:
                self.interaction_controller.set_model(self.live2d_model)
            
            print("[Live2D] OpenGL 初始化成功，模型已加载")
        except Exception as e:
            print(f"[Live2D] OpenGL 初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def resizeGL(self, w: int, h: int) -> None:
        if self.live2d_model:
            try:
                self.live2d_model.Resize(w, h)
            except Exception as e:
                print(f"[Live2D] 调整大小时出错: {e}")

    def paintGL(self) -> None:
        self._frame_count += 1
        try:
            if self.live2d_model:
                live2d.clearBuffer()
                self.live2d_model.Update()
                self.live2d_model.Draw()
            else:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                self._fallback_render(painter)
        except Exception as e:
            print(f"[Live2D] 渲染时出错: {e}")
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            self._fallback_render(painter)

    def _fallback_render(self, painter):
        params = self.model.parameters if self.model else {}
        breath_offset = params.get("ParamBreath", 0.5) * 5
        base_y = settings.WINDOW_HEIGHT // 2
        painter.setBrush(QColor(255, 200, 200))
        painter.setPen(QColor(200, 150, 150))
        body_rect = QRect(
            settings.WINDOW_WIDTH // 2 - 80,
            base_y - 50 + int(breath_offset),
            160,
            120
        )
        painter.drawEllipse(body_rect)
        head_y = base_y - 120 + int(breath_offset)
        head_x = settings.WINDOW_WIDTH // 2 + int(params.get("ParamAngleX", 0) * 2)
        painter.setBrush(QColor(255, 220, 220))
        painter.setPen(QColor(220, 180, 180))
        painter.drawEllipse(QRect(head_x - 60, head_y - 60, 120, 120))
        painter.setFont(QFont("微软雅黑", 10))
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(10, 30, f"帧: {self._frame_count} [模拟模式]")

    def _on_update(self) -> None:
        delta_time = 1.0 / settings.FPS

        if self.animation_controller:
            self.animation_controller.update(delta_time)

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

        if self.model:
            self.model.update(delta_time)

        self.update()

    def _apply_expression(self, expression: Expression) -> None:
        config = EXPRESSION_CONFIGS.get(expression)
        if not config:
            return
        for param, (min_val, max_val) in config.items():
            value = random.uniform(min_val, max_val)
            if self.live2d_model:
                try:
                    self.live2d_model.SetParameterValue(param, value)
                except Exception as e:
                    pass
            elif self.model:
                self.model.set_parameter(param, value)

    def _detect_hit_area(self, y: float) -> HitArea:
        """检测点击区域（头部/身体）"""
        window_height = settings.WINDOW_HEIGHT
        relative_y = (y / window_height) * 100
        
        if relative_y < 40:
            return HitArea.HEAD
        else:
            return HitArea.BODY

    def _handle_click(self, x: float, y: float) -> None:
        """处理点击事件（区分单击、双击、三击）"""
        current_time = time.time()
        hit_area = self._detect_hit_area(y)
        
        if current_time - self._last_click_time > self._double_click_interval:
            self._click_count = 1
        else:
            self._click_count += 1
        
        self._last_click_time = current_time
        
        if self.interaction_controller and self.live2d_model:
            self.interaction_controller.process_click(x, y, self._click_count)
        
        if self._click_count == 1:
            QTimer.singleShot(int(self._double_click_interval * 1000), 
                           lambda: self._process_click_action(x, y, 1, hit_area))
        elif self._click_count == 2:
            QTimer.singleShot(int(self._triple_click_interval * 1000), 
                           lambda: self._process_click_action(x, y, 2, hit_area))
        elif self._click_count >= 3:
            self._process_click_action(x, y, 3, hit_area)

    def _process_click_action(self, x: float, y: float, click_count: int, hit_area: HitArea) -> None:
        """处理点击动作（根据点击次数和区域）"""
        if self._click_count != click_count:
            return
        
        print(f"[交互] 点击位置: ({x:.0f}, {y:.0f}), 命中区域: {hit_area.value}, 点击次数: {click_count}")
        
        if click_count == 1:
            if hit_area == HitArea.BODY:
                self._trigger_motion("Tap@Body")
            else:
                self._trigger_motion("Tap")
            self._cycle_expression()
            
        elif click_count == 2:
            if hit_area == HitArea.BODY:
                self._trigger_motion("Flick@Body")
            else:
                self._trigger_motion("Flick")
                
        elif click_count >= 3:
            self._trigger_motion("FlickDown")

    def _trigger_motion(self, motion_name: str) -> None:
        """触发动作"""
        if self.live2d_model:
            try:
                priority = self.interaction_controller._motion_priorities.get(motion_name, 2) if self.interaction_controller else 2
                self.live2d_model.StartRandomMotion(motion_name, priority)
                print(f"[交互] 触发动作: {motion_name} (优先级: {priority})")
            except Exception as e:
                print(f"[交互] 触发动作失败: {motion_name}, 错误: {e}")
                if self.animation_controller and self.animation_controller.trigger_wave():
                    print("[交互] 模拟触发动作")

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
            return

        if self.live2d_model:
            try:
                self.live2d_model.Drag(event.pos().x(), event.pos().y())
            except Exception as e:
                pass
        elif self.mouse_tracker:
            local_x = event.globalX() - self.x()
            local_y = event.globalY() - self.y()
            self.mouse_tracker.update_mouse_position(local_x, local_y)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self._handle_click(event.pos().x(), event.pos().y())
            
            if self.live2d_model:
                try:
                    self.live2d_model.Touch(event.pos().x(), event.pos().y())
                except Exception as e:
                    pass
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

    def _cycle_expression(self) -> None:
        expressions = list(Expression)
        current_index = expressions.index(self.current_expression)
        new_index = (current_index + 1) % len(expressions)
        self.current_expression = expressions[new_index]
        self._apply_expression(self.current_expression)
        self.expression_changed.emit(self.current_expression.value)
        print(f"[交互] 切换表情: {self.current_expression.value}")

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
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

        expression_menu = menu.addMenu("🎭 切换表情")
        action_happy = expression_menu.addAction("😊 开心")
        action_serious = expression_menu.addAction("🤔 认真")
        action_sleepy = expression_menu.addAction("😪 犯困")

        motion_menu = menu.addMenu("🎬 动作测试")
        action_tap = motion_menu.addAction("👆 点击 (Tap)")
        action_flick = motion_menu.addAction("👆👇 滑动 (Flick)")
        action_flick_down = motion_menu.addAction("👇 下滑 (FlickDown)")
        action_idle = motion_menu.addAction("💤 待机 (Idle)")

        menu.addSeparator()
        
        info_menu = menu.addMenu("ℹ️ 信息")
        action_status = info_menu.addAction(f"📊 帧率: {self._frame_count}")
        action_motions = info_menu.addAction("🎬 可用动作列表")
        
        menu.addSeparator()
        action_quit = menu.addAction("❌ 退出")

        action = menu.exec_(self.mapToGlobal(event.pos()))

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
        elif action == action_flick:
            self._trigger_motion("Flick")
        elif action == action_flick_down:
            self._trigger_motion("FlickDown")
        elif action == action_idle:
            self._trigger_motion("Idle")
        elif action == action_motions:
            if self.interaction_controller:
                motions = self.interaction_controller.get_available_motions()
                print(f"[信息] 可用动作: {', '.join(motions)}")
        elif action == action_quit:
            from PyQt5.QtWidgets import QApplication
            QApplication.quit()

    def set_expression(self, expression: str) -> None:
        try:
            expr = Expression(expression)
            self.current_expression = expr
            self._apply_expression(expr)
        except ValueError:
            pass

    def get_expression(self) -> str:
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