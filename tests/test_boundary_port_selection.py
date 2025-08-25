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
from gui.architecture import SysMLDiagramWindow, SysMLObject, set_ibd_father
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class BoundaryPortSelectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_find_object_prefers_port_over_boundary(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p"})
        diag = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, diag, block.elem_id)
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        win.objects = [SysMLObject(**o) for o in diag.objects]
        win.zoom = 1.0
        port_obj = next(o for o in win.objects if o.obj_type == "Port")
        obj = win.find_object(port_obj.x, port_obj.y, prefer_port=True)
        self.assertEqual(obj.obj_type, "Port")

    def test_find_object_prefers_boundary_port_over_part(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p"})
        diag = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, diag, block.elem_id)
        port_obj = next(o for o in diag.objects if o["obj_type"] == "Port")
        part_elem = repo.create_element("Block", name="P")
        part = repo.create_element("Part", properties={"definition": part_elem.elem_id})
        diag.objects.append(
            {
                "obj_id": max(o["obj_id"] for o in diag.objects) + 1,
                "obj_type": "Part",
                "x": port_obj["x"],
                "y": port_obj["y"],
                "element_id": part.elem_id,
                "properties": {"definition": part_elem.elem_id},
            }
        )
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        win.objects = [SysMLObject(**o) for o in diag.objects]
        win.zoom = 1.0
        win.sort_objects()
        port = next(o for o in win.objects if o.obj_type == "Port")
        obj = win.find_object(port.x, port.y, prefer_port=True)
        self.assertEqual(obj.obj_type, "Port")

if __name__ == '__main__':
    unittest.main()
