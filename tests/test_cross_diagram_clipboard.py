import types


from AutoML import AutoMLApp
from gui.architecture import SysMLDiagramWindow, _get_next_id


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
    return win


def test_copy_paste_between_same_type_diagrams():
    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_clipboard = None
    app.diagram_clipboard_type = None
    app.selected_node = None
    app.root_node = None
    app.clipboard_node = None
    app.cut_mode = False
    repo = DummyRepo("Governance Diagram", "Governance Diagram")

    obj = types.SimpleNamespace(
        obj_id=_get_next_id(),
        obj_type="Plan",
        x=0,
        y=0,
        width=80,
        height=40,
        element_id=None,
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
