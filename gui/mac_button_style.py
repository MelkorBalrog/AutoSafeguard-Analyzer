from __future__ import annotations

from tkinter import ttk
import tkinter as tk


def apply_mac_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Configure ``ttk.Button`` widgets to mimic macOS transparent capsule buttons.

    Padding, borders and relief are adjusted for a rounded capsule look while
    using a transparent background so buttons blend with their surroundings.
    The style changes are applied to the passed ``ttk.Style`` instance. If no
    *style* is supplied a new instance is created.
    """
    style = style or ttk.Style()
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="flat",
        borderwidth=1,
        foreground="black",
    )

    try:
        style.configure("TButton", background="systemTransparent")
        bg_map = [("active", "systemTransparent"), ("pressed", "systemTransparent")]
    except tk.TclError:
        # Fall back to default backgrounds if transparency isn't supported
        style.configure("TButton", background="")
        bg_map = [("active", ""), ("pressed", "")]

    style.map(
        "TButton",
        background=bg_map,
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )
    return style
