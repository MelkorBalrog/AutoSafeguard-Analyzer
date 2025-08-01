import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

log_widget = None


def init_log_window(root, height=8):
    """Create and return a log window packed in *root*."""
    global log_widget
    frame = ttk.Frame(root)
    log_widget = ScrolledText(frame, height=height, state="disabled", font=("Arial", 9))
    log_widget.pack(fill=tk.BOTH, expand=True)
    return frame


def log_message(message: str, level: str = "INFO") -> None:
    """Append *message* with *level* prefix to the log window."""
    if not log_widget:
        return
    log_widget.configure(state="normal")
    log_widget.insert(tk.END, f"[{level}] {message}\n")
    log_widget.see(tk.END)
    log_widget.configure(state="disabled")
