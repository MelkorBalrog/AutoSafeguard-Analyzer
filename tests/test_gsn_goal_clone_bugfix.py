import types

from gsn.nodes import GSNNode
from gsn.diagram import GSNDiagram
from AutoML import AutoMLApp


class StubCanvas:
    def create_rectangle(self, *a, **k):
        pass
    def create_text(self, *a, **k):
        pass
    def create_arc(self, *a, **k):
        pass
    def create_line(self, *a, **k):
        pass
    def create_polygon(self, *a, **k):
        pass
    def bbox(self, tag):
        return None
    def tag_lower(self, *a, **k):
        pass
    def tag_raise(self, *a, **k):
        pass


class RecordingHelper:
    def __init__(self):
        self.calls = []
    def get_text_size(self, text, font):
        return len(text) * 5, 10
    def draw_goal_shape(self, *a, **k):
        self.calls.append("goal")
    def draw_away_goal_shape(self, *a, **k):
        self.calls.append("away")
    def draw_solution_shape(self, *a, **k):
        pass
    def draw_away_solution_shape(self, *a, **k):
        pass
    def draw_module_shape(self, *a, **k):
        pass
    def draw_assumption_shape(self, *a, **k):
        pass
    def draw_justification_shape(self, *a, **k):
        pass
    def draw_context_shape(self, *a, **k):
        pass
    def draw_strategy_shape(self, *a, **k):
        pass
    def draw_solved_by_connection(self, *a, **k):
        pass
    def draw_in_context_connection(self, *a, **k):
        pass
    def point_on_shape(self, shape, target):
        return target


def test_goal_clones_render_away_and_move_independently():
    root = GSNNode("G", "Goal", x=0, y=0)
    helper = RecordingHelper()
    diag = GSNDiagram(root, drawing_helper=helper)
    clone1 = root.clone()
    clone2 = root.clone()
    clone1.x, clone1.y = 10, 20
    clone2.x, clone2.y = 30, 40
    diag.add_node(clone1)
    diag.add_node(clone2)
    canvas = StubCanvas()
    diag.draw(canvas)
    assert helper.calls.count("away") == 2
    app = object.__new__(AutoMLApp)
    def get_all_nodes(self, _):
        return [root, clone1, clone2]
    def get_all_fmea(self):
        return []
    app.root_node = root
    app.get_all_nodes = types.MethodType(get_all_nodes, app)
    app.get_all_fmea_entries = types.MethodType(get_all_fmea, app)
    clone1.x += 100
    clone1.y += 100
    AutoMLApp.sync_nodes_by_id(app, clone1)
    assert (root.x, root.y) == (0, 0)
    assert (clone2.x, clone2.y) == (30, 40)
