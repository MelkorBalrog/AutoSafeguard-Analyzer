import tkinter as tk
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository
from AutoML import FaultTreeApp


class DummyListbox:
    def __init__(self):
        self.items: list[str] = []
        self.colors: list[tuple[int, str]] = []

    def get(self, *_):
        return self.items

    def insert(self, index, item):
        if isinstance(index, int):
            self.items.insert(index, item)
        else:
            self.items.append(item)

    def itemconfig(self, index, foreground="black"):
        self.colors.append((index, foreground))


def test_cause_effect_tool_enabled_with_fta():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"])]
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.set_active_module("P1")
    toolbox.add_work_product("Gov", "FTA", "")

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    lb.insert(tk.END, "Cause & Effect Chain")
    app.tool_listboxes = {"Safety Analysis": lb}
    app.tool_categories = {"Safety Analysis": ["Cause & Effect Chain"]}
    app.tool_actions = {"Cause & Effect Chain": lambda: None}
    app.enable_process_area = lambda area: None
    app.update_views = lambda: None
    app.work_product_menus = {}
    app.enabled_work_products = set()
    app.safety_mgmt_toolbox = toolbox
    app.tool_to_work_product = {"Cause & Effect Chain": {"FTA"}}
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(app, FaultTreeApp)
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(app, FaultTreeApp)
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(
        app, FaultTreeApp
    )

    app.refresh_tool_enablement()

    assert (0, "black") in lb.colors

