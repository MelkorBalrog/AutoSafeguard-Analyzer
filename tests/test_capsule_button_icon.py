import os
import sys
import tkinter as tk
import tkinter.font as tkfont

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gui.capsule_button import CapsuleButton
from gui.icon_factory import create_icon
import pytest


def test_capsule_button_icon_and_sizing():
    try:
        root = tk.Tk()
    except tk.TclError:  # pragma: no cover - environment without display
        pytest.skip("Tk not available")
    root.withdraw()
    icon = create_icon("folder", "black")
    text = "Load CSV File"
    btn = CapsuleButton(root, text=text, image=icon, compound=tk.LEFT)
    root.update_idletasks()
    font = tkfont.nametofont("TkDefaultFont")
    expected = font.measure(text) + icon.width() + 2 * btn._padx + 4
    assert int(btn["width"]) >= expected
    assert btn._image_item is not None
    root.destroy()
