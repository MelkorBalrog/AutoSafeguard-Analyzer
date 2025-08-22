import types

from AutoML import AutoMLApp
from gui.architecture import SysMLObject, ARCH_WINDOWS, _get_next_id
from tests.test_cross_diagram_clipboard import DummyRepo, make_window


def test_copy_paste_task_via_window_between_governance_diagrams():
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
        properties={"name": "Area1"},
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
        properties={"name": "Area2"},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win2 = make_window(app, repo, 2)
    win2.objects = [boundary2]

    win1._on_focus_in()
    win1.copy_selected()
    assert app.diagram_clipboard is not None

    win2._on_focus_in()
    app.paste_node()

    assert any(o.obj_type == "Task" for o in win2.objects)
    assert any(o is task for o in win1.objects)
    assert sum(1 for o in win2.objects if o.obj_type == "System Boundary") == 2
