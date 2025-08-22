import types

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from analysis.causal_bayesian_network import CausalBayesianNetworkDoc


def test_find_node_strategies_with_scroll():
    offset = 100

    class CanvasStub:
        def canvasx(self, x):
            return x + offset

        def canvasy(self, y):
            return y

        def find_overlapping(self, x1, y1, x2, y2):
            if x1 <= 110 <= x2 and y1 <= 15 <= y2:
                return [1]
            return []

        def find_closest(self, x, y):
            return [1]

        def coords(self, obj_id):
            return [100, 0, 120, 30]

    win = object.__new__(CausalBayesianNetworkWindow)
    win.canvas = CanvasStub()
    win.id_to_node = {1: ("A", 0)}
    win.nodes = {"A": [(1, None, "fill_A")]}
    win.NODE_RADIUS = 10
    win.app = types.SimpleNamespace(
        active_cbn=types.SimpleNamespace(positions={"A": [(110, 15)]})
    )

    assert win._find_node_strategy1(10, 15) == ("A", 0)
    assert win._find_node_strategy2(10, 15) == ("A", 0)
    assert win._find_node_strategy3(10, 15) == ("A", 0)
    assert win._find_node_strategy4(10, 15) == ("A", 0)
    assert win._find_node(10, 15) == ("A", 0)


def test_drag_clone_keeps_original_position():
    doc = CausalBayesianNetworkDoc(name="d")
    doc.network.add_node("A", cpd=0.5)
    doc.positions["A"] = [(0, 0), (20, 20)]
    doc.types["A"] = "variable"
    app = types.SimpleNamespace(active_cbn=doc, cbn_docs=[doc])

    class CanvasStub:
        def move(self, *a, **k):
            pass

        def coords(self, *a, **k):
            return [0, 0, 0, 0]

        def create_rectangle(self, *a, **k):
            return 1

        def delete(self, *a, **k):
            pass

    win = object.__new__(CausalBayesianNetworkWindow)
    win.app = app
    win.nodes = {"A": [(1, 2, "fill1"), (3, 4, "fill2")]}
    win.id_to_node = {1: ("A", 0), 2: ("A", 0), 3: ("A", 1), 4: ("A", 1)}
    win.edges = []
    win.NODE_RADIUS = 10
    win.canvas = CanvasStub()
    win._position_table = lambda *a, **k: None
    win._update_scroll_region = lambda: None
    win.current_tool = "Select"
    win.drag_node = None
    win.selection_rect = None
    win._find_node = lambda x, y: ("A", 1)

    win.on_click(types.SimpleNamespace(x=20, y=20))
    win.on_drag(types.SimpleNamespace(x=40, y=50))

    assert doc.positions["A"][1] == (40, 50)
    assert doc.positions["A"][0] == (0, 0)
