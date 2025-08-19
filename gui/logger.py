import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

log_widget = None
_line_widget = None
_log_frame = None
_toggle_button = None
_initial_height = 0

# Mapping of log levels to the tag name that will be used for colouring
_LEVEL_TAGS = {
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
}


def init_log_window(root, height=7, dark_mode: bool = True):
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

    global log_widget, _line_widget, _log_frame, _initial_height
    frame = ttk.Frame(root)
    frame.pack_propagate(False)
    font = tkfont.Font(root=root, family="Consolas", size=11)
    line_height = font.metrics("linespace")
    _initial_height = line_height * height
    frame.configure(height=_initial_height)
    _log_frame = frame

    # Choose colours based on the requested theme
    if dark_mode:
        bg = "#1e1e1e"
        fg = "#d4d4d4"
        line_fg = "white"
        info = "#569CD6"  # instruction blue
        warning = "#FFFF00"  # register yellow
        error = "#FF00FF"  # number magenta
    else:
        bg = "white"
        fg = "black"
        line_fg = "white"
        info = "#0066CC"
        warning = "#FFA500"
        error = "#CC0000"

    _line_widget = tk.Text(
        frame,
        width=4,
        padx=3,
        takefocus=0,
        border=0,
        background=bg,
        foreground=line_fg,
        state="disabled",
        font=font,
        height=height,
    )
    _line_widget.pack(side=tk.LEFT, fill=tk.Y)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    log_widget = tk.Text(
        frame,
        height=height,
        state="disabled",
        font=font,
        wrap="word",
        background=bg,
        foreground=fg,
        insertbackground=fg,
        yscrollcommand=lambda first, last: [scrollbar.set(first, last), _line_widget.yview_moveto(first)],
    )
    log_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=lambda *args: [log_widget.yview(*args), _line_widget.yview(*args)])
    _line_widget.configure(yscrollcommand=scrollbar.set)

    # Define tags for different log levels with appropriate colours
    log_widget.tag_configure("error", foreground=error)
    log_widget.tag_configure("warning", foreground=warning)
    log_widget.tag_configure("info", foreground=info)
    _update_line_numbers()
    return frame


def _update_line_numbers() -> None:
    """Refresh the line number column to match the log content."""
    if not log_widget or not _line_widget:
        return
    _line_widget.configure(state="normal")
    _line_widget.delete("1.0", tk.END)
    num_lines = int(log_widget.index("end-1c").split(".")[0])
    lines = "\n".join(str(i) for i in range(1, num_lines + 1))
    _line_widget.insert("1.0", lines)
    _line_widget.configure(state="disabled")


def log_message(message: str, level: str = "INFO") -> None:
    """Append *message* with *level* prefix to the log window."""
    if not log_widget:
        return
    log_widget.configure(state="normal")
    tag = _LEVEL_TAGS.get(level.upper(), "info")
    log_widget.insert(tk.END, f"[{level}] {message}\n", tag)
    log_widget.see(tk.END)
    log_widget.configure(state="disabled")
    _update_line_numbers()


def set_toggle_button(button) -> None:
    """Register the button used to manually toggle the log window."""
    global _toggle_button
    _toggle_button = button


def _is_visible() -> bool:
    return bool(_log_frame and _log_frame.winfo_manager())


def is_visible() -> bool:
    """Return ``True`` if the log window is currently displayed."""
    return _is_visible()


def show_logs() -> None:
    """Display the log window."""
    if not _log_frame or _is_visible():
        return
    _log_frame.configure(height=_initial_height)
    pack_kwargs = {"side": tk.BOTTOM, "fill": tk.X}
    if _toggle_button:
        pack_kwargs["before"] = _toggle_button
    _log_frame.pack(**pack_kwargs)
    if _toggle_button:
        _toggle_button.config(text="Hide Logs")


def hide_logs() -> None:
    """Hide the log window."""
    if not _log_frame or not _is_visible():
        return
    _log_frame.pack_forget()
    if _toggle_button:
        _toggle_button.config(text="Show Logs")


def _animate_hide(step: int = 10, delay: int = 15) -> None:
    if not _log_frame or not _is_visible():
        return
    h = _log_frame.winfo_height()
    if h <= 0:
        hide_logs()
        _log_frame.configure(height=_initial_height)
        return
    _log_frame.configure(height=max(0, h - step))
    _log_frame.after(delay, lambda: _animate_hide(step, delay))


def flash_log(duration: int = 3000) -> None:
    """Temporarily show the log window and hide it after *duration* ms."""
    if not _log_frame or _is_visible():
        return
    show_logs()
    _log_frame.after(duration, _animate_hide)
