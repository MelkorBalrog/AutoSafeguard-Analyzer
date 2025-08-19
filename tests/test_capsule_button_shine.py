import os
import sys
import tkinter as tk
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.capsule_button import CapsuleButton


def test_capsule_button_has_shine_effect():
    if not os.environ.get("DISPLAY"):
        pytest.skip("Requires display for Tk")
    root = tk.Tk()
    btn = CapsuleButton(root, text="Demo")
    shine_id = getattr(btn, "_shine_item", None)
    assert shine_id is not None
    shine_color = btn.itemcget(shine_id, "fill")
    assert shine_color != btn._current_color
    root.destroy()
