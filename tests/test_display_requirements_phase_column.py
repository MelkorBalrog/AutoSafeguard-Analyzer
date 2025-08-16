import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.safety_management_toolbox import SafetyManagementWindow
from gui import safety_management_toolbox as smt
from analysis.models import global_requirements


def test_display_requirements_includes_phase(monkeypatch):
    class DummyTab:
        def winfo_children(self):
            return []

    class DummyApp:
        def _new_tab(self, title):
            return DummyTab()

    columns_captured = []
    inserted = []

    class DummyTree:
        def __init__(self, master, columns, show="headings"):
            columns_captured.append(columns)

        def heading(self, col, text=""):
            pass

        def insert(self, parent, idx, values):
            inserted.append(values)

        def pack(self, **kwargs):
            pass

    monkeypatch.setattr(smt.ttk, "Treeview", DummyTree)

    win = SafetyManagementWindow.__new__(SafetyManagementWindow)
    win.app = DummyApp()

    global_requirements.clear()
    global_requirements.update({
        "R1": {"req_type": "org", "text": "Do", "phase": "P1"}
    })

    win._display_requirements("Title", ["R1"])

    assert columns_captured[0] == ("ID", "Type", "Text", "Phase")
    assert inserted[0] == ("R1", "org", "Do", "P1")
