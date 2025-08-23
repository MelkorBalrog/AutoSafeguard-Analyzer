import sys
import types

# Ensure repository root on path
sys.path.append(str(__import__("pathlib").Path(__file__).resolve().parents[1]))

# Stub PIL modules so AutoML can be imported without Pillow
for mod in ["PIL", "PIL.Image", "PIL.ImageDraw", "PIL.ImageFont", "PIL.ImageTk"]:
    sys.modules.setdefault(mod, types.ModuleType(mod))

import main.AutoML as AutoML
from main.AutoML import AutoMLApp, FaultTreeNode


class DummyCanvas:
    def __init__(self, master=None, bg=None):
        self.master = master
        self.diagram_mode = None

    # Canvas helpers used by AutoML
    def pack(self, *a, **k):
        pass

    def config(self, *a, **k):
        pass

    def bind(self, *a, **k):
        pass

    def xview(self, *a, **k):
        pass

    def yview(self, *a, **k):
        pass

    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y


class DummyScrollbar:
    def __init__(self, *a, **k):
        self.command = k.get("command")

    def pack(self, *a, **k):
        pass

    def set(self, *a, **k):
        pass


class DummyFrame:
    def __init__(self, master=None):
        self.master = master

    def winfo_exists(self):
        return True


class DummyNotebook:
    def __init__(self):
        self.tabs_added = []

    def add(self, tab, text=""):
        self.tabs_added.append((tab, text))

    def select(self, tab):
        self.selected = tab


class DummyMenu:
    def __init__(self, *a, **k):
        AutoML._last_menu = self
        self.items = []

    def add_command(self, label, command=None):
        self.items.append(label)

    def add_separator(self):
        self.items.append("---")

    def tk_popup(self, *a, **k):
        pass

    # For _update_analysis_menus
    def entryconfig(self, index, state="normal"):
        self.items.append((index, state))


class DummyTk(types.SimpleNamespace):
    HORIZONTAL = 0
    VERTICAL = 1
    NORMAL = "normal"
    DISABLED = "disabled"
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"
    X = "x"
    Y = "y"
    BOTH = "both"
    Canvas = DummyCanvas
    Menu = DummyMenu


class DummyTtk(types.SimpleNamespace):
    Frame = DummyFrame
    Scrollbar = DummyScrollbar


class DummyStyle:
    canvas_bg = "white"

    @staticmethod
    def get_instance():
        return DummyStyle


def test_create_cta_tab_records_mode(monkeypatch):
    monkeypatch.setattr(AutoML, "tk", DummyTk())
    monkeypatch.setattr(AutoML, "ttk", DummyTtk())
    monkeypatch.setattr(AutoML, "StyleManager", DummyStyle)

    app = AutoMLApp.__new__(AutoMLApp)
    app.doc_nb = DummyNotebook()
    app.analysis_tabs = {}
    app._fta_menu_indices = {}
    app._cta_menu_indices = {}
    app._paa_menu_indices = {}
    app._update_analysis_menus = lambda: None

    app._create_cta_tab()
    assert app.canvas.diagram_mode == "CTA"
    assert "CTA" in app.analysis_tabs


def test_update_analysis_menus_gates_items(monkeypatch):
    monkeypatch.setattr(AutoML, "tk", DummyTk())

    app = AutoMLApp.__new__(AutoMLApp)
    app.diagram_mode = "CTA"
    app.fta_menu = DummyMenu()
    app.cta_menu = DummyMenu()
    app.paa_menu = DummyMenu()
    app._fta_menu_indices = {"add_gate": 0, "add_basic_event": 1, "add_gate_from_failure_mode": 2, "add_fault_event": 3}
    app._cta_menu_indices = {"add_trigger": 0, "add_functional_insufficiency": 1}
    app._paa_menu_indices = {"add_confidence": 0, "add_robustness": 1}

    AutoMLApp._update_analysis_menus(app)

    assert all(state == DummyTk.DISABLED for _, state in app.fta_menu.items)
    assert all(state == DummyTk.NORMAL for _, state in app.cta_menu.items)


def test_context_menu_cta_only(monkeypatch):
    monkeypatch.setattr(AutoML.tk, "Menu", DummyMenu)

    app = AutoMLApp.__new__(AutoMLApp)
    app.root = None
    app.zoom = 1.0
    app.canvas = DummyCanvas()
    app.canvas.diagram_mode = "CTA"
    app.root_node = FaultTreeNode("", "TOP EVENT")
    app.root_node.x = 0
    app.root_node.y = 0
    app.get_all_nodes = lambda n: [app.root_node]

    # Stub out actions referenced by the context menu
    for name in [
        "edit_selected",
        "remove_connection",
        "delete_node_and_subtree",
        "remove_node",
        "copy_node",
        "cut_node",
        "paste_node",
        "edit_user_name",
        "edit_description",
        "edit_rationale",
        "edit_value",
        "edit_gate_type",
        "edit_severity",
        "edit_controllability",
        "edit_page_flag",
        "add_node_of_type",
        "add_gate_from_failure_mode",
        "add_fault_event",
    ]:
        setattr(app, name, lambda *a, **k: None)

    AutoML._last_menu = None
    event = types.SimpleNamespace(x=0, y=0, x_root=0, y_root=0)
    app.show_context_menu(event)
    items = AutoML._last_menu.items if AutoML._last_menu else []
    assert "Add Triggering Condition" in items
    assert "Add Functional Insufficiency" in items
    assert "Add Gate" not in items


def test_add_node_invalid_for_mode(monkeypatch):
    calls = {}
    monkeypatch.setattr(AutoML.messagebox, "showwarning", lambda *a, **k: calls.setdefault("called", True))

    app = AutoMLApp.__new__(AutoMLApp)
    app.push_undo_state = lambda: None
    app.analysis_tree = types.SimpleNamespace(selection=lambda: ())
    app.selected_node = FaultTreeNode("", "TOP EVENT")
    app.selected_node.is_primary_instance = True
    app.root_node = app.selected_node

    app.diagram_mode = "CTA"
    app.add_node_of_type("GATE")
    assert calls.get("called")

