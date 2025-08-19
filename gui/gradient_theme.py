import tkinter as tk

_TOP_COLOR = "#ADD8E6"
_BOTTOM_COLOR = "#FFFFFF"
_STRIP_COLOR = "#A0A0A0"
_STRIP_HEIGHT = 3


def _draw_gradient(canvas: tk.Canvas, width: int, height: int) -> None:
    steps = max(height - _STRIP_HEIGHT, 1)
    r1, g1, b1 = canvas.winfo_rgb(_TOP_COLOR)
    r2, g2, b2 = canvas.winfo_rgb(_BOTTOM_COLOR)
    r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
    r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256
    for i in range(steps):
        ratio = i / steps
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")
    canvas.create_rectangle(
        0,
        steps,
        width,
        height,
        outline="",
        fill=_STRIP_COLOR,
        tags="gradient",
    )
    canvas.lower("gradient")


def apply_gradient(win: tk.Misc) -> None:
    canvas = tk.Canvas(win, highlightthickness=0, borderwidth=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def _resize(event):
        canvas.delete("gradient")
        _draw_gradient(canvas, event.width, event.height)
    canvas.bind("<Configure>", _resize)
    win.update_idletasks()
    _draw_gradient(canvas, win.winfo_width(), win.winfo_height())


def install_gradient_theme() -> None:
    original_init = tk.Toplevel.__init__

    def _init_and_gradient(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        apply_gradient(self)

    tk.Toplevel.__init__ = _init_and_gradient
