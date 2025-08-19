from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_mac_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Configure ``ttk.Button`` widgets to mimic macOS capsule buttons.

    The function adjusts padding, border and relief to give buttons a rounded
    3D appearance that resembles native macOS controls.  The style changes are
    applied to the passed ``ttk.Style`` instance.  If no *style* is supplied a
    new instance is created.
    """
    style = style or ttk.Style()
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="raised",
        borderwidth=1,
        foreground="black",
        background="#e1e1e1",
    )
    style.map(
        "TButton",
        background=[("active", "#f5f5f5"), ("pressed", "#d9d9d9")],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )
    return style


def apply_purplish_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Style buttons with a purple theme for message boxes."""

    style = style or ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Purple.TButton",
        padding=(10, 5),
        relief="raised",
        borderwidth=1,
        foreground="white",
        background="#9b59b6",
    )
    style.map(
        "Purple.TButton",
        background=[("active", "#b37cc8"), ("pressed", "#8e44ad")],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )
    return style


def apply_translucid_button_style(style: ttk.Style | None = None) -> ttk.Style:
    """Style the default ``ttk.Button`` with a subtle, translucent look."""

    style = style or ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "TButton",
        padding=(10, 5),
        relief="flat",
        borderwidth=1,
        foreground="black",
        background="#ffffff",
    )
    style.map(
        "TButton",
        background=[("active", "#f0f0f0"), ("pressed", "#e0e0e0")],
        relief=[("pressed", "sunken"), ("!pressed", "flat")],
    )
    return style
