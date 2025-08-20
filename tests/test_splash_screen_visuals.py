import os
import sys
import tkinter as tk

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from gui.splash_screen import SplashScreen


def test_splash_screen_visual_elements():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    root.withdraw()
    splash = SplashScreen(root, auto_start=False)
    splash._draw_gear()
    splash._draw_cube()
    horizon = splash.canvas.find_withtag("horizon")
    glow = splash.canvas.find_withtag("gear_glow")
    faces = splash.canvas.find_withtag("cube_face")
    splash.destroy()
    root.destroy()
    assert horizon, "Horizon line missing"
    assert glow, "Gear glow missing"
    assert faces, "Cube faces missing"
