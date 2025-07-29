# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import (
    SysMLObject,
    remove_orphan_ports,
    update_ports_for_part,
    SysMLDiagramWindow,
)
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class PortParentTests(unittest.TestCase):
    def test_remove_orphan_ports(self):
        part = SysMLObject(1, "Part", 0, 0)
        good_port = SysMLObject(2, "Port", 0, 0, properties={"parent": "1"})
        orphan_port = SysMLObject(3, "Port", 0, 0)
        bad_port = SysMLObject(4, "Port", 0, 0, properties={"parent": "99"})
        objs = [part, good_port, orphan_port, bad_port]
        remove_orphan_ports(objs)
        self.assertIn(part, objs)
        self.assertIn(good_port, objs)
        self.assertNotIn(orphan_port, objs)
        self.assertNotIn(bad_port, objs)

    def test_ports_follow_part_resize(self):
        part = SysMLObject(1, "Part", 0, 0, width=80, height=40)
        port = SysMLObject(
            2,
            "Port",
            part.x + part.width / 2,
            0,
            properties={"parent": "1"},
        )
        objs = [part, port]
        update_ports_for_part(part, objs)
        self.assertEqual(port.properties.get("side"), "E")
        part.width = 100
        update_ports_for_part(part, objs)
        self.assertEqual(port.x, part.x + part.width / 2)


class DirectionValidationTests(unittest.TestCase):
    class DummyWindow:
        def __init__(self):
            self.repo = SysMLRepository.get_instance()
            diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
            self.repo.diagrams[diag.diag_id] = diag
            self.diagram_id = diag.diag_id

    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_incompatible_directions(self):
        win = self.DummyWindow()
        src = SysMLObject(1, "Port", 0, 0, properties={"direction": "out"})
        dst = SysMLObject(2, "Port", 0, 0, properties={"direction": "in"})
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Connector")
        self.assertFalse(valid)


if __name__ == '__main__':
    unittest.main()
