"""
表情模块
定义桌宠的表情类型和配置
"""

from enum import Enum
from typing import Dict, Tuple


class Expression(Enum):
    """
    表情类型枚举
    定义了桌宠可以切换的三种表情
    """
    HAPPY = "happy"    # 开心表情
    SERIOUS = "serious"  # 认真表情
    SLEEPY = "sleepy"    # 犯困表情


# ========== 表情参数配置 ==========
# 每个表情对应一系列 Live2D 参数值
# 参数说明：
#   - ParamEyeLSmile/ParamEyeRSmile: 左/右眼的微笑程度
#   - ParamEyeLOpen/ParamEyeROpen: 左/右眼的开闭程度
#   - ParamBrowLForm/ParamBrowRForm: 左/右眉的形状
#   - ParamMouthForm: 嘴部形状
#   - ParamMouthOpenY: 嘴部开闭
#   - ParamCheek: 脸颊泛红程度
# ======================================

EXPRESSION_CONFIGS: Dict[Expression, Dict[str, float]] = {
    # ========== 开心表情 ==========
    Expression.HAPPY: {
        "ParamEyeLSmile": 0.8,  # 左眼微笑
        "ParamEyeRSmile": 0.8,  # 右眼微笑
        "ParamMouthForm": 0.5,  # 嘴型
        "ParamMouthOpenY": 0.3,  # 嘴部张开
        "ParamCheek": 0.6,      # 脸颊泛红
    },
    # ========== 认真表情 ==========
    Expression.SERIOUS: {
        "ParamEyeLSmile": -0.4,  # 左眼不笑
        "ParamEyeRSmile": -0.4,  # 右眼不笑
        "ParamBrowLForm": 0.7,  # 左眉严肃
        "ParamBrowRForm": 0.7,  # 右眉严肃
        "ParamMouthForm": -0.4,  # 嘴型严肃
        "ParamMouthOpenY": 0.0,  # 嘴部闭上
        "ParamCheek": 0.0,      # 脸颊不红
    },
    # ========== 犯困表情 ==========
    Expression.SLEEPY: {
        "ParamEyeLOpen": 0.2,  # 左眼微闭
        "ParamEyeROpen": 0.2,  # 右眼微闭
        "ParamMouthOpenY": 0.5,  # 嘴部微张
        "ParamCheek": 0.1,      # 脸颊微红
    },
}
