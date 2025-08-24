import sys
from pathlib import Path
import types
from tkinter import simpledialog

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox
from gui.safety_management_explorer import SafetyManagementExplorer


def test_new_diagram_refreshes_toolbox(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()

    refreshed = {"called": False}
    def refresh_diagrams():
        refreshed["called"] = True

    app = types.SimpleNamespace(
        safety_mgmt_window=types.SimpleNamespace(refresh_diagrams=refresh_diagrams)
    )

    explorer = SafetyManagementExplorer.__new__(SafetyManagementExplorer)
    explorer.app = app
    explorer.toolbox = toolbox
    explorer.tree = types.SimpleNamespace(selection=lambda: ["root"])
    explorer.item_map = {"root": ("root", None)}
    explorer.populate = lambda: None

    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "Gov1")

    explorer.new_diagram()

    assert refreshed["called"], "toolbox not refreshed"
    assert "Gov1" in toolbox.list_diagrams()
