from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


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
        init_kwargs = {
            "width": width,
            "height": height,
            "highlightthickness": 0,
        }
        try:
            init_kwargs["bg"] = master.cget("background")
        except tk.TclError:
            pass
        init_kwargs.update(kwargs)
        super().__init__(master, **init_kwargs)
        self._command = command
        self._text = text
        self._normal_color = bg
        self._hover_color = hover_bg or _lighten(bg, 1.2)
        self._current_color = self._normal_color
        self._disabled = False
        self._disabled_color = _lighten(bg, 0.9)
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
        if not self._disabled:
            self._set_color(self._hover_color)

    def _on_leave(self, _event: tk.Event) -> None:
        if not self._disabled:
            self._set_color(self._normal_color)

    def _on_click(self, _event: tk.Event) -> None:
        if not self._disabled and self._command:
            self._command()

    # ------------------------------------------------------------------
    # ttk-compatible state handling
    # ------------------------------------------------------------------
    def state(self, states: Optional[list[str]] = None) -> list[str]:
        """Mimic :meth:`ttk.Button.state` for basic enable/disable support."""
        if not states:
            return ["disabled"] if self._disabled else ["!disabled"]
        if "disabled" in states:
            self._disabled = True
            self._set_color(self._disabled_color)
        if "!disabled" in states or "normal" in states:
            self._disabled = False
            self._set_color(self._normal_color)
        return ["disabled"] if self._disabled else ["!disabled"]

    def configure(self, **kwargs) -> None:  # pragma: no cover - thin wrapper
        """Allow dynamic configuration similar to standard Tk buttons."""
        text = kwargs.pop("text", None)
        if text is not None:
            self._text = text
            if self._text_item is not None:
                self.itemconfigure(self._text_item, text=self._text)
        command = kwargs.pop("command", None)
        if command is not None:
            self._command = command
        bg = kwargs.pop("bg", None)
        hover_bg = kwargs.pop("hover_bg", None)
        state = kwargs.pop("state", None)
        width = kwargs.get("width")
        height = kwargs.get("height")
        super().configure(**kwargs)
        if bg is not None:
            self._normal_color = bg
            self._hover_color = hover_bg or _lighten(bg, 1.2)
            self._set_color(self._normal_color)
            self._disabled_color = _lighten(bg, 0.9)
        if hover_bg is not None and bg is None:
            self._hover_color = hover_bg
        if state is not None:
            if isinstance(state, (list, tuple, set)):
                self.state(list(state))
            else:
                self.state([state])
        if width is not None or height is not None or text is not None:
            self._draw_button()

    config = configure

