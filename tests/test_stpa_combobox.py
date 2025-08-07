import types

from analysis.models import StpaDoc, StpaEntry
from gui.stpa_window import StpaWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


def test_row_dialog_populates_control_actions(monkeypatch):
    """The control action combo box should list actions and preselect one."""

    repo = SysMLRepository.reset_instance()
    diag = SysMLDiagram(diag_id="d1", diag_type="Control Flow Diagram")
    diag.objects = [
        {"obj_id": 1, "name": "Controller"},
        {"obj_id": 2, "name": "Process"},
    ]
    diag.connections = [
        {"src": 1, "dst": 2, "conn_type": "Control Action", "name": "Act"}
    ]
    repo.diagrams[diag.diag_id] = diag

    app = types.SimpleNamespace(active_stpa=StpaDoc("Doc", diag.diag_id, []))
    parent = StpaWindow.__new__(StpaWindow)
    parent.app = app

    # ------------------------------------------------------------------
    # Stub tkinter widgets so the dialog can be created without a display
    # ------------------------------------------------------------------
    class DummyWidget:
        def __init__(self, *args, **kwargs):
            self.configured = {}

        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def insert(self, *a, **k):
            pass

        def bind(self, *a, **k):
            pass

        def configure(self, **k):
            self.configured.update(k)

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, state=None, **k):
            super().__init__(*a, **k)
            self.textvariable = textvariable
            self.state = state

    combo_holder = {}

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_holder["cb"] = cb
        return cb

    monkeypatch.setattr("gui.stpa_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.stpa_window.ttk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.stpa_window.tk.Listbox", lambda *a, **k: DummyWidget())

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

    monkeypatch.setattr("gui.stpa_window.tk.StringVar", lambda value="": DummyVar(value))

    dlg = StpaWindow.RowDialog.__new__(StpaWindow.RowDialog)
    dlg.parent = parent
    dlg.app = app
    dlg.row = StpaEntry("", "", "", "", "", [])

    dlg.body(master=DummyWidget())

    cb = combo_holder["cb"]
    assert cb.configured["values"] == ["Act"]
    assert dlg.action_var.get() == "Act"

