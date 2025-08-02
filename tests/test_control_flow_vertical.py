import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id

class ControlFlowConnectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_vertical_connection_valid(self):
        win = DummyWindow()
        src = SysMLObject(1, "Existing Element", 0, 0)
        dst = SysMLObject(2, "Existing Element", 1, 100)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Control Action")
        self.assertTrue(valid)

    def test_connection_too_offset_invalid(self):
        win = DummyWindow()
        src = SysMLObject(1, "Existing Element", 0, 0)
        dst = SysMLObject(2, "Existing Element", 200, 100)
        valid, msg = SysMLDiagramWindow.validate_connection(win, src, dst, "Control Action")
        self.assertFalse(valid)
        self.assertEqual(msg, "Connections must be vertical")

if __name__ == "__main__":
    unittest.main()
