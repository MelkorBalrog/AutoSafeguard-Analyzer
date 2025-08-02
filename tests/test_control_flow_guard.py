import unittest
from gui.architecture import (
    SysMLObject,
    DiagramConnection,
    format_control_flow_label,
)
from sysml.sysml_repository import SysMLRepository

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
            element_id=act.elem_id,
        )
        diag.connections = [conn.__dict__]
        data = repo.to_dict()
        repo2 = SysMLRepository.reset_instance()
        repo2.from_dict(data)
        loaded = repo2.diagrams[diag.diag_id].connections[0]
        self.assertEqual(loaded.get("guard"), ["g1", "g2"])
        self.assertEqual(loaded.get("element_id"), act.elem_id)

    def test_guard_label_with_operators(self):
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
            guard=["g1", "g2", "g3"],
            guard_ops=["AND", "OR"],
            element_id=act.elem_id,
        )
        diag.connections = [conn.__dict__]
        label = format_control_flow_label(conn, repo, "Control Flow Diagram")
        self.assertEqual(label, "[g1 AND g2 OR g3] / Do")

if __name__ == "__main__":
    unittest.main()
