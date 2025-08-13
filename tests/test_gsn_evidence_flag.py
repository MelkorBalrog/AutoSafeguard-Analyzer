import sys
import types
import os

# Provide stubs for Pillow dependencies used by AutoML/gsn modules
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gsn import GSNNode, GSNDiagram


def test_solution_evidence_flag_roundtrip():
    root = GSNNode("G", "Goal")
    sol = GSNNode("S", "Solution")
    root.add_child(sol)
    sol.evidence_sufficient = True
    diag = GSNDiagram(root)
    diag.add_node(sol)

    data = diag.to_dict()
    loaded = GSNDiagram.from_dict(data)
    loaded_sol = next(n for n in loaded.nodes if n.node_type == "Solution")
    assert loaded_sol.evidence_sufficient
