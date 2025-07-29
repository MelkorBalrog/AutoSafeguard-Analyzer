# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import (
    SysMLObject,
    remove_orphan_ports,
    update_ports_for_part,
)

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


if __name__ == '__main__':
    unittest.main()
