import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt


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

    created_texts = []

    class DummyText:
        def __init__(self, master, wrap="word"):
            self.content = ""
            created_texts.append(self)

        def insert(self, index, text):
            self.content += text

        def configure(self, **kwargs):
            pass

        def pack(self, **kwargs):
            pass

    monkeypatch.setattr(smt.tk, "Text", DummyText)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = types.SimpleNamespace(_new_tab=_new_tab)

    win.generate_phase_requirements("Phase1")

    assert tabs
    title, _tab = tabs[0]
    assert "Phase1 Requirements" in title
    assert created_texts
    content = created_texts[0].content
    assert "Task 'Start' shall precede task 'Finish'." in content
    assert "Task 'Check' shall precede task 'Complete'." in content
