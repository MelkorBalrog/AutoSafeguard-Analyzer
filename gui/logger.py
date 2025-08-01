import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

log_widget = None

# Mapping of log levels to the tag name that will be used for colouring
_LEVEL_TAGS = {
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
}


def init_log_window(root, height=8):
    """Create and return a log window packed in *root*."""
    global log_widget
    frame = ttk.Frame(root)
    log_widget = ScrolledText(frame, height=height, state="disabled", font=("Arial", 9))
    # Define tags for different log levels with appropriate colours
    log_widget.tag_configure("error", foreground="red")
    log_widget.tag_configure("warning", foreground="orange")
    log_widget.tag_configure("info", foreground="blue")
    log_widget.pack(fill=tk.BOTH, expand=True)
    return frame


def log_message(message: str, level: str = "INFO") -> None:
    """Append *message* with *level* prefix to the log window."""
    if not log_widget:
        return
    log_widget.configure(state="normal")
    tag = _LEVEL_TAGS.get(level.upper(), "info")
    log_widget.insert(tk.END, f"[{level}] {message}\n", tag)
    log_widget.see(tk.END)
    log_widget.configure(state="disabled")
