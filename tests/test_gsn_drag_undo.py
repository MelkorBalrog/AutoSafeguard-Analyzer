import sys
import types
from pathlib import Path

# Ensure repository root on path and provide dummy PIL modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))

from AutoML import AutoMLApp
from gsn import GSNNode, GSNDiagram
from gui.gsn_diagram_window import GSNDiagramWindow


def _setup_app(diagram):
    app = AutoMLApp.__new__(AutoMLApp)
    app.gsn_diagrams = [diagram]
    app.gsn_modules = []
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions: bool = False):
        return {
            "gsn_diagrams": [d.to_dict() for d in app.gsn_diagrams],
            "gsn_modules": [m.to_dict() for m in app.gsn_modules],
        }

    def apply_model_data(data):
        app.gsn_diagrams = [GSNDiagram.from_dict(d) for d in data.get("gsn_diagrams", [])]
        app.gsn_modules = []

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
    app.undo = AutoMLApp.undo.__get__(app)
    app.redo = AutoMLApp.redo.__get__(app)
    return app


def test_gsn_node_drag_records_single_undo_step():
    root = GSNNode("Root", "Goal", x=0, y=0)
    diagram = GSNDiagram(root)

    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.diagram = diagram
    win.canvas = types.SimpleNamespace(canvasx=lambda v: v, canvasy=lambda v: v)
    win.refresh = lambda: None
    win.zoom = 1
    win._node_at = lambda x, y: root
    win._connection_at = lambda x, y: None
    win._connect_mode = None
    win._connect_parent = None

    app = _setup_app(diagram)
    win.app = app

    click = types.SimpleNamespace(x=0, y=0)
    drag1 = types.SimpleNamespace(x=10, y=20)
    drag2 = types.SimpleNamespace(x=20, y=30)

    win._on_click(click)
    win._on_drag(drag1)
    win._on_drag(drag2)
    win._on_release(drag2)

    assert len(app._undo_stack) == 1
    assert app.gsn_diagrams[0].root.x == 20 and app.gsn_diagrams[0].root.y == 30

    app.undo()
    assert app.gsn_diagrams[0].root.x == 0 and app.gsn_diagrams[0].root.y == 0

    app.redo()
    assert app.gsn_diagrams[0].root.x == 20 and app.gsn_diagrams[0].root.y == 30
