import tkinter as tk

import pytest

from gui.capsule_button import CapsuleButton


def test_capsule_button_darkens_when_pressed():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()

    btn.event_generate("<ButtonPress-1>", x=1, y=1)
    assert btn._current_color == btn._pressed_color

    btn.event_generate("<ButtonRelease-1>", x=1, y=1)
    assert btn._current_color == btn._hover_color

    root.destroy()


def test_capsule_button_has_inset_shadow():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()

    assert hasattr(btn, "_depth_items")
    assert btn._depth_items
    shadow_item = btn._depth_items[0]
    shadow_color = btn.itemcget(shadow_item, "fill") or btn.itemcget(shadow_item, "outline")
    from gui.capsule_button import _darken
    assert shadow_color == _darken(btn._normal_color, 0.8)

    root.destroy()
