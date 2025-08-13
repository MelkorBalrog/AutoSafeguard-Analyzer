import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gsn import GSNNode, GSNDiagram
from gui.drawing_helper import GSNDrawingHelper


class OffsetCanvas:
    def __init__(self):
        self.rects = {}

    def create_rectangle(self, left, top, right, bottom, tags=()):
        # Record rectangles so bbox() can return their extents.
        if tags:
            self.rects[tags[0]] = (left, top, right, bottom)

    # The diagram calls these no-op methods during rendering.
    def create_line(self, *a, **k):
        pass

    def create_text(self, *a, **k):
        pass

    def bbox(self, tag):
        return self.rects.get(tag)

    def tag_lower(self, *a, **k):
        pass

    def tag_raise(self, *a, **k):
        pass


class TrackingHelper(GSNDrawingHelper):
    """Helper that offsets shapes and records connector points."""

    def __init__(self, offsets=None):
        super().__init__()
        self.offsets = offsets or {}
        self.calls = []
        self.connection = None

    def draw_goal_shape(self, canvas, x, y, scale, text="", font_obj=None, obj_id=""):
        offset = self.offsets.get(obj_id, 0)
        half = scale / 2
        left = x - half + offset
        top = y - half
        right = x + half + offset
        bottom = y + half
        canvas.create_rectangle(left, top, right, bottom, tags=(obj_id,))

    # Reuse the simple rectangle for all node types used in the test.
    draw_strategy_shape = draw_solution_shape = draw_goal_shape
    draw_away_solution_shape = draw_goal_shape
    draw_away_goal_shape = draw_goal_shape
    draw_assumption_shape = draw_goal_shape
    draw_justification_shape = draw_goal_shape
    draw_context_shape = draw_goal_shape
    draw_module_shape = draw_goal_shape
    draw_away_module_shape = draw_goal_shape

    def point_on_shape(self, shape, target_pt):
        self.calls.append((shape["center"], target_pt))
        return super().point_on_shape(shape, target_pt)

    def draw_solved_by_connection(self, canvas, parent_pt, child_pt, obj_id=""):
        self.connection = (parent_pt, child_pt)


def test_connections_touch_shape_surface():
    parent = GSNNode("p", "Goal", x=0, y=0)
    child = GSNNode("c", "Goal", x=100, y=0)
    parent.add_child(child)

    offsets = {parent.unique_id: 0, child.unique_id: 10}
    helper = TrackingHelper(offsets)
    diag = GSNDiagram(parent, drawing_helper=helper)
    diag.add_node(child)

    canvas = OffsetCanvas()
    diag.draw(canvas)

    # point_on_shape should have been called with the centres of the
    # opposite shapes as the target points
    expected_child_center = (child.x + offsets[child.unique_id], child.y)
    expected_parent_center = (parent.x + offsets[parent.unique_id], parent.y)
    assert helper.calls[0][1] == expected_child_center
    assert helper.calls[1][1] == expected_parent_center

    # The connection points returned to draw_solved_by_connection should lie on
    # the surfaces of both rectangles regardless of the offset.
    assert helper.connection[0] == (30.0, 0.0)
    assert helper.connection[1] == (80.0, 0.0)

