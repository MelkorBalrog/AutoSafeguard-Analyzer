import sys
from pathlib import Path
import tkinter as tk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import enable_listbox_hover_highlight


def _rgb(value):
    if isinstance(value, tuple):
        return value[:3]
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def test_listbox_row_highlight_on_hover():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    enable_listbox_hover_highlight(root)
    lb = tk.Listbox(root)
    lb.insert("end", "a", "b")
    lb.pack()
    root.update_idletasks()

    orig = lb.itemcget(0, "background")
    x, y, w, h = lb.bbox(0)
    lb.event_generate("<Motion>", x=x + 1, y=y + 1)
    root.update_idletasks()
    hover = lb.itemcget(0, "background")
    assert hover != orig
    r, g, b = _rgb(hover)
    assert g - max(r, b) >= 20

    x2, y2, w2, h2 = lb.bbox(1)
    lb.event_generate("<Motion>", x=x2 + 1, y=y2 + 1)
    root.update_idletasks()
    assert lb.itemcget(0, "background") == orig
    root.destroy()
