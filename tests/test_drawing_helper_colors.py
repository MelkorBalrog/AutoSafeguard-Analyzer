from gui.drawing_helper import GSNDrawingHelper


class DummyCanvas:
    """Minimal canvas stub capturing drawn lines."""

    def __init__(self):
        self.lines = []

    def create_line(self, x1, y1, x2, y2, fill=None):  # pragma: no cover - simple storage
        self.lines.append(fill)


def test_fill_gradient_rect_accepts_named_color():
    helper = GSNDrawingHelper()
    canvas = DummyCanvas()
    # Using a Tk-style color name previously triggered a ValueError
    helper._fill_gradient_rect(canvas, 0, 0, 4, 4, "lightyellow")
    assert canvas.lines  # some lines were drawn
    assert all(line.startswith("#") for line in canvas.lines)

