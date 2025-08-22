import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gsn.nodes import GSNNode
from gsn.diagram import GSNDiagram

class StubCanvas:
    def __init__(self):
        self.items = []
    def create_rectangle(self, *args, **kwargs):
        self.items.append((args, kwargs))
    def create_arc(self, *args, **kwargs):
        self.items.append((args, kwargs))
    def create_text(self, *args, **kwargs):
        self.items.append((args, kwargs))
    def create_line(self, *args, **kwargs):
        self.items.append((args, kwargs))
    def bbox(self, tag):
        return None
    def tag_lower(self, *args, **kwargs):
        pass
    def tag_raise(self, *args, **kwargs):
        pass

class RecordingHelper:
    def __init__(self):
        self.calls = []
    def get_text_size(self, text, font_obj):
        return len(text) * 5, 10
    def draw_away_goal_shape(self, canvas, x, y, scale, text="", module_text="", font_obj=None, obj_id=""):
        self.calls.append(("goal", module_text))
    def draw_away_solution_shape(self, canvas, x, y, scale, text="", module_text="", font_obj=None, obj_id=""):
        self.calls.append(("solution", module_text))
    def draw_away_context_shape(self, canvas, x, y, scale, text="", module_text="", font_obj=None, obj_id=""):
        self.calls.append(("context", module_text))
    def draw_away_assumption_shape(self, canvas, x, y, scale, text="", module_text="", font_obj=None, obj_id=""):
        self.calls.append(("assumption", module_text))
    def draw_away_justification_shape(self, canvas, x, y, scale, text="", module_text="", font_obj=None, obj_id=""):
        self.calls.append(("justification", module_text))
    # Unused stubs
    def draw_goal_shape(self, *a, **k):
        pass
    def draw_solution_shape(self, *a, **k):
        pass
    def draw_module_shape(self, *a, **k):
        pass
    def draw_assumption_shape(self, *a, **k):
        pass
    def draw_justification_shape(self, *a, **k):
        pass
    def draw_context_shape(self, *a, **k):
        pass
    def draw_solved_by_connection(self, *a, **k):
        pass
    def draw_in_context_connection(self, *a, **k):
        pass
    def point_on_shape(self, shape, target_pt):
        return target_pt

@pytest.mark.parametrize("node_type,expected", [
    ("Goal", "goal"),
    ("Solution", "solution"),
    ("Context", "context"),
    ("Assumption", "assumption"),
    ("Justification", "justification"),
])
def test_away_shapes_receive_module_identifier(node_type, expected):
    module = GSNNode("Mod", "Module")
    original = GSNNode("Orig", node_type)
    original.parents.append(module)
    clone = GSNNode("Clone", node_type, is_primary_instance=False, original=original)
    helper = RecordingHelper()
    diag = GSNDiagram(clone, drawing_helper=helper)
    canvas = StubCanvas()
    diag.draw(canvas)
    assert helper.calls[0] == (expected, "Mod")
