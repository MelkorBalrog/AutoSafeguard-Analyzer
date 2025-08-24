import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.capsule_button import CapsuleButton


def test_capsule_button_has_diffused_circles_and_shade():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test", bg="#888888")
    btn.pack()
    root.update_idletasks()
    assert len(getattr(btn, "_shine_items", [])) >= 7
    assert len(getattr(btn, "_shade_items", [])) >= 1
    root.destroy()
