import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

class _LogWindow:
    """Simple text widget for application logs."""

    def __init__(self, master: tk.Misc):
        frame = tk.Frame(master)
        frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.text = ScrolledText(frame, height=6, state="disabled", wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.tag_config("INFO", foreground="blue")
        self.text.tag_config("WARNING", foreground="orange")
        self.text.tag_config("ERROR", foreground="red")
        self.text.tag_config("QUESTION", foreground="purple")

    def log(self, level: str, msg: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"[{level}] {msg}\n", level)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

_log_window: _LogWindow | None = None

def init(master: tk.Misc) -> None:
    """Create the log window and redirect common messagebox calls."""
    global _log_window
    _log_window = _LogWindow(master)

    def _info(title: str, message: str, *_, **__):
        _log_window.log("INFO", f"{title}: {message}")

    def _warn(title: str, message: str, *_, **__):
        _log_window.log("WARNING", f"{title}: {message}")

    def _error(title: str, message: str, *_, **__):
        _log_window.log("ERROR", f"{title}: {message}")

    def _askyesno(title: str, message: str, *_, **__):
        _log_window.log("QUESTION", f"{title}: {message} [auto-yes]")
        return True

    def _askyesnocancel(title: str, message: str, *_, **__):
        _log_window.log("QUESTION", f"{title}: {message} [auto-yes]")
        return True

    messagebox.showinfo = _info
    messagebox.showwarning = _warn
    messagebox.showerror = _error
    messagebox.askyesno = _askyesno
    messagebox.askyesnocancel = _askyesnocancel
