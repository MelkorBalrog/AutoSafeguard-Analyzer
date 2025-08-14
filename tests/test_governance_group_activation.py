import sys
from pathlib import Path
import tkinter as tk
import pytest

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

    def size(self):
        return len(self.items)

    def delete(self, i):
        del self.items[i]


class DummyMenu:
    def __init__(self):
        self.state = None

    def entryconfig(self, _idx, state=tk.DISABLED):
        self.state = state


@pytest.mark.parametrize(
    "work_product,parent",
    [
        ("FTA", "FTA"),
        ("Safety & Security Case", "GSN"),
        ("GSN Argumentation", "GSN"),
        ("FMEA", "Qualitative Analysis"),
        ("FMEDA", "Quantitative Analysis"),
    ],
)
def test_work_product_groups_follow_phase(work_product, parent):
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
    app.tool_categories = {"Safety Analysis": []}
    app.tool_actions = {}
    wp_menu = DummyMenu()
    parent_menu = wp_menu if work_product == parent else DummyMenu()
    app.work_product_menus = {work_product: [(wp_menu, 0)]}
    if parent not in app.work_product_menus:
        app.work_product_menus[parent] = [(parent_menu, 0)]
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.tool_to_work_product = {info[1]: name for name, info in FaultTreeApp.WORK_PRODUCT_INFO.items()}
    app.update_views = lambda: None
    app.safety_mgmt_toolbox = toolbox
    app.refresh_tool_enablement = FaultTreeApp.refresh_tool_enablement.__get__(app, FaultTreeApp)
    app.enable_work_product = FaultTreeApp.enable_work_product.__get__(app, FaultTreeApp)
    app.disable_work_product = FaultTreeApp.disable_work_product.__get__(app, FaultTreeApp)

    toolbox.add_work_product("Gov", work_product, "")
    toolbox.on_change = app.refresh_tool_enablement
    app.refresh_tool_enablement()

    assert work_product in app.enabled_work_products
    assert parent in app.enabled_work_products
    assert wp_menu.state == tk.NORMAL
    assert parent_menu.state == tk.NORMAL

    toolbox.set_active_module("P2")
    app.refresh_tool_enablement()
    assert work_product not in app.enabled_work_products
    assert parent not in app.enabled_work_products
    assert wp_menu.state == tk.DISABLED
    assert parent_menu.state == tk.DISABLED
    # Reset global toolbox to avoid side effects on other tests
    from analysis import safety_management as _sm
    _sm.ACTIVE_TOOLBOX = None

