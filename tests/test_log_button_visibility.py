import os
import sys
import pytest
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp


def test_log_toggle_button_visible_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    app.show_explorer()
    app.toggle_explorer_pin()  # pin the explorer
    app.toggle_logs()  # show logs
    root.update()
    # The toggle button should remain managed and visible
    assert app.toggle_log_button.winfo_manager() == "pack"
    app.toggle_logs()  # hide logs
    root.destroy()
