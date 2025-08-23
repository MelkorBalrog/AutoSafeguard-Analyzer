import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp, FaultTreeNode


class DummyTree:
    def __init__(self):
        self.items = {}
        self._focus = None

    def focus(self, item=None):
        if item is not None:
            self._focus = item
        return self._focus

    def item(self, node, option):
        return self.items[node][option]

    def insert(self, parent, index, text="", tags=()):
        node_id = f"id{len(self.items)}"
        self.items[node_id] = {"text": text, "tags": tags}
        return node_id


def test_double_click_fta_sets_mode():
    app = AutoMLApp.__new__(AutoMLApp)
    te = FaultTreeNode("", "TOP EVENT")
    te.unique_id = 1
    app.top_events = [te]
    app.diagram_mode = "PAA"
    app.analysis_tree = DummyTree()
    node_id = app.analysis_tree.insert("", "end", text="fta", tags=("fta", "1"))
    app.analysis_tree.focus(node_id)

    called = {}
    app.ensure_fta_tab = lambda: called.setdefault("ensure", True)
    def open_page(node):
        called["node"] = node
    app.open_page_diagram = open_page
    app.doc_nb = type("NB", (), {"select": lambda self, x: None})()
    app.canvas_tab = object()

    app.on_analysis_tree_double_click(None)
    assert app.diagram_mode == "FTA"
    assert called.get("node") is te
