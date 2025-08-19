import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from typing import Optional


def create_tool_button(master, text: str, command=None, icon: Optional[tk.PhotoImage] = None) -> ttk.Button:
    """Return a ttk.Button that sizes itself to fit *text* and icon.

    The button ensures its width and height are at least large enough to
    display both the icon and the text without clipping. A square shape is used
    as a minimum so icon-only buttons appear circular.
    """
    btn = ttk.Button(master, text=text, command=command)
    if icon is not None:
        btn.configure(image=icon, compound=tk.LEFT)

    def _resize() -> None:
        # Determine the pixel width/height the button requests
        btn.update_idletasks()
        req_w = btn.winfo_reqwidth()
        req_h = btn.winfo_reqheight()
        size = max(req_w, req_h)

        # Convert pixel dimensions to character units expected by ttk.Button
        try:
            font = tkfont.nametofont(btn.cget("font"))
            char_width = font.measure("0") or 1
            line_height = font.metrics("linespace") or 1
        except Exception:
            char_width = 7
            line_height = 15

        btn.configure(width=int((size / char_width) + 1))
        btn.configure(height=int((size / line_height) + 1))

    btn.after(0, _resize)
    return btn
