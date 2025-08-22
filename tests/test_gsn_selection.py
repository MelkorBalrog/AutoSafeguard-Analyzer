import types

from gui.gsn_diagram_window import GSNDiagramWindow, GSNNode, GSNDiagram


def test_gsn_find_node_strategies():
    offset = 50

    class CanvasStub:
        def canvasx(self, x):
            return x + offset

        def canvasy(self, y):
            return y

        def find_overlapping(self, x1, y1, x2, y2):
            if x1 <= 60 <= x2 and y1 <= 10 <= y2:
                return ["id"]
            return []

        def find_closest(self, x, y):
            return ["id"]

        def bbox(self, tag):
            if tag == "id":
                return [50, 0, 70, 30]
            return None

        def gettags(self, item):
            return [item]

    node = GSNNode("A", "Goal", x=60, y=15)
    diag = GSNDiagram(node)
    win = object.__new__(GSNDiagramWindow)
    win.canvas = CanvasStub()
    win.id_to_node = {"id": node}
    win.diagram = diag
    win.zoom = 1.0

    assert win._node_at_strategy1(10, 10) is node
    assert win._node_at_strategy2(10, 10) is node
    assert win._node_at_strategy3(10, 10) is node
    assert win._node_at_strategy4(10, 10) is node
    assert win._node_at(10, 10) is node

