import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp


class DummyTree:
    def __init__(self):
        self.children = {"": []}
        self.items = {}

    def delete(self, *nodes):
        for n in nodes:
            for parent, kids in self.children.items():
                if n in kids:
                    kids.remove(n)
            self.children.pop(n, None)
            self.items.pop(n, None)

    def get_children(self, item=""):
        return self.children.get(item, [])

    def insert(self, parent, index, text, **kwargs):
        node_id = f"id{len(self.items)}"
        self.children.setdefault(parent, []).append(node_id)
        self.children.setdefault(node_id, [])
        self.items[node_id] = {"text": text, "tags": kwargs.get("tags", ())}
        return node_id

    def item(self, node, option):
        return self.items[node][option]


def _setup_app_for_tree():
    app = AutoMLApp.__new__(AutoMLApp)
    app.analysis_tree = DummyTree()
    app.top_events = []
    app.cta_events = [type("N", (), {"name": "c1", "unique_id": 1})()]
    app.paa_events = [type("N", (), {"name": "p1", "unique_id": 2})()]
    app.fmeas = []
    app.fmedas = []
    app.hara_docs = []
    app.gsn_diagrams = []
    app.gsn_modules = []
    app.management_diagrams = []
    app.enabled_work_products = {"CTA", "Prototype Assurance Analysis"}
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}

    class TB:
        work_products = [1]
        modules = []
        diagrams = {}

        def enabled_products(self):
            return app.enabled_work_products

        def document_visible(self, a, b):
            return True

        def list_diagrams(self):
            pass

    app.safety_mgmt_toolbox = TB()
    app.update_lifecycle_cb = lambda: None
    app.refresh_tool_enablement = lambda: None
    app.filter_var = type("FV", (), {"get": lambda self: ""})()
    app.displayed_filters = set()
    app.filter_lifecycle = None
    return app


def test_cta_and_paa_groups_separate():
    app = _setup_app_for_tree()
    app.update_views()
    sa_root = next(n for n, d in app.analysis_tree.items.items() if d["text"] == "Safety Analysis")
    child_texts = [app.analysis_tree.items[c]["text"] for c in app.analysis_tree.get_children(sa_root)]
    assert "CTAs" in child_texts
    assert "PAAs" in child_texts


def test_get_node_fill_color_by_mode():
    app = AutoMLApp.__new__(AutoMLApp)
    class C:
        pass
    app.canvas = C()
    app.canvas.diagram_mode = "CTA"
    assert app.get_node_fill_color(None) == "#EE82EE"
    app.canvas.diagram_mode = "PAA"
    assert app.get_node_fill_color(None) == "#40E0D0"
    app.canvas.diagram_mode = "FTA"
    assert app.get_node_fill_color(None) == "#FAD7A0"


def test_paa_group_not_duplicated():
    app = _setup_app_for_tree()
    # Add a PAA top event alongside existing paa_events
    app.top_events = [type("N", (), {"name": "p2", "unique_id": 3, "analysis_mode": "PAA"})()]
    app.update_views()
    sa_root = next(n for n, d in app.analysis_tree.items.items() if d["text"] == "Safety Analysis")
    paa_groups = [c for c in app.analysis_tree.get_children(sa_root) if app.analysis_tree.items[c]["text"] == "PAAs"]
    assert len(paa_groups) == 1
    paa_children = [app.analysis_tree.items[c]["text"] for c in app.analysis_tree.get_children(paa_groups[0])]
    assert set(paa_children) == {"p1", "p2"}
