import sys
from pathlib import Path
import types

# Ensure repository root on path
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Stub out Pillow dependencies so importing the main app doesn't require Pillow
PIL_stub = types.ModuleType("PIL")
PIL_stub.Image = types.SimpleNamespace()
PIL_stub.ImageTk = types.SimpleNamespace()
PIL_stub.ImageDraw = types.SimpleNamespace()
PIL_stub.ImageFont = types.SimpleNamespace()
sys.modules.setdefault("PIL", PIL_stub)
sys.modules.setdefault("PIL.Image", PIL_stub.Image)
sys.modules.setdefault("PIL.ImageTk", PIL_stub.ImageTk)
sys.modules.setdefault("PIL.ImageDraw", PIL_stub.ImageDraw)
sys.modules.setdefault("PIL.ImageFont", PIL_stub.ImageFont)

from AutoML import FaultTreeApp


def test_safety_management_toolbox_single_instance(monkeypatch):
    """Opening the Safety & Security Management toolbox twice doesn't duplicate it."""

    class DummyTab:
        def winfo_exists(self):
            return True

    class DummyNotebook:
        def add(self, tab, text):
            pass

        def select(self, tab):
            pass

    class DummyWindow:
        created = 0

        def __init__(self, master, app, toolbox, show_diagrams=True):
            DummyWindow.created += 1

        def pack(self, **kwargs):
            pass

        def winfo_exists(self):
            return True

    import gui.safety_management_toolbox as smt
    import analysis

    monkeypatch.setattr(smt, "SafetyManagementWindow", DummyWindow)

    class DummyToolbox:
        pass

    monkeypatch.setattr(analysis, "SafetyManagementToolbox", DummyToolbox)

    class DummyApp:
        open_safety_management_toolbox = FaultTreeApp.open_safety_management_toolbox

        def __init__(self):
            self.doc_nb = DummyNotebook()

        def _new_tab(self, title):
            return DummyTab()

    app = DummyApp()
    app.open_safety_management_toolbox()
    app.open_safety_management_toolbox()
    assert DummyWindow.created == 1


def test_display_requirements_clears_existing(monkeypatch):
    """_display_requirements replaces prior content in the tab."""

    import gui.safety_management_toolbox as smt
    from analysis.models import global_requirements

    class DummyTab:
        def __init__(self):
            self.children = []

        def winfo_children(self):
            return list(self.children)

    tab = DummyTab()

    class DummyApp:
        def _new_tab(self, title):
            return tab

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
            self.master = master
            master.children.append(self)
            self.rows = []

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            self.rows.append(values)

        def configure(self, **kwargs):
            pass

        def yview(self, *args):
            pass

        def xview(self, *args):
            pass

        def grid(self, *args, **kwargs):
            pass

        def get_children(self):
            return list(range(len(self.rows)))

        def delete(self, *items):
            self.rows = []

        def destroy(self):
            self.master.children.remove(self)

    monkeypatch.setattr(smt.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(smt.ttk, "Scrollbar", DummyScrollbar)
    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = smt.SafetyManagementWindow.__new__(smt.SafetyManagementWindow)
    win.app = DummyApp()

    global_requirements.clear()
    global_requirements.update({"R1": {"req_type": "", "text": ""}, "R2": {"req_type": "", "text": ""}})

    win._display_requirements("Phase1 Requirements", ["R1"])
    assert len(tab.children) == 1
    first = tab.children[0]

    win._display_requirements("Phase1 Requirements", ["R2"])
    assert len(tab.children) == 1
    assert tab.children[0] is not first
