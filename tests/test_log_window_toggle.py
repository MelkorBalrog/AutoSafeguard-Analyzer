import os
import sys

import pytest
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp


def test_toggle_log_area():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    assert app.log_frame.winfo_manager() == "pack"
    app.toggle_logs()
    assert app.log_frame.winfo_manager() == ""
    app.toggle_logs()
    assert app.log_frame.winfo_manager() == "pack"
    root.destroy()
