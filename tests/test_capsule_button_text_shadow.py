import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_capsule_button_renders_text_without_shadow():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Test")
    btn.pack()
    root.update_idletasks()
    text_items = [i for i in btn.find_withtag("all") if btn.type(i) == "text"]
    assert len(text_items) == 2
    root.destroy()
