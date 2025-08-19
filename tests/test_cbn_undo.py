import sys
import types

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))

from AutoML import AutoMLApp
from analysis import CausalBayesianNetwork, CausalBayesianNetworkDoc
from sysml.sysml_repository import SysMLRepository


def test_cbn_diagram_undo_redo_node_add_and_move():
    # Start with a clean repository
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo._undo_stack = []
    repo._redo_stack = []

    # Minimal application setup
    app = AutoMLApp.__new__(AutoMLApp)
    doc = CausalBayesianNetworkDoc("CBN")
    doc.network.add_node("A", cpd=0.5)
    doc.positions["A"] = (0, 0)
    doc.types["A"] = "variable"

    app.cbn_docs = [doc]
    app.active_cbn = doc
    app.update_views = lambda: None
    app._undo_stack = []
    app._redo_stack = []

    def export_model_data(include_versions=False):
        return {
            "cbn_docs": [
                {
                    "name": d.name,
                    "nodes": list(d.network.nodes),
                    "parents": {k: list(v) for k, v in d.network.parents.items()},
                    "cpds": {
                        var: (
                            cpd
                            if not isinstance(cpd, dict)
                            else {
                                "".join("1" if b else "0" for b in key): val
                                for key, val in cpd.items()
                            }
                        )
                        for var, cpd in d.network.cpds.items()
                    },
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
            raw_cpds = d.get("cpds", {})
            parsed_cpds = {}
            for var, cpd in raw_cpds.items():
                if isinstance(cpd, dict):
                    parsed_cpds[var] = {
                        tuple(ch == "1" for ch in key): val for key, val in cpd.items()
                    }
                else:
                    parsed_cpds[var] = cpd
            net.cpds = parsed_cpds
            positions = {k: tuple(v) for k, v in d.get("positions", {}).items()}
            types = dict(d.get("types", {}))
            app.cbn_docs.append(
                CausalBayesianNetworkDoc(d.get("name", "CBN"), network=net, positions=positions, types=types)
            )
        app.active_cbn = app.cbn_docs[0] if app.cbn_docs else None

    app.export_model_data = export_model_data
    app.apply_model_data = apply_model_data
    app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
    app.undo = AutoMLApp.undo.__get__(app)
    app.redo = AutoMLApp.redo.__get__(app)

    # Record state then modify
    app.push_undo_state()
    doc.network.add_node("B", cpd=0.5)
    doc.positions["B"] = (5, 5)
    doc.types["B"] = "variable"
    doc.positions["A"] = (10, 20)

    # Undo should remove B and restore A's position
    app.undo()
    doc_after = app.cbn_docs[0]
    assert "B" not in doc_after.network.nodes
    assert doc_after.positions["A"] == (0, 0)

    # Redo should bring back B and moved A
    app.redo()
    doc_redo = app.cbn_docs[0]
    assert "B" in doc_redo.network.nodes
    assert doc_redo.positions["A"] == (10, 20)
