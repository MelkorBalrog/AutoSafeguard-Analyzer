import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui.architecture as arch
from gui.architecture import GovernanceDiagramWindow
from sysml.sysml_repository import SysMLRepository


def test_global_relation_not_duplicated(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")

    ai_data = {"nodes": [], "relations": ["Flow", "Assess"], "externals": {}}
    defs_data = {"Entities": {"nodes": [], "relations": ["Bar"], "externals": {}},
                 "Safety & AI Lifecycle": ai_data}
    monkeypatch.setattr(arch, "_toolbox_defs", lambda: defs_data)

    class DummyWidget:
        def __init__(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def pack_forget(self, *a, **k):
            pass

        def bind(self, *a, **k):
            pass

        def configure(self, *a, **k):
            pass

        def destroy(self, *a, **k):
            pass

    def fake_sysml_init(self, master, title, tools, diagram_id=None, app=None, history=None, relation_tools=None, tool_groups=None):
        self.app = app
        self.repo = repo
        self.diagram_id = diagram_id
        self.toolbox = DummyWidget()
        self.tools_frame = DummyWidget()
        self.rel_frame = DummyWidget()
        self.toolbox_selector = DummyWidget()
        self.toolbox_var = types.SimpleNamespace(get=lambda: "", set=lambda v: None)
        self.relation_tools = relation_tools or []
        self._toolbox_frames = {}
        self.canvas = types.SimpleNamespace(master=DummyWidget())

    monkeypatch.setattr(arch.SysMLDiagramWindow, "__init__", fake_sysml_init)
    monkeypatch.setattr(arch, "draw_icon", lambda *a, **k: None)
    monkeypatch.setattr(arch.GovernanceDiagramWindow, "refresh_from_repository", lambda self: None)
    monkeypatch.setattr(arch.ttk, "Combobox", DummyWidget)
    monkeypatch.setattr(arch.ttk, "Frame", DummyWidget)
    monkeypatch.setattr(arch.ttk, "LabelFrame", DummyWidget)
    monkeypatch.setattr(arch.ttk, "Button", DummyWidget)

    win = GovernanceDiagramWindow(None, None, diagram_id=diag.diag_id)
    # Relation "Flow" should be removed from the category since it exists in the
    # global relation toolbox.
    assert ai_data["relations"] == ["Assess"]
