import tkinter as tk

from gui.gsn_diagram_window import GSNDiagramWindow
from gsn import GSNNode


def test_gsn_diagram_window_button_labels():
    labels = GSNDiagramWindow.TOOLBOX_BUTTONS
    assert "Goal" in labels
    assert "Solved By" in labels
    assert "In Context Of" in labels
    assert "Zoom In" in labels


def test_zoom_methods_adjust_factor():
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.zoom = 1.0
    win.refresh = lambda: None
    GSNDiagramWindow.zoom_in(win)
    assert win.zoom > 1.0
    GSNDiagramWindow.zoom_out(win)
    assert abs(win.zoom - 1.0) < 1e-6


def test_temp_connection_line_is_dotted():
    """Dragging in connect mode should draw a dotted preview line."""
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.zoom = 1.0
    win._connect_mode = "solved"
    win._connect_parent = GSNNode("p", "Goal", x=10, y=20)
    win._drag_node = None
    lines = []

    class CanvasStub:
        def create_line(self, *args, **kwargs):
            lines.append(kwargs)

        def delete(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    event = type("Event", (), {"x": 100, "y": 100})
    win._on_drag(event)
    assert lines and lines[0].get("dash") == (2, 2)
    assert lines[0].get("arrow") == tk.LAST


def test_temp_connection_line_no_arrow_in_context_mode():
    """Context connections preview without an arrow."""
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.zoom = 1.0
    win._connect_mode = "context"
    win._connect_parent = GSNNode("p", "Goal", x=10, y=20)
    win._drag_node = None
    lines = []

    class CanvasStub:
        def create_line(self, *args, **kwargs):
            lines.append(kwargs)

        def delete(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    event = type("Event", (), {"x": 50, "y": 50})
    win._on_drag(event)
    assert lines and lines[0].get("dash") == (2, 2)
    assert not lines[0].get("arrow")


def test_drag_creates_solved_by_connection():
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    parent = GSNNode("p", "Goal", x=10, y=20)
    child = GSNNode("c", "Goal", x=30, y=40)
    diag = type("Diag", (), {})()  # simple stub
    diag._traverse = lambda: [parent, child]
    win.diagram = diag
    win.zoom = 1.0
    win.selected_node = parent
    win.id_to_node = {n.unique_id: n for n in diag._traverse()}

    class CanvasStub:
        def create_line(self, *args, **kwargs):
            pass

        def delete(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    win.refresh = lambda: None
    win._node_at = lambda x, y: child

    win.connect_solved_by()
    event = type("Event", (), {"x": child.x, "y": child.y})
    win._on_drag(event)
    win._on_release(event)
    assert child in parent.children


def test_drag_creates_context_connection():
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    parent = GSNNode("p", "Goal", x=10, y=20)
    ctx = GSNNode("c", "Context", x=30, y=40)
    diag = type("Diag", (), {})()
    diag._traverse = lambda: [parent, ctx]
    win.diagram = diag
    win.zoom = 1.0
    win.selected_node = parent
    win.id_to_node = {n.unique_id: n for n in diag._traverse()}

    class CanvasStub:
        def create_line(self, *args, **kwargs):
            pass

        def delete(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    win.refresh = lambda: None
    win._node_at = lambda x, y: ctx

    win.connect_in_context()
    event = type("Event", (), {"x": ctx.x, "y": ctx.y})
    win._on_drag(event)
    win._on_release(event)
    assert ctx in parent.children
