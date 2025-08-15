import unittest
from gui.architecture import SysMLObject, DiagramConnection, SysMLDiagramWindow


class DummyWindow:
    def __init__(self):
        self.connections = []
        self.zoom = 1.0
        self.objects = {}

    def get_object(self, oid):
        return self.objects.get(oid)

    _assign_decision_corner = SysMLDiagramWindow._assign_decision_corner
    _nearest_diamond_corner = SysMLDiagramWindow._nearest_diamond_corner


class DecisionConnectionTests(unittest.TestCase):
    def setUp(self):
        self.win = DummyWindow()
        self.decision = SysMLObject(1, "Decision", 0.0, 0.0, width=40.0, height=40.0)
        self.win.objects[self.decision.obj_id] = self.decision
        # four target actions
        self.targets = []
        for i in range(4):
            tgt = SysMLObject(i + 2, "Action", 100.0 * (i + 1), 0.0, width=40.0, height=40.0)
            self.win.objects[tgt.obj_id] = tgt
            self.targets.append(tgt)

    def test_unique_corners_and_limit(self):
        for tgt in self.targets:
            conn = DiagramConnection(self.decision.obj_id, tgt.obj_id, "Flow")
            ok = self.win._assign_decision_corner(conn, self.decision, "src_pos")
            self.assertTrue(ok)
            self.win.connections.append(conn)
        self.assertEqual(len({c.src_pos for c in self.win.connections}), 4)
        extra = SysMLObject(99, "Action", -100.0, 0.0, width=40.0, height=40.0)
        self.win.objects[extra.obj_id] = extra
        conn = DiagramConnection(self.decision.obj_id, extra.obj_id, "Flow")
        ok = self.win._assign_decision_corner(conn, self.decision, "src_pos")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
