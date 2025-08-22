import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.drawing_helper import GSNDrawingHelper


class DummyFont:
    def measure(self, text):
        return len(text) * 5

    def metrics(self, *args, **kwargs):
        return {"linespace": 10}


class StubCanvas:
    def __init__(self):
        self.ops = []
    def create_rectangle(self, *args, **kwargs):
        self.ops.append(("rect", args, kwargs))
    def create_line(self, *args, **kwargs):
        self.ops.append(("line", args, kwargs))
    def create_arc(self, *args, **kwargs):
        self.ops.append(("arc", args, kwargs))
    def create_polygon(self, *args, **kwargs):
        self.ops.append(("poly", args, kwargs))
    def create_text(self, *args, **kwargs):
        self.ops.append(("text", args, kwargs))
    def bbox(self, tag):
        return (0, 0, 60, 36)

helper = GSNDrawingHelper()
helper._scaled_font = lambda scale: DummyFont()
helper.get_text_size = lambda text, font: (len(text) * 5, 10)

@pytest.mark.parametrize(
    "func,feature",
    [
        (helper.draw_away_goal_shape, "line"),
        (helper.draw_away_solution_shape, "arc"),
        (helper.draw_away_context_shape, "arc"),
        (helper.draw_away_assumption_shape, "arc"),
        (helper.draw_away_justification_shape, "arc"),
    ],
)
def test_away_shapes_draw_module_box(func, feature):
    canvas = StubCanvas()
    func(canvas, 50, 50, scale=60, text="T", module="M1", obj_id="n1", font_obj=DummyFont())
    assert any(op[0] == "text" and op[2].get("text") == "M1" for op in canvas.ops)
    assert any(op[0] == feature for op in canvas.ops)
    assert any(op[0] == "poly" for op in canvas.ops)

@pytest.mark.parametrize(
    "prefix,count",
    [
        ("_draw_away_goal_shape_strategy", 4),
        ("_draw_away_solution_shape_strategy", 4),
        ("_draw_away_context_shape_strategy", 4),
        ("_draw_away_assumption_shape_strategy", 4),
        ("_draw_away_justification_shape_strategy", 4),
    ],
)
def test_all_strategy_variants_draw_module(prefix, count):
    for i in range(1, count + 1):
        canvas = StubCanvas()
        func = getattr(helper, f"{prefix}{i}")
        func(canvas, 50, 50, scale=60, text="T", module="M1", obj_id="n1", font_obj=DummyFont())
        assert any(op[0] == "text" and op[2].get("text") == "M1" for op in canvas.ops)
        assert any(op[0] == "poly" for op in canvas.ops)
