import types
import os
import sys

# provide dummy PIL modules
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp
from gsn import GSNNode, GSNDiagram
from gui.gsn_diagram_window import GSNDiagramWindow


def test_tab_loaded_syncs_clones():
    app = AutoMLApp.__new__(AutoMLApp)
    app.fmea_entries = []
    app.fmeas = []
    app.fmedas = []
    app.get_all_fmea_entries = types.MethodType(lambda _self: [], app)
    app.get_all_nodes = types.MethodType(lambda _self, node=None: [], app)
    app.get_all_nodes_in_model = types.MethodType(lambda _self: [], app)

    original = GSNNode("Orig", "Goal")
    diag1 = GSNDiagram(original)
    clone = original.clone()
    diag2 = GSNDiagram(clone)

    app.gsn_diagrams = [diag1, diag2]
    app.all_gsn_diagrams = [diag1, diag2]

    clone.user_name = "Clone"
    clone.description = "CloneDesc"
    clone.manager_notes = "CloneNotes"

    original.user_name = "Updated"
    original.description = "UpdatedDesc"
    original.manager_notes = "UpdatedNote"

    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.app = app
    win.diagram = diag2
    win.refresh = lambda: None

    GSNDiagramWindow._on_tab_loaded(win, None)

    assert clone.user_name == "Updated"
    assert clone.description == "UpdatedDesc"
    assert clone.manager_notes == "UpdatedNote"
