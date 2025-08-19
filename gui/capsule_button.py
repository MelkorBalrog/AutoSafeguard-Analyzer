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


def _darken(color: str, factor: float = 0.8) -> str:
    r, g, b = _hex_to_rgb(color)
    r = max(int(r * factor), 0)
    g = max(int(g * factor), 0)
    b = max(int(b * factor), 0)
    return _rgb_to_hex((r, g, b))


class CapsuleButton(tk.Canvas):
    """A capsule-shaped button that lightens on hover and appears recessed.

    The widget renders a rounded button using canvas primitives so it does not
    rely on platform specific themes.  A subtle dark/light border is drawn
    around the capsule to give the impression that the button sits inside a
    hole matching its shape.  When the mouse cursor enters the button area the
    fill colour is lightened to mimic a highlight effect.
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
        state: str | None = None,
        image: tk.PhotoImage | None = None,
        compound: str = tk.CENTER,
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
        # ``style`` and ``state`` are ttk-specific options.  Strip them from
        # ``kwargs`` before forwarding to ``Canvas.__init__`` and track the
        # ``state`` value ourselves.  ``image`` and ``compound`` are also Tk
        # button options which ``Canvas`` does not understand, so remove them
        # here and handle them manually.
        kwargs.pop("style", None)
        kwargs.pop("image", None)
        kwargs.pop("compound", None)
        init_kwargs.update(kwargs)
        super().__init__(master, **init_kwargs)
        self._state: set[str] = set()
        if state in {"disabled", tk.DISABLED}:  # type: ignore[arg-type]
            self._state.add("disabled")
        self._command = command
        self._text = text
        self._image = image
        self._compound = compound
        self._normal_color = bg
        self._hover_color = hover_bg or _lighten(bg, 1.2)
        self._pressed_color = _darken(bg, 0.8)
        self._current_color = self._normal_color
        self._radius = height // 2
        self._shape_items: list[int] = []
        self._shine_items: list[int] = []
        # Border items are split into dark and light segments to create a
        # recessed "hole" effect around the button outline.
        self._border_dark: list[int] = []
        self._border_light: list[int] = []
        self._text_item: Optional[int] = None
        self._image_item: Optional[int] = None
        self._draw_button()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        # Apply the initial state after the button has been drawn.
        self._apply_state()

    def _draw_button(self) -> None:
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        r = self._radius
        color = self._current_color
        outline = "#b3b3b3"
        # Draw the filled shapes without outlines so the seams between the
        # rectangle and arcs are not visible.
        self._shape_items = [
            self.create_arc(
                (0, 0, 2 * r, h),
                start=90,
                extent=180,
                style=tk.CHORD,
                outline="",
                fill=color,
            ),
            self.create_rectangle((r, 0, w - r, h), outline="", fill=color),
            self.create_arc(
                (w - 2 * r, 0, w, h),
                start=-90,
                extent=180,
                style=tk.CHORD,
                outline="",
                fill=color,
            ),
        ]
        highlight = _lighten(color, 1.4)
        self._shine_items = [
            self.create_oval(
                1,
                1,
                w - 1,
                h // 2,
                outline="",
                fill=highlight,
                stipple="gray25",
            )
        ]
        self._text_item = self.create_text(w // 2, h // 2, text=self._text)
        self._draw_border(w, h)

    def _draw_border(self, w: int, h: int) -> None:
        """Draw dark/light border to mimic an inset capsule."""
        r = self._radius
        dark = _darken(self._current_color, 0.8)
        light = _lighten(self._current_color, 1.2)
        # Dark top/left edges
        self._border_dark = [
            self.create_arc((0, 0, 2 * r, h), start=90, extent=180, style=tk.ARC, outline=dark, width=2),
            self.create_line(r, 0, w - r, 0, fill=dark, width=2),
            self.create_line(0, r, 0, h - r, fill=dark, width=2),
        ]
        # Light bottom/right edges
        self._border_light = [
            self.create_arc((w - 2 * r, 0, w, h), start=-90, extent=180, style=tk.ARC, outline=light, width=2),
            self.create_line(r, h, w - r, h, fill=light, width=2),
            self.create_line(w, r, w, h - r, fill=light, width=2),
        ]

    def _set_color(self, color: str) -> None:
        for item in self._shape_items:
            self.itemconfigure(item, fill=color)
        highlight = _lighten(color, 1.4)
        for item in self._shine_items:
            self.itemconfigure(item, fill=highlight)
        dark = _darken(color, 0.8)
        light = _lighten(color, 1.2)
        self._apply_border_color(self._border_dark, dark)
        self._apply_border_color(self._border_light, light)
        self._current_color = color

    def _apply_border_color(self, items: list[int], color: str) -> None:
        for item in items:
            if self.type(item) == "line":
                self.itemconfigure(item, fill=color)
            else:
                self.itemconfigure(item, outline=color)

    def _on_enter(self, _event: tk.Event) -> None:
        if "disabled" not in self._state:
            self._set_color(self._hover_color)

    def _on_leave(self, _event: tk.Event) -> None:
        if "disabled" not in self._state:
            self._set_color(self._normal_color)

    def _on_press(self, _event: tk.Event) -> None:
        if "disabled" not in self._state:
            self._set_color(self._pressed_color)

    def _on_release(self, event: tk.Event) -> None:
        if "disabled" in self._state:
            return
        if self.winfo_containing(event.x_root, event.y_root) == self:
            self._set_color(self._hover_color)
            if self._command:
                self._command()
        else:
            self._set_color(self._normal_color)

    def _apply_state(self) -> None:
        """Update the visual appearance to reflect the current state."""
        if "disabled" in self._state:
            # A light gray color roughly matching ttk's disabled buttons
            self._set_color("#d9d9d9")
        else:
            self._set_color(self._normal_color)

    def configure(self, **kwargs) -> None:  # pragma: no cover - thin wrapper
        """Allow dynamic configuration similar to standard Tk buttons."""
        text = kwargs.pop("text", None)
        command = kwargs.pop("command", None)
        bg = kwargs.pop("bg", None)
        hover_bg = kwargs.pop("hover_bg", None)
        image = kwargs.pop("image", None)
        compound = kwargs.pop("compound", None)
        width = kwargs.get("width")
        height = kwargs.get("height")
        state = kwargs.pop("state", None)
        kwargs.pop("style", None)
        super().configure(**kwargs)
        self._update_command(command)
        self._update_text(text)
        self._update_colors(bg, hover_bg)
        self._update_geometry(width, height, text)
        self._update_state(state)
        # Always re-apply the current state so that disabled buttons retain
        # their disabled appearance even after reconfiguration.
        self._apply_state()

    config = configure

    def _update_command(self, command: Optional[Callable[[], None]]) -> None:
        if command is not None:
            self._command = command

    def _update_text(self, text: Optional[str]) -> None:
        if text is None:
            return
        self._text = text
        if self._text_item is not None:
            self.itemconfigure(self._text_item, text=self._text)

    def _update_colors(self, bg: Optional[str], hover_bg: Optional[str]) -> None:
        if bg is not None:
            self._normal_color = bg
            self._hover_color = hover_bg or _lighten(bg, 1.2)
            self._pressed_color = _darken(bg, 0.8)
            self._set_color(self._normal_color)
        elif hover_bg is not None:
            self._hover_color = hover_bg

    def _update_geometry(
        self, width: Optional[int], height: Optional[int], text: Optional[str]
    ) -> None:
        if width is not None or height is not None or text is not None:
            self._draw_button()

    def _update_state(self, state: Optional[str]) -> None:
        if state is None:
            return
        if state in ("disabled", tk.DISABLED):  # type: ignore[arg-type]
            self.state(["disabled"])
        else:
            self.state(["!disabled"])

    def state(self, states: list[str] | tuple[str, ...] | None = None) -> list[str]:
        """Mimic the ``ttk.Widget.state`` method for simple disabled handling."""
        if states is None:
            return list(self._state)
        for s in states:
            if s.startswith("!"):
                self._state.discard(s[1:])
            else:
                self._state.add(s)
        self._apply_state()
        return list(self._state)