import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_capsule_button_renders_text_shading():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()
    assert getattr(btn, "_text_shade_item", None) is not None
    root.destroy()
