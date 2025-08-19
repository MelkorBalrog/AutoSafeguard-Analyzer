import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Widgets and controls associated with the log area
log_widget = None
_line_widget = None
log_frame = None
_toggle_button = None

# Internal state tracking
_default_height = 0
_auto_hide_id = None

# Mapping of log levels to the tag name that will be used for colouring
_LEVEL_TAGS = {
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
}


def init_log_window(root, height=7, dark_mode: bool = True):
    """Create and return an un-packed styled log window in *root*.

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

    global log_widget, _line_widget, log_frame, _default_height
    frame = ttk.Frame(root)
    frame.pack_propagate(False)
    font = tkfont.Font(root=root, family="Consolas", size=11)
    line_height = font.metrics("linespace")
    _default_height = line_height * height
    frame.configure(height=_default_height)
    log_frame = frame

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


def set_toggle_button(button):
    """Register the toggle button that controls log visibility."""
    global _toggle_button
    _toggle_button = button


def show_log():
    """Display the log frame and update the toggle button text."""
    global _auto_hide_id
    if not log_frame or log_frame.winfo_manager():
        if log_frame and _auto_hide_id:
            log_frame.after_cancel(_auto_hide_id)
            _auto_hide_id = None
        return
    log_frame.configure(height=_default_height)
    # Pack the log frame below all other widgets so the toggle button
    # remains visible even when additional panels (like the explorer)
    # are pinned and consume vertical space.  By omitting the ``before``
    # argument the log frame is placed at the very bottom, leaving the
    # toggle button immediately above it.
    log_frame.pack(side=tk.BOTTOM, fill=tk.X)
    if _toggle_button:
        _toggle_button.config(text="Hide Logs")
    if _auto_hide_id:
        log_frame.after_cancel(_auto_hide_id)
        _auto_hide_id = None


def _animate_hide(height):
    """Recursively shrink the log frame height until hidden."""
    if height <= 0:
        log_frame.pack_forget()
        log_frame.configure(height=_default_height)
        if _toggle_button:
            _toggle_button.config(text="Show Logs")
        return
    log_frame.configure(height=height)
    log_frame.after(15, lambda: _animate_hide(height - max(_default_height // 10, 1)))


def hide_log(animate=False):
    """Hide the log frame, optionally with a slide-down animation."""
    global _auto_hide_id
    if not log_frame or not log_frame.winfo_manager():
        return
    if _auto_hide_id:
        log_frame.after_cancel(_auto_hide_id)
        _auto_hide_id = None
    if animate:
        _animate_hide(log_frame.winfo_height())
    else:
        log_frame.pack_forget()
        log_frame.configure(height=_default_height)
        if _toggle_button:
            _toggle_button.config(text="Show Logs")


def toggle_log():
    """Toggle the visibility of the log frame."""
    if log_frame and log_frame.winfo_manager():
        hide_log()
    else:
        show_log()


def show_temporarily(duration=3000):
    """Show the logs briefly before hiding them with animation."""
    global _auto_hide_id
    if not log_frame:
        return
    if not log_frame.winfo_manager():
        show_log()
        if _auto_hide_id:
            log_frame.after_cancel(_auto_hide_id)
        _auto_hide_id = log_frame.after(duration, lambda: hide_log(animate=True))


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
