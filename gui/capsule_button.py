from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional
import tkinter.font as tkfont


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
        width: int | None = None,
        height: int | None = None,
        bg: str = "#e1e1e1",
        hover_bg: Optional[str] = None,
        state: str | None = None,
        image: tk.PhotoImage | None = None,
        compound: str = tk.CENTER,
        padx: int = 10,
        pady: int = 5,
        **kwargs,
    ) -> None:
        init_kwargs = {
            "width": width or 80,
            "height": height or 26,
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
        self._padx = padx
        self._pady = pady
        self._normal_color = bg
        self._hover_color = hover_bg or _lighten(bg, 1.2)
        self._pressed_color = _darken(bg, 0.8)
        self._current_color = self._normal_color
        self._radius = (height or 26) // 2
        self._shape_items: list[int] = []
        self._shine_items: list[int] = []
        self._text_item: Optional[int] = None
        self._image_item: Optional[int] = None
        self._draw_button(width, height)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        # Apply the initial state after the button has been drawn.
        self._apply_state()

    def _compute_size(self, width: int | None, height: int | None) -> tuple[int, int]:
        """Return canvas dimensions accommodating text and image."""
        font = tkfont.nametofont("TkDefaultFont")
        text_w = font.measure(self._text) if self._text else 0
        text_h = font.metrics("linespace") if self._text else 0
        img_w = self._image.width() if self._image else 0
        img_h = self._image.height() if self._image else 0
        spacing = 4 if self._text and self._image and self._compound != tk.CENTER else 0
        if self._compound in (tk.LEFT, tk.RIGHT):
            content_w = text_w + img_w + spacing
            content_h = max(text_h, img_h)
        elif self._compound in (tk.TOP, tk.BOTTOM):
            content_w = max(text_w, img_w)
            content_h = text_h + img_h + spacing
        else:
            content_w = max(text_w, img_w)
            content_h = max(text_h, img_h)
        w = max(width or 0, content_w + 2 * self._padx)
        h = max(height or 0, content_h + 2 * self._pady)
        return w, h

    def _draw_button(self, width: int | None = None, height: int | None = None) -> None:
        self.delete("all")
        w, h = self._compute_size(width, height)
        super().configure(width=w, height=h)
        r = h // 2
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
        # Single outline surrounding the entire button for a smooth border
        self.create_arc(
            (0, 0, 2 * r, h),
            start=90,
            extent=180,
            style=tk.ARC,
            outline=outline,
        )
        self.create_line(r, 0, w - r, 0, fill=outline)
        self.create_line(r, h, w - r, h, fill=outline)
        self.create_arc(
            (w - 2 * r, 0, w, h),
            start=-90,
            extent=180,
            style=tk.ARC,
            outline=outline,
        )
        self._text_item = self._image_item = None
        font = tkfont.nametofont("TkDefaultFont")
        text_w = font.measure(self._text) if self._text else 0
        text_h = font.metrics("linespace") if self._text else 0
        img_w = self._image.width() if self._image else 0
        img_h = self._image.height() if self._image else 0
        spacing = 4 if self._text and self._image and self._compound != tk.CENTER else 0
        if self._compound == tk.LEFT:
            start_x = (w - (img_w + spacing + text_w)) // 2
            if self._image:
                self._image_item = self.create_image(start_x + img_w / 2, h / 2, image=self._image)
                start_x += img_w + spacing
            if self._text:
                self._text_item = self.create_text(start_x + text_w / 2, h / 2, text=self._text)
        elif self._compound == tk.RIGHT:
            start_x = (w - (text_w + spacing + img_w)) // 2
            if self._text:
                self._text_item = self.create_text(start_x + text_w / 2, h / 2, text=self._text)
                start_x += text_w + spacing
            if self._image:
                self._image_item = self.create_image(start_x + img_w / 2, h / 2, image=self._image)
        elif self._compound == tk.TOP:
            start_y = (h - (img_h + spacing + text_h)) // 2
            if self._image:
                self._image_item = self.create_image(w / 2, start_y + img_h / 2, image=self._image)
                start_y += img_h + spacing
            if self._text:
                self._text_item = self.create_text(w / 2, start_y + text_h / 2, text=self._text)
        elif self._compound == tk.BOTTOM:
            start_y = (h - (text_h + spacing + img_h)) // 2
            if self._text:
                self._text_item = self.create_text(w / 2, start_y + text_h / 2, text=self._text)
                start_y += text_h + spacing
            if self._image:
                self._image_item = self.create_image(w / 2, start_y + img_h / 2, image=self._image)
        else:  # CENTER
            if self._image:
                self._image_item = self.create_image(w / 2, h / 2, image=self._image)
            if self._text:
                self._text_item = self.create_text(w / 2, h / 2, text=self._text)

    def _set_color(self, color: str) -> None:
        for item in self._shape_items:
            self.itemconfigure(item, fill=color)
        highlight = _lighten(color, 1.4)
        for item in self._shine_items:
            self.itemconfigure(item, fill=highlight)
        self._current_color = color

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
        width = kwargs.pop("width", None)
        height = kwargs.pop("height", None)
        padx = kwargs.pop("padx", None)
        pady = kwargs.pop("pady", None)
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
        if image is not None:
            self._image = image
        if compound is not None:
            self._compound = compound
        if padx is not None:
            self._padx = padx
        if pady is not None:
            self._pady = pady
        if width is not None or height is not None or text is not None or image is not None or compound is not None or padx is not None or pady is not None:
            self._draw_button(width, height)
        # Always re-apply the current state so that disabled buttons retain
        # their disabled appearance even after reconfiguration.
        self._apply_state()

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