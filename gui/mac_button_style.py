from __future__ import annotations

from tkinter import ttk


def apply_mac_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Configure ``ttk.Button`` widgets with a transparent capsule look.

    The function removes the heavy relief and solid background so that buttons
    blend with their parent widget, similar to the translucent controls on
    macOS.  The style changes are applied to the passed ``ttk.Style`` instance.
    If no *style* is supplied a new instance is created.
    """
    style = style or ttk.Style()
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="flat",
        borderwidth=0,
        foreground="black",
        background="",
    )
    style.map(
        "TButton",
        background=[("active", "#d9d9d9"), ("pressed", "#c0c0c0")],
        relief=[("pressed", "flat"), ("!pressed", "flat")],
    )
    return style
