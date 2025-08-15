import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from gui import safety_management_toolbox as smt
from AutoML import FaultTreeApp


def test_requirements_menu_opens_tab(monkeypatch):
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

    app = types.SimpleNamespace(_new_tab=_new_tab)
    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.toolbox = toolbox
    win.app = app
    win.diag_var = types.SimpleNamespace(get=lambda: "Gov")
    win.winfo_exists = lambda: True
    app.safety_mgmt_window = win

    FaultTreeApp.generate_governance_requirements(app)

    assert tabs
    title, _tab = tabs[0]
    assert "Gov Requirements" in title
    assert created_texts
    assert "Task 'Start' shall precede task 'Finish'." in created_texts[0].content
