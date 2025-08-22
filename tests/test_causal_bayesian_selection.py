import types

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


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
    win.id_to_node = {1: "A"}
    win.nodes = {"A": (1, None, "fill_A")}
    win.NODE_RADIUS = 10
    win.app = types.SimpleNamespace(
        active_cbn=types.SimpleNamespace(positions={"A": (110, 15)})
    )

    assert win._find_node_strategy1(10, 15) == "A"
    assert win._find_node_strategy2(10, 15) == "A"
    assert win._find_node_strategy3(10, 15) == "A"
    assert win._find_node_strategy4(10, 15) == "A"
    assert win._find_node(10, 15) == "A"
