import unittest
import tkinter as tk
from gui.architecture import SysMLObject, DiagramConnection, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def __init__(self):
        self.last_text = None

    def create_line(self, *args, **kwargs):
        pass

    def create_text(self, *args, **kwargs):
        self.last_text = kwargs.get("text")


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1
        self.font = None
        self.canvas = DummyCanvas()
        self.edge_point = lambda obj, _x, _y, _r: (obj.x, obj.y)

class ControlFlowGuardTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_guard_persistence(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="A")
        e2 = repo.create_element("Block", name="B")
        act = repo.create_element("Action", name="Do")
        diag = repo.create_diagram("Control Flow Diagram", name="CF")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
        o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
        diag.objects = [o1.__dict__, o2.__dict__]
        conn = DiagramConnection(
            o1.obj_id,
            o2.obj_id,
            "Control Action",
            guard=["g1", "g2"],
            guard_operator="OR",
            element_id=act.elem_id,
        )
        diag.connections = [conn.__dict__]
        data = repo.to_dict()
        repo2 = SysMLRepository.reset_instance()
        repo2.from_dict(data)
        loaded = repo2.diagrams[diag.diag_id].connections[0]
        self.assertEqual(loaded.get("guard"), ["g1", "g2"])
        self.assertEqual(loaded.get("guard_operator"), "OR")
        self.assertEqual(loaded.get("element_id"), act.elem_id)

    def test_guard_label_display(self):
        repo = self.repo
        act = repo.create_element("Action", name="Do")
        win = DummyWindow()
        a = SysMLObject(1, "Existing Element", 0, 0)
        b = SysMLObject(2, "Existing Element", 0, 100)
        conn = DiagramConnection(
            a.obj_id,
            b.obj_id,
            "Control Action",
            guard=["g1", "g2"],
            guard_operator="OR",
            element_id=act.elem_id,
        )
        SysMLDiagramWindow.draw_connection(win, a, b, conn)
        self.assertEqual(win.canvas.last_text, "[g1 OR g2] / Do")

if __name__ == "__main__":
    unittest.main()
