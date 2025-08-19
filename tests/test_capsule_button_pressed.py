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
