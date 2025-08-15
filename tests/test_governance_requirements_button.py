import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements, REQUIREMENT_TYPE_OPTIONS


def test_requirements_button_opens_tab(monkeypatch):
    repo = SysMLRepository.reset_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    t1 = repo.create_element("Action", name="Start")
    t2 = repo.create_element("Action", name="Finish")
    diag.objects = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t1.elem_id, "properties": {"name": "Start"}},
        {"obj_id": 2, "obj_type": "Action", "x": 0, "y": 0, "element_id": t2.elem_id, "properties": {"name": "Finish"}},
    ]
    diag.connections = [
        {"src": 1, "dst": 2, "conn_type": "Flow", "name": "", "properties": {}}
    ]

    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov"] = diag.diag_id

    class DummyTab:
        pass

    tabs: list[tuple[str, DummyTab]] = []

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
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov")

    global_requirements.clear()
    win.generate_requirements()

    assert tabs
    title, _tab = tabs[0]
    assert "Gov Requirements" in title
    assert trees and trees[0].rows
    texts = [row[2] for row in trees[0].rows]
    assert any("Task 'Start' shall precede task 'Finish'." in t for t in texts)
    # Ensure requirement types are valid
    assert all(row[1] in REQUIREMENT_TYPE_OPTIONS for row in trees[0].rows)
    # Requirements added to global registry
    assert len(global_requirements) == len(trees[0].rows)
