import sys
from pathlib import Path
import tkinter as tk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton


def test_glow_edges_only():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    btn = CapsuleButton(root, text="Glow")
    btn.pack()
    root.update_idletasks()
    btn._on_enter(type("E", (), {})())
    item_types = {btn.type(i) for i in btn._glow_items}
    assert "oval" not in item_types
    root.destroy()
