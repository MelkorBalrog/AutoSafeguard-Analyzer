import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.controls.button_utils import enable_listbox_hover_highlight


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


def test_treeview_hover_after_item_deleted():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    enable_listbox_hover_highlight(root)
    tree = ttk.Treeview(root, columns=("c",), show="headings")
    tree.insert("", "end", iid="0", values=("a",))
    tree.insert("", "end", iid="1", values=("b",))
    tree.pack()
    root.update_idletasks()

    x0, y0, _, _ = tree.bbox("0")
    tree.event_generate("<Motion>", x=x0 + 1, y=y0 + 1)
    root.update_idletasks()
    assert getattr(tree, "_hover_item", None) == "0"

    tree.delete("0")
    root.update_idletasks()

    x1, y1, _, _ = tree.bbox("1")
    tree.event_generate("<Motion>", x=x1 + 1, y=y1 + 1)
    root.update_idletasks()
    assert getattr(tree, "_hover_item", None) == "1"
    assert tree.tag_has("hover", "1")
    root.destroy()
