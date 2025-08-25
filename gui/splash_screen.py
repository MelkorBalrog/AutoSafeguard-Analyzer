"""Compatibility wrapper for splash screen module.

This shim preserves the legacy import path ``gui.splash_screen``
while the real implementation lives in ``gui.windows.splash_screen``.
"""
from .windows.splash_screen import SplashScreen

__all__ = ["SplashScreen"]
