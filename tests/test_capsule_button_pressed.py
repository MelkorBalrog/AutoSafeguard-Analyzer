import tkinter as tk

import pytest

from gui.capsule_button import CapsuleButton, _darken


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


def test_capsule_button_has_inner_outline():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()

    expected = _darken(btn._current_color, 0.7)
    for item in btn._border_gap:
        option = "fill" if btn.type(item) == "line" else "outline"
        assert btn.itemcget(item, option) == expected

    root.destroy()
