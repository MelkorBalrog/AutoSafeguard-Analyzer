import tkinter as tk
from tkinter import ttk

log_widget = None
_log_line_numbers = None
_log_vscroll = None

# Mapping of log levels to the tag name that will be used for colouring
_LEVEL_TAGS = {
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
}


def init_log_window(root, height=3):
    """Create and return a log window packed in *root*.

    The log area now mirrors the dark themed assembly editor styling, using
    a monospaced font and matching foreground/background colours. Line
    numbers are displayed similar to the assembly editor. By default only
    three rows are shown to keep the log area compact.
    """
    global log_widget, _log_line_numbers, _log_vscroll
    frame = ttk.Frame(root)
    _log_line_numbers = tk.Text(
        frame,
        width=4,
        padx=3,
        takefocus=0,
        borderwidth=0,
        highlightthickness=0,
        state="disabled",
        font=("Consolas", 11),
        background="#1e1e1e",
        foreground="#d4d4d4",
    )
    log_widget = tk.Text(
        frame,
        height=height,
        state="disabled",
        font=("Consolas", 11),
        background="#1e1e1e",
        foreground="#d4d4d4",
        insertbackground="#d4d4d4",
        wrap="none",
    )
    _log_vscroll = ttk.Scrollbar(frame, orient="vertical", command=_on_log_scroll)
    log_widget.configure(yscrollcommand=_on_log_yview)
    _log_line_numbers.configure(yscrollcommand=_on_log_yview)
    # Define tags for different log levels with colours that fit the dark theme
    log_widget.tag_configure("error", foreground="#F44747")
    log_widget.tag_configure("warning", foreground="#FFFF00")
    log_widget.tag_configure("info", foreground="#569CD6")
    _log_line_numbers.grid(row=0, column=0, sticky="ns")
    log_widget.grid(row=0, column=1, sticky="nsew")
    _log_vscroll.grid(row=0, column=2, sticky="ns")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    return frame


def _on_log_scroll(*args) -> None:
    """Scroll log text and line numbers together."""
    log_widget.yview(*args)
    _log_line_numbers.yview(*args)


def _on_log_yview(*args) -> None:
    """Update scrollbar and line numbers when log widget scrolls."""
    _log_vscroll.set(*args)
    _log_line_numbers.yview_moveto(args[0])


def _update_log_line_numbers() -> None:
    """Refresh line numbers for the log text widget."""
    if not _log_line_numbers:
        return
    line_count = int(log_widget.index("end-1c").split(".")[0])
    numbers = "\n".join(str(i) for i in range(1, line_count + 1))
    _log_line_numbers.configure(state="normal")
    _log_line_numbers.delete("1.0", tk.END)
    if numbers:
        _log_line_numbers.insert("1.0", numbers)
    _log_line_numbers.configure(state="disabled")


def log_message(message: str, level: str = "INFO") -> None:
    """Append *message* with *level* prefix to the log window."""
    if not log_widget:
        return
    log_widget.configure(state="normal")
    tag = _LEVEL_TAGS.get(level.upper(), "info")
    log_widget.insert(tk.END, f"[{level}] {message}\n", tag)
    log_widget.see(tk.END)
    log_widget.configure(state="disabled")
    _update_log_line_numbers()
