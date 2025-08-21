import types

from AutoML import AutoMLApp


class DummyEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_drag_records_only_endpoints_and_undo_redo():
    app = AutoMLApp.__new__(AutoMLApp)
    app.zoom = 1.0
    app.grid_size = 1
    node = types.SimpleNamespace(
        x=0.0,
        y=0.0,
        node_type="Block",
        children=[],
        is_primary_instance=True,
    )
    app.root_node = node
    app.get_all_nodes = lambda root: [node]
    app.move_subtree = lambda n, dx, dy: None
    app.sync_nodes_by_id = lambda n: None
    app.redraw_canvas = lambda: None
    app._undo_stack = []
    app._redo_stack = []
    app.export_model_data = lambda include_versions=False: {
        "diagrams": [{"objects": [{"x": node.x, "y": node.y}]}]
    }
    app.apply_model_data = lambda data: (
        setattr(node, "x", data["diagrams"][0]["objects"][0]["x"]),
        setattr(node, "y", data["diagrams"][0]["objects"][0]["y"]),
    )
    app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
    app.undo = AutoMLApp.undo.__get__(app)
    app.redo = AutoMLApp.redo.__get__(app)
    app.on_canvas_click = AutoMLApp.on_canvas_click.__get__(app)
    app.on_canvas_drag = AutoMLApp.on_canvas_drag.__get__(app)
    app.on_canvas_release = AutoMLApp.on_canvas_release.__get__(app)
    app.canvas = types.SimpleNamespace(canvasx=lambda x: x, canvasy=lambda y: y)
    app.diagram_tabs = {}
    app.refresh_all = lambda: None

    app.on_canvas_click(DummyEvent(0, 0))
    app.on_canvas_drag(DummyEvent(10, 10))
    app.on_canvas_release(DummyEvent(10, 10))

    assert node.x == 10.0 and node.y == 10.0
    assert len(app._undo_stack) == 2

    app.undo()
    assert node.x == 0.0 and node.y == 0.0

    app.redo()
    assert node.x == 10.0 and node.y == 10.0
