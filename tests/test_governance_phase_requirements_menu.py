import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


def test_phase_requirements_menu(monkeypatch):
    repo = SysMLRepository.reset_instance()
    d1 = repo.create_diagram("Governance Diagram", name="Gov1")
    t1 = repo.create_element("Action", name="Start")
    t2 = repo.create_element("Action", name="Finish")
    d1.objects = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t1.elem_id, "properties": {"name": "Start"}},
        {"obj_id": 2, "obj_type": "Action", "x": 0, "y": 0, "element_id": t2.elem_id, "properties": {"name": "Finish"}},
    ]
    d1.connections = [
        {"src": 1, "dst": 2, "conn_type": "Flow", "name": "", "properties": {}}
    ]

    d2 = repo.create_diagram("Governance Diagram", name="Gov2")
    t3 = repo.create_element("Action", name="Check")
    t4 = repo.create_element("Action", name="Complete")
    d2.objects = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t3.elem_id, "properties": {"name": "Check"}},
        {"obj_id": 2, "obj_type": "Action", "x": 0, "y": 0, "element_id": t4.elem_id, "properties": {"name": "Complete"}},
    ]
    d2.connections = [
        {"src": 1, "dst": 2, "conn_type": "Flow", "name": "", "properties": {}}
    ]

    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov1"] = d1.diag_id
    toolbox.diagrams["Gov2"] = d2.diag_id
    mod = toolbox.add_module("Phase1")
    mod.diagrams.extend(["Gov1", "Gov2"])

    class DummyTab:
        pass

    tabs = []

    def _new_tab(title):
        tab = DummyTab()
        tabs.append((title, tab))
        return tab

    trees = []

    class DummyTree:
        def __init__(self, master, columns, show="headings"):
            self.rows = []
            trees.append(self)

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            self.rows.append(values)

        def pack(self, **kwargs):
            pass

    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=_new_tab)

    global_requirements.clear()
    win.generate_phase_requirements("Phase1")

    assert tabs
    title, _tab = tabs[0]
    assert "Phase1 Requirements" in title
    assert trees and trees[0].rows
    texts = [row[2] for row in trees[0].rows]
    assert any("Start shall precede 'Finish'." in t for t in texts)
    assert any("Check shall precede 'Complete'." in t for t in texts)
    assert all(row[1] == "organizational" for row in trees[0].rows)
    assert len(global_requirements) == len(trees[0].rows)
