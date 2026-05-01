# 更新日志

## v2.0 - 交互系统大改版 (2024-当前版本)

### 🎯 主要更新

#### 1. 新增交互控制器 (`InteractionController`)

**文件**：`src/core/interaction_controller.py`

**功能**：
- 统一的交互管理系统
- 支持单击、双击、三击检测
- 动作优先级管理
- 动作冷却系统
- 动作回调机制
- 命中区域检测（头部/身体）

**核心类**：
```python
class InteractionController:
    def process_click(x, y, click_count)  # 处理点击
    def trigger_motion(motion_name)        # 触发动作
    def set_motion_callback(name, func)    # 设置回调
    def set_cooldown(motion, seconds)      # 设置冷却
```

#### 2. 增强的点击交互

**改进前**：
- 单击触发：`Tap` 动作 + 表情切换

**改进后**：
- 单击头部 → `Tap` + 表情切换
- 单击身体 → `Tap@Body`
- 双击头部 → `Flick`
- 双击身体 → `Flick@Body`
- 三击任意位置 → `FlickDown`

#### 3. 动作优先级系统

```python
_motion_priorities = {
    "Idle": 0,        # 待机（最低）
    "Tap": 2,         # 点击
    "Tap@Body": 2,    # 点击身体
    "Flick": 2,       # 滑动
    "Flick@Body": 2,  # 滑动身体
    "FlickDown": 2,   # 下滑
}
```

#### 4. 动作冷却系统

防止动作被频繁触发，提升用户体验：

```python
_cooldowns = {
    "Tap": 1.0,      # 1秒冷却
    "Tap@Body": 1.0, # 1秒冷却
    "Flick": 0.5,    # 0.5秒冷却
    "Flick@Body": 0.5,
    "FlickDown": 0.5,
}
```

#### 5. 增强的右键菜单

**新增功能**：
- 🎭 表情切换子菜单
- 🎬 动作测试子菜单
- ℹ️ 信息查看（帧率、可用动作）
- ❌ 退出选项

**菜单样式**：
- 圆角边框
- 悬停高亮
- Emoji 图标

#### 6. 命

...

动文件重命名
... [内容已截断，原长度 6149 字符]