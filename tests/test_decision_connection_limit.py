# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
