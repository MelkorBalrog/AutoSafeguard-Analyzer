import os
import sys
import tkinter as tk
import pytest

# Ensure repository root in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui import logger, messagebox
from AutoML import AutoMLApp


def test_log_window_expands_to_fit_message():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    logger.init_log_window(root)
    long_message = "This is a long message " * 50
    default_height = logger._default_height
    messagebox.showinfo("Title", long_message)
    root.update_idletasks()
    display_lines = logger.log_widget.count("1.0", "end-1c", "displaylines")[0]
    expected_height = logger._line_height * display_lines
    assert logger.log_frame.winfo_height() == expected_height
    assert logger.log_frame.winfo_height() > default_height
    root.destroy()


def test_log_window_shrinks_to_message_lines():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    logger.init_log_window(root)
    short_message = "short"
    messagebox.showinfo("Title", short_message)
    root.update_idletasks()
    display_lines = logger.log_widget.count("1.0", "end-1c", "displaylines")[0]
    expected_height = logger._line_height * display_lines
    assert logger.log_frame.winfo_height() == expected_height
    assert expected_height < logger._default_height
    root.destroy()


def test_log_window_resizes_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    app.toggle_explorer_pin()
    long_message = "Pinned panel message " * 40
    messagebox.showinfo("Title", long_message)
    root.update_idletasks()
    display_lines = logger.log_widget.count("1.0", "end-1c", "displaylines")[0]
    expected_height = logger._line_height * display_lines
    assert logger.log_frame.winfo_height() == expected_height
    root.destroy()
