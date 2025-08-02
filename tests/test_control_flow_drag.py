import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject, DiagramConnection
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.objects = [
            SysMLObject(1, "Existing Element", 0, 0),
            SysMLObject(2, "Existing Element", 0, 100),
        ]
        self.connections = [DiagramConnection(1, 2, "Control Action")]


def reset_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


class ControlFlowDragTests(unittest.TestCase):
    def setUp(self):
        reset_repo()

    def test_horizontal_move_restricted(self):
        win = DummyWindow()
        obj = win.objects[1]
        new_x = SysMLDiagramWindow._constrain_horizontal_movement(win, obj, 50)
        self.assertEqual(new_x, win.objects[0].x)

    def test_unconnected_move_free(self):
        win = DummyWindow()
        obj = SysMLObject(3, "Existing Element", 50, 200)
        win.objects.append(obj)
        new_x = SysMLDiagramWindow._constrain_horizontal_movement(win, obj, 80)
        self.assertEqual(new_x, 80)


if __name__ == "__main__":
    unittest.main()
