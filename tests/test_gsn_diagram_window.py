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
            lines.append(kwargs.get("dash"))

        def delete(self, *args, **kwargs):
            pass

    win.canvas = CanvasStub()
    event = type("Event", (), {"x": 100, "y": 100})
    win._on_drag(event)
    assert lines and lines[0] == (2, 2)
