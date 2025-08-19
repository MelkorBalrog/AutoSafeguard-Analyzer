import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_text_without_shadow_or_highlight():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()
    assert not hasattr(btn, "_text_shadow_item")
    assert not hasattr(btn, "_text_highlight_item")
    root.destroy()


def test_icon_highlight_without_shadow():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = tk.PhotoImage(width=10, height=10)
    btn = CapsuleButton(root, image=img)
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_icon_highlight_item", None) is not None
    assert not hasattr(btn, "_icon_shadow_item")
    root.destroy()


def test_glow_on_hover_and_press():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    assert btn._glow_items == []
    btn._on_enter(type("E", (), {})())
    assert btn._glow_items
    btn._on_press(type("E", (), {})())
    assert btn._glow_items == []
    btn._on_release(type("E", (), {"x":1,"y":1})())
    assert btn._glow_items
    root.destroy()
