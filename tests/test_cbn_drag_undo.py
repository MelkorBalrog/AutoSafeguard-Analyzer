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
from analysis import CausalBayesianNetwork, CausalBayesianNetworkDoc
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def _setup_app(doc):
    app = AutoMLApp.__new__(AutoMLApp)
    app.cbn_docs = [doc]
    app.active_cbn = doc
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions: bool = False):
        return {
            "cbn_docs": [
                {
                    "name": d.name,
                    "nodes": list(d.network.nodes),
                    "parents": {k: list(v) for k, v in d.network.parents.items()},
                    "cpds": d.network.cpds,
                    "positions": {k: tuple(v) for k, v in d.positions.items()},
                    "types": dict(d.types),
                }
                for d in app.cbn_docs
            ]
        }

    def apply_model_data(data):
        app.cbn_docs = []
        for d in data.get("cbn_docs", []):
            net = CausalBayesianNetwork()
            net.nodes = d.get("nodes", [])
            net.parents = {k: list(v) for k, v in d.get("parents", {}).items()}
            net.cpds = d.get("cpds", {})
            positions = {k: tuple(v) for k, v in d.get("positions", {}).items()}
            types = dict(d.get("types", {}))
            app.cbn_docs.append(CausalBayesianNetworkDoc(d.get("name", "CBN"), network=net, positions=positions, types=types))
        app.active_cbn = app.cbn_docs[0] if app.cbn_docs else None

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
    app.undo = AutoMLApp.undo.__get__(app)
    app.redo = AutoMLApp.redo.__get__(app)
    return app


def test_cbn_node_drag_records_single_undo_step():
    doc = CausalBayesianNetworkDoc("CBN")
    doc.network.add_node("A", cpd=0.5)
    doc.positions["A"] = (0, 0)
    doc.types["A"] = "variable"

    win = CausalBayesianNetworkWindow.__new__(CausalBayesianNetworkWindow)
    win.nodes = {"A": (None, None, "fill")}
    win.edges = []
    win.canvas = types.SimpleNamespace(canvasx=lambda v: v, canvasy=lambda v: v, move=lambda *a: None, coords=lambda *a: None)
    win._position_table = lambda *a: None
    win._highlight_node = lambda *a: None
    win._find_node = lambda x, y: "A"
    win.current_tool = "Select"
    win.drag_node = None
    win.selected_node = None
    win.selection_rect = None

    app = _setup_app(doc)
    win.app = app

    press = types.SimpleNamespace(x=0, y=0)
    drag1 = types.SimpleNamespace(x=10, y=20)
    drag2 = types.SimpleNamespace(x=20, y=30)

    win.on_click(press)
    win.on_drag(drag1)
    win.on_drag(drag2)
    win.on_release(drag2)

    assert len(app._undo_stack) == 1
    assert app.cbn_docs[0].positions["A"] == (20, 30)

    app.undo()
    assert app.cbn_docs[0].positions["A"] == (0, 0)

    app.redo()
    assert app.cbn_docs[0].positions["A"] == (20, 30)
