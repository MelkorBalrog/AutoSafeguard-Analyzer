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


def test_on_release_creates_context_link():
    """Releasing in context mode should mark the relation accordingly."""
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    parent = GSNNode("p", "Goal")
    child = GSNNode("c", "Goal")
    win._connect_mode = "context"
    win._connect_parent = parent
    win.canvas = type("CanvasStub", (), {"delete": lambda self, *a, **k: None})()
    win._node_at = lambda x, y: child
    win.refresh = lambda: None
    event = type("Event", (), {"x": 0, "y": 0})
    win._on_release(event)
    assert child in parent.children
    assert child in parent.context_children


def test_refresh_updates_scrollregion():
    """Refresh should configure the canvas scrollregion."""
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.selected_node = None
    win.zoom = 1.0

    class DiagramStub:
        def _traverse(self):
            return []

        def draw(self, canvas, zoom):
            pass

    win.diagram = DiagramStub()

    class CanvasStub:
        def __init__(self):
            self.config = {}

        def delete(self, *a, **k):
            pass

        def bbox(self, tag):
            return (0, 0, 100, 100)

        def configure(self, **kwargs):
            self.config.update(kwargs)

        def create_rectangle(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    win.id_to_node = {}
    win.refresh()
    assert win.canvas.config.get("scrollregion") == (0, 0, 100, 100)
