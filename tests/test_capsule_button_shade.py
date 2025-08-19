import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton, _darken


def test_capsule_button_has_background_shade():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_shade_items", []), "shade not created"
    shade_color = btn.itemcget(btn._shade_items[0], "fill")
    assert shade_color == _darken("#888888", 0.9)
    root.destroy()
