import tkinter as tk
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from AutoML import AutoMLApp
from analysis.models import REQUIREMENT_WORK_PRODUCTS

class DummyMenu:
    def __init__(self):
        self.states = {}
    def entryconfig(self, idx, state=tk.DISABLED):
        self.states[idx] = state

class DummyToolbox:
    work_products = [1]
    active_module = None
    def enabled_products(self):
        return {"Vehicle Requirement Specification"}

def test_requirement_menu_enabled_with_any_work_product():
    menu = DummyMenu()
    app = AutoMLApp.__new__(AutoMLApp)
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.tool_actions = {}
    app.enable_process_area = lambda area: None
    app.update_views = lambda: None
    app.work_product_menus = {}
    app.enabled_work_products = set()
    app.WORK_PRODUCT_INFO = AutoMLApp.WORK_PRODUCT_INFO
    app.WORK_PRODUCT_PARENTS = AutoMLApp.WORK_PRODUCT_PARENTS
    app.tool_to_work_product = {}
    app.safety_mgmt_toolbox = DummyToolbox()
    for wp in REQUIREMENT_WORK_PRODUCTS:
        app.work_product_menus.setdefault(wp, []).append((menu, 0))
    AutoMLApp.enable_work_product(app, "Vehicle Requirement Specification", refresh=False)
    AutoMLApp.refresh_tool_enablement(app)
    assert menu.states[0] == tk.NORMAL
