import sys
import types
from pathlib import Path
import tkinter as tk

# Add repository root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
for mod in ["Image", "ImageDraw", "ImageFont", "ImageTk"]:
    sys.modules.setdefault(f"PIL.{mod}", types.ModuleType(mod))

import main.AutoML as AutoML
from main.AutoML import AutoMLApp, PageDiagram, FaultTreeNode


class DummyMenu:
    """Minimal stand-in for tk.Menu capturing commands and state."""

    def __init__(self, *_, **__):
        self.commands = []
        self.states = {}
        created_menus.append(self)

    def add_command(self, label, command=lambda: None):
        self.commands.append(label)

    def add_separator(self):
        pass

    def entryconfig(self, idx, state=tk.DISABLED):
        self.states[idx] = state

    def tk_popup(self, *a, **k):
        pass


created_menus = []


def _make_page_diagram(mode):
    canvas = types.SimpleNamespace(canvasx=lambda v: v, canvasy=lambda v: v)
    root = FaultTreeNode("", "GATE")
    root.x = 0
    root.y = 0
    diag = PageDiagram.__new__(PageDiagram)
    diag.canvas = canvas
    diag.zoom = 1.0
    diag.root_node = root
    diag.app = types.SimpleNamespace(root=None, selected_node=None)
    diag.selected_node = None
    diag.diagram_mode = mode
    diag.get_all_nodes = lambda _=None: [root]
    return diag


def test_context_menu_modes(monkeypatch):
    monkeypatch.setattr(AutoML.tk, "Menu", DummyMenu)
    event = types.SimpleNamespace(x=0, y=0, x_root=0, y_root=0)

    # FTA menu should include gate options
    fta_diag = _make_page_diagram("FTA")
    fta_diag.show_context_menu(event)
    fta_labels = set(created_menus[-1].commands)
    assert "Add Gate" in fta_labels
    assert "Add Triggering Condition" not in fta_labels

    # CTA menu should include CTA-specific options only
    cta_diag = _make_page_diagram("CTA")
    cta_diag.show_context_menu(event)
    cta_labels = set(created_menus[-1].commands)
    assert "Add Triggering Condition" in cta_labels
    assert "Add Gate" not in cta_labels


def test_top_level_menu_gating_on_tab_switch(monkeypatch):
    monkeypatch.setattr(AutoML.tk, "Menu", DummyMenu)

    app = AutoMLApp.__new__(AutoMLApp)
    app.fta_menu = DummyMenu()
    app.cta_menu = DummyMenu()
    app._fta_menu_indices = {
        "add_gate": 0,
        "add_basic_event": 1,
        "add_gate_from_failure_mode": 2,
        "add_fault_event": 3,
    }
    app._cta_menu_indices = {
        "add_trigger": 0,
        "add_functional_insufficiency": 1,
    }
    app._make_doc_tab_visible = lambda tab_id: None
    app.refresh_all = lambda: None

    # Set up analysis tabs for FTA and CTA
    class DummyTab:
        def winfo_children(self):
            return []

    fta_tab = DummyTab()
    cta_tab = DummyTab()
    app.fta_root_node = FaultTreeNode("", "TOP EVENT")
    app.cta_root_node = FaultTreeNode("", "TOP EVENT")
    app.analysis_tabs = {
        "FTA": {"tab": fta_tab, "canvas": types.SimpleNamespace(diagram_mode="FTA"), "hbar": None, "vbar": None},
        "CTA": {"tab": cta_tab, "canvas": types.SimpleNamespace(diagram_mode="CTA"), "hbar": None, "vbar": None},
    }

    # Start in FTA mode
    app.diagram_mode = "FTA"
    app._update_analysis_menus()
    assert app.fta_menu.states[0] == tk.NORMAL
    assert app.cta_menu.states[0] == tk.DISABLED

    class DummyNotebook:
        def select(self):
            return "cta"

        def nametowidget(self, tab_id):
            return cta_tab

    event = types.SimpleNamespace(widget=DummyNotebook())
    app._on_tab_change(event)

    assert app.diagram_mode == "CTA"
    assert app.fta_menu.states[0] == tk.DISABLED
    assert app.cta_menu.states[0] == tk.NORMAL


def test_add_node_enforces_mode(monkeypatch):
    warnings = []
    monkeypatch.setattr(AutoML.messagebox, "showwarning", lambda *a, **k: warnings.append(a[0]))

    app = AutoMLApp.__new__(AutoMLApp)
    app.push_undo_state = lambda *a, **k: None
    app.update_views = lambda: None
    app.selected_node = None
    app.analysis_tree = types.SimpleNamespace(selection=lambda: [])

    root = FaultTreeNode("root", "TOP EVENT")
    root.children = []
    app.selected_node = root
    app.diagram_mode = "CTA"

    app.add_node_of_type("GATE")
    assert root.children == []
    assert warnings
