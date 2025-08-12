import pytest
from gui.architecture import SysMLDiagramWindow, SysMLObject

class DummyWindow:
    def __init__(self):
        self.zoom = 1.0

@pytest.mark.parametrize(
    "tx, ty, expected",
    [
        (10, 0, (6, 0)),   # right side
        (-10, 0, (-6, 0)), # left side
        (0, 10, (0, 6)),   # bottom side (positive y)
        (0, -10, (0, -6)), # top side
    ],
)
def test_edge_point_on_port(tx, ty, expected):
    win = DummyWindow()
    port = SysMLObject(1, "Port", 0, 0)
    x, y = SysMLDiagramWindow.edge_point(win, port, tx, ty)
    assert abs(x - expected[0]) < 1e-6
    assert abs(y - expected[1]) < 1e-6
