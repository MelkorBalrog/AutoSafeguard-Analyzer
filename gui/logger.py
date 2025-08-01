"""Simple Tkinter based logger used by the GUI application."""

import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox


class _LogWindow:
    """Bottom panel used to display log messages."""

    def __init__(self, master: tk.Misc):
        frame = tk.Frame(master)
        frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.text = ScrolledText(frame, height=6, state="disabled", wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True)
        # Define tags for each log level so messages get colored
        self.text.tag_config("INFO", foreground="blue")
        self.text.tag_config("WARNING", foreground="orange")
        self.text.tag_config("ERROR", foreground="red")
        self.text.tag_config("DEBUG", foreground="gray")
        self.text.tag_config("QUESTION", foreground="purple")

    def log(self, level: str, msg: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"[{level}] {msg}\n", level)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

_log_window: _LogWindow | None = None
_logger: logging.Logger | None = None

def init(master: tk.Misc) -> None:
    """Create the log window and wire up logging and message boxes."""
    global _log_window, _logger

    if _log_window:
        return

    _log_window = _LogWindow(master)

    class _TextHandler(logging.Handler):
        def __init__(self, widget: ScrolledText) -> None:
            super().__init__()
            self.widget = widget

        def emit(self, record: logging.LogRecord) -> None:
            msg = self.format(record)
            level = record.levelname
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, msg + "\n", level)
            self.widget.configure(state="disabled")
            self.widget.see(tk.END)

    _logger = logging.getLogger("AutoML")
    _logger.setLevel(logging.INFO)
    handler = _TextHandler(_log_window.text)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(handler)

    def _info(title: str, message: str, *_, **__):
        _logger.info(f"{title}: {message}")

    def _warn(title: str, message: str, *_, **__):
        _logger.warning(f"{title}: {message}")

    def _error(title: str, message: str, *_, **__):
        _logger.error(f"{title}: {message}")

    def _askyesno(title: str, message: str, *_, **__):
        _logger.info(f"{title}: {message} [auto-yes]")
        return True

    def _askyesnocancel(title: str, message: str, *_, **__):
        _logger.info(f"{title}: {message} [auto-yes]")
        return True

    messagebox.showinfo = _info
    messagebox.showwarning = _warn
    messagebox.showerror = _error
    messagebox.askyesno = _askyesno
    messagebox.askyesnocancel = _askyesnocancel


def info(msg: str) -> None:
    """Log an informational message."""
    if _logger:
        _logger.info(msg)


def warning(msg: str) -> None:
    """Log a warning message."""
    if _logger:
        _logger.warning(msg)


def error(msg: str) -> None:
    """Log an error message."""
    if _logger:
        _logger.error(msg)
