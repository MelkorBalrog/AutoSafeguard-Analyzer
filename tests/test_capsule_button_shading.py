import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_text_shading_exists():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_content_shade_item", None) is not None
    assert getattr(btn, "_text_shadow_item", None) is None
    root.destroy()


def test_icon_shading_exists():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = tk.PhotoImage(width=10, height=10)
    btn = CapsuleButton(root, image=img)
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_content_shade_item", None) is not None
    assert getattr(btn, "_icon_shadow_item", None) is None
    root.destroy()
