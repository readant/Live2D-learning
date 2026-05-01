"""
表情模块
定义桌宠的表情类型和配置
"""

from enum import Enum
from typing import Dict, Tuple


class Expression(Enum):
    """表情类型枚举"""
    HAPPY = "happy"
    SERIOUS = "serious"
    SLEEPY = "sleepy"


EXPRESSION_CONFIGS: Dict[Expression, Dict[str, Tuple[float, float]]] = {
    Expression.HAPPY: {
        "ParamMouthOpenY": (0.3, 0.5),
        "ParamEyeBallX": (0, 0),
        "ParamEyeBallY": (0, 0),
    },
    Expression.SERIOUS: {
        "ParamMouthOpenY": (0.0, 0.1),
        "ParamEyeBallX": (0, 0),
        "ParamEyeBallY": (-0.2, 0),
    },
    Expression.SLEEPY: {
        "ParamMouthOpenY": (0.5, 0.7),
        "ParamEyeBallX": (0, 0),
        "ParamEyeBallY": (0.3, 0),
    },
}
