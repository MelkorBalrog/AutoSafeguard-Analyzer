import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_glow_edges_only():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    item_types = {btn.type(i) for i in btn._glow_items}
    assert "oval" not in item_types
    root.destroy()


def test_glow_matches_button_width():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    w = int(btn["width"])
    r = btn._radius
    top_line = btn._glow_items[1]
    x1, _y1, x2, _y2 = btn.coords(top_line)
    assert x1 == r - 1
    assert x2 == w - r + 1
    root.destroy()
