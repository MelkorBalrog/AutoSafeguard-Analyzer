import types

# Provide dummy PIL modules so AutoML can be imported without Pillow
import sys

sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))

from gsn import GSNNode, GSNDiagram
from gui.gsn_explorer import GSNExplorer
from AutoML import FaultTreeApp
from sysml.sysml_repository import SysMLRepository


def test_gsn_diagram_undo_redo_rename(monkeypatch):
    root = GSNNode("G", "Goal")
    diag = GSNDiagram(root)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.gsn_diagrams = [diag]
    app.gsn_modules = []
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions=False):
        return {
            "gsn_diagrams": [d.to_dict() for d in app.gsn_diagrams],
            "gsn_modules": [m.to_dict() for m in app.gsn_modules],
        }

    def apply_model_data(data):
        app.gsn_diagrams = [GSNDiagram.from_dict(d) for d in data.get("gsn_diagrams", [])]
        app.gsn_modules = []

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = FaultTreeApp.push_undo_state.__get__(app)
    app.undo = FaultTreeApp.undo.__get__(app)
    app.redo = FaultTreeApp.redo.__get__(app)

    explorer = GSNExplorer.__new__(GSNExplorer)
    explorer.app = app
    explorer.tree = types.SimpleNamespace(selection=lambda: ["i1"])
    explorer.item_map = {"i1": ("diagram", diag)}
    explorer.populate = lambda: None

    monkeypatch.setattr(
        "gui.gsn_explorer.simpledialog.askstring", lambda *a, **k: "New"
    )

    explorer.rename_item()
    assert app.gsn_diagrams[0].root.user_name == "New"

    app.undo()
    assert app.gsn_diagrams[0].root.user_name == "G"

    app.redo()
    assert app.gsn_diagrams[0].root.user_name == "New"


def test_gsn_undo_redo_preserves_repository(monkeypatch):
    repo = SysMLRepository.reset_instance()
    repo.create_package("Pkg")

    root = GSNNode("G", "Goal")
    diag = GSNDiagram(root)

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.gsn_diagrams = [diag]
    app.gsn_modules = []
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions=False):
        return {
            "gsn_diagrams": [d.to_dict() for d in app.gsn_diagrams],
            "gsn_modules": [],
        }

    def apply_model_data(data):
        app.gsn_diagrams = [GSNDiagram.from_dict(d) for d in data.get("gsn_diagrams", [])]
        app.gsn_modules = []

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = FaultTreeApp.push_undo_state.__get__(app)
    app.undo = FaultTreeApp.undo.__get__(app)
    app.redo = FaultTreeApp.redo.__get__(app)

    app.push_undo_state()
    app.gsn_diagrams[0].root.user_name = "New"

    app.undo()
    assert app.gsn_diagrams[0].root.user_name == "G"
    assert any(e.name == "Pkg" for e in repo.elements.values())

    app.redo()
    assert app.gsn_diagrams[0].root.user_name == "New"
    assert any(e.name == "Pkg" for e in repo.elements.values())

