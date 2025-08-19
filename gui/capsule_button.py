from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return '#%02x%02x%02x' % rgb


def _lighten(color: str, factor: float = 1.2) -> str:
    r, g, b = _hex_to_rgb(color)
    r = min(int(r * factor), 255)
    g = min(int(g * factor), 255)
    b = min(int(b * factor), 255)
    return _rgb_to_hex((r, g, b))


class CapsuleButton(tk.Canvas):
    """A capsule-shaped button that lightens on mouse hover.

    The button is drawn using canvas primitives so it does not rely on platform
    specific themes.  When the mouse cursor enters the button area the fill
    color is lightened to mimic the highlight effect of macOS buttons.
    """

    def __init__(
        self,
        master: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 80,
        height: int = 26,
        bg: str = "#e1e1e1",
        hover_bg: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bg=master.cget("background"),
            **kwargs,
        )
        self._command = command
        self._text = text
        self._normal_color = bg
        self._hover_color = hover_bg or _lighten(bg, 1.2)
        self._current_color = self._normal_color
        self._radius = height // 2
        self._shape_items: list[int] = []
        self._text_item: Optional[int] = None
        self._draw_button()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw_button(self) -> None:
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        r = self._radius
        color = self._current_color
        outline = "#b3b3b3"
        self._shape_items = [
            self.create_arc(
                (0, 0, 2 * r, h),
                start=90,
                extent=180,
                outline=outline,
                fill=color,
            ),
            self.create_rectangle((r, 0, w - r, h), outline=outline, fill=color),
            self.create_arc(
                (w - 2 * r, 0, w, h),
                start=-90,
                extent=180,
                outline=outline,
                fill=color,
            ),
        ]
        self._text_item = self.create_text(w // 2, h // 2, text=self._text)

    def _set_color(self, color: str) -> None:
        for item in self._shape_items:
            self.itemconfigure(item, fill=color)
        self._current_color = color

    def _on_enter(self, _event: tk.Event) -> None:
        self._set_color(self._hover_color)

    def _on_leave(self, _event: tk.Event) -> None:
        self._set_color(self._normal_color)

    def _on_click(self, _event: tk.Event) -> None:
        if self._command:
            self._command()
