import types

import AutoML
from AutoML import AutoMLApp


def test_new_tab_reuses_existing(monkeypatch):
    class DummyFrame:
        pass

    class DummyNotebook:
        def __init__(self):
            self._tabs = []
            self._titles = {}
            self._widgets = {}
            self.selected = None

        def tabs(self):
            return self._tabs

        def tab(self, tab_id, option):
            assert option == "text"
            return self._titles[tab_id]

        def add(self, widget, text):
            tab_id = f"id{len(self._tabs)}"
            self._tabs.append(tab_id)
            self._titles[tab_id] = text
            self._widgets[tab_id] = widget

        def select(self, tab):
            self.selected = tab

        def nametowidget(self, tab_id):
            return self._widgets[tab_id]

    monkeypatch.setattr(AutoML, "ttk", types.SimpleNamespace(Frame=lambda master: DummyFrame()))

    app = AutoMLApp.__new__(AutoMLApp)
    app.doc_nb = DummyNotebook()

    first = app._new_tab("My Tab")
    second = app._new_tab("My Tab")

    assert first is second
    assert len(app.doc_nb.tabs()) == 1
