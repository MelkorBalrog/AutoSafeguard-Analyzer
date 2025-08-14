import types
from dataclasses import asdict

from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from gui.architecture import BPMNDiagramWindow, SysMLDiagramWindow, SysMLObject
import gui.architecture as arch


def test_open_bpmn_diagram_refreshes_after_phase_activation(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("BPMN Diagram", name="Gov2")
    obj = SysMLObject(1, "Work Product", 0.0, 0.0)
    diag.objects.append(asdict(obj))

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("Phase1"), GovernanceModule("Phase2", diagrams=["Gov2"])]
    toolbox.set_active_module("Phase1")

    class DummyVar:
        def __init__(self):
            self.val = ""

        def set(self, val):
            self.val = val

        def get(self):
            return self.val

    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        lifecycle_var=DummyVar(),
        refresh_tool_enablement=lambda: None,
    )

    def on_lifecycle_selected():
        toolbox.set_active_module(app.lifecycle_var.get())

    app.on_lifecycle_selected = on_lifecycle_selected

    def fake_sysml_init(self, master, title, tools, diagram_id=None, app=None, history=None):
        self.app = app
        self.repo = repo
        self.diagram_id = diagram_id
        self.objects = []
        for data in repo.visible_objects(diagram_id):
            self.objects.append(SysMLObject(**data))
        self.sort_objects = lambda: None
        self.connections = []
        self.redraw = lambda: None
        self.update_property_view = lambda: None
        self.toolbox = types.SimpleNamespace(winfo_children=lambda: [])
        canvas_master = types.SimpleNamespace(pack_forget=lambda: None, pack=lambda **kwargs: None)
        self.canvas = types.SimpleNamespace(master=canvas_master)

    monkeypatch.setattr(arch.SysMLDiagramWindow, "__init__", fake_sysml_init)

    class DummyWidget:
        def __init__(self, *args, **kwargs):
            pass

        def pack(self, *args, **kwargs):
            pass

        def configure(self, *args, **kwargs):
            pass

        def cget(self, key):
            return ""

        def winfo_children(self):
            return []

    monkeypatch.setattr(arch.ttk, "LabelFrame", DummyWidget)
    monkeypatch.setattr(arch.ttk, "Button", DummyWidget)

    win = BPMNDiagramWindow(None, app, diagram_id=diag.diag_id)

    assert toolbox.active_module == "Phase2"
    assert len(win.objects) == 1
