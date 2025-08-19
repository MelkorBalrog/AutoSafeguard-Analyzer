import types

import AutoML
from AutoML import AutoMLApp


def test_show_hazard_explorer_creates_tab():
    app = AutoMLApp.__new__(AutoMLApp)

    class DummyNotebook:
        def __init__(self):
            self._tabs = []
            self.selected = None

        def select(self, tab):
            self.selected = tab

        def tabs(self):
            return self._tabs

    app.doc_nb = DummyNotebook()
    app._tab_titles = {}
    app._doc_all_tabs = []
    app._doc_tab_offset = 0
    app.MAX_VISIBLE_TABS = AutoMLApp.MAX_VISIBLE_TABS

    def fake_new_tab(self, title):
        tab = types.SimpleNamespace(title=title, winfo_exists=lambda: True)
        self.doc_nb._tabs.append(tab)
        return tab

    app._new_tab = types.MethodType(fake_new_tab, app)

    class DummyHazExp:
        def __init__(self, master, app):
            self.master = master

        def pack(self, **kwargs):
            pass

    old_cls = AutoML.HazardExplorerWindow
    AutoML.HazardExplorerWindow = DummyHazExp
    try:
        AutoMLApp.show_hazard_explorer(app)
        assert app._haz_exp_tab.title == "Hazard Explorer"
        assert app.doc_nb._tabs == [app._haz_exp_tab]

        AutoMLApp.show_hazard_explorer(app)
        assert app.doc_nb.selected is app._haz_exp_tab
        assert len(app.doc_nb._tabs) == 1
    finally:
        AutoML.HazardExplorerWindow = old_cls
