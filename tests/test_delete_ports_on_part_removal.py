import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.objects = []
        self.connections = []

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]

class RemovePartPortsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_ports_removed_with_part(self):
        win = DummyWindow()
        part = SysMLObject(1, "Part", 0, 0)
        port = SysMLObject(2, "Port", 0, 0, properties={"parent": "1"})
        win.objects = [part, port]
        SysMLDiagramWindow.remove_object(win, part)
        self.assertNotIn(port, win.objects)

if __name__ == "__main__":
    unittest.main()
