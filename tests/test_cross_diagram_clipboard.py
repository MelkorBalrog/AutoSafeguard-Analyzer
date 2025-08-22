import types


import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from gui.architecture import SysMLDiagramWindow, _get_next_id, SysMLObject, ARCH_WINDOWS


class DummyRepo:
    def __init__(self, diag1_type, diag2_type):
        self.diagrams = {
            1: types.SimpleNamespace(diag_type=diag1_type, elements=[]),
            2: types.SimpleNamespace(diag_type=diag2_type, elements=[]),
        }

    def diagram_read_only(self, _id):
        return False


def make_window(app, repo, diagram_id):
    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.app = app
    win.repo = repo
    win.diagram_id = diagram_id
    win.selected_obj = None
    win.objects = []
    win.remove_object = lambda o: win.objects.remove(o)
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.update_property_view = lambda: None
    win.sort_objects = lambda: None
    win.refresh_from_repository = lambda e=None: None
    win._on_focus_in = types.MethodType(SysMLDiagramWindow._on_focus_in, win)
    win._constrain_to_parent = lambda obj, parent: None
    def _stub_place_process_area(name, x, y):
        area = SysMLObject(
            obj_id=_get_next_id(),
            obj_type="System Boundary",
            x=x,
            y=y,
            element_id=None,
            width=80,
            height=40,
            properties={"name": name},
            requirements=[],
            locked=False,
            hidden=False,
            collapsed={},
        )
        win.objects.append(area)
        return area

    win._place_process_area = _stub_place_process_area
    win._rebuild_toolboxes = lambda: None
    return win


def test_copy_paste_between_same_type_diagrams():
    ARCH_WINDOWS.clear()
    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_clipboard = None
    app.diagram_clipboard_type = None
    app.selected_node = None
    app.root_node = None
    app.clipboard_node = None
    app.cut_mode = False
    repo = DummyRepo("Governance Diagram", "Governance Diagram")

    obj = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="Plan",
        x=0,
        y=0,
        element_id=None,
        width=80,
        height=40,
        properties={},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )

    win1 = make_window(app, repo, 1)
    win1.selected_obj = obj
    win1.objects = [obj]

    win2 = make_window(app, repo, 2)

    win1._on_focus_in()
    app.copy_node()
    assert app.diagram_clipboard is not None

    win2._on_focus_in()
    app.paste_node()

    assert len(win2.objects) == 1
    assert win2.objects[0] is not obj


def test_copy_paste_task_between_governance_diagrams():
    ARCH_WINDOWS.clear()
    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_clipboard = None
    app.diagram_clipboard_type = None
    app.selected_node = None
    app.root_node = None
    app.clipboard_node = None
    app.cut_mode = False
    repo = DummyRepo("Governance Diagram", "Governance Diagram")

    boundary1 = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="System Boundary",
        x=0,
        y=0,
        element_id=None,
        width=80,
        height=40,
        properties={"name": "Area"},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    task = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="Task",
        x=10,
        y=10,
        element_id=None,
        width=80,
        height=40,
        properties={"boundary": str(boundary1.obj_id)},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )

    win1 = make_window(app, repo, 1)
    win1.objects = [boundary1, task]
    win1.selected_obj = task

    boundary2 = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="System Boundary",
        x=0,
        y=0,
        element_id=None,
        width=80,
        height=40,
        properties={"name": "Area"},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win2 = make_window(app, repo, 2)
    win2.objects = [boundary2]

    win1._on_focus_in()
    app.copy_node()
    assert app.diagram_clipboard is not None

    win2._on_focus_in()
    app.paste_node()

    assert len(win2.objects) == 3
    assert sum(1 for o in win2.objects if o.obj_type == "System Boundary") == 2
    assert any(o.obj_type == "Task" for o in win2.objects)


def test_copy_paste_process_area_between_diagrams():
    ARCH_WINDOWS.clear()
    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_clipboard = None
    app.diagram_clipboard_type = None
    app.selected_node = None
    app.root_node = None
    app.clipboard_node = None
    app.cut_mode = False
    repo = DummyRepo("Governance Diagram", "Governance Diagram")

    area = SysMLObject(
        obj_id=_get_next_id(),
        obj_type="System Boundary",
        x=0,
        y=0,
        element_id=None,
        width=80,
        height=40,
        properties={"name": "Area"},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )

    win1 = make_window(app, repo, 1)
    win1.objects = [area]
    win1.selected_obj = area

    win2 = make_window(app, repo, 2)

    win1._on_focus_in()
    app.copy_node()
    assert app.diagram_clipboard is not None

    win2._on_focus_in()
    app.paste_node()

    assert len(win2.objects) == 1
    assert win2.objects[0].obj_type == "System Boundary"
