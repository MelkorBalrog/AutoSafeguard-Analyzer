import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import (
    _BOTTOM_LABEL_TYPES,
    GovernanceDiagramWindow,
    SysMLRepository,
    SysMLObject,
)


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


def test_governance_names_after_shape():
    for obj_type in ("Organization", "Model", "Business Unit"):
        assert obj_type in _BOTTOM_LABEL_TYPES


def test_bottom_label_shapes_fixed_size():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.zoom = 1.0
    win.canvas = DummyCanvas()
    win.start = None
    win.current_tool = "Select"
    win.select_rect_start = None
    win.dragging_endpoint = None
    win.selected_conn = None
    win.dragging_point_index = None
    win.conn_drag_offset = None
    for obj_type in ("Organization", "Model", "Business Unit"):
        obj = SysMLObject(
            1,
            obj_type,
            0.0,
            0.0,
            width=80.0,
            height=40.0,
            properties={"name": obj_type},
        )
        win.objects = [obj]
        win.selected_obj = obj
        assert win.hit_resize_handle(obj, 0.0, 0.0) is None
        win.resizing_obj = obj
        win.resize_edge = "se"
        event = types.SimpleNamespace(x=100, y=100)
        win.on_left_drag(event)
        assert obj.width == 80.0
        assert obj.height == 40.0
