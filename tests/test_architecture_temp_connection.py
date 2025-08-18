import tkinter as tk
import types

from gui.architecture import SysMLDiagramWindow, SysMLObject


def test_temp_connection_line_is_dotted_and_animated():
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.zoom = 1.0
    win.start = SysMLObject(1, "Block", 10, 20)
    win.temp_line_end = (50, 60)
    win.current_tool = "Association"
    win.selected_conn = None
    win.dragging_endpoint = None
    win.endpoint_drag_pos = None
    win.connections = []
    win.objects = []
    win.compartment_buttons = []
    win.gradient_cache = {}

    def edge_point(self, obj, tx, ty, rel=None, apply_radius=True):
        return obj.x * self.zoom, obj.y * self.zoom

    win.edge_point = types.MethodType(edge_point, win)

    class CanvasStub:
        def __init__(self):
            self.lines = []
            self.after_calls = 0
            self.last_dashoffset = None

        def configure(self, **kwargs):
            pass

        def delete(self, *args):
            pass

        def create_line(self, *args, **kwargs):
            self.lines.append(kwargs)
            return 1

        def tag_raise(self, *args):
            pass

        def config(self, **kwargs):
            pass

        def bbox(self, *args):
            return (0, 0, 0, 0)

        def find_withtag(self, tag):
            return [1] if tag == "_temp_conn" and self.lines else []

        def itemconfigure(self, *args, **kwargs):
            self.last_dashoffset = kwargs.get("dashoffset")

        def after(self, delay, func):
            self.after_calls += 1
            return "after_id"

        def after_cancel(self, _):
            pass

    win.canvas = CanvasStub()
    win.redraw()

    assert win.canvas.lines
    line_kwargs = win.canvas.lines[0]
    assert line_kwargs.get("dash") == (2, 2)
    assert line_kwargs.get("arrow") == tk.LAST
    assert win.canvas.after_calls == 1
    assert win.canvas.last_dashoffset == 2
