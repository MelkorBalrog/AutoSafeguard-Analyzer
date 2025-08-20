import tkinter as tk
import pytest
from gui.capsule_button import CapsuleButton, _lighten

def test_hover_brightens_entire_button():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Bright", bg="#445566")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    assert btn._current_color == _lighten("#445566", 1.5)
    root.destroy()
