import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gui.drawing_helper import GSNDrawingHelper


class DummyCanvas:
    def __init__(self):
        self.text_calls = []

    def create_rectangle(self, *a, **k):
        pass

    def create_polygon(self, *a, **k):
        pass

    def create_oval(self, *a, **k):
        pass

    def create_line(self, *a, **k):
        pass

    def create_text(self, *a, **k):
        self.text_calls.append(k)


def test_goal_text_has_obj_id_tag(monkeypatch):
    canvas = DummyCanvas()
    helper = GSNDrawingHelper()

    class DummyFont:
        def measure(self, _):
            return 10

        def metrics(self, _):
            return 10

    monkeypatch.setattr("gui.drawing_helper.tkFont.Font", lambda *a, **k: DummyFont())

    helper.draw_goal_shape(canvas, 0, 0, text="Goal", obj_id="nid")
    assert any(call.get("tags") == ("nid",) for call in canvas.text_calls)
