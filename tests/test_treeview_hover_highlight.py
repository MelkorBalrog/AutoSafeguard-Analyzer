import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import enable_listbox_hover_highlight


def _rgb(value):
    if isinstance(value, tuple):
        return value[:3]
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def test_treeview_row_highlight_on_hover():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    enable_listbox_hover_highlight(root)
    tree = ttk.Treeview(root, columns=("c",), show="headings")
    tree.insert("", "end", iid="0", values=("a",))
    tree.pack()
    root.update_idletasks()

    x, y, w, h = tree.bbox("0")
    tree.event_generate("<Motion>", x=x + 1, y=y + 1)
    root.update_idletasks()
    assert tree.tag_has("hover", "0")
    color = tree.tag_configure("hover", "background")[-1]
    r, g, b = _rgb(color)
    assert g - max(r, b) >= 20

    tree.event_generate("<Leave>")
    root.update_idletasks()
    assert not tree.tag_has("hover", "0")
    root.destroy()
