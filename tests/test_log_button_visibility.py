import os
import sys
import tkinter as tk
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp


def test_log_toggle_button_visible_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    # Pin the explorer pane which previously caused the toggle button to be hidden
    app.toggle_explorer_pin()
    app.toggle_logs()  # show logs
    root.update_idletasks()
    button_bottom = app.toggle_log_button.winfo_y() + app.toggle_log_button.winfo_height()
    assert button_bottom <= root.winfo_height()
    root.destroy()
