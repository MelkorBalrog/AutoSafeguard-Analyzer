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


def init_log_window(root, height=8, dark_mode: bool = True):
    """Create and return a styled log window packed in *root*.

    Parameters
    ----------
    root:
        Parent widget in which the log window is created.
    height:
        Height of the ScrolledText widget.
    dark_mode:
        When ``True`` the widget uses the dark theme that matches the
        SynapseX assembly editor style. Otherwise a light theme is used.
    """

    global log_widget
    frame = ttk.Frame(root)

    # Choose colours based on the requested theme
    if dark_mode:
        bg = "#1e1e1e"
        fg = "#d4d4d4"
        info = "#569CD6"  # instruction blue
        warning = "#FFFF00"  # register yellow
        error = "#FF00FF"  # number magenta
    else:
        bg = "white"
        fg = "black"
        info = "#0066CC"
        warning = "#FFA500"
        error = "#CC0000"

    log_widget = ScrolledText(
        frame,
        height=height,
        state="disabled",
        font=("Consolas", 11),
        wrap="word",
        background=bg,
        foreground=fg,
        insertbackground=fg,
    )

    # Define tags for different log levels with appropriate colours
    log_widget.tag_configure("error", foreground=error)
    log_widget.tag_configure("warning", foreground=warning)
    log_widget.tag_configure("info", foreground=info)
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
