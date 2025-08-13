import types

from gsn import GSNNode, GSNDiagram


class StubCanvas:
    def __init__(self):
        self.items = []

    def create_rectangle(self, left, top, right, bottom, **kw):  # pragma: no cover - simple storage
        self.items.append((left, top, right, bottom, kw))

    def create_line(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass

    def create_text(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass

    def tag_lower(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass

    def tag_raise(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass


class ColorHelper:
    def draw_goal_shape(self, canvas, x, y, scale, obj_id="", **kw):  # pragma: no cover - basic rectangle
        left = x - scale / 2
        top = y - scale / 2
        right = x + scale / 2
        bottom = y + scale / 2
        canvas.create_rectangle(left, top, right, bottom, tags=(obj_id,), **kw)

    draw_strategy_shape = draw_goal_shape
    draw_solution_shape = draw_goal_shape
    draw_away_solution_shape = draw_goal_shape
    draw_away_goal_shape = draw_goal_shape
    draw_assumption_shape = draw_goal_shape
    draw_justification_shape = draw_goal_shape
    draw_context_shape = draw_goal_shape
    draw_module_shape = draw_goal_shape
    draw_away_module_shape = draw_goal_shape

    def draw_solved_by_connection(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass

    def draw_in_context_connection(self, *args, **kwargs):  # pragma: no cover - placeholder
        pass

    def point_on_shape(self, shape, target_pt):  # pragma: no cover - straight through
        return target_pt

    def get_text_size(self, text, font_obj):  # pragma: no cover - simple approximation
        lines = text.split("\n")
        width = max(len(l) for l in lines) * 5
        height = 10 * len(lines)
        return width, height


def _kw_for(node_id, canvas):
    for _, _, _, _, kw in canvas.items:
        if kw.get("tags") == (node_id,):
            return kw
    raise KeyError(node_id)


def test_solution_spi_colors():
    root = GSNNode("Root", "Goal", x=0, y=0)
    pos = GSNNode("P", "Solution", x=10, y=10)
    neg = GSNNode("N", "Solution", x=30, y=10)
    pos.spi_target = "Pos"
    neg.spi_target = "Neg"
    root.add_child(pos)
    root.add_child(neg)
    helper = ColorHelper()
    diag = GSNDiagram(root, drawing_helper=helper)
    diag.add_node(pos)
    diag.add_node(neg)

    class TopEvent:
        def __init__(self, name, validation_target, probability):
            self.validation_desc = name
            self.validation_target = validation_target
            self.probability = probability

    app = types.SimpleNamespace(
        top_events=[
            TopEvent("Pos", "1e-5", "1e-6"),
            TopEvent("Neg", "1e-5", "1e-4"),
        ]
    )
    diag.app = app

    canvas = StubCanvas()
    diag.draw(canvas, zoom=1.0)

    pos_kw = _kw_for(pos.unique_id, canvas)
    neg_kw = _kw_for(neg.unique_id, canvas)
    assert pos_kw["fill"] == "#ADD8E6"
    assert neg_kw["fill"] == "orange"

