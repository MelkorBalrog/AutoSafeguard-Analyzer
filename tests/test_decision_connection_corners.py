import unittest
from gui.architecture import SysMLDiagramWindow, DiagramConnection, SysMLObject
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Control Flow Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id
        self.zoom = 1.0
        self.objects = []
        self.connections = []

    get_object = SysMLDiagramWindow.get_object
    validate_connection = SysMLDiagramWindow.validate_connection
    _assign_decision_corners = SysMLDiagramWindow._assign_decision_corners
    _decision_used_corners = SysMLDiagramWindow._decision_used_corners
    _corner_index = SysMLDiagramWindow._corner_index
    _choose_decision_corner = SysMLDiagramWindow._choose_decision_corner
    _nearest_diamond_corner = SysMLDiagramWindow._nearest_diamond_corner


class DecisionCornerTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.win = DummyWindow()
        self.dec = SysMLObject(1, "Decision", 0, 0, width=40, height=40)
        self.actions = [
            SysMLObject(2, "Action", 0, -100),
            SysMLObject(3, "Action", 100, 0),
            SysMLObject(4, "Action", 0, 100),
            SysMLObject(5, "Action", -100, 0),
        ]
        self.win.objects = [self.dec] + self.actions

    def test_unique_corners_and_limit(self):
        corners = set()
        # two outgoing connections
        for act in self.actions[:2]:
            valid, _ = self.win.validate_connection(self.dec, act, "Flow")
            self.assertTrue(valid)
            conn = DiagramConnection(self.dec.obj_id, act.obj_id, "Flow")
            self.win._assign_decision_corners(conn)
            self.win.connections.append(conn)
            corners.add(conn.src_pos)
        # two incoming connections
        for act in self.actions[2:]:
            valid, _ = self.win.validate_connection(act, self.dec, "Flow")
            self.assertTrue(valid)
            conn = DiagramConnection(act.obj_id, self.dec.obj_id, "Flow")
            self.win._assign_decision_corners(conn)
            self.win.connections.append(conn)
            corners.add(conn.dst_pos)
        self.assertEqual(corners, {(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)})
        # fifth connection should be rejected
        extra = SysMLObject(6, "Action", 50, 50)
        self.win.objects.append(extra)
        valid, _ = self.win.validate_connection(self.dec, extra, "Flow")
        self.assertFalse(valid)

    def test_bidirectional_connections_use_opposite_corners(self):
        act = self.actions[0]
        conn1 = DiagramConnection(act.obj_id, self.dec.obj_id, "Flow")
        self.win._assign_decision_corners(conn1)
        self.win.connections.append(conn1)
        conn2 = DiagramConnection(self.dec.obj_id, act.obj_id, "Flow")
        self.win._assign_decision_corners(conn2)
        self.win.connections.append(conn2)
        self.assertNotEqual(conn1.dst_pos, conn2.src_pos)
        if conn1.dst_pos:
            self.assertEqual(conn2.src_pos, (-conn1.dst_pos[0], -conn1.dst_pos[1]))


if __name__ == "__main__":
    unittest.main()
