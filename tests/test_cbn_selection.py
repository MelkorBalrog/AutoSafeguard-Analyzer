import types
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def test_event_coord_versions_agree_after_scroll():
    win = object.__new__(CausalBayesianNetworkWindow)

    class CanvasStub:
        def __init__(self, ox=0, oy=0):
            self.ox = ox
            self.oy = oy
        def canvasx(self, x):
            return x + self.ox
        def canvasy(self, y):
            return y + self.oy

    win.canvas = CanvasStub(50, 75)
    event = types.SimpleNamespace(x=10, y=20, widget=win.canvas)
    coords = [
        CausalBayesianNetworkWindow._event_coords_v1(win, event),
        CausalBayesianNetworkWindow._event_coords_v2(win, event),
        CausalBayesianNetworkWindow._event_coords_v3(win, event),
        CausalBayesianNetworkWindow._event_coords_v4(win, event),
    ]
    assert coords.count(coords[0]) == 4


def test_find_node_after_scroll():
    win = object.__new__(CausalBayesianNetworkWindow)

    class CanvasStub:
        def __init__(self, ox=0, oy=0):
            self.ox = ox
            self.oy = oy
        def canvasx(self, x):
            return x + self.ox
        def canvasy(self, y):
            return y + self.oy
        def find_overlapping(self, x1, y1, x2, y2):
            if (x1, y1, x2, y2) == (100, 100, 100, 100):
                return [1]
            return []

    win.canvas = CanvasStub(50, 50)
    win.id_to_node = {1: "A"}
    event = types.SimpleNamespace(x=50, y=50, widget=win.canvas)
    x, y = CausalBayesianNetworkWindow._event_coords(win, event)
    assert CausalBayesianNetworkWindow._find_node(win, x, y) == "A"
