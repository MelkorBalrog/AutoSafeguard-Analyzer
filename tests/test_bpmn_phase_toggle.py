import types

from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from gui.architecture import BPMNDiagramWindow


class DummyVar:
    def __init__(self):
        self.value = ""

    def set(self, val):
        self.value = val

    def get(self):
        return self.value


def test_open_bpmn_diagram_activates_phase():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="Gov1")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="Phase1", diagrams=["Gov1"])]
    toolbox.diagrams = {"Gov1": diag.diag_id}

    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        lifecycle_var=DummyVar(),
        refresh_tool_enablement_called=False,
    )

    def on_lifecycle_selected(_event=None):
        app.safety_mgmt_toolbox.set_active_module(app.lifecycle_var.get())
        app.refresh_tool_enablement_called = True

    app.on_lifecycle_selected = on_lifecycle_selected

    win = BPMNDiagramWindow.__new__(BPMNDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.app = app

    BPMNDiagramWindow._activate_parent_phase(win)

    assert toolbox.active_module == "Phase1"
    assert app.lifecycle_var.get() == "Phase1"
    assert app.refresh_tool_enablement_called
