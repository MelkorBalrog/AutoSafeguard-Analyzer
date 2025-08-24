import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.capsule_button import CapsuleButton, _darken


def test_capsule_button_tints_parent_background():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Blend", bg="#89aaff")
    btn.pack()
    root.update_idletasks()
    expected_bg = _darken("#89aaff", 0.9)
    assert root.cget("bg") == expected_bg
    assert btn.cget("bg") == expected_bg
    root.destroy()

