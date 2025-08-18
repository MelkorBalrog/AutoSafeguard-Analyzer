import types
import AutoML
from AutoML import FaultTreeApp
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule, SafetyWorkProduct


def test_phase_change_closes_ungoverned_tabs(monkeypatch):
    class DummyFrame:
        def __init__(self, master=None, **kw):
            pass
        def winfo_children(self):
            return []
    class DummyNotebook:
        def __init__(self):
            self._tabs = []
            self._titles = {}
            self._widgets = {}
            self._closing_tab = None
            self.protected = set()
        def tabs(self):
            return list(self._tabs)
        def add(self, widget, text):
            tab_id = f"id{len(self._tabs)}"
            self._tabs.append(tab_id)
            self._titles[tab_id] = text
            self._widgets[tab_id] = widget
        def select(self, tab):
            pass
        def tab(self, tab_id, option):
            return self._titles[tab_id]
        def nametowidget(self, tab_id):
            return self._widgets[tab_id]
        def forget(self, tab_id):
            self._tabs.remove(tab_id)
            self._titles.pop(tab_id, None)
            self._widgets.pop(tab_id, None)
        def event_generate(self, event):
            pass
    monkeypatch.setattr(AutoML, "ttk", types.SimpleNamespace(Frame=lambda *a, **k: DummyFrame()))
    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = DummyNotebook()
    app._tab_titles = {}
    app.diagram_tabs = {}
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov1"]), GovernanceModule("P2")]
    toolbox.work_products = [SafetyWorkProduct("Gov1", "Threat Analysis")]
    toolbox.set_active_module("P1")
    app.safety_mgmt_toolbox = toolbox
    class DummyVar:
        def __init__(self, val=""):
            self.val = val
        def set(self, v):
            self.val = v
        def get(self):
            return self.val
    app.lifecycle_var = DummyVar("P1")
    app.update_views = lambda: None
    app.refresh_tool_enablement = lambda: None
    app.refresh_all = lambda: None
    app.on_lifecycle_selected = FaultTreeApp.on_lifecycle_selected.__get__(app, FaultTreeApp)
    class DummyThreatWindow(DummyFrame):
        def __init__(self, master, app):
            super().__init__(master)
        def refresh_docs(self):
            pass
        def winfo_exists(self):
            return True
    monkeypatch.setattr(AutoML, "ThreatWindow", DummyThreatWindow)
    app.open_threat_window()
    assert app.doc_nb.tabs()
    app.lifecycle_var.set("P2")
    app.on_lifecycle_selected()
    assert not app.doc_nb.tabs()
