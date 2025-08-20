import os
import sys
import tkinter as tk

import pytest

# Ensure repository root in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui import logger, messagebox  # noqa: E402
from AutoML import AutoMLApp  # noqa: E402


def test_log_window_uses_default_height_for_messages():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    logger.init_log_window(root)
    long_message = "This is a long message " * 50
    short_message = "short"
    default_height = logger._default_height
    messagebox.showinfo("Title", long_message)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    messagebox.showinfo("Title", short_message)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    root.destroy()


def test_log_window_default_height_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    app.toggle_explorer_pin()
    default_height = logger._default_height
    messagebox.showinfo("Title", "Pinned panel message" * 40)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    root.destroy()

