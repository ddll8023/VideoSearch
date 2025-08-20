"""
蓝图包
包含所有路由蓝图的定义
"""

from .video import video_bp
from .resource import resource_bp

__all__ = ["video_bp", "resource_bp"]
