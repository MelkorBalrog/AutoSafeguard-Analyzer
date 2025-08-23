import tkinter as tk
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp

class DummyMenu:
    def __init__(self):
        self.states = {}
    def entryconfig(self, idx, state=tk.DISABLED):
        self.states[idx] = state

class DummyToolbox:
    work_products = [1]
    active_module = None
    def enabled_products(self):
        return {"Product Goal Specification"}

def test_product_goal_enables_requirement_menu():
    menu = DummyMenu()
    app = AutoMLApp.__new__(AutoMLApp)
    app.tool_listboxes = {}
    app.tool_categories = {}
    app.tool_actions = {}
    app.enable_process_area = lambda area: None
    app.update_views = lambda: None
    app.work_product_menus = {"Product Goal Specification": [(menu, 0)]}
    app.enabled_work_products = set()
    app.WORK_PRODUCT_INFO = AutoMLApp.WORK_PRODUCT_INFO
    app.WORK_PRODUCT_PARENTS = AutoMLApp.WORK_PRODUCT_PARENTS
    app.tool_to_work_product = {}
    app.safety_mgmt_toolbox = DummyToolbox()
    AutoMLApp.enable_work_product(app, "Product Goal Specification", refresh=False)
    AutoMLApp.refresh_tool_enablement(app)
    assert menu.states[0] == tk.NORMAL
