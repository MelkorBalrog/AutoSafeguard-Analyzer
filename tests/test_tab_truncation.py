import types

import AutoML
from AutoML import FaultTreeApp


def test_long_tab_title_truncated(monkeypatch):
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

    app = FaultTreeApp.__new__(FaultTreeApp)
    app.doc_nb = DummyNotebook()

    long_title = "x" * (FaultTreeApp.MAX_TAB_TEXT_LENGTH + 10)
    tab = app._new_tab(long_title)

    tab_id = app.doc_nb.tabs()[0]
    displayed = app.doc_nb.tab(tab_id, "text")
    assert displayed.endswith("…")
    assert len(displayed) == FaultTreeApp.MAX_TAB_TEXT_LENGTH

    second = app._new_tab(long_title)
    assert second is tab
