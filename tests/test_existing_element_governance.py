import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sysml.sysml_repository import SysMLRepository
from gui.architecture import SysMLDiagramWindow, SysMLObjectDialog
from analysis.safety_management import SafetyManagementToolbox


def test_existing_element_respects_governance(monkeypatch):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()

    # Source architecture diagram with an element
    arch = repo.create_diagram("Architecture Diagram", name="Arch")
    elem = repo.create_element("Block", name="B1")
    repo.add_element_to_diagram(arch.diag_id, elem.elem_id)
    repo.link_diagram(elem.elem_id, arch.diag_id)

    # Target control flow diagram
    cfd = repo.create_diagram("Control Flow Diagram", name="CFD")

    toolbox = SafetyManagementToolbox()
    app = types.SimpleNamespace(safety_mgmt_toolbox=toolbox)

    class DummyCanvas:
        def canvasx(self, v):
            return v

        def canvasy(self, v):
            return v

    class DummyWin:
        def __init__(self):
            self.repo = repo
            self.diagram_id = cfd.diag_id
            self.zoom = 1
            self.current_tool = "Existing Element"
            self.canvas = DummyCanvas()
            self.app = app
            self.objects = []

        def find_object(self, *a, **k):
            return None

    win = DummyWin()
    event = types.SimpleNamespace(x=0, y=0, state=0)

    messages = []
    monkeypatch.setattr("gui.architecture.messagebox.showinfo", lambda *a, **k: messages.append(a))

    captured = []

    class DummyDialog:
        def __init__(self, parent, names, title="Select Element"):
            captured.extend(names)
            self.result = None

    monkeypatch.setattr(SysMLObjectDialog, "SelectElementDialog", DummyDialog)

    # Without governance no elements are available
    SysMLDiagramWindow.on_left_press(win, event)
    assert messages and not captured

    # Establish governance: Architecture Diagram -> Control Flow Diagram
    gov = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams["Gov"] = gov.diag_id
    gov.objects = [
        {"obj_id": 1, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Architecture Diagram"}},
        {"obj_id": 2, "obj_type": "Work Product", "x": 0.0, "y": 0.0, "properties": {"name": "Control Flow Diagram"}},
    ]
    gov.connections = [{"src": 1, "dst": 2, "conn_type": "Used By"}]
    toolbox.add_work_product("Gov", "Architecture Diagram", "")
    toolbox.add_work_product("Gov", "Control Flow Diagram", "")

    messages.clear()
    captured.clear()
    SysMLDiagramWindow.on_left_press(win, event)
    assert not messages
    assert captured == ["B1"]
