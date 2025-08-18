import tkinter as tk
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from sysml.sysml_repository import SysMLRepository
from AutoML import FaultTreeApp


class DummyListbox:
    def __init__(self):
        self.items = []
        self.colors = []

    def get(self, *_):
        return self.items

    def insert(self, index, item):
        self.items.insert(index if isinstance(index, int) else len(self.items), item)

    def itemconfig(self, index, foreground="black"):
        self.colors.append((index, foreground))


class DummyMenu:
    def __init__(self):
        self.state = None

    def entryconfig(self, _idx, state=tk.DISABLED):
        self.state = state


def test_repository_phase_enables_work_product():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.active_phase = "P1"
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    diag.tags.append("safety-management")
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule(name="P1"), GovernanceModule(name="P2")]
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.set_active_module("P1")

    app = FaultTreeApp.__new__(FaultTreeApp)
    lb = DummyListbox()
    info = FaultTreeApp.WORK_PRODUCT_INFO["GSN Argumentation"]
    app.tool_listboxes = {info[0]: lb}
    app.tool_categories = {info[0]: []}
    app.tool_actions = {}
    wp_menu = DummyMenu()
    parent_menu = DummyMenu()
    app.work_product_menus = {"GSN Argumentation": [(wp_menu, 0)], "GSN": [(parent_menu, 0)]}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.tool_to_work_product = {info[1]: name for name, info in FaultTreeApp.WORK_PRODUCT_INFO.items()}
    app.update_views = lambda: None
    app.safety_mgmt_toolbox = toolbox
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(app, FaultTreeApp)
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(app, FaultTreeApp)
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(app, FaultTreeApp)

    toolbox.add_work_product("Gov", "GSN Argumentation", "")
    toolbox.on_change = app.refresh_tool_enablement
    app.refresh_tool_enablement()

    assert "GSN Argumentation" in app.enabled_work_products
    assert "GSN" in app.enabled_work_products
    assert wp_menu.state == tk.NORMAL
    assert parent_menu.state == tk.NORMAL
