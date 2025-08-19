import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository
from config import load_diagram_rules


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


class DummyTip:
    def __init__(self, widget, text, automatic=False):
        self.text = text

    def show(self, x=None, y=None):
        pass

    def hide(self):
        pass


def _expected_text(cfg, node_type: str) -> str:
    rules = cfg["connection_rules"]["Governance Diagram"]
    outgoing = {}
    incoming = {}
    for rel, srcs in rules.items():
        targets = srcs.get(node_type, [])
        if targets:
            outgoing[rel] = sorted(targets)
        for src, dests in srcs.items():
            if node_type in dests:
                incoming.setdefault(rel, []).append(src)
    if not outgoing and not incoming:
        return ""
    lines = ["To Others | From Others"]
    for rel in sorted(set(outgoing) | set(incoming)):
        outs = ", ".join(outgoing.get(rel, []))
        ins = ", ".join(sorted(incoming.get(rel, [])))
        lines.append(f"{rel}: {outs} | {ins}")
    return "\n".join(lines)


def test_governance_element_tooltips(monkeypatch):
    cfg = load_diagram_rules(Path(__file__).resolve().parents[1] / "config/diagram_rules.json")
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")

    role = SysMLObject(1, "Role", 0.0, 0.0)
    org = SysMLObject(2, "Organization", 200.0, 0.0)
    op = SysMLObject(3, "Operation", 400.0, 0.0)

    win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    win.canvas = DummyCanvas()
    win._conn_tip = DummyTip(win.canvas, "")
    win._conn_tip_obj = None
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.current_tool = "Select"
    win.start = None
    win.zoom = 1.0
    win.objects = [role, org, op]
    win.find_object = SysMLDiagramWindow.find_object.__get__(win)

    win.on_mouse_move(types.SimpleNamespace(x=0, y=0))
    assert win._conn_tip.text == _expected_text(cfg, "Role")

    win.on_mouse_move(types.SimpleNamespace(x=200, y=0))
    assert win._conn_tip.text == _expected_text(cfg, "Organization")

    win.on_mouse_move(types.SimpleNamespace(x=400, y=0))
    assert win._conn_tip.text == _expected_text(cfg, "Operation")
