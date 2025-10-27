"""
stickerbot 包

对外提供 run() 与 build_application() 入口，便于 main.py 调用。
"""

from .app import run, build_application

__all__ = ["run", "build_application"]

