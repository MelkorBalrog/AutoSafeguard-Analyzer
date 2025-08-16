import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


def test_display_requirements_includes_phase(monkeypatch):
    class DummyTab:
        def __init__(self):
            self.children = []

        def winfo_children(self):
            return list(self.children)

    class DummyApp:
        def _new_tab(self, title):
            return DummyTab()

    columns_captured = []
    inserted = []

    class DummyFrame:
        def __init__(self, master):
            self.master = master
            self.children = []
            master.children.append(self)

        def winfo_children(self):
            return list(self.children)

        def rowconfigure(self, *args, **kwargs):
            pass

        def columnconfigure(self, *args, **kwargs):
            pass

        def pack(self, **kwargs):
            pass

        def destroy(self):
            self.master.children.remove(self)

    class DummyScrollbar:
        def __init__(self, master, orient=None, command=None):
            self.master = master
            master.children.append(self)

        def grid(self, *args, **kwargs):
            pass

        def set(self, *args):
            pass

        def destroy(self):
            self.master.children.remove(self)

    class DummyTree:
        def __init__(self, master, columns, show="headings"):
            columns_captured.append(columns)
            master.children.append(self)

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            inserted.append(values)

        def configure(self, **kwargs):
            pass

        def yview(self, *args):
            pass

        def xview(self, *args):
            pass

        def grid(self, *args, **kwargs):
            pass

    monkeypatch.setattr(smt.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(smt.ttk, "Scrollbar", DummyScrollbar)
    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.app = DummyApp()

    global_requirements.clear()
    global_requirements.update({
        "R1": {"req_type": "org", "text": "Do", "phase": "P1", "status": "draft"}
    })

    win._display_requirements("Title", ["R1"])

    assert columns_captured[0] == ("ID", "Type", "Text", "Phase", "Status")
    assert inserted[0] == ("R1", "org", "Do", "P1", "draft")
