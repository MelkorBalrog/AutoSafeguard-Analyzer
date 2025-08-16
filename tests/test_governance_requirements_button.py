import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


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
        def winfo_children(self):
            return []

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
    assert any("Start shall precede 'Finish'." in t for t in texts)
    # Ensure requirement types are organizational
    assert all(row[1] == "organizational" for row in trees[0].rows)
    assert all(row[4] == "draft" for row in trees[0].rows)
    # Requirements added to global registry
    assert len(global_requirements) == len(trees[0].rows)
    assert all(req.get("diagram") == "Gov" for req in global_requirements.values())


def test_requirements_button_no_change(monkeypatch):
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
        def winfo_children(self):
            return []

    def _new_tab(title):
        return DummyTab()

    class DummyTree:
        def __init__(self, master, columns, show="headings"):
            pass

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            pass

        def pack(self, **kwargs):
            pass

    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=_new_tab)
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov")

    global_requirements.clear()
    win.generate_requirements()
    rid = next(iter(global_requirements))

    # Regenerate without changes; requirement should remain unchanged
    win.generate_requirements()
    assert len(global_requirements) == 1
    assert global_requirements[rid]["status"] == "draft"
    assert global_requirements[rid]["diagram"] == "Gov"


def test_other_diagram_requirements_preserved(monkeypatch):
    repo = SysMLRepository.reset_instance()
    diag1 = repo.create_diagram("Governance Diagram", name="Gov1")
    diag2 = repo.create_diagram("Governance Diagram", name="Gov2")
    t1 = repo.create_element("Action", name="Start")
    t2 = repo.create_element("Action", name="Finish")
    objs = [
        {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": t1.elem_id, "properties": {"name": "Start"}},
        {"obj_id": 2, "obj_type": "Action", "x": 0, "y": 0, "element_id": t2.elem_id, "properties": {"name": "Finish"}},
    ]
    conns = [
        {"src": 1, "dst": 2, "conn_type": "Flow", "name": "", "properties": {}}
    ]
    diag1.objects = [dict(o) for o in objs]
    diag1.connections = list(conns)
    diag2.objects = [dict(o) for o in objs]
    diag2.connections = list(conns)

    toolbox = SafetyManagementToolbox()
    toolbox.diagrams["Gov1"] = diag1.diag_id
    toolbox.diagrams["Gov2"] = diag2.diag_id

    class DummyTab:
        def winfo_children(self):
            return []

    def _new_tab(title):
        return DummyTab()

    class DummyTree:
        def __init__(self, master, columns, show="headings"):
            pass

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            pass

        def pack(self, **kwargs):
            pass

    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=_new_tab)

    global_requirements.clear()
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov1")
    win.generate_requirements()
    rid1 = next(iter(global_requirements))
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov2")
    win.generate_requirements()
    rid2 = [rid for rid in global_requirements if rid != rid1][0]

    # Move object in first diagram; requirements unchanged
    diag1.objects[0]["x"] = 10
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov1")
    win.generate_requirements()

    assert len(global_requirements) == 2
    assert global_requirements[rid1]["status"] == "draft"
    assert global_requirements[rid2]["status"] == "draft"
