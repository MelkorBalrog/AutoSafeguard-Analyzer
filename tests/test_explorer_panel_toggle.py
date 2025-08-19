import os
import sys
import pytest
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp


def test_toggle_explorer_panel():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    assert app.explorer_pane.winfo_manager() == ""
    app.show_explorer()
    assert app.explorer_pane.winfo_manager() == "panedwindow"
    app.hide_explorer()
    assert app.explorer_pane.winfo_manager() == ""
    app.show_explorer()
    app.toggle_explorer_pin()  # pin the explorer
    app._schedule_explorer_hide(delay=0)
    root.update()
    assert app.explorer_pane.winfo_manager() == "panedwindow"
    app.toggle_explorer_pin()  # unpin
    app._schedule_explorer_hide(delay=0)
    root.update()
    assert app.explorer_pane.winfo_manager() == ""
    root.destroy()
