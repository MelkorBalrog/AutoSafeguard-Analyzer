import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from gui.architecture import SysMLObjectDialog, SysMLObject
from analysis.safety_management import SafetyWorkProduct, SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository
from analysis.models import REQUIREMENT_WORK_PRODUCTS


def test_requirement_allocation_disabled(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()

    class DummyWidget:
        def __init__(self, *a, **k):
            self.state = k.get("state")
            self.tooltip_text = None
        def grid(self, *a, **k):
            return self
        def pack(self, *a, **k):
            return self
        def bind(self, *a, **k):
            return self
        def insert(self, *a, **k):
            return self
        def delete(self, *a, **k):
            return self
        def curselection(self):
            return ()
        def selection_set(self, *a, **k):
            return self
        def configure(self, **k):
            if "state" in k:
                self.state = k["state"]
            return self
        def add(self, *a, **k):
            return self
        def create_window(self, *a, **k):
            return self
        def yview(self, *a, **k):
            return self
        def bbox(self, *a, **k):
            return (0, 0, 0, 0)
        def set(self, *a, **k):
            return self

    class DummyListbox(DummyWidget):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.items = []
        def insert(self, index, item):
            self.items.append(item)
            return self
        def get(self, i):
            return self.items[i]

    class DummyVar:
        def __init__(self, value=""):
            self.value = value
        def get(self):
            return self.value
        def set(self, value):
            self.value = value

    tk_ns = types.SimpleNamespace(
        Listbox=DummyListbox,
        Canvas=DummyWidget,
        StringVar=lambda value="": DummyVar(value),
        BooleanVar=lambda value=False: DummyVar(value),
        END="end",
        BOTH="both",
        TOP="top",
        BOTTOM="bottom",
        LEFT="left",
        RIGHT="right",
    )
    ttk_ns = types.SimpleNamespace(
        Notebook=DummyWidget,
        Frame=DummyWidget,
        Label=DummyWidget,
        Entry=DummyWidget,
        Combobox=DummyWidget,
        Scrollbar=DummyWidget,
        Button=DummyWidget,
        Checkbutton=DummyWidget,
    )
    monkeypatch.setattr(SysMLObjectDialog, "nb", None, raising=False)
    monkeypatch.setattr(SysMLObjectDialog, "listboxes", {}, raising=False)
    monkeypatch.setattr(SysMLObjectDialog, "entries", {}, raising=False)
    monkeypatch.setattr(SysMLObjectDialog, "_operations", [], raising=False)
    monkeypatch.setattr(SysMLObjectDialog, "_behaviors", [], raising=False)
    monkeypatch.setattr(sys.modules['gui.architecture'], "tk", tk_ns)
    monkeypatch.setattr(sys.modules['gui.architecture'], "ttk", ttk_ns)
    monkeypatch.setattr(sys.modules['gui.architecture'], "SYSML_PROPERTIES", {})

    tooltip_holder = {}
    def dummy_tooltip(widget, text):
        widget.tooltip_text = text
        tooltip_holder["text"] = text
    monkeypatch.setattr(sys.modules['gui.architecture'], "ToolTip", dummy_tooltip)

    toolbox = SafetyManagementToolbox()
    toolbox.get_work_products = lambda: [SafetyWorkProduct(diagram="Gov", analysis="DiagWP")]
    toolbox.can_trace = lambda s, t: False
    app = types.SimpleNamespace(safety_mgmt_toolbox=toolbox)

    diagram = repo.create_diagram("DiagWP", name="Diag")
    master = types.SimpleNamespace(app=app, diagram_id=diagram.diag_id)

    obj = SysMLObject(1, "Block", 0.0, 0.0, properties={}, requirements=[])
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = master
    dlg.resizable = lambda *a, **k: None

    SysMLObjectDialog.body(dlg, master)

    assert dlg.req_list.state == "disabled"
    assert tooltip_holder["text"]
