import os
import sys
import pytest
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.closable_notebook import ClosableNotebook


def test_tab_detach_and_reattach():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    nb = ClosableNotebook(root)
    frame = ttk.Frame(nb)
    nb.add(frame, text="Tab1")
    nb.update_idletasks()

    class Event: ...

    press = Event(); press.x = 5; press.y = 5
    nb._on_tab_press(press)
    nb._dragging = True
    release = Event()
    release.x_root = nb.winfo_rootx() + nb.winfo_width() + 40
    release.y_root = nb.winfo_rooty() + nb.winfo_height() + 40
    nb._on_tab_release(release)

    assert len(nb.tabs()) == 0
    new_nb = frame.master
    assert isinstance(new_nb, ClosableNotebook)

    press2 = Event(); press2.x = 5; press2.y = 5
    new_nb._on_tab_press(press2)
    new_nb._dragging = True
    release2 = Event()
    release2.x_root = nb.winfo_rootx() + 10
    release2.y_root = nb.winfo_rooty() + 10
    new_nb._on_tab_release(release2)

    assert len(nb.tabs()) == 1
    assert frame.master is nb
    root.destroy()


def test_tab_detach_without_motion():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    nb = ClosableNotebook(root)
    frame = ttk.Frame(nb)
    nb.add(frame, text="Tab1")
    nb.update_idletasks()

    class Event: ...

    press = Event(); press.x = 5; press.y = 5
    nb._on_tab_press(press)
    release = Event()
    release.x_root = nb.winfo_rootx() + nb.winfo_width() + 40
    release.y_root = nb.winfo_rooty() + nb.winfo_height() + 40
    release.x = nb.winfo_width() + 40
    release.y = nb.winfo_height() + 40
    nb._on_tab_release(release)

    assert len(nb.tabs()) == 0
    root.destroy()
