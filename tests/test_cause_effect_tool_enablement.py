import sys
from pathlib import Path

import tkinter as tk
sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository
from AutoML import FaultTreeApp


class DummyListbox:
    def __init__(self):
        self.items = ["Cause & Effect Diagram"]
        self.colors = {}
        self.selection = ()

    def get(self, start, end=None):
        if end is None:
            return self.items[start]
        if end == tk.END:
            return self.items[start:]
        return self.items[start:end]

    def insert(self, index, item):
        self.items.insert(index if isinstance(index, int) else len(self.items), item)

    def itemconfig(self, index, foreground="black"):
        self.colors[self.items[index]] = foreground

    def curselection(self):
        return self.selection

    def selection_set(self, index):
        self.selection = (index,)

    def selection_clear(self, _start, _end):
        self.selection = ()

    def nearest(self, _y):
        return 0


def test_cause_effect_tool_enabled_with_safety_analysis():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov")

    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1", diagrams=["Gov"]), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.set_active_module("P1")

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    app.tool_listboxes = {"Safety Analysis": lb}
    app.tool_categories = {"Safety Analysis": ["Cause & Effect Diagram"]}
    app.tool_actions = {"Cause & Effect Diagram": lambda: None}
    app.work_product_menus = {}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.update_views = lambda: None
    app.tool_to_work_product = {"Cause & Effect Diagram": {"FTA"}}
    app.safety_mgmt_toolbox = toolbox
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(app, FaultTreeApp)
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(app, FaultTreeApp)
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(app, FaultTreeApp)

    toolbox.on_change = app.refresh_tool_enablement
    toolbox.add_work_product("Gov", "FTA", "")
    app.refresh_tool_enablement()

    assert lb.colors.get("Cause & Effect Diagram") == "black"


def test_cause_effect_tool_opens_on_double_click():
    action_called = {"flag": False}

    def action():
        action_called["flag"] = True

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    app.tool_actions = {"Cause & Effect Diagram": action}
    app.tool_to_work_product = {"Cause & Effect Diagram": {"FTA"}}
    app.enabled_work_products = {"FTA"}
    app.safety_mgmt_toolbox = None

    event = type("E", (), {"widget": lb, "y": 0})()
    app.on_tool_list_double_click(event)

    assert action_called["flag"]
