import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import toolboxes as tb


def test_requirements_text_multiline(monkeypatch):
    created = {}

    class DummyText:
        def __init__(self, master):
            created["widget"] = "text"
            self._val = ""

        def insert(self, index, value):
            self._val = value

        def place(self, *_, **__):
            pass

        def focus_set(self):
            pass

        def bind(self, *_, **__):
            pass

        def destroy(self):
            pass

        def get(self, *_):
            return self._val

    class DummyEntry(DummyText):
        def __init__(self, master, textvariable=None):
            created["widget"] = "entry"

    class DummyCombobox(DummyEntry):
        def __init__(self, master, textvariable=None, values=None, state=None):
            super().__init__(master, textvariable)

    monkeypatch.setattr(tb.tk, "Text", DummyText)
    monkeypatch.setattr(tb.tk, "Entry", DummyEntry)
    monkeypatch.setattr(tb.ttk, "Combobox", DummyCombobox)

    tree = types.SimpleNamespace(
        _edit_widget=None,
        _multiline_cols={"Text"},
        _col_options={},
        _req_cols={},
        _req_target=None,
        _edit_cb=None,
        cget=lambda key: ("ID", "Text"),
        identify=lambda what, x, y: "cell" if what == "region" else None,
        identify_row=lambda y: "row1",
        identify_column=lambda x: "#2",
        set=lambda rowid, col_name, value=None: "old" if value is None else None,
        bbox=lambda rowid, col: (0, 0, 100, 20),
        index=lambda rowid: 0,
    )

    event = types.SimpleNamespace(x=0, y=0)
    tb.EditableTreeview._begin_edit(tree, event)

    assert created.get("widget") == "text"

