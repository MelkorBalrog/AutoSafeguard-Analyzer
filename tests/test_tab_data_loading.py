import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.closable_notebook import ClosableNotebook


class DummyTab:
    def __init__(self):
        self.methods = []
        self.events = []

    def load_data(self):
        self.methods.append("load")

    def unload_data(self):
        self.methods.append("unload")

    def event_generate(self, name):
        self.events.append(name)


@pytest.mark.parametrize("strategy", [1, 2, 3, 4])
def test_tab_data_loading(strategy):
    nb = ClosableNotebook.__new__(ClosableNotebook)
    nb._data_strategy = strategy
    nb._focused_tab = None

    tabs = {"t1": DummyTab(), "t2": DummyTab()}

    def select():
        return nb._current

    nb.select = select
    nb.nametowidget = lambda widget_id: tabs[widget_id]
    nb._get_widget = lambda widget_id: tabs.get(widget_id)
    nb._call_method = ClosableNotebook._call_method.__get__(nb)

    nb._current = "t1"
    nb._handle_tab_focus()
    nb._current = "t2"
    nb._handle_tab_focus()

    t1, t2 = tabs["t1"], tabs["t2"]

    if strategy == 1:
        assert t1.methods == ["load"]
        assert t1.events == []
        assert t2.methods == ["load"]
    elif strategy == 2:
        assert t1.methods == ["load", "unload"]
        assert t1.events == []
        assert t2.methods == ["load"]
    elif strategy == 3:
        assert t1.methods == []
        assert t1.events == ["<<TabLoaded>>", "<<TabUnloaded>>"]
        assert t2.events == ["<<TabLoaded>>"]
    else:
        assert t1.methods == ["load", "unload"]
        assert t1.events == ["<<TabLoaded>>", "<<TabUnloaded>>"]
        assert t2.methods == ["load"]
        assert t2.events == ["<<TabLoaded>>"]
