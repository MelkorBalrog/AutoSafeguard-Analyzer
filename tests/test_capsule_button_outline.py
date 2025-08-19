import tkinter as tk

import pytest

from gui.capsule_button import CapsuleButton, _darken


def test_capsule_button_has_inner_outline():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()

    assert getattr(btn, "_border_outline", []), "outline not created"
    outline_color = btn.itemcget(btn._border_outline[0], "outline")
    assert outline_color == _darken("#888888", 0.7)

    root.destroy()
