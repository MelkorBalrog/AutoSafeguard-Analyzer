import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp, FaultTreeNode


def test_double_click_fta_sets_mode():
    class Tree:
        def identify_row(self, y):
            return "i1"
        def focus(self, item=None):
            return "i1"
        def item(self, iid, option):
            return {"tags": ("fta", "1")}[option]
    app = AutoMLApp.__new__(AutoMLApp)
    app.analysis_tree = Tree()
    app.top_events = [type("N", (), {"unique_id":1})()]
    app.ensure_fta_tab = lambda: None
    class NB:
        def select(self, tab):
            pass
    app.doc_nb = NB()
    app.canvas_tab = object()
    app.open_page_diagram = lambda te: None
    app.diagram_mode = "PAA"

    app.on_analysis_tree_double_click(None)
    assert app.diagram_mode == "FTA"
