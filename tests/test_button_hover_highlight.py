import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import add_hover_highlight


def _sum_rgb(value):
    if isinstance(value, tuple):
        return sum(value[:3])
    return sum(int(value[i : i + 2], 16) for i in (1, 3, 5))


def test_add_hover_highlight_swaps_to_lighter_image():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    img = tk.PhotoImage(width=2, height=2)
    img.put("#808080", to=(0, 0, 2, 2))
    btn = ttk.Button(root, image=img)
    hover_img = add_hover_highlight(btn, img)

    btn.event_generate("<Enter>")
    root.update_idletasks()

    assert btn.cget("image") == str(hover_img)
    assert _sum_rgb(hover_img.get(0, 0)) > _sum_rgb(img.get(0, 0))
    root.destroy()

