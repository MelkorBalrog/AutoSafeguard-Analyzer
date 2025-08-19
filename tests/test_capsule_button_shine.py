import os
import sys
import pytest
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.capsule_button import CapsuleButton, _lighten


def test_capsule_button_has_shine():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Hi")
    try:
        assert len(btn._shine_items) == 3
        shine = btn.itemcget(btn._shine_items[0], "fill").lower()
        assert shine == _lighten(btn._normal_color, 1.3)
    finally:
        root.destroy()
