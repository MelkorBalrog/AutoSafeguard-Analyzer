import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


def test_display_requirements_column_widths(monkeypatch):
    class DummyTab:
        def __init__(self):
            self.children = []

        def winfo_children(self):
            return list(self.children)

    class DummyApp:
        def _new_tab(self, title):
            return DummyTab()

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
        def __init__(self, master, columns, show="headings", style=None):
            master.children.append(self)
            self.columns = columns
            self.rows = []
            self.column_widths = {}

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            row = {c: v for c, v in zip(self.columns, values)}
            self.rows.append(row)
            return str(len(self.rows) - 1)

        def set(self, item, column=None, value=None):
            if value is None:
                return self.rows[int(item)][column]
            self.rows[int(item)][column] = value

        def configure(self, **kwargs):
            pass

        def yview(self, *args):
            pass

        def xview(self, *args):
            pass

        def grid(self, *args, **kwargs):
            pass

        def get_children(self):
            return [str(i) for i in range(len(self.rows))]

        def delete(self, *items):
            self.rows = []

        def column(self, col, width=None, stretch=None):
            if width is not None:
                self.column_widths[col] = width

    class DummyFont:
        def measure(self, text):
            return len(text)

    monkeypatch.setattr(smt.tkfont, "nametofont", lambda name: DummyFont())
    monkeypatch.setattr(smt.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(smt.ttk, "Scrollbar", DummyScrollbar)
    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.app = DummyApp()

    global_requirements.clear()
    global_requirements.update({
        "R1": {"req_type": "org", "text": "Do", "phase": "P1", "status": "draft"}
    })

    frame = win._display_requirements("Title", ["R1"])
    tree = frame.children[0].children[0]

    assert tree.column_widths["ID"] == len("ID") + 10
    assert tree.column_widths["Type"] == len("Type") + 10
    assert tree.column_widths["Status"] == len("Status") + 10
